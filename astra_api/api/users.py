import httpx
import os
from typing import Optional
from fastapi import Cookie, FastAPI, APIRouter, HTTPException, Header, Request, Depends, Response
from models.user import Location, User
from services.db.UserService import UserService
from core.db_exceptions import ObjectNotFoundError
from core.dependencies import get_request_user, bearer_scheme
from fastapi.security import HTTPAuthorizationCredentials

router = APIRouter()

AUTH_ME_URL = os.getenv("AUTH_ME_URL", "http://astra_auth:80/api/auth/me")

class UserEnriched(User):
    email: Optional[str] = None
    profile_picture_url: Optional[str] = None

@router.get("/me", response_model=UserEnriched)
async def get_user(
    username: str = Depends(get_request_user),
    auth: HTTPAuthorizationCredentials = Depends(bearer_scheme)
):
    user_service: UserService = UserService()

    try:
        # Get app data (locations) from local DB
        user_data = await user_service.get_user(username)
        
        # Create enriched response
        enriched_user = UserEnriched(**user_data.model_dump())
        
        # Enrich with identity data from astra_auth
        try:
            async with httpx.AsyncClient() as client:
                headers = {"Authorization": f"Bearer {auth.credentials}"}
                response = await client.get(AUTH_ME_URL, headers=headers)
                if response.status_code == 200:
                    auth_info = response.json()
                    enriched_user.email = auth_info.get("email")
                    enriched_user.profile_picture_url = auth_info.get("profile_picture_url")
        except Exception:
            # Fallback: return what we have from local DB
            pass

        return enriched_user
    except ObjectNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/me/locations")
async def add_location(location: Location, user: str = Depends(get_request_user)):
    service = UserService()
    success = await service.add_location(user, location)
    if not success:
        raise HTTPException(status_code=400, detail="Could not add location")
    return {"status": "success"}


@router.delete("/me/locations/{location_id}")
async def delete_location(location_id: str, user: str = Depends(get_request_user)):
    service = UserService()
    success = await service.remove_location(user, location_id)
    if not success:
        raise HTTPException(status_code=400, detail="Could not delete location")
    return {"status": "success"}