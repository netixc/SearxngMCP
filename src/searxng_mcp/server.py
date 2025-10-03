"""Main server implementation for SearXNG MCP."""

import logging
import sys
from typing import Optional, Annotated, Literal

from mcp.server.fastmcp import FastMCP
from pydantic import Field

from .config import load_config
from .tools import SearchTools

# Tool descriptions
SEARCH_DESC = """Quick search for web or news content.

Use this when:
- User asks for a simple web search or lookup
- Need quick information, not comprehensive research
- Looking for news articles on a topic

This runs a SINGLE search and returns up to max_results (default 10).
For comprehensive research with multiple sources, use research_topic instead.

Parameters:
query* - What to search for
category - "general" for web search, "news" for news articles (default: general)
engines - Optional: Specific engines (e.g., "google,bing")
max_results - Number of results (default: 10, max: 50)

Returns: Search results with titles, URLs, and snippets"""

SEARCH_MEDIA_DESC = """Search for images or videos.

Use this when:
- User wants to find images or photos
- Looking for video content
- "show me pictures of..." or "find videos about..."

Parameters:
query* - What to find
media_type - "images" or "videos" (default: images)
engines - Optional: Specific engines
max_results - Number of results (default: 10, max: 50)

Returns: Media URLs with thumbnails and sources"""

RESEARCH_TOPIC_DESC = """Deep research with multiple searches and source validation.

Use this when:
- User wants comprehensive research or briefing
- Need to validate information across multiple sources
- Looking for in-depth analysis
- User asks to "research", "investigate", or "give me a briefing"

This tool runs 2-6 searches automatically using different strategies:
- Searches multiple engines (Google, Bing, DuckDuckGo, Brave, Wikipedia)
- Searches both general web and news sources
- Deduplicates results across all searches
- Returns 15-50 UNIQUE sources depending on depth

Perfect for creating comprehensive briefings with validated information.

Parameters:
query* - Research topic
depth - Research thoroughness:
  • "quick" - 2 searches, ~15 unique sources
  • "standard" - 4 searches, ~30 unique sources (recommended)
  • "deep" - 6 searches, ~50 unique sources

CRITICAL - After receiving sources, you MUST:
1. Read and analyze ALL sources provided (titles, URLs, content snippets)
2. Cross-reference claims across multiple sources
3. Identify facts confirmed by many sources (high confidence)
4. Note contradictions or single-source claims (lower confidence)
5. Synthesize findings into a comprehensive briefing with:
   • Executive summary of key findings
   • Main facts/developments (note how many sources confirm each)
   • Contradictions or uncertainties
   • Source quality assessment (which engines found what)
6. DO NOT just list the sources - you must analyze, validate, and synthesize them into actionable intelligence

Returns: Research briefing with analyzed, validated, cross-referenced information"""


class SearxngMCPServer:
    """Main server class for SearXNG MCP."""

    def __init__(self, config_path: Optional[str] = None):
        """Initialize the server.

        Args:
            config_path: Path to configuration file
        """
        self.config = load_config(config_path)
        self._setup_logging()

        # Initialize search tools
        self.search_tools = SearchTools(
            self.config.searxng.url,
            self.config.searxng.timeout
        )

        # Initialize MCP server
        self.mcp = FastMCP("SearxngMCP")
        self._setup_tools()

    def _setup_logging(self) -> None:
        """Configure logging."""
        handlers = []

        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(
            logging.Formatter(self.config.logging.format)
        )
        handlers.append(console_handler)

        # File handler if specified
        if self.config.logging.file:
            file_handler = logging.FileHandler(self.config.logging.file)
            file_handler.setFormatter(
                logging.Formatter(self.config.logging.format)
            )
            handlers.append(file_handler)

        # Configure root logger
        logging.basicConfig(
            level=getattr(logging, self.config.logging.level.upper()),
            handlers=handlers,
            force=True
        )

        self.logger = logging.getLogger("searxng-mcp")
        self.logger.info("SearXNG MCP Server initialized")
        self.logger.info(f"SearXNG URL: {self.config.searxng.url}")

    def _setup_tools(self) -> None:
        """Register MCP tools with the server."""

        @self.mcp.tool(description=SEARCH_DESC)
        def search(
            query: Annotated[str, Field(description="Search query")],
            category: Annotated[Literal["general", "news"], Field(description="Search category")] = "general",
            engines: Annotated[Optional[str], Field(description="Comma-separated engine list")] = None,
            max_results: Annotated[int, Field(description="Maximum results", ge=1, le=50)] = 10
        ):
            return self.search_tools.search(query, category, engines, max_results)

        @self.mcp.tool(description=SEARCH_MEDIA_DESC)
        def search_media(
            query: Annotated[str, Field(description="Media search query")],
            media_type: Annotated[Literal["images", "videos"], Field(description="Type of media")] = "images",
            engines: Annotated[Optional[str], Field(description="Comma-separated engine list")] = None,
            max_results: Annotated[int, Field(description="Maximum results", ge=1, le=50)] = 10
        ):
            return self.search_tools.search_media(query, media_type, engines, max_results)

        @self.mcp.tool(description=RESEARCH_TOPIC_DESC)
        def research_topic(
            query: Annotated[str, Field(description="Research topic or question")],
            depth: Annotated[Literal["quick", "standard", "deep"], Field(description="Research depth")] = "standard"
        ):
            return self.search_tools.research_topic(query, depth)

    async def run(self):
        """Run the MCP server."""
        await self.mcp.run_stdio_async()


def main():
    """Main entry point for the SearXNG MCP server."""
    import argparse
    import anyio

    parser = argparse.ArgumentParser(description='SearXNG MCP Server')
    parser.add_argument(
        '--config',
        help='Path to configuration file'
    )
    args = parser.parse_args()

    async def run_server():
        try:
            server = SearxngMCPServer(config_path=args.config)
            await server.run()
        except Exception as e:
            print(f"Error: {e}", file=sys.stderr)
            sys.exit(1)

    try:
        anyio.run(run_server)
    except KeyboardInterrupt:
        sys.exit(0)


if __name__ == "__main__":
    main()
