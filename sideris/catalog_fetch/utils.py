import os
import re
import numpy as np
from typing import Tuple, Set, List, Dict, Any, Type
from astropy.coordinates import SkyCoord
import astropy.units as u
from catalog_fetch.config import IAU_CONSTELLATIONS, IMPORTANT_STAR_NAMES, OBJECT_TAGS, STAR_CATALOG_RANKING, DSO_CATALOG_RANKING
from models.catalog.sidereal import Metadata, Star, DeepSky
from models.catalog.constellations import ConstellationCatalog

class NamingUtils:
    @staticmethod
    def clean_name(raw_name) -> str:
        if isinstance(raw_name, bytes):
            raw_name = raw_name.decode('utf-8')
        return " ".join(str(raw_name).split())

    @staticmethod
    def classify_names(simbad_ids_str: str, obj_type: Type[Star] | Type[DeepSky] = DeepSky) -> Tuple[Set[str], Set[str]]:
        active_ranking = STAR_CATALOG_RANKING if obj_type is Star else DSO_CATALOG_RANKING
        common_names, catalog_names = set(), set()
        if not simbad_ids_str: 
            return common_names, catalog_names

        for alias in simbad_ids_str.split('|'):
            alias = NamingUtils.clean_name(alias)
            if not alias: continue
            if alias.startswith("NAME "):
                clean_name = alias.replace("NAME ", "").strip()
                if not clean_name.isupper() or len(clean_name) < 4:
                    common_names.add(clean_name)
            elif alias.startswith(tuple(active_ranking.keys())):
                catalog_names.add(alias)
        return common_names, catalog_names

    @staticmethod
    def sort_catalogs(names_set: Set[str], obj_type: Type[Star] | Type[DeepSky] = DeepSky) -> List[str]:
        active_ranking = STAR_CATALOG_RANKING if obj_type is Star else DSO_CATALOG_RANKING
        def ranker(name):
            for prefix, rank in active_ranking.items():
                if name.startswith(prefix):
                    suffix = name[len(prefix):].strip()
                    try: return (rank, float(suffix.split()[0]), name)
                    except ValueError: return (rank, float('inf'), name)
            return (99, float('inf'), name)
        return sorted(list(names_set), key=ranker)

    @staticmethod
    def choose_default_name(common_ordered: List[str], catalogs_ordered: List[str]) -> str:
        if not common_ordered:
            if catalogs_ordered:
                name = catalogs_ordered[0]
                if name.startswith('* '): return name[2:]
                elif name.startswith('V* '): return name[3:]
                return name
            return "Unknown Object"
            
        forbidden = ['amas ', 'nébuleuse', 'nebuleuse', 'galaxie', 'haufen', 'ammasso', "l'ecu", 'stellaire', 'nebel']
        candidates = [n for n in common_ordered if not any(p in n.lower() for p in forbidden)]
        
        if not candidates:
            candidates = common_ordered
            
        favorites = ['cluster', 'nebula', 'galaxy']
        top_names = [n for n in candidates if any(f in n.lower() for f in favorites)]
        
        if top_names:
            return max(top_names, key=len)
            
        for vip in IMPORTANT_STAR_NAMES:
            if vip in candidates:
                return vip 
                
        single_word = [n for n in candidates if " " not in n]
        if single_word:
            return max(single_word, key=len)
            
        return max(candidates, key=len)

    @staticmethod
    def clean_catalog_list(sorted_catalogs: List[str]) -> List[str]:
        clean_list = []
        for name in sorted_catalogs:
            if name.startswith('* '): clean_val = name[2:]
            elif name.startswith('V* '): clean_val = name[3:]
            else: clean_val = name
            if clean_val not in clean_list: clean_list.append(clean_val)
        return clean_list
    
    @staticmethod
    def generate_iau_id(ra_hours: float, dec_deg: float, obj_type: Type[Star] | Type[DeepSky] = DeepSky) -> str:
        """
        Generate an unique ID based on the IAU standard
        Example: Sirius -> s_J064508-164258
        """
        if ra_hours is None or dec_deg is None:
            import random
            return f"{obj_type[0]}_UNKNOWN_{random.randint(10000,99999)}"

        # 1. RA to sexagecimal
        ra_h = int(ra_hours)
        ra_m = int((ra_hours - ra_h) * 60)
        ra_s = ((ra_hours - ra_h) * 60 - ra_m) * 60

        # 1. DEC to sexagecimal
        sign = '+' if dec_deg >= 0 else '-'
        dec_abs = abs(dec_deg)
        dec_d = int(dec_abs)
        dec_m = int((dec_abs - dec_d) * 60)
        dec_s = ((dec_abs - dec_d) * 60 - dec_m) * 60

        # 3. Format ID (HHMMSS+DDMMSS)
        
        # More precision in RA to avoid collitions in near objects
        ra_str = f"{ra_h:02d}{ra_m:02d}{int(ra_s * 10):03d}" 
        dec_str = f"{dec_d:02d}{dec_m:02d}{int(dec_s):02d}"

        prefix = "s" if obj_type is Star else "d"
        
        return f"{prefix}_J{ra_str}{sign}{dec_str}"


class MetadataUtils:
    """Generates natural sort indices for object catalogs and constellations."""
    
    @staticmethod
    def natural_sort_key(s: str) -> List[Any]:
        return [int(text) if text.isdigit() else text.lower() for text in re.split('([0-9]+)', s)]

    # @staticmethod
    # def generate_metadata(stars: List[Any], deep_sky: List[Any]) -> Metadata:
    #     """Generates inverted indices grouped by prefix and constellation."""
    #     PREFIXES = ["M", "NGC", "IC", "Sh2", "B", "HIP", "HD", "HR"]
        
    #     indices = {p: [] for p in PREFIXES}
    #     indices["constellations"] = {}

    #     all_objects = stars + deep_sky
        
    #     for obj in all_objects:
    #         cat_names = getattr(obj, "catalog_names", []) if not isinstance(obj, dict) else obj.get("catalog_names", [])
    #         for cat_name in cat_names:
    #             parts = cat_name.split()
    #             if not parts: continue
                
    #             # Case A: Standard prefixes (M 31, NGC 17)
    #             if parts[0] in indices:
    #                 # Special check for 'M' to avoid capturing 'M Car' as Messier
    #                 if parts[0] == "M":
    #                     if len(parts) > 1 and parts[1].isdigit():
    #                         indices[parts[0]].append(cat_name)
    #                 else:
    #                     indices[parts[0]].append(cat_name)
                
    #             # Case B: Stars with constellation (184 Car, alf Cen, M Car)
    #             if len(parts) > 1 and parts[1] in IAU_CONSTELLATIONS:
    #                 const_abbr = parts[1]
    #                 if const_abbr not in indices["constellations"]:
    #                     indices["constellations"][const_abbr] = []
    #                 indices["constellations"][const_abbr].append(cat_name)

    #     # Sort each catalog numerically
    #     for k in list(indices.keys()):
    #         if k == "constellations":
    #             for const in indices[k]:
    #                 indices[k][const] = sorted(list(set(indices[k][const])), key=MetadataUtils.natural_sort_key)
    #         else:
    #             indices[k] = sorted(list(set(indices[k])), key=MetadataUtils.natural_sort_key)
                
    #     return Metadata(
    #         total_objects=len(all_objects),
    #         catalogs=indices
    #     )

    @staticmethod
    def generate_metadata(stars: List[Any], deep_sky: List[Any]) -> Metadata:
        PREFIXES = ["M", "NGC", "IC", "Sh2", "B", "HIP", "HD", "HR"]
        
        # Guardaremos tuplas temporales: (alias, id)
        indices_temp = {p: [] for p in PREFIXES}
        indices_temp["constellations"] = {}

        all_objects = stars + deep_sky
        
        for obj in all_objects:
            cat_names = getattr(obj, "catalog_names", []) if not isinstance(obj, dict) else obj.get("catalog_names", [])
            obj_id = getattr(obj, "id", None) if not isinstance(obj, dict) else obj.get("id")
            
            for cat_name in cat_names:
                parts = cat_name.split()
                if not parts: continue
                
                prefix = parts[0]
                entry = (cat_name, obj_id) # (ej: "M 31", "d_J004244+411609")
                
                # Catálogos estándar
                if prefix in indices_temp:
                    if prefix == "M":
                        if len(parts) > 1 and parts[1].isdigit():
                            indices_temp[prefix].append(entry)
                    else:
                        indices_temp[prefix].append(entry)
                
                # Constelaciones
                if len(parts) > 1 and parts[1] in IAU_CONSTELLATIONS:
                    const_abbr = parts[1]
                    if const_abbr not in indices_temp["constellations"]:
                        indices_temp["constellations"][const_abbr] = []
                    indices_temp["constellations"][const_abbr].append(entry)

        # Limpiar y extraer SOLAMENTE el ID
        final_indices = {p: [] for p in PREFIXES}
        final_indices["constellations"] = {}

        for k in list(indices_temp.keys()):
            if k == "constellations":
                for const in indices_temp[k]:
                    # Ordenamos usando el alias (M 1, M 2...)
                    sorted_tuples = sorted(indices_temp[k][const], key=lambda x: MetadataUtils.natural_sort_key(x[0]))
                    
                    # Extraemos solo los IDs, evitando duplicados
                    seen = set()
                    final_ids = []
                    for _, target_id in sorted_tuples:
                        if target_id not in seen:
                            seen.add(target_id)
                            final_ids.append(target_id)
                    final_indices[k][const] = final_ids
            else:
                sorted_tuples = sorted(indices_temp[k], key=lambda x: MetadataUtils.natural_sort_key(x[0]))
                seen = set()
                final_ids = []
                for _, target_id in sorted_tuples:
                    if target_id not in seen:
                        seen.add(target_id)
                        final_ids.append(target_id)
                final_indices[k] = final_ids
                
        return Metadata(
            total_objects=len(all_objects),
            catalogs=final_indices
        )

class ParseUtils:
    @staticmethod
    def extract_number(row, keys):
        # For determinism
        sorted_cols = sorted(row.colnames)
        
        for key in keys:
            # 1. Exact search
            for col in sorted_cols:
                if key.lower() == col.lower():
                    val = row[col]
                    if np.ma.is_masked(val) or val is None or str(val).strip() == '':
                        continue
                    match = re.search(r"[-+]?\d*\.\d+|\d+", str(val).strip())
                    if match:
                        return round(float(match.group()), 2)
                        
        return None

    @staticmethod
    def translate_type(raw_code):
        if not raw_code: return 'unknown'
        code = NamingUtils.clean_name(raw_code)
        return OBJECT_TAGS.get(code, f"other_({code})")
    
    @staticmethod
    def parse_fab_file(file_path: str = "constellationship.fab") -> Tuple[Set[int], List[Dict[str, Any]]]:
        """Parses .fab files for constellation metadata."""
        global_hip_ids = set()
        constellations_data = []
        
        if not os.path.exists(file_path):
            return global_hip_ids, []
            
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                parts = line.strip().split()
                if len(parts) > 2:
                    abbr = parts[0]
                    ids_in_line = [int(p) for p in parts[2:] if p.isdigit()]
                    
                    # 1. Extract unique stars
                    unique_stars = []
                    for hid in ids_in_line:
                        if hid not in unique_stars:
                            unique_stars.append(hid)
                    
                    # 2. Generate line indices pair based on unique list
                    lines_indices = []
                    for i in range(0, len(ids_in_line) - 1, 2):
                        idx_orig = unique_stars.index(ids_in_line[i])
                        idx_dest = unique_stars.index(ids_in_line[i+1])
                        lines_indices.append([idx_orig, idx_dest])
                    
                    constellations_data.append({
                        "abbr": abbr,
                        "full_name": IAU_CONSTELLATIONS.get(abbr, "Unknown"),
                        "stars_ids": unique_stars,
                        "lines_indices": lines_indices
                    })
                    
                    global_hip_ids.update(unique_stars)

            print(f" -> .fab parsed: {len(global_hip_ids)} stars required for {len(constellations_data)} constellations.")
            catalog = ConstellationCatalog(constellations=constellations_data)

        return global_hip_ids, catalog




class CrossMatchUtils:
    """
    Engine for consolidating objects using spatial coordinates as fallback.
    """
    @staticmethod
    def spatial_cross_match(
        base_objects: List[Any], 
        target_objects: List[Any], 
    ) -> Tuple[List[int], List[float]]:
        """
        Matches target objects to base objects using spatial coordinates.
        Expects objects to be dicts or models with 'ra' and 'dec'.
        Returns lists of indices into base_objects and distances in arcmin for each target_object.
        """
        def get_ra_dec(objs):
            ras, decs = [], []
            for obj in objs:
                if isinstance(obj, dict):
                    ras.append(obj.get('ra', obj.get('ra_j2000')))
                    decs.append(obj.get('dec', obj.get('dec_j2000')))
                else:
                    ras.append(getattr(obj, 'ra', getattr(obj, 'ra_j2000', 0)))
                    decs.append(getattr(obj, 'dec', getattr(obj, 'dec_j2000', 0)))
            return ras, decs

        base_ras, base_decs = get_ra_dec(base_objects)
        target_ras, target_decs = get_ra_dec(target_objects)

        if not base_ras or not target_ras:
            return [], []

        base_coords = SkyCoord(base_ras, base_decs, unit=(u.hourangle, u.deg))
        target_coords = SkyCoord(target_ras, target_decs, unit=(u.hourangle, u.deg))

        idx_dist, d2d, _ = target_coords.match_to_catalog_sky(base_coords)
        
        return list(idx_dist), [d.arcmin for d in d2d]
