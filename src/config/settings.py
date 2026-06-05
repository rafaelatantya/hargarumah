"""Settings loader — combines YAML config files with .env overrides."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any

import yaml
from dotenv import load_dotenv
from pydantic import BaseModel, Field


# Project root is 2 levels up from this file (src/config/settings.py → hargarumah/)
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
CONFIG_DIR = PROJECT_ROOT / "config"
DATA_DIR = PROJECT_ROOT / "data"

# Load .env file if it exists
load_dotenv(PROJECT_ROOT / ".env")


class GeoSettings(BaseModel):
    """Default geographic search parameters."""

    default_latitude: float = Field(default=-6.2607, description="Default search latitude (Bekasi Selatan)")
    default_longitude: float = Field(default=106.9894, description="Default search longitude (Bekasi Selatan)")
    default_radius_km: float = Field(default=5.0, description="Default search radius in kilometers")


class BrowserSettings(BaseModel):
    """Browser automation settings."""

    headless: bool = Field(default=False, description="Run browser in headless mode")
    chrome_path: str | None = Field(default=None, description="Path to Chrome binary (auto-detect if None)")
    lang: str = Field(default="id-ID", description="Browser language")


class ProxySettings(BaseModel):
    """Proxy configuration."""

    use_free_proxy: bool = Field(default=False, description="Enable free proxy rotation")
    proxy_url: str | None = Field(default=None, description="Manual proxy URL (overrides free proxy)")


class ScrapingSettings(BaseModel):
    """Scraping behavior settings."""

    min_delay_seconds: float = Field(default=2.0, description="Minimum delay between requests")
    max_delay_seconds: float = Field(default=5.0, description="Maximum delay between requests")
    min_listings: int = Field(default=100, description="Minimum listings to collect per site")
    max_pages: int = Field(default=50, description="Maximum pages to scrape per site")
    session_max_pages: int = Field(default=100, description="Max pages before rotating browser session")


class Settings(BaseModel):
    """Root settings model combining all configuration sources."""

    geo: GeoSettings = Field(default_factory=GeoSettings)
    browser: BrowserSettings = Field(default_factory=BrowserSettings)
    proxy: ProxySettings = Field(default_factory=ProxySettings)
    scraping: ScrapingSettings = Field(default_factory=ScrapingSettings)
    log_level: str = Field(default="INFO", description="Logging level")


def _load_yaml(filename: str) -> dict[str, Any]:
    """Load a YAML config file from the config directory."""
    filepath = CONFIG_DIR / filename
    if not filepath.exists():
        return {}
    with open(filepath, encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def load_settings() -> Settings:
    """Load settings from YAML files and environment variables.

    Priority: .env overrides > YAML config > defaults
    """
    # Load YAML config
    default_config = _load_yaml("default.yaml")

    # Build settings from YAML
    settings_dict: dict[str, Any] = {}

    if "geo" in default_config:
        settings_dict["geo"] = default_config["geo"]
    if "browser" in default_config:
        settings_dict["browser"] = default_config["browser"]
    if "proxy" in default_config:
        settings_dict["proxy"] = default_config["proxy"]
    if "scraping" in default_config:
        settings_dict["scraping"] = default_config["scraping"]

    # Override with environment variables
    env_overrides = {
        "geo": {
            "default_latitude": os.getenv("DEFAULT_LATITUDE"),
            "default_longitude": os.getenv("DEFAULT_LONGITUDE"),
            "default_radius_km": os.getenv("DEFAULT_RADIUS_KM"),
        },
        "browser": {
            "headless": os.getenv("HEADLESS"),
            "chrome_path": os.getenv("CHROME_PATH") or None,
        },
        "proxy": {
            "use_free_proxy": os.getenv("USE_FREE_PROXY"),
            "proxy_url": os.getenv("PROXY_URL") or None,
        },
        "scraping": {
            "min_delay_seconds": os.getenv("MIN_DELAY_SECONDS"),
            "max_delay_seconds": os.getenv("MAX_DELAY_SECONDS"),
        },
        "log_level": os.getenv("LOG_LEVEL"),
    }

    # Merge env overrides (only non-None values)
    for section, values in env_overrides.items():
        if isinstance(values, dict):
            if section not in settings_dict:
                settings_dict[section] = {}
            for key, value in values.items():
                if value is not None:
                    settings_dict[section][key] = value
        elif values is not None:
            settings_dict[section] = values

    return Settings(**settings_dict)


# Singleton instance
settings = load_settings()
