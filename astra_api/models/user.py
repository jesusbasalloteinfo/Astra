from pydantic import BaseModel, Field
from pydantic.json_schema import SkipJsonSchema 
from typing import Optional

class User(BaseModel):
    
    id:  SkipJsonSchema[Optional[str]] = Field(alias="_id", default=None, exclude=True)# Mongo ids to string id
    username: str
    
    # Populate as the alias or as the field name
    model_config = {"populate_by_name": True}