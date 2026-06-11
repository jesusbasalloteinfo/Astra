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
Implementation logic for observation tools interacting with external services and devices.
"""
from typing import Tuple

import httpx
import os
from datetime import datetime, timezone
from services.device_tunnel.tunnel import DeviceTunnel
from models.device_messages import SlewCommand, SlewCommandData, CoordinateTypes

SIDERIS_URL = os.getenv("SIDERIS_API_BASE", "http://sideris:8624")

async def search_object_impl(query: str):
    """
    Implementation for searching celestial objects via the Sideris API.

    Args:
        query (str): The search term.

    Returns:
        dict: The search results from Sideris.
    """
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{SIDERIS_URL}/search", params={"q": query})
        response.raise_for_status()
        return response.json()

async def get_object_details_impl(object_id: str, type: str, location: Tuple[float, float]):
    """
    Implementation for fetching detailed object ephemerides via the Sideris API.

    Args:
        object_id (str): The identifier of the celestial object.
        type (str): The type ('sidereal' or 'planetary').
        location (Tuple[float, float]): The observer's location [lat, lon].

    Returns:
        dict: The object details including current coordinates.

    Raises:
        ValueError: If an invalid object type is provided.
    """
    async with httpx.AsyncClient() as client:
        # Both sidereal and planetary ephemeris endpoints require target_time, lat, lon
        
        params = {
            "target_time": datetime.now(timezone.utc).isoformat(),
            "lat": location[0],
            "lon": location[1]
        }
        
        if type == "sidereal":
            response = await client.get(f"{SIDERIS_URL}/sidereal/{object_id}", params=params)
        elif type == "planetary":
            response = await client.get(f"{SIDERIS_URL}/planetary/{object_id}", params=params)
        else:
            raise ValueError("Invalid object type")
            
        response.raise_for_status()
        return response.json()

async def slew_to_object_impl(tunnel: DeviceTunnel, 
                              telescope: str,
                              location: Tuple[float, float],
                              id: str, 
                              type: str, 
                              mode: str,
                              name: str = None):
    """
    Implementation for commanding a telescope to slew to a specific object.

    Fetches the current horizontal coordinates of the object from Sideris
    and sends a movement command through the device tunnel.

    Args:
        tunnel (DeviceTunnel): The active tunnel to the Edge device.
        telescope (str): The name of the telescope device.
        location (Tuple[float, float]): The observer's location [lat, lon].
        id (str): The target object identifier.
        type (str): The target object type.
        mode (str): The slew mode ('TRACK', 'SLEW', or 'SYNC').
        name (str, optional): The human-readable name of the object.

    Returns:
        str: Success message.

    Raises:
        ValueError: If coordinates cannot be retrieved.
        Exception: If the device command fails or is cancelled.
    """
    try:
        # 1. Fetch object coordinates from sideris
        details = await get_object_details_impl(id, type, location)
        
        # 2. Extract coordinates based on exact models
        alt = details.get("alt")
        az = details.get("az")
        
        if alt is None or az is None:
            raise ValueError("Could not retrieve ALT/AZ coordinates for the object.")
        
        # 3. Send SlewCommand
        params = SlewCommandData(
            coord=(alt, az),
            input_type=CoordinateTypes.HORIZONTAL,
            mode=mode
        )
        payload = SlewCommand(device=telescope, data=params)
        
        resp = await tunnel.send_command(payload, timeout=1000)
        if resp.status == "ERROR":
            raise Exception(f"Error slewing telescope: {resp.reason}")
        elif resp.status == "CANCELLED":
            raise Exception("Operation was cancelled")
        
        return "Telescope slew completed."
    except Exception as e:
        raise e
