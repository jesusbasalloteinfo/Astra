from abc import ABC, abstractmethod
from datetime import datetime, timedelta

import numpy as np
from astropy.coordinates import SkyCoord, EarthLocation, AltAz
from astropy.time import Time
import astropy.units as u
from typing import List, Tuple
from models.ResponseSchemas import SyncPayload

class BaseEngine(ABC):
    
    @abstractmethod
    def get_sky_movement(self, t0_dt: datetime, lat: float, lon: float, elev_m: float = 0.0, ttl:float=120.0) -> SyncPayload:
        """
        Calculates the sky and its movement for a time and location
        """
        pass
    

