import logging
import re
import asyncio
from typing import Any

from src.core.base_scraper import BaseScraper
from src.models.property import PropertyListing

logger = logging.getLogger(__name__)

class OlxScraper(BaseScraper):
    """Scraper for OLX Indonesia"""

    site_name = "olx"
    base_url = "https://www.olx.co.id"

    # Area mapping dictionary - key is kebab-case area name, value is (location-slug, location-id)
    # OLX requires specific location IDs in URLs
    AREA_MAP = {
        "bekasi": ("bekasi-kota", "g4000020"),
        "bekasi-selatan": ("bekasi-selatan", "g5001297"),
        "bekasi-kota": ("bekasi-kota", "g4000020"),
        "bandung-kota": ("bandung-kota", "g4000018"),
        "jakarta-selatan": ("jakarta-selatan", "g4000030"),
        "jakarta-barat": ("jakarta-barat", "g4000028"),
        "jakarta-timur": ("jakarta-timur", "g4000031"),
        "jakarta-utara": ("jakarta-utara", "g4000032"),
        "jakarta-pusat": ("jakarta-pusat", "g4000029"),
        "tangerang-selatan": ("tangerang-selatan", "g4000057"),
        "tangerang": ("tangerang", "g4000055"),
        "depok": ("depok", "g4000021"),
        "bogor": ("bogor", "g4000022")
    }

    async def build_search_url(self, area_name: str, page: int = 1) -> str:
        """Construct the search URL for a given area. Note: OLX uses load more, not pages."""
        # Clean up keyword
        keyword = area_name.replace("/", "-").replace("_", "-").strip()

        # Try to use mapping if available, otherwise use global keyword search
        location_data = self.AREA_MAP.get(keyword.lower())

        if location_data:
            location_slug, location_id = location_data
            url = f"{self.base_url}/{location_slug}_{location_id}/dijual-rumah-apartemen_c5158?filter=type_eq_rumah"
        else:
            # Fallback to keyword search across Indonesia BUT inside property category
            url = f"{self.base_url}/dijual-rumah-apartemen_c5158/q-{keyword}?filter=type_eq_rumah"

        return url

    async def extract_listings(self, tab: Any) -> list[PropertyListing]:
        """Extract property listings from the current page."""

        # OLX has popup "Aktifkan notifikasi" which might block interactions
        close_popup_js = """
        (() => {
            const btns = document.querySelectorAll('button');
            for(let btn of btns) {
                if(btn.innerText.toLowerCase().includes('tidak dulu') ||
                   btn.innerText.toLowerCase().includes('nanti')) {
                    btn.click();
                }
            }
        })();
        """
        await tab.evaluate(close_popup_js)

        js_code = """
        (() => {
            try {
                const listings = [];
                const links = document.querySelectorAll('a');

                for (const link of links) {
                    try {
                        const href = link.getAttribute('href');
                        if (!href || !href.includes('/item/')) continue;

                        // It's a property link. Get text content
                        const fullText = link.innerText || '';
                        if (!fullText) continue;

                        listings.push({
                            url: 'https://www.olx.co.id' + href,
                            fullText: fullText
                        });
                    } catch (e) {
                        // ignore individual item errors
                    }
                }

                // Deduplicate by URL
                const uniqueListings = [];
                const seenUrls = new Set();
                for (const item of listings) {
                    if (!seenUrls.has(item.url)) {
                        seenUrls.add(item.url);
                        uniqueListings.push(item);
                    }
                }

                return JSON.stringify(uniqueListings);
            } catch (err) {
                return JSON.stringify([]);
            }
        })();
        """

        raw_result = await tab.evaluate(js_code)
        import json
        raw_listings = json.loads(raw_result)

        listings = []
        for raw in raw_listings:
            try:
                url = raw.get("url", "")
                text = raw.get("fullText", "")

                if not url or not text:
                    continue

                # Clean text: "Rp 1.650.000.000\n4 KT - 2 KM - 256 m2\nJual Rumah Sakura Regency..."
                text = re.sub(r'\s+', ' ', text).strip()

                # Extract listing ID
                listing_id_match = re.search(r'-iid-(\d+)', url)
                listing_id = listing_id_match.group(1) if listing_id_match else url.split('-')[-1]

                # Extract price
                price_match = re.search(r'Rp\s*([\d\.]+)', text)
                price_idr = None
                if price_match:
                    price_str = price_match.group(1).replace('.', '')
                    try:
                        price_idr = float(price_str)
                    except ValueError:
                        pass

                if not price_idr:
                    continue # Price is mandatory

                # Extract specs
                kt = km = lb = None
                kt_match = re.search(r'(\d+)\s*KT', text, re.IGNORECASE)
                if kt_match: kt = int(kt_match.group(1))

                km_match = re.search(r'(\d+)\s*KM', text, re.IGNORECASE)
                if km_match: km = int(km_match.group(1))

                lb_match = re.search(r'(\d+)\s*m2', text, re.IGNORECASE)
                if lb_match: lb = float(lb_match.group(1))

                # Extract Title - roughly anything after the m2 and before the location/date
                title = text
                if lb_match:
                    parts = text.split(lb_match.group(0))
                    if len(parts) > 1:
                        title = parts[1].strip()
                elif km_match:
                    parts = text.split(km_match.group(0))
                    if len(parts) > 1:
                        title = parts[1].strip()

                # Just take the first few words as title if we couldn't parse properly
                if len(title) > 100:
                    title = ' '.join(title.split(' ')[:15])

                listing = PropertyListing(
                    id=listing_id,
                    source=self.site_name,
                    title=title,
                    price_idr=price_idr,
                    url=url,
                    land_area_m2=None, # Only available on detail page for OLX
                    building_area_m2=lb,
                    bedrooms=kt,
                    bathrooms=km,
                    property_type="rumah",
                    listing_type="dijual"
                )
                listings.append(listing)
            except Exception as e:
                self._logger.warning(f"Failed to parse OLX listing {url}: {e}")

        return listings

    async def get_next_page(self, tab: Any) -> bool:
        """Navigate to the next page of results using 'Load More' button."""
        js_code = """
        (() => {
            const btns = document.querySelectorAll('button');
            for(let btn of btns) {
                if(btn.innerText.toLowerCase().includes('muat lainnya')) {
                    btn.click();
                    return true;
                }
            }
            return false;
        })();
        """
        has_next = await tab.evaluate(js_code)
        if has_next:
            # Wait for content to load after clicking
            await asyncio.sleep(4)
            # Scroll down a bit to ensure images/lazy content load
            await tab.evaluate("window.scrollBy(0, 1000)")
            await asyncio.sleep(1)
        return has_next

    async def scrape(
        self,
        area_name: str,
        min_listings: int | None = None,
        max_pages: int | None = None,
    ) -> list[PropertyListing]:
        """Override scrape to handle Load More pagination instead of URL page reloading."""
        from src.config.settings import settings

        if min_listings is None:
            min_listings = settings.scraping.min_listings
        if max_pages is None:
            max_pages = 999

        all_listings_dict: dict[str, PropertyListing] = {}

        url = await self.build_search_url(area_name)
        self._logger.info(f"Starting OLX scrape on {url}")

        tab = await self.browser.get_page(url)
        # Wait for page content to load
        import random
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

            # Try to click Load More
            has_next = await self.get_next_page(tab)
            if not has_next:
                self._logger.info("No 'Muat lainnya' button found after page %d.", page_num)
                break

            page_num += 1

        return list(all_listings_dict.values())
