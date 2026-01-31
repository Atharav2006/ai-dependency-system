"""
Quick test to check if Gemini service is working
"""
import os
from dotenv import load_dotenv

load_dotenv()

print("Testing Gemini Service...")
print(f"API Key loaded: {'Yes' if os.getenv('GEMINI_API_KEY') else 'No'}")
print(f"API Key length: {len(os.getenv('GEMINI_API_KEY', ''))}")

try:
    from app.utils.gemini_service import get_gemini_service
    print("\n✅ Gemini service imported successfully")
    
    service = get_gemini_service()
    print("✅ Gemini service initialized")
    
    print("\nGenerating test response...")
    response = service.generate_response("Hello, what is 2+2?")
    print(f"\n🤖 AI Response:\n{response}")
    print("\n✅ Gemini service is working!")
    
except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()
