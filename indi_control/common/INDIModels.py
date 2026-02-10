from pydantic import BaseModel, Field
from typing import Annotated, Literal, Union, Dict, Any
from datetime import datetime

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
    """Common message for all events"""
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

# --- Messages ---


class EventMessage(BaseModel):
    """Event type message"""
    type: Literal["event"] = "event"            
    timestamp: datetime
    payload: EventPayloadUnion         


# TODO: COMMAND and RESPONSE types

GlobalMessage = Annotated[
    Union[EventMessage],
    Field(discriminator="type")
]