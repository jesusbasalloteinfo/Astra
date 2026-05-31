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
DEBUG = os.getenv("USER_DEBUG", "False").lower() == "true"

API_BASE_PATH="/api/auth"

async def init_db():
    """Initialize the MongoDB connection and setup required indexes.
    
    This function connects to the database using the global db_connector and
    ensures that the AuthRepository has its indexes (username, email) configured.
    """
    await db_connector.connect()
    auth_repo = AuthRepository()
    await auth_repo.setup_indexes() 

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage the application lifespan events.

    This async context manager handles the startup and shutdown phases of the
    FastAPI application, including key generation, database initialization,
    and connection teardown.

    Args:
        app (FastAPI): The FastAPI application instance.

    Raises:
        HTTPException: If an error occurs during the startup phase.
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
    docs_url=API_BASE_PATH+"/docs" if DEBUG else None,
    redoc_url=API_BASE_PATH+"/redoc" if DEBUG else None,
    openapi_url=API_BASE_PATH+"/openapi.json" if DEBUG else None,
    swagger_ui_parameters={"defaultModelsExpandDepth": -1}
)

# ----------------------------------
# Routers configuration
# --------------------------------------------------------------------------------

api=APIRouter(prefix=API_BASE_PATH)

@api.get("/health")
def health():
    """Service health check endpoint.

    Returns:
        dict: A status message indicating the service is running.
    """
    return {"status": "ok", "message": "Astra Auth Service is running!"}

app.include_router(api, tags=["Main"])
app.include_router(auth_router, prefix=API_BASE_PATH, tags=["Authentication"])
