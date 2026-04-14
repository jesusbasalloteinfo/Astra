from pydantic import BaseModel, Field
from datetime import datetime
from typing import List, Tuple, TypeVar, Generic

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
