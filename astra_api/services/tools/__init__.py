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

# services/tools/__init__.py

from .wikipedia import (
    WikiEngine,
    WikiError,
    WikiNotFoundError,
    create_search_article_tool,
    create_get_article_intro_tool,
    create_get_article_section_tool,
    create_get_article_infotable_tool
)
from .observation import (
    fly_to_const_tool,
    focus_object_element_tool,
    search_object_tool,
    get_object_details_tool,
    slew_to_object_tool
)

__all__ = [
    "WikiEngine",
    "WikiError",
    "WikiNotFoundError",
    "create_search_article_tool",
    "create_get_article_intro_tool",
    "create_get_article_section_tool",
    "create_get_article_infotable_tool",
    "fly_to_const_tool",
    "focus_object_element_tool",
    "search_object_tool",
    "get_object_details_tool",
    "slew_to_object_tool"
]