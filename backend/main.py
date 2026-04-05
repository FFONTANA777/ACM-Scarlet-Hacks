from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import google.generativeai as genai
import os
from dotenv import load_dotenv
from supabase import create_client, Client
from datetime import date, timedelta
from typing import Optional
from vision import analyze_food_image, FoodAnalysis

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

# ============================
# Response Models + DB Objects
# ============================
class User(BaseModel):
    email: str
    password: str
    username: str
    pet_name: str

class Profile(BaseModel):
    uuid: str
    username: str
    pet_name: str
    created_date: str

class CheckPointStats(BaseModel):
    uuid: str
    user_id: str
    checkpoint: str
    day_type: str
    mean: float
    variance: float
    standard_dev: float
    n: int
    needy_at: float
    updated_at: str

class CheckIn(BaseModel):
    uuid: str
    user_id: str
    checkpoint: str
    checked_in_at: str
    hour_float: float
    day_of_week: int
    is_weekend: bool
    created_at: str

class UserRegister(BaseModel):
    email: str
    password: str
    username: str
    pet_name: str = "Buddy"

class ProfileResponse(BaseModel):
    id: str
    username: str
    pet_name: str
    created_at: str

class UserLogin(BaseModel):
    email: str
    password: str

class LoginResponse(BaseModel):
    access_token: str
    user_id: str
    username: str
    pet_name: str

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

# genai.configure(api_key=os.environ["GEMINI_API_KEY"])
 
 
# # --- Models ---
# class CheckInRequest(BaseModel):
#     user_id: str
#     username: str
#     sleep_hours: float = Field(..., ge=0, le=12)
#     calories: int = Field(..., ge=0, le=10000)
#     steps: int = Field(..., ge=0)
#     mood: int = Field(..., ge=1, le=5)
 
 
# class CheckInResponse(BaseModel):
#     username: str  
#     health_score: float          # 0.0 – 1.0
#     pet_state: str               # thriving | happy | neutral | tired | sad
#     streak: int                  # consecutive days
#     streak_milestone: bool       # true if streak hit 7 / 14 / 30 / etc.
#     message: str                 # first-person pet message from Claude

# # --- Routes ---
 
# @app.post("/checkin", response_model=CheckInResponse)
# def checkin(req: CheckInRequest):
#     # Guard: one check-in per day
#     if already_checked_in_today(req.user_id):
#         raise HTTPException(status_code=409, detail="Already checked in today.")
 
#     # Fetch history for ML (before inserting today)
#     history = fetch_checkin_history(req.user_id)
 
#     # Get personalized baselines from PyTorch model
#     today_metrics = {"sleep_hours": req.sleep_hours, "calories": req.calories, "steps": req.steps}
#     baselines = get_personal_baselines(req.user_id, today_metrics, history)
 
#     # Score using personal ideals
#     health_score = compute_health_score(
#         req.sleep_hours, req.calories, req.steps, req.mood,
#         baselines.sleep_ideal,
#         baselines.calories_ideal,
#         baselines.steps_ideal,
#         baselines.consistency_bonus,
#     )
 
#     pet_state        = score_to_pet_state(health_score)
#     streak           = compute_streak(req.user_id)
#     streak_milestone = streak in STREAK_MILESTONES
 
#     if not MOCK:
#         supabase.table("checkins").insert({
#             "user_id":      req.user_id,
#             "username":     req.username,
#             "sleep_hours":  req.sleep_hours,
#             "calories":     req.calories,
#             "steps":        req.steps,
#             "mood":         req.mood,
#             "health_score": health_score,
#             "pet_state":    pet_state,
#             "streak":       streak,
#             "sleep_time":   req.sleep_time,
#             "wake_time":    req.wake_time,
#         }).execute()
 
#         supabase.table("profiles").upsert({
#             "user_id":  req.user_id,
#             "username": req.username,
#         }).execute()
 
#     message = generate_pet_message(pet_state, streak, req.sleep_time, req.wake_time)
 
#     return CheckInResponse(
#         username=req.username,
#         health_score=health_score,
#         pet_state=pet_state,
#         streak=streak,
#         streak_milestone=streak_milestone,
#         message=message,
#         personal_sleep_ideal=baselines.sleep_ideal,
#         personal_calories_ideal=baselines.calories_ideal,
#         personal_steps_ideal=baselines.steps_ideal,
#         ml_confidence=baselines.confidence,
#         consistency_bonus=baselines.consistency_bonus,
#     )
 
# @app.get("/pet/{user_id}")
# def get_pet_state(user_id: str):
#     if MOCK:
#         return {
#             "username":         "TestUser",
#             "health_score":     0.75,
#             "pet_state":        "happy",
#             "streak":           3,
#             "streak_milestone": False,
#             "checked_in_today": False,
#         }
 
#     result = (
#         supabase.table("checkins")
#         .select("health_score, pet_state, streak, created_at")
#         .eq("user_id", user_id)
#         .order("created_at", desc=True)
#         .limit(1)
#         .execute()
#     )
 
#     profile  = (
#         supabase.table("profiles")
#         .select("username")
#         .eq("user_id", user_id)
#         .limit(1)
#         .execute()
#     )
#     username = profile.data[0]["username"] if profile.data else "You"
 
#     if not result.data:
#         return {
#             "username":         username,
#             "health_score":     0.5,
#             "pet_state":        "neutral",
#             "streak":           0,
#             "streak_milestone": False,
#             "checked_in_today": False,
#         }
 
#     row              = result.data[0]
#     checked_in_today = row["created_at"][:10] == str(date.today())
 
#     return {
#         "username":         username,
#         "health_score":     row["health_score"],
#         "pet_state":        row["pet_state"],
#         "streak":           row["streak"],
#         "streak_milestone": row["streak"] in STREAK_MILESTONES,
#         "checked_in_today": checked_in_today,
#     }
 
@app.post("/analyze-food", response_model=FoodAnalysis)
async def analyze_food(file: UploadFile = File(...)):
    """Upload a food photo -> Gemini Vision estimates calories + macros."""
    if file.content_type not in ALLOWED_MEDIA_TYPES:
        raise HTTPException(
            status_code=415,
            detail=f"Unsupported file type '{file.content_type}'. Send JPEG, PNG, WebP, or GIF.",
        )
 
#     image_bytes = await file.read()
 
#     if len(image_bytes) > 10 * 1024 * 1024:
#         raise HTTPException(status_code=413, detail="Image too large. Max 10 MB.")
 
#     try:
#         return analyze_food_image(image_bytes, file.content_type)
#     except Exception as e:
#         raise HTTPException(status_code=502, detail=f"Food analysis failed: {str(e)}")
 
# @app.get("/health")
# def health_check():
#     return {"status": "ok", "mock": MOCK}

@app.get("/")
def root():
    return {"message": "Hello from FastAPI"}

@app.get("/dashboard")
def dashboard():
    return {"message": "Hello from FastAPI"}