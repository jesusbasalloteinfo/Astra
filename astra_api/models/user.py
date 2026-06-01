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
Models for user profiles and settings in astra_api.
"""
from datetime import datetime, timezone
from uuid import uuid4

from pydantic import BaseModel, Field
from pydantic.json_schema import SkipJsonSchema 
from typing import Optional

class Location(BaseModel):
    """
    Model representing a geographic location saved by a user.

    Attributes:
        id (str): Unique identifier for the location.
        label (str): Custom label given by the user (e.g., 'Home').
        lat (float): Latitude in decimal degrees.
        lng (float): Longitude in decimal degrees.
        elevation (float): Elevation in meters.
        timezone (float): Timezone offset from UTC.
        is_default (Optional[bool]): Flag indicating if this is the user's primary location.
    """
    id: Optional[str] = Field(default_factory=lambda: str(uuid4()))
    label: str  # Custom user label
    lat: float = Field(..., ge=-90, le=90, description="Latitude")
    lng: float = Field(..., ge=-180, le=180, description="Longitude")
    elevation: float = 0.0
    timezone: float = 0.0
    is_default: Optional[bool] = False

class UserSettings(BaseModel):
    """
    Model for user-specific UI and application settings.

    Attributes:
        theme (str): Preferred UI theme name.
        language (str): Preferred language code.
    """
    theme: str = "standard"
    language: str = "en"

class User(BaseModel):
    """
    Model representing a user profile within astra_api.

    Attributes:
        id (Optional[str]): The unique identifier (MongoDB ID), excluded from JSON schema.
        username (str): The unique username.
        full_name (Optional[str]): The user's full name.
        bio (Optional[str]): A short user biography.
        settings (UserSettings): The user's application settings.
        locations (list[Location]): List of locations saved by the user.
        creation (datetime): The timestamp when the user profile was created.
    """
    
    id:  SkipJsonSchema[Optional[str]] = Field(alias="_id", default=None, exclude=True)# Mongo ids to string id
    username: str
    full_name: Optional[str] = None
    bio: Optional[str] = None
    
    settings: UserSettings = Field(default_factory=UserSettings)

    locations: list[Location] = []
    
    creation: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    
    
    # Populate as the alias or as the field name
    model_config = {"populate_by_name": True}
