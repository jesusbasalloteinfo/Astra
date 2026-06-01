"""
ASTRA - Automated Smart Telescope Remote Assistant
Copyright (C) 2026 Jesus Basallote

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""

from catalog_fetch.providers.base import *
from catalog_fetch.utils import NamingUtils, ParseUtils
from models.catalog.sidereal import DeepSky
from astropy.coordinates import SkyCoord
import astropy.units as u

from ..config import SIMBAD_VOTABLE_FIELDS

class MessierProvider(BaseCatalogProvider):
    def __init__(self):
        super().__init__()
        self.objects=[f"M {i}" for i in range(1, 111)]
        self.simbad_fields = SIMBAD_VOTABLE_FIELDS

    def run(self) -> list[DeepSky]:
        """Run the fetching and clearing of data"""
        raw_table = self.fetch()
        return self.normalize(self.clean(raw_table))

    def fetch(self):
        """Run the fetching of data"""
        print("Fetching Messier Catalog (Simbad)...")
        return self._query_simbad(object_list=self.objects, request_columns=self.simbad_fields)

    def clean(self, raw_data):
        """Clean and validate fetched data (done)"""
        return raw_data

    def normalize(self, cleaned_data) -> list[DeepSky]:
        """Enrich data by processing Simbad star data"""
        objects = []
        if cleaned_data is not None:
            coords = SkyCoord(cleaned_data['ra'], cleaned_data['dec'], unit=(u.hourangle, u.deg))
            constellations = coords.get_constellation(short_name=True) 

            for i, row in enumerate(cleaned_data):
                # Get clean name and classify other names
                user_id = NamingUtils.clean_name(row['user_specified_id'])
                raw_ids = row['ids'].decode('utf-8') if isinstance(row['ids'], bytes) else str(row['ids'])
                otype_raw = row['otype'].decode('utf-8') if isinstance(row['otype'], bytes) else str(row['otype'])
                com, cat = NamingUtils.classify_names(raw_ids)
                cat.add(user_id)
                cat_ord = NamingUtils.sort_catalogs(cat)
                com_ord = sorted(list(com))
                
                objects.append(DeepSky(
                    id="", # Will be added at the end
                    name=NamingUtils.choose_default_name(com_ord, cat_ord),
                    type=ParseUtils.translate_type(otype_raw),
                    common_names=com_ord,
                    catalog_names=NamingUtils.clean_catalog_list(cat_ord),
                    mag = ParseUtils.extract_number(row, ['r', 'V', 'flux_v', 'B', 'flux_b', 'mag']),
                    size_arcmin=ParseUtils.extract_number(row, ['majaxis', 'minaxis', 'dim']),
                    constellation=constellations[i],
                    ra_j2000=round(coords[i].ra.hour, 6),
                    dec_j2000=round(coords[i].dec.deg, 6)
                ))
        return objects
