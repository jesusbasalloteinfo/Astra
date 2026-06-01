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
FastAPI router for astronomical observation management in astra_api.
"""
from datetime import datetime

from fastapi import APIRouter, HTTPException, Depends, status
from typing import List, Optional
from pydantic import BaseModel

from models.observation import Observation
from services.db.ObservationService import ObservationService
from core.db_exceptions import ObjectNotFoundError, ObjectAlreadyExistsError
from core.dependencies import get_request_user

router = APIRouter()

# --- Request Schemas ---

class ObservationResponse(BaseModel):
    """Data model for observation listing and detail responses."""
    id: str
    name: str
    description: Optional[str] = None
    owner: str
    creation: datetime
    last_used: datetime
    
    model_config = {"from_attributes": True} # Read the atributes from DB

class ObservationCreate(BaseModel):
    """Request model for creating a new observation."""
    name: str
    description: Optional[str] = None

class ObservationUpdate(BaseModel):
    """Request model for updating observation details."""
    name: Optional[str] = None
    description: Optional[str] = None

# --- Endpoints ---

@router.get("", response_model=List[ObservationResponse], response_model_by_alias=False)
async def list_obs(username: str = Depends(get_request_user)):
    """
    Lists all active observations belonging to the authenticated user.

    Args:
        username (str): The authenticated username.

    Returns:
        List[ObservationResponse]: The list of user observations.
    """
    service = ObservationService()
    return await service.get_owner_observations(username)


@router.get("/{obs_id}", response_model=ObservationResponse, response_model_by_alias=False)
async def get_obs(
    obs_id: str, 
    username: str = Depends(get_request_user)
):
    """
    Retrieves detailed information for a specific observation.

    Args:
        obs_id (str): The observation ID.
        username (str): The authenticated username.

    Returns:
        ObservationResponse: The observation details.

    Raises:
        HTTPException: If the observation is not found or access is denied.
    """
    service = ObservationService()
    try:
        return await service.get_observation(obs_id, username)
    except ObjectNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_obs(
    data: ObservationCreate, 
    username: str = Depends(get_request_user)
):
    """
    Creates a new astronomical observation session.

    Args:
        data (ObservationCreate): The observation data.
        username (str): The authenticated username.

    Returns:
        dict: The identifier of the created observation and a success message.

    Raises:
        HTTPException: If an observation with the same name already exists.
    """
    service = ObservationService()
    try:
        # Create Observation from the schema
        new_obs = Observation(**data.model_dump(), owner=username)
        obs_id = await service.create_observation(new_obs)
        return {"id": obs_id, "message": "Observation created successfully"}
    except ObjectAlreadyExistsError as e:
        raise HTTPException(status_code=409, detail=str(e))



@router.patch("/{obs_id}")
async def update_obs(
    obs_id: str, 
    data: ObservationUpdate, 
    username: str = Depends(get_request_user)
):
    """
    Updates the name or description of an existing observation.

    Args:
        obs_id (str): The observation ID.
        data (ObservationUpdate): The update fields.
        username (str): The authenticated username.

    Returns:
        dict: Success status.

    Raises:
        HTTPException: If the observation is not found.
    """
    service = ObservationService()
    try:
        success = await service.update_observation_info(
            obs_id, 
            username, 
            **data.model_dump(exclude_unset=True) # As dict
        )
        return {"success": success}
    except ObjectNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.delete("/{obs_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_obs(
    obs_id: str, 
    username: str = Depends(get_request_user)
):
    """
    Soft-deletes an astronomical observation.

    Args:
        obs_id (str): The observation ID.
        username (str): The authenticated username.

    Returns:
        None

    Raises:
        HTTPException: If the observation is not found or access is denied.
    """
    service = ObservationService()
    try:
        await service.delete_observation(obs_id, username)
        return None 
    except ObjectNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
