from app.utils.gemini_service import get_gemini_service
from dotenv import load_dotenv
import sys

load_dotenv()

# Mocking print to see what's happening internally if needed, 
# but we rely on the service's own print statements for now.

print("Testing Gemini Service Failover...")
service = get_gemini_service()

try:
    response = service.generate_response("Test failover functionality.")
    print(f"✅ Success! Response: {response[:50]}...")
except Exception as e:
    print(f"❌ Failed after retries: {e}")
