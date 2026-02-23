"""
Quick setup test for local development
Run this to verify your API key and configuration
"""

import json
import os

def test_setup():
    print("=" * 50)
    print("TESTING LOCAL SETUP")
    print("=" * 50)
    
    # Test 1: Check key.json exists
    print("\n1. Checking key.json...")
    if os.path.exists('key.json'):
        print("   ✅ key.json found")
        
        try:
            with open('key.json', 'r') as f:
                data = json.load(f)
                api_key = data.get('api_key', '')
                
                if api_key == 'your-actual-api-key-here':
                    print("   ❌ ERROR: key.json has placeholder value!")
                    print("   📝 ACTION NEEDED:")
                    print("      1. Go to https://aistudio.google.com/app/apikey")
                    print("      2. Create a new API key")
                    print("      3. Replace 'your-actual-api-key-here' in key.json with your actual key")
                    return False
                elif not api_key or len(api_key) < 20:
                    print("   ❌ ERROR: API key looks invalid (too short)")
                    return False
                else:
                    print(f"   ✅ API key found (length: {len(api_key)})")
                    masked_key = api_key[:10] + "..." + api_key[-4:]
                    print(f"   🔑 Key: {masked_key}")
        except Exception as e:
            print(f"   ❌ ERROR reading key.json: {e}")
            return False
    else:
        print("   ❌ key.json not found")
        print("   📝 Create key.json with:")
        print('      {"api_key": "YOUR_ACTUAL_KEY_HERE"}')
        return False
    
    # Test 2: Test API connection
    print("\n2. Testing Google AI API connection...")
    try:
        import google.generativeai as genai
        from config import get_api_key
        
        api_key = get_api_key()
        if not api_key:
            print("   ❌ Could not load API key")
            return False
        
        genai.configure(api_key=api_key)
        
        # Try to list models
        print("   📡 Connecting to Google AI...")
        models = genai.list_models()
        available_models = [m.name for m in models if 'generateContent' in m.supported_generation_methods]
        
        if available_models:
            print(f"   ✅ API connection successful!")
            print(f"   📋 Available models: {len(available_models)}")
            for model in available_models[:3]:
                print(f"      - {model}")
        else:
            print("   ⚠️ Connected but no models available")
            
    except Exception as e:
        print(f"   ❌ API connection failed: {e}")
        print("\n   Possible issues:")
        print("   - Invalid API key")
        print("   - API key not enabled for Gemini API")
        print("   - Network connection issue")
        print("   - Rate limit exceeded")
        return False
    
    # Test 3: Check required packages
    print("\n3. Checking required packages...")
    required = ['flask', 'pillow', 'google-generativeai']
    missing = []
    
    for package in required:
        try:
            if package == 'pillow':
                __import__('PIL')
            else:
                __import__(package.replace('-', '_'))
            print(f"   ✅ {package}")
        except ImportError:
            print(f"   ❌ {package} not installed")
            missing.append(package)
    
    if missing:
        print(f"\n   📝 Install missing packages:")
        print(f"      pip install {' '.join(missing)}")
        return False
    
    # All tests passed
    print("\n" + "=" * 50)
    print("✅ ALL TESTS PASSED!")
    print("=" * 50)
    print("\n🚀 You can now run the app:")
    print("   python app.py")
    print("\n   Then open: http://localhost:5000")
    return True

if __name__ == "__main__":
    success = test_setup()
    if not success:
        print("\n❌ Setup incomplete. Please fix the issues above.")
        exit(1)
