from datetime import datetime
from typing import List, Literal

from pydantic import BaseModel, Field
import uvicorn
from fastapi import APIRouter, Depends, WebSocket, HTTPException, Header
from services.db import DeviceService
from core.db_exceptions import ObjectAlreadyExistsError, ObjectNotFoundError
from core.dependencies import get_request_user
from models.pairing import PairingRequest
from services.device_tunnel.pairing_manager import pairing_manager
from services.device_tunnel.tunnel import DeviceTunnel, tunnel_manager
from models.device_messages import GetDevicesCommand, GetTelescopeLocationCommand, SlewCommand, SlewCommandData, AbortCommand, CoordinateTypes
from models.device import DeviceAccess
router = APIRouter()


@router.post("/pair")
async def pair_device(req: PairingRequest, user_id: str = Depends(get_request_user)):
    try:
        device_id = await pairing_manager.pair_device(req.pin, user_id)
        return {"device_id": device_id}
    except ValueError as e:
        raise HTTPException(400, detail=str(e))
    except ObjectAlreadyExistsError as e:
        raise HTTPException(409, detail=str(e))
    
    
@router.websocket("/ws/pair")
async def ws_pair_tunnel(ws: WebSocket, device_id: str):
    await pairing_manager.register(device_id, ws)

@router.websocket("/ws/tunnel/{device_id}")
async def ws_device_tunnel(
    ws: WebSocket,
    device_id: str,
    authorization: str | None = Header(default=None),
):
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
    device_id: str
    name: str
    owner: str
    linked: datetime
    is_online:bool

    access_list: list[DeviceAccess] 

    model_config = {"from_attributes": True}

class DeviceComponents(BaseModel):
    telescope: list[str] = []
    camera: list[str] = []
    focuser: list[str] = []
    filter_wheel: list[str] = []
    indi: list[str] = []

class DeviceInfoResponse(DeviceResponse):
    components: DeviceComponents

class DeviceUpdate(BaseModel):
    name: str

@router.get("", response_model=List[DeviceResponse], response_model_by_alias=False)
async def list_devices(username: str = Depends(get_request_user)):
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
    service = DeviceService()
    try:
        await service.unlink_device(device_id, username)
        return None 
    except ObjectNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    

# ── DEVICE OPERATION ────────────────────────────────────────────
class Coordinates(BaseModel):
    ra: float
    dec: float

class HorizontalCoordinates(BaseModel):
    alt: float
    az: float

class TelescopePosition(BaseModel):
    equatorial_j2000: Coordinates = Field(..., alias="equatorial_j2000")
    equatorial_eod: Coordinates = Field(..., alias="equatorial_eod")
    horizontal: HorizontalCoordinates = Field(..., alias="horizontal")

    class Config:
        populate_by_name = True

@router.get("/{device_id}/telescope/position", response_model=TelescopePosition)
async def get_telescope_position(device_id: str, 
    telescope: str, 
    username: str = Depends(get_request_user)):
    """Get the current position of a telescope from the device"""
    try:
        service = DeviceService()
        device = await service.get_user_device(device_id, username)
        tunnel = tunnel_manager.get(device_id)
        if not tunnel:
            raise HTTPException(404, detail="Edge is not connected")
    except ObjectNotFoundError as e:
        raise HTTPException(404, detail=str(e))
    payload = GetTelescopeLocationCommand(device=telescope)
    try:
        resp = await tunnel.send_command(payload, timeout=1000)
        if resp.status == "ERROR":
            raise HTTPException(
                status_code=400, 
                detail=f"Error getting telescope position: {resp.reason}"
            )
        return TelescopePosition.model_validate(resp.data)
    except TimeoutError as e:
        raise HTTPException(504, detail=str(e))

# ── TESTING ENDPOINTS ────────────────────────────────────────────
@router.post("/test/get/{device_id}")
async def test_get_devices(device_id: str):
    tunnel = tunnel_manager.get(device_id)
    if not tunnel:
        raise HTTPException(404, detail="Edge is not connected")
    
    payload = GetDevicesCommand()
    try:
        resp = await tunnel.send_command(payload, timeout=1000)
        return {"status": resp.status, "data": resp.data}
    except TimeoutError as e:
        raise HTTPException(504, detail=str(e))
    
@router.post("/test/slew/{device_id}")
async def test_slew(device_id: str, device_name:str, params: SlewCommandData):
    tunnel = tunnel_manager.get(device_id)
    if not tunnel:
        raise HTTPException(404, detail="Edge is not connected")
    
    payload = SlewCommand(
        device=device_name,
        data=params
    )
    try:
        resp = await tunnel.send_command(payload, timeout=1000)
        return {"status": resp.status, "data": resp.data}
    except TimeoutError as e:
        raise HTTPException(504, detail=str(e))
    

@router.post("/test/slew_horizontal/{device_id}")
async def test_slew_horizontal(device_id: str, device_name:str, alt: float, az: float):
    tunnel = tunnel_manager.get(device_id)
    if not tunnel:
        raise HTTPException(404, detail="Edge is not connected")
    
    payload = SlewCommand(
        device=device_name,
        data=SlewCommandData(coord=(alt, az), input_type=CoordinateTypes.HORIZONTAL)
    )
    try:
        resp = await tunnel.send_command(payload, timeout=1000)
        return {"status": resp.status, "data": resp.data}
    except TimeoutError as e:
        raise HTTPException(504, detail=str(e))

@router.post("/test/abort/{device_id}")
async def test_abort(device_id: str, telescope:str):
    tunnel = tunnel_manager.get(device_id)
    if not tunnel:
        raise HTTPException(404, detail="Edge is not connected")
    
    payload = AbortCommand(device=telescope)
    try:
        resp = await tunnel.send_command(payload)
        return {"status": resp.status}
    except TimeoutError as e:
        raise HTTPException(504, detail=str(e))