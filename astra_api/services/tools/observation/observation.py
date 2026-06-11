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
Frontend-only observation tools for the AI assistant.
"""
from typing import Literal

from pydantic import BaseModel, Field

from services.assistant.tools import CurriedTool

class FlyConstArgs(BaseModel):
    """Arguments for flying to a constellation."""
    abbr: str = Field(..., description="IAU constellation abbreviation")

def fly_to_const_tool() -> CurriedTool:
    """
    Creates a tool that flies the user's camera to a specific constellation.

    Returns:
        CurriedTool: The fly-to-constellation tool.
    """
    return CurriedTool(
        name="fly_to_constellation",
        description="Flies the user camera to a constellation",
        args_model=FlyConstArgs,
        frontend_only=True
    )

class FocusObjectArgs(BaseModel):
    """Arguments for focusing on an object."""
    id: str = Field(..., description="The id of the object to select.")
    name: str = Field(None, description="The human-readable name of the object in the user's language (e.g., 'Andromeda Galaxy').")
    type: Literal["sidereal", "planetary"] = Field(..., description="The object type (planetary for Solar System objects, sidereal for any other).")

def focus_object_element_tool() -> CurriedTool:
    """
    Creates a tool that centers a celestial object in the user's UI.

    Returns:
        CurriedTool: The focus object tool.
    """
    return CurriedTool(
        name="focus_object",
        description="Centers a celestial object in the user's UI",
        args_model=FocusObjectArgs,
        frontend_only=True
    )
