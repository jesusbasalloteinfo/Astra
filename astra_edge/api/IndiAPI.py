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

logger = get_logger("IndiAPI")

class IndiAPI:
    """
    Class with state management and high-level methods to control the INDI devices
    """

    def __init__(self, host="localhost", port=7624, location:tuple[float, float]=(0,0), time:Clock=Clock()):
        
        self._observers = []

        self._manager = IndiManager(
            host=host, 
            port=port,
            context_provider=self._get_context_logic,
            event_callback=self._notify_observers
        )
        self._location:tuple[float, float]=location
        self._time:Clock=time


    def _get_context_logic(self) -> tuple[tuple, callable]:
        return self._location, self._time.now

    async def _notify_observers(self, pydantic_packet):
        """Updates a new event to all observers"""
        for callback in self._observers:
            await callback(pydantic_packet)

    def subscribe(self, callback):
        """Allows to subscribe a component to the events"""
        self._observers.append(callback)

    def unsubscribe(self, callback):
        """Allows to unsubscribe a component from the events"""
        if callback in self._observers:
            self._observers.remove(callback)

    async def start_indi_manager(self):
        "Starts the INDI manager"
        await self._manager.start()
        await asyncio.sleep(2) # Initial handshake
        await self._manager.get_devices()
    
    async def stop_indi_manager(self):
        "Stops the INDI manager"
        await self._manager.stop()

    # ==========================================
    # Device and API logic
    # ==========================================

    async def _connect_telescope(self, telescope_name:str) -> Telescope:
        """ Auxiliar method to get and connect a telescope """
        telescope = await self._manager.connect_device(telescope_name)
        if not isinstance(telescope, Telescope):
            raise ValueError(f"Device {telescope_name} is not a Telescope.")
        return telescope

    async def disconnect_device(self, device_name:str):
        await self._manager.disconnect_device(device_name)
    
    async def get_devices(self) -> dict:
        """Get the managed devices"""
        return await self._manager.get_devices()

    async def position_telescope(self, telescope_name:str) -> dict:
        telescope=await self._connect_telescope(telescope_name)
        return telescope.get_position(self._location, self._time.now)
    
    async def slew_telescope(self, telescope_name:str, 
                             coord:tuple[float, float],
                             input_type:CoordinateTypes=CoordinateTypes.EQUATORIAL_J2000,
                             mode:Literal["SLEW", "TRACK", "SYNC"]="TRACK"):
        telescope=await self._connect_telescope(telescope_name)
        await telescope.slew(input_type, mode, coord, self._location, self._time.now)
        
        while telescope.is_slewing():
            await asyncio.sleep(0.2)

    async def abort_slew_telescope(self, telescope_name:str):
        telescope=await self._connect_telescope(telescope_name)
        await telescope.abort_motion()

    def update_location(self, lat: float, lon: float):
        """Update location and notify observers"""
        self._location = (lat, lon)
    
    def update_time(self, new_time: datetime):
        """Update time and notify observers"""
        self._time.set_time(new_time)
        
    