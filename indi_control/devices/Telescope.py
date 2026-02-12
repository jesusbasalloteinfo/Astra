from enum import Enum
import json
from typing import Literal
from devices.INDIDevice import INDIDevice, INDIDeviceType
from utils.CoordinateHandler import CoordinateHandler, CoordinateTypes
from utils.logging import get_logger
from datetime import datetime, timezone

LOGGER=get_logger("INDITelescope")

class Telescope(INDIDevice):

    def __init__(self, client, device_name):
        super().__init__(client, device_name)
        self._type:INDIDeviceType = INDIDeviceType.TELESCOPE

        self._converter:CoordinateHandler=CoordinateHandler(self._device_data)
        
    def get_position(self, 
                     location:tuple[float, float], 
                     time:datetime)-> dict:
        """Gets the position of the telescope in diferent coordinate systems"""
        slew_command = self._converter.get_slew_command()
        vector = self._device_data.get(slew_command)

        if not vector:
            raise ValueError(f"No data available for command: {slew_command}")
        
        data = tuple(map(float, (vector.get("RA", "ALT"), vector.get("DEC", "AZ"))))

        result = {}
        coordinate_types = [
                (CoordinateTypes.EQUATORIAL_J2000, 'equatorial_j2000'),
                (CoordinateTypes.EQUATORIAL_EOD, 'equatorial_eod'),
                (CoordinateTypes.HORIZONTAL, 'horizontal')
            ]
        for coord_type, key in coordinate_types:
            converted = CoordinateHandler.convert_coord(time, data, location, convert_from=slew_command, convert_to=coord_type)
            keys = coord_type.get_properties()

            # Coordinates with their properties
            result[key] = dict(zip(keys, converted))
        
        return result

    
    async def slew(self, input_type:CoordinateTypes, 
                   mode:Literal["SLEW", "TRACK", "SYNC"], 
                   coord :tuple[float, float], 
                   location:tuple[float, float], 
                   time:datetime):
        """Move the telescope"""
        
        # Handle SLEW/SYNC 
        if "ON_COORD_SET" in self._device_data:
            # All the diferent slew modes
            switch_states = {"SLEW": "Off", "TRACK": "Off", "SYNC": "Off"}
            switch_states[mode] = "On"
            await self._client.send_newVector(self.name, "ON_COORD_SET", members=switch_states)

        members=self._converter.convert_from(time, coord, location, input_type)
        LOGGER.info(f"Slewing to {coord} in {input_type} to {self._converter.get_converter_type()}", details=members)
        # Send movement command
        await self._client.send_newVector(self.name, self._converter.get_slew_command(), members=members)

    