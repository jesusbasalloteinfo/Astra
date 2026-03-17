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

# ================================================================================
# API CONFIGURATION
# ================================================================================

setup_global_logging(file_path=f".tmp/log-{datetime.now(timezone.utc)}.log")


API_BASE_PATH="/api"


@asynccontextmanager
async def lifespan(app:FastAPI):
    """
    App lifespan with async context manager
    """

    LOG = get_logger("ASTRA API")

    LOG.debug("Starting Astra API...")

    try:
        app.state.logger=LOG
        yield
    except Exception as e:
        LOG.error(f"Error during lifespan: {e}", details=inspect.currentframe().f_code.co_name)
        raise HTTPException(
            status_code=500,
            detail="Error during lifespan"
            ) from e
    
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
async def dummy_login(data:DummyAuth, response:Response):
    """ Set an HTTP-only dummy cookie with a token"""
    response.set_cookie(key="auth", 
                        value=data.token,
                        httponly=True, 
                        secure=True,
                        samesite="lax",
                        max_age=72000,
                        path="/",
                        domain=None)
    return {"status":"ok", "message": "Successful dummy Login!"}



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
async def dummy_check(auth: Optional[str] = Cookie(None)):
    """ Check a dummy session"""
    if not auth:
        raise HTTPException(401, "Not authenticated!")
    return CheckResponse(status="ok", message=auth)



@api.post("/logout")
async def dummy_logout(response:Response):
    """ Delete an HTTP-only dummy cookie"""
    response.delete_cookie(
        key="auth",
        path="/"
    )
    return {"status":"ok", "message": "Successful dummy Logout!"}

app.include_router(api)




