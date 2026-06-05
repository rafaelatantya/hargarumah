"""Browser manager — nodriver browser lifecycle with stealth configuration."""

from __future__ import annotations

import asyncio
import logging
import random
from typing import TYPE_CHECKING

import nodriver as uc

from src.config.settings import settings

if TYPE_CHECKING:
    pass

logger = logging.getLogger(__name__)


class BrowserManager:
    """Manages the nodriver browser instance with stealth settings.

    Handles browser initialization, session rotation, and cleanup.
    Uses Chrome DevTools Protocol (CDP) for undetectable automation.
    """

    def __init__(self) -> None:
        self._browser: uc.Browser | None = None
        self._page_count: int = 0

    @classmethod
    async def create(cls, proxy_url: str | None = None) -> BrowserManager:
        """Create and initialize a new BrowserManager instance.

        Args:
            proxy_url: Optional proxy URL to use for this session.
                       Format: http://host:port or socks5://host:port

        Returns:
            Initialized BrowserManager with an active browser session.
        """
        manager = cls()
        await manager._start_browser(proxy_url)
        return manager

    async def _start_browser(self, proxy_url: str | None = None) -> None:
        """Start a new browser instance with stealth configuration."""
        browser_args = []

        if proxy_url:
            browser_args.append(f"--proxy-server={proxy_url}")
            logger.info("Starting browser with proxy: %s", proxy_url)

        self._browser = await uc.start(
            headless=settings.browser.headless,
            lang=settings.browser.lang,
            browser_args=browser_args,
        )
        self._page_count = 0
        logger.info("Browser started (headless=%s, lang=%s)", settings.browser.headless, settings.browser.lang)

    async def get_page(self, url: str) -> uc.Tab:
        """Navigate to a URL and return the tab.

        Automatically applies random delays for human-like behavior.
        Rotates browser session if page count exceeds threshold.

        Args:
            url: The URL to navigate to.

        Returns:
            The browser tab after navigation.
        """
        if self._browser is None:
            await self._start_browser()

        # Check if session rotation is needed
        if self._page_count >= settings.scraping.session_max_pages:
            logger.info("Session page limit reached (%d), rotating browser...", self._page_count)
            await self.close()
            await self._start_browser()

        # Random delay for human-like behavior
        delay = random.uniform(settings.scraping.min_delay_seconds, settings.scraping.max_delay_seconds)
        logger.debug("Waiting %.1f seconds before navigation...", delay)
        await asyncio.sleep(delay)

        tab = await self._browser.get(url)  # type: ignore[union-attr]
        self._page_count += 1
        logger.debug("Navigated to %s (page %d in session)", url, self._page_count)

        return tab

    async def scroll_page(self, tab: uc.Tab, scroll_count: int = 3) -> None:
        """Scroll the page gradually to trigger lazy-loaded content.

        Args:
            tab: The browser tab to scroll.
            scroll_count: Number of scroll actions to perform.
        """
        for i in range(scroll_count):
            scroll_amount = random.randint(300, 700)
            await tab.evaluate(f"window.scrollBy(0, {scroll_amount})")
            await asyncio.sleep(random.uniform(0.5, 1.5))
            logger.debug("Scroll %d/%d: %dpx", i + 1, scroll_count, scroll_amount)

    async def close(self) -> None:
        """Close the browser instance and cleanup."""
        if self._browser:
            try:
                self._browser.stop()
                logger.info("Browser closed (total pages: %d)", self._page_count)
            except Exception as e:
                logger.warning("Error closing browser: %s", e)
            finally:
                self._browser = None
                self._page_count = 0

    @property
    def is_active(self) -> bool:
        """Check if the browser session is currently active."""
        return self._browser is not None
