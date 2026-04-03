from datetime import datetime, timezone
from uuid import uuid4

from pydantic import BaseModel, Field
from pydantic.json_schema import SkipJsonSchema 
from typing import Optional

class Location(BaseModel):
    id: Optional[str] = Field(default_factory=lambda: str(uuid4()))
    label: str  # Custom user label
    lat: float
    lng: float
    elevation: float = 0.0
    is_default: Optional[bool] = False


class User(BaseModel):
    
    id:  SkipJsonSchema[Optional[str]] = Field(alias="_id", default=None, exclude=True)# Mongo ids to string id
    username: str

    locations: list[Location] = []
    creation: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    
    
    # Populate as the alias or as the field name
    model_config = {"populate_by_name": True}