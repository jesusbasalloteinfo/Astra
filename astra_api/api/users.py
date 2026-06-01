"""
ASTRA - Automated Smart Telescope Remote Assistant
Copyright (C) 2026 Jesus Basallote

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""

"""
FastAPI router for user profile and settings management in astra_api.
"""
import httpx
import os
from typing import Optional
from fastapi import Cookie, FastAPI, APIRouter, HTTPException, Header, Request, Depends, Response
from pydantic import BaseModel
from models.user import Location, User
from services.db.UserService import UserService
from core.db_exceptions import ObjectNotFoundError
from core.dependencies import get_request_user, bearer_scheme
from fastapi.security import HTTPAuthorizationCredentials

router = APIRouter()

AUTH_ME_URL = os.getenv("AUTH_ME_URL", "http://astra_auth:80/api/auth/me")

class UserEnriched(User):
    """User profile enriched with identity data from the auth service."""
    email: Optional[str] = None
    profile_picture_url: Optional[str] = None

class UserUpdate(BaseModel):
    """Request model for updating basic user information."""
    full_name: Optional[str] = None
    bio: Optional[str] = None

class SettingsUpdate(BaseModel):
    """Request model for updating user application settings."""
    theme: Optional[str] = None
    language: Optional[str] = None

@router.get("/me", response_model=UserEnriched)
async def get_user(
    username: str = Depends(get_request_user),
    auth: HTTPAuthorizationCredentials = Depends(bearer_scheme)
):
    """
    Retrieves the current user's profile and settings.

    Enriches local database data with identity information (email, picture)
    from the central authentication service.

    Args:
        username (str): The authenticated username.
        auth (HTTPAuthorizationCredentials): The raw bearer token for enrichment.

    Returns:
        UserEnriched: The complete user profile.

    Raises:
        HTTPException: If the user is not found in the local database.
    """
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

@router.put("/me")
async def update_user(data: UserUpdate, username: str = Depends(get_request_user)):
    """
    Updates the current user's profile information.

    Args:
        data (UserUpdate): The update data.
        username (str): The authenticated username.

    Returns:
        dict: Success status.

    Raises:
        HTTPException: If the update fails.
    """
    service = UserService()
    # Filter out None values
    update_data = {k: v for k, v in data.model_dump().items() if v is not None}
    if not update_data:
        return {"status": "success", "message": "No changes to apply"}
        
    success = await service.update_user(username, update_data)
    if not success:
        raise HTTPException(status_code=400, detail="Could not update user profile")
    return {"status": "success"}

@router.put("/me/settings")
async def update_settings(data: SettingsUpdate, username: str = Depends(get_request_user)):
    """
    Updates the current user's application settings.

    Args:
        data (SettingsUpdate): The update data.
        username (str): The authenticated username.

    Returns:
        dict: Success status.

    Raises:
        HTTPException: If the update fails.
    """
    service = UserService()
    # Use dot notation for nested update to avoid overwriting other settings
    update_data = {f"settings.{k}": v for k, v in data.model_dump().items() if v is not None}
    if not update_data:
        return {"status": "success", "message": "No changes to apply"}
        
    success = await service.update_user(username, update_data)
    if not success:
        raise HTTPException(status_code=400, detail="Could not update settings")
    return {"status": "success"}

@router.post("/me/locations")
async def add_location(location: Location, user: str = Depends(get_request_user)):
    """
    Adds a new geographic location to the current user's profile.

    Args:
        location (Location): The location data.
        user (str): The authenticated username.

    Returns:
        dict: Success status.

    Raises:
        HTTPException: If the location cannot be added.
    """
    service = UserService()
    success = await service.add_location(user, location)
    if not success:
        raise HTTPException(status_code=400, detail="Could not add location")
    return {"status": "success"}


@router.delete("/me/locations/{location_id}")
async def delete_location(location_id: str, user: str = Depends(get_request_user)):
    """
    Deletes a specific geographic location from the user's profile.

    Args:
        location_id (str): The location ID to remove.
        user (str): The authenticated username.

    Returns:
        dict: Success status.

    Raises:
        HTTPException: If the location cannot be deleted.
    """
    service = UserService()
    success = await service.remove_location(user, location_id)
    if not success:
        raise HTTPException(status_code=400, detail="Could not delete location")
    return {"status": "success"}
