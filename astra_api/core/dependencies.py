import os
import jwt
import httpx
from datetime import datetime
from pydantic import BaseModel
from typing import Optional
from fastapi import Depends, HTTPException, Header
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from services.db.UserService import UserService

class JWTPayload(BaseModel):
    sub: str  # Username
    email: str
    exp: datetime
    iat: datetime

bearer_scheme = HTTPBearer(auto_error=False)

AUTH_SERVICE_URL = os.getenv("AUTH_PUBLIC_KEY_URL", "http://astra_auth:80/api/auth/public-key")
DEBUG = os.getenv("USER_DEBUG", "False").lower() == "true"

_public_key_cache: Optional[bytes] = None

async def get_public_key() -> bytes:
    """Fetch and cache the public key from the auth service. Fetches once and reuses."""
    global _public_key_cache
    if _public_key_cache is not None:
        return _public_key_cache
        
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(AUTH_SERVICE_URL)
            response.raise_for_status()
            _public_key_cache = response.content
            return _public_key_cache
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Could not fetch public key from auth service: {str(e)}")

async def get_request_user(
    auth_header: Optional[HTTPAuthorizationCredentials] = Depends(bearer_scheme),
    x_user_id: Optional[str] = Header(None, alias="X-User-Id")
) -> str:
    """
    Validates JWT and returns the username (sub).
    Supports X-User-Id as a token or as a raw username in DEBUG mode.
    """
    user_service = UserService()
    token = None

    if auth_header and auth_header.credentials:
        token = auth_header.credentials
    elif x_user_id and DEBUG:
        # In debug mode, treat X-User-Id as a direct username
        await user_service.ensure_user(x_user_id)
        return x_user_id
    elif x_user_id:
        token = x_user_id

    if token:
        try:
            public_key = await get_public_key()
            decoded = jwt.decode(token, public_key, algorithms=["RS256"])
            payload = JWTPayload(**decoded)
            
            # Sync user entry in astra_api DB
            await user_service.ensure_user(payload.sub)
            return payload.sub
        except jwt.ExpiredSignatureError:
            raise HTTPException(status_code=401, detail="Token has expired")
        except jwt.InvalidTokenError as e:
            raise HTTPException(status_code=401, detail=f"Invalid token: {str(e)}")
        except Exception as e:
            raise HTTPException(status_code=401, detail=f"Authentication error: {str(e)}")
        
    raise HTTPException(status_code=401, detail="Unauthorised")