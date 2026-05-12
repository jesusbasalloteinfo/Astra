from datetime import datetime, timezone
from uuid import uuid4

from pydantic import BaseModel, Field
from pydantic.json_schema import SkipJsonSchema 
from typing import Optional

class Location(BaseModel):
    id: Optional[str] = Field(default_factory=lambda: str(uuid4()))
    label: str  # Custom user label
    lat: float = Field(..., ge=-90, le=90, description="Latitude")
    lng: float = Field(..., ge=-180, le=180, description="Longitude")
    elevation: float = 0.0
    timezone: float = 0.0
    is_default: Optional[bool] = False

class UserSettings(BaseModel):
    theme: str = "standard"
    language: str = "en"

class User(BaseModel):
    
    id:  SkipJsonSchema[Optional[str]] = Field(alias="_id", default=None, exclude=True)# Mongo ids to string id
    username: str
    full_name: Optional[str] = None
    bio: Optional[str] = None
    
    settings: UserSettings = Field(default_factory=UserSettings)

    locations: list[Location] = []
    
    creation: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    
    
    # Populate as the alias or as the field name
    model_config = {"populate_by_name": True}