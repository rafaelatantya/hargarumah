"""Scraper registry and auto-discovery.

This module centralizes access to all implemented scrapers.
To add a new site, simply import its scraper class here and add it to ALL_SCRAPERS.
"""

from src.scrapers.rumah123 import Rumah123Scraper
from src.scrapers.olx import OlxScraper
from src.scrapers.ninetynine_co import NinetynineCoScraper
from src.scrapers.pinhome import PinhomeScraper
from src.scrapers.dekoruma import DekorumaScraper
from src.scrapers.cariproperti import CariPropertiScraper
from src.scrapers.easyfind import EasyFindScraper
from src.scrapers.pashouses import PashousesScraper

# Dictionary mapping standard names (as used in CLI --site flag) to their scraper classes
SCRAPER_REGISTRY = {
    "rumah123": ("Rumah123", Rumah123Scraper),
    "olx": ("OLX", OlxScraper),
    "99co": ("99.co", NinetynineCoScraper),
    "pinhome": ("Pinhome", PinhomeScraper),
    "dekoruma": ("Dekoruma", DekorumaScraper),
    "cariproperti": ("CariProperti", CariPropertiScraper),
    "easyfind": ("EasyFind", EasyFindScraper),
    "pashouses": ("PasHouses", PashousesScraper),
}

def get_scrapers(site_filter: str = "all") -> list[tuple[str, type]]:
    """Get a list of requested scraper classes based on the filter string.

    Args:
        site_filter: Comma-separated list of site names, or "all".

    Returns:
        List of tuples: (Display Name, ScraperClass)
    """
    if site_filter.strip().lower() == "all":
        return list(SCRAPER_REGISTRY.values())

    selected = []
    keys = [k.strip().lower() for k in site_filter.split(",")]

    for key in keys:
        if key in SCRAPER_REGISTRY:
            selected.append(SCRAPER_REGISTRY[key])

    return selected

def get_available_names() -> list[str]:
    """Get list of all valid keys for the CLI --site argument."""
    return list(SCRAPER_REGISTRY.keys())
