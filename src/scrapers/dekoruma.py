import html
import logging
import re
from typing import Any

from src.core.base_scraper import BaseScraper
from src.models.property import PropertyListing

logger = logging.getLogger(__name__)


class DekorumaScraper(BaseScraper):
    """Scraper for Dekoruma.com"""

    site_name = "dekoruma"
    base_url = "https://www.dekoruma.com"

    async def build_search_url(self, area_name: str, page: int = 1) -> str:
        """Construct the search URL for a given area and page number."""
        area_clean = area_name.strip().lower().replace("_", "-")

        if "/" in area_clean:
            parts = area_clean.split("/")
            city = parts[-2]
            district = parts[-1]
        else:
            known_cities = {
                "bekasi", "depok", "tangerang", "bogor", "bandung", "surabaya",
                "sidoarjo", "malang", "jakarta", "jakarta-selatan", "jakarta-barat",
                "jakarta-timur", "jakarta-utara", "jakarta-pusat", "tangerang-selatan",
                "kabupaten-bandung", "kabupaten-bandung-barat", "cimahi"
            }
            if area_clean in known_cities or any(c in area_clean for c in ["jakarta", "bandung", "tangerang"]):
                city = area_clean
                district = None
            else:
                city = "bekasi"
                district = area_clean

        if district:
            url = f"{self.base_url}/rumah-dijual/di-area-{district}"
        else:
            url = f"{self.base_url}/rumah-dijual/di-kota-{city}"

        if page > 1:
            url += f"?page={page}"

        return url

    async def extract_listings(self, tab: Any) -> list[PropertyListing]:
        """Extract property listings from the current page."""
        js_code = """
        (() => {
            try {
                const listings = [];
                const cards = Array.from(document.querySelectorAll('a')).filter(a => {
                    return a.className.includes('link-reset') &&
                           a.href.includes('/properti/') &&
                           !a.href.includes('/simulasi-kpr') &&
                           !a.href.includes('/area/') &&
                           !a.href.includes('/request') &&
                           !a.href.includes('/login') &&
                           !a.href.includes('/internal');
                });

                for (const card of cards) {
                    try {
                        const url = card.href;

                        // Extract inner text which handles elements properly
                        const innerText = card.innerText;
                        const innerHTML = card.innerHTML;

                        // Identify secondary homes by checking if the SVG path starts with M3
                        // M3 represents the bedroom icon
                        let bedrooms = null;
                        let bathrooms = null;

                        const svgs = Array.from(card.querySelectorAll('svg'));
                        for (const svg of svgs) {
                            if (svg.innerHTML.includes('M3') || svg.innerHTML.includes('d="M3')) {
                                const parent = svg.parentElement;
                                if (parent && parent.nextElementSibling) {
                                    bedrooms = parseInt(parent.nextElementSibling.innerText.trim());
                                }
                            } else if (svg.innerHTML.includes('M8') || svg.innerHTML.includes('d="M8')) {
                                const parent = svg.parentElement;
                                if (parent && parent.nextElementSibling) {
                                    bathrooms = parseInt(parent.nextElementSibling.innerText.trim());
                                }
                            }
                        }

                        listings.push({
                            url: url,
                            fullText: innerText,
                            html: innerHTML,
                            bedrooms: bedrooms,
                            bathrooms: bathrooms
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
        import json
        raw_listings = json.loads(raw_result)

        listings = []
        for raw in raw_listings:
            try:
                if "error" in raw:
                    continue

                url = raw.get("url", "")
                if not url:
                    continue

                listing_id = url.split("-")[-1].strip("/")

                text = raw.get("fullText", "")
                lines = [line.strip() for line in text.split('\n') if line.strip()]
                if not lines:
                    continue

                title = lines[0]
                if "NEW" in title.upper() and len(lines) > 1:
                    title = lines[1]
                title = html.unescape(title)
                title = re.sub(r'^(NEW\s+|NEW\n)', '', title, flags=re.IGNORECASE).strip()

                price_text = None
                for line in lines:
                    if "Rp" in line:
                        price_text = line
                        break

                if not price_text:
                    continue

                price_idr = PropertyListing.parse_indonesian_price(price_text)

                lt = lb = kt = km = None

                # Extract specs (Primary homes)
                for line in lines:
                    if "LT" in line.upper():
                        val = re.search(r'([\d.,]+)', line)
                        if val:
                            lt = float(val.group(1).replace(',', '.'))
                    elif "LB" in line.upper():
                        val = re.search(r'([\d.,]+)', line)
                        if val:
                            lb = float(val.group(1).replace(',', '.'))
                    elif "KT" in line.upper():
                        val = re.search(r'(\d+)', line)
                        if val:
                            kt = int(val.group(1))
                    elif "KM" in line.upper():
                        val = re.search(r'(\d+)', line)
                        if val:
                            km = int(val.group(1))

                # If KT/KM wasn't found in the text directly, use our JS extraction fallback
                if kt is None and raw.get("bedrooms") is not None and not str(raw.get("bedrooms")) == "NaN":
                    kt = int(raw.get("bedrooms"))
                if km is None and raw.get("bathrooms") is not None and not str(raw.get("bathrooms")) == "NaN":
                    km = int(raw.get("bathrooms"))

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
                    property_type="rumah",
                    listing_type="dijual"
                )
                listings.append(listing)
            except Exception as e:
                self._logger.warning(f"Failed to parse listing {raw.get('url')}: {e}")

        return listings

    async def get_next_page(self, tab: Any) -> bool:
        js_code = """
        (() => {
            const cards = Array.from(document.querySelectorAll('a')).filter(a => {
                return a.className.includes('link-reset') &&
                       a.href.includes('/properti/') &&
                       !a.href.includes('/simulasi-kpr');
            });
            return cards.length >= 20;
        })();
        """
        has_next = await tab.evaluate(js_code)
        return has_next