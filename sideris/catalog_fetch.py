import json
import argparse
from pathlib import Path
import pickle
import sys

from catalog_fetch.utils import *
from catalog_fetch.registry import CatalogRegistry
from models.CatalogSchemas import AstronomicalCatalog, CatalogData, Constellation, Star, DeepSky

from catalog_fetch.providers.hipparcos import HipparcosProvider
from catalog_fetch.providers.messier import MessierProvider
from catalog_fetch.providers.ngc import NGCProvider
from catalog_fetch.providers.vip import ManualOverrideProvider


def merge_messier_ngc(objects: List[DeepSky], dist_threshold: float = 2.5) -> List[DeepSky]:
    """
    Consolidates and merges different object catalog names and properties into one unique
    """

    # Name-Based Deduplication (O(N))
    alias_map = {}
    unique_list = []
    
    for obj in objects:
        existing = None

        # Check naming duplicates across catalogs
        for cat in obj.catalog_names:
            if cat in alias_map:
                existing = alias_map[cat]
                break
                
        if existing:
            _merge_objects(existing, obj)
            # Ensure all names point to the same object
            for name in obj.catalog_names:
                alias_map[name] = existing
        else:
            # Not duplicate, so add to next
            unique_list.append(obj)
            for name in obj.catalog_names:
                alias_map[name] = obj

    # Spacial Deduplication
    others = [obj for obj in unique_list if any(cat.startswith("NGC ") or cat.startswith("IC ") for cat in obj.catalog_names)]
    priority_objs = [obj for obj in unique_list if any(cat.startswith("M ") for cat in obj.catalog_names)]

    idx_matched, dists = CrossMatchUtils.spatial_cross_match(others, priority_objs)

    
    to_remove = set()
    for i, p_obj in enumerate(priority_objs):
        # Near objects are considered duplicates
        if dists and i < len(dists) and dists[i] < dist_threshold:
            other_obj = others[idx_matched[i]]
            
            # Others only, not the same object
            if id(p_obj) != id(other_obj):
                _merge_objects(p_obj, other_obj)
                to_remove.add(id(other_obj))
                
    return [o for o in unique_list if id(o) not in to_remove]

def _merge_objects(target, source):
    """Merge the information of two objects."""
    target.catalog_names = list(set(target.catalog_names) | set(source.catalog_names))
    target.common_names = list(set(target.common_names) | set(source.common_names))
    if target.mag is None: target.mag = source.mag
    if target.size_arcmin is None: target.size_arcmin = source.size_arcmin

def audit_catalog(stars, deep_sky):

    print("\n" + "="*40)
    print("CATALOG AUDIT")
    print("="*40)
    # 1. Volume Verification
    print(f"Total stars: {len(stars)}")
    print(f"Deep Sky Objects (DSO): {len(deep_sky)}")

    # 2. Infinite Names Test
    anomalies = [obj for obj in deep_sky if len(obj.catalog_names) > 15]
    if anomalies:
        print(f"ALERT: {len(anomalies)} objects found with excessive name aliases.")
        for a in anomalies[:3]:
            print(f" - {a.name}: {len(a.catalog_names)} names (e.g., {a.catalog_names[:3]}...)")
    else:
        print("Name Control: Clean (No objects with excessive aliases).")

    # 3. Messier-NGC Merger Verification
    m31 = next((o for o in deep_sky if "M 31" in o.catalog_names), None)
    if m31 and "NGC 224" in m31.catalog_names:
        print("Spatial Cross-Match: Functional (M 31 and NGC 224 merged).")
    else:
        print("Spatial Cross-Match: Possible failure (M 31 does not contain NGC 224).")

    # 4. Magnitude Integrity
    no_mag = [o for o in deep_sky if o.mag is None]
    if no_mag:
        print(f"Info: {len(no_mag)} DSOs without magnitude (standard for some catalogs).")
    print("="*40 + "\n")


def generate_catalog(
    output_file: str = "data/sidereal_catalog",
    const_input: str = "data/constellationship.fab",
    const_output: str = "data/constellationship.json",
    mag_limit: float = 6.0,
    dist_threshold: float = 2.5,
    debug:bool = False
):
    print("Starting Astronomical Catalog Generation Pipeline...")
    
    # 1. Parse FAB
    print("--- 1. Parsing Constellations (FAB) ---")
    min_stars_set, constellations_data = ParseUtils.parse_fab_file(const_input)
    
    
    # 2. Setup Registry
    registry = CatalogRegistry()
    registry.register(HipparcosProvider(mag_limit, min_stars_set))
    registry.register(MessierProvider())
    registry.register(NGCProvider())
    registry.register(ManualOverrideProvider())

    stars = []
    deep_sky = []

    # 3. Execute Providers
    print("\n--- 2. Fetching and Processing Catalogs ---")
    for provider in registry.get_providers():
        provider_name = provider.__class__.__name__
        print(f"[{provider_name}] starting...")
        try:
            results = provider.run()

            # Manual Override provider
            if isinstance(results, dict):
                stars.extend(results.get("stars", []))
                deep_sky.extend(results.get("deep_sky", []))
                
            # Other providers
            elif isinstance(results, list) and results:
                if isinstance(results[0], Star):
                    stars.extend(results)
                elif isinstance(results[0], DeepSky):
                    deep_sky.extend(results)
                else:
                    raise TypeError(f"Unknown type {type(results[0])}")

            print(f"[{provider_name}] completed successfully.")
        except Exception as e:
            print(f"[{provider_name}] failed: {e}")

    # 4. Cross Matching (NGC/IC vs Messier)
    print("\n--- 3. Merging Messier and NGC/IC catalogs ---")
    final_deep_sky=merge_messier_ngc(deep_sky, dist_threshold)
    
    # Clean unique names and recalculate default_name with proper ranking
    for obj in final_deep_sky + stars:
        obj_class = Star if isinstance(obj, Star) else type(obj)

        obj.catalog_names = NamingUtils.clean_catalog_list(NamingUtils.sort_catalogs(set(obj.catalog_names)))
        obj.common_names = sorted(list(set(obj.common_names)))
        obj.name = NamingUtils.choose_default_name(obj.common_names, obj.catalog_names)

        obj.id = NamingUtils.generate_iau_id(obj.ra_j2000, obj.dec_j2000, obj_class)
    

    stars.sort(key=lambda x: (x.ra_j2000, x.dec_j2000))
    final_deep_sky.sort(key=lambda x: (x.ra_j2000, x.dec_j2000))


    print("\n--- Translating Constellation HIP IDs to IAU IDs ---")
    
    # Dictionary to translate HIP -> ID
    hip_to_iau = {}
    for star in stars:
        for cat in star.catalog_names:
            if cat.startswith("HIP "):
                try:
                    hip_num = int(cat.split()[1])
                    hip_to_iau[hip_num] = star.id
                except ValueError:
                    pass
    # Do the translation
    if constellations_data:
        for const in constellations_data.constellations:
            mapped_ids = []
            for hip_num in const.stars_ids:
                mapped_ids.append(hip_to_iau.get(hip_num, f"UNKNOWN_HIP_{hip_num}"))
            const.stars_ids = mapped_ids
            
        print(f"Saving translated constellations to {const_output}")
        with open(const_output, "w", encoding="utf-8") as f:
            json.dump(constellations_data.model_dump(), f, ensure_ascii=False, indent=4)


    # 5. Generate Metadata
    print("\n--- 4. Generating Metadata ---")
    metadata = MetadataUtils.generate_metadata(stars, final_deep_sky)
    
    catalog_data = CatalogData(stars=stars, deep_sky=final_deep_sky)
    
    final_catalog = AstronomicalCatalog(
        metadata=metadata,
        data=catalog_data
    )
        
    # 6. Export to JSON    
    json_file = output_file + ".json"
    print(f"--- 5. Exporting data to JSON {json_file} ---")
    with open(json_file, "w", encoding="utf-8") as f:
        dump_func = getattr(final_catalog, 'model_dump', final_catalog.model_dump())
        json.dump(dump_func(), f, ensure_ascii=False, indent=4)


    # 7. Export to PICKLE
    pickle_file = output_file + ".pkl"
    print(f"--- 6. Exporting data to Pickle: {pickle_file} ---")
    with open(pickle_file, "wb") as f:
        pickle.dump(final_catalog, f)

    if debug:
        audit_catalog(stars, final_deep_sky)
        
    print("Process completed successfully!")

    return final_catalog, constellations_data
    

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Astronomical Catalog Fetching pipeline")
    
    parser.add_argument("-ci","--const-input", type=str, default="data/constellationship.fab",
                        help="Path to the .fab file with constellation data.")
    parser.add_argument("-co","--const-output", type=str, default="data/constellationship.json",
                        help="Output path for saving the constellations in JSON.")
    parser.add_argument("-m","--mag-limit", type=float, default=6.0,
                        help="Maximum star magnitude.")
    parser.add_argument("-d","--dist-threshold", type=float, default=2.5,
                        help="Distance threshold for object merging.")
    parser.add_argument("-o","--output", type=str, default="data/sidereal_catalog",
                        help="Output path for the final result catalog in JSON and pkl.")
    parser.add_argument("-ns","--no-stats", action="store_true",
                    help="Disable final stats print")

    args = parser.parse_args()

    fab_path = Path(args.const_input)
    
    if not fab_path.exists():
        print(f"Error: Constellation data not found in '{args.const_input}'")
        sys.exit(1)


    try:
        generate_catalog(
            const_input=args.const_input,
            const_output=args.const_output,
            mag_limit=args.mag_limit,
            dist_threshold=args.dist_threshold,
            output_file=args.output,
            debug=not args.no_stats
        )
        print("Generation completed successfully!")
        
    except Exception as e:
        print(f"Unexpected error during generation: {e}")
        sys.exit(1)
    