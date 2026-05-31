"""
Models for device pairing in astra_api.
"""
from __future__ import annotations
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
