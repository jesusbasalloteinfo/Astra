import asyncio
import urllib.parse
import httpx
from bs4 import BeautifulSoup
import markdownify

class WikiError(Exception):
    """Base Exception."""
    pass

class WikiNotFoundError(WikiError):
    """Raised when no info was found."""
    pass


class WikiEngine:
    """
    Engine for interacting with the Wikipedia and Wikidata APIs.

    Provides high-level methods to search for articles, fetch introductions,
    parse tables of contents, and extract structured infobox data as Markdown.
    """
    def __init__(self, lang="en", user_agent="WikiBot/1.0 (contact: email@example.com)"):
        """
        Initializes the WikiEngine.

        Args:
            lang (str): The language code for Wikipedia (e.g., 'en', 'es').
            user_agent (str): The User-Agent header to use for API requests.
        """
        self.lang = lang
        self.headers = {"User-Agent": user_agent, "Accept": "application/json"}
        self.wiki_api_base = f"https://{lang}.wikipedia.org/w/api.php"
        self.wikidata_api_base = "https://www.wikidata.org/w/api.php"
        
        # Banned Table of Contents (TOC) sections
        self.banned_toc_dict = {
            "en": ["See also", "References", "External links", "Further reading", "Notes", "Sources", "Bibliography"],
            "ca": ["Referències", "Bibliografia", "Enllaços externs", "Vegeu també", "Notes", "Fonts", "Lectura adicional"],
            "es": ["Véase también", "Referencias", "Enlaces externos", "Bibliografía", "Notas", "Fuentes", "Lectura adicional"],
            "fr": ["Voir aussi", "Notes et références", "Annexes", "Bibliographie", "Liens externes"],
            "de": ["Siehe auch", "Literatur", "Weblinks", "Einzelnachweise", "Quellen"]
        }
        self.banned_toc = self.banned_toc_dict.get(self.lang, self.banned_toc_dict["en"])
        
        # Keep an open session for faster, reused TCP connections
        self.client = httpx.AsyncClient(headers=self.headers, timeout=30.0)
        self._cache = {}
    
    async def close(self):
        """Close the HTTP session at the end"""
        await self.client.aclose()

    
    # ==========================================
    # INTERNAL METHODS (API Requests)
    # ==========================================

    async def _make_request(self, url: str, use_cache: bool = True) -> dict:
        """Execute HTTP request with error handling and optional caching."""
        if use_cache and url in self._cache:
            # Cache hit!
            return self._cache[url]

        try:
            response = await self.client.get(url)
            response.raise_for_status()
            data = response.json()
            
            if use_cache:
                self._cache[url] = data 
                
            return data
            
        except httpx.HTTPError as e:
            raise WikiError(f"HTTP Request failed: {str(e)}")
    
    async def _resolve_qid(self, qid: str) -> str:
        """Resolve a Wikidata QID to the specific localized Wikipedia URL."""
        url = f"{self.wikidata_api_base}?action=wbgetentities&ids={qid}&props=sitelinks/urls&format=json"
        data = await self._make_request(url)
        sitelinks = data.get("entities", {}).get(qid, {}).get("sitelinks", {})

        resolve_url = sitelinks.get(f"{self.lang}wiki", {}).get("url")
        
        if not resolve_url:
            raise WikiNotFoundError(f"Article for QID '{qid}' not found or not available in language '{self.lang}'.")
            
        return resolve_url

    async def _get_title(self, qid:str) -> str:
        """Extract the exact article title from a QID"""
        url = await self._resolve_qid(qid)
        return url.split('wiki/')[-1]

    async def _request_search_article(self, query:str, limit:int) -> str:
        """Query the Wikipedia Search API."""
        url = (
            f"{self.wiki_api_base}?action=query"
            f"&generator=search&gsrsearch={urllib.parse.quote(query)}&gsrlimit={limit}"
            f"&prop=description|pageprops|info|categories"
            f"&inprop=url"      
            f"&ppprop=wikibase_item"
            f"&format=json"
            f"&formatversion=2" # So that pages is a list
        )
        data = await self._make_request(url, use_cache=False)

        if not data or "query" not in data or "pages" not in data["query"]:
            raise WikiNotFoundError(f"No search results found for {query}")

        return data

    async def _request_article_section(self, title:str, section:int) -> str:
        """Fetch the raw HTML of a specific article section."""
        url = f"{self.wiki_api_base}?action=parse&page={title}&prop=text&section={section}&format=json&redirects=1"
        data = await self._make_request(url)
        if not data or "parse" not in data:
            raise WikiNotFoundError(f"Article {title} or section not found")
        return data

    async def _request_article_TOC(self, title:str) -> str:
        """Fetch the Table of Contents data."""
        url = f"{self.wiki_api_base}?action=parse&page={title}&prop=sections&format=json&redirects=1"
        data = await self._make_request(url)
        if not data:
            raise WikiNotFoundError(f"Article {title} TOC not found")
        return data
    

    # ==========================================
    # INTERNAL METHODS (HTML Parsing & Cleaning)
    # ==========================================

    def _format_wiki_links(self, soup: BeautifulSoup):
        """Helper to clean and format internal Wikipedia links."""
        for a in soup.find_all("a"):
            href = a.get("href", "")
            if href.startswith("/wiki/") and ":" not in href:
                title_clean = urllib.parse.unquote(href.split("/wiki/")[-1]).replace("_", " ").split("#")[0]
                a["href"] = "wiki/" + title_clean
                if "title" in a.attrs:
                    del a["title"]
            else:
                a.unwrap() # Remove link formatting for external or file links

    def _clean_html(self, html_content: str) -> str:
        """Clean raw HTML from wikinoise, adapting it for Markdown"""
        soup = BeautifulSoup(html_content, "html.parser")
        
        # STEP 1: PRESERVE MATH FORMULAS (LaTeX)
        # MediaWiki renders math as complex HTML. We extract the raw LaTeX from the 'alt' attribute
        # of the fallback image BEFORE we destroy all images in Step 2.
        for math_span in soup.find_all(["span", "math"], class_="mwe-math-element"):
            img = math_span.find("img")
            if img and img.has_attr("alt"):
                latex_code = img["alt"].strip()
                
                # Safely remove '\displaystyle' without breaking trailing brackets
                if latex_code.startswith(r"{\displaystyle") and latex_code.endswith("}"):
                    latex_code = latex_code.replace(r"{\displaystyle ", "", 1).replace(r"{\displaystyle", "", 1)
                    latex_code = latex_code[:-1]
                
                # Wrap in <code> so Markdownify doesn't escape underscores (e.g., a\_1)
                new_tag = soup.new_tag("code")
                new_tag.string = f"${latex_code}$"
                
                parent_dd = math_span.find_parent("dd")
                parent_dl = math_span.find_parent("dl")
                
                math_span.replace_with(new_tag)
                
                # Remove indentation tags (<dl>, <dd>) wrapping the formula so it sits inline
                if parent_dd: parent_dd.unwrap()
                if parent_dl: parent_dl.unwrap()

        # STEP 2: REMOVE MULTIMEDIA
        for tag in soup.find_all(["figure", "img", "audio", "video", "sup"]):
            tag.decompose()

        # STEP 3: DESTROY METADATA & NAVBOXES
        # Remove massive footers, warning boxes, and references.
        classes_to_kill = [
            "reference", "reflist", "references", "mw-editsection",
            "error", "mw-ext-cite-error", "noprint", "hatnote", "mw-empty-elt", "ambox",
            "navbox", "vertical-navbox", "sidebar", "metadata", "infobox",
            "thumb", "thumbinner", "tright", "tleft", "gallery", 
            "multiple-image", "preview-warning"
        ]
        
        for tag in soup.find_all(class_=classes_to_kill):
            tag.decompose()
            

        # STEP 4: CLEAN LINKS
        self._format_wiki_links(soup)

        return str(soup)

    def _parse_infotable(self, html_content: str) -> dict:
        """Extract and semantically split the Infobox into a dictionary of Markdown tables."""
        
        soup = BeautifulSoup(html_content, "html.parser")
        infobox = soup.find("table", class_="infobox")
        
        if not infobox:
            raise WikiNotFoundError(f"Article Infotable not found")

        # STEP 1: CLEAN INFOBOX NOISE
        classes_to_kill = ["reference", "noprint", "mw-empty-elt", "infobox-image"]
        for tag in infobox.find_all(class_=classes_to_kill):
            tag.decompose()
            
        for tag in infobox.find_all(["sup"]):
            tag.decompose()

        self._format_wiki_links(soup)

        # STEP 2: REMOVE EMPTY ROWS
        # Prevents markdownify from creating broken rows like '| | |'
        for tr in infobox.find_all("tr"):
            if not tr.get_text(strip=True):
                tr.decompose()


        # STEP 3: FLATTEN NESTED TABLES (MARKDOWN COMPATIBILITY)
        # Markdown cannot render tables inside tables. We must convert inner tables 
        # into flat comma-separated text (e.g., "min, max ; 10, 20").
        for nested_table in infobox.find_all("table"):
            if nested_table == infobox:
                continue 
                
            rows_data = []
            for row in nested_table.find_all("tr"):
                # Use " " as separator so words don't stick together (e.g. "Surfacetemp")
                cells = [cell.get_text(" ", strip=True) for cell in row.find_all(["th", "td"])]
                cells = [c for c in cells if c]
                if cells:
                    rows_data.append(cells)
                    
            if not rows_data:
                nested_table.decompose()
                continue

            outer_td = nested_table.find_parent(["td", "th"])
            outer_tr = outer_td.find_parent("tr") if outer_td else None
            
            # Sub-case: The nested table spans the entire row (colspan=2).
            # We must extract the first element to act as the "Property" column.
            if outer_tr and len(outer_tr.find_all(["td", "th"], recursive=False)) == 1:
                if len(rows_data[0]) > 1:
                    prop_name = rows_data[0].pop(0) 
                else:
                    prop_name = rows_data[0][0]
                    rows_data.pop(0)
                    
                val_lines = [", ".join(r) for r in rows_data if r]
                val_text = " ; ".join(val_lines)
                
                # Reconstruct the outer row to force 2 perfect Markdown columns
                outer_tr.clear() 
                new_th = soup.new_tag("th")
                new_th.string = prop_name
                new_td = soup.new_tag("td")
                new_td.string = val_text
                outer_tr.append(new_th)
                outer_tr.append(new_td)
                
            # Sub-case: Standard nested table (already sitting in the "Value" column).
            else:
                val_lines = [", ".join(r) for r in rows_data if r]
                flat_text = " ; ".join(val_lines)
                new_tag = soup.new_tag("span")
                new_tag.string = flat_text
                nested_table.replace_with(new_tag)

        # STEP 4: SEMANTIC SPLITTING
        # Group rows into sub-tables based on Infobox headers (<th> with colspan)
        sub_tables = {}
        current_section = "General"
        current_html = ""

        for tr in infobox.find_all("tr"):
            th = tr.find("th")
            is_header = th and th.get("colspan") and len(tr.find_all(["th", "td"])) == 1
            
            if is_header:
                # Save the accumulated HTML into the previous section dictionary
                if current_html.strip():
                    # Inject generic <thead> to force valid Markdown table rendering
                    temp_table = f"<table><thead><tr><th>Property</th><th>Value</th></tr></thead><tbody>{current_html}</tbody></table>"
                    sub_tables[current_section] = markdownify.markdownify(temp_table, heading_style="ATX").strip()
                
                current_section = th.get_text(strip=True)
                current_html = ""
            else:
                current_html += str(tr)

        # Save the final accumulated block
        if current_html.strip():
            temp_table = f"<table><thead><tr><th>Property</th><th>Value</th></tr></thead><tbody>{current_html}</tbody></table>"
            sub_tables[current_section] = markdownify.markdownify(temp_table, heading_style="ATX").strip()

        if "General" in sub_tables and not sub_tables["General"]:
            del sub_tables["General"]
        
        return sub_tables


    # ==========================================
    # PUBLIC METHODS (Tools)
    # ==========================================

    async def search_articles(self, query: str, limit: int = 10) -> list[dict]:
        """
        Searches for Wikipedia articles matching a query.

        Args:
            query (str): The search term.
            limit (int): Maximum number of results to return.

        Returns:
            list[dict]: A list of dictionaries containing 'qid', 'title', 
                'description', and 'url'.

        Raises:
            WikiNotFoundError: If no matching articles are found.
        """
        
        data = await self._request_search_article(query, limit)
        
        # Parse response
        response = []
        for page_data in data["query"].get("pages", []):
            response.append({
                "qid": page_data.get("pageprops", {}).get("wikibase_item"),
                "title": page_data.get("title"),
                "description": page_data.get("description", "No description available"),
                "url": page_data.get("fullurl"),                
                "index": page_data.get("index", 99)
            })

        # Order by response index
        response.sort(key=lambda x: x["index"])

        # Clear index data from response (unnecesary)
        for res in response:
            del res["index"]

        return response

    async def get_intro_toc(self, qid: str) -> str:
        """
        Retrieves an article's introduction and its Table of Contents.

        Args:
            qid (str): The Wikidata QID of the article.

        Returns:
            str: A Markdown-formatted string containing the summary and TOC.
        """

        title = await self._get_title(qid)

        data_intro, data_toc = await asyncio.gather(
            self._request_article_section(title, 0),
            self._request_article_TOC(title)
        )

        # 1. Parse Introduction
        html_intro = data_intro["parse"]["text"]["*"]
        clean = self._clean_html(html_intro)
        intro_md = markdownify.markdownify(clean, heading_style="ATX").strip()

        # 2. Parse Table of Contents
        sections = data_toc.get("parse", {}).get("sections", [])
        toc_lines = []
        for s in sections:
            soup_line = BeautifulSoup(s['line'], "html.parser")

            # Remove references/notes from titles to avoid bugs like "Objects[4]"
            for tag in soup_line.find_all(class_=["reference", "mw-editsection"]):
                tag.decompose()
            for tag in soup_line.find_all("sup"): 
                tag.decompose()
                
            clean_line_html = str(soup_line)
            title_md = markdownify.markdownify(clean_line_html).strip()
            title_plain = soup_line.get_text().strip()

            if title_plain not in self.banned_toc:
                indent = "  " * (s['toclevel'] - 1)
                toc_lines.append(f"{indent}- {s['index']}: {title_md}")

        toc_text = "\n".join(toc_lines)

        final_message = f"{intro_md}\n\n# SECTIONS INDEX\n{toc_text}"

        return final_message

    async def get_section(self, qid: str, section_index: str) -> str:
        """
        Retrieves and formats a specific section of a Wikipedia article.

        Args:
            qid (str): The Wikidata QID of the article.
            section_index (str): The index of the section to retrieve.

        Returns:
            str: The Markdown-formatted content of the section.

        Raises:
            WikiNotFoundError: If the section content is missing.
        """
        title = await self._get_title(qid)
        raw_data = await self._request_article_section(title, section_index)

        html_content = raw_data["parse"].get("text", {}).get("*", "")
        if not html_content:
            raise WikiNotFoundError(f"Section {section_index} not found")

        clean = self._clean_html(html_content)
        return markdownify.markdownify(clean, heading_style="ATX").strip()

    async def get_infotable(self, qid: str) -> dict:
        """
        Extracts structured Infobox data from an article as Markdown tables.

        Args:
            qid (str): The Wikidata QID of the article.

        Returns:
            dict: A dictionary mapping section headers to Markdown tables.
        """
        title = await self._get_title(qid)
        raw_data = await self._request_article_section(title, 0)
        html_content = raw_data["parse"]["text"]["*"]
        return self._parse_infotable(html_content)

        