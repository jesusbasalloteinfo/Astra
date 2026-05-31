"""
Models for astronomical observations in astra_api.
"""
from datetime import datetime, timezone

from pydantic import BaseModel, Field
from typing import Optional

class Observation(BaseModel):
    """
    Model representing an astronomical observation session.

    Attributes:
        id (Optional[str]): The unique identifier (MongoDB ID).
        name (str): The name of the observation.
        description (Optional[str]): A brief description of the observation.
        owner (str): The username of the owner of this observation.
        creation (datetime): The timestamp when the observation was created.
        last_used (datetime): The timestamp of the last activity in this observation.
        deleted (Optional[bool]): Flag indicating if the observation is marked as deleted.
    """
    
    id:  Optional[str] = Field(alias="_id", default=None)# Mongo ids to string id
    name: str
    description: Optional[str] = None
    owner: str
    creation: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    last_used: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    deleted: Optional[bool] = False
    
    # Populate as the alias or as the field name
    model_config = {"populate_by_name": True}
