import pytesseract
from PIL import Image
import json, os, time
from google import genai

with open("key.json") as f:
    key_data = json.load(f)

client = genai.Client(api_key=key_data["api_key"])


def extract_text(image_path):
    return pytesseract.image_to_string(Image.open(image_path))


def clean_json(text):
    text = text.strip()

    if text.startswith("```"):
        text = text.replace("```", "").strip()

    if text.lower().startswith("json"):
        text = text[4:].strip()

    return text


def run_pipeline(image_path, language):
    ocr = extract_text(image_path)

    prompt = f"""
You are a helpful medical assistant for villagers. 
Analyze this prescription and extract medicines.

Return ONLY a valid JSON object with this exact structure:

{{
  "english": [
    {{
      "name": "Medicine Name",
      "purpose": "Simple purpose (e.g. for fever)",
      "dosage": "1-0-1 (Morning-Afternoon-Night)",
      "visual_timing": "Use emojis: ☀️/🌤️/🌙. Example: ☀️ -- 🌙",
      "timing": "After food",
      "duration": "3 days",
      "warnings": "Take with water",
      "generic_alternative": "Name of cheaper generic version (if applicable)"
    }}
  ],
  "translated": [
    {{
      "name": "Medicine Name in {language}",
      "purpose": "Simple purpose in {language}",
      "dosage": "1-0-1 (Morning-Afternoon-Night) in {language}",
      "visual_timing": "Use emojis: ☀️/🌤️/🌙. Example: ☀️ -- 🌙",
      "timing": "After food in {language}",
      "duration": "3 days in {language}",
      "warnings": "Take with water in {language}",
      "generic_alternative": "Name of cheaper generic version in {language}"
    }}
  ]
}}

Ensure the "translated" list is fully translated into {language}.
Keep the explanation very simple and easy to understand for a villager.
Do NOT use markdown code blocks (```json). Just return raw JSON string.

OCR Text:
{ocr}
"""

    # Retry with fallback models on 503 errors
    models = ["models/gemini-flash-latest", "gemini-2.0-flash", "gemini-2.0-flash-lite"]
    for i, model in enumerate(models):
        try:
            response = client.models.generate_content(
                model=model,
                contents=prompt
            )
            return clean_json(response.text)
        except Exception as e:
            if ("503" in str(e) or "429" in str(e)) and i < len(models) - 1:
                print(f"Model {model} unavailable, trying {models[i+1]}...")
                time.sleep(2)
                continue
            raise
