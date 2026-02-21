"""
Configuration helper for API keys
Supports both local development (key.json) and production (environment variables)
"""

import os
import json

def get_api_key():
    """
    Get API key from environment variable or key.json
    Priority: Environment variable > key.json
    """
    # Try environment variable first (production/Render)
    api_key = os.environ.get("GOOGLE_API_KEY")
    
    if api_key:
        print("🔑 Using API key from environment variable (production mode)")
        return api_key
    
    # Try key.json (local development)
    try:
        with open('key.json', 'r') as f:
            key_data = json.load(f)
            api_key = key_data.get('api_key')
            if api_key:
                print("🔑 Using API key from key.json (local mode)")
                return api_key
    except FileNotFoundError:
        print("⚠️ key.json not found")
    except Exception as e:
        print(f"⚠️ Error reading key.json: {e}")
    
    print("❌ API key not found in environment or key.json")
    return None
