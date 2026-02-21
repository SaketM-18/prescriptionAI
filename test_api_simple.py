"""Simple API test without image"""

from google import genai
from google.genai import types
from config import get_api_key

api_key = get_api_key()
client = genai.Client(api_key=api_key)

print("Testing simple text generation...")

try:
    response = client.models.generate_content(
        model="models/gemini-2.5-flash",
        contents="Say 'Hello, API works!' in JSON format: {\"message\": \"...\"}",
        config=types.GenerateContentConfig(
            temperature=0.1,
            response_mime_type="application/json"
        )
    )
    
    print(f"✅ Response: {response.text}")
except Exception as e:
    print(f"❌ Error: {e}")
