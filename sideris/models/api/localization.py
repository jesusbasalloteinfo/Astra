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
