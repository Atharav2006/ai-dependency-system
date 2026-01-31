import os
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

url: str = os.getenv("SUPABASE_URL")
key: str = os.getenv("SUPABASE_ANON_KEY")

if not url or not key:
    # We allow running without error if just loading imports, but ideally check here
    print("Warning: Missing SUPABASE_URL or SUPABASE_ANON_KEY environment variables")

supabase: Client = None

try:
    if url and key:
        supabase = create_client(url, key)
except Exception as e:
    print(f"Error initializing Supabase client: {e}")
    supabase = None

def get_supabase_client(token: str = None) -> Client:
    """
    Get a Supabase client, optionally with a user token for RLS.
    
    Args:
        token: Optional JWT token for authenticated requests
        
    Returns:
        Supabase client instance
    """
    if not url or not key:
        raise Exception("Supabase credentials missing")
    
    # Create a new client instance
    client = create_client(url, key)
    
    # If a token is provided, set it in the client's headers
    if token:
        # Set the Authorization header for RLS
        client.postgrest.auth(token)
    
    return client
