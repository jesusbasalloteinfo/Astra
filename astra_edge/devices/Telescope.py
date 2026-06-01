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
Telescope device implementation with coordinate transformation support.
"""
import asyncio
from typing import Literal
from datetime import datetime
from devices.INDIDevice import INDIDevice, INDIDeviceType
from utils.CoordinateHandler import CoordinateHandler, CoordinateTypes
from utils.logging import get_logger

LOGGER = get_logger("INDITelescope")

class Telescope(INDIDevice):
    """
    Proxy for an INDI Telescope device.

    Provides high-level methods for positioning, slewing, and motion control,
    automatically handling coordinate transformations between different frames.

    Attributes:
        _converter (CoordinateHandler): Utility for handling coordinate conversions.
    """

    def __init__(self, client, device_name):
        """
        Initializes the Telescope proxy.

        Args:
            client (IPyClient): The INDI client instance.
            device_name (str): The unique name of the telescope.
        """
        super().__init__(client, device_name)
        self._type: INDIDeviceType = INDIDeviceType.TELESCOPE
        self._converter: CoordinateHandler = CoordinateHandler(self._device_data)
        
    def get_position(self, 
                     location: tuple[float, float], 
                     time: datetime) -> dict:
        """
        Gets the current position of the telescope in multiple coordinate systems.

        Args:
            location (tuple[float, float]): The observer's location (latitude, longitude).
            time (datetime): The current observation time.

        Returns:
            dict: A dictionary containing 'equatorial_j2000', 'equatorial_eod', 
                and 'horizontal' coordinates.

        Raises:
            ValueError: If no coordinate data is available for the device.
        """
        command_type = self._converter.get_converter_type()
        vector = self._device_data.get(command_type.value)

        if not vector:
            raise ValueError(f"No data available for command: {command_type}")
        
        data = tuple(map(float, (vector.get("RA", "ALT"), vector.get("DEC", "AZ"))))

        result = {}
        coordinate_types = [
                (CoordinateTypes.EQUATORIAL_J2000, 'equatorial_j2000'),
                (CoordinateTypes.EQUATORIAL_EOD, 'equatorial_eod'),
                (CoordinateTypes.HORIZONTAL, 'horizontal')
            ]
        for coord_type, key in coordinate_types:
            converted = CoordinateHandler.convert_coord(time, data, location, convert_from=command_type, convert_to=coord_type)
            keys = coord_type.get_properties()

            # Coordinates with their properties
            result[key] = dict(zip(keys, converted))
        
        return result

    
    async def slew(self, input_type: CoordinateTypes, 
                   mode: Literal["SLEW", "TRACK", "SYNC"], 
                   coord: tuple[float, float], 
                   location: tuple[float, float], 
                   time: datetime):
        """
        Moves the telescope to the specified coordinates.

        Args:
            input_type (CoordinateTypes): The coordinate frame of the input coordinates.
            mode (Literal["SLEW", "TRACK", "SYNC"]): The operation mode.
            coord (tuple[float, float]): Target coordinates [ra/alt, dec/az].
            location (tuple[float, float]): The observer's location (latitude, longitude).
            time (datetime): The current observation time.
        """
        
        # Handle SLEW/SYNC 
        if "ON_COORD_SET" in self._device_data:
            # All the diferent slew modes
            switch_states = {"SLEW": "Off", "TRACK": "Off", "SYNC": "Off"}
            switch_states[mode] = "On"
            await self._client.send_newVector(self.name, "ON_COORD_SET", members=switch_states)

        members = self._converter.convert_from(time, coord, location, input_type)
        LOGGER.info(f"Slewing to {coord} in {input_type} to {self._converter.get_converter_type()}", details=members)
        # Send movement command
        await self._client.send_newVector(self.name, self._converter.get_converter_type_value(), members=members)

    def is_slewing(self) -> bool:
        """
        Checks if the telescope is currently moving.

        Returns:
            bool: True if the device state is 'Busy', False otherwise.

        Raises:
            ValueError: If no coordinate data is available for the device.
        """
        command_type = self._converter.get_converter_type()
        vector = self._device_data.get(command_type.value)

        if not vector:
            raise ValueError(f"No data available for command: {command_type}")
        
        return True if vector.state == "Busy" else False
        

    async def abort_motion(self):
        """
        Cancels any ongoing movement or tracking.

        Raises:
            ValueError: If the abort command results in an unexpected device state.
        """
        
        vector = self._device_data["TELESCOPE_ABORT_MOTION"]
        property = list(vector.keys())[0]
        await self._client.send_newVector(self.name, "TELESCOPE_ABORT_MOTION", members={property: "On"})

        vector = self._device_data["TELESCOPE_ABORT_MOTION"]
        while vector.state == "Busy":
            await asyncio.sleep(0.2)
            vector = self._device_data["TELESCOPE_ABORT_MOTION"]

        
        if vector.state != "Ok":
            raise ValueError(f"Unexpected state at abort for {self.name}: {vector.state}")
