import asyncio
from concurrent.futures import ProcessPoolExecutor
from contextlib import asynccontextmanager
import inspect
import os
from fastapi import APIRouter, FastAPI, HTTPException, Query
from fastapi.concurrency import run_in_threadpool
from pydantic import BaseModel, Field
from typing import List, Tuple, Dict, Any
import time
import math
import json
import numpy as np
from astropy.coordinates import SkyCoord, EarthLocation, AltAz
from astropy.time import Time
import astropy.units as u
from typing import List, Tuple
from services.astro_service.astro_service import AstroService
from core.logging import get_logger, setup_global_logging
import uvicorn
from api.sidereal_catalog import router as sidereal_catalog_router



setup_global_logging()

API_BASE_PATH="/api"

CATALOG_FILE="data/catalog.pkl"

CONSTELLATION_IN_FILE= "data/constellationship.fab"
CONSTELLATION_OUT_FILE= "data/constellationship.json"

@asynccontextmanager
async def lifespan(app:FastAPI):
    """
    App lifespan with async context manager
    """

    LOG = get_logger("Ephem API")

    LOG.debug("Starting Sideris Ephemerides API...")

    try:
        app.state.logger=LOG

        if not os.path.isfile(CATALOG_FILE) or not os.path.isfile(CONSTELLATION_OUT_FILE):
            LOG.warning("Catalog files not found. Generating catalog...")

        t_0=time.time()
        await AstroService.get_instance(CATALOG_FILE, CONSTELLATION_IN_FILE, CONSTELLATION_OUT_FILE)
        t_1=time.time()
        delta_t=t_1-t_0
        LOG.debug(f"Catalog files generated in {delta_t:.2f} seconds!")  
    
        LOG.info(f"Service is running!")  
        yield
    except Exception as e:
        LOG.error(f"Error during lifespan: {e} \n {inspect.currentframe().f_code.co_name}")
        raise HTTPException(
            status_code=500,
            detail="Error during lifespan"
            ) from e
    
app=FastAPI(
    title="Sideris Ephemerides API",
    description="Documentation for Sideris Ephemerides API",
    lifespan=lifespan,
    docs_url=API_BASE_PATH+"/docs",
    redoc_url=API_BASE_PATH+"/redoc",
    openapi_url=API_BASE_PATH+"/openapi.json",
    swagger_ui_parameters={"defaultModelsExpandDepth": -1} # Hide the schemas section
)





api=APIRouter(prefix=API_BASE_PATH)






@api.get("")
def health():
    return {"status": "ok", "message": "Sideris Ephemerides API is running!"}


app.include_router(sidereal_catalog_router, prefix=API_BASE_PATH+"/sidereal", tags=["Sidereal Catalog"])
app.include_router(api)
if __name__=="__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8624, reload=True)