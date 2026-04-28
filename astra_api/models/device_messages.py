from enum import Enum
from typing import Callable, Awaitable
from pydantic import BaseModel, Field
from typing import Annotated, Literal, Optional, Union, Dict, Any
from datetime import datetime


class CoordinateTypes(Enum):
    EQUATORIAL_J2000 = "EQUATORIAL_COORD" # Equatorial coordinats at J2000 frame (at 2000)
    EQUATORIAL_EOD = "EQUATORIAL_EOD_COORD" # Equatorial coordinates at Equinox of Date (at this moment)
    HORIZONTAL = "HORIZONTAL_COORD" # Horizontal coordinates with the observer position and date

    @classmethod
    def from_str(cls, value: str):
        """Get the type from a string"""
        try:
            return cls(value.lower())
        except ValueError:
            return cls.EQUATORIAL_EOD

    def __str__(self):
        """Get the device value"""
        return self.value
    
    def get_properties(self) -> tuple[str, str]:
        properties=("ra", "dec")
        if self == CoordinateTypes.HORIZONTAL:
            properties=("alt", "az")
        return properties
    
    @classmethod
    def list(cls):
        """Returns a list with the enum"""
        return [item for item in cls]
    
    @classmethod
    def list_values(cls):
        """Returns a list with the enum values"""
        return [item.value for item in cls]

# --- Coord Data ---

class EquatorialCoordModel(BaseModel):
    """Equatorial coordinates model"""
    ra: float
    dec: float

class HorizontalCoordModel(BaseModel):
    "Horizontal coordinates model"
    alt: float
    az: float

class CoordEventData(BaseModel):
    """Coordinates update model"""
    equatorial_j2000: EquatorialCoordModel
    equatorial_eod: EquatorialCoordModel
    horizontal: HorizontalCoordModel


# --- Message Data ---
class MessageEventData(BaseModel):
    """Message data model"""
    level: Literal["INFO", "WARNING", "ERROR", "DEBUG"] = "INFO"
    content: str
    

# --- Event Payload ---

class CoordEvent(BaseModel):
    """Coord message"""
    event_type: Literal["coord"] = "coord"
    device: str
    device_type: Literal["telescope"] = "telescope"
    data: CoordEventData


class MessageEvent(BaseModel):
    """Common message for all events"""
    event_type: Literal["message"] = "message"
    device: str
    device_type: Literal["indi", "telescope", "camera"]
    data: MessageEventData


EventPayloadUnion = Annotated[
    Union[CoordEvent, MessageEvent], 
    Field(discriminator="event_type")
]

# ------------------------------------------------------------------------------------
# COMMAND TYPES
# ------------------------------------------------------------------------------------

# --- Command Data ---
class SlewCommandData(BaseModel):
    """Slew command parameters for telescope"""
    coord: tuple[float, float]
    input_type: CoordinateTypes = CoordinateTypes.EQUATORIAL_J2000 
    mode: Literal["SLEW", "TRACK", "SYNC"] = "TRACK"

    class Config: # TODO: Maybe we should change to v2 model_config = ConfigDict(use_enum_values=True)
        # String-capable for coordinate types
        use_enum_values = True 

# --- Command Payload ---
class GetDevicesCommand(BaseModel):
    action: Literal["get_devices"] = "get_devices"

class GetTelescopeLocationCommand(BaseModel):
    action: Literal["telescope_location"] = "telescope_location"
    device: str

class SlewCommand(BaseModel):
    action: Literal["slew"] = "slew"
    lane: Literal["MOVEMENT"] = Field("MOVEMENT", frozen=True)
    device: str
    data: SlewCommandData

class AbortCommand(BaseModel):
    action: Literal["abort"] = "abort"
    lane: Literal["MOVEMENT"] = Field("MOVEMENT", frozen=True)
    device: str

CommandPayloadUnion = Annotated[
    Union[GetDevicesCommand, GetTelescopeLocationCommand, SlewCommand, AbortCommand], 
    Field(discriminator="action")
]

# ************************************************************************************
# GLOBAL MESSAGE TYPES
# ************************************************************************************

class EventMessage(BaseModel):
    """Event type message"""
    type: Literal["EVENT"] = Field("EVENT", frozen=True)
    timestamp: datetime
    payload: EventPayloadUnion         

class CommandMessage(BaseModel):
    type: Literal["COMMAND"] = Field("COMMAND", frozen=True)
    req_id: str
    payload: CommandPayloadUnion


class ResponseMessage(BaseModel):
    type: Literal["RESPONSE"] = Field("RESPONSE", frozen=True)
    req_id: str
    status: Literal["OK", "ERROR", "CANCELLED"]
    reason: Optional[str] = None
    data: Optional[Dict[str, Any]] = None



GlobalMessage = Annotated[
    Union[EventMessage, CommandMessage, ResponseMessage],
    Field(discriminator="type")
]

EventListener = Callable[[EventMessage], Awaitable[None]]