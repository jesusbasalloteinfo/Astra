from catalog_fetch.providers.base import BaseCatalogProvider
from catalog_fetch.config import VIP_STARS, VIP_DSO, SIMBAD_VOTABLE_FIELDS
from catalog_fetch.utils import NamingUtils, ParseUtils
from models.catalog.sidereal import Star, DeepSky
from astropy.coordinates import SkyCoord
import astropy.units as u


class ManualOverrideProvider(BaseCatalogProvider):
    def run(self):
        s_raw, d_raw = self.fetch()
        return self.normalize((s_raw, d_raw))

    def fetch(self):
        print("Fetching VIP manual objects (Simbad)...")
        vip_s_table = None
        try: vip_s_table = self._query_simbad(VIP_STARS, SIMBAD_VOTABLE_FIELDS)
        except Exception as e: print(f"Error VIP stars: {e}")
        
        vip_d_table = None
        try: vip_d_table = self._query_simbad(VIP_DSO, SIMBAD_VOTABLE_FIELDS)
        except Exception as e: print(f"Error VIP objects: {e}")
            
        return vip_s_table, vip_d_table

    def clean(self, raw_data):
        return raw_data

    def normalize(self, cleaned_data):
        vip_s_table, vip_d_table = cleaned_data
        stars = []
        deep_sky = []

        if vip_s_table is not None:
            coords = SkyCoord(vip_s_table['ra'], vip_s_table['dec'], unit=(u.hourangle, u.deg))
            constellations = coords.get_constellation(short_name=True)

            for i, row in enumerate(vip_s_table):
                # Get clean name and classify other names
                raw_ids = row['ids'].decode('utf-8') if isinstance(row['ids'], bytes) else str(row['ids'])
                com, cat = NamingUtils.classify_names(raw_ids)
                cat_ord = NamingUtils.sort_catalogs(cat)
                com_ord = sorted(list(com))
                               
                stars.append(Star(
                    id="", # Will be added at the end
                    name=NamingUtils.choose_default_name(com_ord, cat_ord),
                    type="star",
                    constellation=constellations[i],
                    common_names=com_ord,
                    catalog_names=NamingUtils.clean_catalog_list(cat_ord),
                    mag=ParseUtils.extract_number(row, ['flux_v', 'mag']),
                    ra_j2000=round(coords[i].ra.hour, 6),
                    dec_j2000=round(coords[i].dec.deg, 6),
                    pmra_mas=0.0,
                    pmdec_mas=0.0
                ))
                
        if vip_d_table is not None:
            coords = SkyCoord(vip_d_table['ra'], vip_d_table['dec'], unit=(u.hourangle, u.deg))
            constellations = coords.get_constellation(short_name=True)

            for i, row in enumerate(vip_d_table):
                # Get clean name and classify other names
                raw_ids = row['ids'].decode('utf-8') if isinstance(row['ids'], bytes) else str(row['ids'])
                otype = row['otype'].decode('utf-8') if isinstance(row['otype'], bytes) else str(row['otype'])
                com, cat = NamingUtils.classify_names(raw_ids)
                cat_ord = NamingUtils.sort_catalogs(cat)
                com_ord = sorted(list(com))
                
                deep_sky.append(DeepSky(
                    id="", # Will be added at the end
                    name=NamingUtils.choose_default_name(com_ord, cat_ord),
                    type=ParseUtils.translate_type(otype),
                    constellation=constellations[i],
                    common_names=com_ord,
                    catalog_names=NamingUtils.clean_catalog_list(cat_ord),
                    mag=ParseUtils.extract_number(row, ['flux_v', 'flux_b', 'mag']),
                    size_arcmin=ParseUtils.extract_number(row, ['majaxis', 'minaxis', 'dim']),
                    ra_j2000=round(coords[i].ra.hour, 6),
                    dec_j2000=round(coords[i].dec.deg, 6)
                ))

        return {"stars": stars, "deep_sky": deep_sky}
