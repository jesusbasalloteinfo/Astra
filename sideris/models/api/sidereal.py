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
from typing import List, Literal, Optional, Tuple, Union
from models.catalog.sidereal import Star, DeepSky

class EphemerisMovementData(BaseModel):
    alt: float
    az: float
    next_transit: Optional[datetime] = None
    next_rise: Optional[datetime] = None
    next_set: Optional[datetime] = None
    is_circumpolar: Optional[bool]= False
    never_rises: Optional[bool]= False
    description: Optional[str] = None
    fun_fact: Optional[str] = None
    visual_tip: Optional[str] = None
    wikipedia_qid: Optional[str] = None


class StarDataResponse(EphemerisMovementData, Star):
    type: Literal["sidereal"] = "sidereal"

class DSODataResponse(EphemerisMovementData, DeepSky):
    type: Literal["sidereal"] = "sidereal"

SiderealObjectDataResponse = Union[StarDataResponse, DSODataResponse]

class SiderealObjectMetadata(BaseModel):
    id: str
    name: str
    type: Literal["sidereal"] = "sidereal"
    category: str # "star", "galaxy", "nebula", etc.
    common_names: List[str] = Field(default_factory=list)
    
    catalog_names: List[str] = Field(default_factory=list)
    constellation: str
    ra_j2000: float
    dec_j2000: float
    mag: Optional[float] = None
    abs_mag: Optional[float] = None
    b_v: Optional[float] = None
    
    luminosity: Optional[float] = None
    dist: Optional[float] = None
    spectral_type: Optional[str] = None
    size_arcmin: Optional[float] = None

class ConstellationMetadata(BaseModel):
    abbr: str
    name: str
    latin: str
    stars_ids: List[str] 
    lines_indices: List[Tuple[int, int]] 

ObjectMetadata = Union[SiderealObjectMetadata]
