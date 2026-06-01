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
High-level API for controlling INDI devices with state management.
"""
import asyncio
from typing import Literal
from datetime import datetime
from api.IndiManager import IndiManager
from utils.Clock import Clock
from devices.Telescope import Telescope
from utils.CoordinateHandler import CoordinateTypes
from utils.logging import get_logger
from common.INDIModels import *

logger = get_logger("IndiAPI")

class IndiAPI:
    """
    Class with state management and high-level methods to control INDI devices.

    Provides a clean interface for UI or other services to interact with 
    astronomical hardware, handling connection persistence and event observation.
    """

    def __init__(self, host="localhost", port=7624, location: tuple[float, float] = (0, 0), time: Clock = Clock()):
        """
        Initializes the IndiAPI.

        Args:
            host (str): INDI server hostname.
            port (int): INDI server port.
            location (tuple[float, float]): Observer location [lat, lon].
            time (Clock): Clock instance for time synchronization.
        """
        self._observers = []

        self._manager = IndiManager(
            host=host, 
            port=port,
            context_provider=self._get_context_logic,
            event_callback=self._notify_observers
        )
        self._location: tuple[float, float] = location
        self._time: Clock = time


    def _get_context_logic(self) -> tuple[tuple, callable]:
        """
        Internal callback to provide current location and time to the manager.

        Returns:
            tuple[tuple, callable]: A tuple containing (location_tuple, time_now_callable).
        """
        return self._location, self._time.now

    async def _notify_observers(self, pydantic_packet):
        """
        Propagates events from the INDI manager to all registered observers.

        Args:
            pydantic_packet: The event message packet.
        """
        for callback in self._observers:
            await callback(pydantic_packet)

    def subscribe(self, callback: callable):
        """
        Registers a component to receive INDI events.

        Args:
            callback (callable): The async function to call on new events.
        """
        self._observers.append(callback)

    def unsubscribe(self, callback: callable):
        """
        Unregisters a component from events.

        Args:
            callback (callable): The previously registered callback.
        """
        if callback in self._observers:
            self._observers.remove(callback)

    async def start_indi_manager(self):
        """
        Starts the INDI manager and performs an initial device handshake.
        """
        await self._manager.start()
        await asyncio.sleep(2) # Initial handshake
        await self._manager.get_devices()
    
    async def stop_indi_manager(self):
        """
        Stops the INDI manager and releases resources.
        """
        await self._manager.stop()

    # ==========================================
    # Device and API logic
    # ==========================================

    async def _connect_telescope(self, telescope_name: str) -> Telescope:
        """
        Helper method to get and connect a telescope device proxy.

        Args:
            telescope_name (str): The name of the telescope.

        Returns:
            Telescope: The connected telescope proxy.

        Raises:
            ValueError: If the device is not found or is not a telescope.
        """
        telescope = await self._manager.connect_device(telescope_name)
        if not isinstance(telescope, Telescope):
            raise ValueError(f"Device {telescope_name} is not a Telescope.")
        return telescope

    async def disconnect_device(self, device_name: str):
        """
        Disconnects a device from the INDI server.

        Args:
            device_name (str): The name of the device.
        """
        await self._manager.disconnect_device(device_name)
    
    async def get_devices(self) -> dict:
        """
        Retrieves the list of managed devices grouped by type.

        Returns:
            dict: The device dictionary.
        """
        return await self._manager.get_devices()

    async def position_telescope(self, telescope_name: str) -> dict:
        """
        Gets the current position of a telescope.

        Args:
            telescope_name (str): The name of the telescope.

        Returns:
            dict: The position data in multiple frames.
        """
        telescope = await self._connect_telescope(telescope_name)
        return telescope.get_position(self._location, self._time.now)
    
    async def slew_telescope(self, telescope_name: str, 
                             coord: tuple[float, float],
                             input_type: CoordinateTypes = CoordinateTypes.EQUATORIAL_J2000,
                             mode: Literal["SLEW", "TRACK", "SYNC"] = "TRACK"):
        """
        Initiates a slew operation on a telescope and waits for completion.

        Args:
            telescope_name (str): The name of the telescope.
            coord (tuple[float, float]): Target coordinates.
            input_type (CoordinateTypes): The frame of the input coordinates.
            mode (Literal["SLEW", "TRACK", "SYNC"]): Slew mode.
        """
        telescope = await self._connect_telescope(telescope_name)
        await telescope.slew(input_type, mode, coord, self._location, self._time.now)
        
        while telescope.is_slewing():
            await asyncio.sleep(0.2)

    async def abort_slew_telescope(self, telescope_name: str):
        """
        Aborts any ongoing movement on a telescope.

        Args:
            telescope_name (str): The name of the telescope.
        """
        telescope = await self._connect_telescope(telescope_name)
        await telescope.abort_motion()

    def update_location(self, lat: float, lon: float):
        """
        Updates the observer's location.

        Args:
            lat (float): Latitude in decimal degrees.
            lon (float): Longitude in decimal degrees.
        """
        self._location = (lat, lon)
    
    def update_time(self, new_time: datetime):
        """
        Updates the synchronized clock time.

        Args:
            new_time (datetime): The new reference time.
        """
        self._time.set_time(new_time)
