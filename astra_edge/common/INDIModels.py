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
Models for INDI messages and command/event payloads used in astra_edge.
"""
from pydantic import BaseModel, Field
from typing import Annotated, Literal, Optional, Union, Dict, Any
from datetime import datetime
from utils.CoordinateHandler import CoordinateTypes

# --- Coord Data ---

class EquatorialCoordModel(BaseModel):
    """
    Model for Equatorial coordinates (Right Ascension and Declination).

    Attributes:
        ra (float): Right Ascension in decimal hours.
        dec (float): Declination in decimal degrees.
    """
    ra: float
    dec: float

class HorizontalCoordModel(BaseModel):
    """
    Model for Horizontal coordinates (Altitude and Azimuth).

    Attributes:
        alt (float): Altitude in decimal degrees.
        az (float): Azimuth in decimal degrees.
    """
    alt: float
    az: float

class CoordEventData(BaseModel):
    """
    Consolidated coordinate update model containing multiple coordinate frames.

    Attributes:
        equatorial_j2000 (EquatorialCoordModel): Coordinates in J2000 frame.
        equatorial_eod (EquatorialCoordModel): Coordinates in Equinox of Date frame.
        horizontal (HorizontalCoordModel): Local horizontal coordinates.
    """
    equatorial_j2000: EquatorialCoordModel
    equatorial_eod: EquatorialCoordModel
    horizontal: HorizontalCoordModel


# --- Message Data ---
class MessageEventData(BaseModel):
    """
    Model for log or status messages emitted by devices.

    Attributes:
        level (Literal["INFO", "WARNING", "ERROR", "DEBUG"]): The severity level of the message.
        content (str): The textual content of the message.
    """
    level: Literal["INFO", "WARNING", "ERROR", "DEBUG"] = "INFO"
    content: str
    

# --- Event Payload ---

class CoordEvent(BaseModel):
    """
    Payload for a coordinate update event.

    Attributes:
        event_type (Literal["coord"]): Discriminator for coordinate events.
        device (str): Name of the device emitting the event.
        device_type (Literal["telescope"]): Type of the device.
        data (CoordEventData): The coordinate data.
    """
    event_type: Literal["coord"] = "coord"
    device: str
    device_type: Literal["telescope"] = "telescope"
    data: CoordEventData


class MessageEvent(BaseModel):
    """
    Payload for a general message/log event.

    Attributes:
        event_type (Literal["message"]): Discriminator for message events.
        device (str): Name of the device emitting the event.
        device_type (Literal["indi", "telescope", "camera"]): Type of the device.
        data (MessageEventData): The message data.
    """
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
    """
    Data for a telescope slew command.

    Attributes:
        coord (tuple[float, float]): Target coordinates (e.g., [ra, dec] or [alt, az]).
        input_type (CoordinateTypes): The coordinate frame of the input coordinates.
        mode (Literal["SLEW", "TRACK", "SYNC"]): The operation mode for the telescope.
    """
    coord: tuple[float, float]
    input_type: CoordinateTypes = CoordinateTypes.EQUATORIAL_J2000 
    mode: Literal["SLEW", "TRACK", "SYNC"] = "TRACK"

    class Config: # TODO: Maybe we should change to v2 model_config = ConfigDict(use_enum_values=True)
        # String-capable for coordinate types
        use_enum_values = True 

# --- Command Payload ---
class GetDevicesCommand(BaseModel):
    """
    Command to request the list of available INDI devices.

    Attributes:
        action (Literal["get_devices"]): Discriminator for the get_devices command.
    """
    action: Literal["get_devices"] = "get_devices"

class GetTelescopeLocationCommand(BaseModel):
    """
    Command to request the observer's location set in the telescope.

    Attributes:
        action (Literal["telescope_location"]): Discriminator for the location command.
        device (str): Name of the telescope device.
    """
    action: Literal["telescope_location"] = "telescope_location"
    device: str

class SlewCommand(BaseModel):
    """
    Command to initiate a slew operation on a telescope.

    Attributes:
        action (Literal["slew"]): Discriminator for the slew command.
        lane (Literal["MOVEMENT"]): Execution lane for concurrency management.
        device (str): Name of the telescope device.
        data (SlewCommandData): Slew parameters.
    """
    action: Literal["slew"] = "slew"
    lane: Literal["MOVEMENT"] = Field("MOVEMENT", frozen=True)
    device: str
    data: SlewCommandData

class AbortCommand(BaseModel):
    """
    Command to immediately stop device movement.

    Attributes:
        action (Literal["abort"]): Discriminator for the abort command.
        lane (Literal["MOVEMENT"]): Execution lane for concurrency management.
        device (str): Name of the device to abort.
    """
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
    """
    Top-level message wrapper for events sent from Edge to API.

    Attributes:
        type (Literal["EVENT"]): Message type discriminator.
        timestamp (datetime): When the event occurred.
        payload (EventPayloadUnion): The specific event data.
    """
    type: Literal["EVENT"] = Field("EVENT", frozen=True)
    timestamp: datetime
    payload: EventPayloadUnion         

class CommandMessage(BaseModel):
    """
    Top-level message wrapper for commands sent from API to Edge.

    Attributes:
        type (Literal["COMMAND"]): Message type discriminator.
        req_id (str): Unique request identifier for tracking responses.
        payload (CommandPayloadUnion): The specific command data.
    """
    type: Literal["COMMAND"] = Field("COMMAND", frozen=True)
    req_id: str
    payload: CommandPayloadUnion


class ResponseMessage(BaseModel):
    """
    Top-level message wrapper for command responses sent from Edge to API.

    Attributes:
        type (Literal["RESPONSE"]): Message type discriminator.
        req_id (str): The identifier of the original request.
        status (Literal["OK", "ERROR", "CANCELLED"]): The outcome of the command.
        reason (Optional[str]): Error or cancellation details.
        data (Optional[Dict[str, Any]]): Additional response data.
    """
    type: Literal["RESPONSE"] = Field("RESPONSE", frozen=True)
    req_id: str
    status: Literal["OK", "ERROR", "CANCELLED"]
    reason: Optional[str] = None
    data: Optional[Dict[str, Any]] = None



GlobalMessage = Annotated[
    Union[EventMessage, CommandMessage, ResponseMessage],
    Field(discriminator="type")
]
