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
Singleton API layer for managing INDI tasks with concurrency control.
"""
import asyncio
import contextlib
from api.IndiAPI import IndiAPI
from utils.Clock import Clock
from utils.logging import get_logger
from common.INDIModels import GetTelescopeLocationCommand

logger = get_logger("IndiTaskAPI")

class IndiTaskAPI(IndiAPI):
    """
    Singleton class that manages asynchronous INDI tasks and command dispatching.

    Extends IndiAPI to provide task queuing, exclusivity lanes (preemption),
    and high-level command handling for remote requests.
    """

    _instance = None

    def __new__(cls, *args, **kwargs):
        """
        Ensures only one instance of IndiTaskAPI exists (Singleton pattern).
        """
        if not cls._instance:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self, host="localhost", port=7624, location: tuple[float, float] = (0, 0), time: Clock = Clock()):
        """
        Initializes the IndiTaskAPI instance.

        Args:
            host (str): INDI server hostname.
            port (int): INDI server port.
            location (tuple[float, float]): Observer location [lat, lon].
            time (Clock): Clock instance for time synchronization.
        """
        if self._initialized: return 

        super().__init__(host, port, location, time)
        
        self.active_tasks: dict[str, asyncio.Task] = {}
        self.category_locks: dict[str, str] = {}
        
        self._command_handlers = {
            "slew": self._handle_slew_cmd,
            "abort": self._handle_abort_cmd,
            "get_devices": self._handle_get_devices,
            "telescope_location": self._handle_telescope_location,
        }
        
        self._initialized = True

    
    # ==========================================
    # TASK MANAGER FOR WEB API 
    # ==========================================
    
    async def dispatch(self, cmd_msg, reply_callback: callable):
        """
        Parses a received command message and dispatches it to the appropriate handler.

        Manages task lanes to ensure that conflicting commands (e.g., two slews 
        on the same device) preempt each other.

        Args:
            cmd_msg (CommandMessage): The incoming command message.
            reply_callback (callable): Async callback to send responses back to the requester.
        """

        req_id = cmd_msg.req_id
        action = cmd_msg.payload.action
        lane = getattr(cmd_msg.payload, "lane", None)

        # LANE MANAGEMENT
        if lane:
            current = self.category_locks.get(lane)
            if current and current in self.active_tasks:
                # Some task has the same type, so we'll use Preemption to take over
                old_task = self.active_tasks[current]
                logger.debug(f"Collision detected on lane '{lane}'. Cancelling last task...")
                old_task.cancel()
                with contextlib.suppress(asyncio.CancelledError):
                    await old_task 
            self.category_locks[lane] = req_id

        handler_func = self._command_handlers.get(action)
        if not handler_func:
            logger.error(f"Unknown command: {action}")
            # TODO: Send an error by reply_callback
            return

        task = asyncio.create_task(
            self._execute_with_safety_net(req_id, action, handler_func, cmd_msg.payload, reply_callback)
        )
        self.active_tasks[req_id] = task
        
        def cleanup(t):
            self.active_tasks.pop(req_id, None)
            if lane and self.category_locks.get(lane) == req_id:
                self.category_locks.pop(lane, None)

        task.add_done_callback(cleanup)


    async def _execute_with_safety_net(self, req_id: str, action: str, handler_func: callable, payload, reply_callback: callable):
        """
        Executes a command handler with standardized error handling and status reporting.

        Args:
            req_id (str): The request ID.
            action (str): The action name.
            handler_func (callable): The handler function to execute.
            payload: The command payload.
            reply_callback (callable): The response callback.
        """
        try:
            result = await handler_func(payload)
            response = {"req_id": req_id, "type": "response", "status": "ok"}
            if result: 
                response["data"] = result
            await reply_callback(response)
            
        except asyncio.CancelledError:
            logger.warning(f"Command '{action}' has been cancelled")
            await reply_callback({"req_id": req_id, "type": "response", "status": "cancelled"})
            raise
        except Exception as e:
            logger.error(f"Error executing command '{action}': {e}")
            await reply_callback({"req_id": req_id, "type": "response", "status": "error", "reason": str(e)})

    # ==========================================
    # API NET TRANSLATORS (Async dispatch to API)
    # Extract pydantic data and use it
    # ==========================================

    async def _handle_get_devices(self, payload):
        """
        Handles a 'get_devices' command.

        Args:
            payload (GetDevicesCommand): The command payload.

        Returns:
            dict: The list of connected devices grouped by type.
        """
        return await self.get_devices()
    
    async def _handle_telescope_location(self, payload: GetTelescopeLocationCommand):
        """
        Handles a 'telescope_location' command.

        Args:
            payload (GetTelescopeLocationCommand): The command payload.

        Returns:
            dict: The current position data for the telescope.
        """
        return await self.position_telescope(telescope_name=payload.device)

    async def _handle_slew_cmd(self, payload):
        """
        Handles a 'slew' command.

        Args:
            payload (SlewCommand): The command payload.
        """
        await self.slew_telescope(
            telescope_name=payload.device, 
            coord=payload.data.coord, 
            input_type=payload.data.input_type,
            mode=payload.data.mode
        )

    async def _handle_abort_cmd(self, payload):
        """
        Handles an 'abort' command.

        Args:
            payload (AbortCommand): The command payload.
        """
        await self.abort_slew_telescope(telescope_name=payload.device)
