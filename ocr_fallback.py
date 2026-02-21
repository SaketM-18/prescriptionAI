"""
OCR Fallback Module
Provides Tesseract OCR as a fallback when AI vision fails
"""

import os
import json

def extract_text_with_tesseract(image_path):
    """
    Extract text from image using Tesseract OCR
    Returns extracted text or None if failed
    """
    try:
        import pytesseract
        from PIL import Image, ImageEnhance, ImageFilter
        
        # Load and preprocess image
        img = Image.open(image_path)
        
        # Convert to grayscale for better OCR
        img = img.convert('L')
        
        # Enhance contrast
        enhancer = ImageEnhance.Contrast(img)
        img = enhancer.enhance(2.0)
        
        # Apply threshold to make text clearer
        img = img.point(lambda x: 0 if x < 140 else 255, '1')
        
        # Extract text
        text = pytesseract.image_to_string(img, lang='eng')
        
        return text.strip() if text else None
        
    except ImportError:
        print("⚠️ Tesseract not available")
        return None
    except Exception as e:
        print(f"⚠️ OCR extraction failed: {e}")
        return None

def parse_ocr_text_with_ai(ocr_text, language):
    """
    Use AI to parse OCR-extracted text into structured medicine data
    """
    try:
        import google.generativeai as genai
        
        api_key = os.environ.get("GOOGLE_API_KEY")
        if not api_key:
            return None
            
        genai.configure(api_key=api_key)
        
        prompt = f"""
        You are a medical prescription parser. The following text was extracted from a prescription using OCR.
        It may contain errors, misspellings, or formatting issues.
        
        Parse this text and extract medicine information:
        
        {ocr_text}
        
        Return ONLY valid JSON with this structure:
        {{
          "english": [
            {{
              "name": "Medicine Name (correct spelling)",
              "purpose": "Purpose in simple language",
              "dosage": "Dosage in M-A-N format (e.g., 1-0-1)",
              "timing": "When to take",
              "duration": "How long",
              "warnings": "Warnings if any"
            }}
          ],
          "translated": [
            {{
              "name": "Medicine Name",
              "purpose": "Translated to {language}",
              "dosage": "1-0-1",
              "timing": "Translated to {language}",
              "duration": "Translated to {language}",
              "warnings": "Translated to {language}"
            }}
          ]
        }}
        
        If you cannot extract clear medicine information, return empty arrays.
        """
        
        model = genai.GenerativeModel('gemini-2.0-flash')
        response = model.generate_content(
            prompt,
            generation_config=genai.types.GenerationConfig(
                temperature=0.1,
                response_mime_type="application/json"
            )
        )
        
        if response.text:
            return response.text
            
    except Exception as e:
        print(f"⚠️ AI parsing of OCR text failed: {e}")
        
    return None

def ocr_fallback_pipeline(image_path, language):
    """
    Complete OCR fallback pipeline
    """
    print("🔄 Attempting OCR fallback...")
    
    # Step 1: Extract text with Tesseract
    ocr_text = extract_text_with_tesseract(image_path)
    
    if not ocr_text or len(ocr_text) < 10:
        print("❌ OCR extraction failed or insufficient text")
        return None
    
    print(f"📝 OCR extracted {len(ocr_text)} characters")
    
    # Step 2: Parse with AI
    result = parse_ocr_text_with_ai(ocr_text, language)
    
    if result:
        print("✅ OCR fallback successful")
        return result
    
    print("❌ OCR fallback failed")
    return None
