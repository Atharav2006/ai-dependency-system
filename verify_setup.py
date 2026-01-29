import os
import requests
from dotenv import load_dotenv

load_dotenv(dotenv_path="backend/.env")

BASE_URL = "http://127.0.0.1:8000"

def test_manual_token():
    print("to verify the backend, please provide a valid access token from your frontend (Supabase Auth).")
    token = input("Enter Access Token: ").strip()
    
    if not token:
        print("No token provided. Exiting.")
        return

    headers = {"Authorization": f"Bearer {token}"}
    
    # 1. Start Session
    print("\n--- Testing /sessions/start ---")
    try:
        r = requests.post(f"{BASE_URL}/sessions/start", headers=headers)
        print(f"Status: {r.status_code}")
        print(f"Response: {r.text}")
        
        if r.status_code == 200:
            session_id = r.json().get("session_id")
            if session_id:
                print(f"Session Created: {session_id}")
                
                # 2. Add Message
                print(f"\n--- Testing /sessions/{session_id}/message ---")
                msg = {"message": "Hello from manual test", "role": "user"}
                r_msg = requests.post(f"{BASE_URL}/sessions/{session_id}/message", json=msg, headers=headers)
                print(f"Message Status: {r_msg.status_code}")
                print(f"Message Response: {r_msg.text}")
                
                # 3. End Session
                print(f"\n--- Testing /sessions/{session_id}/end ---")
                r_end = requests.post(f"{BASE_URL}/sessions/{session_id}/end", headers=headers)
                print(f"End Status: {r_end.status_code}")
                print(f"End Response: {r_end.text}")
            else:
                print("Session ID missing in response.")
        else:
            print("Failed to start session.")
            
    except Exception as e:
        print(f"Request failed: {e}")

if __name__ == "__main__":
    test_manual_token()
