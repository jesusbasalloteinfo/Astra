import asyncio
from datetime import datetime
import json
import os
import pickle
import time
from typing import List, Optional, Tuple

from models.api.sidereal import SiderealObjectMetadata, StarDataResponse, DSODataResponse, SiderealObjectDataResponse, ConstellationMetadata
from models.api.common import MetadataCatalogPayload, SyncPayload
from services.astro_service.engines.SiderealEngine import SiderealEngine
from services.astro_service.engines.PlanetaryEngine import PlanetaryEngine
from models.catalog.constellations import ConstellationCatalog
from models.catalog.sidereal import Star
from core.logging import get_logger
from models.catalog.planetary import PlanetaryObject

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
        self._planetary_engine:PlanetaryEngine = PlanetaryEngine()

        self._catalog_index = {}
        for star in self._sidereal_catalog.data.stars:
            self._catalog_index[star.id] = star
        for dso in self._sidereal_catalog.data.deep_sky:
            self._catalog_index[dso.id] = dso
        
        self._build_sidereal_metadata_cache()

    def _build_sidereal_metadata_cache(self):
        """Construct the static metadata catalog in startup"""
        get_logger("Astroservice").debug("Building frontend metadata cache...")
        ui_objects = {}

        for star in self._sidereal_catalog.data.stars:
            ui_objects[star.id] = SiderealObjectMetadata(
                id=star.id,
                name=star.name if star.name else star.id,
                type=star.type,
                common_names=star.common_names,
                catalog_names=star.catalog_names,
                constellation=star.constellation,
                mag=star.mag,
                abs_mag=star.abs_mag,
                b_v=star.b_v,
                luminosity=getattr(star, 'luminosity', None),
                dist=star.dist_ly,
                spectral_type=getattr(star, 'spectral_type', None),
                size_arcmin=None
            )

        for ds in self._sidereal_catalog.data.deep_sky:
            ui_objects[ds.id] = SiderealObjectMetadata(
                id=ds.id,
                name=ds.name if ds.name else ds.id,
                type=ds.type,
                common_names=ds.common_names,
                catalog_names=ds.catalog_names,
                constellation=ds.constellation,
                mag=ds.mag,
                abs_mag=None,
                b_v=None,
                luminosity=None,
                dist=None,
                spectral_type=None,
                size_arcmin=ds.size_arcmin
            )

        ui_constellations = []
        for const in self._constellation_catalog.constellations:
            ui_constellations.append(ConstellationMetadata(
                abbr=const.abbr,
                name=const.full_name,
                latin=const.full_name,
                stars_ids=[str(sid) for sid in const.stars_ids],
                lines_indices=const.lines_indices
            ))

        self._sidereal_metadata = MetadataCatalogPayload(
            version="1.0",
            total=len(ui_objects),
            data=ui_objects
        )
        self._constellations_metadata = MetadataCatalogPayload(
            version="1.0",
            total=len(ui_constellations),
            data=ui_constellations
        )
        get_logger("Astroservice").debug("Metadata cache ready!")
        
    
    # Sidereal Object Handling
    def get_sidereal_metadata(self) -> MetadataCatalogPayload:
        """Return the cached sidereal metadata."""
        return self._sidereal_metadata
    
    def get_constellations_metadata(self) -> MetadataCatalogPayload:
        """Return the cached constellations metadata."""
        return self._constellations_metadata
    
    def get_sidereal_positions(self, target_time: datetime, lat: float, lon: float, elev: float, ttl:float=120.0) -> SyncPayload:
        """Calculate positions for stars and deep-sky objects."""
        return self._sidereal_engine.get_sky_movement(target_time, lat, lon, elev, ttl)
    
    
    def get_sidereal_object(self, target_obj:str, target_time: datetime, lat: float, lon: float, elev: float) -> SiderealObjectDataResponse:
        """Calculate and return information about an object."""
        catalog_obj = self._catalog_index.get(target_obj)
        if not catalog_obj:
            raise ValueError(f"Object {target_obj} not found!")
        
        movement_info = self._sidereal_engine.get_object_movement(target_obj, target_time, lat, lon, elev)
        
        combined_dict = {**catalog_obj.model_dump(), **movement_info.model_dump()}

        if type(catalog_obj) == Star:
            return StarDataResponse(**combined_dict)
        else:
            return DSODataResponse(**combined_dict)
        
        

    # ═════════════════════════════════════════════
    # PLANETARY METHODS
    # ═════════════════════════════════════════════


    def get_planetary_metadata(self, utc_time: datetime, lat: float, lon: float, elev_m: float = 0.0, ttl:float=120.0):
        """Return the cached sidereal metadata"""
        return self._planetary_engine.get_metadata(utc_time, lat, lon, elev_m, ttl)
    

    def get_planetary_positions(self, target_time: datetime, lat: float, lon: float, elev: float, ttl:float=120.0) -> SyncPayload:
        """Calculate positions for all planetary objects"""
        return self._planetary_engine.get_sky_movement(target_time, lat, lon, elev, ttl)
    
    
    def get_planetary_object(self, target_obj:str, target_time: datetime, lat: float, lon: float, elev: float, ttl:float=120.0):
        """Calculate and return information about an object"""
        
        try:
            _ = PlanetaryObject[target_obj.upper()]
        except KeyError:
            raise ValueError(f"Object {target_obj} not found!")
            
        return self._planetary_engine.get_object_movement(target_obj, target_time, lat, lon, elev, ttl)
        