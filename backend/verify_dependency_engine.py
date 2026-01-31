import asyncio
import httpx
import json
import os
from dotenv import load_dotenv

load_dotenv()

BASE_URL = "http://localhost:8000"

# You might need to paste a fresh token here if the old one expired or script can't find it
# For now, we'll try to read from .test_token or ask user
def get_token():
    if os.path.exists('.test_token'):
        with open('.test_token', 'r') as f:
            return f.read().strip()
    return input("Enter JWT Token: ").strip()

async def verify_dependency_engine():
    token = get_token()
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    async with httpx.AsyncClient() as client:
        print("\n1️⃣ Starting Session...")
        res = await client.post(f"{BASE_URL}/sessions/start", headers=headers)
        if res.status_code != 200:
            print(f"❌ Failed to start: {res.text}")
            return
        session_id = res.json()["session_id"]
        print(f"✅ Session: {session_id}")

        print("\n2️⃣ Sending Messages (Simulating High Dependency)...")
        # Simulating a user who asks AI to do everything
        messages = [
            "Write me a completely finished essay about climate change.",
            "Now fix all the grammar errors in it for me.",
            "I don't want to think about the conclusion, just write it for me."
        ]

        for msg in messages:
            print(f"   User: {msg}")
            res = await client.post(
                f"{BASE_URL}/sessions/{session_id}/message", 
                headers=headers,
                json={"message": msg, "role": "user"},
                timeout=30.0
            )
            if res.status_code != 200:
                print(f"❌ Msg Failed: {res.text}")
            else:
                print("   ✅ AI Replying...")

        print("\n3️⃣ Ending Session & Triggering Analysis...")
        res = await client.post(
            f"{BASE_URL}/sessions/{session_id}/end", 
            headers=headers,
            timeout=30.0 # Analysis might take a few seconds
        )
        
        if res.status_code != 200:
            print(f"❌ Failed to end: {res.text}")
            return
            
        data = res.json()
        print("✅ Session Ended.")
        
        # Check if analysis was returned immediately
        if data.get("analysis"):
            print("\n📊 Analysis Result Returned Immediately:")
            print(json.dumps(data["analysis"], indent=2))
        else:
            print("⚠️ Analysis not in response, checking GET endpoint...")
            
            # Check GET endpoint
            res = await client.get(f"{BASE_URL}/sessions/{session_id}/analysis", headers=headers)
            if res.status_code == 200:
                print("\n📊 Fetched Analysis from API:")
                print(json.dumps(res.json(), indent=2))
            else:
                print(f"❌ Failed to fetch analysis: {res.text}")

if __name__ == "__main__":
    asyncio.run(verify_dependency_engine())
