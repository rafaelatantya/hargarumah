"""Free proxy fetcher and rotator.

Fetches free proxies from public APIs, validates them,
and provides a rotation mechanism for IP diversity.

Note: Free proxies are unreliable. This is best-effort.
Fallback to direct connection on proxy failure.
"""

from __future__ import annotations

import asyncio
import logging
import random
import time
from dataclasses import dataclass, field

import httpx

logger = logging.getLogger(__name__)

# Public free proxy API endpoints
PROXY_SOURCES = [
    "https://api.proxyscrape.com/v2/?request=displayproxies&protocol=http&timeout=5000&country=all&ssl=all&anonymity=all",
    "https://www.proxy-list.download/api/v1/get?type=http",
]

# How long to cache proxy list before refreshing (seconds)
PROXY_CACHE_TTL = 300  # 5 minutes
# Timeout for proxy validation (seconds)
PROXY_VALIDATE_TIMEOUT = 10
# Max proxies to validate at once
MAX_VALIDATE_CONCURRENT = 20


@dataclass
class ProxyInfo:
    """Information about a single proxy."""

    url: str  # Full URL (e.g., "http://1.2.3.4:8080")
    response_time_ms: float = 0.0  # Validation response time
    last_used: float = 0.0  # Unix timestamp of last use
    failures: int = 0  # Consecutive failure count


@dataclass
class ProxyPool:
    """Manages a pool of free proxies with rotation and validation."""

    proxies: list[ProxyInfo] = field(default_factory=list)
    _last_fetched: float = 0.0
    _current_index: int = 0

    async def refresh(self) -> int:
        """Fetch and validate fresh proxies from public sources.

        Returns:
            Number of valid proxies found.
        """
        logger.info("Fetching free proxies from %d sources...", len(PROXY_SOURCES))

        raw_proxies: set[str] = set()

        async with httpx.AsyncClient(timeout=15) as client:
            for source_url in PROXY_SOURCES:
                try:
                    response = await client.get(source_url)
                    if response.status_code == 200:
                        lines = response.text.strip().split("\n")
                        for line in lines:
                            line = line.strip()
                            if line and ":" in line:
                                raw_proxies.add(f"http://{line}")
                        logger.info("Fetched %d proxies from %s", len(lines), source_url)
                except Exception as e:
                    logger.warning("Failed to fetch proxies from %s: %s", source_url, e)

        if not raw_proxies:
            logger.warning("No proxies fetched from any source")
            return 0

        logger.info("Validating %d candidate proxies...", len(raw_proxies))

        # Validate proxies concurrently (limited)
        semaphore = asyncio.Semaphore(MAX_VALIDATE_CONCURRENT)
        valid_proxies: list[ProxyInfo] = []

        async def validate_one(proxy_url: str) -> ProxyInfo | None:
            async with semaphore:
                return await _validate_proxy(proxy_url)

        tasks = [validate_one(url) for url in list(raw_proxies)[:100]]  # Cap at 100
        results = await asyncio.gather(*tasks, return_exceptions=True)

        for result in results:
            if isinstance(result, ProxyInfo):
                valid_proxies.append(result)

        # Sort by response time (fastest first)
        valid_proxies.sort(key=lambda p: p.response_time_ms)

        self.proxies = valid_proxies
        self._last_fetched = time.time()
        self._current_index = 0

        logger.info("Proxy pool refreshed: %d valid proxies", len(self.proxies))
        return len(self.proxies)

    def get_next(self) -> str | None:
        """Get the next proxy URL from the pool (round-robin rotation).

        Returns:
            Proxy URL string, or None if pool is empty.
        """
        if not self.proxies:
            return None

        # Skip proxies with too many failures
        attempts = 0
        while attempts < len(self.proxies):
            proxy = self.proxies[self._current_index]
            self._current_index = (self._current_index + 1) % len(self.proxies)

            if proxy.failures < 3:
                proxy.last_used = time.time()
                return proxy.url
            attempts += 1

        logger.warning("All proxies have excessive failures")
        return None

    def get_random(self) -> str | None:
        """Get a random proxy URL from the pool.

        Returns:
            Proxy URL string, or None if pool is empty.
        """
        healthy = [p for p in self.proxies if p.failures < 3]
        if not healthy:
            return None
        proxy = random.choice(healthy)
        proxy.last_used = time.time()
        return proxy.url

    def report_failure(self, proxy_url: str) -> None:
        """Report that a proxy failed."""
        for proxy in self.proxies:
            if proxy.url == proxy_url:
                proxy.failures += 1
                logger.debug("Proxy failure recorded: %s (total: %d)", proxy_url, proxy.failures)
                break

    def report_success(self, proxy_url: str) -> None:
        """Report that a proxy succeeded (resets failure count)."""
        for proxy in self.proxies:
            if proxy.url == proxy_url:
                proxy.failures = 0
                break

    @property
    def needs_refresh(self) -> bool:
        """Check if the proxy pool should be refreshed."""
        if not self.proxies:
            return True
        return (time.time() - self._last_fetched) > PROXY_CACHE_TTL

    @property
    def healthy_count(self) -> int:
        """Number of proxies with fewer than 3 failures."""
        return sum(1 for p in self.proxies if p.failures < 3)


async def _validate_proxy(proxy_url: str) -> ProxyInfo | None:
    """Validate a single proxy by making a test request.

    Args:
        proxy_url: Proxy URL to validate (e.g., "http://1.2.3.4:8080").

    Returns:
        ProxyInfo if valid, None if invalid/unreachable.
    """
    try:
        start = time.monotonic()
        async with httpx.AsyncClient(
            proxies={"http://": proxy_url, "https://": proxy_url},
            timeout=PROXY_VALIDATE_TIMEOUT,
        ) as client:
            response = await client.get("http://httpbin.org/ip")
            elapsed_ms = (time.monotonic() - start) * 1000

            if response.status_code == 200:
                return ProxyInfo(url=proxy_url, response_time_ms=elapsed_ms)
    except Exception:
        pass
    return None
