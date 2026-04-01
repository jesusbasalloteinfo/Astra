from fastapi import APIRouter, HTTPException, Depends, status
from typing import List, Optional
from pydantic import BaseModel

from models.observation import Observation
from services.db.ObservationService import ObservationService
from core.db_exceptions import ObjectNotFoundError, ObjectAlreadyExistsError
from core.dependencies import get_request_user

router = APIRouter()

# --- Request Schemas ---

class ObservationCreate(BaseModel):
    name: str
    description: Optional[str] = None

class ObservationUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None

# --- Endpoints ---

@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_obs(
    data: ObservationCreate, 
    username: str = Depends(get_request_user)
):
    service = ObservationService()
    try:
        # Create Observation from the schema
        new_obs = Observation(**data.model_dump(), owner=username)
        obs_id = await service.create_observation(new_obs)
        return {"id": obs_id, "message": "Observation created successfully"}
    except ObjectAlreadyExistsError as e:
        raise HTTPException(status_code=409, detail=str(e))


@router.get("/", response_model=List[Observation], response_model_by_alias=False)
async def list_obs(username: str = Depends(get_request_user)):
    service = ObservationService()
    return await service.get_owner_observations(username)


@router.get("/{obs_id}", response_model=Observation, response_model_by_alias=False)
async def get_obs(
    obs_id: str, 
    username: str = Depends(get_request_user)
):
    service = ObservationService()
    try:
        return await service.get_observation(obs_id, username)
    except ObjectNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.patch("/{obs_id}")
async def update_obs(
    obs_id: str, 
    data: ObservationUpdate, 
    username: str = Depends(get_request_user)
):
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
    service = ObservationService()
    try:
        await service.delete_observation(obs_id, username)
        return None 
    except ObjectNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))