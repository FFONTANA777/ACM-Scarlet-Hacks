from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import google.generativeai as genai
import os
from dotenv import load_dotenv
from supabase import create_client, Client
from datetime import date, timedelta
from typing import Optional
# from vision import analyze_food_image, FoodAnalysis

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

@app.get("/test")
def test():
    result = supabase.table("profiles").select("*").execute()
    return result.data

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

# # --- Constants ---
# PET_STATES = [
#     (0.8, "thriving"),
#     (0.6, "happy"),
#     (0.4, "neutral"),
#     (0.2, "tired"),
#     (0.0, "sad"),
# ]

# STREAK_MILESTONES = {7, 14, 30, 60, 100} # Change depending on game balances

# # --- Scoring helpers ---
 
# def score_sleep(hours: float, ideal: float) -> float:
#     """
#     Summary:
#         Bell-curve around ideal. Penalizes both under and over.

#     Args:
#         hours (float): user's hour of sleep
#         ideal (float): personal ideals

#     Returns:
#         float: sleep score
#     """
#     diff = abs(hours - ideal)
#     return max(0.0, 1.0 - (diff / ideal))
 
 
# def score_calories(cals: int, ideal: float) -> float:
#     """
#     Summary:
#         Symmetric tolerance band ±500 kcal around ideal.

#     Args:
#         cals (int): user's calorie intake
#         ideal (float): personal ideals

#     Returns:
#         float: calorie score
#     """
#     diff = abs(cals - ideal)
#     tolerance = ideal * 0.25  # ±25% of personal ideal = perfect score
#     if diff <= tolerance:
#         return 1.0
#     return max(0.0, 1.0 - ((diff - tolerance) / ideal))
 
 
# def score_steps(steps: int,  ideal: float) -> float:
#     """
#     Summary:
#         Reward up to ideal, soft cap after.

#     Args:
#         steps (int): user's steps
#         ideal (float): personal ideals

#     Returns:
#         float: steps score
#     """
#     return min(1.0, steps / ideal)
 
 
# def score_mood(mood: int) -> float:
#     """
#     Summary:
#         Normalize 1–5 scale to 0–1.

#     Args:
#         mood (int): user's mood rate

#     Returns:
#         float: mood score
#     """
#     return (mood - 1) / 4.0
 
 
# def compute_health_score(sleep: float, calories: int, steps: int, mood: int, sleep_ideal: float, calories_ideal: float, steps_ideal: float, consistency_bonus: float,) -> float:
#     """
#     Summary:
#         Using the base score helpers to determine health score.

#     Args:
#         sleep (float): user's hour of sleep
#         calories (int): user's calorie intake
#         steps (int): user's steps
#         mood (int): user's mood rate
    
#     Returns 
#         float: health score

#     """
#     weights = {"sleep": 0.30, "calories": 0.25, "steps": 0.25, "mood": 0.20}
#     raw = (
#         weights["sleep"]    * score_sleep(sleep, sleep_ideal)       +
#         weights["calories"] * score_calories(calories, calories_ideal) +
#         weights["steps"]    * score_steps(steps, steps_ideal)       +
#         weights["mood"]     * score_mood(mood)
#     )
#     return round(min(1.0, max(0.0, raw + consistency_bonus)), 4)
 
 
# def score_to_pet_state(score: float) -> str:
#     """
#     Summary:
#         Using the base score helpers to determine health score.

#     Args:
#         score (float): health score
    
#     Returns 
#         str: pet state

#     """
#     for threshold, state in PET_STATES:
#         if score >= threshold:
#             return state
#     return "sad"

# # --- Streak logic ---
 
# def compute_streak(user_id: str) -> int:
#     """
#     Summary:
#         Count consecutive days with a check-in, going backwards from yesterday.
#         Today's check-in (being inserted now) will extend this by 1.

#     Args:
#         user_id (str): user ID
    
#     Returns:
#         int: streak score

#     """
#     if MOCK:
#         return 3
 
#     result = (
#         supabase.table("checkins")
#         .select("created_at")
#         .eq("user_id", user_id)
#         .order("created_at", desc=True)
#         .execute()
#     )
 
#     checkin_dates = {
#         date.fromisoformat(row["created_at"][:10])
#         for row in result.data
#     }
 
#     streak = 0
#     check_date = date.today() - timedelta(days=1)
#     while check_date in checkin_dates:
#         streak += 1
#         check_date -= timedelta(days=1)
 
#     return streak + 1

# # --- Fetch history for ML ---
 
# def fetch_checkin_history(user_id: str) -> list[dict]:
#     """
#     Summary:
#         Fetch all past check-ins for a user, oldest first, for ML training.

#     Args:
#         user_id (str): user ID
    
#     Returns:
#         list[dict]: check in history
#     """
#     if MOCK:
#         # Return some fake history so ML has something to work with in testing
#         return [
#             {"sleep_hours": 7.0, "calories": 1900, "steps": 7500},
#             {"sleep_hours": 6.5, "calories": 2100, "steps": 6000},
#             {"sleep_hours": 7.5, "calories": 1800, "steps": 8200},
#             {"sleep_hours": 7.0, "calories": 2000, "steps": 7000},
#             {"sleep_hours": 6.0, "calories": 2200, "steps": 5500}
#         ]
 
#     result = (
#         supabase.table("checkins")
#         .select("sleep_hours, calories, steps")
#         .eq("user_id", user_id)
#         .order("created_at", desc=False)
#         .execute()
#     )
#     return result.data

# # --- One check-in per day guard ---
 
# def already_checked_in_today(user_id: str) -> bool:
#     if MOCK:
#         return False
 
#     result = (
#         supabase.table("checkins")
#         .select("id")
#         .eq("user_id", user_id)
#         .gte("created_at", str(date.today()))
#         .limit(1)
#         .execute()
#     )
#     return len(result.data) > 0

# # --- AI message ---

# def classify_sleep_timing(sleep_time: Optional[str], wake_time: Optional[str]) -> str:
#     """
#     Returns a short natural-language note about sleep timing for the pet message.
#     sleep_time / wake_time are "HH:MM" strings (24h).
#     """
#     note = ""
#     if sleep_time:
#         try:
#             h, m = map(int, sleep_time.split(":"))
#             hour = h + m / 60
#             if hour < 21:
#                 note += "Your owner went to bed really early tonight. "
#             elif hour < 23:
#                 note += "Your owner got to bed at a healthy time. "
#             elif hour < 1 or hour >= 23:
#                 note += "Your owner stayed up quite late last night. "
#             else:
#                 note += "Your owner went to bed very late — well past midnight. "
#         except ValueError:
#             pass
#     if wake_time:
#         try:
#             h, m = map(int, wake_time.split(":"))
#             hour = h + m / 60
#             if hour < 6:
#                 note += "They woke up very early. "
#             elif hour < 8:
#                 note += "They woke up at a great time. "
#             elif hour < 10:
#                 note += "They had a bit of a slow morning start. "
#             else:
#                 note += "They slept in pretty late. "
#         except ValueError:
#             pass
#     return note.strip()

# PET_PERSONALITY = """
# You are a small, expressive virtual pet. You speak in first person,
# in a warm and playful tone — like a Tamagotchi that has feelings.
# Keep your message to 1-2 sentences. React to how the user is doing today.
# Never mention numbers or metrics directly. Just express how you feel based on their state.
# """
 
# STATE_PROMPTS = {
#     "thriving": "Your owner had a fantastic day — great sleep, nutrition, activity, and mood. You feel absolutely amazing.",
#     "happy":    "Your owner had a pretty good day. You feel energetic and cheerful.",
#     "neutral":  "Your owner had an okay day — not great, not bad. You feel fine but a little quiet.",
#     "tired":    "Your owner struggled a bit today — maybe not enough sleep or activity. You feel low energy.",
#     "sad":      "Your owner really didn't take care of themselves today. You feel sad and a little worried.",
# }
 
# def generate_pet_message(
#     pet_state: str,
#     streak: int,
#     sleep_time: Optional[str] = None,
#     wake_time: Optional[str] = None,
# ) -> str:
#     streak_note = ""
#     if streak >= 7:
#         streak_note = f" We've been together for {streak} days in a row — that means a lot to me."
 
#     sleep_note = classify_sleep_timing(sleep_time, wake_time)
#     sleep_context = f" {sleep_note}" if sleep_note else ""
 
#     prompt = f"{STATE_PROMPTS[pet_state]}{streak_note}{sleep_context} Write a first-person message from the pet."
 
#     model = genai.GenerativeModel(
#         model_name="gemini-2.5-flash",
#         system_instruction=PET_PERSONALITY,
#     )
#     response = model.generate_content(
#         prompt,
#         generation_config={"max_output_tokens": 100},
#     )
#     return response.text.strip()

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
 
# ALLOWED_MEDIA_TYPES = {"image/jpeg", "image/jpg", "image/png", "image/webp", "image/gif"}
 
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
 
# @app.get("/health")
# def health_check():
#     return {"status": "ok", "mock": MOCK}

@app.get("/")
def root():
    return {"message": "Hello from FastAPI"}

@app.get("/dashboard")
def dashboard():
    return {"message": "Hello from FastAPI"}