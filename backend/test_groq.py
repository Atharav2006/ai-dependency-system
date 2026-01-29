from app.utils.groq_service import get_groq_service
from dotenv import load_dotenv
import os

load_dotenv()

print(f"Testing Groq Integration...")
key = os.getenv("GROQ_API_KEY")
if key:
    print(f"Found Key: {key[:10]}...")
else:
    print("❌ GROQ_API_KEY not found in env!")

try:
    service = get_groq_service()
    print(f"Service initialized with model: {service.model}")
    
    response = service.generate_response("Hello Groq! Reply with 'Working'.")
    print(f"✅ Response: {response}")
except Exception as e:
    print(f"❌ Error: {e}")
