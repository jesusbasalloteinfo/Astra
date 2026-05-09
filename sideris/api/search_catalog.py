from fastapi import APIRouter, Depends, Query
from datetime import datetime
from typing import List

from services.astro_service.astro_service import AstroService
from models.api.common import SearchResultItem
from core.translations import get_lang_dict, localise_dict_payload

router = APIRouter()

async def get_astro_service() -> AstroService:
    return await AstroService.get_instance()

@router.get("", response_model=List[SearchResultItem], summary="Global catalog search")
async def search_catalog(
    q: str = Query(..., min_length=2, description="Search query string"),
    limit: int = Query(10, ge=1, le=50, description="Max results limit"),
    lang: str = Query("en", description="Language code for searching by localised names"),
    service: AstroService = Depends(get_astro_service)
):
    """
    Performs a fast memory search across Sidereal, Constellations, and Planetary catalogs.
    """
    
    planetary_lang = get_lang_dict("planetary", lang)
    sidereal_lang = get_lang_dict("sidereal", lang)

    results = service.search_objects(query=q, limit=limit, planetary_translations=planetary_lang)
    
    for res in results:
        if res["id"] in sidereal_lang:
            trans_obj = sidereal_lang.get(res["id"])
            if trans_obj:
                res["name"] = trans_obj.name

    return results