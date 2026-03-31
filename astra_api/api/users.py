from fastapi import Cookie, FastAPI, APIRouter, HTTPException, Header, Request, Depends, Response
from models.user import User
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

