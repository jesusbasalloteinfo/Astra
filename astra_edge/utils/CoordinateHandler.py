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
Utility for handling astronomical coordinate transformations.
"""
from astropy.coordinates import SkyCoord, AltAz, FK5, ICRS, EarthLocation
from astropy import units as u
from astropy.time import Time
from enum import Enum

class CoordinateTypes(Enum):
    """
    Enumeration of coordinate frames supported by INDI and Astra.
    """
    EQUATORIAL_J2000 = "EQUATORIAL_COORD" # Equatorial coordinates at J2000 frame (at 2000)
    EQUATORIAL_EOD = "EQUATORIAL_EOD_COORD" # Equatorial coordinates at Equinox of Date (at this moment)
    HORIZONTAL = "HORIZONTAL_COORD" # Horizontal coordinates with the observer position and date

    @classmethod
    def from_str(cls, value: str):
        """
        Returns the matching CoordinateTypes for a given string.

        Args:
            value (str): The string representation of the coordinate type.

        Returns:
            CoordinateTypes: The matching enum member, or EQUATORIAL_EOD if no match is found.
        """
        try:
            return cls(value.lower())
        except ValueError:
            return cls.EQUATORIAL_EOD

    def __str__(self):
        """
        Returns the INDI property name for the coordinate type.

        Returns:
            str: The property name (e.g., 'EQUATORIAL_COORD').
        """
        return self.value
    
    def get_properties(self) -> tuple[str, str]:
        """
        Returns the property keys (axis names) for this coordinate type.

        Returns:
            tuple[str, str]: ('ra', 'dec') or ('alt', 'az').
        """
        properties = ("ra", "dec")
        if self == CoordinateTypes.HORIZONTAL:
            properties = ("alt", "az")
        return properties
    
    @classmethod
    def list(cls):
        """
        Returns a list of all enum members.

        Returns:
            list[CoordinateTypes]: All members of the enum.
        """
        return [item for item in cls]
    
    @classmethod
    def list_values(cls):
        """
        Returns a list of all enum member values.

        Returns:
            list[str]: All property names of the enum.
        """
        return [item.value for item in cls]



class CoordinateHandler:
    """
    Manager for coordinate conversions for telescope slewing and positioning.

    Automatically identifies the best coordinate frame supported by a device
    and provides methods to convert between different systems using Astropy.
    """
    
    def __init__(self, device_data: dict = None):
        """
        Initializes the coordinate handler.

        Args:
            device_data (dict, optional): Dictionary containing device properties from INDI 
                to determine supported coordinate frames.
        """
        priority_types = [
            CoordinateTypes.EQUATORIAL_EOD,
            CoordinateTypes.EQUATORIAL_J2000,
            CoordinateTypes.HORIZONTAL
        ]
        self.converter_type = CoordinateTypes.EQUATORIAL_J2000
        
        if device_data:
            for coord_type in priority_types:
                if coord_type.value in device_data:
                    self.converter_type = coord_type
                    break 

    def get_converter_type(self) -> CoordinateTypes:
        """
        Gets the primary coordinate type supported by the device.

        Returns:
            CoordinateTypes: The configured coordinate frame.
        """
        return self.converter_type
    
    def get_converter_type_value(self) -> str:
        """
        Gets the INDI property name for the primary coordinate type.

        Returns:
            str: The INDI property name.
        """
        return self.converter_type.value
    
    @staticmethod
    def convert_coord(time: Time, coord: tuple[float, float], location_in: tuple[float, float] | None, 
                       convert_from: CoordinateTypes, convert_to: CoordinateTypes):
        """
        Converts coordinates between different astronomical systems.

        Args:
            time (Time): The observation time.
            coord (tuple[float, float]): The input coordinates [ra/alt, dec/az].
            location_in (tuple[float, float] | None): Observer location [lat, lon].
            convert_from (CoordinateTypes): Input coordinate frame.
            convert_to (CoordinateTypes): Output coordinate frame.

        Returns:
            map: A map object yielding two floats (the converted coordinates).

        Raises:
            ValueError: If location is missing for horizontal conversions or if coordinates are invalid.
        """

        coord_1, coord_2 = coord
        lat, lon = location_in if location_in is not None else (None, None)
        if (lat is None or lon is None) and \
            (convert_from == CoordinateTypes.HORIZONTAL or convert_to == CoordinateTypes.HORIZONTAL):
            raise ValueError("Latitude and longitude needed for Horizontal conversions")

        location = None   
        coord_obj = None     
        try:
            if lat is not None and lon is not None:
                location = EarthLocation(lat=lat * u.deg, lon=lon * u.deg)
        
            if convert_from == CoordinateTypes.EQUATORIAL_J2000:
                coord_obj = SkyCoord(
                    ra=coord_1 * u.hourangle,
                    dec=coord_2 * u.deg,
                    frame=ICRS()
                )
            elif convert_from == CoordinateTypes.EQUATORIAL_EOD:
                coord_obj = SkyCoord(
                    ra=coord_1 * u.hourangle,
                    dec=coord_2 * u.deg,
                    frame=FK5(equinox=time)
                )
            else:  # Horizontal
                coord_obj = SkyCoord(
                    alt=coord_1 * u.deg,
                    az=coord_2 * u.deg,
                    frame=AltAz(obstime=time, location=location)
                )
        except ValueError as e:
            raise ValueError(f"Invalid input coordinates for {convert_from.name}: {e}")

        ret_coords = None
        if convert_to == CoordinateTypes.EQUATORIAL_J2000:
            aux = coord_obj.transform_to(ICRS())
            ret_coords = aux.ra.hour, aux.dec.deg
        elif convert_to == CoordinateTypes.EQUATORIAL_EOD:
            aux = coord_obj.transform_to(FK5(equinox=time))
            ret_coords = aux.ra.hour, aux.dec.deg
        else:
            aux = coord_obj.transform_to(AltAz(obstime=time, location=location))
            ret_coords = aux.alt.deg, aux.az.deg
            
        return map(float, ret_coords)

    def convert_from(self, time: Time, coord: tuple, location: tuple[float, float] | None, convert_from: CoordinateTypes):
        """
        Converts coordinates from an external frame to the device's native frame.

        Args:
            time (Time): The observation time.
            coord (tuple): Input coordinates.
            location (tuple[float, float] | None): Observer location.
            convert_from (CoordinateTypes): Input coordinate frame.

        Returns:
            dict: Dictionary with axis names ('RA', 'DEC' or 'ALT', 'AZ') as keys.
        """
        result1, result2 = CoordinateHandler.convert_coord(time, coord, location, convert_from=convert_from, convert_to=self.converter_type)
        
        if self.converter_type == CoordinateTypes.HORIZONTAL:
            return {"ALT": result1, "AZ": result2}
        else:
            return {"RA": result1, "DEC": result2}
        

    def convert_to(self, time: Time, coord: dict, location: tuple[float, float] | None, convert_to: CoordinateTypes):
        """
        Converts coordinates from the device's native frame to an external frame.

        Args:
            time (Time): The observation time.
            coord (dict): Input coordinates in native frame.
            location (tuple[float, float] | None): Observer location.
            convert_to (CoordinateTypes): Target coordinate frame.

        Returns:
            dict: Dictionary with axis names as keys.
        """
        if self.converter_type == CoordinateTypes.HORIZONTAL:
            coords = map(float, (coord["ALT"], coord["AZ"]))
        else:
            coords = map(float, (coord["RA"], coord["DEC"]))
        
        result1, result2 = CoordinateHandler.convert_coord(time, coords, location, convert_to=convert_to, convert_from=self.converter_type)

        if convert_to == CoordinateTypes.HORIZONTAL:
            return {"ALT": result1, "AZ": result2}
        else:
            return {"RA": result1, "DEC": result2}
