import base64
import json
import os
import anthropic
from pydantic import BaseModel

claude = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
 
# --- Response model ---
class FoodAnalysis(BaseModel):
    description: str
    calories: int
    protein_g: float
    carbs_g: float
    fat_g: float
    items: list[dict]

# --- Prompt ---
 
VISION_SYSTEM = """
                You are a nutrition estimation assistant with expert knowledge of food and calories.
                Given a photo of food, identify each item and estimate its nutrition.

                Respond ONLY with valid JSON — no markdown, no explanation, no code fences.

                Format:
                {
                  "description": "brief overall description",
                  "items": [
                    {
                      "name": "food item with portion",
                      "calories": 284,
                      "protein_g": 26.7,
                      "carbs_g": 0.0,
                      "fat_g": 6.2
                    }
                  ]
                }

                Guidelines:
                - Use realistic portion sizes based on what you see
                - Be as accurate as possible but estimates are fine
                - Include every distinct food item visible
                """
 
def analyze_food_image(image_bytes: bytes, media_type: str) -> FoodAnalysis:
    """
    Summary: 
        Single Claude call: image -> description + nutrition estimates.
        
    Args:
        image_bytes (bytes)
        media_type (str)

    Returns:
        FoodAnalysis: response model
    """
    image_b64 = base64.standard_b64encode(image_bytes).decode("utf-8")
 
    response = claude.messages.create(
        model="claude-opus-4-5",
        max_tokens=600,
        system=VISION_SYSTEM,
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "image",
                        "source": {
                            "type": "base64",
                            "media_type": media_type,
                            "data": image_b64,
                        },
                    },
                    {
                        "type": "text",
                        "text": "Identify the food in this photo and estimate the nutrition.",
                    },
                ],
            }
        ],
    )
 
    raw = response.content[0].text.strip()
 
    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        raise ValueError(f"Claude returned unexpected format: {raw[:200]}")
 
    items = data.get("items", [])
    if not items:
        raise ValueError("No food items could be identified in the image.")
 
    return FoodAnalysis(
        description=data.get("description", ""),
        calories=round(sum(i.get("calories", 0) for i in items)),
        protein_g=round(sum(i.get("protein_g", 0) for i in items), 1),
        carbs_g=round(sum(i.get("carbs_g", 0) for i in items), 1),
        fat_g=round(sum(i.get("fat_g", 0) for i in items), 1),
        items=[
            {
                "name":      i.get("name", "unknown"),
                "calories":  round(i.get("calories", 0)),
                "protein_g": round(i.get("protein_g", 0), 1),
                "carbs_g":   round(i.get("carbs_g", 0), 1),
                "fat_g":     round(i.get("fat_g", 0), 1),
            }
            for i in items
        ],
    )