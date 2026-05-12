import os
import shutil
from fastapi import APIRouter, HTTPException, Depends, UploadFile, File, Response
from fastapi.responses import FileResponse
from models.auth import UserRegister, UserLogin, TokenResponse, UserProfile
from services.AuthService import AuthService
from core.security import create_access_token, get_public_key
from core.dependencies import get_request_user

router = APIRouter()
auth_service = AuthService()

UPLOADS_DIR = os.getenv("UPLOADS_DIR", "uploads")
PROFILES_DIR = os.path.join(UPLOADS_DIR, "profiles")

if not os.path.exists(PROFILES_DIR):
    os.makedirs(PROFILES_DIR)

@router.post("/register")
async def register(data: UserRegister):
    success = await auth_service.register(data)
    if not success:
        raise HTTPException(status_code=400, detail="Username or email already exists")
    return {"status": "success", "message": "User registered successfully"}

@router.post("/login", response_model=TokenResponse)
async def login(data: UserLogin):
    user = await auth_service.authenticate(data)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid username or password")
    
    token = create_access_token(data={"sub": user.username, "email": user.email})
    return TokenResponse(access_token=token)

@router.get("/public-key")
async def public_key():
    return Response(content=get_public_key(), media_type="application/x-pem-file")

@router.get("/me", response_model=UserProfile)
async def get_me(username: str = Depends(get_request_user)):
    profile = await auth_service.get_profile(username)
    if not profile:
        raise HTTPException(status_code=404, detail="User not found")
    return profile

@router.post("/me/picture")
async def upload_picture(
    file: UploadFile = File(...),
    username: str = Depends(get_request_user)
):
    # Validate file type
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File must be an image")

    # Save file
    file_ext = file.filename.split(".")[-1]
    filename = f"{username}_{int(os.path.getmtime(PROFILES_DIR))}.{file_ext}" # Simple unique filename
    file_path = os.path.join(PROFILES_DIR, filename)

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Update DB
    # We serve them via /api/auth/static/profiles/{filename}
    url = f"/api/auth/static/profiles/{filename}"
    await auth_service.update_profile_picture(username, url)

    return {"url": url}

@router.get("/static/profiles/{filename}")
async def get_profile_picture(filename: str):
    file_path = os.path.join(PROFILES_DIR, filename)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Image not found")
    return FileResponse(file_path)
