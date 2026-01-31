import os
import jwt
import json
from fastapi import HTTPException, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from dotenv import load_dotenv

load_dotenv()

security = HTTPBearer()

SUPABASE_URL = os.getenv("SUPABASE_URL")

async def get_current_user(credentials: HTTPAuthorizationCredentials = Security(security)):
    token = credentials.credentials
    
    try:
        # Debug: Print token header to see what algorithm is being used
        unverified_header = jwt.get_unverified_header(token)
        print(f"Token header: {unverified_header}")
        
        # Supabase uses RS256 for user JWTs
        # Fetch the public key from JWKS endpoint
        jwks_url = f"{SUPABASE_URL}/auth/v1/.well-known/jwks.json"
        
        # Get the signing key from JWKS - don't restrict algorithms here
        jwks_client = jwt.PyJWKClient(
            jwks_url,
            cache_keys=True,
            max_cached_keys=16
        )
        signing_key = jwks_client.get_signing_key_from_jwt(token)
        
        alg = unverified_header.get('alg', 'RS256')
        print(f"Using algorithm: {alg}")
        
        # Decode and verify the token
        payload = jwt.decode(
            token,
            signing_key.key,
            algorithms=[alg],  # Use algorithm from token header
            audience="authenticated",
            options={
                "verify_signature": True,
                "verify_exp": True,
                "verify_aud": True
            }
        )

        # Add the raw token to payload for downstream usage
        payload["access_token"] = token
        print(f"Token verified successfully for user: {payload.get('sub')}")
        return payload

    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except jwt.InvalidAudienceError as e:
        print(f"Invalid audience error: {e}")
        raise HTTPException(status_code=401, detail="Invalid token audience")
    except jwt.InvalidTokenError as e:
        print(f"Token validation error: {e}")
        raise HTTPException(status_code=401, detail=f"Invalid token: {str(e)}")
    except Exception as e:
        print(f"Auth error: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=401, detail=f"Authentication failed: {str(e)}")
