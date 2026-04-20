import asyncio
import json
import logging
import os
import aiohttp
from pydantic import TypeAdapter
from api.IndiTaskAPI import IndiTaskAPI
from common.comm_models import WsPairingCode, WsPairedSuccess
from common.INDIModels import GlobalMessage, CommandMessage, ResponseMessage, EventMessage

logger = logging.getLogger("edge")

TOKEN_STORAGE = "edge_auth.json"

_adapter = TypeAdapter(GlobalMessage)

def get_serial() -> str:
    for path in ('/proc/device-tree/serial-number', '/etc/machine-id'):
        if os.path.exists(path):
            with open(path, 'rb') as f:
                return f.read().decode().strip('\x00').strip()
    return "dev-local"




class EdgeClient:
    def __init__(self, server: str, indi_api: IndiTaskAPI):
        self.server = server.rstrip('/')
        self.device_id = get_serial()
        self.token: str | None = None
        self.ws_url: str | None = None
        self.indi_api = indi_api
        self._load()

    # ───────────────────────── Token Storage ───────────────────────────────────────────────────────────
    def _load(self):
        if os.path.exists(TOKEN_STORAGE):
            try:
                data = json.load(open(TOKEN_STORAGE))
                self.token = data.get("token")
                self.ws_url = data.get("ws_url")
            except Exception:
                pass

    def _save(self):
        json.dump({"token": self.token, "ws_url": self.ws_url}, open(TOKEN_STORAGE, "w"))

    def _clear(self):
        self.token = self.ws_url = None
        if os.path.exists(TOKEN_STORAGE):
            os.remove(TOKEN_STORAGE)

    # ───────────────────────── Startup and Pairing ───────────────────────────────────────────────────────────

    async def start(self):
        self.indi_api.subscribe(self._on_indi_event)
        if not self.token:
            await self._pairing()
        await self._tunnel()

    async def _pairing(self):
        url = f"ws://{self.server}/devices/ws/pair?device_id={self.device_id}"
        async with aiohttp.ClientSession() as s:
            while not self.token:
                try:
                    async with s.ws_connect(url) as ws:
                        async for msg in ws:
                            if msg.type != aiohttp.WSMsgType.TEXT:
                                break
                            data = json.loads(msg.data)
                            t = data.get("type")
                            if t == "PAIRING_CODE":
                                m = WsPairingCode.model_validate(data)
                                logger.info(f"Pairing PIN: {m.code}")
                            elif t == "PAIRED_SUCCESS":
                                m = WsPairedSuccess.model_validate(data)
                                self.token = m.token
                                self.ws_url = f"ws://{self.server}{m.ws_url}"
                                self._save()
                                logger.info("Paired ✓")
                                break
                except Exception as e:
                    logger.warning(f"Pairing error: {e} — retrying en 5s")
                    await asyncio.sleep(5)

    async def _tunnel(self):
        """
        Create a WS tunnel to the backend and handle all communications
        """
        headers = {"Authorization": f"Bearer {self.token}"}
        async with aiohttp.ClientSession() as s:
            while True:
                try:
                    async with s.ws_connect(self.ws_url, headers=headers) as ws:
                        logger.info("Tunnel established!")
                        self._active_ws = ws

                        async for msg in ws:
                            if msg.type == aiohttp.WSMsgType.TEXT:
                                await self._handle(ws, msg.data)
                            elif msg.type in (aiohttp.WSMsgType.CLOSED, aiohttp.WSMsgType.ERROR):
                                break
                        self._active_ws = None 
                except aiohttp.WSServerHandshakeError as e:
                    if e.status in (4401, 401, 403):
                        logger.error("Invalid token — trying to pair")
                        self._clear()
                        await self._pairing()
                    else:
                        await asyncio.sleep(5)
                except Exception as e:
                    logger.warning(f"Tunnel connection lost: {e} — retrying in 5s")
                    await asyncio.sleep(5)


    # ───────────────────────── Command and Event handling ───────────────────────────────────────────────────────────
    async def _handle(self, ws, raw: str):
        """
        Handles a backend sent message and queues to IndiTask API
        """
        # TODO: Should we send an error message acknowledging the error?
        try:
            msg = _adapter.validate_json(raw)
        except Exception:
            logger.warning("Malformated message: Ignoring...")
            return

        if not isinstance(msg, CommandMessage):
            return  # Edge shouldn't receive Events nor Responses

        logger.info(f"Command: {msg.payload.action} (req_id={msg.req_id})")

        async def reply_to_backend(response_data: dict):
            try:
                status_map = {"ok": "OK", "error": "ERROR", "cancelled": "CANCELLED"}
                
                resp = ResponseMessage(
                    req_id=response_data["req_id"],
                    status=status_map.get(response_data.get("status", "error"), "ERROR"),
                    reason=response_data.get("reason"),
                    data=response_data.get("data")
                )
                await ws.send_str(resp.model_dump_json())
            except Exception as e:
                logger.error(f"Error sending response to backend: {e}")

        try:
            await self.indi_api.dispatch(msg, reply_to_backend)
        except Exception as e:
            logger.error(f"Error dispatching command: {e}")
            fallback_resp = ResponseMessage(req_id=msg.req_id, status="ERROR", reason=str(e))
            await ws.send_str(fallback_resp.model_dump_json())


    async def _on_indi_event(self, pydantic_packet):
        """
        Callback: Sends an event message to the backend when and event has happened
        """
        if not self.ws_url:
            # No tunel, so no event
            return

        try:
            if hasattr(self, '_active_ws') and self._active_ws and not self._active_ws.closed:
                
                # Convert to json and send!
                await self._active_ws.send_str(pydantic_packet.model_dump_json())
                
                logger.debug(f"Event sent to backend: {pydantic_packet.payload.event_type}")
                
        except Exception as e:
            logger.error(f"Error sending event to backend: {e}")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    indi_api = IndiTaskAPI(host="localhost", port=7624)
    
    client = EdgeClient("localhost:8000/api", indi_api=indi_api)
    
    async def main():
        await indi_api.start_indi_manager()
        
        await client.start()

    asyncio.run(main())
