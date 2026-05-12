import os
import asyncio
import inspect
from typing import Optional
from fastapi import FastAPI, APIRouter, HTTPException, Depends
from datetime import datetime, timezone
from contextlib import asynccontextmanager
from core.logging_utils import get_logger, setup_global_logging
from core.MongoDBConnector import db_connector
from repositories.auth import AuthRepository
from core.security import generate_keys_if_not_exists
from api.auth import router as auth_router

# ================================================================================
# API CONFIGURATION
# ================================================================================

setup_global_logging(file_path=f".tmp/log-{datetime.now(timezone.utc)}.log")

API_BASE_PATH="/api/auth"

async def init_db():
    await db_connector.connect()
    auth_repo = AuthRepository()
    await auth_repo.setup_indexes() 

@asynccontextmanager
async def lifespan(app:FastAPI):
    """
    App lifespan with async context manager
    """
    LOG = get_logger("ASTRA AUTH")
    LOG.debug("Starting Astra Auth Service...")

    try:
        app.state.logger=LOG
        
        # Initialize keys
        generate_keys_if_not_exists()
        
        await init_db()
        yield
    except Exception as e:
        LOG.error(f"Error during lifespan: {e}", details=inspect.currentframe().f_code.co_name)
        raise HTTPException(
            status_code=500,
            detail="Error during lifespan"
            ) from e
    finally:
        await db_connector.disconnect()
    
app=FastAPI(
    title="Astra Auth API",
    description="Identity and Authentication Service for Astra",
    lifespan=lifespan,
    docs_url=API_BASE_PATH+"/docs",
    redoc_url=API_BASE_PATH+"/redoc",
    openapi_url=API_BASE_PATH+"/openapi.json",
    swagger_ui_parameters={"defaultModelsExpandDepth": -1}
)

# ----------------------------------
# Routers configuration
# --------------------------------------------------------------------------------

api=APIRouter(prefix=API_BASE_PATH)

@api.get("/health")
def health():
    return {"status": "ok", "message": "Astra Auth Service is running!"}

app.include_router(api, tags=["Main"])
app.include_router(auth_router, prefix=API_BASE_PATH, tags=["Authentication"])
