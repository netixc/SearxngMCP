"""Configuration models for SearXNG MCP."""

from typing import Optional
from pydantic import BaseModel, Field


class SearxngConfig(BaseModel):
    """SearXNG instance configuration."""

    url: str = Field(
        default="http://192.168.50.67:8080",
        description="SearXNG instance URL"
    )
    timeout: int = Field(
        default=10,
        description="Request timeout in seconds"
    )


class LoggingConfig(BaseModel):
    """Logging configuration."""

    level: str = Field(default="INFO", description="Log level")
    format: str = Field(
        default="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        description="Log format"
    )
    file: Optional[str] = Field(default=None, description="Log file path")


class Config(BaseModel):
    """Main configuration model."""

    searxng: SearxngConfig = Field(default_factory=SearxngConfig)
    logging: LoggingConfig = Field(default_factory=LoggingConfig)
