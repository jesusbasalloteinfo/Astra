from datetime import datetime, timedelta, timezone

import numpy as np
from astropy.coordinates import SkyCoord, EarthLocation, AltAz
from astropy.time import Time
from astroplan import Observer, TargetAlwaysUpWarning, TargetNeverUpWarning
import astropy.units as u
from typing import List, Tuple
from services.astro_service.engines.BaseEngine import BaseEngine
from models.catalog.sidereal import AstronomicalCatalog, Star, DeepSky
from models.catalog.constellations import ConstellationCatalog
from models.api.sidereal import EphemerisMovementData
from models.api.common import SyncPayload
from core.logging import get_logger

class SiderealEngine(BaseEngine):
    """Engine for calculating positions of sidereal objects (stars and DSOs).

    Uses Astropy to perform bulk transformations of catalog coordinates into 
    horizontal AltAz coordinates for synchronization, and Astroplan for 
    high-precision rise/set/transit events.
    """

    def __init__(self, catalog: AstronomicalCatalog, constellations: ConstellationCatalog):
        """Initialize the SiderealEngine with catalog data.

        Extracts positions and proper motions from the catalog and creates a 
        cached SkyCoord object for fast vector-based transformations.

        Args:
            catalog (AstronomicalCatalog): The astronomical catalog containing stars and DSOs.
            constellations (ConstellationCatalog): The catalog of constellation definitions.
        """
        super().__init__()
        get_logger("SiderealEngine").debug("Starting Sidereal Engine...")
        ras, decs, pm_ras, pm_decs, self.ids = [], [], [], [], []
        self._sidereal_catalog: AstronomicalCatalog = catalog
        self._constellations: ConstellationCatalog = constellations
        
        # Extract Stars
        for star in catalog.data.stars:
            self.ids.append(star.id)
            ras.append(star.ra_j2000)
            decs.append(star.dec_j2000)
            pm_ras.append(star.pmra_mas)
            pm_decs.append(star.pmdec_mas)

        # Extract Deep Sky Objects (DSO)
        for ds in catalog.data.deep_sky:
            self.ids.append(ds.id)
            ras.append(ds.ra_j2000)
            decs.append(ds.dec_j2000)
            pm_ras.append(0.0) 
            pm_decs.append(0.0)

        # Id mapping with the object list position
        self._id_to_idx = {obj_id: i for i, obj_id in enumerate(self.ids)}

        # Cached SkyCoords object
        self.coords = SkyCoord(
            ra=ras * u.hourangle, 
            dec=decs * u.deg,
            pm_ra_cosdec=pm_ras * u.mas/u.yr,
            pm_dec=pm_decs * u.mas/u.yr,
            frame='icrs',
            obstime=Time('J2000')
        )
        get_logger("SiderealEngine").info(f"Sidereal engine started: Loaded {len(self.ids)} objects.")
    

    def get_sky_movement(self, t0_dt: datetime, lat: float, lon: float, elev_m: float = 0.0, ttl: float = 120.0) -> SyncPayload:
        """Calculates current Altitude/Azimuth and drifts for all sidereal objects.

        Performs vector-based coordinate transformations for the entire catalog 
        at once to compute real-time positions and velocities.

        Args:
            t0_dt (datetime): Target UTC time.
            lat (float): Observer latitude.
            lon (float): Observer longitude.
            elev_m (float): Observer elevation in meters. Defaults to 0.0.
            ttl (float): Movement window in seconds for drift calculation. Defaults to 120.0.

        Returns:
            SyncPayload: Collection of computed horizontal positions and drifts.
        """
        obs_loc = EarthLocation(lat=lat * u.deg, lon=lon * u.deg, height=elev_m * u.m)
        
        time_t0 = Time(t0_dt)
        time_t1 = Time(t0_dt + timedelta(seconds=ttl))

        altaz_t0 = self.coords.transform_to(AltAz(obstime=time_t0, location=obs_loc))
        altaz_t1 = self.coords.transform_to(AltAz(obstime=time_t1, location=obs_loc))

        alt0 = altaz_t0.alt.degree
        az0 = altaz_t0.az.degree
        alt1 = altaz_t1.alt.degree
        az1 = altaz_t1.az.degree

        d_alt = (alt1 - alt0) / ttl
        d_az = self._circular_diff(az1, az0) / ttl
        d_az = np.where(alt0 > 89.5, 0.0, d_az) # Zenit filter for high stars

        return SyncPayload(
            target_time=t0_dt,
            ttl=ttl,
            updates=list(zip(self.ids, alt0, az0, d_alt, d_az))
        )
  

    def get_object_movement(self, target_id: str, target_time: datetime, lat: float, lon: float, elev_m: float = 0.0):
        """Calculates movement data and rise/set events for a specific object.

        Args:
            target_id (str): The identifier of the sidereal object.
            target_time (datetime): Target UTC time.
            lat (float): Observer latitude.
            lon (float): Observer longitude.
            elev_m (float): Observer elevation. Defaults to 0.0.

        Returns:
            EphemerisMovementData: Computed horizontal coordinates and visibility events.

        Raises:
            ValueError: If the object ID is not found in the catalog.
        """
        id = self._id_to_idx.get(target_id)
        if id is None:
            raise ValueError(f"Object {target_id} not found!")

        obs_loc = EarthLocation(lat=lat * u.deg, lon=lon * u.deg, height=elev_m * u.m)
        observer = Observer(location=obs_loc)
        time_t0 = Time(target_time)

        target_coord = self.coords[id]
        
        altaz = target_coord.transform_to(AltAz(obstime=time_t0, location=obs_loc))
        current_alt = altaz.alt.degree
        current_az = altaz.az.degree

        # Manual circumpolar / never rises check (robust)
        lat_deg = obs_loc.lat.degree
        dec_deg = target_coord.dec.degree
        
        is_circumpolar = False
        never_rises = False
        if lat_deg > 0: # North
            is_circumpolar = dec_deg > (90.0 - lat_deg)
            never_rises = dec_deg < (lat_deg - 90.0)
        else: # South
            is_circumpolar = dec_deg < (-90.0 - lat_deg)
            never_rises = dec_deg > (90.0 + lat_deg)

        def safe_get_datetime(time_obj):
            """Safely extracts a UTC datetime from an Astropy Time object."""
            if time_obj is None:
                return None
            try:
                # Time objects in astroplan might be masked arrays
                dt = time_obj.datetime
                if hasattr(dt, 'mask') and np.any(dt.mask):
                    return None
                if isinstance(dt, np.ndarray):
                    # If it's an array but not masked, take the first element if it's 0-d or 1-d
                    dt = dt.item() if dt.size == 1 else dt[0]
                
                return dt.replace(tzinfo=timezone.utc)
            except Exception:
                return None

        # Always calculate transit
        next_transit = safe_get_datetime(observer.target_meridian_transit_time(time_t0, target_coord, which='nearest'))
        
        next_rise = None
        next_set = None

        if not is_circumpolar and not never_rises:
            import warnings
            with warnings.catch_warnings():
                warnings.simplefilter("ignore", (TargetAlwaysUpWarning, TargetNeverUpWarning))
                next_rise = safe_get_datetime(observer.target_rise_time(time_t0, target_coord, which='nearest'))
                next_set = safe_get_datetime(observer.target_set_time(time_t0, target_coord, which='nearest'))
        
        return EphemerisMovementData(
            alt= current_alt,
            az = current_az,
            next_rise= next_rise,
            next_transit=next_transit,
            next_set=next_set,
            is_circumpolar=is_circumpolar,
            never_rises=never_rises
        )
        