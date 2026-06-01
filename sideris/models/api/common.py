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

from pydantic import BaseModel, Field
from datetime import datetime
from typing import List, Optional, Tuple, TypeVar, Generic

T = TypeVar('T')

class SyncPayload(BaseModel):
    target_time: datetime = Field(..., description="Time in UTC for calculation")
    ttl: float = Field(120.0, description="Time to live in seconds for the velocities")
    # Updates: [id (str), alt (float), az (float), d_alt (float), d_az (float)]
    updates: List[Tuple[str, float, float, float, float]]

class MetadataCatalogPayload(BaseModel, Generic[T]):
    version: str = "1.0"
    total: int
    data: T

class SearchResultItem(BaseModel):
    id: str
    name: str
    type: str
    category: str
