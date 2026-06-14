import json
import logging
import re
from typing import Any

from src.core.base_scraper import BaseScraper
from src.models.property import PropertyListing

logger = logging.getLogger(__name__)


class EasyFindScraper(BaseScraper):
    """Scraper for EasyFind.id"""

    site_name = "easyfind"
    base_url = "https://www.easyfind.id"

    async def build_search_url(self, area_name: str, page: int = 1) -> str:
        """Construct the search URL for a given area and page number."""
        # Clean area name into a search query
        query_val = f"Rumah {area_name.replace('-', ' ').replace('_', ' ').replace('/', ' ')}"
        # Normalize multiple spaces
        query_val = " ".join(query_val.split())
        query = query_val.replace(" ", "+")

        url = f"{self.base_url}/properties?query={query}"

        # Append city query param if area refers to Bekasi
        if "bekasi" in area_name.lower():
            url += "&city=Kota+Bekasi"

        url += f"&page={page}"
        return url

    async def extract_listings(self, tab: Any) -> list[PropertyListing]:
        """Extract property listings from the current page."""
        # Scroll page to load lazy content
        await self.browser.scroll_page(tab, scroll_count=3)

        js_code = """
        (() => {
            try {
                const listings = [];
                const cards = document.querySelectorAll('a[href^="/properties/"]');
                const seen = new Set();
                for (const card of cards) {
                    try {
                        let url = card.href || '';
                        if (url && !url.startsWith('http')) {
                            url = 'https://www.easyfind.id' + url;
                        }
                        if (!url || seen.has(url)) continue;
                        seen.add(url);

                        const titleEl = card.querySelector('h3');
                        const title = titleEl ? titleEl.innerText : '';

                        let price = '';
                        const priceMatch = card.innerText.match(/Rp\\s*[\\d.,]+\\s*(Juta|Milyar|Miliar|M|Jt)/i);
                        if (priceMatch) {
                            price = priceMatch[0];
                        } else {
                            // Check any div/span containing price words
                            const divs = card.querySelectorAll('div, p, span');
                            for (const el of divs) {
                                const txt = el.innerText || '';
                                if ((txt.includes('Juta') || txt.includes('Milyar') || txt.includes('Miliar')) && txt.includes('Rp')) {
                                    price = txt;
                                    break;
                                }
                            }
                        }

                        const figureEl = card.querySelector('figure');
                        const locationText = figureEl ? figureEl.innerText : '';

                        listings.push({
                            url: url,
                            title: title,
                            priceText: price,
                            locationText: locationText,
                            fullText: card.innerText || ''
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
            return listings

        for raw in raw_listings:
            if "error" in raw:
                continue

            try:
                url = raw.get("url", "")
                if not url:
                    continue

                # Extract listing ID (slug at end of path)
                listing_id = url.split('/')[-1] if not url.endswith('/') else url.split('/')[-2]

                title = raw.get("title", "").strip()
                text = raw.get("fullText", "")

                if not title:
                    lines_temp = [l.strip() for l in text.split("\n") if l.strip()]
                    title = lines_temp[0] if lines_temp else "No title"

                price_text = raw.get("priceText", "")
                if not price_text:
                    price_match = re.search(
                        r"(?:Rp\s*)?[\d.,]+\s*(?:Juta|Milyar|Miliar|M|Jt)",
                        text,
                        re.IGNORECASE
                    )
                    if price_match:
                        price_text = price_match.group(0)
                    else:
                        continue  # Price is mandatory

                price_idr = PropertyListing.parse_indonesian_price(price_text)

                address = raw.get("locationText", "").strip() or None

                # Specs: LT, LB, KT, KM
                lt = None
                lb = None
                kt = None
                km = None

                # Luas Tanah (LT)
                lt_match = re.search(r"(?:LT|Luas\s*Tanah)\s*:?\s*(\d+)", text, re.IGNORECASE)
                if not lt_match:
                    lt_match = re.search(r"Area:\s*(\d+)", text, re.IGNORECASE)
                if lt_match:
                    try:
                        lt = float(lt_match.group(1))
                    except ValueError:
                        pass

                # Luas Bangunan (LB)
                lb_match = re.search(r"(?:LB|Luas\s*Bangunan)\s*:?\s*(\d+)", text, re.IGNORECASE)
                if not lb_match:
                    lb_match = re.search(r"Area:\s*(\d+)", text, re.IGNORECASE)
                if lb_match:
                    try:
                        lb = float(lb_match.group(1))
                    except ValueError:
                        pass

                # Kamar Tidur (KT)
                kt_match = re.search(r"(\d+)\s*(?:KT|Kamar\s*Tidur)", text, re.IGNORECASE)
                if not kt_match:
                    kt_match = re.search(r"(?:KT|Kamar\s*Tidur)\s*:?\s*(\d+)", text, re.IGNORECASE)
                if not kt_match:
                    kt_match = re.search(r"Beds:\s*(\d+)", text, re.IGNORECASE)
                if kt_match:
                    try:
                        kt = int(kt_match.group(1))
                    except ValueError:
                        pass

                # Kamar Mandi (KM)
                km_match = re.search(r"(\d+)\s*(?:KM|Kamar\s*Mandi)", text, re.IGNORECASE)
                if not km_match:
                    km_match = re.search(r"(?:KM|Kamar\s*Mandi)\s*:?\s*(\d+)", text, re.IGNORECASE)
                if not km_match:
                    km_match = re.search(r"Baths:\s*(\d+)", text, re.IGNORECASE)
                if km_match:
                    try:
                        km = int(km_match.group(1))
                    except ValueError:
                        pass

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
        """Check if current page has property cards to decide if we should proceed to next page."""
        js_code = """
        (() => {
            const cards = document.querySelectorAll('a[href^="/properties/"]');
            return cards.length > 0;
        })();
        """
        has_cards = await tab.evaluate(js_code)
        return bool(has_cards)
