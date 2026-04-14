import json
from pathlib import Path
from typing import Dict, Any, List, TypeVar
from pydantic import BaseModel
from models.api.common import MetadataCatalogPayload

# Translations loaded
translations_cache: Dict[str, Dict[str, Any]] = {}

# A pydantic model
TModel = TypeVar('TModel', bound=BaseModel)

def load_translations():
    """Load all translations from locales"""
    locales_dir = Path("locales")
    
    if not locales_dir.exists():
        return

    for file_path in locales_dir.glob("*.json"):
        lang_code = file_path.stem  # Get locale tag
        with open(file_path, "r", encoding="utf-8") as f:
            translations_cache[lang_code] = json.load(f)
            
    print(f"Loaded languages: {list(translations_cache.keys())}")

def get_lang_dict(catalog_type: str, lang: str) -> dict:
    """ Get the language dict"""
    if lang == "en" or lang not in translations_cache:
        return {}
    return translations_cache[lang].get(catalog_type, {})


def localise_object(obj: TModel, lang_dict: dict) -> TModel:
    """
    Localises an object and injects translations
    """
    if not lang_dict:
        return obj
        
    # Can be a constellation or Sidereal/Planetary
    obj_id = getattr(obj, "id", None) or getattr(obj, "abbr", None)
    if not obj_id:
        return obj

    translation = lang_dict.get(str(obj_id)) or lang_dict.get(str(obj_id).lower())
    if not translation:
        return obj

    original_name = getattr(obj, "name")
    translated_name = translation.get("name", original_name)

    updates = {"name": translated_name}
    
    if hasattr(obj, "common_names"):
        # Add to common names
        transl_common = translation.get("common_names", [])
        orig_common = getattr(obj, "common_names", [])

        combined = [translated_name, original_name] + transl_common + orig_common

        # Remove duplicates
        updates["common_names"] = list(dict.fromkeys([n for n in combined if n]))
        
    return obj.model_copy(update=updates)


# 2. Inyector específico para Payloads que contienen diccionarios
def localise_dict_payload(
    payload: MetadataCatalogPayload[Dict[str, TModel]], 
    lang_dict: dict
) -> MetadataCatalogPayload[Dict[str, TModel]]:
    
    if not lang_dict:
        return payload

    localised_data = {
        k: localise_object(v, lang_dict) 
        for k, v in payload.data.items()
    }
    
    return payload.model_copy(update={"data": localised_data})


# 3. Inyector específico para Payloads que contienen listas
def localise_list_payload(
    payload: MetadataCatalogPayload[List[TModel]], 
    lang_dict: dict
) -> MetadataCatalogPayload[List[TModel]]:
    
    if not lang_dict:
        return payload

    localised_data = [localise_object(item, lang_dict) for item in payload.data]
    
    return payload.model_copy(update={"data": localised_data})