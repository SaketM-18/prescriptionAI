"""Quick test of prescription processing"""

from pipeline import run_pipeline
import json

print("Testing prescription processing...")
print("-" * 60)

result = run_pipeline('sample.jpg', 'English')
data = json.loads(result)

if 'error' in data:
    print(f"❌ ERROR: {data['error']}")
else:
    english = data.get('english', [])
    translated = data.get('translated', [])
    interactions = data.get('dangerous_combinations', [])
    
    print(f"✅ SUCCESS!")
    print(f"   Medicines (English): {len(english)}")
    print(f"   Medicines (Translated): {len(translated)}")
    print(f"   Drug Interactions: {len(interactions)}")
    
    if english:
        print(f"\n   First medicine:")
        med = english[0]
        print(f"   - Name: {med.get('name', 'N/A')}")
        print(f"   - Dosage: {med.get('dosage', 'N/A')}")
        print(f"   - Timing: {med.get('timing', 'N/A')}")
        print(f"   - Purpose: {med.get('purpose', 'N/A')}")

print("-" * 60)
