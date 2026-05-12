import os
from typing import Optional
from fastapi import Depends, HTTPException, Header
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from core.security import decode_access_token

bearer_scheme = HTTPBearer(auto_error=False)
DEBUG = os.getenv("USER_DEBUG", "False").lower() == "true"

async def get_request_user(
    auth_header: Optional[HTTPAuthorizationCredentials] = Depends(bearer_scheme),
    x_user_id: Optional[str] = Header(None, alias="X-User-Id")
) -> str:
    """
    Gets the user from token validation or headers.
    Supports X-User-Id as a token or as a raw username in DEBUG mode.
    """
    token = None

    if auth_header and auth_header.credentials:
        token = auth_header.credentials
    elif x_user_id and DEBUG:
        # In debug mode, treat X-User-Id as a direct username
        return x_user_id
    elif x_user_id:
        token = x_user_id

    if token:
        try:
            payload = decode_access_token(token)
            return payload.sub
        except Exception as e:
            raise HTTPException(status_code=401, detail=f"Invalid token: {str(e)}")

    raise HTTPException(status_code=401, detail="Unauthorised")