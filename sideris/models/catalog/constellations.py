from pydantic import BaseModel
from typing import List, Tuple

class Constellation(BaseModel):
    abbr: str
    full_name: str
    stars_ids: List[int|str]
    lines_indices: List[Tuple[int, int]]

class ConstellationCatalog(BaseModel):
    constellations: List[Constellation]
