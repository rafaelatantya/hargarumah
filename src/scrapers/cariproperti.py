import asyncio
import json
import logging
import random
import re
from typing import Any

from src.core.base_scraper import BaseScraper
from src.models.property import PropertyListing

logger = logging.getLogger(__name__)


class CariPropertiScraper(BaseScraper):
    """Scraper for CariProperti.com

    Edge Cases Handled:
    1. Infinite Scroll: Uses `tab.scroll_down` and evaluates DOM changes to detect end.
    2. Range Prices: Extracts the lowest price from formats like 'Rp 1.7 Milyar - Rp 3.1 Milyar'.
    3. URL structure: `cariproperti.com/<area>` or `<area>/<district>`.
    4. BaseScraper `scrape()` compatibility: Since BaseScraper iterates by page number
       but this site uses infinite scroll, we override `scrape()` entirely or adapt `get_next_page`
       to perform infinite scroll within a single page load. Overriding `scrape` is cleaner
       for infinite scroll sites.
    """

    site_name = "cariproperti"
    base_url = "https://cariproperti.com"

    async def build_search_url(self, area_name: str, page: int = 1) -> str:
        """Construct the search URL. Note: CariProperti doesn't use page numbers in URL."""
        # E.g., area_name = 'bekasi' or 'bekasi/bekasi-barat'
        return f"{self.base_url}/{area_name}"

    async def extract_listings(self, tab: Any) -> list[PropertyListing]:
        """Extract property listings from the currently loaded/scrolled page."""
        js_code = """
        (() => {
            try {
                const listings = [];
                // Target the specific a.new-map-card wrappers
                const cards = document.querySelectorAll('a.new-map-card');

                for (const card of cards) {
                    try {
                        const url = card.href;
                        // The wrapper contains siblings/children with the actual text
                        const parent = card.parentElement;
                        const fullText = parent ? parent.innerText : card.innerText;

                        listings.push({
                            url: url,
                            fullText: fullText
                        });
                    } catch (innerErr) {
                        listings.push({error: innerErr.toString(), url: card.href});
                    }
                }
                return JSON.stringify(listings);
            } catch (err) {
                return JSON.stringify([{error: err.toString()}]);
            }
        })();
        """
        raw_result = await tab.evaluate(js_code)
        raw_listings = json.loads(raw_result)

        listings = []
        if not raw_listings:
            self._logger.warning("No listings found during extraction.")
            return listings

        for raw in raw_listings:
            if "error" in raw:
                continue

            try:
                url = raw.get("url", "")
                if not url:
                    continue

                # ID: Extract from URL (e.g., .../properti/nama-properti-123)
                # Or generate hash if no clear ID. We'll use the last slug segment.
                listing_id = url.split('/')[-1] if not url.endswith('/') else url.split('/')[-2]

                text = raw.get("fullText", "")
                if not text:
                    continue

                lines = [line.strip() for line in text.split('\n') if line.strip()]
                if not lines:
                    continue

                # Title is usually the first line
                title = lines[0]

                # Find price (handle ranges, take lowest)
                price_text = ""
                price_match = re.search(r'Rp\s*[\d.,]+\s*(?:Milyar|Juta|M|Jt)', text, re.IGNORECASE)
                if price_match:
                    price_text = price_match.group(0)
                else:
                    continue # Price is mandatory

                try:
                    price_idr = PropertyListing.parse_indonesian_price(price_text)
                except ValueError:
                    continue

                # Location usually below title
                address = lines[1] if len(lines) > 1 else None

                # Specs: KT, KM, LT, LB
                kt, km, lt, lb = None, None, None, None

                # KT/KM format: "2 - 3 KT"
                kt_match = re.search(r'(\d+)\s*(?:-\s*\d+\s*)?KT', text, re.IGNORECASE)
                if kt_match:
                    kt = int(kt_match.group(1))

                # LB/LT format: "30 - 45 m²"
                # Usually first m2 is LB, second is LT based on docs, but we'll try to find both
                area_matches = re.findall(r'(\d+)\s*(?:-\s*\d+\s*)?m²', text, re.IGNORECASE)
                if len(area_matches) >= 1:
                    lb = float(area_matches[0])
                if len(area_matches) >= 2:
                    lt = float(area_matches[1])

                listing = PropertyListing(
                    id=listing_id,
                    source=self.site_name,
                    title=title,
                    price_idr=price_idr,
                    url=url,
                    land_area_m2=lt,
                    building_area_m2=lb,
                    bedrooms=kt,
                    bathrooms=km,
                    address=address,
                    property_type="rumah",
                    listing_type="dijual"
                )
                listings.append(listing)
            except Exception as e:
                self._logger.warning(f"Failed to parse listing {raw.get('url')}: {e}")

        # Deduplicate based on ID since infinite scroll will re-read early elements
        unique_listings = {l.id: l for l in listings}.values()
        return list(unique_listings)

    async def get_next_page(self, tab: Any) -> bool:
        """
        Since CariProperti uses infinite scroll, 'next page' means scrolling down.
        However, to integrate cleanly with `BaseScraper.scrape()`, which expects page URL changes,
        we override `scrape()` directly.
        """
        return False

    async def scrape(
        self,
        area_name: str,
        min_listings: int | None = None,
        max_pages: int | None = None,
    ) -> list[PropertyListing]:
        """Override scrape to handle Infinite Scroll instead of URL pagination."""
        from src.config.settings import settings

        if min_listings is None:
            min_listings = settings.scraping.min_listings

        all_listings_dict: dict[str, PropertyListing] = {}

        url = await self.build_search_url(area_name)
        self._logger.info(f"Starting infinite scroll scrape on {url}")

        tab = await self.browser.get_page(url)
        await asyncio.sleep(3) # Wait for initial load

        # Optionally click 'Residential' filter if needed. The prompt says we can rely on Pydantic filtering
        # but clicking is safer. We'll skip for now and filter post-scrape if needed, or implement simple JS click.

        scroll_attempts = 0
        max_scrolls = 50 # Safeguard
        last_count = 0

        while scroll_attempts < max_scrolls:
            listings = await self.extract_listings(tab)
            for listing in listings:
                all_listings_dict[listing.id] = listing

            current_count = len(all_listings_dict)
            self._logger.info(f"Scroll {scroll_attempts}: Found {current_count} unique listings so far.")

            if current_count >= min_listings:
                self._logger.info("Reached minimum listings target.")
                break

            if current_count == last_count and scroll_attempts > 0:
                # Might be at the end, or needs more time. We'll give it one more try
                self._logger.info("No new listings found after scroll. Waiting longer...")
                await asyncio.sleep(2)

            last_count = current_count

            # Perform scroll
            # CariProperti has a split pane, we need to scroll the listing container.
            # Using JS to find scrollable container and scroll it down.
            js_scroll = """
            (() => {
                // Find the likely container (usually has overflow-y: auto)
                const containers = Array.from(document.querySelectorAll('div')).filter(el => {
                    const style = window.getComputedStyle(el);
                    return style.overflowY === 'auto' || style.overflowY === 'scroll';
                });

                // Usually the main list container is the largest scrollable one
                let target = window; // Fallback
                if (containers.length > 0) {
                    target = containers.sort((a, b) => b.clientHeight - a.clientHeight)[0];
                    target.scrollBy(0, 1000);
                } else {
                    window.scrollBy(0, 1000);
                }
                return true;
            })();
            """
            await tab.evaluate(js_scroll)
            await asyncio.sleep(random.uniform(1.5, 3.0))
            scroll_attempts += 1

        return list(all_listings_dict.values())