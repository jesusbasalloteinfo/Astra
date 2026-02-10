from enum import Enum
import json
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
        
    def get_position(self, location:tuple[float, float]|None=None, time=datetime.now(timezone.utc))-> dict:
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

    
    async def slew(self, mode:CoordinateTypes, coord :tuple[float, float], location:tuple[float, float]|None=None, time=datetime.now(timezone.utc)):
        """Move the telescope"""
        
        # Handle SLEW/SYNC 
        if "ON_COORD_SET" in self._device_data:
            await self._client.send_newVector(self.name, "ON_COORD_SET", members={"SLEW": "On"})

        members=self._converter.convert_from(time, coord, location, mode)
        LOGGER.info(f"Slewing to {coord} in {mode} to {self._converter.get_converter_type()}", details=members)
        # Send movement command
        await self._client.send_newVector(self.name, self._converter.get_slew_command(), members=members)

    
 
    async def slew_equatorialJ2000(self, ra:float, dec:float, time=datetime.now(timezone.utc)):
        await self.slew(time=time, coord=(ra, dec), mode=CoordinateTypes.EQUATORIAL_J2000)

    async def slew_equatorialEOD(self, ra:float, dec:float, time=datetime.now(timezone.utc)):
        await self.slew(time=time, coord=(ra, dec), mode=CoordinateTypes.EQUATORIAL_EOD)

    async def slew_horizontal(self, alt:float, az:float, lat:float, lon:float, time=datetime.now(timezone.utc)):
        await self.slew(time=time, coord=(alt, az), location=(lat, lon), mode=CoordinateTypes.HORIZONTAL)