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
