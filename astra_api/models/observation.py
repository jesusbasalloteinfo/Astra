from datetime import datetime, timezone

from pydantic import BaseModel, Field
from typing import Optional

class Observation(BaseModel):
    
    id:  Optional[str] = Field(alias="_id", default=None)# Mongo ids to string id
    name: str
    description: Optional[str] = None
    owner: str
    creation: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    last_used: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    deleted: Optional[bool] = False
    
    # Populate as the alias or as the field name
    model_config = {"populate_by_name": True}