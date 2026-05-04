from pydantic import BaseModel, Field
from datetime import datetime
from typing import List, Literal, Optional, Union

class MoonDetails(BaseModel):
    type: Literal["moon"] = "moon"
    illumination_pct: float
    age: Optional[float]=0.0
    phase_angle_deg: float
    limb_angle_deg: float
    next_new_moon: Optional[datetime] = None
    next_full_moon: Optional[datetime] = None

class PlanetDetails(BaseModel):
    type: Literal["planet"] = "planet"
    elongation_deg: float
    phase_angle_deg: float
    illumination_pct: float

ExtraDetails = Union[MoonDetails, PlanetDetails]

class RiseSetTransit(BaseModel):
    is_visible: Optional[bool] = False
    next_rise: Optional[datetime]
    next_transit: Optional[datetime]
    next_set: Optional[datetime]
    
    rise_az: Optional[float] = None
    set_az: Optional[float]  = None
    transit_alt: Optional[float] = None
    transit_visible: Optional[bool] = False

class ObjectLightMetadata(BaseModel):
    id: str
    name: str
    common_names: List[str] = Field(default_factory=list)
    type: Literal["planetary", "star", "moon"] = "planetary"
    dist: float # AU
    mag: Optional[float]

class MotionDelta(BaseModel):
    ttl: int
    target_time: datetime = Field(..., description="Time in UTC for calculation")
    delta_alt: float = Field(description="Delta altitude (arcsec)")
    delta_az:  float = Field(description="Delta Azimuth (arcsec)")
    delta_ra:  float = Field(description="Delta RA (arcsec)")
    delta_dec: float = Field(description="Delta Dec (arcsec)")

class PlanetaryObjectMetadata(BaseModel):
    id: str
    name: str
    common_names: List[str] = Field(default_factory=list)
    type: Literal["planetary", "star", "moon"] = "planetary"
    description: Optional[str] = None
    fun_fact: Optional[str] = None
    visual_tip: Optional[str] = None
    wikipedia_qid: Optional[str] = None
    image_url: Optional[str] = None
    
    dist: float # AU
    mag: Optional[float] = None
    ang_diameter: Optional[float] = None # In arcmin
    
    alt: float
    az: float
    ra_j2000: float
    dec_j2000: float
    motion: MotionDelta

    rise_set_transit: RiseSetTransit
    extra_details: Optional[ExtraDetails] = Field(default=None, discriminator='type')
