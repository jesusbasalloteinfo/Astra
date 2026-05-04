from pydantic import BaseModel, Field
from typing import List, Dict, Optional

class TranslationEntry(BaseModel):
    """
    Generic translation entry for an object.
    """
    name: str = Field(..., description="Translated name of the object")
    common_names: List[str] = Field(default_factory=list, description="Additional translated common names")
    description: Optional[str] = None
    fun_fact: Optional[str] = None
    visual_tip: Optional[str] = None
    wikipedia_qid: Optional[str] = None

class ConstellationTranslationEntry(BaseModel):
    """
    Translation entry for a constellation.
    Usually only requires the name.
    """
    name: str = Field(..., description="Translated name of the constellation")

class LanguageLocale(BaseModel):
    """
    Represents all translations for a language.
    """
    planetary: Dict[str, TranslationEntry] = Field(default_factory=dict)
    sidereal: Dict[str, TranslationEntry] = Field(default_factory=dict)
    constellations: Dict[str, ConstellationTranslationEntry] = Field(default_factory=dict)
