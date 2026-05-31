import asyncio
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query
from services.astro_service.astro_service import AstroService
from models.api.common import SyncPayload, MetadataCatalogPayload
from models.api.sidereal import SiderealObjectDataResponse
from core.translations import get_lang_dict, localise_dict_payload, localise_list_payload, localise_object

async def get_astro_service() -> AstroService:
    """FastAPI dependency to retrieve the AstroService singleton instance.

    Returns:
        AstroService: The initialized AstroService instance.
    """
    return await AstroService.get_instance()

router = APIRouter()

@router.get("/metadata", response_model=MetadataCatalogPayload, summary="Get sidereal catalog metadata")
async def get_metadata(
    lang: str = Query("en", description="Language code for names (e.g., 'es', 'en')"),
    service: AstroService = Depends(get_astro_service)
):
    """Retrieves all metadata for the sidereal catalog.

    Args:
        lang (str): Language code for localized names and descriptions. Defaults to "en".
        service (AstroService): The astronomical service instance.

    Returns:
        MetadataCatalogPayload: A localized dictionary containing metadata for all sidereal objects.
    """
    raw_data = service.get_sidereal_metadata()
    lang_dict = get_lang_dict("sidereal", lang)
    
    return localise_dict_payload(raw_data, lang_dict)

@router.get("/constellations", response_model=MetadataCatalogPayload, summary="Get constellations metadata")
async def get_constellations(
    lang: str = Query("en", description="Language code for names (e.g., 'es', 'en')"),
    service: AstroService = Depends(get_astro_service)
):
    """Retrieves metadata for all astronomical constellations.

    Args:
        lang (str): Language code for localized names. Defaults to "en".
        service (AstroService): The astronomical service instance.

    Returns:
        MetadataCatalogPayload: A localized list containing metadata for all constellations.
    """
    raw_data = service.get_constellations_metadata()
    lang_dict = get_lang_dict("constellations", lang)
  
    return localise_list_payload(raw_data, lang_dict)

@router.get("/sync", response_model=SyncPayload, summary="Get star and DSO movement for a given time and place")
def sync_sky(
    target_time: datetime = Query(..., description="Target time in ISO 8601 UTC"),
    lat: float = Query(..., description="Observer latitude in degrees"),
    lon: float = Query(..., description="Observer longitude in degrees"),
    elev: float = Query(0.0, description="Observer elevation in metres"), 
    service: AstroService = Depends(get_astro_service)
):
    """Calculates real-time horizontal positions for all sidereal objects.

    Computes the Altitude and Azimuth for the entire star and deep-sky object (DSO) 
    catalogs based on the observer's location and time. A movement window (TTL) 
    of 120 seconds is applied for optimized synchronization.

    Args:
        target_time (datetime): The target UTC time for calculation.
        lat (float): Observer's latitude in decimal degrees.
        lon (float): Observer's longitude in decimal degrees.
        elev (float): Observer's elevation in meters. Defaults to 0.0.
        service (AstroService): The astronomical service instance.

    Returns:
        SyncPayload: A payload containing positions and timing metadata.
    """
    return service.get_sidereal_positions(
        target_time=target_time,
        lat=lat,
        lon=lon,
        elev=elev,
        ttl=120.0
    )
    


@router.get("/{object_id}", response_model=SiderealObjectDataResponse, summary="Get star or DSO movement for a given time and place")
async def get_ephemeris(
    object_id: str,
    target_time: datetime = Query(..., description="Target time in ISO 8601 UTC"),
    lat: float = Query(..., description="Observer latitude in degrees"),
    lon: float = Query(..., description="Observer longitude in degrees"),
    elev: float = Query(0.0, description="Observer elevation in metres"), 
    lang: str = Query("en", description="Language code for names (e.g., 'es', 'en')"), 
    service: AstroService = Depends(get_astro_service)
):
    """Calculates detailed ephemeris data for a specific sidereal object.

    Args:
        object_id (str): The unique identifier of the astronomical object (e.g., 'M42', 'sirius').
        target_time (datetime): The target UTC time for calculation.
        lat (float): Observer's latitude in decimal degrees.
        lon (float): Observer's longitude in decimal degrees.
        elev (float): Observer's elevation in meters. Defaults to 0.0.
        lang (str): Language code for localized output. Defaults to "en".
        service (AstroService): The astronomical service instance.

    Returns:
        SiderealObjectDataResponse: Localized object data including computed horizontal coordinates.

    Raises:
        HTTPException: If the object ID is not found in the catalog.
    """
    try:
        raw_data = service.get_sidereal_object(object_id, target_time, lat, lon, elev)
        lang_dict = get_lang_dict("sidereal", lang)
        
        return localise_object(raw_data, lang_dict)
    except ValueError as e:
        raise HTTPException(404, str(e))
