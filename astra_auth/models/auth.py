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

class JWTPayload(BaseModel):
    sub: str  # Username
    email: str
    exp: datetime
    iat: datetime
