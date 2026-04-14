import asyncio
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query
from services.astro_service.astro_service import AstroService
from models.api.common import SyncPayload, MetadataCatalogPayload
from core.translations import get_lang_dict, localise_dict_payload, localise_object

async def get_astro_service() -> AstroService:
    return await AstroService.get_instance()

router = APIRouter()

@router.get("/metadata", summary="Get planetary catalog metadata")
async def get_metadata(
    target_time: datetime = Query(..., description="Target time in ISO 8601 UTC"),
    lat: float = Query(..., description="Observer latitude in degrees"),
    lon: float = Query(..., description="Observer longitude in degrees"),
    elev: float = Query(0.0, description="Observer elevation in metres"), 
    lang: str = Query("en", description="Language code for names (e.g., 'es', 'en')"),
    service:AstroService=Depends(get_astro_service)):
    """
    Returns all planetary catalog metadata
    """
    
    raw_data=service.get_planetary_metadata(target_time, lat, lon, elev, ttl=120)
    lang_dict = get_lang_dict("planetary", lang)

    
    return localise_dict_payload(raw_data, lang_dict)

@router.get("/sync", response_model=SyncPayload, summary="Get planetary movement for a given time and place")
def sync_sky(
    target_time: datetime = Query(..., description="Target time in ISO 8601 UTC"),
    lat: float = Query(..., description="Observer latitude in degrees"),
    lon: float = Query(..., description="Observer longitude in degrees"),
    elev: float = Query(0.0, description="Observer elevation in metres"), 
    service:AstroService=Depends(get_astro_service)):

    """
    Calculates the Altazimutal positions of the planetary catalog with a movement window of 2 minutes.
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
    service:AstroService=Depends(get_astro_service)
):
    """
    Calculates the object ephemeris data for a given time and place
    """
    try:
        raw_data=service.get_planetary_object(object_id, target_time, lat, lon, elev, ttl=120)
        lang_dict = get_lang_dict("planetary", lang)

        
        return localise_object(raw_data, lang_dict)
    except ValueError as e:
        raise HTTPException(404, str(e))
