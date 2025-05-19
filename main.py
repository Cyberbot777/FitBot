from fastapi import FastAPI
import openai
from dotenv import load_dotenv
import os
import json
import random
import requests

# Load environment variables from .env
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")
USDA_API_KEY = os.getenv("USDA_API_KEY")

# Create FastAPI app
app = FastAPI()

# Load exercise data from exercises.json
with open("exercises.json", "r") as file:
    exercises = json.load(file)

# Endpoint for motivation (using OpenAI)
@app.get("/motivate")
def motivate(goal: str = "stay fit"):
    prompt = f"Give a short motivational message for someone trying to {goal}."
    response = openai.chat.completions.create(
    model="gpt-4",
    messages=[{"role": "user", "content": prompt}],
    max_tokens=50
)
    return {"message": response.choices[0].message.content}

# Endpoint for fitness plan (using exercises.json)
@app.get("/fitness-plan")
def fitness_plan(equipment: str = "none"):
    filtered = [ex for ex in exercises if equipment.lower() in ex.get("equipment", "").lower()]
    selected = random.sample(filtered, min(3, len(filtered)))
    return {"plan": [{"name": ex["name"], "instructions": ex["instructions"]} for ex in selected]}

# Endpoint for food plan (using USDA API)
@app.get("/food-plan")
def food_plan(dietary: str = "general"):
    url = f"https://api.nal.usda.gov/fdc/v1/foods/search?query={dietary}&api_key={USDA_API_KEY}"
    response = requests.get(url)
    if response.status_code != 200:
        return {"error": "Failed to fetch food data"}
    foods = response.json().get("foods", [])[:3]
    return {"plan": [{"name": food["description"], "calories": food.get("foodNutrients", [{}])[0].get("value", 0)} for food in foods]}