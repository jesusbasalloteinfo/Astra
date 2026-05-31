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

API_BASE_PATH=""

CATALOG_FILE="data/sidereal_catalog.pkl"
CONST_CATALOG= "data/constellationship.json"

        

@asynccontextmanager
async def lifespan(app:FastAPI):
    """
    App lifespan with async context manager
    """

    LOG = get_logger("Ephem API")

    LOG.debug("Starting Sideris Ephemerides API...")

    try:
        app.state.logger=LOG

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
    
app=FastAPI(
    title="Sideris Ephemerides API",
    description="Documentation for Sideris Ephemerides API",
    lifespan=lifespan,
    docs_url=API_BASE_PATH+"/docs" if DEBUG else None,
    redoc_url=API_BASE_PATH+"/redoc" if DEBUG else None,
    openapi_url=API_BASE_PATH+"/openapi.json" if DEBUG else None,
    swagger_ui_parameters={"defaultModelsExpandDepth": -1} # Hide the schemas section
)




api = APIRouter(prefix=API_BASE_PATH)




@api.get("/")
def health():
    return {"status": "ok", "message": "Sideris Ephemerides API is running!"}

app.include_router(search_catalog_router, prefix=API_BASE_PATH+"/search", tags=["Search Catalog"])
app.include_router(sidereal_catalog_router, prefix=API_BASE_PATH+"/sidereal", tags=["Sidereal Catalog"])
app.include_router(planetary_catalog_router, prefix=API_BASE_PATH+"/planetary", tags=["Planetary Catalog"])
app.include_router(api)

app.mount("/static", StaticFiles(directory="static"), name="static")
if __name__=="__main__":
    uvicorn.run("sideris:app", host="127.0.0.1", port=8624, reload=True)