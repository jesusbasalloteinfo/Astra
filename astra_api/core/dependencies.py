
from typing import Optional

from fastapi import Depends, HTTPException, Header
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer


bearer_scheme = HTTPBearer(auto_error=False)

async def get_request_user(
    auth_header: Optional[HTTPAuthorizationCredentials] = Depends(bearer_scheme),
    x_user_id: Optional[str] = Header(None, alias="X-User-Id")
) -> str:
    """
    Gets the user from kong or dummy headers
    """
    if x_user_id:
        return x_user_id
    
    if auth_header and auth_header.credentials:
        return auth_header.credentials
        
    raise HTTPException(status_code=401, detail="Unauthorised")