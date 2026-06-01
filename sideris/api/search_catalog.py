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

from fastapi import APIRouter, Depends, Query
from datetime import datetime
from typing import List

from services.astro_service.astro_service import AstroService
from models.api.common import SearchResultItem
from core.translations import get_lang_dict, localise_dict_payload

router = APIRouter()

async def get_astro_service() -> AstroService:
    """FastAPI dependency to retrieve the AstroService singleton instance.

    Returns:
        AstroService: The initialized AstroService instance.
    """
    return await AstroService.get_instance()

@router.get("", response_model=List[SearchResultItem], summary="Global catalog search")
async def search_catalog(
    q: str = Query(..., min_length=2, description="Search query string"),
    limit: int = Query(10, ge=1, le=50, description="Max results limit"),
    lang: str = Query("en", description="Language code for searching by localised names"),
    service: AstroService = Depends(get_astro_service)
):
    """Performs a fast memory search across all catalogs.

    Searches across Sidereal (stars and DSOs), Constellations, and Planetary 
    catalogs. Results are scored based on query matches and sorted by relevance 
    (exact match, prefix match) and brightness (magnitude).

    Args:
        q (str): The search query string (minimum 2 characters).
        limit (int): Maximum number of results to return (1-50). Defaults to 10.
        lang (str): Language code for localized name matching. Defaults to "en".
        service (AstroService): The astronomical service instance.

    Returns:
        List[SearchResultItem]: A list of search results including ID, name, type, and category.
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