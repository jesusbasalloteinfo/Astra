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
    """Loads all translation files from the 'locales' directory.

    Iterates through language subdirectories, parses JSON files into Pydantic models, 
    and caches them for global use.
    """
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
    """Retrieves the translation dictionary for a specific catalog and language.

    Args:
        catalog_type (str): The type of catalog ('sidereal', 'planetary', 'constellations').
        lang (str): The ISO language code.

    Returns:
        Dict[str, Union[TranslationEntry, ConstellationTranslationEntry]]: The translation map.
    """
    if lang not in translations_cache:
        return {}
    
    locale = translations_cache[lang]
    # Return the dictionary associated with the category
    return getattr(locale, catalog_type, {})


def localise_object(obj: TModel, lang_dict: Dict[str, Union[TranslationEntry, ConstellationTranslationEntry]]) -> TModel:
    """Injects localized strings into an astronomical object model.

    Updates names, descriptions, and other textual fields based on the 
    provided language dictionary.

    Args:
        obj (TModel): The Pydantic model instance to localize.
        lang_dict (Dict[str, Union[TranslationEntry, ConstellationTranslationEntry]]): 
            The dictionary of translations.

    Returns:
        TModel: A copy of the object with localized fields.
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


def localise_dict_payload(
    payload: MetadataCatalogPayload[Dict[str, TModel]], 
    lang_dict: dict
) -> MetadataCatalogPayload[Dict[str, TModel]]:
    """Localizes a payload containing a dictionary of objects.

    Args:
        payload (MetadataCatalogPayload): The payload containing the 'data' dictionary.
        lang_dict (dict): The translation map.

    Returns:
        MetadataCatalogPayload: The localized payload.
    """
    if not lang_dict:
        return payload

    localised_data = {
        k: localise_object(v, lang_dict) 
        for k, v in payload.data.items()
    }
    
    return payload.model_copy(update={"data": localised_data})


def localise_list_payload(
    payload: MetadataCatalogPayload[List[TModel]], 
    lang_dict: dict
) -> MetadataCatalogPayload[List[TModel]]:
    """Localizes a payload containing a list of objects.

    Args:
        payload (MetadataCatalogPayload): The payload containing the 'data' list.
        lang_dict (dict): The translation map.

    Returns:
        MetadataCatalogPayload: The localized payload.
    """
    if not lang_dict:
        return payload

    localised_data = [localise_object(item, lang_dict) for item in payload.data]
    
    return payload.model_copy(update={"data": localised_data})
