from datetime import datetime, timedelta, timezone
import math
from skyfield.api import load, wgs84
from skyfield import almanac
from skyfield.magnitudelib import planetary_magnitude
from skyfield.trigonometry import position_angle_of
from typing import Dict, Literal, Optional, List, Union, Tuple
from models.ResponseSchemas import SyncPayload
from models.PlanetarySchemas import *
from services.astro_service.engines.BaseEngine import BaseEngine




class PlanetaryEngine(BaseEngine):

    PLANETARY_RADIUS = {    
        # Equatorial radii in kilometres
        PlanetaryObject.SUN: 695700.0,
        PlanetaryObject.MOON: 1737.1,
        PlanetaryObject.MERCURY: 2439.7,
        PlanetaryObject.VENUS: 6051.8,
        PlanetaryObject.EARTH: 6371.0,
        PlanetaryObject.MARS: 3389.5,
        PlanetaryObject.JUPITER: 71488.0,
        PlanetaryObject.SATURN: 60268.0,
        PlanetaryObject.URANUS: 25559.0,
        PlanetaryObject.NEPTUNE: 24764.0,
        PlanetaryObject.PLUTO: 1188.3
    }

    def __init__(self, bsp_file: str = 'de440.bsp'):
        print(f"[Engine] Loading ephemerides from {bsp_file}...")
        self._eph = load(bsp_file)
        self._ts = load.timescale()
        self._sun = self._eph[PlanetaryObject.SUN.value]
        self._earth = self._eph[PlanetaryObject.EARTH.value]
    
    # ═════════════════════════════════════════════
    # UTILITY METHODS
    # ═════════════════════════════════════════════

    def _get_angular_diameter(self, obj: PlanetaryObject, distance_km: float) -> float:
        """Calculates angular diameter in arcminutes."""
        radius_km = self.PLANETARY_RADIUS.get(obj)
        if not radius_km or distance_km <= 0:
            return 0.0
        
        # 2 * arctan(radius / distance) converted to degrees, then to arcminutes
        ang_diam_deg = math.degrees(2 * math.atan2(radius_km, distance_km))
        return round(ang_diam_deg * 60.0, 2)
    
    def _calculate_magnitude(self, obj: PlanetaryObject, astrometric, t_now) -> Optional[float]:
        """Calculates a planetary magnitude with the current time"""
        apparent = astrometric.apparent()
        dist = astrometric.distance().au
        sun = self._eph[PlanetaryObject.SUN.value]

        # SUN, MOON and PLUTO use a different formula
        if obj == PlanetaryObject.SUN:
            return round(-26.74 + 5 * math.log10(dist), 2)
        elif obj == PlanetaryObject.MOON:
            phase_angle = apparent.phase_angle(sun).degrees
            mag = -12.73 + 0.026 * phase_angle + (4e-9) * (phase_angle**4)
            return round(mag, 2)
        elif obj == PlanetaryObject.PLUTO:  
            H0 = -0.7
            G = 0.15
            pluto = self._eph[PlanetaryObject.PLUTO.value]
            sun_dist_au = pluto.at(t_now).observe(sun).distance().au

            phi = math.radians(apparent.phase_angle(sun).degrees)
            phi1 = math.exp(-3.33 * math.tan(phi / 2) ** 0.63)
            phi2 = math.exp(-1.87 * math.tan(phi / 2) ** 1.22)
            mag = H0 + 5 * math.log10(sun_dist_au * dist) - 2.5 * math.log10((1 - G) * phi1 + G * phi2)
            return round(mag, 2)
        else:
            try:
                mag_raw = planetary_magnitude(apparent)
                return round(float(mag_raw), 2)
            except Exception:
                return None

    def _calculate_movement(self, obj: PlanetaryObject, observer, t_now, ttl: float = 1.0
        ) -> Tuple[Tuple[float, float], Tuple[float, float], Tuple[float, float], Tuple[float, float]]:
            """
            Calculates current positions and their rates of change over `ttl` seconds.
            Returns: ((alt, az), (d_alt, d_az), (ra, dec), (d_ra, d_dec))
            """

            body = self._eph[obj.value]
            t_next = self._ts.from_datetime(t_now.utc_datetime() + timedelta(seconds=ttl))

            # --- 1. Current Position (T0) ---
            apparent_now = observer.at(t_now).observe(body).apparent()
            alt_now, az_now, _ = apparent_now.altaz()
            ra_now, dec_now, _ = apparent_now.radec(epoch=self._ts.J2000)

            # --- 2. Future Position (T1) ---
            apparent_next = observer.at(t_next).observe(body).apparent()
            alt_next, az_next, _ = apparent_next.altaz()
            ra_next, dec_next, _ = apparent_next.radec(epoch=self._ts.J2000)

            # --- 3. Calculate Deltas (normalized per second) ---
            d_alt = (alt_next.degrees - alt_now.degrees) / ttl

            # Zenith filter: Prevent azimuth spins if the object is directly overhead
            if alt_now.degrees > 89.5:
                d_az = 0.0
            else:
                d_az = self._circular_diff(az_next.degrees, az_now.degrees, 360.0) / ttl
            
            d_ra = self._circular_diff(ra_next.hours, ra_now.hours, 24.0) / ttl
            d_dec = (dec_next.degrees - dec_now.degrees) / ttl

            # --- 4. Package into Tuples ---
            current_altaz = (round(alt_now.degrees, 6), round(az_now.degrees, 6))
            delta_altaz = (round(d_alt, 6), round(d_az, 6))
            
            current_radec = (round(ra_now.hours, 6), round(dec_now.degrees, 6))
            delta_radec = (round(d_ra, 8), round(d_dec, 6))

            return (current_altaz, delta_altaz, current_radec, delta_radec)

    def _calculate_rise_set(self, obj: PlanetaryObject, topo_observer, t_now) -> RiseSetTransit:
        """Calculates the rise-setting events of a planet"""

        body = self._eph[obj.value]
        t_future = self._ts.from_datetime(t_now.utc_datetime() + timedelta(days=1))
        
        earth_obs = self._earth + topo_observer
        alt_now, _, _ = earth_obs.at(t_now).observe(body).apparent().altaz()
        is_visible = alt_now.degrees > 0

        if obj == PlanetaryObject.SUN or obj == PlanetaryObject.MOON:
            # Bigger "horizon value for first rise, instead of center rise"
            horizon = -0.8333
        else:
            horizon = -0.5667

        # Rise and Set
        f_rs = almanac.risings_and_settings(self._eph, body, topo_observer, horizon)
        t_rs, v_rs = almanac.find_discrete(t_now, t_future, f_rs)
        
        next_rise, next_set = None, None
        t_rise, t_set = None, None
        for t_evt, v_evt in zip(t_rs, v_rs):
            if v_evt == 1 and not next_rise:
                next_rise = t_evt.utc_datetime()
                t_rise= t_evt
            elif v_evt == 0 and not next_set:
                next_set = t_evt.utc_datetime()
                t_set=t_evt

        # Transit
        f_tr = almanac.meridian_transits(self._eph, body, topo_observer)
        t_tr, v_tr = almanac.find_discrete(t_now, t_future, f_tr)
        
      
        next_transit = t_tr[0]
        nxt_visible = v_tr[0]
        
        # Rise/Set/Transit positions
        astrometric = earth_obs.at(t_rise).observe(body).apparent()
        _, r_az, _ = astrometric.altaz()

        astrometric = earth_obs.at(t_set).observe(body).apparent()
        _, s_az, _ = astrometric.altaz()

        astrometric = earth_obs.at(next_transit).observe(body).apparent()
        t_alt, _, _ = astrometric.altaz()
        
        return RiseSetTransit(
            is_visible=is_visible,
            next_rise=next_rise,
            next_set=next_set,
            next_transit=next_transit.utc_datetime(),
            rise_az=round(r_az.degrees, 2) if r_az is not None else None,
            set_az=round(s_az.degrees, 2) if s_az is not None else None,
            transit_alt=round(t_alt.degrees, 2) if t_alt is not None else None,
            transit_visible=nxt_visible            
        )

    def _calculate_moon_details(self, astrometric, observer, t_now) -> MoonDetails:
        """Calculates extra Moon information"""
        apparent = astrometric.apparent()
        sun = self._eph[PlanetaryObject.SUN.value]
        sun_apparent = observer.at(t_now).observe(sun).apparent()

        # 1. Angles for Moon drawing
        phase_angle = apparent.phase_angle(sun).degrees
        moon_altaz = apparent.altaz()
        sun_altaz = sun_apparent.altaz()
        limb_angle = position_angle_of(moon_altaz, sun_altaz).degrees

        # 2. Illumination
        frac = almanac.fraction_illuminated(self._eph, 'moon', t_now)
        illumination_pct = round(frac * 100, 1)

        # 3. Next new/full Moon
        t_future = self._ts.from_datetime(t_now.utc_datetime() + timedelta(days=30))
        t_phases, v_phases = almanac.find_discrete(t_now, t_future, almanac.moon_phases(self._eph))
        
        next_new, next_full = None, None
        for t_phase, v_phase in zip(t_phases, v_phases):
            if v_phase == 0 and not next_new: next_new = t_phase.utc_datetime()
            elif v_phase == 2 and not next_full: next_full = t_phase.utc_datetime()

        # 4. Past phases for Moon age
        t_past = self._ts.from_datetime(t_now.utc_datetime() - timedelta(days=30))
        t_phases_past, v_phases_past = almanac.find_discrete(t_past, t_now, almanac.moon_phases(self._eph))
        
        last_new_moon = None
        for t_phase, v_phase in zip(reversed(t_phases_past), reversed(v_phases_past)):
            if v_phase == 0:
                last_new_moon = t_phase
                break
        
        age_days = round(t_now.tt - last_new_moon.tt, 2) if last_new_moon is not None else 0.0

        return MoonDetails(
            illumination_pct=illumination_pct,
            age=age_days,
            phase_angle_deg=round(phase_angle, 2),
            limb_angle_deg=round(limb_angle, 2),
            next_new_moon=next_new,
            next_full_moon=next_full
        )
    
    def _calculate_planet_details(self, astrometric, t_now) -> PlanetDetails:
        """Calculate planetary extra information"""
        apparent = astrometric.apparent()
        sun = self._eph[PlanetaryObject.SUN.value]
        sun_apparent = self._earth.at(t_now).observe(sun).apparent()
        phase_angle = apparent.phase_angle(sun).degrees
        illumination_pct = 100 * (1 + math.cos(math.radians(phase_angle))) / 2
        elongation = apparent.separation_from(sun_apparent).degrees
        
        return PlanetDetails(
            elongation_deg=round(elongation, 2),
            phase_angle_deg=round(phase_angle, 2),
            illumination_pct=round(illumination_pct, 1)
        )
    
    # ═════════════════════════════════════════════
    # MAIN METHODS
    # ═════════════════════════════════════════════

    def get_metadata(self, utc_time: datetime, lat: float, lon: float, elev_m: float = 0.0, ttl:float=120.0) -> MetadataCatalogPayload:
        """Returns heavy metadata for all available objects."""
        objects = {}
        topo_observer = wgs84.latlon(lat, lon)
        observer = self._earth + topo_observer
        t_now = self._ts.from_datetime(utc_time)

        for obj in PlanetaryObject:
            if obj == PlanetaryObject.EARTH:
                continue
            
            body = self._eph[obj.value]

            astrometric = observer.at(t_now).observe(body)
            apparent = astrometric.apparent()
            _, _, distance = apparent.altaz()

            magnitude = self._calculate_magnitude(obj, astrometric, t_now)

            objects[obj.name.lower()] = ObjectLightMetadata(
                id=obj.name.lower(),
                name=obj.name.capitalize(),
                dist=round(distance.au, 6),
                mag=magnitude
            )

        
        results = MetadataCatalogPayload(
            version="1.0",
            total=len(objects),
            data=objects
        )
        return results

    def get_sky_movement(self, t0_dt: datetime, lat: float, lon: float, elev_m: float = 0.0, ttl:float=120.0, targets: Optional[List[PlanetaryObject]] = None) -> SyncPayload:
        """
        Calculates the sky and its movement for a time and location
        """
        topo_observer = wgs84.latlon(lat, lon, elev_m)
        observer = self._earth + topo_observer
        
        t_now = self._ts.from_datetime(t0_dt)
        
        if targets is None:
            targets = [obj for obj in PlanetaryObject if obj != PlanetaryObject.EARTH]

        updates = []
        for obj in targets:
            if obj == PlanetaryObject.EARTH:
                continue
            
            (alt, az), (d_alt, d_az), _, _ = self._calculate_movement(obj, observer, t_now, ttl)

            updates.append((
                obj.name.lower(), 
                alt, 
                az, 
                d_alt, 
                d_az
            ))

        return SyncPayload(
            target_time=t0_dt,
            ttl=ttl,
            updates=updates
        )
    
    def get_object_movement(self, target_id:str, target_time: datetime, lat: float, lon: float, elev_m: float = 0.0, ttl:float=120):
        """
        Calculate an object movement and metadata
        """
        try:
            obj = PlanetaryObject[target_id.upper()]
        except KeyError:
            raise ValueError(f"Object {target_id} not found!")

        if obj == PlanetaryObject.EARTH:
            raise ValueError("Cannot observe Earth from Earth.")

        topo_observer = wgs84.latlon(lat, lon, elev_m)
        observer = self._earth + topo_observer
        t_now = self._ts.from_datetime(target_time)
        body = self._eph[obj.value]

        astrometric = observer.at(t_now).observe(body)
        apparent = astrometric.apparent()
        _, _, distance = apparent.altaz()

        magnitude = self._calculate_magnitude(obj, astrometric, t_now)

        (alt, az), (d_alt, d_az), (ra, dec), (d_ra, d_dec) = self._calculate_movement(obj, observer, t_now, ttl)

        ang_diameter = self._get_angular_diameter(obj, astrometric.distance().km)

        rise_set=self._calculate_rise_set(obj, topo_observer, t_now)

        extra = None
        if obj == PlanetaryObject.MOON:
            extra = self._calculate_moon_details(astrometric, observer, t_now)
        elif obj not in (PlanetaryObject.SUN, PlanetaryObject.EARTH):
            extra = self._calculate_planet_details(astrometric, t_now)

        motion=MotionDelta(
            ttl=ttl,
            target_time=target_time,
            delta_alt=d_alt,
            delta_az=d_az,
            delta_ra=d_ra,
            delta_dec=d_dec
        )

        return ObjectMetadata(
            id=obj.name.lower(),
            name=obj.name.capitalize(),
            dist=round(distance.au, 6),
            mag=magnitude,
            ang_diameter=ang_diameter,
            alt=alt,
            az=az,
            ra_j2000=ra,
            dec_j2000=dec,
            motion=motion,
            rise_set_transit=rise_set,
            extra_details=extra
        )
