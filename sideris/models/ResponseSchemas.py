from pydantic import BaseModel, Field
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Union

from models.CatalogSchemas import Star, DeepSky

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
    is_circumpolar: Optional[bool]= None
    never_rises: Optional[bool]= None


class StarDataResponse(EphemerisMovementData, Star):
    pass

class DSODataResponse(EphemerisMovementData, DeepSky):
    pass

# One of the two are accepted
SiderealObjectDataResponse = Union[StarDataResponse, DSODataResponse]


# ===========================================================================================
# Metadata
# ===========================================================================================

class UIObjectData(BaseModel):
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

class UIConstellation(BaseModel):
    abbr: str
    name: str
    stars_ids: List[str] # TODO S'HA DE CONVERTIR DE HIP AL MEU SISTEMA D'ID!!!
    lines_indices: List[Tuple[int, int]] 

class MetadataCatalogPayload(BaseModel):
    version: str = "1.0"
    total_objects: int
    constellations: List[UIConstellation]
    sky_objects: Dict[str, UIObjectData] 
