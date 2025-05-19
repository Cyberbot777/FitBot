from fastapi import FastAPI
import openai
from dotenv import load_dotenv
import os
import requests
import json
from typing import Dict, List, Any
import time  # Add this import

# Load environment variables from .env
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")
USDA_API_KEY = os.getenv("USDA_API_KEY")

# Create FastAPI app
app = FastAPI()

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

# Endpoint for fitness plan (using OpenAI)
@app.get("/fitness-plan")
def fitness_plan(equipment: str = "none"):
    # Add timestamp to prompt for variability
    timestamp = int(time.time())
    prompt = (
        f"Create a fitness plan with 3 unique exercises for someone using {equipment} equipment at timestamp {timestamp}. "
        f"Ensure the exercises are varied each time this prompt is run by selecting different, less common exercises "
        f"(avoid overused exercises like push-ups and squats unless specifically requested). "
        f"For each exercise, provide the name and a short list of instructions (2-4 steps). "
        f"Return the response as a JSON object with a 'plan' key, where the value is an array of exercises, "
        f"each with 'name' and 'instructions' keys."
    )
    try:
        response = openai.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=300
        )
        # Type hint for clarity
        result: str = response.choices[0].message.content
        # Parse the JSON response
        parsed_response: Dict[str, List[Dict[str, Any]]] = json.loads(result)
        if "plan" not in parsed_response:
            return {"error": "OpenAI response missing 'plan' key"}
        return parsed_response
    except (json.JSONDecodeError, KeyError, ValueError) as e:
        return {"error": f"Failed to parse OpenAI response: {str(e)}"}

# Endpoint for food plan (using USDA API)
@app.get("/food-plan")
def food_plan(dietary: str = "general"):
    url = f"https://api.nal.usda.gov/fdc/v1/foods/search?query={dietary}&api_key={USDA_API_KEY}"
    response = requests.get(url)
    if response.status_code != 200:
        return {"error": "Failed to fetch food data"}
    foods = response.json().get("foods", [])[:3]
    return {"plan": [{"name": food["description"], "calories": food.get("foodNutrients", [{}])[0].get("value", 0)} for food in foods]}