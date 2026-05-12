from datetime import datetime, timezone
from pydantic import BaseModel, Field
from pydantic.json_schema import SkipJsonSchema 
from typing import Optional

class AuthUser(BaseModel):
    id: SkipJsonSchema[Optional[str]] = Field(alias="_id", default=None)
    username: str
    email: str
    password: str 
    profile_picture_url: Optional[str] = None
    creation: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    model_config = {"populate_by_name": True}

class UserRegister(BaseModel):
    username: str
    email: str
    password: str

class UserLogin(BaseModel):
    username: str
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"

class UserProfile(BaseModel):
    username: str
    email: str
    profile_picture_url: Optional[str] = None
    creation: datetime
