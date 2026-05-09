from typing import Literal

from pydantic import BaseModel, Field

from services.assistant.tools import CurriedTool

class FlyConstArgs(BaseModel):
    abbr: str = Field(..., description="IAU constellation abbreviation")

def fly_to_const_tool() -> CurriedTool:
    return CurriedTool(
        name="fly_to_constellation",
        description="Flies the user camera to a constellation",
        args_model=FlyConstArgs,
        frontend_only=True
    )

class FocusObjectArgs(BaseModel):
    id: str = Field(..., description="The id of the object to select.")
    type: Literal["sidereal", "planetary"] = Field(..., description="The object type (planetary for Solar System objects, sidereal for any other).")

def focus_object_element_tool() -> CurriedTool:
    return CurriedTool(
        name="focus_object",
        description="Centers a celestial object in the user's UI",
        args_model=FocusObjectArgs,
        frontend_only=True
    )

