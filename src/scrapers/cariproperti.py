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

    Handles:
    1. AJAX Pagination: Uses "Next" button on desktop.
    2. Range Prices: Extracts the lowest price from ranges.
    3. Spec parsing: Handles KT/KM and LT/LB correctly.
    """

    site_name = "cariproperti"
    base_url = "https://cariproperti.com"

    async def build_search_url(self, area_name: str, page: int = 1) -> str:
        """Construct the search URL. Note: CariProperti doesn't use page numbers in URL."""
        return f"{self.base_url}/{area_name}"

    async def extract_listings(self, tab: Any) -> list[PropertyListing]:
        """Extract property listings from the currently loaded/scrolled page."""
        js_code = """
        (() => {
            try {
                const listings = [];
                const cards = document.querySelectorAll('a.new-map-card');

                for (const card of cards) {
                    try {
                        const url = card.href;
                        const fullText = card.innerText || "";

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

                listing_id = url.split('/')[-1] if not url.endswith('/') else url.split('/')[-2]

                text = raw.get("fullText", "")
                if not text:
                    continue

                lines = [line.strip() for line in text.split('\n') if line.strip()]
                if not lines:
                    continue

                title = lines[0]

                # Find price (handle ranges, take lowest)
                price_text = ""
                price_match = re.search(r'Rp\s*[\d.,]+\s*(?:Milyar|Miliar|Juta|M|Jt|T|Triliun)?', text, re.IGNORECASE)
                if price_match:
                    price_text = price_match.group(0)
                else:
                    continue  # Price is mandatory

                # Normalize the decimal dot to comma so parse_indonesian_price works
                price_text_norm = re.sub(r'\b(\d+)\.(\d{1,2})\b', r'\1,\2', price_text)

                try:
                    price_idr = PropertyListing.parse_indonesian_price(price_text_norm)
                except ValueError:
                    continue

                # Location usually below title
                address = lines[2] if len(lines) > 2 and "rp" in lines[1].lower() else lines[1] if len(lines) > 1 else None

                # Specs: KT, KM, LT, LB
                kt, km, lt, lb = None, None, None, None

                # KT/KM format: "3 - 4KT" or "3KT"
                kt_match = re.search(r'(\d+)\s*(?:-\s*\d+\s*)?KT', text, re.IGNORECASE)
                if kt_match:
                    kt = int(kt_match.group(1))

                km_match = re.search(r'(\d+)\s*(?:-\s*\d+\s*)?KM', text, re.IGNORECASE)
                if km_match:
                    km = int(km_match.group(1))

                # LB/LT format: "70 - 126m2"
                area_matches = re.findall(r'(\d+)\s*(?:-\s*\d+\s*)?m[²2]', text, re.IGNORECASE)
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

        return listings

    async def get_next_page(self, tab: Any) -> bool:
        """Click the 'Next' button to navigate to the next page of results."""
        # 1. Get the first card href before click
        js_first_href = "(() => { const c = document.querySelector('a.new-map-card'); return c ? c.href : ''; })()"
        old_href = await tab.evaluate(js_first_href)

        # 2. Click the 'Next' button
        js_click = """
        (() => {
            const btns = Array.from(document.querySelectorAll('button'));
            const nextBtn = btns.find(b => b.innerText.trim().toLowerCase() === 'next');
            if (nextBtn && !nextBtn.disabled && !nextBtn.hasAttribute('disabled')) {
                nextBtn.click();
                return true;
            }
            return false;
        })();
        """
        clicked = await tab.evaluate(js_click)
        if not clicked:
            return False

        # 3. Wait for page transition (first card href changes)
        success = False
        for _ in range(20):
            await asyncio.sleep(0.5)
            new_href = await tab.evaluate(js_first_href)
            if new_href and new_href != old_href:
                success = True
                break

        if not success:
            # Fallback sleep if it took longer
            await asyncio.sleep(2.0)

        return True

    async def scrape(
        self,
        area_name: str,
        min_listings: int | None = None,
        max_pages: int | None = None,
    ) -> list[PropertyListing]:
        """Override scrape to handle AJAX pagination instead of URL page reloading."""
        from src.config.settings import settings

        if min_listings is None:
            min_listings = settings.scraping.min_listings
        if max_pages is None:
            max_pages = 999

        all_listings_dict: dict[str, PropertyListing] = {}

        url = await self.build_search_url(area_name)
        self._logger.info(f"Starting scrape on {url}")

        tab = await self.browser.get_page(url)
        # Wait for page content to load
        await asyncio.sleep(random.uniform(2.0, 4.0))

        page_num = 1
        while page_num <= max_pages:
            # Extract listings from current page state
            listings = await self.extract_listings(tab)
            if not listings:
                self._logger.info("No listings found on page %d, stopping.", page_num)
                break

            for listing in listings:
                all_listings_dict[listing.id] = listing

            self._logger.info(
                "Page %d: extracted %d listings (total unique: %d)",
                page_num, len(listings), len(all_listings_dict),
            )

            # Check if we have enough listings
            if len(all_listings_dict) >= min_listings:
                self._logger.info(
                    "Reached minimum listings target (%d >= %d)",
                    len(all_listings_dict), min_listings,
                )
                break

            # Try to go to next page
            has_next = await self.get_next_page(tab)
            if not has_next:
                self._logger.info("No more pages available after page %d.", page_num)
                break

            page_num += 1

        return list(all_listings_dict.values())
