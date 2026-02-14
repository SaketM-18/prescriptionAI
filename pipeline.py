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
Also check if any of the medicines have dangerous interactions with each other.

Return ONLY a valid JSON object with this exact structure:

{{
  "english": [
    {{
      "name": "Medicine Name",
      "purpose": "Simple purpose (e.g. for fever)",
      "dosage": "1-0-1",
      "visual_timing": "Use emojis: ☀️/🌤️/🌙. Example: ☀️ -- 🌙",
      "timing": "After food",
      "frequency": "After food",
      "duration": "5 days",
      "warnings": "Take with water",
      "precautions": "Take with water",
      "generic_alternative": "Name of cheaper generic version (if applicable)"
    }}
  ],
  "translated": [
    {{
      "name": "Medicine Name (keep original English name)",
      "purpose": "FULLY translated purpose in {language} script",
      "dosage": "1-0-1",
      "visual_timing": "Use emojis: ☀️/🌤️/🌙. Example: ☀️ -- 🌙",
      "timing": "FULLY translated in {language} script (e.g. for Hindi: खाने के बाद, for Kannada: ಊಟದ ನಂತರ)",
      "frequency": "Same as timing, FULLY translated in {language} script",
      "duration": "FULLY translated in {language} script (e.g. for Hindi: 5 दिन, for Kannada: 5 ದಿನಗಳು)",
      "warnings": "FULLY translated in {language} script",
      "precautions": "Same as warnings, FULLY translated in {language} script",
      "generic_alternative": "Medicine name + FULLY translated description in {language} script"
    }}
  ],
  "dangerous_combinations": [
    {{
      "medicines": "Medicine A + Medicine B",
      "risk": "Simple explanation of what could go wrong in English",
      "risk_translated": "Same explanation FULLY in {language} script",
      "severity": "high or medium"
    }}
  ]
}}

CRITICAL TRANSLATION RULES:
- In the "translated" array, EVERY value MUST be written in {language} script/language, NOT in English
- The medicine "name" can stay in English since it's a brand name
- But purpose, timing, frequency, duration, warnings, precautions, generic_alternative MUST ALL be in {language}
- Do NOT write English words like "After food", "5 days", "Morning-Afternoon-Night" in the translated array
- Instead write the {language} equivalent, for example in Kannada: "ಊಟದ ನಂತರ", "5 ದಿನಗಳು", "ಬೆಳಿಗ್ಗೆ-ಮಧ್ಯಾಹ್ನ-ರಾತ್ರಿ"
- The "timing" and "frequency" fields should have the same translated value
- The "warnings" and "precautions" fields should have the same translated value

IMPORTANT for dangerous_combinations:
- Check ALL pairs of medicines for known interactions
- If no dangerous combinations exist, return an empty array: "dangerous_combinations": []
- Use very simple language a villager can understand
- severity should be "high" for life-threatening or "medium" for uncomfortable side effects

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
