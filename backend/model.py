from pydantic import BaseModel, Field
from typing import Optional

# ============================
# Response Models + DB Objects
# ============================
class User(BaseModel):
    email: str
    password: str
    username: str
    pet_name: str

class UserRegister(BaseModel):
    email: str
    password: str
    username: str
    pet_name: str = "Buddy"

class UserLogin(BaseModel):
    email: str
    password: str

class LoginResponse(BaseModel):
    access_token: str
    user_id: str
    username: str
    pet_name: str

class Profile(BaseModel):
    uuid: str
    username: str
    pet_name: str
    created_date: str

class ProfileResponse(BaseModel):
    id: str
    username: str
    pet_name: str
    created_at: str

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

class CheckInRequest(BaseModel):
    user_id: str
    checkpoint: str  # wake | gym | breakfast | lunch | dinner | sleep
 
 
class CheckInResponse(BaseModel):
    username: str
    health_score: float
    pet_state: str
    streak: int
    streak_milestone: bool
    message: str

class StatMessageRequest(BaseModel):
    user_id: str
    stat_type: str       # "sleep" | "steps" | "calories"
    value: float         # hours for sleep, count for steps, kcal for calories
    goal_value: float    # user's personal goal for this stat
    fitness_goal: str    # "Cut" | "Bulk" | "Maintain"