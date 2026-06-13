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
        # Clean and slugify the area name
        area_clean = area_name.strip().lower().replace("_", "-")

        if "/" in area_clean:
            parts = area_clean.split("/")
            city = parts[-2]
            district = parts[-1]
        else:
            # Check if area_name is a known city, otherwise default to district
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
            # E.g., https://www.dekoruma.com/rumah-dijual/di-area-bekasi-selatan
            url = f"{self.base_url}/rumah-dijual/di-area-{district}"
        else:
            # E.g., https://www.dekoruma.com/rumah-dijual/di-kota-bekasi
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
                // Target cards that represent individual property listings
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

                        // Clean HTML tags and replace br with newlines to split correctly
                        let innerHtml = card.innerHTML;
                        innerHtml = innerHtml.replace(/<br\\s*\\/?>/gi, '\\\\n');
                        innerHtml = innerHtml.replace(/<[^>]+>/g, '\\n');

                        listings.push({
                            url: url,
                            fullText: innerHtml
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
        if not raw_listings:
            # Dump HTML for debugging if no listings found
            html_content = await tab.evaluate("document.body.innerHTML")
            with open("dekoruma_debug.html", "w", encoding="utf-8") as f:
                f.write(html_content)
            self._logger.warning("No listings found, dumped HTML to dekoruma_debug.html")
            return listings

        for raw in raw_listings:
            try:
                if "error" in raw:
                    continue

                url = raw.get("url", "")
                if not url:
                    continue

                # ID: Extract the last unique slug segment after the last dash
                listing_id = url.split("-")[-1].strip("/")

                # Split inner text to lines and clean them
                text = raw.get("fullText", "")
                lines = [line.strip() for line in text.split('\n') if line.strip()]
                if not lines:
                    continue

                # Base fields extraction
                title = lines[1] if len(lines) > 1 else "No title"
                title = html.unescape(title)
                # Drop "NEW" prefix if it exists
                title = re.sub(r'^(NEW\s+|NEW\n)', '', title, flags=re.IGNORECASE).strip()

                # Find index of price and LT/LB labels
                i_price = -1
                i_lt = -1
                i_lb = -1

                for i, line in enumerate(lines):
                    if re.match(r'^Rp\s*\d+', line, re.IGNORECASE):
                        i_price = i
                    elif line.upper() == 'LT':
                        i_lt = i
                    elif line.upper() == 'LB':
                        i_lb = i

                if i_price == -1:
                    continue  # Price is a mandatory field

                price_text = lines[i_price]
                price_idr = PropertyListing.parse_indonesian_price(price_text)

                # Specs extraction (bedrooms, bathrooms, garage)
                kt = None
                km = None
                garage = None

                if i_lt != -1:
                    # Get digit lines between price and LT line
                    middle_lines = lines[i_price + 1:i_lt]
                    digits = [int(line) for line in middle_lines if line.isdigit()]
                    if len(digits) >= 1:
                        kt = digits[0]
                    if len(digits) >= 2:
                        km = digits[1]
                    if len(digits) >= 3:
                        garage = digits[2]

                # Land and building area
                lt = None
                lb = None

                if i_lt != -1 and i_lt + 1 < len(lines):
                    try:
                        val_str = lines[i_lt + 1].replace(".", "").replace(",", ".")
                        lt = float(val_str)
                    except ValueError:
                        pass

                if i_lb != -1 and i_lb + 1 < len(lines):
                    try:
                        val_str = lines[i_lb + 1].replace(".", "").replace(",", ".")
                        lb = float(val_str)
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
                    garage=garage,
                    property_type="rumah",
                    listing_type="dijual"
                )
                listings.append(listing)
            except Exception as e:
                self._logger.warning(f"Failed to parse listing {raw.get('url')}: {e}")

        return listings

    async def get_next_page(self, tab: Any) -> bool:
        """Navigate to the next page of results.

        Returns True if the current page has 20 or more listings,
        which indicates it's a full page and a next page likely exists.
        """
        js_code = """
        (() => {
            const cards = Array.from(document.querySelectorAll('a')).filter(a => {
                return a.className.includes('link-reset') &&
                       a.href.includes('/properti/') &&
                       !a.href.includes('/simulasi-kpr') &&
                       !a.href.includes('/area/') &&
                       !a.href.includes('/request') &&
                       !a.href.includes('/login') &&
                       !a.href.includes('/internal');
            });
            return cards.length >= 20;
        })();
        """
        has_next = await tab.evaluate(js_code)
        return has_next
