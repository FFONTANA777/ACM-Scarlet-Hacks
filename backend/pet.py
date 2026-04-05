import google.generativeai as genai
import os
from datetime import date, timedelta
from typing import Optional
from supabase import Client

MOCK = os.environ["MOCK"]

# =========
# Constants
# =========
PET_STATES = [
    (0.8, "thriving"),
    (0.6, "happy"),
    (0.4, "neutral"),
    (0.2, "tired"),
    (0.0, "sad"),
]

STREAK_MILESTONES = {7, 14, 30, 60, 100} # Change depending on game balances

# ===============
# Scoring helpers
# ===============
def score_sleep(hours: float, ideal: float) -> float:
    """
    Summary:
        Bell-curve around ideal. Penalizes both under and over.

    Args:
        hours (float): user's hour of sleep
        ideal (float): personal ideals

    Returns:
        float: sleep score
    """
    diff = abs(hours - ideal)
    return max(0.0, 1.0 - (diff / ideal))
 
 
def score_calories(cals: int, ideal: float) -> float:
    """
    Summary:
        Symmetric tolerance band ±500 kcal around ideal.

    Args:
        cals (int): user's calorie intake
        ideal (float): personal ideals

    Returns:
        float: calorie score
    """
    diff = abs(cals - ideal)
    tolerance = ideal * 0.25  # ±25% of personal ideal = perfect score
    if diff <= tolerance:
        return 1.0
    return max(0.0, 1.0 - ((diff - tolerance) / ideal))
 
 
def score_steps(steps: int,  ideal: float) -> float:
    """
    Summary:
        Reward up to ideal, soft cap after.

    Args:
        steps (int): user's steps
        ideal (float): personal ideals

    Returns:
        float: steps score
    """
    return min(1.0, steps / ideal)
 
 
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
 
 
def compute_health_score(sleep: float, calories: int, steps: int, mood: int, sleep_ideal: float, calories_ideal: float, steps_ideal: float, consistency_bonus: float,) -> float:
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
    weights = {"sleep": 0.30, "calories": 0.25, "steps": 0.25, "mood": 0.20}
    raw = (
        weights["sleep"]    * score_sleep(sleep, sleep_ideal)       +
        weights["calories"] * score_calories(calories, calories_ideal) +
        weights["steps"]    * score_steps(steps, steps_ideal)       +
        weights["mood"]     * score_mood(mood)
    )
    return round(min(1.0, max(0.0, raw + consistency_bonus)), 4)
 
 
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

# ===============
# Streak logic
# ===============
def compute_streak(user_id: str,  supabase: Client) -> int:
    """
    Summary:
        Count consecutive days with a check-in, going backwards from yesterday.
        Today's check-in (being inserted now) will extend this by 1.

    Args:
        user_id (str): user ID
    
    Returns:
        int: streak score

    """
    if MOCK:
        return 3
 
    result = (
        supabase.table("checkins")
        .select("created_at")
        .eq("user_id", user_id)
        .order("created_at", desc=True)
        .execute()
    )
 
    checkin_dates = {
        date.fromisoformat(row["created_at"][:10])
        for row in result.data
    }
 
    streak = 0
    check_date = date.today() - timedelta(days=1)
    while check_date in checkin_dates:
        streak += 1
        check_date -= timedelta(days=1)
 
    return streak + 1

# --- One check-in per day guard ---
 
def already_checked_in_today(user_id: str,  supabase: Client) -> bool:
    if MOCK:
        return False
 
    result = (
        supabase.table("checkins")
        .select("id")
        .eq("user_id", user_id)
        .gte("created_at", str(date.today()))
        .limit(1)
        .execute()
    )
    return len(result.data) > 0

# --- Sleep timing ---

def classify_sleep_timing(sleep_time: Optional[str], wake_time: Optional[str]) -> str:
    """
    Returns a short natural-language note about sleep timing for the pet message.
    sleep_time / wake_time are "HH:MM" strings (24h).
    """
    note = ""
    if sleep_time:
        try:
            h, m = map(int, sleep_time.split(":"))
            hour = h + m / 60
            if hour < 21:
                note += "Your owner went to bed really early tonight. "
            elif hour < 23:
                note += "Your owner got to bed at a healthy time. "
            elif hour < 1 or hour >= 23:
                note += "Your owner stayed up quite late last night. "
            else:
                note += "Your owner went to bed very late — well past midnight. "
        except ValueError:
            pass
    if wake_time:
        try:
            h, m = map(int, wake_time.split(":"))
            hour = h + m / 60
            if hour < 6:
                note += "They woke up very early. "
            elif hour < 8:
                note += "They woke up at a great time. "
            elif hour < 10:
                note += "They had a bit of a slow morning start. "
            else:
                note += "They slept in pretty late. "
        except ValueError:
            pass
    return note.strip()

# --- AI message ---

PET_PERSONALITY = """
You are a small, expressive virtual pet. You speak in first person,
in a warm and playful tone — like a Tamagotchi that has strong feelings and opinions.
Always write exactly 2 full sentences. Each sentence must be complete and expressive — no one-word reactions.
React to how the user is doing. Never mention raw numbers or metrics. Be specific about the situation.
"""
 
STATE_PROMPTS = {
    "thriving": "Your owner had a fantastic day — great sleep, nutrition, activity, and mood. You feel absolutely amazing.",
    "happy":    "Your owner had a pretty good day. You feel energetic and cheerful.",
    "neutral":  "Your owner had an okay day — not great, not bad. You feel fine but a little quiet.",
    "tired":    "Your owner struggled a bit today — maybe not enough sleep or activity. You feel low energy.",
    "sad":      "Your owner really didn't take care of themselves today. You feel sad and a little worried.",
}
 
def generate_stat_message(
    stat_type: str,
    value: float,
    goal_value: float,
    fitness_goal: str,
    pet_state: str,
    current_hour: float,
    upcoming: list,
) -> str:
    ratio = value / goal_value if goal_value > 0 else 1.0

    if current_hour < 12:
        time_of_day = "morning"
    elif current_hour < 17:
        time_of_day = "afternoon"
    else:
        time_of_day = "evening"

    checkpoint_note = f" They still need to: {', '.join(upcoming)}." if upcoming else ""

    if stat_type == "sleep":
        if ratio >= 1.1:
            tone = "tease them lovingly — they slept in a bit too much, call them a little sleepyhead"
        elif ratio >= 0.9:
            tone = "cheer them on — they nailed their sleep, you feel so well-rested because of them"
        elif ratio >= 0.7:
            tone = "gently worry — they didn't quite get enough sleep, you feel a little groggy"
        else:
            tone = "dramatically complain — they barely slept at all, you're exhausted on their behalf, maybe guilt-trip them a little"

        prompt = (
            f"Your owner logged their sleep for the {time_of_day}. "
            f"They slept {'more than' if ratio > 1 else 'less than'} their goal "
            f"({'a lot more' if ratio >= 1.3 else 'a bit more' if ratio >= 1.1 else 'a bit less' if ratio >= 0.7 else 'way less'}). "
            f"The pet feels {pet_state}.{checkpoint_note} "
            f"Your job: {tone}. "
            f"Write exactly 2 full expressive sentences in first person. Do not use numbers. Make each sentence at least 8 words long."
        )

    elif stat_type == "steps":
        if ratio >= 1.3:
            tone = "go absolutely wild with hype — they absolutely demolished their step goal, you're losing your mind with pride"
        elif ratio >= 1.0:
            tone = "cheer them on warmly — they hit their step goal, you feel so proud and energetic"
        elif ratio >= 0.6:
            tone = "tease them a little — they were kinda lazy today, gently roast them for it"
        else:
            tone = "dramatically roast them — they barely moved at all today, call them a couch potato with love"

        prompt = (
            f"Your owner just logged their steps for the {time_of_day}. "
            f"They got {'way more than' if ratio >= 1.3 else 'more than' if ratio >= 1.0 else 'about' if ratio >= 0.8 else 'less than half of'} their step goal. "
            f"The pet feels {pet_state}.{checkpoint_note} "
            f"Your job: {tone}. "
            f"Write exactly 2 full expressive sentences in first person. Do not use numbers. Make each sentence at least 8 words long."
        )

    else:  # calories
        if fitness_goal == "Bulk":
            if ratio >= 1.0:
                tone = "hype them up — they ate enough to fuel those gains, you're so proud of the dedication"
            else:
                tone = "guilt-trip them with love — they didn't eat enough for their bulk, remind them muscles need food"
        elif fitness_goal == "Cut":
            if ratio <= 1.0:
                tone = "cheer them on — their discipline is real, you're so impressed by their willpower"
            else:
                tone = "tease them like a little gremlin — they went over their cut goal, lovingly call them out for it"
        else:  # Maintain
            diff = abs(value - goal_value)
            if diff <= goal_value * 0.1:
                tone = "praise them — perfect balance, they're nailing the maintenance life"
            elif value > goal_value:
                tone = "tease them — they ate a bit too much, playfully question their choices"
            else:
                tone = "softly worry — they didn't eat enough, encourage them to fuel up"

        prompt = (
            f"Your owner logged their calories for the {time_of_day}. "
            f"Their fitness goal is to {fitness_goal.lower()}. "
            f"They ate {'more than' if value > goal_value else 'less than' if value < goal_value else 'exactly'} their calorie goal "
            f"({'way more' if ratio > 1.3 else 'a bit more' if ratio > 1.0 else 'way less' if ratio < 0.7 else 'a bit less'}). "
            f"The pet feels {pet_state}.{checkpoint_note} "
            f"Your job: {tone}. "
            f"Write exactly 2 full expressive sentences in first person. Do not use numbers. Make each sentence at least 8 words long."
        )

    model = genai.GenerativeModel(
        model_name="gemini-2.5-flash",
        system_instruction=PET_PERSONALITY,
    )
    response = model.generate_content(
        prompt,
        generation_config={"max_output_tokens": 2048},
    )
    return response.text.strip()


def generate_pet_message(
    pet_state: str,
    streak: int,
    sleep_time: Optional[str] = None,
    wake_time: Optional[str] = None,
) -> str:
    streak_note = ""
    if streak >= 7:
        streak_note = f" We've been together for {streak} days in a row — that means a lot to me."
 
    sleep_note = classify_sleep_timing(sleep_time, wake_time)
    sleep_context = f" {sleep_note}" if sleep_note else ""
 
    prompt = f"{STATE_PROMPTS[pet_state]}{streak_note}{sleep_context} Write a first-person message from the pet."
 
    model = genai.GenerativeModel(
        model_name="gemini-2.5-flash",
        system_instruction=PET_PERSONALITY,
    )
    response = model.generate_content(
        prompt,
        generation_config={"max_output_tokens": 2048},
    )
    return response.text.strip()