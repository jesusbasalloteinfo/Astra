from functools import partial
from typing import Literal, Tuple
from pydantic import BaseModel, Field
from services.device_tunnel.tunnel import DeviceTunnel
from services.assistant.tools import CurriedTool, EmptyArgs
from .devices import search_object_impl, get_object_details_impl, slew_to_object_impl

class SearchObjectArgs(BaseModel):
    query: str = Field(..., description="The search query for the celestial object.")

def search_object_tool() -> CurriedTool:
    return CurriedTool(
        name="search_object",
        description="Searches for celestial objects in the catalog.",
        args_model=SearchObjectArgs,
        func=search_object_impl
    )

class GetDetailsArgs(BaseModel):
    object_id: str = Field(..., description="The unique ID of the object.")
    type: Literal["sidereal", "planetary"] = Field(..., description="The type of the object.")

def get_object_details_tool(location:Tuple[float, float]) -> CurriedTool:
    return CurriedTool(
        name="get_object_details",
        description="Fetches detailed information about a specific celestial object.",
        args_model=GetDetailsArgs,
        func=partial(get_object_details_impl, location=location)
    )

class SlewToArgs(BaseModel):
    object_id: str = Field(..., description="The unique ID of the target object.")
    type: Literal["sidereal", "planetary"] = Field(..., description="The type of the object.")
    mode: Literal["TRACK", "SLEW", "SYNC"] = Field(..., description="The movement type. TRACK for slew and tracking, SLEW for movement and SYNC for syncing")

def slew_to_object_tool(tunnel:DeviceTunnel, telescope:str, location:Tuple[float, float]) -> CurriedTool:
    return CurriedTool(
        name="slew_to_object",
        description="Commands the telescope to slew to a specific object.",
        args_model=SlewToArgs,
        func=partial(slew_to_object_impl, tunnel=tunnel, telescope=telescope, location=location)
    )

# def get_telescope_position_tool(tunnel:DeviceTunnel, telescope:str, location:Tuple[float, float]) -> CurriedTool:
#     return CurriedTool(
#         name="get_telescope_position",
#         description="Fetches the telescope current position.",
#         args_model=EmptyArgs,
#         func=partial(slew_to_object_impl, tunnel=tunnel, telescope=telescope, location=location)
#     )