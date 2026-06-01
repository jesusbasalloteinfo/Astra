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

import os
from fastapi.staticfiles import StaticFiles
import uvicorn
from contextlib import asynccontextmanager
import inspect
from fastapi import APIRouter, FastAPI, HTTPException, Query
from pydantic import BaseModel, Field
from services.astro_service.astro_service import AstroService
from core.logging import get_logger, setup_global_logging
from api.sidereal_catalog import router as sidereal_catalog_router
from api.planetary_catalog import router as planetary_catalog_router
from api.search_catalog import router as search_catalog_router
from core.translations import load_translations


setup_global_logging()
DEBUG = os.getenv("USER_DEBUG", "False").lower() == "true"

API_BASE_PATH = ""

CATALOG_FILE = "data/sidereal_catalog.pkl"
CONST_CATALOG = "data/constellationship.json"

        

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manages the application lifespan events for Sideris.

    Handles the initialization of the AstroService singleton (loading catalogs 
    into memory) and the loading of localized translation files during startup.

    Args:
        app (FastAPI): The FastAPI application instance.

    Raises:
        HTTPException: If an error occurs during the catalog or translation loading.
    """

    LOG = get_logger("Ephem API")

    LOG.debug("Starting Sideris Ephemerides API...")

    try:
        app.state.logger = LOG

        await AstroService.get_instance(CATALOG_FILE, CONST_CATALOG)

        load_translations()

        LOG.info(f"Service is running!")  
        yield
    except Exception as e:
        LOG.error(f"Error during lifespan: {e} \n {inspect.currentframe().f_code.co_name}")

        load_translations()
        
        raise HTTPException(
            status_code=500,
            detail="Error during lifespan"
            ) from e
    
app = FastAPI(
    title="Sideris Ephemerides API",
    description="Documentation for Sideris Ephemerides API",
    lifespan=lifespan,
    docs_url=API_BASE_PATH + "/docs" if DEBUG else None,
    redoc_url=API_BASE_PATH + "/redoc" if DEBUG else None,
    openapi_url=API_BASE_PATH + "/openapi.json" if DEBUG else None,
    swagger_ui_parameters={"defaultModelsExpandDepth": -1} # Hide the schemas section
)




api = APIRouter(prefix=API_BASE_PATH)




@api.get("/")
def health():
    """Service health check endpoint.

    Returns:
        dict: A status message indicating the service is running.
    """
    return {"status": "ok", "message": "Sideris Ephemerides API is running!"}

app.include_router(search_catalog_router, prefix=API_BASE_PATH + "/search", tags=["Search Catalog"])
app.include_router(sidereal_catalog_router, prefix=API_BASE_PATH + "/sidereal", tags=["Sidereal Catalog"])
app.include_router(planetary_catalog_router, prefix=API_BASE_PATH + "/planetary", tags=["Planetary Catalog"])
app.include_router(api)

app.mount("/static", StaticFiles(directory="static"), name="static")
if __name__ == "__main__":
    uvicorn.run("sideris:app", host="127.0.0.1", port=8624, reload=True)