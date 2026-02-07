import pytesseract
from PIL import Image
from google import genai

client = genai.Client(api_key="AIzaSyCvphqIp4rjmJKjwD4kqJORPo_nz0lW1zc")


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

    response = client.models.generate_content(
        model="models/gemini-flash-latest",
        contents=prompt
    )

    return clean_json(response.text)
