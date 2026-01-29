import google.generativeai as genai
import os
import sys
from dotenv import load_dotenv

# Force UTF-8 for stdout/stderr
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

load_dotenv()
api_key = os.getenv('GEMINI_API_KEY')
genai.configure(api_key=api_key)

candidates = [
    "gemini-1.5-flash",
    "gemini-1.5-pro",
    "gemini-2.0-flash-exp",
    "gemini-pro"
]

print(f"Testing API Key: {api_key[:5]}...{api_key[-5:]}")

found = False
for model_name in candidates:
    print(f"\nTesting model: {model_name}")
    try:
        model = genai.GenerativeModel(model_name)
        response = model.generate_content("Hello")
        print(f"✅ SUCCESS! Model '{model_name}' works.")
        print(f"Response: {response.text}")
        found = True
        break
    except Exception as e:
        print(f"❌ FAILED: {str(e)[:200]}") # Truncate error to avoid clutter

if not found:
    print("\nNo working model found.")
