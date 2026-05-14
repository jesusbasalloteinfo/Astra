from pydantic import BaseModel, Field
from functools import partial
from services.assistant.tools import CurriedTool
from .WikiEngine import WikiEngine


wiki = WikiEngine(lang="en")

# ==========================================
# 1. PYDANTIC MODELS
# ==========================================

class SearchArticleArgs(BaseModel):
    query: str = Field(..., description="The query to search in Wikipedia. Use broad terms.")
    limit: int = Field(default=10, description="Max number of results to return. Default is 10.")

class GetArticleIntroArgs(BaseModel):
    qid: str = Field(..., description="The Wikidata QID of the article (e.g., 'Q111'). You MUST obtain this ID using the 'search_articles' tool first.")

class GetArticleSectionArgs(BaseModel):
    qid: str = Field(..., description="The Wikidata QID of the article (e.g., 'Q111').")
    section_index: str = Field(..., description="The exact section index number. You MUST get this number from the Table of Contents provided by 'get_article_intro'.")

class GetArticleInfotableArgs(BaseModel):
    qid: str = Field(..., description="The Wikidata QID of the article (e.g., 'Q111').")


# ==========================================
# 2. TOOL CREATORS 
# ==========================================

def create_search_article_tool(wiki_instance: WikiEngine) -> CurriedTool:
    return CurriedTool(
        name="search_wiki_articles",
        description="Searches Wikipedia and returns a list of matching articles with their Q-IDs. ALWAYS use this first to find the correct Q-ID for a topic.",
        args_model=SearchArticleArgs,
        func=wiki_instance.search_articles
    )

def create_get_article_intro_tool(wiki_instance: WikiEngine) -> CurriedTool:
    return CurriedTool(
        name="get_wiki_article_intro",
        description="Gets the article's introduction and Table of Contents (TOC). Use this to understand the summary and to find the 'section_index' numbers for deeper reading.",
        args_model=GetArticleIntroArgs,
        func=wiki_instance.get_intro_toc
    )

def create_get_article_section_tool(wiki_instance: WikiEngine) -> CurriedTool:
    return CurriedTool(
        name="get_wiki_article_section",
        description="Gets the full Markdown text of a specific section of the article. Requires a section_index obtained from the TOC.",
        args_model=GetArticleSectionArgs,
        func=wiki_instance.get_section
    )

def create_get_article_infotable_tool(wiki_instance: WikiEngine) -> CurriedTool:
    return CurriedTool(
        name="get_wiki_article_infotable",
        description="Gets the structured data (Infobox) of the article parsed as Markdown tables. Highly recommended for finding precise numbers, dates, formulas, or specific facts.",
        args_model=GetArticleInfotableArgs,
        func=wiki_instance.get_infotable
    )