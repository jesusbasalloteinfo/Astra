from abc import ABC, abstractmethod
from datetime import datetime, timedelta

import numpy as np
from astropy.coordinates import SkyCoord, EarthLocation, AltAz
from astropy.time import Time
import astropy.units as u
from typing import List, Tuple
from models.ResponseSchemas import SyncPayload

class BaseEngine(ABC):
    
    # @abstractmethod
    # def get_metadata(self, t0_dt: datetime, lat: float, lon: float, elev_m: float = 0.0):
    #     """
    #     Returns all the objects metadata for a time and location
    #     """
    #     pass
    @staticmethod
    def _circular_diff(a: float, b: float, max_val: float = 360.0) -> float:
        """Handles wrap-around differences (e.g., 359 degrees to 1 degree)."""
        return (a - b + max_val / 2) % max_val - max_val / 2
    
    @abstractmethod
    def get_sky_movement(self, t0_dt: datetime, lat: float, lon: float, elev_m: float = 0.0, ttl:float=120.0) -> SyncPayload:
        """
        Calculates the sky and its movement for a time and location
        """
        pass
    
    @abstractmethod
    def get_object_movement(self, target_id:str, target_time: datetime, lat: float, lon: float, elev_m: float = 0.0):
        """
        Calculate an object movement and metadata
        """

