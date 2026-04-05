from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import google.generativeai as genai
import os
from datetime import datetime, timezone
from dotenv import load_dotenv
from supabase import create_client, Client
from datetime import date, timedelta
from typing import Optional
from vision import analyze_food_image, FoodAnalysis
from model import *
from pet import (
    compute_health_score, score_to_pet_state,
    compute_streak, already_checked_in_today,
    generate_pet_message, STREAK_MILESTONES,
)

load_dotenv()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)

supabase: Client = create_client(
    os.environ["SUPABASE_URL"],
    os.environ["SUPABASE_KEY"]
)

genai.configure(api_key=os.environ["GEMINI_API_KEY"])

# =========
# Constants
# =========
CHECKPOINTS = ["wake", "gym", "breakfast", "lunch", "dinner", "sleep"]
BASELINE = {"wake": 7.0, "gym": 8.0, "breakfast": 8.5, "lunch": 12.5, "dinner": 18.5, "sleep": 23.0}
ALLOWED_MEDIA_TYPES = {"image/jpeg", "image/jpg", "image/png", "image/webp", "image/gif"}

# =================
# All API Endpoints
# =================

@app.post("/register", response_model=ProfileResponse)
def register(body: UserRegister):
    # 1. Create Supabase auth user
    auth_response = supabase.auth.sign_up({
        "email": body.email,
        "password": body.password
    })

    if not auth_response.user:
        raise HTTPException(status_code=400, detail="Registration failed — check if email confirmation is disabled in Supabase")
    user_id = auth_response.user.id

    # 2. Create profile (trigger handles this but we can upsert to add username/pet_name)
    supabase.table("profiles").upsert({
        "id": user_id,
        "username": body.username,
        "pet_name": body.pet_name
    }).execute()

    # 3. Seed 12 checkpoint stats rows with baselines
    stats_rows = [
        {
            "user_id": user_id,
            "checkpoint": cp,
            "day_type": day_type,
            "mean": BASELINE[cp],
            "variance": 0,
            "std": None,
            "n": 0,
            "needy_at": BASELINE[cp] - 0.5
        }
        for cp in CHECKPOINTS
        for day_type in ["weekday", "weekend"]
    ]
    supabase.table("user_checkpoint_stats").insert(stats_rows).execute()

    # 4. Return profile
    profile = supabase.table("profiles").select("*").eq("id", user_id).single().execute()
    return profile.data

@app.post("/login", response_model=LoginResponse)
def login(body: UserLogin):
    # 1. Sign in with Supabase auth
    auth_response = supabase .auth.sign_in_with_password({
        "email": body.email,
        "password": body.password
    })

    if not auth_response.user:
        raise HTTPException(status_code=401, detail="Invalid email or password")

    user_id = auth_response.user.id
    access_token = auth_response.session.access_token # type: ignore

    # 2. Fetch profile
    profile = supabase.table("profiles").select("*").eq("id", user_id).single().execute()

    if not profile.data:
        raise HTTPException(status_code=404, detail="Profile not found")

    data = dict(profile.data) # type: ignore

    return {
        "access_token": access_token,
        "user_id": user_id,
        "username": data["username"], # type: ignore
        "pet_name": data["pet_name"]  # type: ignore
    }

@app.post("/checkin")
def checkin(body: CheckInRequest):
    now = datetime.now(timezone.utc)
    hour_float = now.hour + now.minute / 60
    day_of_week = now.weekday()  # 0=Mon, 6=Sun
    is_weekend = day_of_week >= 5
    day_type = "weekend" if is_weekend else "weekday"

    # 1. Insert raw checkin
    supabase.table("checkins").insert({
        "user_id": body.user_id,
        "checkpoint": body.checkpoint,
        "checked_in_at": now.isoformat(),
        "hour_float": hour_float,
        "day_of_week": day_of_week,
        "is_weekend": is_weekend
    }).execute()

    # 2. Fetch current stats for this checkpoint + day type
    stats_res = supabase.table("user_checkpoint_stats")\
        .select("*")\
        .eq("user_id", body.user_id)\
        .eq("checkpoint", body.checkpoint)\
        .eq("day_type", day_type)\
        .single()\
        .execute()

    stats = dict(stats_res.data)                    # type: ignore
    n = stats["n"] + 1                              # type: ignore
    mean = stats["mean"] or 0.0                     # type: ignore

    # 3. Welford's online algorithm
    new_mean = mean + (hour_float - mean) / n       # type: ignore
    new_variance = stats["variance"] + (hour_float - mean) * (hour_float - new_mean)    # type: ignore
    new_std = (new_variance / n) ** 0.5 if n > 1 else None
    new_needy_at = new_mean - (0.5 * new_std) if new_std else new_mean - 0.5

    # 4. Update stats row
    supabase.table("user_checkpoint_stats").update({
        "n": n,
        "mean": new_mean,
        "variance": new_variance,
        "std": new_std,
        "needy_at": new_needy_at,
        "updated_at": now.isoformat()
    }).eq("user_id", body.user_id)\
      .eq("checkpoint", body.checkpoint)\
      .eq("day_type", day_type)\
      .execute()

    return {
        "checkpoint": body.checkpoint,
        "logged_at": hour_float,
        "new_mean": new_mean,
        "n": n
    }

@app.get("/pet/state")
def pet_state(user_id: str):
    now = datetime.now(timezone.utc)
    # hour_float = now.hour + now.minute / 60
    hour_float = 14.0
    day_of_week = now.weekday()
    is_weekend = day_of_week >= 5
    day_type = "weekend" if is_weekend else "weekday"

    # 1. Fetch all stats for this user + day type
    stats_res = supabase.table("user_checkpoint_stats")\
        .select("*")\
        .eq("user_id", user_id)\
        .eq("day_type", day_type)\
        .execute()

    # 2. Fetch today's checkins
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0).isoformat()
    checkins_res = supabase.table("checkins")\
        .select("checkpoint")\
        .eq("user_id", user_id)\
        .gte("checked_in_at", today_start)\
        .execute()

    done_today = {row["checkpoint"] for row in checkins_res.data}       # type: ignore

    # 3. Check which checkpoints are overdue
    overdue = []
    upcoming = []

    for stat in stats_res.data:
        cp = stat["checkpoint"]                                         # type: ignore
        needy_at = stat["needy_at"] or BASELINE[cp] - 0.5               # type: ignore

        if cp in done_today:
            continue  # already logged, skip

        if hour_float >= needy_at:                                      # type: ignore
            overdue.append(cp)
        elif hour_float >= needy_at - 1:                                # type: ignore
            upcoming.append(cp)  # within 1hr of being due

    # 4. Derive pet state from overdue count
    if len(overdue) == 0:
        pet_state = "happy"
    elif len(overdue) == 1:
        pet_state = "neutral"
    elif len(overdue) == 2:
        pet_state = "tired"
    else:
        pet_state = "sad"

    return {
        "pet_state": pet_state,
        "overdue": overdue,
        "upcoming": upcoming,
        "done_today": list(done_today),
        "hour": hour_float
    }

@app.post("/analyze-food", response_model=FoodAnalysis)
async def analyze_food(file: UploadFile = File(...)):
    """Upload a food photo -> Gemini Vision estimates calories + macros."""
    if file.content_type not in ALLOWED_MEDIA_TYPES:
        raise HTTPException(
            status_code=415,
            detail=f"Unsupported file type '{file.content_type}'. Send JPEG, PNG, WebP, or GIF.",
        )
 
    image_bytes = await file.read()
 
    if len(image_bytes) > 10 * 1024 * 1024:
        raise HTTPException(status_code=413, detail="Image too large. Max 10 MB.")
 
    try:
        return analyze_food_image(image_bytes, file.content_type)
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Food analysis failed: {str(e)}")
 
@app.get("/health")
def health_check():
    return {"status": "ok", "mock": MOCK}