"""Search tools for SearXNG MCP."""

import logging
from typing import Dict, Any, List, Optional, Literal
import requests
from mcp.types import TextContent


class SearchTools:
    """Tools for searching via SearXNG."""

    def __init__(self, searxng_url: str, timeout: int = 10):
        """Initialize search tools.

        Args:
            searxng_url: SearXNG instance URL
            timeout: Request timeout in seconds
        """
        self.searxng_url = searxng_url.rstrip("/")
        self.timeout = timeout
        self.logger = logging.getLogger("searxng-mcp.search")

    def _search(
        self,
        query: str,
        category: Optional[str] = None,
        engines: Optional[str] = None,
        language: str = "en",
        page: int = 1
    ) -> Dict[str, Any]:
        """Internal search method.

        Args:
            query: Search query
            category: Search category (general, images, videos, news, etc.)
            engines: Comma-separated list of engines
            language: Search language
            page: Page number

        Returns:
            Search results from SearXNG
        """
        params = {
            "q": query,
            "format": "json",
            "language": language,
            "pageno": page
        }

        if category:
            params["categories"] = category

        if engines:
            params["engines"] = engines

        try:
            self.logger.info(f"Searching: {query} (category: {category})")
            response = requests.get(
                f"{self.searxng_url}/search",
                params=params,
                timeout=self.timeout
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            self.logger.error(f"Search failed: {e}")
            raise RuntimeError(f"Search failed: {e}")

    def _deduplicate_results(self, results: List[Dict]) -> List[Dict]:
        """Remove duplicate results by URL.

        Args:
            results: List of search results

        Returns:
            Deduplicated list
        """
        seen_urls = set()
        unique_results = []

        for result in results:
            url = result.get('url', '')
            if url and url not in seen_urls:
                seen_urls.add(url)
                unique_results.append(result)

        return unique_results

    def search(
        self,
        query: str,
        category: Literal["general", "news"] = "general",
        engines: Optional[str] = None,
        max_results: int = 10
    ) -> List[TextContent]:
        """Quick search for web or news.

        Args:
            query: Search query
            category: "general" for web search, "news" for news
            engines: Comma-separated engine list (e.g., "google,bing,brave")
            max_results: Maximum results to return

        Returns:
            Formatted search results
        """
        results = self._search(query, category=category, engines=engines)

        if category == "news":
            output = f"📰 News Results for: {query}\n\n"
        else:
            output = f"🔍 Search Results for: {query}\n\n"

        for i, result in enumerate(results.get("results", [])[:max_results], 1):
            output += f"{i}. **{result.get('title', 'No title')}**\n"
            output += f"   {result.get('url', '')}\n"
            if result.get('content'):
                content = result['content'][:200] + "..." if len(result['content']) > 200 else result['content']
                output += f"   {content}\n"
            if category == "news" and result.get('publishedDate'):
                output += f"   📅 {result['publishedDate']}\n"
            output += "\n"

        if not results.get("results"):
            output += "No results found.\n"

        return [TextContent(type="text", text=output)]

    def search_media(
        self,
        query: str,
        media_type: Literal["images", "videos"] = "images",
        engines: Optional[str] = None,
        max_results: int = 10
    ) -> List[TextContent]:
        """Search for images or videos.

        Args:
            query: Search query
            media_type: "images" or "videos"
            engines: Comma-separated engine list
            max_results: Maximum results to return

        Returns:
            Formatted media search results
        """
        results = self._search(query, category=media_type, engines=engines)

        if media_type == "images":
            output = f"🖼️ Image Results for: {query}\n\n"
            for i, result in enumerate(results.get("results", [])[:max_results], 1):
                output += f"{i}. **{result.get('title', 'No title')}**\n"
                output += f"   URL: {result.get('img_src', 'N/A')}\n"
                output += f"   Source: {result.get('url', 'N/A')}\n"
                if result.get('thumbnail_src'):
                    output += f"   Thumbnail: {result['thumbnail_src']}\n"
                output += "\n"
        else:  # videos
            output = f"🎥 Video Results for: {query}\n\n"
            for i, result in enumerate(results.get("results", [])[:max_results], 1):
                output += f"{i}. **{result.get('title', 'No title')}**\n"
                output += f"   {result.get('url', '')}\n"
                if result.get('content'):
                    output += f"   {result['content']}\n"
                if result.get('publishedDate'):
                    output += f"   Published: {result['publishedDate']}\n"
                output += "\n"

        if not results.get("results"):
            output += f"No {media_type} found.\n"

        return [TextContent(type="text", text=output)]

    def research_topic(
        self,
        query: str,
        depth: Literal["quick", "standard", "deep"] = "standard"
    ) -> List[TextContent]:
        """Deep research with multiple searches and deduplication.

        Performs multiple searches with different strategies to gather
        comprehensive information from diverse sources. Automatically
        deduplicates results.

        Args:
            query: Research topic
            depth: Research depth
                - quick: 2 searches, ~15 unique results
                - standard: 4 searches, ~30 unique results
                - deep: 6 searches, ~50 unique results

        Returns:
            Deduplicated and aggregated research results
        """
        self.logger.info(f"Starting {depth} research on: {query}")

        all_results = []
        search_strategies = []

        # Define search strategies based on depth
        if depth == "quick":
            search_strategies = [
                {"category": "general", "engines": None},
                {"category": "news", "engines": None},
            ]
            max_per_search = 10
        elif depth == "standard":
            search_strategies = [
                {"category": "general", "engines": "google,bing"},
                {"category": "general", "engines": "duckduckgo,brave"},
                {"category": "news", "engines": None},
                {"category": "general", "engines": "wikipedia"},
            ]
            max_per_search = 10
        else:  # deep
            search_strategies = [
                {"category": "general", "engines": "google,bing"},
                {"category": "general", "engines": "duckduckgo,brave"},
                {"category": "news", "engines": "google,bing"},
                {"category": "news", "engines": "duckduckgo"},
                {"category": "general", "engines": "wikipedia"},
                {"category": "general", "engines": None},  # All engines
            ]
            max_per_search = 15

        # Execute all searches
        for strategy in search_strategies:
            try:
                results = self._search(
                    query,
                    category=strategy["category"],
                    engines=strategy["engines"]
                )
                all_results.extend(results.get("results", [])[:max_per_search])
            except Exception as e:
                self.logger.warning(f"Search strategy failed: {e}")
                continue

        # Deduplicate
        unique_results = self._deduplicate_results(all_results)

        # Format output - present as raw material to analyze, not numbered references
        output = f"🔬 RESEARCH DATA for analysis: {query}\n"
        output += f"📊 {len(unique_results)} unique sources gathered from {len(search_strategies)} search strategies\n\n"
        output += f"{'='*80}\n"
        output += f"RAW SOURCE MATERIAL (analyze and synthesize - do NOT list to user):\n"
        output += f"{'='*80}\n\n"

        for result in unique_results[:25]:
            output += f"• **{result.get('title', 'No title')}**\n"
            output += f"  URL: {result.get('url', '')}\n"
            if result.get('content'):
                content = result['content'][:100] + "..." if len(result['content']) > 100 else result['content']
                output += f"  Content: {content}\n"

            if result.get('publishedDate'):
                output += f"  Date: {result['publishedDate']}\n"

            output += "\n"

        if not unique_results:
            output += "No results found. Try a different query.\n"

        output += f"\n{'='*80}\n"
        output += f"⚠️  YOUR TASK: ANALYZE & SYNTHESIZE (NOT list sources!)\n"
        output += f"{'='*80}\n\n"
        output += f"You have {min(len(unique_results), 25)} sources above as RAW MATERIAL.\n\n"
        output += f"REQUIRED ANALYSIS PROCESS:\n"
        output += f"1. Read all source titles and content snippets above\n"
        output += f"2. Extract key claims and facts from the content\n"
        output += f"3. Cross-reference: What do MULTIPLE sources say? (HIGH confidence)\n"
        output += f"4. What's only in ONE source? (LOW confidence - note as unverified)\n"
        output += f"5. Any contradictions between sources? (flag for user)\n\n"
        output += f"REQUIRED OUTPUT FORMAT:\n"
        output += f"- Executive summary (2-3 sentences)\n"
        output += f"- Key findings with confidence indicators:\n"
        output += f"  ✓ HIGH (5+ sources agree)\n"
        output += f"  ~ MEDIUM (2-4 sources)\n"
        output += f"  ? LOW (single source only)\n"
        output += f"- Contradictions/uncertainties if any\n"
        output += f"- Brief conclusion\n\n"
        output += f"DO NOT output source URLs or numbered lists - synthesize into narrative!\n"
        output += f"{'='*80}\n"

        return [TextContent(type="text", text=output)]
