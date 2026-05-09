import os
import asyncio
import inspect
from typing import Optional
from fastapi import Cookie, FastAPI, APIRouter, HTTPException, Header, Request, Depends, Response
from pydantic import BaseModel
from starlette.middleware.base import BaseHTTPMiddleware
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime, timezone
from contextlib import asynccontextmanager
from core.logging_utils import get_logger, setup_global_logging
from core.MongoDBConnector import MongoDBConnector, db_connector
from services.db.UserService import UserService
from core.dependencies import get_request_user
from api.users import router as users_router
from api.observations import router as obs_router
from api.devices import router as devices_router
from api.chat import router as chat_router

# ================================================================================
# API CONFIGURATION
# ================================================================================

setup_global_logging(file_path=f".tmp/log-{datetime.now(timezone.utc)}.log")


API_BASE_PATH="/api"

async def init_db():
    await db_connector.connect()

    user_service = UserService()
    await user_service.repo.setup_indexes() 


@asynccontextmanager
async def lifespan(app:FastAPI):
    """
    App lifespan with async context manager
    """

    LOG = get_logger("ASTRA API")

    LOG.debug("Starting Astra API...")

    try:
        app.state.logger=LOG
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
    title="Astra Backend API",
    description="Documentation for the Astra Backend API",
    lifespan=lifespan,
    docs_url=API_BASE_PATH+"/docs",
    redoc_url=API_BASE_PATH+"/redoc",
    openapi_url=API_BASE_PATH+"/openapi.json",
    swagger_ui_parameters={"defaultModelsExpandDepth": -1} # Hide the schemas section
)

# ----------------------------------
# Middleware configuration & routers
# --------------------------------------------------------------------------------

api=APIRouter(prefix=API_BASE_PATH)



# ================================================================================
# MAIN ENDPOINTS
# ================================================================================

@api.get("")
def health():
    return {"status": "ok", "message": "Astra API is running!"}




# TODO Temporal dummy token auth. Later we will use a separate Auth Handler
# --------------------------------------------------------------------------------

class DummyAuth(BaseModel):
    token:str

@api.post("/login")
async def dummy_login(data: DummyAuth):
    """ 
    Login + create a dummy user
    """
    user_service = UserService()
    try:
        await user_service.ensure_user(data.token)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database Error: {str(e)}")

    return {
        "access_token": data.token,
        "token_type": "bearer"
    }


class CheckResponse(BaseModel):
    status: str
    message: str

@api.get("/session",
        responses={
            200: {"description": "User has a valid session"},
            401: {"description": "User is not authenticated"}
        },
        response_model=CheckResponse
    )
async def dummy_check(user: str = Depends(get_request_user)):
    """ Check a dummy session"""
    return CheckResponse(status="ok", message=f"Authorised as: {user}")


@api.post("/logout")
async def dummy_logout():
    """ Delete a session (dummy)"""
    return {"status":"ok", "message": "Successful dummy Logout!"}


app.include_router(api, tags=["Main API"])
app.include_router(users_router, prefix=API_BASE_PATH+"/users", tags=["User Management"])
app.include_router(devices_router, prefix=API_BASE_PATH+"/devices", tags=["Device management"])
app.include_router(obs_router, prefix=API_BASE_PATH+"/observations", tags=["Observations"])
app.include_router(chat_router, prefix=API_BASE_PATH+"/chat", tags=["Chat"])





