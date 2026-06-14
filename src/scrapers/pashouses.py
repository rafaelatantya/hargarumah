import logging
import re
from typing import Any

from src.core.base_scraper import BaseScraper
from src.models.property import PropertyListing

logger = logging.getLogger(__name__)


class PashousesScraper(BaseScraper):
    """Scraper for Pashouses.id"""

    site_name = "pashouses"
    base_url = "https://pashouses.id"

    async def build_search_url(self, area_name: str, page: int = 1) -> str:
        """Construct the search URL for a given area and page number."""
        area_key = area_name.lower().replace("_", "-")

        if "/" in area_key:
            parts = area_key.split("/")
            city = parts[0]
            district = parts[1]
            url = f"{self.base_url}/rumah-dijual/area/{city}/{district}"
        else:
            city = "bekasi"
            district = area_key
            url = f"{self.base_url}/rumah-dijual/area/{city}/{district}"

        if page > 1:
            url += f"/{page}"

        return url

    async def extract_listings(self, tab: Any) -> list[PropertyListing]:
        """Extract property listings from the current page."""
        js_code = """
        (() => {
            try {
                const listings = [];
                const cards = document.querySelectorAll('a[href^="/rumah/"]');

                for (const card of cards) {
                    try {
                        const href = card.getAttribute('href');
                        if (!href) continue;

                        const titleEl = card.querySelector('h2');
                        const title = titleEl ? titleEl.innerText : '';

                        const pTags = card.querySelectorAll('p');
                        let location = '';
                        if (titleEl && titleEl.nextElementSibling && titleEl.nextElementSibling.tagName.toLowerCase() === 'p') {
                            location = titleEl.nextElementSibling.innerText;
                        }

                        let priceText = '';
                        const spans = card.querySelectorAll('span');
                        for (const span of spans) {
                            if (span.innerText.includes('Rp')) {
                                priceText = span.innerText;
                                break;
                            }
                        }

                        let lt = '', lb = '', kt = '', km = '';
                        for (const p of pTags) {
                            const text = p.innerText;
                            if (text.includes('LT')) lt = text;
                            if (text.includes('LB')) lb = text;
                            if (text.includes('KT')) kt = text;
                            if (text.includes('KM')) km = text;
                        }

                        listings.push({
                            url: 'https://pashouses.id' + href,
                            title: title,
                            location: location,
                            priceText: priceText,
                            lt: lt,
                            lb: lb,
                            kt: kt,
                            km: km
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
                title = raw.get("title", "")
                price_text = raw.get("priceText", "")

                if not url or not title or not price_text:
                    continue

                try:
                    price_idr = PropertyListing.parse_indonesian_price(price_text)
                except ValueError:
                    continue

                listing_id = url.split('/')[-1]

                def parse_spec_num(text, pattern):
                    m = re.search(pattern + r'\s*\n?([\d\.,]+)', text, re.IGNORECASE)
                    if not m:
                        m = re.search(r'([\d\.,]+)\s*' + pattern, text, re.IGNORECASE)
                    if m:
                        val = m.group(1).replace(',', '.')
                        try:
                            return float(val) if '.' in val else int(val)
                        except ValueError:
                            pass
                    return None

                lt = parse_spec_num(raw.get("lt", ""), "LT")
                lb = parse_spec_num(raw.get("lb", ""), "LB")
                kt = parse_spec_num(raw.get("kt", ""), "KT")
                km = parse_spec_num(raw.get("km", ""), "KM")

                location = raw.get("location", "")
                district = None
                city = None
                if location and "," in location:
                    parts = [p.strip() for p in location.split(",")]
                    if len(parts) >= 2:
                        district = parts[0]
                        city = parts[1]
                    else:
                        district = parts[0]
                elif location:
                    district = location.strip()

                listing = PropertyListing(
                    id=listing_id,
                    source=self.site_name,
                    title=title,
                    price_idr=price_idr,
                    url=url,
                    land_area_m2=lt,
                    building_area_m2=lb,
                    bedrooms=int(kt) if kt else None,
                    bathrooms=int(km) if km else None,
                    address=location if location else None,
                    city=city,
                    district=district,
                    property_type="rumah",
                    listing_type="dijual"
                )
                listings.append(listing)
            except Exception as e:
                self._logger.warning(f"Failed to parse Pashouses listing {url}: {e}")

        return listings

    async def get_next_page(self, tab: Any) -> bool:
        """Navigate to the next page of results."""
        js_code = """
        (() => {
            return document.querySelectorAll('a[href^="/rumah/"]').length >= 20;
        })();
        """
        has_next = await tab.evaluate(js_code)
        return has_next
