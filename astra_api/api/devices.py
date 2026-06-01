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

from datetime import datetime
from typing import List, Literal

from pydantic import BaseModel, Field
import uvicorn
from fastapi import APIRouter, Depends, WebSocket, HTTPException, Header, status
from services.db import DeviceService
from core.db_exceptions import ObjectAlreadyExistsError, ObjectNotFoundError
from core.dependencies import get_request_user
from models.pairing import PairingRequest
from services.device_tunnel.pairing_manager import pairing_manager
from services.device_tunnel.tunnel import DeviceTunnel, tunnel_manager
from models.device_messages import GetDevicesCommand, GetTelescopeLocationCommand, SlewCommand, SlewCommandData, AbortCommand, CoordinateTypes
from models.device import DeviceAccess
router = APIRouter()

async def get_device_tunnel(device_id: str, username: str) -> DeviceTunnel:
    """
    Retrieves and validates a device tunnel for a specific user.

    Args:
        device_id (str): The identifier of the device.
        username (str): The username requesting access.

    Returns:
        DeviceTunnel: The active tunnel for the device.

    Raises:
        HTTPException: If the user doesn't have access or the device is offline.
    """
    try:
        service = DeviceService()
        device = await service.get_user_device(device_id, username)
        tunnel = tunnel_manager.get(device_id)
        if not tunnel:
            raise HTTPException(404, detail="Edge is not connected")
        return tunnel
    except ObjectNotFoundError as e:
        raise HTTPException(404, detail=str(e))

@router.post("/pair")
async def pair_device(req: PairingRequest, user_id: str = Depends(get_request_user)):
    """
    Pairs a user with a device using a PIN.

    Args:
        req (PairingRequest): The request containing the PIN.
        user_id (str): The authenticated user ID.

    Returns:
        dict: The device ID if pairing was successful.

    Raises:
        HTTPException: If the PIN is invalid or the device is already paired.
    """
    try:
        device_id = await pairing_manager.pair_device(req.pin, user_id)
        return {"device_id": device_id}
    except ValueError as e:
        raise HTTPException(400, detail=str(e))
    except ObjectAlreadyExistsError as e:
        raise HTTPException(409, detail=str(e))
    
    
@router.websocket("/ws/pair")
async def ws_pair_tunnel(ws: WebSocket, device_id: str):
    """
    WebSocket endpoint for devices to initiate the pairing process.

    Args:
        ws (WebSocket): The incoming connection.
        device_id (str): The device hardware ID.
    """
    await pairing_manager.register(device_id, ws)

@router.websocket("/ws/tunnel/{device_id}")
async def ws_device_tunnel(
    ws: WebSocket,
    device_id: str,
    authorization: str | None = Header(default=None),
):
    """
    WebSocket endpoint for established device tunnels.

    Requires a valid Bearer token previously generated during pairing.

    Args:
        ws (WebSocket): The incoming tunnel connection.
        device_id (str): The device hardware ID.
        authorization (Optional[str]): The Bearer token header.
    """
    if not authorization or not authorization.startswith("Bearer "):
        await ws.close(code=4401)
        return

    token = authorization.removeprefix("Bearer ")
    device_service = DeviceService()

    is_valid = await device_service.validate_tunnel_token(device_id, token)
    
    if not is_valid:
        await ws.close(code=4401)
        return
    
    await ws.accept()
    tunnel = DeviceTunnel(device_id, ws)
    tunnel_manager.register(tunnel)

    try:
        await tunnel.listen()
    finally:
        tunnel_manager.unregister(device_id)


# ── DEVICE MANAGEMENT ────────────────────────────────────────────
class DeviceResponse(BaseModel):
    """Data model for device listing responses."""
    device_id: str
    name: str
    owner: str
    linked: datetime
    is_online: bool

    access_list: list[DeviceAccess] 

    model_config = {"from_attributes": True}

class DeviceComponents(BaseModel):
    """List of INDI components (drivers) available on a device."""
    telescope: list[str] = []
    camera: list[str] = []
    focuser: list[str] = []
    filter_wheel: list[str] = []
    indi: list[str] = []

class DeviceInfoResponse(DeviceResponse):
    """Enriched device data including active components."""
    components: DeviceComponents

class DeviceUpdate(BaseModel):
    """Request model for updating device details."""
    name: str

@router.get("", response_model=List[DeviceResponse], response_model_by_alias=False)
async def list_devices(username: str = Depends(get_request_user)):
    """
    Lists all devices accessible by the authenticated user.

    Args:
        username (str): The authenticated username.

    Returns:
        List[DeviceResponse]: The list of user devices.
    """
    service = DeviceService()
    devices = await service.get_user_devices(username)
    
    # Enrich the response with the is_online flag
    return [
        DeviceResponse(
            **device.model_dump(),
            is_online=tunnel_manager.get(device.device_id) is not None
        )
        for device in devices
    ]

@router.get("/{device_id}", response_model=DeviceInfoResponse, response_model_by_alias=False)
async def get_device_info(
    device_id: str, 
    username: str = Depends(get_request_user)
):
    """
    Retrieves detailed information and active components for a device.

    Args:
        device_id (str): The device ID.
        username (str): The authenticated username.

    Returns:
        DeviceInfoResponse: The detailed device information.

    Raises:
        HTTPException: If the device is not found or communication times out.
    """
    service = DeviceService()
    tunnel = tunnel_manager.get(device_id)
    try:
        info: DeviceResponse = await service.get_user_device(device_id, username)
        if tunnel is not None:
            resp = await tunnel.send_command(GetDevicesCommand(), timeout=10)
            return DeviceInfoResponse(
                **info.model_dump(),
                is_online=True, 
                components=resp.data
            )
        else:
            return DeviceInfoResponse(
                **info.model_dump(),
                is_online=False, 
                components=DeviceComponents()
            )
    except ObjectNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except TimeoutError as e:
        raise HTTPException(504, detail=str(e))

@router.patch("/{device_id}")
async def update_device(
    device_id: str, 
    data: DeviceUpdate, 
    username: str = Depends(get_request_user)
):
    """
    Updates a device's human-readable name.

    Args:
        device_id (str): The device ID.
        data (DeviceUpdate): The update data.
        username (str): The authenticated username.

    Returns:
        dict: Success status.

    Raises:
        HTTPException: If the device is not found.
    """
    service = DeviceService()
    try:
        success = await service.update_device_info(
            device_id, 
            username, 
            **data.model_dump(exclude_unset=True)
        )
        return {"success": success}
    except ObjectNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.delete("/{device_id}", status_code=204)
async def delete_device(
    device_id: str, 
    username: str = Depends(get_request_user)
):
    """
    Unlinks and deletes a device registration.

    Args:
        device_id (str): The device ID.
        username (str): The authenticated username.

    Returns:
        None

    Raises:
        HTTPException: If the device is not found or user is not the owner.
    """
    service = DeviceService()
    try:
        await service.unlink_device(device_id, username)
        return None 
    except ObjectNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    

# ── DEVICE OPERATION ────────────────────────────────────────────
class Coordinates(BaseModel):
    """Equatorial coordinate model."""
    ra: float
    dec: float

class HorizontalCoordinates(BaseModel):
    """Horizontal coordinate model."""
    alt: float
    az: float

class TelescopePosition(BaseModel):
    """Consolidated telescope position model."""
    equatorial_j2000: Coordinates = Field(..., alias="equatorial_j2000")
    equatorial_eod: Coordinates = Field(..., alias="equatorial_eod")
    horizontal: HorizontalCoordinates = Field(..., alias="horizontal")

    class Config:
        populate_by_name = True

@router.get("/{device_id}/telescope/position", response_model=TelescopePosition)
async def get_telescope_position(device_id: str, 
    telescope: str, 
    username: str = Depends(get_request_user)):
    """
    Retrieves the current astronomical position of a telescope.

    Args:
        device_id (str): The Edge device ID.
        telescope (str): The telescope driver name.
        username (str): The authenticated username.

    Returns:
        TelescopePosition: The current coordinates.

    Raises:
        HTTPException: If the command fails or times out.
    """
    tunnel = await get_device_tunnel(device_id, username)
    payload = GetTelescopeLocationCommand(device=telescope)
    try:
        resp = await tunnel.send_command(payload, timeout=10)
        if resp.status == "ERROR":
            raise HTTPException(
                status_code=400, 
                detail=f"Error getting telescope position: {resp.reason}"
            )
        return TelescopePosition.model_validate(resp.data)
    except TimeoutError as e:
        raise HTTPException(504, detail=str(e))
    
@router.post("/{device_id}/telescope/slew", status_code=status.HTTP_204_NO_CONTENT)
async def slew_telescope(device_id: str, 
    telescope: str, 
    params: SlewCommandData,
    username: str = Depends(get_request_user)):
    """
    Commands a telescope to slew to specific coordinates.

    Args:
        device_id (str): The Edge device ID.
        telescope (str): The telescope driver name.
        params (SlewCommandData): Target coordinates and mode.
        username (str): The authenticated username.

    Returns:
        None

    Raises:
        HTTPException: If the command fails, is cancelled, or times out.
    """

    tunnel = await get_device_tunnel(device_id, username)
    payload = SlewCommand(device=telescope, data=params)
    try:
        resp = await tunnel.send_command(payload, timeout=1000) # big timeout for the slew movement
        if resp.status == "ERROR":
            raise HTTPException(
                status_code=400, 
                detail=f"Error slewing telescope: {resp.reason}"
            )
        elif resp.status == "CANCELLED":
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Operation cancelled"
            )
        return None
    except TimeoutError as e:
        raise HTTPException(504, detail=str(e))


@router.post("/{device_id}/telescope/abort", status_code=status.HTTP_204_NO_CONTENT)
async def abort_slew_telescope(device_id: str, 
    telescope: str, 
    username: str = Depends(get_request_user)):
    """
    Aborts all ongoing telescope movements immediately.

    Args:
        device_id (str): The Edge device ID.
        telescope (str): The telescope driver name.
        username (str): The authenticated username.

    Returns:
        None

    Raises:
        HTTPException: If the command fails or times out.
    """

    tunnel = await get_device_tunnel(device_id, username)
    payload = AbortCommand(device=telescope)
    try:
        resp = await tunnel.send_command(payload, timeout=10)
        if resp.status == "ERROR":
            raise HTTPException(
                status_code=400, 
                detail=f"Error aborting telescope slew: {resp.reason}"
            )
        return None
    except TimeoutError as e:
        raise HTTPException(504, detail=str(e))
