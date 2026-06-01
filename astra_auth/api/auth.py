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
    """Register a new user in the system.

    Args:
        data (UserRegister): The registration data containing username, email, and password.

    Returns:
        dict: A success message if registration is successful.

    Raises:
        HTTPException: If the username or email already exists.
    """
    success = await auth_service.register(data)
    if not success:
        raise HTTPException(status_code=400, detail="Username or email already exists")
    return {"status": "success", "message": "User registered successfully"}

@router.post("/login", response_model=TokenResponse)
async def login(data: UserLogin):
    """Authenticate a user and return an access token.

    Args:
        data (UserLogin): The login credentials (username and password).

    Returns:
        TokenResponse: An object containing the access token.

    Raises:
        HTTPException: If authentication fails due to invalid credentials.
    """
    user = await auth_service.authenticate(data)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid username or password")
    
    token = create_access_token(username=user.username, email=user.email)
    return TokenResponse(access_token=token)

@router.get("/public-key")
async def public_key():
    """Retrieve the RS256 public key for token verification.

    Returns:
        Response: The public key in PEM format.
    """
    return Response(content=get_public_key(), media_type="application/x-pem-file")

@router.get("/me", response_model=UserProfile)
async def get_me(username: str = Depends(get_request_user)):
    """Retrieve the profile of the currently authenticated user.

    Args:
        username (str): The username extracted from the JWT token.

    Returns:
        UserProfile: The profile information of the user.

    Raises:
        HTTPException: If the user profile is not found.
    """
    profile = await auth_service.get_profile(username)
    if not profile:
        raise HTTPException(status_code=404, detail="User not found")
    return profile

@router.post("/me/picture")
async def upload_picture(
    file: UploadFile = File(...),
    username: str = Depends(get_request_user)
):
    """Upload and update the profile picture for the authenticated user.

    Args:
        file (UploadFile): The image file to be uploaded.
        username (str): The username of the user performing the upload.

    Returns:
        dict: A dictionary containing the URL of the uploaded profile picture.

    Raises:
        HTTPException: If the uploaded file is not an image.
    """
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
    """Serve a user's profile picture.

    Args:
        filename (str): The name of the profile picture file to retrieve.

    Returns:
        FileResponse: The requested image file.

    Raises:
        HTTPException: If the image file is not found.
    """
    file_path = os.path.join(PROFILES_DIR, filename)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Image not found")
    return FileResponse(file_path)
