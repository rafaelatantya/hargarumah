"""Abstract base scraper — defines the interface all site-specific scrapers must implement."""

from __future__ import annotations

import asyncio
import logging
import random
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

from src.config.settings import settings
from src.models.property import PropertyListing

if TYPE_CHECKING:
    from src.core.browser import BrowserManager

logger = logging.getLogger(__name__)


class BaseScraper(ABC):
    """Abstract base class for all property website scrapers.

    Every site-specific scraper must inherit from this class and implement:
    - build_search_url(): Construct the search URL for a given area and page
    - extract_listings(): Parse the page DOM into PropertyListing objects
    - get_next_page(): Handle pagination (navigate to next page)

    The base class provides:
    - Shared utilities (delay management, retry logic)
    - The main scrape() orchestration method
    - Consistent error handling and logging
    """

    # Subclasses MUST override these
    site_name: str = ""
    base_url: str = ""

    def __init__(self, browser: BrowserManager) -> None:
        """Initialize the scraper with a browser manager.

        Args:
            browser: An active BrowserManager instance for page navigation.
        """
        self.browser = browser
        self._logger = logging.getLogger(f"{__name__}.{self.site_name}")

    @abstractmethod
    async def build_search_url(self, area_name: str, page: int = 1) -> str:
        """Construct the search URL for a given area and page number.

        Args:
            area_name: The area slug (e.g., "bekasi-selatan").
            page: Page number (1-indexed).

        Returns:
            The full search URL string.
        """

    @abstractmethod
    async def extract_listings(self, tab: object) -> list[PropertyListing]:
        """Extract property listings from the current page.

        Args:
            tab: The nodriver Tab object with the loaded page.

        Returns:
            List of validated PropertyListing objects extracted from the page.
        """

    @abstractmethod
    async def get_next_page(self, tab: object) -> bool:
        """Navigate to the next page of results.

        Args:
            tab: The current nodriver Tab object.

        Returns:
            True if successfully navigated to next page, False if no more pages.
        """

    async def scrape(
        self,
        area_name: str,
        min_listings: int | None = None,
        max_pages: int | None = None,
    ) -> list[PropertyListing]:
        """Main scraping orchestration method.

        Iterates through search result pages until either:
        - min_listings is reached
        - max_pages is reached
        - No more pages available

        Args:
            area_name: The area slug to search (e.g., "bekasi-selatan").
            min_listings: Minimum number of listings to collect.
                          Defaults to settings.scraping.min_listings.
            max_pages: Maximum number of pages to scrape.
                       Defaults to settings.scraping.max_pages.

        Returns:
            List of all collected PropertyListing objects.
        """
        if min_listings is None:
            min_listings = settings.scraping.min_listings
        if max_pages is None:
            max_pages = settings.scraping.max_pages

        all_listings: list[PropertyListing] = []
        page_num = 1

        self._logger.info(
            "Starting scrape: site=%s area=%s min_listings=%d max_pages=%d",
            self.site_name, area_name, min_listings, max_pages,
        )

        while page_num <= max_pages:
            try:
                # Build and navigate to search URL
                url = await self.build_search_url(area_name, page_num)
                tab = await self.browser.get_page(url)

                # Wait for page content to load
                await asyncio.sleep(random.uniform(1.0, 3.0))

                # Extract listings from current page
                listings = await self.extract_listings(tab)

                if not listings:
                    self._logger.info("No listings found on page %d, stopping.", page_num)
                    break

                all_listings.extend(listings)
                self._logger.info(
                    "Page %d: extracted %d listings (total: %d)",
                    page_num, len(listings), len(all_listings),
                )

                # Check if we have enough listings
                if len(all_listings) >= min_listings:
                    self._logger.info(
                        "Reached minimum listings target (%d >= %d)",
                        len(all_listings), min_listings,
                    )
                    break

                # Try to go to next page
                has_next = await self.get_next_page(tab)
                if not has_next:
                    self._logger.info("No more pages available after page %d.", page_num)
                    break

                page_num += 1

            except Exception as e:
                self._logger.error("Error on page %d: %s", page_num, e, exc_info=True)
                # Try to continue with next page
                page_num += 1
                continue

        self._logger.info(
            "Scrape complete: site=%s area=%s total_listings=%d pages_scraped=%d",
            self.site_name, area_name, len(all_listings), page_num,
        )
        return all_listings
