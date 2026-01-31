import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv('GEMINI_API_KEY')
print(f"Testing with API Key: {api_key[:10]}...")

genai.configure(api_key=api_key)
model = genai.GenerativeModel('gemini-2.5-flash')

try:
    print("Sending request to Gemini...")
    response = model.generate_content("Hello, can you hear me? Reply with 'Yes'.")
    print(f"Response: {response.text}")
    print("✅ Gemini API is working!")
except Exception as e:
    print(f"❌ Error: {e}")
    if "429" in str(e):
        print("⚠️ Rate Limit Exceeded (Quota issues)")
