from ..config import SIMBAD_VOTABLE_FIELDS
from .base import *
from ..utils import NamingUtils, ParseUtils
from models.CatalogSchemas import DeepSky
import numpy as np
from astropy.coordinates import SkyCoord
import astropy.units as u
from core.logging import get_logger


class NGCProvider(BaseCatalogProvider):
    def __init__(self):
        super().__init__()
        self.catalog = 'VII/118/ngc2000'
        self.vizier_fields = ['Name', 'Type', '_RAJ2000', '_DEJ2000', 'mag', 'size', 'Mag']
        self.simbad_fields = SIMBAD_VOTABLE_FIELDS

    def run(self) -> list[DeepSky]:
        """Run the fetching and clearing of data"""
        raw_table = self.fetch()
        cleaned = self.clean(raw_table)
        return self.normalize(cleaned)

    def fetch(self):
        """Run the fetching of data"""
        get_logger("CatalogFetch").debug("Fetching NGC/IC Catalog...")
        return self._query_vizieR(self.vizier_fields, self.catalog, row_limit=-1)

    def clean(self, raw_data):
        """Clean and validate fetched data"""
        get_logger("CatalogFetch").debug(f"Cleaning {len(raw_data)} NGC/IC rows...")
        dso_temp = []

        # Transform the equatorial data to RA hours and DEC degrees + constellation calc
        ras = [(float(r['_RAJ2000']) / 15.0) % 24.0 for r in raw_data]
        decs = [float(r['_DEJ2000']) for r in raw_data]
        coords = SkyCoord(ras, decs, unit=(u.hourangle, u.deg))
        constellations = coords.get_constellation(short_name=True)

        for i, row in enumerate(raw_data):
            if not np.ma.is_masked(row['_RAJ2000']) and not np.isnan(row['_RAJ2000']): # Is a valid entry?
                # Separate between catalogs
                clean_str = NamingUtils.clean_name(row['Name'])
                if clean_str.startswith('I'):
                    nombre_oficial = f"IC {clean_str[1:].strip()}"
                else:
                    nombre_oficial = f"NGC {clean_str}"

                dso_temp.append({
                    "base_id": nombre_oficial,
                    "catalog_names": {nombre_oficial},
                    "common_names": set(),
                    "type": ParseUtils.translate_type(row['Type']),
                    "mag": ParseUtils.extract_number(row, ['mag']),
                    "size_arcmin": ParseUtils.extract_number(row, ['size']),
                    "constellation": constellations[i], 
                    "ra_j2000": ras[i],
                    "dec_j2000": decs[i]
                })
        return dso_temp

    def normalize(self, cleaned_data) -> list[DeepSky]:
        names_for_simbad = sorted([obj["base_id"] for obj in cleaned_data])
        ngc_dict = {obj["base_id"]: obj for obj in cleaned_data}
        
        get_logger("CatalogFetch").debug(f"Merging {len(names_for_simbad)} NGC/IC objects...")
        s_table = self._query_simbad_batch(names_for_simbad, SIMBAD_VOTABLE_FIELDS, batch_size=1500)
        
        consolidated_objects = {}
        if s_table is not None:
            for row in s_table:
                user_id = NamingUtils.clean_name(row['user_specified_id'])
                raw_ids = row['ids'].decode('utf-8') if isinstance(row['ids'], bytes) else str(row['ids'])
                fingerprint = raw_ids
                
                vizier_data = ngc_dict.get(user_id)
                if not vizier_data: continue
                
                if user_id not in consolidated_objects:
                    # New object. Saves the simbad data, vizier for fallback
                    raw_type = row['otype'].decode('utf-8') if isinstance(row['otype'], bytes) else str(row['otype'])
                    obj_type = ParseUtils.translate_type(raw_type)
                    if obj_type == 'unknown' or 'other' in obj_type:
                        obj_type = vizier_data['type']

                    mag_simbad = ParseUtils.extract_number(row, ['V', 'r', 'flux_v', 'B', 'flux_b', 'mag'])
                    mag_final = mag_simbad if mag_simbad is not None else vizier_data['mag']

                    size_simbad = ParseUtils.extract_number(row, ['majaxis', 'dim'])
                    size_final = size_simbad if size_simbad is not None else vizier_data['size_arcmin']

                    com_simbad, cat_simbad = NamingUtils.classify_names(fingerprint)
                    cat_final = cat_simbad.union(vizier_data['catalog_names'])
                    com_final = com_simbad.union(vizier_data['common_names'])

                    consolidated_objects[fingerprint] = {
                        "type": obj_type,
                        "mag": mag_final,
                        "size_arcmin": size_final,
                        "catalog_names": cat_final,
                        "common_names": com_final,
                        "constellation": vizier_data['constellation'],
                        "ra_j2000": vizier_data['ra_j2000'],
                        "dec_j2000": vizier_data['dec_j2000']
                    }
                else:
                    # Object is not new (already processed). So try to fill any gaps left by Simbad
                    current = consolidated_objects[fingerprint]
                    if current['mag'] is None and vizier_data['mag'] is not None:
                        current['mag'] = vizier_data['mag']

                    if current['size_arcmin'] is None and vizier_data['size_arcmin'] is not None:
                        current['size_arcmin'] = vizier_data['size_arcmin']

                    current['catalog_names'].update(vizier_data['catalog_names'])
                    if vizier_data['common_names']:
                        current['common_names'].update(vizier_data['common_names'])

        results = []
        # Add all the ngc/ic object entries into DeepSky objects
        for obj in consolidated_objects.values():
            cat_ord = NamingUtils.sort_catalogs(obj['catalog_names'])
            com_ord = sorted(list(obj['common_names']))
            
            results.append(DeepSky(
                id="", # Will be added at the end
                name=NamingUtils.choose_default_name(com_ord, cat_ord),
                type=obj['type'],
                common_names=com_ord,
                catalog_names=NamingUtils.clean_catalog_list(cat_ord),
                mag=obj['mag'],
                size_arcmin=obj['size_arcmin'],
                constellation=obj['constellation'],
                ra_j2000=round(obj['ra_j2000'], 6),
                dec_j2000=round(obj['dec_j2000'], 6)
            ))
        return results
