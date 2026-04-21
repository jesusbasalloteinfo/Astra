from __future__ import annotations
from typing import Any, Literal
from pydantic import BaseModel


# ── Pairing ──────────────────────────────────────

class WsPairingCode(BaseModel):
    type: Literal["PAIRING_CODE"] = "PAIRING_CODE"
    code: str

class WsPairedSuccess(BaseModel):
    type: Literal["PAIRED_SUCCESS"] = "PAIRED_SUCCESS"
    token: str
    ws_url: str


class PairingRequest(BaseModel):
    pin: str
