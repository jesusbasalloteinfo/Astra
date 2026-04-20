import asyncio
from typing import Literal
import contextlib
from datetime import datetime, timezone
from api.IndiManager import IndiManager
from utils.Clock import Clock
from devices.Telescope import Telescope
from utils.CoordinateHandler import CoordinateTypes
from utils.logging import get_logger
from common.INDIModels import *
from api.IndiAPI import IndiAPI

logger = get_logger("IndiTaskAPI")

class IndiTaskAPI(IndiAPI):
    """
    Class with state management and high-level methods to control the INDI devices
    """

    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self, host="localhost", port=7624):
        if self._initialized: return 

        super().__init__(host, port)
        
        self.active_tasks: dict[str, asyncio.Task] = {}
        self.category_locks: dict[str, str] = {}
        
        self._command_handlers = {
            "slew": self._handle_slew_cmd,
            "abort": self._handle_abort_cmd,
        }
        
        self._initialized = True

    
    # ==========================================
    # TASK MANAGER FOR WEB API 
    # ==========================================
    
    async def dispatch(self, cmd_msg, reply_callback):
        """Parse the received command and handle tasks and exclusivity lanes"""

        req_id = cmd_msg.req_id
        action = cmd_msg.payload.action
        lane = getattr(cmd_msg.payload, "lane", None)
        device = getattr(cmd_msg.payload, "device", None)

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


    async def _execute_with_safety_net(self, req_id, action, handler_func, payload, reply_callback):
        """Generic wrapper to handle exceptions"""
        try:
            await handler_func(payload)
            await reply_callback({"req_id": req_id, "type": "response", "status": "ok"})
            
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

    async def _handle_slew_cmd(self, payload):
        """Traduce un SlewCommand a tu método slew_telescope."""
        await self.slew_telescope(
            telescope_name=payload.device, 
            coord=payload.data.coord, 
            input_type=payload.data.input_type,
            mode=payload.data.mode
        )

    async def _handle_abort_cmd(self, payload):
        """Traduce un AbortCommand a tu método abort_slew_telescope."""
        await self.abort_slew_telescope(telescope_name=payload.device)
