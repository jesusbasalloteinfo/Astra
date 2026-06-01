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

"""
Tool definitions for Wikipedia integration to be used by the AI assistant.
"""
from pydantic import BaseModel, Field
from services.assistant.tools import CurriedTool
from .WikiEngine import WikiEngine


wiki = WikiEngine(lang="en")

# ==========================================
# 1. PYDANTIC MODELS
# ==========================================

class SearchArticleArgs(BaseModel):
    """Arguments for searching Wikipedia articles."""
    query: str = Field(..., description="The query to search in Wikipedia. Use broad terms.")
    limit: int = Field(default=10, description="Max number of results to return. Default is 10.")

class GetArticleIntroArgs(BaseModel):
    """Arguments for fetching a Wikipedia article's introduction."""
    qid: str = Field(..., description="The Wikidata QID of the article (e.g., 'Q111'). You MUST obtain this ID using the 'search_articles' tool first.")

class GetArticleSectionArgs(BaseModel):
    """Arguments for fetching a specific section of a Wikipedia article."""
    qid: str = Field(..., description="The Wikidata QID of the article (e.g., 'Q111').")
    section_index: str = Field(..., description="The exact section index number. You MUST get this number from the Table of Contents provided by 'get_article_intro'.")

class GetArticleInfotableArgs(BaseModel):
    """Arguments for fetching a Wikipedia article's infobox."""
    qid: str = Field(..., description="The Wikidata QID of the article (e.g., 'Q111').")


# ==========================================
# 2. TOOL CREATORS 
# ==========================================

def create_search_article_tool(wiki_instance: WikiEngine) -> CurriedTool:
    """
    Creates a tool to search Wikipedia articles.

    Args:
        wiki_instance (WikiEngine): The Wikipedia engine instance.

    Returns:
        CurriedTool: The search article tool.
    """
    return CurriedTool(
        name="search_wiki_articles",
        description="Searches Wikipedia and returns a list of matching articles with their Q-IDs. ALWAYS use this first to find the correct Q-ID for a topic.",
        args_model=SearchArticleArgs,
        func=wiki_instance.search_articles
    )

def create_get_article_intro_tool(wiki_instance: WikiEngine) -> CurriedTool:
    """
    Creates a tool to fetch a Wikipedia article's introduction and TOC.

    Args:
        wiki_instance (WikiEngine): The Wikipedia engine instance.

    Returns:
        CurriedTool: The article intro tool.
    """
    return CurriedTool(
        name="get_wiki_article_intro",
        description="Gets the article's introduction and Table of Contents (TOC). Use this to understand the summary and to find the 'section_index' numbers for deeper reading.",
        args_model=GetArticleIntroArgs,
        func=wiki_instance.get_intro_toc
    )

def create_get_article_section_tool(wiki_instance: WikiEngine) -> CurriedTool:
    """
    Creates a tool to fetch a specific section of a Wikipedia article.

    Args:
        wiki_instance (WikiEngine): The Wikipedia engine instance.

    Returns:
        CurriedTool: The article section tool.
    """
    return CurriedTool(
        name="get_wiki_article_section",
        description="Gets the full Markdown text of a specific section of the article. Requires a section_index obtained from the TOC.",
        args_model=GetArticleSectionArgs,
        func=wiki_instance.get_section
    )

def create_get_article_infotable_tool(wiki_instance: WikiEngine) -> CurriedTool:
    """
    Creates a tool to fetch a Wikipedia article's infobox as Markdown tables.

    Args:
        wiki_instance (WikiEngine): The Wikipedia engine instance.

    Returns:
        CurriedTool: The article infotable tool.
    """
    return CurriedTool(
        name="get_wiki_article_infotable",
        description="Gets the structured data (Infobox) of the article parsed as Markdown tables. Highly recommended for finding precise numbers, dates, formulas, or specific facts.",
        args_model=GetArticleInfotableArgs,
        func=wiki_instance.get_infotable
    )
