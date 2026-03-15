from pydantic import BaseModel, Field
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Union

from models.CatalogSchemas import Star, DeepSky



# ===========================================================================================
# Payload
# ===========================================================================================

class SyncPayload(BaseModel):
    target_time: datetime = Field(..., description="Time in UTC for calculation")
    ttl: float = Field(120.0, description="Time to live in seconds for the velocities")
    # Updates: [id (str), alt (float), az (float), d_alt (float), d_az (float)]
    updates: List[Tuple[str, float, float, float, float]]

class EphemerisMovementData(BaseModel):
    alt: float
    az: float
    next_transit: Optional[datetime] = None
    next_rise: Optional[datetime] = None
    next_set: Optional[datetime] = None
    is_circumpolar: Optional[bool]= False
    never_rises: Optional[bool]= False

class StarDataResponse(EphemerisMovementData, Star):
    pass

class DSODataResponse(EphemerisMovementData, DeepSky):
    pass

SiderealObjectDataResponse = Union[StarDataResponse, DSODataResponse]


# ===========================================================================================
# Metadata
# ===========================================================================================

class SiderealObjectMetadata(BaseModel):
    id: str
    name: str
    type: str # "star", "galaxy", "nebula", etc.
    common_names: List[str] = Field(default_factory=list)
    catalog_names: List[str] = Field(default_factory=list)
    constellation: str
    mag: Optional[float] = None
    abs_mag: Optional[float] = None
    b_v: Optional[float] = None
    
    luminosity: Optional[float] = None
    distance_ly: Optional[float] = None
    spectral_type: Optional[str] = None
    size_arcmin: Optional[float] = None

class SolarSistemObjectMetadata(BaseModel):
    id: str
    name: str
    type: str # "planet", "moon"

class ConstellationMetadata(BaseModel):
    abbr: str
    name: str
    stars_ids: List[str] 
    lines_indices: List[Tuple[int, int]] 

ObjectMetadata = Union[SolarSistemObjectMetadata, SiderealObjectMetadata]

class MetadataCatalogPayload(BaseModel):
    version: str = "1.0"
    total: int
    data: Union[Dict[str, ObjectMetadata], List[ConstellationMetadata]]
