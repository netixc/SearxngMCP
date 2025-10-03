"""Configuration loading for SearXNG MCP."""

import json
import os
from pathlib import Path
from typing import Optional

from .models import Config


def load_config(config_path: Optional[str] = None) -> Config:
    """Load configuration from file or environment.

    Args:
        config_path: Optional path to config file

    Returns:
        Loaded configuration
    """
    if config_path:
        config_file = Path(config_path)
    else:
        # Try environment variable
        env_path = os.getenv("SEARXNG_MCP_CONFIG")
        if env_path:
            config_file = Path(env_path)
        else:
            # Default location
            config_file = Path("searxng-config/config.json")

    if config_file.exists():
        with open(config_file) as f:
            data = json.load(f)
        return Config(**data)

    # Return defaults if no config found
    return Config()
