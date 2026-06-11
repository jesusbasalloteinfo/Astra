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
Manager for the device pairing process via WebSockets.
"""
import asyncio
import random
import string
from fastapi import WebSocket, WebSocketDisconnect
from models.pairing import WsPairingCode, WsPairedSuccess
from services.db import DeviceService
from core.logging_utils import get_logger, setup_global_logging

device_service = DeviceService()

class PairingManager:
    """
    Manages the lifecycle of device pairing requests.

    Handles PIN generation, temporary WebSocket connections for devices awaiting
    pairing, and notifying devices when a user successfully pairs with them.
    """
    def __init__(self):
        """Initializes the PairingManager."""
        self._pin_to_device: dict[str, str] = {}
        self._device_to_pin: dict[str, str] = {}
        self._pending_ws: dict[str, WebSocket] = {}

    def _new_pin(self) -> str:
        """
        Generates a new unique 8-character connection PIN.

        Returns:
            str: The generated PIN.
        """
        while True:
            pin = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
            
            if pin not in self._pin_to_device:
                return pin
            
    def _cleanup(self, device_id: str):
        """
        Removes temporary pairing information for a device.

        Args:
            device_id (str): The identifier of the device.
        """
        pin = self._device_to_pin.pop(device_id, None)
        if pin:
            self._pin_to_device.pop(pin, None)
        self._pending_ws.pop(device_id, None)

    async def register(self, device_id: str, ws: WebSocket):
        """
        Registers a new device awaiting pairing.

        Accepts the WebSocket connection, generates a PIN, and waits for a pairing
        confirmation.

        Args:
            device_id (str): The identifier of the device.
            ws (WebSocket): The active WebSocket connection.
        """
        await ws.accept()

        # Check if we already have a pin for this device to reuse it
        pin = self._device_to_pin.get(device_id)
        
        # Remove older pending pair requests (but don't cleanup the PIN yet if we found one)
        old_ws = self._pending_ws.get(device_id)
        if old_ws:
            try:
                await old_ws.close(code=4000)
            except Exception:
                pass
        
        if not pin:
            pin = self._new_pin()
            self._pin_to_device[pin] = device_id
            self._device_to_pin[device_id] = pin
        
        self._pending_ws[device_id] = ws
        
        await ws.send_text(WsPairingCode(code=pin).model_dump_json())

        try:
            while True:
                await ws.receive_text()  # keep alive
        except WebSocketDisconnect:
            # We don't cleanup here to allow the PIN to survive intermittent reconnections.
            # The PIN is removed when pair_device succeeds.
            pass

    async def pair_device(self, pin: str, user_id: str) -> str:
        """
        Processes a user's request to pair with a device using a PIN.

        Args:
            pin (str): The PIN provided by the user.
            user_id (str): The ID of the user performing the pairing.

        Returns:
            str: The device ID that was paired.

        Raises:
            ValueError: If the PIN is invalid or expired.
        """
        LOG = get_logger("PAIR")
        pin = pin.upper()
        
        LOG.debug("Pairing attempt", {"pin": pin, "user": user_id})
        print(f"[PAIR] Attempting to pair PIN {pin} for user {user_id}")
        
        device_id = self._pin_to_device.get(pin)
        if not device_id:
            print(f"[PAIR] PIN {pin} not found in memory. Current pins: {list(self._pin_to_device.keys())}")
            raise ValueError("Invalid pin")

        # Create a new device token FIRST
        try:
            token = await device_service.link_device(device_id, user_id)
        except Exception as e:
            print(f"[PAIR] link_device failed for {device_id}: {e}")
            raise e

        # Now we can cleanup
        ws = self._pending_ws.get(device_id)
        self._cleanup(device_id)
        
        ws_url = f"/devices/ws/tunnel/{device_id}"

        # Send the device token
        if ws:
            print(f"[PAIR] Notifying device {device_id} of success via WebSocket")
            asyncio.create_task(
                self._notify_pair(ws, token, ws_url)
            )
        else:
            print(f"[PAIR] Device {device_id} has no active pairing WebSocket")

        return device_id

    async def _notify_pair(self, ws: WebSocket, token: str, ws_url: str):
        """
        Sends the newly assigned device token to the edge device.

        Args:
            ws (WebSocket): The device's pairing WebSocket.
            token (str): The generated access token.
            ws_url (str): The WebSocket tunnel URL for the device.
        """
        try:
            msg = WsPairedSuccess(token=token, ws_url=ws_url)
            await ws.send_text(msg.model_dump_json())
            await ws.close()
        except Exception:
            pass  

pairing_manager  = PairingManager()
