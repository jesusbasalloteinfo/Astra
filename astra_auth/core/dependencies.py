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
    """Gets the user from token validation or headers.

    This dependency supports extracting the user identity from either the
    standard Authorization bearer token or a custom X-User-Id header.
    In DEBUG mode, X-User-Id can be treated as a raw username.

    Args:
        auth_header (Optional[HTTPAuthorizationCredentials]): The bearer token credentials.
        x_user_id (Optional[str]): The user ID or token from the X-User-Id header.

    Returns:
        str: The username (subject) of the authenticated user.

    Raises:
        HTTPException: If the token is invalid or no authentication is provided.
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