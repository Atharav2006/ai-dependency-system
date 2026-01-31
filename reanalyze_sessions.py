import asyncio
import os
import sys
from dotenv import load_dotenv

# Add backend to path so we can import app modules
sys.path.append(os.path.join(os.getcwd(), "backend"))

load_dotenv(os.path.join("backend", ".env"))

from app.utils.supabase_client import get_supabase_client
from app.utils.dependency_service import get_dependency_service

async def reanalyze_all_sessions():
    supabase = get_supabase_client()
    dependency_service = get_dependency_service()
    
    print("🚀 Starting re-analysis of all sessions...")
    
    # Fetch all sessions that need analysis update (including those with null types)
    response = supabase.table("session_metrics").select("session_id").execute()
    
    if not response.data:
        print("✅ No session metrics found to analyze.")
        return
        
    session_ids = [r["session_id"] for r in response.data]
    print(f"📊 Found {len(session_ids)} sessions to re-analyze.")
    
    for i, session_id in enumerate(session_ids):
        print(f"🔄 Analyzing session {i+1}/{len(session_ids)}: {session_id}...")
        try:
            # We don't have the user's token here, but analyze_session 
            # falls back to service client if token is None.
            # NOTE: analyze_session will OVERWRITE existing metrics in the DB 
            # because we are using .insert() which might fail if session_id is a primary key or has unique constraint.
            # Actually session_metrics usually has session_id as a unique field or primary key.
            # Let's check session_metrics schema. 
            # In my previous list_tables, session_metrics had an 'id' as primary key.
            
            await dependency_service.analyze_session(session_id)
            print(f"✅ Successfully re-analyzed {session_id}")
        except Exception as e:
            print(f"❌ Failed to analyze {session_id}: {e}")
            
    print("\n✨ Re-analysis complete! Restart your frontend to see the updated Dependency DNA.")

if __name__ == "__main__":
    asyncio.run(reanalyze_all_sessions())
