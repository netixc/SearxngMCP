# 🔍 SearXNG MCP Server

A privacy-focused Model Context Protocol (MCP) server that provides Claude with web search capabilities through [SearXNG](https://github.com/searxng/searxng) metasearch engine.

<a href="https://glama.ai/mcp/servers/@netixc/SearxngMCP">
  <img width="380" height="200" src="https://glama.ai/mcp/servers/@netixc/SearxngMCP/badge" />
</a>

## ✨ Features

- 🔒 **Privacy-first** - No tracking, no data collection via SearXNG
- 🌐 **Multi-engine** - Aggregates results from Google, Bing, DuckDuckGo, Brave, and more
- 🎯 **Specialized search** - Web, images, videos, and news search
- ⚡ **Fast** - Optimized with minimal tool set (4 tools)
- 🐳 **Docker included** - SearXNG instance setup included
- 🛠️ **Easy setup** - Python-based with UV package manager

## 📦 Installation

### Prerequisites
- Python 3.10 or higher
- Docker and Docker Compose
- Git

### Quick Install

**1. Clone repository:**
```bash
git clone https://github.com/netixc/SearxngMCP.git
cd SearxngMCP
```

**2. Configure SearXNG:**

Edit the following files with your settings:

- `docker-compose.yml` - Replace `YOUR_IP` with your server's IP address
- `docker-compose.yml` - Replace `CHANGE_THIS_SECRET_KEY` with a secret key
- `searxng/settings.yml` - Replace `CHANGE_THIS_TO_YOUR_OWN_SECRET_KEY` with the same secret key
- `searxng-config/config.json` - Replace `YOUR_IP` with your server's IP address

Generate a secret key:
```bash
openssl rand -hex 32
```

**3. Start SearXNG instance:**
```bash
docker compose up -d
```

SearXNG will be available at `http://YOUR_IP:8080`

**4. Install MCP server (using UV - recommended):**
```bash
# Create venv and install
uv venv
source .venv/bin/activate  # Linux/macOS
uv pip install -e ".[dev]"
```

**5. Verify installation:**
```bash
# Check SearXNG is running
curl http://YOUR_IP:8080
```

## ⚙️ Configuration

### MCP Client Setup

Add to your MCP settings (e.g., Claude Desktop config):

```json
{
  "mcpServers": {
    "searxng": {
      "command": "/absolute/path/to/SearxngMCP/run-server.sh"
    }
  }
}
```

### SearXNG Configuration

The SearXNG instance is configured via `searxng/settings.yml`:
- Default engines: Google, Bing, DuckDuckGo, Brave, Wikipedia, YouTube
- JSON API enabled for MCP access
- Privacy features enabled (no tracking)
- Accessible on your LAN at YOUR_IP:8080

**IMPORTANT:** Before starting Docker, replace the following in your config files:
1. `docker-compose.yml`: Replace `YOUR_IP` and `CHANGE_THIS_SECRET_KEY`
2. `searxng/settings.yml`: Replace `CHANGE_THIS_TO_YOUR_OWN_SECRET_KEY`
3. `searxng-config/config.json`: Replace `YOUR_IP`

Generate secret key: `openssl rand -hex 32`

### MCP Server Configuration

Edit `searxng-config/config.json` (replace YOUR_IP with your server's IP):

```json
{
  "searxng": {
    "url": "http://YOUR_IP:8080",
    "timeout": 10
  },
  "logging": {
    "level": "INFO",
    "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    "file": null
  }
}
```

## 🔧 Available Tools

The server provides **3 optimized tools** designed for efficient research:

### 1. search - Quick Web/News Search
Quick single search for web or news content.

**Use when:**
- Need quick information or simple lookup
- User asks for a basic web search
- Looking for news on a topic

**Parameters:**
- `query*` - What to search for
- `category` - "general" (default) or "news"
- `engines` - Optional: Specific engines (e.g., "google,bing")
- `max_results` - Number of results (default: 10, max: 50)

**Example:**
```
User: What's the latest Python release?
Claude: [Calls search("latest Python release", category="general")]
```

### 2. search_media - Images & Videos
Search for images or videos.

**Use when:**
- User wants to find images or photos
- Looking for video content
- "show me pictures of..." or "find videos about..."

**Parameters:**
- `query*` - What to find
- `media_type` - "images" (default) or "videos"
- `engines` - Optional: Specific engines
- `max_results` - Number of results (default: 10, max: 50)

**Example:**
```
User: Show me pictures of Northern Lights
Claude: [Calls search_media("Northern Lights", media_type="images")]
```

### 3. research_topic - Deep Research ⭐
**Multi-search research with automatic analysis and synthesis.**

**Use when:**
- User wants comprehensive research or briefing
- Need to validate information across multiple sources
- User asks to "research", "investigate", or "analyze"
- Creating detailed reports with cross-referenced sources

**What it does:**
- Runs 2-6 searches automatically using different strategies
- Searches multiple engines (Google, Bing, DuckDuckGo, Brave, Wikipedia)
- Combines general web + news sources
- **Deduplicates results** across all searches
- Returns 15-50 UNIQUE sources
- **Instructs Claude to analyze and synthesize** (not just list sources)

**Critical behavior:**
After gathering sources, Claude is instructed to:
1. Read and analyze ALL sources
2. Cross-reference claims across sources
3. Identify high-confidence facts (confirmed by many sources)
4. Note contradictions or single-source claims
5. Create comprehensive briefing with executive summary
6. Assess source quality and credibility

**Parameters:**
- `query*` - Research topic or question
- `depth` - Research thoroughness:
  - `"quick"` - 2 searches, ~15 unique sources
  - `"standard"` - 4 searches, ~30 unique sources (recommended)
  - `"deep"` - 6 searches, ~50 unique sources

**Example:**
```
User: Research the latest AI developments and give me a briefing
Claude: [Calls research_topic("latest AI developments 2025", depth="standard")]

Claude receives 32 unique sources, then synthesizes:

"# AI Developments Briefing (2025)

## Executive Summary
Based on analysis of 32 sources from Google, Bing, DuckDuckGo, and Wikipedia...

## Key Findings
✓ Major development 1 (HIGH CONFIDENCE - confirmed by 12 sources)
✓ Emerging trend 2 (MEDIUM - reported by 5 sources)
⚠ Claim 3 (LOW - single source, needs verification)

## Contradictions
Source A says X, but Sources B, C, D report Y...

## Source Quality
Most reliable: Google News (8 sources), Wikipedia (3 sources)
..."
```

## 💡 Usage Examples

**General search:**
```
User: What is the latest news about AI?
Claude: [Calls search("latest AI news")]
```

**Image search:**
```
User: Show me pictures of Northern Lights
Claude: [Calls search_images("Northern Lights")]
```

**Video search:**
```
User: Find Python tutorial videos
Claude: [Calls search_videos("Python tutorial")]
```

**News search:**
```
User: What's happening with climate change?
Claude: [Calls search_news("climate change")]
```

## 🐳 Docker Management

**Start SearXNG:**
```bash
docker-compose up -d
```

**Stop SearXNG:**
```bash
docker-compose down
```

**View logs:**
```bash
docker-compose logs -f searxng
```

**Rebuild:**
```bash
docker-compose down
docker-compose up -d --build
```

## 🛠️ Development

**Run tests:**
```bash
pytest
```

**Format code:**
```bash
black .
```

**Type checking:**
```bash
mypy .
```

**Lint:**
```bash
ruff .
```

## 🎯 Why Only 4 Tools?

This MCP server is optimized for efficiency:

1. **Focused functionality** - Each tool has a clear, distinct purpose
2. **LLM-friendly** - Tool descriptions include "Use this when..." guidance
3. **Low context** - Minimal tool set reduces token usage
4. **Privacy-first** - SearXNG aggregates without tracking

Unlike direct search engine APIs, SearXNG provides:
- Privacy protection (no tracking)
- Multi-engine aggregation
- Self-hosted control
- No API keys needed

## 📁 Project Structure

```
SearxngMCP/
├── docker-compose.yml          # SearXNG Docker setup
├── searxng/
│   └── settings.yml            # SearXNG configuration
├── src/searxng_mcp/
│   ├── server.py               # Main MCP server
│   ├── config/                 # Configuration handling
│   │   ├── models.py
│   │   └── loader.py
│   └── tools/                  # Search tool implementations
│       └── search.py
├── searxng-config/
│   └── config.json             # MCP configuration
├── run-server.sh               # Server startup script
├── pyproject.toml              # Dependencies
└── README.md
```

## 📄 License

MIT License

## 🙏 Credits

- [SearXNG](https://github.com/searxng/searxng) - Privacy-respecting metasearch engine
- [Model Context Protocol](https://modelcontextprotocol.io) - MCP specification
- Built with [FastMCP](https://github.com/modelcontextprotocol/python-sdk)
