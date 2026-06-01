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

# services/tools/wikipedia/__init__.py

from .WikiEngine import WikiEngine, WikiError, WikiNotFoundError
from .tools import (
    create_search_article_tool,
    create_get_article_intro_tool,
    create_get_article_section_tool,
    create_get_article_infotable_tool
)

__all__ = [
    "WikiEngine",
    "WikiError",
    "WikiNotFoundError",
    "create_search_article_tool",
    "create_get_article_intro_tool",
    "create_get_article_section_tool",
    "create_get_article_infotable_tool"
]