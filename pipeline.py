from PIL import Image
import json, os, time
from google import genai
from google.genai import types

client = None
def get_client():
    global client
    if client is None:
        api_key = os.environ.get("GOOGLE_API_KEY")
        if not api_key:
            print("❌ GOOGLE_API_KEY not found in environment variables!")
        client = genai.Client(api_key=api_key)
    return client


def clean_json(text):
    text = text.strip()

    if text.startswith("```"):
        text = text.replace("```", "").strip()

    if text.lower().startswith("json"):
        text = text[4:].strip()

    return text


def run_pipeline(image_path, language):
    # Load image for Gemini (Multimodal)
    try:
        from PIL import Image
        import io

        # Resize image to reduce memory usage
        img = Image.open(image_path)
        img = img.convert("RGB")
        img.thumbnail((1024, 1024))  # Max 1024x1024
        buffer = io.BytesIO()
        img.save(buffer, format="JPEG", quality=85)
        image_data = buffer.getvalue()
        del img, buffer  # Free memory
    except Exception as e:
        return json.dumps({"error": f"Could not read image: {e}"})

    prompt = f"""
    You are a helpful medical assistant for rural villagers. 
    Analyze this prescription image and extract medicines.
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
    """

    # Retry with fallback models on 503 errors
    models = [
        "gemini-2.0-flash",           # Primary
        "gemini-1.5-flash-002",       # Fallback 1 (Specific version)
        "gemini-1.5-pro-002",         # Fallback 2 (Specific version)
        "gemini-1.5-flash-8b"         # Fallback 3 (Lightweight)
    ]

    max_retries = 3

    for i, model_name in enumerate(models):
        for retry in range(max_retries):
            try:
                client = get_client()
                response = client.models.generate_content(
                    model=model_name,
                    contents=[prompt, types.Part.from_bytes(data=image_data, mime_type="image/jpeg")]
                )
            
                result = clean_json(response.text)
                # del image_data  # Free memory after success (optional, python is garbage collected)
                return result

            except Exception as e: 
                error_str = str(e)
                
                # Handle quota exhaustion (429 error)
                if "429" in error_str or "RESOURCE_EXHAUSTED" in error_str:
                    wait_time = retry + 1  # Linear backoff: 1s, 2s, 3s (keep it short for web request)
                    print(f"⚠️ Quota exceeded. Waiting {wait_time}s before retry {retry+1}/{max_retries}...")
                    time.sleep(wait_time)
                    
                    if retry == max_retries - 1:
                        print(f"❌ Max retries reached for {model_name} due to quota limits")
                        if i < len(models) - 1:
                            print(f"🔄 Switching to {models[i+1]}...")
                            break  # Try next model
                        else:
                            return json.dumps({
                                "error": "Server is busy (API quota exceeded). Please try again in a minute.",
                                "english": [], 
                                "translated": [], 
                                "dangerous_combinations": []
                            })
                    continue
                
                # Handle 404 model not found
                elif "404" in error_str or "NOT_FOUND" in error_str:
                    print(f"❌ Model {model_name} not found. Trying next model...")
                    break  # Try next model immediately
                
                # Other errors
                else:
                    if retry < max_retries - 1:
                        wait_time = 2 ** retry  # 1s, 2s, 4s
                        print(f"⚠️ Error with {model_name}: {e}. Retrying in {wait_time}s...")
                        time.sleep(wait_time)
                    else:
                        print(f"❌ Model {model_name} failed after {max_retries} retries: {e}")
                        if i < len(models) - 1:
                            break  # Try next model
                        else:
                            return json.dumps({
                                "error": f"All models failed: {e}",
                                "english": [], 
                                "translated": [], 
                                "dangerous_combinations": []
                            })

    # If we get here, all models and retries failed
    return json.dumps({
        "error": "All API attempts failed. Please try again later.",
        "english": [], 
        "translated": [], 
        "dangerous_combinations": []
    })
            

