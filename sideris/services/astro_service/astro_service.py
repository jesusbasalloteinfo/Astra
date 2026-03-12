import asyncio
from datetime import datetime
import json
import os
import pickle
import time
from typing import List, Optional, Tuple

from models.ResponseSchemas import SiderealObjectDataResponse, StarDataResponse, DSODataResponse
from services.astro_service.engines.SiderealEngine import SiderealEngine
from models.CatalogSchemas import ConstellationCatalog

class AstroService:
    """Singleton class for astronomical calculations and data retrieval."""

    _instance: Optional['AstroService'] = None
    _lock = asyncio.Lock()  # Avoid race conditions

    def __init__(self, sidereal_path: str, constellation_path: str):
        self._sidereal_path = sidereal_path
        self._constellation_path = constellation_path
        self._initialized = True
        self._sidereal_catalog=None

    @classmethod
    async def get_instance(cls, *args, **kwargs) -> 'AstroService':
        if cls._instance is None:
            async with cls._lock:
                if cls._instance is None:
                    instance = cls(*args, **kwargs)
                    await instance._setup_catalog()
                    cls._instance = instance
        return cls._instance
    
    async def _setup_catalog(self):
        if os.path.isfile(self._sidereal_path) and os.path.isfile(self._constellation_path):
            get_logger("Astroservice").debug("Loading from Pickle...")
            with open(self._sidereal_path, 'rb') as f:
                self._sidereal_catalog = pickle.load(f)
            with open(self._constellation_path, 'r', encoding='utf-8') as f:
                data=json.load(f)
                self._constellation_catalog=ConstellationCatalog.model_validate(data)
            get_logger("Astroservice").debug("Loaded from Pickle successfully!")
        else:
            raise FileNotFoundError("Catalogs have not been found!")
        
        self._sidereal_engine:SiderealEngine = SiderealEngine(self._sidereal_catalog, self._constellation_catalog)

        self._catalog_index = {}
        for star in self._sidereal_catalog.data.stars:
            self._catalog_index[star.id] = star
        for dso in self._sidereal_catalog.data.deep_sky:
            self._catalog_index[dso.id] = dso
        
    
    # Sidereal Object Handling

    def get_sidereal_positions(self, target_time: datetime, lat: float, lon: float, elev: float, ttl:float=120.0) -> List[Tuple]:
        """Calculate positions for stars and deep-sky objects."""
        return self._sidereal_engine.get_sky_movement(target_time, lat, lon, elev, ttl)
    

    
    def get_sidereal_object(self, target_obj:str, target_time: datetime, lat: float, lon: float, elev: float) -> SiderealObjectDataResponse:
        """Calculate and return information about an object."""
        catalog_obj = self._catalog_index.get(target_obj)
        if not catalog_obj:
            raise ValueError(f"Object {target_obj} not found!")
        movement_info = self._sidereal_engine.get_object_movement(target_obj, target_time, lat, lon, elev)
        
        combined_dict = {**catalog_obj.model_dump(), **movement_info.model_dump()}

        if catalog_obj.type == "star":
            return StarDataResponse(**combined_dict)
        else:
            return DSODataResponse(**combined_dict)


    
    def calculate_solar_system_positions(self, body_name: str, timestamp: float) -> dict:
        """Calculate positions for solar system bodies."""
        return {
            "body": body_name,
            "timestamp": timestamp,
            "ra": 0.0,
            "dec": 0.0,
            "distance": 0.0
        }
    
    def get_objects_metadata(self, object_id: str) -> dict:
        """Retrieve metadata for astronomical objects."""
        return {
            "object_id": object_id,
            "name": "",
            "type": "",
            "magnitude": 0.0,
            "catalog_reference": ""
        }