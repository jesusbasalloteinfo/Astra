import uvicorn
from fastapi import APIRouter, Depends, WebSocket, HTTPException, Header
from services.db import DeviceService
from core.db_exceptions import ObjectAlreadyExistsError
from core.dependencies import get_request_user
from models.pairing import PairingRequest
from services.device_tunnel.pairing_manager import pairing_manager
from services.device_tunnel.tunnel import DeviceTunnel, tunnel_manager
from models.device_messages import GetDevicesCommand, SlewCommand, SlewCommandData, AbortCommand, CoordinateTypes

device_service = DeviceService()
router = APIRouter()

@router.websocket("/ws/pair")
async def ws_pair_tunnel(ws: WebSocket, device_id: str):
    await pairing_manager.register(device_id, ws)


@router.post("/pair")
async def pair_device(req: PairingRequest, user_id: str = Depends(get_request_user)):
    try:
        device_id = await pairing_manager.pair_device(req.pin, user_id)
        return {"device_id": device_id}
    except ValueError as e:
        raise HTTPException(400, detail=str(e))
    except ObjectAlreadyExistsError as e:
        raise HTTPException(409, detail=str(e))

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