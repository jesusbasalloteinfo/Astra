from pydantic import BaseModel, Field
from typing import Optional

class User(BaseModel):
    
    id: Optional[str] = Field(alias="_id", default=None) # Mongo ids to string id
    name: str
    
    # Populate as the alias or as the field name
    model_config = {"populate_by_name": True}