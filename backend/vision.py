import json
import re
import os
from dotenv import load_dotenv
import google.generativeai as genai
from pydantic import BaseModel

load_dotenv()

genai.configure(api_key=os.environ["GEMINI_API_KEY"])

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

def extract_json(text: str) -> str:
    """Extract the JSON object from the response, however it's wrapped."""
    text = text.strip()
 
    # Strip code fences if present
    text = re.sub(r"^```(?:json)?\s*", "", text)
    text = re.sub(r"\s*```$", "", text)
    text = text.strip()
 
    # If it still doesn't start with {, find the first { and last }
    start = text.find("{")
    end   = text.rfind("}")
    if start != -1 and end != -1:
        return text[start:end + 1]
 
    return text

def analyze_food_image(image_bytes: bytes, media_type: str) -> FoodAnalysis:
    """
    Summary:
        Single Gemini call: image -> description + nutrition estimates.

    Args:
        image_bytes (bytes)
        media_type (str)

    Returns:
        FoodAnalysis: response model
    """
    image_part = {"mime_type": media_type, "data": image_bytes}

    model = genai.GenerativeModel(
        model_name="gemini-2.5-flash",
        system_instruction=VISION_SYSTEM,
    )

    response = model.generate_content(
        ["Identify the food in this photo and estimate the nutrition.", image_part],
        generation_config={
            "max_output_tokens": 2048,
            "temperature": 0.1,
        },
    )

    raw = extract_json(response.text)

    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        raise ValueError(f"Gemini returned unexpected format: {raw[:200]}")

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
