from PIL import Image, ImageEnhance, ImageFilter
import json, os, time, io
from config import get_api_key

def clean_json(text):
    text = text.strip()
    if text.startswith("```"):
        text = text.replace("```", "").strip()
    if text.lower().startswith("json"):
        text = text[4:].strip()
    return text

def preprocess_image(img):
    """Enhance image quality for better recognition"""
    try:
        # Convert to RGB if needed
        if img.mode != 'RGB':
            img = img.convert('RGB')
        
        # Enhance contrast
        enhancer = ImageEnhance.Contrast(img)
        img = enhancer.enhance(1.5)
        
        # Enhance sharpness
        enhancer = ImageEnhance.Sharpness(img)
        img = enhancer.enhance(2.0)
        
        # Enhance brightness
        enhancer = ImageEnhance.Brightness(img)
        img = enhancer.enhance(1.2)
        
        # Apply sharpening filter
        img = img.filter(ImageFilter.SHARPEN)
        
        return img
    except Exception as e:
        print(f"⚠️ Preprocessing error: {e}")
        return img

def run_pipeline(image_path, language):
    """Main pipeline for prescription processing"""
    
    # Step 1: Load and preprocess image
    try:
        import google.generativeai as genai  # Use OLD SDK that works!
        
        # Get API key (from environment or key.json)
        api_key = get_api_key()
        
        if not api_key:
            return json.dumps({
                "error": "API key not configured. Add GOOGLE_API_KEY to environment or create key.json",
                "english": [],
                "translated": [],
                "dangerous_combinations": []
            })
        
        # Configure API
        genai.configure(api_key=api_key)
        
        # Load image
        img = Image.open(image_path)
        print(f"📸 Original image: {img.size}, mode: {img.mode}")
        
        # Preprocess
        img = preprocess_image(img)
        
        # Resize to optimal size
        img.thumbnail((1024, 1024), Image.Resampling.LANCZOS)
        
        print(f"📸 Preprocessed: {img.size}")
        
    except Exception as e:
        print(f"❌ Image processing error: {e}")
        return json.dumps({
            "error": f"Image processing failed: {str(e)}",
            "english": [],
            "translated": [],
            "dangerous_combinations": []
        })
    
    # Step 2: Create prompt
    prompt = f"""Analyze this prescription image and extract medicine information.

Return ONLY valid JSON with this structure:
{{
  "english": [
    {{
      "name": "Medicine Name with strength (e.g., Paracetamol 500mg)",
      "purpose": "Simple purpose (e.g., for fever and pain)",
      "dosage": "Format: Morning-Afternoon-Night (e.g., 1-0-1, 1-1-1)",
      "visual_timing": "Emojis: ☀️ for morning, 🌤️ for afternoon, 🌙 for night",
      "timing": "When to take (e.g., After food, Before food)",
      "frequency": "Same as timing",
      "duration": "How long (e.g., 5 days, 2 weeks)",
      "warnings": "Warnings (e.g., Avoid alcohol, Take with water)",
      "precautions": "Same as warnings",
      "generic_alternative": "Cheaper option if available"
    }}
  ],
  "translated": [
    {{
      "name": "Medicine Name (keep English)",
      "purpose": "Translated to {language}",
      "dosage": "1-0-1 (keep format)",
      "visual_timing": "☀️ -- 🌙 (keep emojis)",
      "timing": "Translated to {language}",
      "frequency": "Translated to {language}",
      "duration": "Translated to {language}",
      "warnings": "Translated to {language}",
      "precautions": "Translated to {language}",
      "generic_alternative": "Translated to {language}"
    }}
  ],
  "dangerous_combinations": [
    {{
      "medicines": "Medicine A + Medicine B",
      "risk": "Risk in English",
      "risk_translated": "Risk in {language}",
      "severity": "high or medium"
    }}
  ]
}}

IMPORTANT:
- Recognize abbreviations: OD (once daily), BD (twice daily), TDS (three times), AC (before food), PC (after food)
- Convert to standard format (1-0-1 means morning and night)
- Translate all fields except medicine names to {language}
- If unclear, make educated guess
- Return ONLY JSON, no markdown"""

    # Step 3: Try models (using OLD SDK with correct model names)
    models = [
        "gemini-2.5-flash",      # Latest
        "gemini-2.0-flash",      # Stable
        "gemini-2.5-pro",        # Most capable
        "gemini-flash-latest"    # Alias
    ]
    
    for model_name in models:
        print(f"🤖 Trying {model_name}...")
        
        for attempt in range(3):
            try:
                print(f"   Attempt {attempt + 1}/3...")
                
                model = genai.GenerativeModel(model_name)
                response = model.generate_content(
                    [prompt, img],
                    generation_config=genai.types.GenerationConfig(
                        temperature=0.1,
                        max_output_tokens=4096,
                        response_mime_type="application/json"
                    )
                )
                
                print(f"   Got response from {model_name}")
                
                if response and response.text:
                    result = clean_json(response.text)
                    print(f"✅ Success with {model_name}")
                    
                    # Validate JSON
                    try:
                        data = json.loads(result)
                        if 'english' in data or 'translated' in data:
                            print(f"   Extracted {len(data.get('english', []))} medicines")
                            return result
                        else:
                            print(f"   Invalid response structure")
                    except Exception as parse_error:
                        print(f"   JSON parse error: {parse_error}")
                
                print(f"⚠️ Empty or invalid response from {model_name}")
                
            except Exception as e:
                error_msg = str(e)
                print(f"⚠️ {model_name} attempt {attempt+1}: {error_msg[:200]}")
                
                if "429" in error_msg or "quota" in error_msg.lower():
                    print("⏳ Quota exceeded, waiting 10s...")
                    time.sleep(10)
                    continue
                elif "404" in error_msg or "not found" in error_msg.lower():
                    print(f"❌ {model_name} not available")
                    break
                else:
                    time.sleep(2)
    
    # All failed
    print("❌ All models failed")
    return json.dumps({
        "error": "Could not process prescription. Please try again with a clearer image.",
        "english": [],
        "translated": [],
        "dangerous_combinations": []
    })
