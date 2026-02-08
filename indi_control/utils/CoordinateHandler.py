from astropy.coordinates import SkyCoord, AltAz, FK5, ICRS, EarthLocation, Angle
from astropy import units as u
from astropy.time import Time
from enum import Enum
from datetime import datetime, timezone
import asyncio

class CoordinateTypes(Enum):
    EQUATORIAL_J2000 = "EQUATORIAL_COORD" # Equatorial coordinats at J2000 frame (at 2000)
    EQUATORIAL_EOD = "EQUATORIAL_EOD_COORD" # Equatorial coordinates at Equinox of Date (at this moment)
    ALTAZIMUTAL = "HORIZONTAL_COORD" # Altazimutal coordinates with the observer position and date

    @classmethod
    def from_str(cls, value: str):
        """Get the type from a string"""
        try:
            return cls(value.lower())
        except ValueError:
            return cls.EQUATORIAL_EOD

    def __str__(self):
        """Get the device value"""
        return self.value
    
    @classmethod
    def list_values(cls):
        """Returns a list with the enum values"""
        return [item.value for item in cls]



class CoordinateHandler:
    """
    Coordinate handler that manages coordinate conversions for telescope slewing
    """
    
    def __init__(self, device_data: dict=None):
        """
        Initialize coordinate handler with device capabilities and location data
        
        Args:
            device_data: Dictionary containing device properties from INDI
        """
        priority_types = [
            CoordinateTypes.EQUATORIAL_EOD,
            CoordinateTypes.EQUATORIAL_J2000,
            CoordinateTypes.ALTAZIMUTAL
        ]
        self.converter_type = CoordinateTypes.EQUATORIAL_J2000
        
        if device_data:
            for coord_type in priority_types:
                if coord_type.value in device_data:
                    self.converter_type = coord_type
                    break 

    def get_converter_type(self) -> CoordinateTypes:
        """
        Get the conversion type of the device
        
        Returns:
            Coordinate Converter type of the configured type
        """
        return self.converter_type
    
    def get_slew_command(self) -> str:
        """
        Get the appropriate slew command name for the device
        
        Returns:
            String with the command name
        """
        return self.converter_type.value
    
    @staticmethod
    def _convert_coord(time:Time, coord:tuple[float, float], location_in:tuple[float, float]|None, 
                       convert_from: CoordinateTypes, convert_to: CoordinateTypes):
        """
        Convert coordinates between different systems
        """

        coord_1, coord_2 = coord
        lat, lon = location_in if location_in is not None else (None, None)
        if (lat is None or lon is None) and \
            (convert_from == CoordinateTypes.ALTAZIMUTAL or convert_to == CoordinateTypes.ALTAZIMUTAL):
            raise ValueError("Latitude and longitude needed for ALTAZ conversions")

        location = None   
        coord = None     
        try:
            if lat is not None and lon is not None:
                location = EarthLocation(lat=lat *u.deg, lon=lon*u.deg)
        
            if convert_from == CoordinateTypes.EQUATORIAL_J2000:
                coord = SkyCoord(
                    ra=coord_1 * u.hourangle,
                    dec=coord_2 * u.deg,
                    frame=ICRS()
                )
            elif convert_from == CoordinateTypes.EQUATORIAL_EOD:
                coord = SkyCoord(
                    ra=coord_1 * u.hourangle,
                    dec=coord_2 * u.deg,
                    frame=FK5(equinox=time)
                )
            else:  # ALTAZ
                coord = SkyCoord(
                    alt=coord_1 * u.deg,
                    az=coord_2 * u.deg,
                    frame=AltAz(obstime=time, location=location)
                )
        except ValueError as e:
            raise ValueError(f"Invalid input coordinates for {convert_from.name}: {e}")

        ret_coords = None
        if convert_to == CoordinateTypes.EQUATORIAL_J2000:
            aux = coord.transform_to(ICRS())
            ret_coords = aux.ra.hour, aux.dec.deg
        elif convert_to == CoordinateTypes.EQUATORIAL_EOD:
            aux = coord.transform_to(FK5(equinox=time))
            ret_coords = aux.ra.hour, aux.dec.deg
        else:
            aux = coord.transform_to(AltAz(obstime=time, location=location))
            ret_coords = aux.alt.deg, aux.az.deg
            
        return map(float, ret_coords)

    def convert_from(self, time:Time, coord:tuple, location:tuple[float, float]|None, convert_from: CoordinateTypes):
        """
        Convert coordinates between different systems
        """
        result1, result2 = CoordinateHandler._convert_coord(time, coord, location, convert_from=convert_from, convert_to=self.converter_type)
        
        if self.converter_type==CoordinateTypes.ALTAZIMUTAL:
            return {"ALT": result1,"AZ":result2}
        else:
            return {"RA": result1, "DEC": result2}
        

    def convert_to(self, time:Time, coord:dict, location:tuple[float, float]|None, convert_to: CoordinateTypes):
        """
        Convert coordinates between different systems
        """
        if self.converter_type==CoordinateTypes.ALTAZIMUTAL:
            coords = map(float, (coord["ALT"], coord["AZ"]))
        else:
            coords = map(float, (coord["RA"], coord["DEC"]))
        
        result1, result2 = CoordinateHandler._convert_coord(time, coords, location, convert_to=convert_to, convert_from=self.converter_type)

        if convert_to==CoordinateTypes.ALTAZIMUTAL:
            return {"ALT": result1,"AZ":result2}
        else:
            return {"RA": result1, "DEC": result2}
        
        #TODO: MIRAR SI JSON KEYS EN MAJUSCULES SEMPRE