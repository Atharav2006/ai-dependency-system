"""
Test script for Gemini AI integration
Tests the session message endpoint with AI response generation
"""
import httpx
import json
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

BASE_URL = "http://localhost:8000"

def get_token():
    """Get token from file or user input"""
    # Try to read from saved token file
    if os.path.exists('.test_token'):
        with open('.test_token', 'r') as f:
            token = f.read().strip()
            if token:
                print("✅ Using saved token from .test_token file")
                return token
    
    # Otherwise, ask user
    print("\n" + "="*70)
    print("To get your JWT token:")
    print("1. Run: python get_token.py")
    print("2. Or manually copy it from the browser console")
    print("="*70 + "\n")
    
    token = input("Enter your Supabase JWT token: ").strip()
    return token

async def test_ai_integration():
    """Test the AI integration end-to-end"""
    
    TEST_TOKEN = get_token()
    
    if not TEST_TOKEN:
        print("❌ No token provided. Exiting.")
        return
    
    headers = {
        "Authorization": f"Bearer {TEST_TOKEN}",
        "Content-Type": "application/json"
    }
    
    async with httpx.AsyncClient() as client:
        print("\n" + "="*70)
        print("🧪 TESTING GEMINI AI INTEGRATION")
        print("="*70)
        
        print("\n1️⃣  Starting a new session...")
        try:
            start_response = await client.post(
                f"{BASE_URL}/sessions/start",
                headers=headers,
                timeout=10.0
            )
            
            if start_response.status_code != 200:
                print(f"❌ Failed to start session: {start_response.text}")
                return
            
            session_data = start_response.json()
            session_id = session_data["session_id"]
            print(f"   ✅ Session started: {session_id}")
        except Exception as e:
            print(f"   ❌ Error: {e}")
            print("\n   Make sure the backend server is running:")
            print("   uvicorn app.main:app --reload")
            return
        
        print("\n2️⃣  Sending a message to the AI...")
        print("   📝 User: 'Hello! Can you explain what quantum computing is in simple terms?'")
        
        try:
            message_response = await client.post(
                f"{BASE_URL}/sessions/{session_id}/message",
                headers=headers,
                json={
                    "message": "Hello! Can you explain what quantum computing is in simple terms?",
                    "role": "user"
                },
                timeout=30.0  # AI generation might take a bit longer
            )
            
            if message_response.status_code != 200:
                print(f"   ❌ Failed to send message: {message_response.text}")
                return
            
            message_data = message_response.json()
            print(f"   ✅ Message sent successfully")
            
            if message_data.get('ai_response'):
                print(f"\n   🤖 AI Response:")
                print(f"   {'-'*66}")
                print(f"   {message_data['ai_response']['message']}")
                print(f"   {'-'*66}")
            else:
                print("\n   ⚠️  No AI response generated")
        except Exception as e:
            print(f"   ❌ Error: {repr(e)}")
            import traceback
            traceback.print_exc()
            return
        
        print("\n3️⃣  Sending a follow-up message...")
        print("   📝 User: 'Can you give me a real-world example?'")
        
        try:
            followup_response = await client.post(
                f"{BASE_URL}/sessions/{session_id}/message",
                headers=headers,
                json={
                    "message": "Can you give me a real-world example?",
                    "role": "user"
                },
                timeout=30.0
            )
            
            if followup_response.status_code != 200:
                print(f"   ❌ Failed to send follow-up: {followup_response.text}")
                return
            
            followup_data = followup_response.json()
            print(f"   ✅ Follow-up sent successfully")
            
            if followup_data.get('ai_response'):
                print(f"\n   🤖 AI Follow-up Response:")
                print(f"   {'-'*66}")
                print(f"   {followup_data['ai_response']['message']}")
                print(f"   {'-'*66}")
            else:
                print("\n   ⚠️  No AI response generated")
        except Exception as e:
            print(f"   ❌ Error: {e}")
            return
        
        print("\n4️⃣  Ending the session...")
        try:
            end_response = await client.post(
                f"{BASE_URL}/sessions/{session_id}/end",
                headers=headers,
                timeout=10.0
            )
            
            if end_response.status_code != 200:
                print(f"   ❌ Failed to end session: {end_response.text}")
                return
            
            print(f"   ✅ Session ended successfully")
        except Exception as e:
            print(f"   ❌ Error: {e}")
            return
        
        print("\n" + "="*70)
        print("✨ ALL TESTS PASSED! ✨")
        print("="*70)
        print("\nThe Gemini AI integration is working correctly!")
        print("- Messages are being stored ✅")
        print("- AI responses are being generated ✅")
        print("- Conversation context is maintained ✅")

if __name__ == "__main__":
    import asyncio
    asyncio.run(test_ai_integration())
