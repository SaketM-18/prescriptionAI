from PIL import Image
import json, os, time
import google.generativeai as genai

# Configure API Key globally
api_key = os.environ.get("GOOGLE_API_KEY")
if not api_key:
    print("❌ GOOGLE_API_KEY not found in environment variables!")
else:
    genai.configure(api_key=api_key)

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

        # Resize image to reduce memory usage and payload size
        img = Image.open(image_path)
        img = img.convert("RGB")
        img.thumbnail((1024, 1024))  # Max 1024x1024
        buffer = io.BytesIO()
        img.save(buffer, format="JPEG", quality=85)
        image_data = buffer.getvalue()
        # Re-open as PIL image for SDK
        pil_image = Image.open(io.BytesIO(image_data))
    except Exception as e:
        return json.dumps({"error": f"Could not read image: {e}"})

    prompt = f"""
    You are a helpful medical assistant for rural villagers. 
    Analyze this prescription image and extract medicines.
    Also check if any of the medicines have dangerous interactions with each other.

    Return ONLY valid JSON.
    Structure:
    {{
        "english": [
            {{ "name": "Medicine Name", "dosage": "Dosage (e.g. 500mg)", "timing": "Frequency (e.g. 1-0-1)", "instructions": "When to take (e.g. After food)" }}
        ],
        "translated": [
            {{ "name": "Medicine Name", "dosage": "Dosage", "timing": "Frequency", "instructions": "Translated instructions in {language}" }}
        ],
        "dangerous_combinations": [
            {{ "medicines": ["Med A", "Med B"], "reason": "Reason in {language}" }}
        ]
    }}
    """

    # Models to try (standard names for google-generativeai SDK)
    models = [
        "gemini-2.0-flash",           # Primary
        "gemini-1.5-flash",           # Standard
        "gemini-1.5-flash-001",       # Specific version
        "gemini-1.5-flash-002",       # Specific version
        "gemini-1.5-pro",
        "gemini-1.5-pro-001",
        "gemini-1.5-pro-002",
    ]

    max_retries = 3
    final_error = None

    for i, model_name in enumerate(models):
        print(f"🤖 Trying model: {model_name}...")
        
        for retry in range(max_retries):
            try:
                # Initialize model
                model = genai.GenerativeModel(model_name)
                
                # Generate content
                response = model.generate_content(
                    [prompt, pil_image],
                    generation_config=genai.types.GenerationConfig(
                        temperature=0.2,
                        response_mime_type="application/json"
                    )
                )
                
                # Check response
                if not response.text:
                    raise ValueError("Empty response from API")
                    
                json_str = clean_json(response.text)
                print(f"✅ Success with {model_name}")
                return json_str

            except Exception as e:
                error_str = str(e)
                print(f"⚠️ Error with {model_name} (Attempt {retry+1}/{max_retries}): {error_str}")
                
                # Handle Resource Exhausted (429)
                if "429" in error_str or "quota" in error_str.lower():
                    if retry < max_retries - 1:
                        time.sleep(1) # Very short wait, better to fail fast to next model
                        continue
                    else:
                        print(f"❌ Quota exceeded for {model_name}. Switching model...")
                        break # Break inner loop to try next model
                
                # Handle Not Found (404) - specific to model version
                elif "404" in error_str or "not found" in error_str.lower():
                    print(f"❌ Model {model_name} not found. Switching model...")
                    break # Break inner loop immediately to try next model

                # Other errors - wait and retry
                else:
                    if retry < max_retries - 1:
                        time.sleep(1)
                    else:
                        final_error = str(e)
        
        # If we broke out of retry loop, outer loop continues to next model

    # If all models failed
    return json.dumps({
        "error": f"All AI models failed. Please try again. Last error: {final_error}",
        "english": [], 
        "translated": [], 
        "dangerous_combinations": []
    })
