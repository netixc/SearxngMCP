#!/bin/bash
# Wrapper script for SearxngMCP server

cd "$(dirname "$0")"
source .venv/bin/activate
exec searxng-mcp "$@"
