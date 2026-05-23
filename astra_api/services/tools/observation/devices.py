from typing import Tuple

import httpx
import os
from datetime import datetime, timezone
from api.devices import get_device_tunnel
from services.device_tunnel.tunnel import DeviceTunnel
from models.device_messages import SlewCommand, SlewCommandData, CoordinateTypes

SIDERIS_URL = os.getenv("SIDERIS_API_BASE", "http://sideris:8624")

async def search_object_impl(query: str):
    print("\n\n")
    print(f"{SIDERIS_URL}/search")
    print("\n\n")
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{SIDERIS_URL}/search", params={"q": query})
        response.raise_for_status()
        return response.json()

async def get_object_details_impl(object_id: str, type: str, location:Tuple[float, float]):
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
                              telescope:str,
                              location:Tuple[float, float],
                              id: str, 
                              type: str, 
                              mode: str):
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
