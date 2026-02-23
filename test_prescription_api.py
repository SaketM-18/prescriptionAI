"""
Test the prescription reading API
"""

import requests
import os

def test_prescription_reading():
    print("Testing prescription reading...")
    
    # Check if sample.jpg exists
    if not os.path.exists('sample.jpg'):
        print("❌ sample.jpg not found")
        print("   Please make sure you have a sample prescription image")
        return
    
    # Test the API
    url = 'http://127.0.0.1:5000/process'
    
    try:
        with open('sample.jpg', 'rb') as f:
            files = {'file': f}
            data = {'language': 'English'}
            
            print("📤 Sending request to /process endpoint...")
            response = requests.post(url, files=files, data=data, timeout=30)
            
            if response.status_code == 200:
                print("✅ Request successful!")
                result = response.json()
                
                if 'error' in result:
                    print(f"❌ API Error: {result['error']}")
                else:
                    english = result.get('english', [])
                    print(f"✅ Found {len(english)} medicines")
                    
                    if english:
                        print("\nFirst medicine:")
                        med = english[0]
                        print(f"  Name: {med.get('name', 'N/A')}")
                        print(f"  Dosage: {med.get('dosage', 'N/A')}")
                        print(f"  Purpose: {med.get('purpose', 'N/A')}")
            else:
                print(f"❌ Request failed with status {response.status_code}")
                print(f"   Response: {response.text}")
                
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to Flask app")
        print("   Make sure the app is running: python app.py")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_prescription_reading()
