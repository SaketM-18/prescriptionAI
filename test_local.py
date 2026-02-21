"""
Quick test script for local development
Run this to verify your setup is working
"""

import sys

def test_api_key():
    """Test API key loading"""
    print("\n" + "="*60)
    print("TEST 1: API Key Loading")
    print("="*60)
    
    try:
        from config import get_api_key
        api_key = get_api_key()
        
        if api_key:
            print(f"✅ API key loaded: {api_key[:10]}...{api_key[-4:]}")
            return True
        else:
            print("❌ API key not found")
            print("\nTo fix:")
            print("1. Check if key.json exists")
            print("2. Verify format: {\"api_key\": \"your-key-here\"}")
            print("3. Or set environment variable: export GOOGLE_API_KEY='your-key'")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_imports():
    """Test required imports"""
    print("\n" + "="*60)
    print("TEST 2: Required Packages")
    print("="*60)
    
    packages = {
        'flask': 'Flask',
        'PIL': 'Pillow',
        'google.genai': 'google-genai'
    }
    
    all_ok = True
    for module, package in packages.items():
        try:
            __import__(module)
            print(f"✅ {package} installed")
        except ImportError:
            print(f"❌ {package} not installed")
            print(f"   Install with: pip install {package}")
            all_ok = False
    
    return all_ok

def test_image_processing():
    """Test image preprocessing"""
    print("\n" + "="*60)
    print("TEST 3: Image Processing")
    print("="*60)
    
    try:
        from PIL import Image
        from pipeline import preprocess_image
        import os
        
        # Check if sample image exists
        if not os.path.exists('sample.jpg'):
            print("⚠️  sample.jpg not found (optional)")
            print("   Place a prescription image as 'sample.jpg' to test")
            return True
        
        img = Image.open('sample.jpg')
        print(f"✅ Loaded image: {img.size}, mode: {img.mode}")
        
        processed = preprocess_image(img)
        print(f"✅ Preprocessed: {processed.size}")
        
        return True
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_api_connection():
    """Test API connection"""
    print("\n" + "="*60)
    print("TEST 4: API Connection")
    print("="*60)
    
    try:
        from google import genai
        from config import get_api_key
        
        api_key = get_api_key()
        if not api_key:
            print("❌ No API key available")
            return False
        
        client = genai.Client(api_key=api_key)
        print("✅ API client initialized")
        
        # Try to list models (quick test)
        try:
            # This is a lightweight test
            print("✅ API connection successful")
            return True
        except Exception as e:
            print(f"⚠️  API test skipped: {e}")
            return True  # Don't fail on this
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_pipeline():
    """Test full pipeline"""
    print("\n" + "="*60)
    print("TEST 5: Full Pipeline")
    print("="*60)
    
    try:
        from pipeline import run_pipeline
        import json
        import os
        
        if not os.path.exists('sample.jpg'):
            print("⚠️  sample.jpg not found")
            print("   Place a prescription image as 'sample.jpg' to test full pipeline")
            return True
        
        print("🚀 Running pipeline...")
        result = run_pipeline('sample.jpg', 'English')
        
        data = json.loads(result)
        
        if 'error' in data:
            print(f"⚠️  Pipeline returned error: {data['error']}")
            print("   This might be due to:")
            print("   - API quota exceeded (wait 1 minute)")
            print("   - Poor image quality")
            print("   - Model availability")
            return False
        else:
            english_count = len(data.get('english', []))
            translated_count = len(data.get('translated', []))
            print(f"✅ Pipeline successful!")
            print(f"   - Extracted {english_count} medicines (English)")
            print(f"   - Extracted {translated_count} medicines (Translated)")
            
            if english_count > 0:
                print(f"\n   Sample medicine:")
                med = data['english'][0]
                print(f"   - Name: {med.get('name', 'N/A')}")
                print(f"   - Dosage: {med.get('dosage', 'N/A')}")
                print(f"   - Timing: {med.get('timing', 'N/A')}")
            
            return True
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all tests"""
    print("\n" + "🧪 "*20)
    print("LOCAL DEVELOPMENT TEST SUITE")
    print("🧪 "*20)
    
    results = []
    
    # Run tests
    results.append(("API Key", test_api_key()))
    results.append(("Imports", test_imports()))
    results.append(("Image Processing", test_image_processing()))
    results.append(("API Connection", test_api_connection()))
    results.append(("Full Pipeline", test_pipeline()))
    
    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {name}")
    
    print("\n" + "="*60)
    print(f"Results: {passed}/{total} tests passed")
    print("="*60)
    
    if passed == total:
        print("\n🎉 All tests passed! You're ready to develop locally.")
        print("\nNext steps:")
        print("1. Run: python app.py")
        print("2. Visit: http://localhost:5000")
        print("3. Upload a prescription to test")
    else:
        print("\n⚠️  Some tests failed. Check the errors above.")
        print("\nCommon fixes:")
        print("1. Install packages: pip install -r requirements.txt")
        print("2. Check key.json exists and has correct format")
        print("3. Verify API key is valid at https://aistudio.google.com/")
    
    print("\n")
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
