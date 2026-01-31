import os
import requests
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv('GEMINI_API_KEY')
print(f"API Key: {api_key}")
print(f"Key length: {len(api_key)}")
print(f"Starts with 'AIza': {api_key.startswith('AIza')}")

# Test with direct HTTP request
MODEL = "models/gemini-2.5-flash"
URL = f"https://generativelanguage.googleapis.com/v1beta/{MODEL}:generateContent?key={api_key}"
payload = {
    "contents": [{
        "parts": [{
            "text": "Hello, what is 2+2?"
        }]
    }]
}

print("\nTesting API key with direct HTTP request...")
try:
    response = requests.post(URL, json=payload, timeout=10)
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        print("✅ API key is valid!")
        result = response.json()
        if 'candidates' in result:
            text = result['candidates'][0]['content']['parts'][0]['text']
            print(f"Response: {text}")
    else:
        print(f"❌ Error: {response.status_code}")
        print(f"Response: {response.text}")
except Exception as e:
    print(f"❌ Request failed: {e}")
