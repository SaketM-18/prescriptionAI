from PIL import Image
import json, os, time

# Removed top-level genai import and config to prevent startup blocking

def validate_and_enhance_response(json_str):
    """
    Validate and enhance the AI response with additional checks
    """
    try:
        data = json.loads(json_str)
        
        # Ensure required fields exist
        if 'english' not in data:
            data['english'] = []
        if 'translated' not in data:
            data['translated'] = []
        if 'dangerous_combinations' not in data:
            data['dangerous_combinations'] = []
        
        # Enhance each medicine entry
        for med in data.get('english', []):
            # Ensure all required fields exist
            if 'name' not in med or not med['name']:
                med['name'] = 'Unknown Medicine'
            if 'purpose' not in med:
                med['purpose'] = 'As prescribed by doctor'
            if 'dosage' not in med:
                med['dosage'] = 'As directed'
            if 'timing' not in med:
                med['timing'] = 'As directed'
            if 'frequency' not in med:
                med['frequency'] = med.get('timing', 'As directed')
            if 'duration' not in med:
                med['duration'] = 'As prescribed'
            if 'warnings' not in med:
                med['warnings'] = 'Follow doctor\'s advice'
            if 'precautions' not in med:
                med['precautions'] = med.get('warnings', 'Follow doctor\'s advice')
            if 'visual_timing' not in med:
                # Generate visual timing from dosage
                med['visual_timing'] = generate_visual_timing(med.get('dosage', ''))
            if 'generic_alternative' not in med:
                med['generic_alternative'] = ''
        
        # Do the same for translated
        for med in data.get('translated', []):
            if 'name' not in med or not med['name']:
                med['name'] = 'Unknown Medicine'
            if 'frequency' not in med:
                med['frequency'] = med.get('timing', 'As directed')
            if 'precautions' not in med:
                med['precautions'] = med.get('warnings', 'Follow doctor\'s advice')
            if 'visual_timing' not in med:
                med['visual_timing'] = generate_visual_timing(med.get('dosage', ''))
        
        return json.dumps(data)
    except Exception as e:
        print(f"⚠️ Validation error: {e}")
        return json_str

def generate_visual_timing(dosage):
    """
    Generate emoji-based visual timing from dosage string
    """
    if not dosage:
        return ''
    
    # Check for standard format (1-0-1, 1-1-1, etc.)
    import re
    match = re.match(r'(\d+)-(\d+)-(\d+)', dosage)
    if match:
        morning, afternoon, night = match.groups()
        result = []
        if morning != '0':
            result.append('☀️')
        if afternoon != '0':
            result.append('🌤️')
        if night != '0':
            result.append('🌙')
        return ' '.join(result) if result else ''
    
    # Fallback: keyword detection
    lower = dosage.lower()
    result = []
    if 'morn' in lower or 'am' in lower:
        result.append('☀️')
    if 'after' in lower or 'noon' in lower or 'lunch' in lower:
        result.append('🌤️')
    if 'night' in lower or 'bed' in lower or 'pm' in lower or 'evening' in lower:
        result.append('🌙')
    
    return ' '.join(result) if result else ''

def clean_json(text):
    text = text.strip()
    if text.startswith("```"):
        text = text.replace("```", "").strip()
    if text.lower().startswith("json"):
        text = text[4:].strip()
    return text

def preprocess_image(img):
    """
    Enhance image quality for better OCR/AI recognition
    """
    from PIL import ImageEnhance, ImageFilter
    
    # Convert to RGB if needed
    if img.mode != 'RGB':
        img = img.convert('RGB')
    
    # Enhance contrast for better text visibility
    enhancer = ImageEnhance.Contrast(img)
    img = enhancer.enhance(1.5)
    
    # Enhance sharpness for clearer text
    enhancer = ImageEnhance.Sharpness(img)
    img = enhancer.enhance(2.0)
    
    # Enhance brightness if image is too dark
    enhancer = ImageEnhance.Brightness(img)
    img = enhancer.enhance(1.2)
    
    # Apply slight sharpening filter
    img = img.filter(ImageFilter.SHARPEN)
    
    return img

def run_pipeline(image_path, language):
    # Lazy Load SDK to prevent startup timeouts
    try:
        from google import genai
        from google.genai import types
        import logging
        from PIL import Image, ImageEnhance, ImageFilter
        import io
        
        # Configure API Key (Lazy)
        api_key = os.environ.get("GOOGLE_API_KEY")
        if not api_key:
            return json.dumps({"error": "GOOGLE_API_KEY not found in environment variables!"})
        
        # Initialize client
        client = genai.Client(api_key=api_key)

        # Load and preprocess image
        img = Image.open(image_path)
        
        # Apply preprocessing for better recognition
        img = preprocess_image(img)
        
        # Resize to optimal size (higher quality for text recognition)
        # Use 1536x1536 for better text clarity while staying within limits
        img.thumbnail((1536, 1536), Image.Resampling.LANCZOS)
        
        # Save with higher quality for better text recognition
        buffer = io.BytesIO()
        img.save(buffer, format="JPEG", quality=95)
        image_data = buffer.getvalue()
        
        print(f"📸 Image preprocessed: {img.size}, {len(image_data)} bytes")
        
    except Exception as e:
        return json.dumps({"error": f"Could not initialize AI or read image: {e}"})

    prompt = f"""
    You are an expert medical prescription analyzer helping rural villagers understand their medicines.
    
    TASK: Analyze this prescription image with MAXIMUM ACCURACY and extract ALL medicine information.
    
    CRITICAL INSTRUCTIONS:
    1. READ CAREFULLY: Look for handwritten AND printed text
    2. EXTRACT EVERYTHING: Medicine names, dosages, frequencies, durations, special instructions
    3. HANDLE VARIATIONS: Recognize common abbreviations (OD=once daily, BD=twice daily, TDS=three times, QID=four times, SOS=as needed)
    4. DOSAGE PATTERNS: Convert to standard format (Morning-Afternoon-Night, e.g., 1-0-1, 1-1-1, 0-0-1)
    5. TIMING CLUES: Look for "AC" (before food), "PC" (after food), "HS" (at bedtime), "PRN" (as needed)
    6. DURATION: Extract days/weeks (e.g., "5 days", "2 weeks", "1 month")
    7. SPECIAL NOTES: Capture warnings like "avoid alcohol", "take with water", "empty stomach"
    8. GENERIC ALTERNATIVES: Suggest cheaper generic versions when possible
    9. DRUG INTERACTIONS: Check ALL medicine pairs for dangerous combinations
    10. UNCLEAR TEXT: If text is unclear, make best educated guess based on context and common prescriptions
    
    COMMON MEDICINE PATTERNS TO RECOGNIZE:
    - Antibiotics: Usually 5-7 days, often BD or TDS
    - Pain relievers: Often SOS or TDS
    - Antacids: Usually AC (before food)
    - Vitamins: Usually OD (once daily)
    - Blood pressure meds: Usually OD, morning
    
    RETURN ONLY VALID JSON with this EXACT structure:
    {{
      "english": [
        {{
          "name": "Full Medicine Name (with strength if visible, e.g., Paracetamol 500mg)",
          "purpose": "Simple purpose in plain language (e.g., 'for fever and pain', 'for infection', 'for acidity')",
          "dosage": "Standard format: Morning-Afternoon-Night (e.g., 1-0-1, 1-1-1, 0-0-1)",
          "visual_timing": "Emoji format: ☀️ for morning, 🌤️ for afternoon, 🌙 for night (e.g., ☀️ -- 🌙)",
          "timing": "When to take (e.g., After food, Before food, Empty stomach, At bedtime)",
          "frequency": "Same as timing field",
          "duration": "How long (e.g., 5 days, 2 weeks, 1 month, Continue)",
          "warnings": "Important warnings (e.g., Avoid alcohol, Take with water, Do not crush)",
          "precautions": "Same as warnings",
          "generic_alternative": "Cheaper generic option with brief description (e.g., 'Paracetamol (Generic) - Same effect, costs 50% less')"
        }}
      ],
      "translated": [
        {{
          "name": "Medicine Name (keep in English)",
          "purpose": "FULLY translated purpose in {language} script",
          "dosage": "1-0-1 (keep numeric format)",
          "visual_timing": "☀️ -- 🌙 (keep emojis)",
          "timing": "FULLY translated in {language} script",
          "frequency": "FULLY translated in {language} script (same as timing)",
          "duration": "FULLY translated in {language} script",
          "warnings": "FULLY translated in {language} script",
          "precautions": "FULLY translated in {language} script (same as warnings)",
          "generic_alternative": "FULLY translated in {language} script"
        }}
      ],
      "dangerous_combinations": [
        {{
          "medicines": "Medicine A + Medicine B",
          "risk": "Clear explanation in English of what could happen",
          "risk_translated": "Same explanation FULLY in {language} script",
          "severity": "high or medium"
        }}
      ]
    }}
    
    TRANSLATION RULES FOR {language}:
    - Medicine names stay in English (brand names)
    - ALL other fields MUST be in {language} script
    - Use simple, village-friendly language
    - Avoid medical jargon
    
    IMPORTANT: If prescription is unclear or partially visible:
    - Extract what you CAN read clearly
    - Make educated guesses for common medicines
    - Mark uncertain extractions with "(?)" in the name
    - Still provide helpful information
    
    DO NOT use markdown code blocks. Return ONLY the raw JSON object.
    """
    
    print("🚀 STARTING APP WITH STABLE SDK (google-genai) 🚀")

    # Models to try (Verified available from debug_models)
    models = [
        "gemini-2.0-flash-exp",       # Primary (Fastest)
        "gemini-1.5-flash",           # Fallback 1 (Stable)
        "gemini-1.5-flash-8b",        # Fallback 2 (Efficient)
        "gemini-1.5-pro",             # Fallback 3 (Most capable)
    ]

    max_retries = 3
    final_error = None

    for i, model_name in enumerate(models):
        print(f"🤖 Trying model: {model_name}...")
        
        for retry in range(max_retries):
            try:
                # Generate content with enhanced configuration
                response = client.models.generate_content(
                    model=model_name,
                    contents=[
                        prompt,
                        types.Part.from_bytes(data=image_data, mime_type="image/jpeg")
                    ],
                    config=types.GenerateContentConfig(
                        temperature=0.1,
                        top_p=0.95,
                        top_k=40,
                        max_output_tokens=4096,
                        response_mime_type="application/json"
                    )
                )
                
                # Check response
                if not response.text:
                    raise ValueError("Empty response from API")
                    
                json_str = clean_json(response.text)
                
                # Validate and enhance the response
                json_str = validate_and_enhance_response(json_str)
                
                print(f"✅ Success with {model_name}")
                print(f"📊 Extracted medicines: {json.loads(json_str).get('english', [])}")
                
                return json_str

            except Exception as e:
                error_str = str(e)
                print(f"⚠️ Error with {model_name} (Attempt {retry+1}/{max_retries}): {error_str}")
                
                # Handle Resource Exhausted (429) - Wait and Retry aggressively on known good models
                if "429" in error_str or "quota" in error_str.lower():
                    print(f"⏳ Quota hit for {model_name}. Waiting 10s...")
                    time.sleep(10) # Wait 10s for quota recovery
                    if retry == max_retries - 1:
                        print(f"❌ Quota exceeded for {model_name}. Switching model...")
                        break
                    continue
                
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

    # If all models failed, try OCR fallback
    print("🔄 All AI vision models failed. Attempting OCR fallback...")
    
    try:
        from ocr_fallback import ocr_fallback_pipeline
        ocr_result = ocr_fallback_pipeline(image_path, language)
        
        if ocr_result:
            print("✅ OCR fallback succeeded")
            return ocr_result
    except Exception as e:
        print(f"⚠️ OCR fallback error: {e}")
    
    # If everything failed
    return json.dumps({
        "error": f"All AI models and OCR fallback failed. Please try again with a clearer image. Last error: {final_error}",
        "english": [], 
        "translated": [], 
        "dangerous_combinations": []
    })
