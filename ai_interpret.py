from google import genai
import os

# NEVER hardcode API keys! Use environment variables or config
api_key = os.environ.get("GOOGLE_API_KEY")
if not api_key:
    raise ValueError("GOOGLE_API_KEY environment variable not set")

client = genai.Client(api_key=api_key)

OCR_TEXT = """
Smile Designing | Teeth Whitening THE Cu ITE TUSK.
Dental Implants | General Dentistry
Tab. Prymentin 625
Hexcgel ...
X tweek
"""

prompt = f"""
You are an AI that explains Indian doctor prescriptions.

Tasks:
- Fix OCR spelling mistakes
- Expand medical abbreviations (1-0-1 = morning and night)
- Identify ALL medicines present
- Infer common Indian drug usage
- Convert into patient-friendly instructions
- Do NOT diagnose

Return ONLY valid JSON array with fields:
name, purpose, dosage, timing, duration, warnings

OCR text:
{OCR_TEXT}



OCR text:
{OCR_TEXT}
"""

response = client.models.generate_content(
    model="models/gemini-flash-latest",
    contents=prompt
)

print(response.text)
