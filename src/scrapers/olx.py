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
        area_key = area_name.lower().replace("_", "-")
        if "/" in area_key:
            area_key = area_key.split("/")[-1]

        location_slug, location_id = self.AREA_MAP.get(area_key, ("bekasi-kota", "g4000020"))

        # We start with page 1, subsequent pages are loaded via "muat lainnya" button
        url = f"{self.base_url}/{location_slug}_{location_id}/dijual-rumah-apartemen_c5158?filter=type_eq_rumah"
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
            await asyncio.sleep(3)
        return has_next
