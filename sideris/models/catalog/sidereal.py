from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
class Star(BaseModel):
    id: str
    name: str
    category: str = Field(default="star", validation_alias="type")
    common_names: List[str] = Field(default_factory=list)
    catalog_names: List[str] = Field(default_factory=list)
    mag: Optional[float] = None
    abs_mag: Optional[float] = None
    luminosity: Optional[float] = None
    spectral_type: Optional[str] = None
    dist_ly: Optional[float] = None
    ra_j2000: float
    dec_j2000: float
    constellation: str
    b_v: Optional[float] = None
    pmra_mas: float
    pmdec_mas: float

class DeepSky(BaseModel):
    model_config = {"populate_by_name": True}
    id: str
    name: str
    category: str = Field(..., alias="type")
    common_names: List[str] = Field(default_factory=list)
    catalog_names: List[str] = Field(default_factory=list)
    mag: Optional[float] = None
    size_arcmin: Optional[float] = None
    constellation: str
    ra_j2000: float
    dec_j2000: float

class Metadata(BaseModel):
    total_objects: int
    catalogs: Dict[str, Any]

class CatalogData(BaseModel):
    stars: List[Star]
    deep_sky: List[DeepSky]

class AstronomicalCatalog(BaseModel):
    metadata: Metadata
    data: CatalogData
