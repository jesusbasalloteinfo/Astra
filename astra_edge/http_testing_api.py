from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict, List, Optional
from datetime import datetime
import asyncio
from api.IndiAPI import IndiAPI
from utils.CoordinateHandler import CoordinateTypes
from common.INDIModels import *
from contextlib import asynccontextmanager
from fastapi import FastAPI
import uvicorn


# Global instance of IndiAPI
indi_api = None

class Coordinate(BaseModel):
    ra: Optional[float] = None
    dec: Optional[float] = None
    alt: Optional[float] = None
    az: Optional[float] = None

class SlewRequest(BaseModel):
    coordinate: Coordinate
    input_type: CoordinateTypes = CoordinateTypes.EQUATORIAL_J2000
    mode: str = "TRACK"

class LocationRequest(BaseModel):
    lat: float
    lon: float

class TimeRequest(BaseModel):
    time: datetime

@asynccontextmanager
async def lifespan(app: FastAPI):
    global indi_api
    indi_api = IndiAPI()
    indi_api.update_location(42,2)
    await indi_api.start_indi_manager()
    
    yield  
    
    if indi_api:
        await indi_api.stop_indi_manager()

app = FastAPI(title="INDI test API", version="1.0.0", lifespan=lifespan)


@app.get("/")
async def root():
    return {"message": "INDI test API is running"}

@app.get("/devices")
async def get_devices():
    """Get all managed devices"""
    try:
        devices = await indi_api.get_devices()
        return devices
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/telescope/{telescope_name}/position")
async def get_telescope_position(telescope_name: str):
    """Get the current position of a telescope"""
    try:
        position = await indi_api.position_telescope(telescope_name)
        return position
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/telescope/{telescope_name}/slew")
async def slew_telescope(telescope_name: str, request: SlewRequest):
    """Slew a telescope to the specified coordinates"""
    try:
        # Convert Coordinate object to tuple
        if request.input_type == CoordinateTypes.HORIZONTAL:
            coord = (request.coordinate.alt, request.coordinate.az)
        else:
            coord = (request.coordinate.ra, request.coordinate.dec)
        
        await indi_api.slew_telescope(
            telescope_name=telescope_name,
            coord=coord,
            input_type=request.input_type,
            mode=request.mode
        )
        return {"message": f"Telescope {telescope_name} slewed successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/telescope/{telescope_name}/slew")
async def abord_slew_telescope(telescope_name: str):
    """Cancel the telescope movement"""
    try:
        position = await indi_api.abort_slew_telescope(telescope_name)
        return {"message": f"Telescope {telescope_name} slew aborted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/location")
async def update_location(location: LocationRequest):
    """Update the observer's location"""
    try:
        indi_api.update_location(location.lat, location.lon)
        return {"message": "Location updated successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/time")
async def update_time(time_request: TimeRequest):
    """Update the current time"""
    try:
        indi_api.update_time(time_request.time)
        return {"message": "Time updated successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/status")
async def get_status():
    """Get the status of the INDI API"""
    return {
        "status": "running",
        "location": indi_api._location if indi_api else None,
        "time": indi_api._time.now if indi_api else None
    }


if __name__=="__main__":
    uvicorn.run("http_api:app", host="0.0.0.0", port=9000, reload=True)