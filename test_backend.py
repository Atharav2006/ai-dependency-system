import jwt
import httpx
import time
import os
import uuid
from dotenv import load_dotenv

from supabase import create_client

load_dotenv(dotenv_path="backend/.env")

BASE_URL = "http://127.0.0.1:8000"
URL = os.getenv("SUPABASE_URL")
KEY = os.getenv("SUPABASE_ANON_KEY")

def get_real_token():
    if not URL or not KEY:
        raise ValueError("Missing SUPABASE_URL or SUPABASE_ANON_KEY")
    
    sb = create_client(URL, KEY)
    
    # Create a random test user
    email = f"test_{uuid.uuid4()}@example.com"
    password = "password123"
    
    print(f"Signing up test user: {email}")
    try:
        res = sb.auth.sign_up({"email": email, "password": password})
        if res.user and res.session:
            return res.session.access_token, res.user.id
        
        # If auto-confirm is off, we might not get a session.
        # But usually in dev it's on or we can't test easily.
        if res.user and not res.session:
            print("User created but no session (email confirmation required?). Trying sign_in...")
            # Try sign in (works if confirmation not required)
            try:
                res = sb.auth.sign_in_with_password({"email": email, "password": password})
                if res.session:
                    return res.session.access_token, res.user.id
            except Exception as e:
                print(f"Sign in failed: {e}")
                
        raise Exception("Failed to get session from sign_up")

    except Exception as e:
        print(f"Auth Signup Error: {e}")
        raise

def test_flow():
    try:
        token, user_id = get_real_token()
    except Exception as e:
        print(f"Skipping Real Auth Test due to: {e}")
        # Fallback to local token just to test 'auth' dependency logic, 
        # but DB calls will likely fail as seen before.
        # We really want this to work.
        return

    headers = {"Authorization": f"Bearer {token}"}

    
    print(f"Testing with User ID: {user_id}")

    # 1. Health
    try:
        r = httpx.get(f"{BASE_URL}/")
        print(f"Health Check: {r.status_code} {r.json()}")
    except Exception as e:
        print(f"Health Check Failed: {e}")
        return

    # 2. Start Session
    print("\n--- Testing /sessions/start ---")
    try:
        r = httpx.post(f"{BASE_URL}/sessions/start", headers=headers)
        print(f"Status: {r.status_code}")
        print(f"Response: {r.text}")
        
        if r.status_code == 200:
            session_id = r.json()["session_id"]
            print(f"Session Created: {session_id}")
            
            # 3. Add Message
            print("\n--- Testing /sessions/{id}/message ---")
            msg_payload = {"message": "Hello AI", "role": "user"}
            r_msg = httpx.post(f"{BASE_URL}/sessions/{session_id}/message", json=msg_payload, headers=headers)
            print(f"Message Status: {r_msg.status_code}")
            print(f"Message Response: {r_msg.text}")

            # 4. End Session
            print("\n--- Testing /sessions/{id}/end ---")
            r_end = httpx.post(f"{BASE_URL}/sessions/{session_id}/end", headers=headers)
            print(f"End Status: {r_end.status_code}")
            print(f"End Response: {r_end.text}")

        else:
            print("Session creation failed.")
            if r.status_code == 500:
                print("Note: If this is a FK violation (auth.users), it means the database enforces Supabase Auth user existence.")
                
    except Exception as e:
        print(f"Request failed: {e}")

if __name__ == "__main__":
    test_flow()
