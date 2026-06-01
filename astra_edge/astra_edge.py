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
Main entry point for the Astra Edge client.

Handles device identification, pairing with the Astra backend, 
establishing a WebSocket tunnel, and managing local INDI subprocesses.
"""
import asyncio
from datetime import datetime, timezone
import hashlib
import json
import logging
import os
import aiohttp
import argparse
import urllib.parse
from pydantic import TypeAdapter
from api.IndiTaskAPI import IndiTaskAPI
from utils.Clock import Clock
from common.comm_models import WsPairingCode, WsPairedSuccess
from common.INDIModels import GlobalMessage, CommandMessage, ResponseMessage
from dotenv import load_dotenv

logger = logging.getLogger("edge")

TOKEN_STORAGE = "edge_auth.json"

_adapter = TypeAdapter(GlobalMessage)


def get_serial() -> str:
    """
    Generates a unique hardware fingerprint for the device.

    Attempts to read the SoC serial number or machine ID to create a 
    deterministic device identifier.

    Returns:
        str: A unique device ID string (e.g., 'dev-xxxx').

    Raises:
        RuntimeError: If no hardware identifiers are found.
    """
    hw_identifiers = []

    # 1. SoC serial number. Fallback to installation id
    if os.path.exists('/proc/device-tree/serial-number'):
        with open('/proc/device-tree/serial-number', 'rb') as f:
            serial = f.read().decode().strip('\x00').strip()
            if serial:
                hw_identifiers.append(serial)
    elif os.path.exists('/etc/machine-id'):
        with open('/etc/machine-id', 'rb') as f:
            serial = f.read().decode().strip('\x00').strip()
            if serial:
                hw_identifiers.append(serial)
    
    if not hw_identifiers:
        # If we're here, we're officially doomed.
        raise RuntimeError(
            "No hardware serial found. "
            "This device cannot be uniquely identified."
        )

    # 2. Merge the identifiers in a deterministic way
    raw_hw_string = "-".join(hw_identifiers)
    
    unique_fingerprint = hashlib.sha256(raw_hw_string.encode()).hexdigest()[:32]
    
    return f"dev-{unique_fingerprint}"

class EdgeClient:
    """
    Client for managing communication between local INDI devices and the Astra API.

    Handles authentication (pairing), maintaining a persistent WebSocket tunnel,
    and routing commands/events.
    """
    def __init__(self, server: str, indi_api: IndiTaskAPI):
        """
        Initializes the EdgeClient.

        Args:
            server (str): The Astra API server address.
            indi_api (IndiTaskAPI): The local INDI task API instance.
        """
        # Ensure URL has a scheme for urlparse if missing
        if "://" not in server:
            server = f"http://{server}"
        
        parsed = urllib.parse.urlparse(server)
        self.server = f"{parsed.netloc}{parsed.path}".rstrip('/')
        
        self.device_id = get_serial()
        self.token: str | None = None
        self.ws_url: str | None = None
        self.indi_api = indi_api
        self._load()

    # ───────────────────────── Token Storage ───────────────────────────────────────────────────────────
    def _load(self):
        """Loads authentication tokens from local storage."""
        if os.path.exists(TOKEN_STORAGE):
            try:
                data = json.load(open(TOKEN_STORAGE))
                self.token = data.get("token")
                self.ws_url = data.get("ws_url")
            except Exception:
                pass

    def _save(self):
        """Saves authentication tokens to local storage."""
        json.dump({"token": self.token, "ws_url": self.ws_url}, open(TOKEN_STORAGE, "w"))

    def _clear(self):
        """Clears authentication tokens from local storage."""
        self.token = self.ws_url = None
        if os.path.exists(TOKEN_STORAGE):
            os.remove(TOKEN_STORAGE)

    # ───────────────────────── Startup and Pairing ───────────────────────────────────────────────────────────

    async def start(self):
        """
        Starts the client lifecycle: subscribes to events, pairs if needed, 
        and opens the communication tunnel.
        """
        self.indi_api.subscribe(self._on_indi_event)
        if not self.token:
            await self._pairing()
        await self._tunnel()

    async def _pairing(self):
        """
        Initiates the device pairing process via WebSocket.

        Waits for a pairing code to be issued and then for a success message 
        containing the authentication token.
        """
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
                    logger.warning(f"Pairing error: {e} — retrying in 5s")
                    await asyncio.sleep(5)

    async def _tunnel(self):
        """
        Establishes and maintains a persistent WebSocket tunnel to the Astra backend.

        Automatically reconnects on failure and handles token expiration.
        """
        async with aiohttp.ClientSession() as s:
            while True:
                try:
                    headers = {"Authorization": f"Bearer {self.token}"}
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
        Handles an incoming command from the backend.

        Args:
            ws (ClientWebSocketResponse): The active WebSocket connection.
            raw (str): The raw JSON message string.
        """
        try:
            msg = _adapter.validate_json(raw)
        except Exception:
            logger.warning("Malformated message: Ignoring...")
            return

        if not isinstance(msg, CommandMessage):
            return  # Edge shouldn't receive Events nor Responses

        logger.info(f"Command: {msg.payload.action} (req_id={msg.req_id})")

        async def reply_to_backend(response_data: dict):
            """Internal helper to send command responses back to the API."""
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
        Callback triggered when a local INDI event occurs.

        Sends the event data through the WebSocket tunnel to the backend.

        Args:
            pydantic_packet (EventMessage): The event message to send.
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


async def main(args):
    """
    Main application loop.

    Sets up the environment, starts local INDI subprocesses, and 
    initializes the Edge client and API.
    """
    logging.basicConfig(level=logging.INFO)
    
    clock = Clock()
    if args.time:
        try:
            dt = datetime.fromisoformat(args.time)
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
            clock.set_time(dt)
            logging.info(f"Clock set to: {clock.now}")
        except ValueError:
            logging.error("Invalid date format. Use YYYY-MM-DDTHH:MM:SS ISO 8601")

    logging.info(f"Starting with location: {args.location}")

    indi_process = None

    log_file = open("indiserver.log", "a", encoding="utf-8")

    if args.indi_host in ("localhost", "127.0.0.1") and args.drivers:
        comm = ["indiserver", "-p", str(args.indi_port), "-v"] + args.drivers
        logging.info(f"Starting INDI subprocess: {' '.join(comm)}")

        # Subprocess start
        indi_process = await asyncio.create_subprocess_exec(
            *comm,
            stdout=log_file,
            stderr=log_file
        )
        logging.info(f"indiserver started with PID {indi_process.pid}")

        # Wait a second to let indi load
        await asyncio.sleep(1)
    elif args.drivers:
        logging.warning("No local INDI host. INDI subprocess will not start.")


    try:
        indi_api = IndiTaskAPI(
            host=args.indi_host,
            port=args.indi_port,
            location=args.location,
            time=clock
        )

        client = EdgeClient(
            server=args.astra_url,
            indi_api=indi_api
        )

        await indi_api.start_indi_manager()
        await client.start()

    finally:
        if indi_process:
            logging.info("Shutting down...")
            try:
                indi_process.terminate()
                await asyncio.wait_for(indi_process.wait(), timeout=3.0)
                logging.info("indiserver closed!")
            except asyncio.TimeoutError:
                logging.warning("indiserver killed!")
                indi_process.kill()
            finally:
                log_file.close()

def valid_location(coords):
    """
    Validates the provided location coordinates.

    Args:
        coords (list[float]): A list containing [lat, lon].

    Returns:
        tuple[float, float]: Validated (lat, lon) tuple.

    Raises:
        argparse.ArgumentTypeError: If coordinates are out of valid ranges.
    """
    try:
        lat, lon = map(float, coords)
        if not (-90 <= lat <= 90):
            raise argparse.ArgumentTypeError(f"Latitude must be between -90 and 90. Got: {lat}")
        if not (-180 <= lon <= 180):
            raise argparse.ArgumentTypeError(f"Longitude must be between -180 and 180. Got: {lon}")
        return (lat, lon)
    except ValueError:
        raise argparse.ArgumentTypeError("Location must be two numbers (floats).")


if __name__ == "__main__":
    load_dotenv()
    parser = argparse.ArgumentParser(description="Astra Edge CLI Client Runner")
    
    # IndiTaskAPI Parameters
    parser.add_argument("--indi-host", 
                        default=os.getenv("INDI_HOST", "localhost"), 
                        help="Indi server host address")
    
    parser.add_argument("--indi-port", 
                        type=int, 
                        default=int(os.getenv("INDI_PORT", 7624)), 
                        help="Indi server port number")
    
    # Edge Client Parameters
    parser.add_argument("--astra-url",
                        default=os.getenv("ASTRA_URL", "localhost:8000/api"),  
                        help="Astra API URL")
    
    # Location Parameter (receives two floats)
    parser.add_argument("--location", 
                        type=float, 
                        nargs=2, 
                        metavar=('LAT', 'LON'),
                        default=(float(os.getenv("LAT", 0.0)), float(os.getenv("LON", 0.0))),
                        help="Latitude and Longitude (e.g. 40.41 -3.70)")
    
    # Time Parameter
    parser.add_argument("--time", 
                        default=os.getenv("START_TIME", None),
                        help="Initial time ISO format")

    # INDI drivers to be used
    parser.add_argument("--drivers",
                        nargs="*",
                        default=os.getenv("INDI_DRIVERS", "").split(),
                        help="INDI driver list to be used (e.g. indi_celestron_gps indi_asi_ccd)")

    args = parser.parse_args()
    
    try:
        args.location = valid_location(args.location)
    except argparse.ArgumentTypeError as e:
        parser.error(str(e))

    asyncio.run(main(args))
