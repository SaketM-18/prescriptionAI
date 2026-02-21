"""
Test script for prescription reading enhancements
Run this to verify the improvements are working
"""

import os
import json
from pipeline import run_pipeline, preprocess_image, validate_and_enhance_response
from PIL import Image

def test_image_preprocessing():
    """Test image preprocessing"""
    print("\n" + "="*60)
    print("TEST 1: Image Preprocessing")
    print("="*60)
    
    try:
        # Check if sample image exists
        if not os.path.exists('sample.jpg'):
            print("⚠️  No sample.jpg found. Skipping preprocessing test.")
            return
        
        img = Image.open('sample.jpg')
        print(f"✅ Original image size: {img.size}")
        
        processed = preprocess_image(img)
        print(f"✅ Preprocessed image size: {processed.size}")
        print("✅ Image preprocessing working correctly")
        
    except Exception as e:
        print(f"❌ Preprocessing test failed: {e}")

def test_validation():
    """Test response validation"""
    print("\n" + "="*60)
    print("TEST 2: Response Validation")
    print("="*60)
    
    try:
        # Test with incomplete data
        test_data = {
            "english": [
                {"name": "Paracetamol"}  # Missing other fields
            ],
            "translated": []
        }
        
        json_str = json.dumps(test_data)
        enhanced = validate_and_enhance_response(json_str)
        result = json.loads(enhanced)
        
        # Check if fields were added
        med = result['english'][0]
        required_fields = ['name', 'purpose', 'dosage', 'timing', 'frequency', 
                          'duration', 'warnings', 'precautions', 'visual_timing']
        
        missing = [f for f in required_fields if f not in med]
        
        if not missing:
            print("✅ All required fields present after validation")
            print(f"✅ Sample enhanced medicine: {json.dumps(med, indent=2)}")
        else:
            print(f"⚠️  Missing fields: {missing}")
            
    except Exception as e:
        print(f"❌ Validation test failed: {e}")

def test_ocr_fallback():
    """Test OCR fallback"""
    print("\n" + "="*60)
    print("TEST 3: OCR Fallback")
    print("="*60)
    
    try:
        from ocr_fallback import extract_text_with_tesseract
        
        if not os.path.exists('sample.jpg'):
            print("⚠️  No sample.jpg found. Skipping OCR test.")
            return
        
        text = extract_text_with_tesseract('sample.jpg')
        
        if text:
            print(f"✅ OCR extracted {len(text)} characters")
            print(f"📝 Sample text: {text[:100]}...")
        else:
            print("⚠️  OCR extraction returned no text (Tesseract may not be installed)")
            
    except ImportError:
        print("⚠️  Tesseract not installed. OCR fallback will not work.")
        print("   Install with: apt-get install tesseract-ocr (Linux)")
        print("   or: brew install tesseract (Mac)")
    except Exception as e:
        print(f"❌ OCR test failed: {e}")

def test_full_pipeline():
    """Test complete pipeline"""
    print("\n" + "="*60)
    print("TEST 4: Full Pipeline")
    print("="*60)
    
    try:
        if not os.path.exists('sample.jpg'):
            print("⚠️  No sample.jpg found. Skipping pipeline test.")
            print("   Place a prescription image as 'sample.jpg' to test.")
            return
        
        if not os.environ.get('GOOGLE_API_KEY'):
            print("⚠️  GOOGLE_API_KEY not set. Skipping pipeline test.")
            return
        
        print("🚀 Running full pipeline...")
        result = run_pipeline('sample.jpg', 'English')
        
        data = json.loads(result)
        
        if 'error' in data:
            print(f"⚠️  Pipeline returned error: {data['error']}")
        else:
            english_count = len(data.get('english', []))
            translated_count = len(data.get('translated', []))
            interactions = len(data.get('dangerous_combinations', []))
            
            print(f"✅ Pipeline completed successfully")
            print(f"   - Extracted {english_count} medicines (English)")
            print(f"   - Extracted {translated_count} medicines (Translated)")
            print(f"   - Found {interactions} drug interactions")
            
            if english_count > 0:
                print(f"\n📋 Sample medicine:")
                print(json.dumps(data['english'][0], indent=2))
                
    except Exception as e:
        print(f"❌ Pipeline test failed: {e}")

def test_api_connection():
    """Test API connection"""
    print("\n" + "="*60)
    print("TEST 5: API Connection")
    print("="*60)
    
    try:
        api_key = os.environ.get('GOOGLE_API_KEY')
        
        if not api_key:
            print("❌ GOOGLE_API_KEY not found in environment")
            print("   Set it with: export GOOGLE_API_KEY='your-key-here'")
            return
        
        print(f"✅ API key found: {api_key[:10]}...{api_key[-4:]}")
        
        # Try to import and configure
        import google.generativeai as genai
        genai.configure(api_key=api_key)
        
        print("✅ Google Generative AI SDK configured")
        
        # Try to list models
        models = genai.list_models()
        available = [m.name for m in models if 'gemini' in m.name.lower()]
        
        print(f"✅ Found {len(available)} Gemini models")
        print(f"   Available models: {', '.join(available[:3])}...")
        
    except ImportError:
        print("❌ google-generativeai package not installed")
        print("   Install with: pip install google-generativeai")
    except Exception as e:
        print(f"❌ API connection test failed: {e}")

def run_all_tests():
    """Run all tests"""
    print("\n" + "🧪 "*20)
    print("PRESCRIPTION READING ENHANCEMENT TESTS")
    print("🧪 "*20)
    
    test_api_connection()
    test_image_preprocessing()
    test_validation()
    test_ocr_fallback()
    test_full_pipeline()
    
    print("\n" + "="*60)
    print("TESTS COMPLETED")
    print("="*60)
    print("\n💡 Tips:")
    print("   - Place a prescription image as 'sample.jpg' for full testing")
    print("   - Ensure GOOGLE_API_KEY is set in environment")
    print("   - Install Tesseract for OCR fallback support")
    print("   - Check logs for detailed error messages")
    print("\n")

if __name__ == "__main__":
    run_all_tests()
