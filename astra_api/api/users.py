from fastapi import Cookie, FastAPI, APIRouter, HTTPException, Header, Request, Depends, Response
from models.user import Location, User
from services.db.UserService import UserService
from core.db_exceptions import ObjectNotFoundError
from core.dependencies import get_request_user

router = APIRouter()


@router.get("/me", response_model=User)
async def get_user(user: str = Depends(get_request_user)):
    user_service:UserService = UserService()

    try:
        return await user_service.get_user(user)
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