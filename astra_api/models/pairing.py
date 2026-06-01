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
Models for device pairing in astra_api.
"""
from typing import Any, Literal
from pydantic import BaseModel


# ── Pairing ──────────────────────────────────────

class WsPairingCode(BaseModel):
    """
    Message sent to the device to provide a pairing code.

    Attributes:
        type (Literal["PAIRING_CODE"]): The message type identifier.
        code (str): The numeric or alphanumeric pairing code.
    """
    type: Literal["PAIRING_CODE"] = "PAIRING_CODE"
    code: str

class WsPairedSuccess(BaseModel):
    """
    Message sent to the device when pairing is successful.

    Attributes:
        type (Literal["PAIRED_SUCCESS"]): The message type identifier.
        token (str): The authentication token for future requests.
        ws_url (str): The WebSocket URL for the persistent tunnel.
    """
    type: Literal["PAIRED_SUCCESS"] = "PAIRED_SUCCESS"
    token: str
    ws_url: str


class PairingRequest(BaseModel):
    """
    Request model for the pairing process initiated by a user.

    Attributes:
        pin (str): The PIN provided by the device.
    """
    pin: str
