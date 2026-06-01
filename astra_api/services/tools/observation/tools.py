"""
ASTRA - Automated Smart Telescope Remote Assistant
Copyright (C) 2026 Jesus Basallote

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""

"""
Tool definitions for astronomical observations to be used by the AI assistant.
"""
from functools import partial
from typing import Literal, Tuple
from pydantic import BaseModel, Field
from services.device_tunnel.tunnel import DeviceTunnel
from services.assistant.tools import CurriedTool, EmptyArgs
from .devices import search_object_impl, get_object_details_impl, slew_to_object_impl

class SearchObjectArgs(BaseModel):
    """Arguments for searching celestial objects."""
    query: str = Field(..., description="The search query for the celestial object.")

def search_object_tool() -> CurriedTool:
    """
    Creates a tool to search for celestial objects in the catalog.

    Returns:
        CurriedTool: The search object tool.
    """
    return CurriedTool(
        name="sideris_search_object",
        description="Searches for celestial objects in the catalog.",
        args_model=SearchObjectArgs,
        func=search_object_impl
    )

class GetDetailsArgs(BaseModel):
    """Arguments for fetching object details."""
    object_id: str = Field(..., description="The unique ID of the object.")
    type: Literal["sidereal", "planetary"] = Field(..., description="The type of the object.")

def get_object_details_tool(location: Tuple[float, float]) -> CurriedTool:
    """
    Creates a tool to fetch detailed information about a specific celestial object.

    Args:
        location (Tuple[float, float]): The observer's location (lat, lon).

    Returns:
        CurriedTool: The object details tool.
    """
    return CurriedTool(
        name="sideris_get_object_details",
        description="Fetches detailed information about a specific celestial object.",
        args_model=GetDetailsArgs,
        func=partial(get_object_details_impl, location=location)
    )

class SlewToArgs(BaseModel):
    """Arguments for commanding a telescope slew."""
    id: str = Field(..., description="The unique ID of the target object.")
    type: Literal["sidereal", "planetary"] = Field(..., description="The type of the object.")
    mode: Literal["TRACK", "SLEW", "SYNC"] = Field(..., description="The movement type. TRACK for slew and tracking, SLEW for movement and SYNC for syncing")

def slew_to_object_tool(tunnel: DeviceTunnel, telescope: str, location: Tuple[float, float]) -> CurriedTool:
    """
    Creates a tool to command the telescope to slew to a specific object.

    Args:
        tunnel (DeviceTunnel): The active tunnel to the Edge device.
        telescope (str): The name of the telescope device.
        location (Tuple[float, float]): The observer's location (lat, lon).

    Returns:
        CurriedTool: The telescope slew tool.
    """
    return CurriedTool(
        name="slew_telescope",
        description="Commands the telescope to slew to a specific object.",
        args_model=SlewToArgs,
        func=partial(slew_to_object_impl, tunnel=tunnel, telescope=telescope, location=location),
        frontend_action=True
    )

# def get_telescope_position_tool(tunnel:DeviceTunnel, telescope:str, location:Tuple[float, float]) -> CurriedTool:
#     return CurriedTool(
#         name="get_telescope_position",
#         description="Fetches the telescope current position.",
#         args_model=EmptyArgs,
#         func=partial(slew_to_object_impl, tunnel=tunnel, telescope=telescope, location=location)
#     )