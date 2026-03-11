import random
import time
from astroquery.simbad import Simbad
from astroquery.vizier import Vizier
from astropy.table import vstack
from core.logging import get_logger
from .config import SIMBAD_VOTABLE_FIELDS, VIZIER_MIRRORS, SIMBAD_MIRRORS

class NetworkMixin:
    """
    Mixin to provide reliable network interaction with VizieR and Simbad 
    using mirror rotation and retry logic.
    """

    def _query_vizieR(self, columns, catalog_name: str, row_limit:int=-1):
        """Try to download a VizieR catalog with mirrors"""
        for mirror in VIZIER_MIRRORS:
            try:
                v = Vizier(columns=columns, row_limit=row_limit, vizier_server=mirror)
                catalogs = v.get_catalogs(catalog_name)
                if not catalogs:
                    raise Exception(f"No results found for catalog {catalog_name}")
                get_logger("CatalogFetch").debug(f"  > VizieR data fetched from {mirror}!")
                return catalogs[0]
            except Exception as e:
                get_logger("CatalogFetch").debug(f"  [!] Failed on {mirror}: {e}. Switching mirror...")
                
                raise Exception(f"All VizieR servers failed! Unable to download catalog {catalog_name}")

    def _query_simbad(self, object_list: list, request_columns: list[str], row_limit:int=-1, timeout:int=60):
        """Try to download Simbad data catalog with mirrors"""
        simbad = Simbad()
        simbad.ROW_LIMIT = row_limit
        simbad.TIMEOUT = timeout
        simbad.add_votable_fields(*request_columns)

        for mirror in SIMBAD_MIRRORS:
            try:
                simbad.SIMBAD_URL = mirror
                table = simbad.query_objects(object_list)
                return table
            except Exception as e:
                get_logger("CatalogFetch").debug(f"  [!] Failed Simbad ({mirror}): {e}. Switching mirror...")
                
        raise Exception(f"All Simbad servers failed! Unable to download data!")

    def _query_simbad_batch(self, object_list: list, request_columns: list[str], batch_size:int=500, timeout:int=60):
        """Query to simbad as batch and merge the results"""
        results = []
        total = len(object_list)
        batches = [object_list[i : i + batch_size] for i in range(0, total, batch_size)]
        total_batches = len(batches)
        
        for i, batch in enumerate(batches, 1): 
            get_logger("CatalogFetch").debug(f"    -> Querying Simbad: Batch {i}/{total_batches} ({len(batch)} objets)")
            
            table = self._query_simbad(batch, request_columns, timeout=timeout)
            if table is not None:
                table.meta.clear()
                results.append(table)
                
            if i < total_batches:
                # Await to not stress the servers
                time.sleep(random.uniform(0.2, 1.0))
            
        if results:
            return vstack(results)
        return None
