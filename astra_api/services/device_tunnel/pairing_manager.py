import asyncio
import random
import string
from fastapi import WebSocket, WebSocketDisconnect
from models.pairing import WsPairingCode, WsPairedSuccess
from services.db import DeviceService
device_service = DeviceService()

class PairingManager:
    def __init__(self):
        self._pin_to_device: dict[str, str] = {}
        self._device_to_pin: dict[str, str] = {}
        self._pending_ws: dict[str, WebSocket] = {}

    def _new_pin(self) -> str:
        """
        Generate a new connection pin
        """
        return ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))

    def _cleanup(self, device_id: str):
        """
        Remove the temporaly info of a device
        """
        pin = self._device_to_pin.pop(device_id, None)
        if pin:
            self._pin_to_device.pop(pin, None)
        self._pending_ws.pop(device_id, None)

    async def register(self, device_id: str, ws: WebSocket):
        """
        Register a new pending pair request
        """
        await ws.accept()
        # Remove older pending pair requests
        old_ws = self._pending_ws.get(device_id)
        if old_ws:
            self._cleanup(device_id)
            try:
                await old_ws.close(code=4000)
            except Exception:
                pass

        pin = self._new_pin()
        self._pin_to_device[pin] = device_id
        self._device_to_pin[device_id] = pin
        self._pending_ws[device_id] = ws

        await ws.send_text(WsPairingCode(code=pin).model_dump_json())

        try:
            while True:
                await ws.receive_text()  # keep alive
        except WebSocketDisconnect:
            self._cleanup(device_id)

    async def pair_device(self, pin: str, user_id: str) -> str:
        """
        Pairs a new device
        """
        device_id = self._pin_to_device.get(pin)
        if not device_id:
            raise ValueError("Invalid pin")

        # After validating pin, remove the request keeping the ws connection
        ws = self._pending_ws.get(device_id)
        self._cleanup(device_id)

        # Create a new device token
        token = await device_service.link_device(device_id, user_id)
        ws_url = f"/devices/ws/tunnel/{device_id}"

        # Send the device token
        if ws:
            asyncio.create_task(
                self._notify_pair(ws, token, ws_url)
            )

        return device_id

    async def _notify_pair(self, ws: WebSocket, token: str, ws_url: str):
        """
        Sends the newly assigned device token to the edge device
        """
        try:
            msg = WsPairedSuccess(token=token, ws_url=ws_url)
            await ws.send_text(msg.model_dump_json())
            await ws.close()
        except Exception:
            pass  

pairing_manager  = PairingManager()
