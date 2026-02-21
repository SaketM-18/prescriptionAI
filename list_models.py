"""
List available Gemini models
Run this to see which models you can use
"""

from google import genai
from config import get_api_key

api_key = get_api_key()
if not api_key:
    print("❌ No API key found")
    exit(1)

client = genai.Client(api_key=api_key)

print("\n" + "="*60)
print("AVAILABLE GEMINI MODELS")
print("="*60 + "\n")

try:
    models = client.models.list()
    
    gemini_models = []
    for model in models:
        if 'gemini' in model.name.lower():
            gemini_models.append(model)
    
    if not gemini_models:
        print("⚠️  No Gemini models found")
        print("\nAll available models:")
        for model in models:
            print(f"  - {model.name}")
    else:
        print(f"Found {len(gemini_models)} Gemini models:\n")
        
        for model in gemini_models:
            print(f"✅ {model.name}")
            if hasattr(model, 'supported_generation_methods'):
                methods = model.supported_generation_methods
                if methods:
                    print(f"   Methods: {', '.join(methods)}")
            print()
    
    print("="*60)
    print("\nTo use in pipeline.py, copy the model names above")
    print("Example: 'models/gemini-1.5-flash'")
    print("="*60 + "\n")
    
except Exception as e:
    print(f"❌ Error listing models: {e}")
    print("\nTrying alternative method...")
    
    # Try direct API call
    try:
        import requests
        response = requests.get(
            "https://generativelanguage.googleapis.com/v1beta/models",
            params={"key": api_key}
        )
        
        if response.status_code == 200:
            data = response.json()
            models = data.get('models', [])
            
            print("\nAvailable models:")
            for model in models:
                name = model.get('name', '')
                if 'gemini' in name.lower():
                    print(f"✅ {name}")
                    methods = model.get('supportedGenerationMethods', [])
                    if 'generateContent' in methods:
                        print(f"   ✓ Supports generateContent")
                    print()
        else:
            print(f"❌ API request failed: {response.status_code}")
            print(response.text)
    except Exception as e2:
        print(f"❌ Alternative method failed: {e2}")
