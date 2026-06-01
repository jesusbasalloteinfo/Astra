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

from abc import ABC, abstractmethod
from datetime import datetime, timedelta

import numpy as np
from astropy.coordinates import SkyCoord, EarthLocation, AltAz
from astropy.time import Time
import astropy.units as u
from typing import List, Tuple
from models.api.common import SyncPayload

class BaseEngine(ABC):
    """Abstract base class for astronomical calculation engines.

    Defines common utilities and the standard interface for engines that calculate 
    the positions and movements of astronomical objects.
    """
    
    @staticmethod
    def _circular_diff(a: float, b: float, max_val: float = 360.0) -> float:
        """Handles wrap-around differences for angular values.

        Args:
            a (float): The first angle.
            b (float): The second angle.
            max_val (float): The maximum value for wrap-around (e.g., 360.0 for degrees).

        Returns:
            float: The signed difference between the two angles.
        """
        return (a - b + max_val / 2) % max_val - max_val / 2
    
    @abstractmethod
    def get_sky_movement(self, t0_dt: datetime, lat: float, lon: float, elev_m: float = 0.0, ttl: float = 120.0) -> SyncPayload:
        """Calculates the movement of a full catalog of objects.

        Args:
            t0_dt (datetime): The target UTC time for calculation.
            lat (float): Observer's latitude in decimal degrees.
            lon (float): Observer's longitude in decimal degrees.
            elev_m (float): Observer's elevation in meters. Defaults to 0.0.
            ttl (float): Movement window in seconds. Defaults to 120.0.

        Returns:
            SyncPayload: Computed positions for all relevant objects.
        """
        pass
    
    @abstractmethod
    def get_object_movement(self, target_id: str, target_time: datetime, lat: float, lon: float, elev_m: float = 0.0):
        """Calculates detailed movement and data for a single object.

        Args:
            target_id (str): The identifier of the object.
            target_time (datetime): The target UTC time for calculation.
            lat (float): Observer's latitude.
            lon (float): Observer's longitude.
            elev_m (float): Observer's elevation.
        """
        pass

