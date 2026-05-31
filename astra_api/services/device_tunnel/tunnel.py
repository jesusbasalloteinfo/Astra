"""
Manager for WebSocket tunnels between the Astra API and Edge devices.
"""
import asyncio
import uuid
from typing import Callable, Awaitable
from fastapi import WebSocket, WebSocketDisconnect
from pydantic import TypeAdapter

from models.device_messages import (
    GlobalMessage, CommandMessage, ResponseMessage,
    EventMessage, CommandPayloadUnion, EventListener
)


_adapter = TypeAdapter(GlobalMessage)

EventListener = Callable[[EventMessage], Awaitable[None]]


class DeviceTunnel:
    """
    Represents an active WebSocket connection to an Edge device.

    Handles message dispatching, command transmission with response tracking,
    and event notification for registered listeners.
    """
    def __init__(self, device_id: str, ws: WebSocket):
        """
        Initializes the DeviceTunnel.

        Args:
            device_id (str): The identifier of the Edge device.
            ws (WebSocket): The active WebSocket connection.
        """
        self.device_id = device_id
        self._ws = ws
        self._pending: dict[str, asyncio.Future[ResponseMessage]] = {}
        self.listeners: list[EventListener] = []

    async def listen(self):
        """
        Main tunnel loop that asynchronously receives and dispatches device messages.
        """
        try:
            while True:
                raw = await self._ws.receive_text()
                await self._dispatch(raw)
        except (WebSocketDisconnect, Exception):
            # Cancel all pending tasks
            for fut in self._pending.values():
                if not fut.done():
                    fut.cancel()

    async def _dispatch(self, raw: str):
        """
        Parses and routes an incoming message from the device.

        Args:
            raw (str): The raw JSON message string.
        """
        try:
            # Check if is a valid response
            msg = _adapter.validate_json(raw)
        except Exception:
            return  # Malformed message, ignore
        
        if isinstance(msg, ResponseMessage):
            # Resolve the pending task with the response
            fut = self._pending.pop(msg.req_id, None)
            if fut and not fut.done():
                fut.set_result(msg)

        elif isinstance(msg, EventMessage):
            # Device event, we'll send to frontend
            
            print(f"[EDGE-EVENT] {msg.payload.device}: {msg.payload.event_type}")
            print(f"             Data: {msg.payload.data}")
            
            for listener in self.listeners:
                asyncio.create_task(listener(msg))


    async def send_command(self, payload: CommandPayloadUnion, timeout: float = 10.0) -> ResponseMessage:
        """
        Sends a command to the Edge device and waits for a response.

        Args:
            payload (CommandPayloadUnion): The command to send.
            timeout (float): Max seconds to wait for a response.

        Returns:
            ResponseMessage: The response from the device.

        Raises:
            TimeoutError: If the device does not respond within the timeout period.
        """
        req_id = str(uuid.uuid4())
        msg = CommandMessage(req_id=req_id, payload=payload)

        # Create the future to wait the edge response
        future: asyncio.Future[ResponseMessage] = asyncio.get_event_loop().create_future()
        self._pending[req_id] = future
        await self._ws.send_text(msg.model_dump_json())

        # Await the task sent
        try:
            return await asyncio.wait_for(future, timeout=timeout)
        except asyncio.TimeoutError:
            self._pending.pop(req_id, None)
            raise TimeoutError(f"No response in {timeout}s")


class TunnelManager:
    """
    Central manager for all active Edge device tunnels.
    """
    def __init__(self):
        """Initializes the TunnelManager."""
        self._tunnels: dict[str, DeviceTunnel] = {}

    def register(self, tunnel: DeviceTunnel):
        """
        Registers a new tunnel and inherits listeners from previous connections if any.

        Args:
            tunnel (DeviceTunnel): The tunnel instance to register.
        """
        old = self._tunnels.get(tunnel.device_id)
        if old:
            tunnel.listeners = old.listeners  # inherit listeners from frontend
        self._tunnels[tunnel.device_id] = tunnel

    def unregister(self, device_id: str):
        """
        Removes a tunnel registration.

        Args:
            device_id (str): The device identifier.
        """
        self._tunnels.pop(device_id, None)

    def get(self, device_id: str) -> DeviceTunnel | None:
        """
        Retrieves an active tunnel by device ID.

        Args:
            device_id (str): The device identifier.

        Returns:
            Optional[DeviceTunnel]: The tunnel instance if active, None otherwise.
        """
        return self._tunnels.get(device_id)
    
tunnel_manager  = TunnelManager()
