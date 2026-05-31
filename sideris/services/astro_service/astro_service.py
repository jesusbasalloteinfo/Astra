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
    """Singleton class for astronomical calculations and data retrieval.

    This service coordinates the loading of astronomical catalogs, maintains
    in-memory indexes for fast searching, and delegates complex calculations
    to specialized sidereal and planetary engines.
    """

    _instance: Optional['AstroService'] = None
    _lock = asyncio.Lock()  # Avoid race conditions

    def __init__(self, sidereal_path: str, constellation_path: str):
        """Initialize the AstroService.

        Args:
            sidereal_path (str): File path to the pickled sidereal catalog.
            constellation_path (str): File path to the constellations JSON catalog.
        """
        self._sidereal_path = sidereal_path
        self._constellation_path = constellation_path
        self._initialized = True
        self._sidereal_catalog = None

    @classmethod
    async def get_instance(cls, *args, **kwargs) -> 'AstroService':
        """Retrieves or creates the singleton instance of AstroService.

        Args:
            *args: Positional arguments for initialization.
            **kwargs: Keyword arguments for initialization.

        Returns:
            AstroService: The singleton service instance.
        """
        if cls._instance is None:
            async with cls._lock:
                if cls._instance is None:
                    instance = cls(*args, **kwargs)
                    await instance._setup_catalog()
                    cls._instance = instance
        return cls._instance
    
    async def _setup_catalog(self):
        """Loads catalogs from the file system and initializes calculation engines.

        Raises:
            FileNotFoundError: If the required catalog files are missing.
        """
        if os.path.isfile(self._sidereal_path) and os.path.isfile(self._constellation_path):
            get_logger("Astroservice").debug("Loading from Pickle...")
            with open(self._sidereal_path, 'rb') as f:
                self._sidereal_catalog = pickle.load(f)
            with open(self._constellation_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self._constellation_catalog = ConstellationCatalog.model_validate(data)
            get_logger("Astroservice").debug("Loaded from Pickle successfully!")
        else:
            raise FileNotFoundError("Catalogs have not been found!")
        
        self._sidereal_engine: SiderealEngine = SiderealEngine(self._sidereal_catalog, self._constellation_catalog)
        self._planetary_engine: PlanetaryEngine = PlanetaryEngine()

        self._catalog_index = {}
        for star in self._sidereal_catalog.data.stars:
            self._catalog_index[star.id] = star
        for dso in self._sidereal_catalog.data.deep_sky:
            self._catalog_index[dso.id] = dso
        
        self._build_sidereal_metadata_cache()

    def _build_sidereal_metadata_cache(self):
        """Constructs the static metadata cache for API responses.

        Processes the loaded catalogs to create a ready-to-serve representation
        of stars, DSOs, and constellations, including J2000 coordinates.
        """
        get_logger("Astroservice").debug("Building frontend metadata cache...")
        ui_objects = {}

        for star in self._sidereal_catalog.data.stars:
            ui_objects[star.id] = SiderealObjectMetadata(
                id=star.id,
                name=star.name if star.name else star.id,
                type="sidereal",
                category=star.category,
                common_names=star.common_names,
                catalog_names=star.catalog_names,
                constellation=star.constellation,
                ra_j2000=star.ra_j2000,
                dec_j2000=star.dec_j2000,
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
                type="sidereal",
                category=ds.category,
                common_names=ds.common_names,
                catalog_names=ds.catalog_names,
                constellation=ds.constellation,
                ra_j2000=ds.ra_j2000,
                dec_j2000=ds.dec_j2000,
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
        self._build_search_index()
        get_logger("Astroservice").debug("Metadata cache & Search index ready!")
        
    def _build_search_index(self):
        """Creates a flattened search index for fast text matching.

        Generates lowercased, space-removed keys for all object names (common, 
        catalog, latin, etc.) to allow for fuzzy-like fast memory search.
        """
        self._search_index = []

        # Sidereal indexing
        for obj_id, data in self._sidereal_metadata.data.items():
            possible_names = [data.name] + (data.common_names or []) + (data.catalog_names or []) + [obj_id]
            res = {"id": obj_id, "name": data.name, "type": "sidereal", "category": data.category or 'star', "mag": data.mag}

            for name in possible_names:
                if name:
                    search_key = str(name).lower().replace(" ", "")
                    self._search_index.append({"key": search_key, "result": res})

        # Constellation indexing
        for const in self._constellations_metadata.data:
            possible_names = [const.name, const.latin, const.abbr]
            res = {"id": const.abbr, "name": const.name, "type": 'constellation', "category": 'constellation', "mag": None}            
            for name in possible_names:
                if name:
                    search_key = str(name).lower().replace(" ", "")
                    self._search_index.append({"key": search_key, "result": res})
    
    def search_objects(self, query: str, limit: int = 10, planetary_translations: dict = None) -> list:
        """Performs a ranked search across all astronomical catalogs.

        Uses the pre-built search index for sidereal objects and constellations, 
        and dynamically injects planetary objects using provided translations.

        Args:
            query (str): The search string.
            limit (int): Maximum number of results. Defaults to 10.
            planetary_translations (dict): Localization dictionary for planets.

        Returns:
            list: A ranked list of search result dictionaries.
        """
        clean_query = query.lower().replace(" ", "")
        if len(clean_query) < 2:
            return []

        matches = {}

        # 1. Search in static index (Sidereal + Constellations)
        for item in self._search_index:
            if clean_query in item["key"]:
                score = 1 if item["key"] == clean_query else (2 if item["key"].startswith(clean_query) else 3)
                obj_id = item["result"]["id"]
                
                if obj_id not in matches or score < matches[obj_id]["score"]:
                    matches[obj_id] = {"result": item["result"].copy(), "score": score}

        # 2. Search in planetary
        planetary_ids = ["sun", "moon", "mercury", "venus", "mars", "jupiter", "saturn", "uranus", "neptune", "pluto"]
        
        for p_id in planetary_ids:
            trans = planetary_translations.get(p_id) if planetary_translations else None
            name = trans.name if trans else p_id.capitalize()
            common = trans.common_names if trans else []
            
            possible_names = [name, p_id] + common
            res = {"id": p_id, "name": name, "type": "planetary", "mag": -99.0} 
            
            for p_name in possible_names:
                if p_name:
                    key = str(p_name).lower().replace(" ", "")
                    if clean_query in key:
                        score = 1 if key == clean_query else (2 if key.startswith(clean_query) else 3)
                        if p_id not in matches or score < matches[p_id]["score"]:
                            # Assume moon for "moon" and planet for the rest in search
                            category = "moon" if p_id == "moon" else "planet"
                            res = {"id": p_id, "name": name, "type": "planetary", "category": category, "mag": -99.0} 
                            matches[p_id] = {"result": res, "score": score}

        # Sort by Score and then by magnitude
        results = list(matches.values())
        results.sort(key=lambda x: (
            x["score"],
            x["result"]["mag"] if x["result"]["mag"] is not None else 99.0
        ))

        for res in results:
            del res["result"]["mag"]

        return [item["result"] for item in results[:limit]]
    
    # Sidereal Object Handling
    def get_sidereal_metadata(self) -> MetadataCatalogPayload:
        """Retrieves the cached sidereal metadata.

        Returns:
            MetadataCatalogPayload: The full sidereal catalog metadata.
        """
        return self._sidereal_metadata
    
    def get_constellations_metadata(self) -> MetadataCatalogPayload:
        """Retrieves the cached constellations metadata.

        Returns:
            MetadataCatalogPayload: The full constellations catalog metadata.
        """
        return self._constellations_metadata
    
    def get_sidereal_positions(self, target_time: datetime, lat: float, lon: float, elev: float, ttl: float = 120.0) -> SyncPayload:
        """Calculates current Altitude/Azimuth for all sidereal objects.

        Args:
            target_time (datetime): Target time for the calculation.
            lat (float): Latitude of the observer.
            lon (float): Longitude of the observer.
            elev (float): Elevation of the observer.
            ttl (float): Movement window in seconds. Defaults to 120.0.

        Returns:
            SyncPayload: The computed positions for stars and DSOs.
        """
        return self._sidereal_engine.get_sky_movement(target_time, lat, lon, elev, ttl)
    
    
    def get_sidereal_object(self, target_obj: str, target_time: datetime, lat: float, lon: float, elev: float) -> SiderealObjectDataResponse:
        """Retrieves ephemeris and physical data for a specific sidereal object.

        Args:
            target_obj (str): The ID of the object.
            target_time (datetime): Target time for the calculation.
            lat (float): Latitude of the observer.
            lon (float): Longitude of the observer.
            elev (float): Elevation of the observer.

        Returns:
            SiderealObjectDataResponse: Combined catalog and real-time movement data.

        Raises:
            ValueError: If the object is not found in the index.
        """
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


    def get_planetary_metadata(self, utc_time: datetime, lat: float, lon: float, elev_m: float = 0.0, ttl: float = 120.0):
        """Retrieves the current metadata for all planetary bodies.

        Args:
            utc_time (datetime): Target time.
            lat (float): Latitude.
            lon (float): Longitude.
            elev_m (float): Elevation in meters. Defaults to 0.0.
            ttl (float): Movement window. Defaults to 120.0.

        Returns:
            MetadataCatalogPayload: Metadata including observability for planets.
        """
        return self._planetary_engine.get_metadata(utc_time, lat, lon, elev_m, ttl)
    

    def get_planetary_positions(self, target_time: datetime, lat: float, lon: float, elev: float, ttl: float = 120.0) -> SyncPayload:
        """Calculates current Altitude/Azimuth for all planetary objects.

        Args:
            target_time (datetime): Target time.
            lat (float): Latitude.
            lon (float): Longitude.
            elev (float): Elevation.
            ttl (float): Movement window. Defaults to 120.0.

        Returns:
            SyncPayload: Computed planetary positions.
        """
        return self._planetary_engine.get_sky_movement(target_time, lat, lon, elev, ttl)
    
    
    def get_planetary_object(self, target_obj: str, target_time: datetime, lat: float, lon: float, elev: float, ttl: float = 120.0):
        """Retrieves ephemeris and physical data for a specific planetary object.

        Args:
            target_obj (str): The name/id of the planetary object.
            target_time (datetime): Target time.
            lat (float): Latitude.
            lon (float): Longitude.
            elev (float): Elevation.
            ttl (float): Movement window. Defaults to 120.0.

        Returns:
            PlanetaryObjectDataResponse: Computed data for the planet.

        Raises:
            ValueError: If the object is not a valid planetary body.
        """
        try:
            _ = PlanetaryObject[target_obj.upper()]
        except KeyError:
            raise ValueError(f"Object {target_obj} not found!")
            
        return self._planetary_engine.get_object_movement(target_obj, target_time, lat, lon, elev, ttl)
        