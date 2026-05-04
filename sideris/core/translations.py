import json
from pathlib import Path
from typing import Dict, Any, List, TypeVar, Union
from pydantic import BaseModel, ValidationError
from models.api.common import MetadataCatalogPayload
from models.api.localization import LanguageLocale, TranslationEntry, ConstellationTranslationEntry

# Translations loaded
translations_cache: Dict[str, LanguageLocale] = {}

# A pydantic model
TModel = TypeVar('TModel', bound=BaseModel)

def load_translations():
    """Load all translations from locales and validate with Pydantic"""
    # Use absolute path relative to this file (sideris/core/translations.py)
    # parent.parent goes up to 'sideris/'
    base_path = Path(__file__).parent.parent
    locales_dir = base_path / "locales"
    
    if not locales_dir.exists():
        print(f"Warning: Locales directory not found at {locales_dir.absolute()}")
        return

    # Iterate over directories in locales (each directory is a language)
    for lang_dir in locales_dir.iterdir():
        if lang_dir.is_dir():
            lang_code = lang_dir.name
            lang_data = {}
            
            # Collect all JSON data for this language
            for file_path in lang_dir.glob("*.json"):
                category = file_path.stem
                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        lang_data[category] = json.load(f)
                except Exception as e:
                    print(f"Error reading {file_path}: {e}")
            
            # Validate and convert to Pydantic model
            try:
                # model_validate ensures dictionaries are converted to the proper Pydantic models
                translations_cache[lang_code] = LanguageLocale.model_validate(lang_data)
            except ValidationError as e:
                print(f"Validation error for language '{lang_code}': {e}")
            except Exception as e:
                print(f"Unexpected error loading language '{lang_code}': {e}")
            
    print(f"Loaded languages: {list(translations_cache.keys())}")

def get_lang_dict(catalog_type: str, lang: str) -> Dict[str, Union[TranslationEntry, ConstellationTranslationEntry]]:
    """ Get the language dict for a specific catalog type """
    if lang not in translations_cache:
        return {}
    
    locale = translations_cache[lang]
    # Return the dictionary associated with the category
    return getattr(locale, catalog_type, {})


def localise_object(obj: TModel, lang_dict: Dict[str, Union[TranslationEntry, ConstellationTranslationEntry]]) -> TModel:
    """
    Localises an object and injects translations
    """
    if not lang_dict:
        return obj
        
    # Can be a constellation (abbr) or Sidereal/Planetary (id)
    obj_id = getattr(obj, "id", None) or getattr(obj, "abbr", None)
    if not obj_id:
        return obj

    # Look up translation entry
    translation = lang_dict.get(str(obj_id)) or lang_dict.get(str(obj_id).lower())
    if not translation:
        return obj

    # Extract name (both entry types have name)
    translated_name = translation.name
    updates = {"name": translated_name}
    
    # Handle common names if applicable (TranslationEntry only)
    if isinstance(translation, TranslationEntry):
        # Inject new optional fields
        if translation.description:
            updates["description"] = translation.description
        if translation.fun_fact:
            updates["fun_fact"] = translation.fun_fact
        if translation.visual_tip:
            updates["visual_tip"] = translation.visual_tip
        if translation.wikipedia_qid:
            updates["wikipedia_qid"] = translation.wikipedia_qid

        if hasattr(obj, "common_names"):
            original_name = getattr(obj, "name")
            transl_common = translation.common_names
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
