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

import asyncio
from datetime import datetime
import os

from fastapi import APIRouter, Depends, HTTPException, Query
from services.astro_service.astro_service import AstroService
from models.api.common import SyncPayload, MetadataCatalogPayload
from core.translations import get_lang_dict, localise_dict_payload, localise_object

async def get_astro_service() -> AstroService:
    """FastAPI dependency to retrieve the AstroService singleton instance.

    Returns:
        AstroService: The initialized AstroService instance.
    """
    return await AstroService.get_instance()

router = APIRouter()

@router.get("/metadata", summary="Get planetary catalog metadata")
async def get_metadata(
    target_time: datetime = Query(..., description="Target time in ISO 8601 UTC"),
    lat: float = Query(..., description="Observer latitude in degrees"),
    lon: float = Query(..., description="Observer longitude in degrees"),
    elev: float = Query(0.0, description="Observer elevation in metres"), 
    lang: str = Query("en", description="Language code for names (e.g., 'es', 'en')"),
    service: AstroService = Depends(get_astro_service)
):
    """Retrieves metadata for all objects in the planetary catalog.

    Calculates the current state (visibility, distance, etc.) for all major
    solar system bodies at the given time and location.

    Args:
        target_time (datetime): The target UTC time for calculation.
        lat (float): Observer's latitude in decimal degrees.
        lon (float): Observer's longitude in decimal degrees.
        elev (float): Observer's elevation in meters. Defaults to 0.0.
        lang (str): Language code for localized names. Defaults to "en".
        service (AstroService): The astronomical service instance.

    Returns:
        MetadataCatalogPayload: A localized dictionary containing metadata for all planetary objects.
    """
    raw_data = service.get_planetary_metadata(target_time, lat, lon, elev, ttl=120)
    lang_dict = get_lang_dict("planetary", lang)
    
    return localise_dict_payload(raw_data, lang_dict)

@router.get("/sync", response_model=SyncPayload, summary="Get planetary movement for a given time and place")
def sync_sky(
    target_time: datetime = Query(..., description="Target time in ISO 8601 UTC"),
    lat: float = Query(..., description="Observer latitude in degrees"),
    lon: float = Query(..., description="Observer longitude in degrees"),
    elev: float = Query(0.0, description="Observer elevation in metres"), 
    service: AstroService = Depends(get_astro_service)
):
    """Calculates real-time horizontal positions for all planetary objects.

    Computes the Altitude and Azimuth for major solar system bodies based on the 
    observer's location and time. A movement window (TTL) of 120 seconds is applied.

    Args:
        target_time (datetime): The target UTC time for calculation.
        lat (float): Observer's latitude in decimal degrees.
        lon (float): Observer's longitude in decimal degrees.
        elev (float): Observer's elevation in meters. Defaults to 0.0.
        service (AstroService): The astronomical service instance.

    Returns:
        SyncPayload: A payload containing positions and timing metadata.
    """
    return service.get_planetary_positions(
        target_time=target_time,
        lat=lat,
        lon=lon,
        elev=elev,
        ttl=120.0
    )
    


@router.get("/{object_id}", summary="Get a planetary object movement for a given time and place")
async def get_ephemeris(
    object_id: str,
    target_time: datetime = Query(..., description="Target time in ISO 8601 UTC"),
    lat: float = Query(..., description="Observer latitude in degrees"),
    lon: float = Query(..., description="Observer longitude in degrees"),
    elev: float = Query(0.0, description="Observer elevation in metres"), 
    lang: str = Query("en", description="Language code for names (e.g., 'es', 'en')"),
    service: AstroService = Depends(get_astro_service)
):
    """Calculates detailed ephemeris data for a specific planetary object.

    Args:
        object_id (str): The identifier of the planet (e.g., 'mars', 'jupiter').
        target_time (datetime): The target UTC time for calculation.
        lat (float): Observer's latitude in decimal degrees.
        lon (float): Observer's longitude in decimal degrees.
        elev (float): Observer's elevation in meters. Defaults to 0.0.
        lang (str): Language code for localized output. Defaults to "en".
        service (AstroService): The astronomical service instance.

    Returns:
        PlanetaryObjectDataResponse: Localized object data including coordinates and physical properties.

    Raises:
        HTTPException: If the planetary object ID is not recognized.
    """
    try:
        raw_data = service.get_planetary_object(object_id, target_time, lat, lon, elev, ttl=120)
        lang_dict = get_lang_dict("planetary", lang)

        # Inject image URL if exists
        base_dir = "static/planetary"
        valid_extensions = [".jpg", ".png", ".jpeg", ".webp"]
        
        safe_obj_id = object_id.lower() 
        raw_data.image_url = None
        
        for ext in valid_extensions:
            if os.path.exists(f"{base_dir}/{safe_obj_id}{ext}"):
                raw_data.image_url = f"/static/planetary/{safe_obj_id}{ext}"
                break 
        
        return localise_object(raw_data, lang_dict)
    except ValueError as e:
        raise HTTPException(404, str(e))
