from datetime import datetime, timedelta, timezone

import numpy as np
from astropy.coordinates import SkyCoord, EarthLocation, AltAz
from astropy.time import Time
from astroplan import Observer, TargetAlwaysUpWarning, TargetNeverUpWarning
import astropy.units as u
from typing import List, Tuple
from services.astro_service.engines.BaseEngine import BaseEngine
from models.CatalogSchemas import *
from models.ResponseSchemas import EphemerisMovementData, SyncPayload
from core.logging import get_logger

class SiderealEngine(BaseEngine):
    def __init__(self, catalog:AstronomicalCatalog, constellations:ConstellationCatalog):
        """
        Starts the engine with the catalog data
        """
        super().__init__()
        get_logger("SiderealEngine").debug("Starting Sidereal Engine...")
        ras, decs, pm_ras, pm_decs, self.ids = [], [], [], [], []
        self._sidereal_catalog:AstronomicalCatalog=catalog
        self._constellations:ConstellationCatalog=constellations
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
    

    def get_sky_movement(self, t0_dt: datetime, lat: float, lon: float, elev_m: float = 0.0, ttl:float=120.0) -> SyncPayload:
        """
        Calculates the sky and its movement for a time and location
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
        delta_az = (az1 - az0 + 180) % 360 - 180
        d_az = delta_az / ttl
        d_az = np.where(alt0 > 89.5, 0.0, d_az) # Zenit filter for high stars

        return SyncPayload(
            target_time=t0_dt,
            ttl=ttl,
            updates=list(zip(self.ids, alt0, az0, d_alt, d_az))
        )
  

    def get_object_movement(self, target_id:str, target_time: datetime, lat: float, lon: float, elev_m: float = 0.0):
        
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

        try:
            next_transit = observer.target_meridian_transit_time(time_t0, target_coord, which='next').datetime.replace(tzinfo=timezone.utc)
            next_rise = observer.target_rise_time(time_t0, target_coord, which='next').datetime.replace(tzinfo=timezone.utc)
            next_set = observer.target_set_time(time_t0, target_coord, which='next').datetime.replace(tzinfo=timezone.utc)
            is_circumpolar = False
            never_rises = False
        except TargetAlwaysUpWarning:
            is_circumpolar = True
            next_rise, next_set = None, None
        except TargetNeverUpWarning:
            never_rises = True
            next_rise, next_set = None, None
        
        return EphemerisMovementData(
            alt= current_alt,
            az = current_az,
            next_rise= next_rise,
            next_transit=next_transit,
            next_set=next_set,
            is_circumpolar=is_circumpolar,
            never_rises=never_rises
        )
        