import asyncio
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query
from services.astro_service.astro_service import AstroService
from models.api.common import SyncPayload, MetadataCatalogPayload
from models.api.sidereal import SiderealObjectDataResponse

async def get_astro_service() -> AstroService:
    return await AstroService.get_instance()

router = APIRouter()

@router.get("/metadata", response_model=MetadataCatalogPayload, summary="Get sidereal catalog metadata")
async def get_metadata(service:AstroService=Depends(get_astro_service)):
    """
    Returns all sidereal catalog metadata
    """
    return service.get_sidereal_metadata()

@router.get("/constellations", response_model=MetadataCatalogPayload, summary="Get constellations metadata")
async def get_constellations(service:AstroService=Depends(get_astro_service)):
    """
    Returns all constellations metadata
    """
    return service.get_constellations_metadata()

@router.get("/sync", response_model=SyncPayload, summary="Get star and DSO movement for a given time and place")
def sync_sky(
    target_time: datetime = Query(..., description="Target time in ISO 8601 UTC"),
    lat: float = Query(..., description="Observer latitude in degrees"),
    lon: float = Query(..., description="Observer longitude in degrees"),
    elev: float = Query(0.0, description="Observer elevation in metres"), 
    service:AstroService=Depends(get_astro_service)
):
    """
    Calculates the Altazimutal positions of the star and dso catalogs with a movement window of 2 minutes.
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
    service:AstroService=Depends(get_astro_service)
):
    """
    Calculates the object ephemeris data for a given time and place
    """
    try:
        return service.get_sidereal_object(object_id, target_time, lat, lon, elev)
    except ValueError as e:
        raise HTTPException(404, str(e))
