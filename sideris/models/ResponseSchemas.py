from pydantic import BaseModel, Field
from datetime import datetime
from typing import List, Optional, Tuple, Union

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