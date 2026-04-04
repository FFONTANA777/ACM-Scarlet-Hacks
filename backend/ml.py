import torch
import torch.nn as nn
import torch.optim as optim
import numpy as np
from dataclasses import dataclass

# --- Hardcoded fallback ideals ---
DEFAULT_SLEEP    = 8.0
DEFAULT_CALORIES = 2000
DEFAULT_STEPS    = 8000
 
# Blend starts at 14 check-ins, fully learned by 30
BLEND_START = 14
BLEND_FULL  = 30

# --- Data class for baselines ---
@dataclass
class PersonalBaselines:
    sleep_ideal:    float
    calories_ideal: float
    steps_ideal:    float
    confidence:     float   # 0.0 = all defaults, 1.0 = fully personalized
    consistency_bonus: float  # 0.0 - 0.10 added to health score

# --- Model ---
 
class BaselineModel(nn.Module):
    """
    Summary:
        Learns a user's personal baseline for sleep, calories, steps.

    Args: 
        [1] normalized day index

    Returns:
        [3] predicted (sleep, calories, steps)
    """
    def __init__(self):
        super().__init__()
        self.fc = nn.Linear(1, 3)
 
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.fc(x)

# --- Training ---
 
def train_baseline_model(history: list[dict]) -> tuple[BaselineModel, np.ndarray]:
    """
    Summary:
        Train the model on a user's check-in history.
 
    Args:
        history (list[dict]): list of dicts with keys sleep_hours, calories, steps ordered oldest -> newest
 
    Returns:
        tuple[BaselineModel, np.ndarray]: trained model, array [sleep, calories, steps]
    """
    n = len(history)
    if n == 0:
        model = BaselineModel()
        return model, np.array([DEFAULT_SLEEP, DEFAULT_CALORIES, DEFAULT_STEPS])
 
    # Build tensors
    # X: normalized day indices [0, 1] so recent days count more
    x_raw = np.arange(n, dtype=np.float32)
    x_norm = x_raw / max(x_raw.max(), 1.0)
    X = torch.tensor(x_norm, dtype=torch.float32).unsqueeze(1)  # (n, 1)
 
    Y = torch.tensor(
        [[h["sleep_hours"], h["calories"], h["steps"]] for h in history],
        dtype=torch.float32,
    )  # (n, 3)
 
    # Normalize targets so the model trains stably across very different scales
    y_mean = Y.mean(dim=0)
    y_std  = Y.std(dim=0).clamp(min=1.0)
    Y_norm = (Y - y_mean) / y_std
 
    model     = BaselineModel()
    optimizer = optim.Adam(model.parameters(), lr=0.05)
    loss_fn   = nn.MSELoss()
 
    for _ in range(300):
        optimizer.zero_grad()
        pred = model(X)
        loss = loss_fn(pred, Y_norm)
        loss.backward()
        optimizer.step()
 
    # Predict baseline = what the model expects for the "next" day
    with torch.no_grad():
        next_day   = torch.tensor([[1.0]])  # normalized index for next entry
        pred_norm  = model(next_day)        # (1, 3)
        pred_raw   = (pred_norm * y_std + y_mean).squeeze().numpy()
 
    # Clamp to sane ranges
    learned = np.array([
        float(np.clip(pred_raw[0], 4.0, 12.0)),    # sleep 4-12h
        float(np.clip(pred_raw[1], 800, 5000)),     # calories 800-5000
        float(np.clip(pred_raw[2], 1000, 25000)),   # steps 1000-25000
    ])
 
    return model, learned

# --- Blending ---
 
def blend_baselines(learned: np.ndarray, n_checkins: int) -> tuple[np.ndarray, float]:
    """
    Summary:
        Blend learned baselines with hardcoded defaults based on data confidence.

    Args:
        learned (np.ndarray): array [sleep, calories, steps]
        n_checkins (int): days of check ins

    Returns: 
        blended_baselines, confidence (where confidence is 0.0-1.0)
    """
    if n_checkins < BLEND_START:
        confidence = 0.0
    elif n_checkins >= BLEND_FULL:
        confidence = 1.0
    else:
        confidence = (n_checkins - BLEND_START) / (BLEND_FULL - BLEND_START)
 
    defaults = np.array([DEFAULT_SLEEP, DEFAULT_CALORIES, DEFAULT_STEPS])
    blended  = (1 - confidence) * defaults + confidence * learned
 
    return blended, confidence

# --- Consistency score ---
 
def compute_consistency_bonus(today: dict, history: list[dict], baselines: np.ndarray) -> float:
    """
    Summary:
        Bonus (0.0 - 0.10) for how close today's metrics are to the user's own norm.
        Rewards consistency, not just hitting global ideals.

    Args:
        today (dict): a dict of today's metrics {"sleep_hours", "calories", "steps"}
        history (list[dict]): a dict of past metrics
        baselines (np.ndarray): baseline array
    
    Returns:
        float: consistency bonus
    """
    if not history:
        return 0.0
 
    sleep_ideal, cal_ideal, steps_ideal = baselines
 
    def proximity(value: float, ideal: float, scale: float) -> float:
        """How close is value to ideal, normalized by scale. Returns 0-1."""
        return max(0.0, 1.0 - abs(value - ideal) / scale)
 
    sleep_prox = proximity(today["sleep_hours"], sleep_ideal, max(sleep_ideal, 1.0))
    cal_prox   = proximity(today["calories"],    cal_ideal,   max(cal_ideal * 0.5, 1.0))
    steps_prox = proximity(today["steps"],       steps_ideal, max(steps_ideal, 1.0))
 
    avg_proximity = (sleep_prox + cal_prox + steps_prox) / 3.0
    return round(avg_proximity * 0.10, 4)  # max bonus is 0.10

# --- Public entry point ---
 
def get_personal_baselines(user_id: str, today_metrics: dict, history: list[dict]) -> PersonalBaselines:
    """
    Summary:
    Full pipeline: history -> trained model -> blended baselines + consistency bonus.
 
    Args:
        user_id (str):       for logging/future model persistence
        today_metrics (dict): dict with sleep_hours, calories, steps (not yet in history)
        history (list[dict]):       past check-ins ordered oldest -> newest
 
    Returns:
        PersonalBaselines with ideals to use in scoring + consistency bonus
    """
    n = len(history)
 
    _, learned      = train_baseline_model(history)
    blended, conf   = blend_baselines(learned, n)
    consistency     = compute_consistency_bonus(today_metrics, history, blended)
 
    return PersonalBaselines(
        sleep_ideal=round(blended[0], 2),
        calories_ideal=round(blended[1], 1),
        steps_ideal=round(blended[2], 1),
        confidence=round(conf, 3),
        consistency_bonus=consistency,
    )