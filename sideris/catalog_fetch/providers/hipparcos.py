from catalog_fetch.config import SIMBAD_VOTABLE_FIELDS
from catalog_fetch.providers.base import BaseCatalogProvider
from catalog_fetch.utils import NamingUtils
from catalog_fetch.physics import calculate_absolute_magnitude_and_luminosity, calculate_distance_ly
from models.CatalogSchemas import Star
import numpy as np
from astropy.coordinates import SkyCoord
import astropy.units as u


class HipparcosProvider(BaseCatalogProvider):
    def __init__(self, min_fetch_mag:float, min_stars_set: set):
        super().__init__()
        self.catalog = 'I/239/hip_main'
        self.vizier_fields = ['HIP', 'Vmag', 'pmRA', 'pmDE', 'SpType', 'Plx', 'B-V']
        self.simbad_fields = SIMBAD_VOTABLE_FIELDS

        self.min_stars_set = min_stars_set
        self.min_fetch_mag=min_fetch_mag
        

    def run(self) -> list[Star]:
        """Run the fetching and clearing of data"""
        raw_table = self.fetch()
        valid_stars = self.clean(raw_table)
        return self.normalize(valid_stars)

    def fetch(self):
        """Run the fetching of data"""
        print("Fetching Hipparcos Catalog...")
        return self._query_vizieR(self.vizier_fields, self.catalog, row_limit=-1)

    def clean(self, raw_data):
        """Clean and validate fetched data"""
        print(f"Cleaning {len(raw_data)} Hipparcos rows...")
        valid_stars = {}
        # Debug counters
        n_bright = 0
        n_req = 0
        req_names = []
        
        for row in raw_data:
            if not np.ma.is_masked(row['HIP']):
                hip_num = int(row['HIP'])
                hip_id = f"HIP {hip_num}"
                
                # Check visual magnitude or required star
                vmag_val = row['Vmag']
                has_mag = not np.ma.is_masked(vmag_val) and not np.isnan(vmag_val)
                is_bright = has_mag and float(vmag_val) <= self.min_fetch_mag
                is_req = hip_num in self.min_stars_set
                        
                if is_bright or is_req:
                    # Get stellar proper motion, spectral type and B-V index (for color)
                    pmra_raw=row['pmRA']
                    pmdec_raw=row['pmDE']
                    sptype_raw = str(row['SpType']).strip() if not np.ma.is_masked(row['SpType']) else None
                    bv_raw = row['B-V']
                    pmra = round(float(pmra_raw), 3) if not np.ma.is_masked(pmra_raw) and not np.isnan(pmra_raw) else 0.0
                    pmdec = round(float(pmdec_raw), 3) if not np.ma.is_masked(pmdec_raw) and not np.isnan(pmdec_raw) else 0.0
                    sp_type = sptype_raw.split()[0] if sptype_raw else None
                    b_v = round(float(bv_raw), 3) if not np.ma.is_masked(bv_raw) and not np.isnan(bv_raw) else None

                    # Get parallax and calculate the star's distance
                    plx_raw=row['Plx']
                    plx = float(plx_raw) if not np.ma.is_masked(plx_raw) and not np.isnan(plx_raw) else 0.0
                    dist_ly = calculate_distance_ly(plx)
                    
                    # Debugging
                    n_bright += int(is_bright)
                    n_req += int(is_req and not is_bright)
                    if is_req and not is_bright:
                        req_names.append(hip_id)

                    valid_stars[hip_id] = {
                        'mag': round(float(vmag_val), 6) if has_mag else None,
                        'pmra': pmra,
                        'pmdec': pmdec,
                        "spectral_type": sp_type,
                        "b_v": b_v,
                        'distance_ly': dist_ly
                    }
        print(f"Found {len(valid_stars)} stars ({n_bright} bright / {n_req} required).")
        if req_names and n_req<=10:
            print(f"   ↳ Stars required and added: {', '.join(req_names)}")
        return valid_stars

    def normalize(self, cleaned_data) -> list[Star]:
        """Enrich data by fetching Simbad star data"""
        print(f"Querying Simbad for {len(cleaned_data)} stars...")
        s_table = self._query_simbad_batch(list(cleaned_data.keys()), self.simbad_fields, batch_size=1500)
        stars = []
        if s_table is not None:
            print("Enriching stars with Simbad data...")
            coords = SkyCoord(s_table['ra'], s_table['dec'], unit=(u.hourangle, u.deg))
            constellations = coords.get_constellation(short_name=True)

            for i, row in enumerate(s_table):
                # Get clean name and classify other names
                user_id = NamingUtils.clean_name(row['user_specified_id'])
                raw_ids = row['ids'].decode('utf-8') if isinstance(row['ids'], bytes) else str(row['ids'])
                com, cat = NamingUtils.classify_names(raw_ids, Star)
                cat.add(user_id)
                cat_ord = NamingUtils.sort_catalogs(cat, Star)
                com_ord = sorted(list(com))

                # Get cleaned data and calculate      
                d = cleaned_data.get(user_id, {})
                sp_type = d.get('spectral_type', None)
                mag_ap = d.get('mag', None)
                dist_ly = d.get('distance_ly', None)
                b_v=d.get('b_v', None)
                pmra=d.get('pmra', 0.0)
                pmdec=d.get('pmdec', 0.0)
                mag_abs, luminosity = calculate_absolute_magnitude_and_luminosity(mag_ap, dist_ly)
                
                stars.append(Star(
                    id="", # Will be added at the end
                    name=NamingUtils.choose_default_name(com_ord, cat_ord),
                    type="star",
                    common_names=com_ord,
                    catalog_names=NamingUtils.clean_catalog_list(cat_ord),
                    mag=mag_ap,
                    abs_mag=mag_abs,
                    luminosity=luminosity,
                    spectral_type=sp_type,
                    dist_ly=dist_ly,
                    ra_j2000=round(coords[i].ra.hour, 6),
                    dec_j2000=round(coords[i].dec.deg, 6),
                    constellation=constellations[i],
                    b_v=b_v,
                    pmra_mas=pmra,
                    pmdec_mas=pmdec
                ))
        return stars
