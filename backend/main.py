from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import google.generativeai as genai
import os
from dotenv import load_dotenv
from supabase import create_client, Client
from datetime import date, timedelta
from vision import analyze_food_image, FoodAnalysis

load_dotenv()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Clients ---
MOCK = True
if not MOCK:
    from supabase import create_client, Client
    supabase: Client = create_client(
        os.environ["SUPABASE_URL"],
        os.environ["SUPABASE_SERVICE_KEY"],
    )

genai.configure(api_key=os.environ["GEMINI_API_KEY"])
 
 
# --- Models ---
class CheckInRequest(BaseModel):
    user_id: str
    username: str
    sleep_hours: float = Field(..., ge=0, le=12)
    calories: int = Field(..., ge=0, le=10000)
    steps: int = Field(..., ge=0)
    mood: int = Field(..., ge=1, le=5)
 
 
class CheckInResponse(BaseModel):
    username: str  
    health_score: float          # 0.0 – 1.0
    pet_state: str               # thriving | happy | neutral | tired | sad
    streak: int                  # consecutive days
    streak_milestone: bool       # true if streak hit 7 / 14 / 30 / etc.
    message: str                 # first-person pet message from Claude

# --- Constants ---
PET_STATES = [
    (0.8, "thriving"),
    (0.6, "happy"),
    (0.4, "neutral"),
    (0.2, "tired"),
    (0.0, "sad"),
]

# Ideal targets (used for scoring)
SLEEP_IDEAL = 8.0       # hours
CALORIES_IDEAL = 2000   # kcal
STEPS_IDEAL = 8000      # steps

# Score weights (must sum to 1.0)
WEIGHTS = {
    "sleep": 0.30,
    "calories": 0.25,
    "steps": 0.25,
    "mood": 0.20,
}

STREAK_MILESTONES = {7, 14, 30, 60, 100} # Change depending on game balances

# --- Scoring helpers ---
 
def score_sleep(hours: float) -> float:
    """
    Summary:
        Bell-curve around ideal. Penalizes both under and over.

    Args:
        hours (float): user's hour of sleep

    Returns:
        float: sleep score
    """
    diff = abs(hours - SLEEP_IDEAL)
    return max(0.0, 1.0 - (diff / SLEEP_IDEAL))
 
 
def score_calories(cals: int) -> float:
    """
    Summary:
        Symmetric tolerance band ±500 kcal around ideal.

    Args:
        cals (int): user's calorie intake

    Returns:
        float: calorie score
    """
    diff = abs(cals - CALORIES_IDEAL)
    if diff <= 500:
        return 1.0
    return max(0.0, 1.0 - ((diff - 500) / CALORIES_IDEAL))
 
 
def score_steps(steps: int) -> float:
    """
    Summary:
        Reward up to ideal, soft cap after.

    Args:
        steps (int): user's steps

    Returns:
        float: steps score
    """
    return min(1.0, steps / STEPS_IDEAL)
 
 
def score_mood(mood: int) -> float:
    """
    Summary:
        Normalize 1–5 scale to 0–1.

    Args:
        mood (int): user's mood rate

    Returns:
        float: mood score
    """
    return (mood - 1) / 4.0
 
 
def compute_health_score(sleep: float, calories: int, steps: int, mood: int) -> float:
    """
    Summary:
        Using the base score helpers to determine health score.

    Args:
        sleep (float): user's hour of sleep
        calories (int): user's calorie intake
        steps (int): user's steps
        mood (int): user's mood rate
    
    Returns 
        float: health score

    """
    raw = (
        WEIGHTS["sleep"]    * score_sleep(sleep)    +
        WEIGHTS["calories"] * score_calories(calories) +
        WEIGHTS["steps"]    * score_steps(steps)    +
        WEIGHTS["mood"]     * score_mood(mood)
    )
    return round(min(1.0, max(0.0, raw)), 4)
 
 
def score_to_pet_state(score: float) -> str:
    """
    Summary:
        Using the base score helpers to determine health score.

    Args:
        score (float): health score
    
    Returns 
        str: pet state

    """
    for threshold, state in PET_STATES:
        if score >= threshold:
            return state
    return "sad"

# --- Streak logic ---
 
def compute_streak(user_id: str) -> int:
    """
    Summary:
        Count consecutive days with a check-in, going backwards from yesterday.
        Today's check-in (being inserted now) will extend this by 1.

    Args:
        user_id (str): user ID
    
    Returns 
        int: streak score

    """
    today = date.today()
    streak = 0
    check_date = today - timedelta(days=1)  # start from yesterday
 
    # Fetch all check-in dates for this user, sorted desc
    result = (
        supabase.table("checkins")
        .select("created_at")
        .eq("user_id", user_id)
        .order("created_at", desc=True)
        .execute()
    )
 
    checkin_dates = set()
    for row in result.data:
        d = date.fromisoformat(row["created_at"][:10])
        checkin_dates.add(d)
 
    while check_date in checkin_dates:
        streak += 1
        check_date -= timedelta(days=1)
 
    return streak + 1  # +1 for today

# --- AI message ---
 
PET_PERSONALITY = """
                You are a small, expressive virtual pet. You speak in first person, 
                in a warm and playful tone — like a Tamagotchi that has feelings.
                Keep your message to 1-2 sentences. React to how the user is doing today.
                Never mention numbers or metrics directly. Just express how you feel based on their state.
                """
 
STATE_PROMPTS = {
    "thriving": "Your owner had a fantastic day — great sleep, nutrition, activity, and mood. You feel absolutely amazing.",
    "happy":    "Your owner had a pretty good day. You feel energetic and cheerful.",
    "neutral":  "Your owner had an okay day — not great, not bad. You feel fine but a little quiet.",
    "tired":    "Your owner struggled a bit today — maybe not enough sleep or activity. You feel low energy.",
    "sad":      "Your owner really didn't take care of themselves today. You feel sad and a little worried.",
}
 
def generate_pet_message(pet_state: str, streak: int) -> str:
    streak_note = ""
    if streak >= 7:
        streak_note = f" We've been together for {streak} days in a row — that means a lot to me."
 
    prompt = f"{STATE_PROMPTS[pet_state]}{streak_note} Write a first-person message from the pet."
 
    model = genai.GenerativeModel(
        model_name="gemini-2.5-flash",
        system_instruction=PET_PERSONALITY,
    )
    response = model.generate_content(
        prompt,
        generation_config={"max_output_tokens": 100},
    )
    return response.text.strip()

# --- Routes ---
 
@app.post("/checkin", response_model=CheckInResponse)
def checkin(req: CheckInRequest):
    # 1. Compute health score
    health_score = compute_health_score(
        req.sleep_hours, req.calories, req.steps, req.mood
    )
 
    # 2. Map to pet state
    pet_state = score_to_pet_state(health_score)
 
    # 3. Compute streak (before insert so we read prior days)
    streak = compute_streak(req.user_id)
    streak_milestone = streak in STREAK_MILESTONES
 
    # 4. Persist check-in
    supabase.table("checkins").insert({
        "user_id": req.user_id,
        "username": req.username, 
        "sleep_hours": req.sleep_hours,
        "calories": req.calories,
        "steps": req.steps,
        "mood": req.mood,
        "health_score": health_score,
        "pet_state": pet_state,
        "streak": streak,
    }).execute()
    
    # 5. Upsert username into profiles so GET /pet can return it
    supabase.table("profiles").upsert({
        "user_id":  req.user_id,
        "username": req.username,
    }).execute()

    # 6. Generate AI pet message
    message = generate_pet_message(pet_state, streak)
 
    return CheckInResponse(
        health_score=health_score,
        pet_state=pet_state,
        streak=streak,
        streak_milestone=streak_milestone,
        message=message,
    )
 
 
@app.get("/pet/{user_id}")
def get_pet_state(user_id: str):
    """
    Summary:
        Returns the user's most recent pet state — for loading the dashboard without requiring a new check-in.
    Args:
        user_id (str): user ID
    """
    result = (
        supabase.table("checkins")
        .select("health_score, pet_state, streak, created_at")
        .eq("user_id", user_id)
        .order("created_at", desc=True)
        .limit(1)
        .execute()
    )
    
    # Fetch username from profiles
    profile = (
        supabase.table("profiles")
        .select("username")
        .eq("user_id", user_id)
        .limit(1)
        .execute()
    )
    username = profile.data[0]["username"] if profile.data else "You"

    if not result.data:
        return {
            "username": username,
            "health_score": 0.5,
            "pet_state": "neutral",
            "streak": 0,
            "streak_milestone": False,
            "checked_in_today": False,
        }
 
    row = result.data[0]
    checked_in_today = row["created_at"][:10] == str(date.today())
 
    return {
        "username": username,
        "health_score": row["health_score"],
        "pet_state": row["pet_state"],
        "streak": row["streak"],
        "streak_milestone": row["streak"] in STREAK_MILESTONES,
        "checked_in_today": checked_in_today,
    }

ALLOWED_MEDIA_TYPES = {"image/jpeg", "image/jpg", "image/png", "image/webp", "image/gif"}
 
@app.post("/analyze-food", response_model=FoodAnalysis)
async def analyze_food(file: UploadFile = File(...)):
    """
    Upload a food photo -> Claude Vision estimates calories + macros.
    Frontend uses the returned `calories` value to pre-fill the check-in form.
    """
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
    return {"status": "ok"}

@app.get("/")
def root():
    return {"message": "Hello from FastAPI"}

@app.get("/dashboard")
def dashboard():
    return {"message": "Hello from FastAPI"}