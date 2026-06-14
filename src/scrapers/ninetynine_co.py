import logging
import re
from typing import Any

from src.core.base_scraper import BaseScraper
from src.models.property import PropertyListing

logger = logging.getLogger(__name__)


class NinetynineCoScraper(BaseScraper):
    """Scraper for 99.co Indonesia"""

    site_name = "99co"
    base_url = "https://www.99.co/id"

    async def build_search_url(self, area_name: str, page: int = 1) -> str:
        """Construct the search URL for a given area and page number."""
        # 99.co uses /id/jual/rumah/city/district
        # For simplicity, assuming city="bekasi"
        parts = [p.strip().replace(" ", "-") for p in area_name.split("/") if p.strip()]
        if len(parts) >= 2:
            city, district = parts[-2], parts[-1]
        else:
            city = "bekasi"
            district = parts[0] if parts else "bekasi-selatan"

        url = f"{self.base_url}/jual/rumah/{city}/{district}"
        if page > 1:
            url += f"?hlmn={page}"
        return url

    async def extract_listings(self, tab: Any) -> list[PropertyListing]:
        """Extract property listings from the current page."""
        
        # Close the helper bubble if it exists
        close_bubble_js = """
        (() => {
            try {
                const tutups = Array.from(document.querySelectorAll('button')).filter(b => b.innerText && b.innerText.includes('Tutup'));
                for (const btn of tutups) {
                    btn.click();
                }
            } catch(e) {}
        })();
        """
        await tab.evaluate(close_bubble_js)
        
        js_code = """
        (() => {
            const listings = [];
            const links = document.querySelectorAll('a[href*="/properti/"]');
            const seen = new Set();
            for (const link of links) {
                const url = link.href;
                if (url.includes('/projects/') || seen.has(url)) continue;
                seen.add(url);
                
                // Find a parent div that looks like a card wrapper
                let card = link.parentElement;
                let foundCard = false;
                for (let i = 0; i < 5; i++) {
                    if (card && card.innerText && card.innerText.length > 50) {
                        foundCard = true;
                        break;
                    }
                    if (card) card = card.parentElement;
                }
                if (!foundCard) card = link;
                
                const titleEl = card.querySelector('h2, .cardSecondary__info-title');
                let title = titleEl ? titleEl.innerText : link.innerText;
                
                const priceEl = card.querySelector('strong, .cardSecondary__price');
                let price = priceEl ? priceEl.innerText : '';
                
                if (!price) {
                    const match = card.innerText.match(/Rp\\s*[\\d.,]+\\s*[A-Za-z]*/);
                    if (match) {
                        price = match[0];
                    }
                }
                
                listings.push({
                    url: url,
                    title: title,
                    priceText: price,
                    fullText: card.innerText || ''
                });
            }
            return JSON.stringify(listings);
        })();
        """
        
        raw_result = await tab.evaluate(js_code)
        import json
        raw_listings = json.loads(raw_result)
        
        listings = []
        if not raw_listings:
            html = await tab.evaluate("document.body.innerHTML")
            with open("99co_debug.html", "w", encoding="utf-8") as f:
                f.write(html)
            self._logger.warning("No listings found, dumped HTML to 99co_debug.html")
            return listings
            
        for raw in raw_listings:
            try:
                url = raw.get("url", "")
                
                # Extract ID from url (e.g. /properti/rumah-cantik-12345)
                # Let's just use the slug as ID if no explicit ID
                id_match = re.search(r'properti/([^/?]+)', url)
                listing_id = id_match.group(1) if id_match else url.split('/')[-1]
                
                title = raw.get("title", "").strip()
                if not title:
                    title = raw.get("fullText", "").split("\n")[0]

                price_text = raw.get("priceText", "")
                if not price_text:
                    continue

                price_idr = PropertyListing.parse_indonesian_price(price_text)

                text = raw.get("fullText", "")

                # Specs extraction (often listed as 'LT 72 m2' or similar)
                lt_match = re.search(r'LT\s*\n*:?\s*(\d+)', text, re.IGNORECASE)
                if not lt_match:
                    lt_match = re.search(r'Luas Tanah\s*(\d+)', text, re.IGNORECASE)

                lb_match = re.search(r'LB\s*\n*:?\s*(\d+)', text, re.IGNORECASE)
                if not lb_match:
                    lb_match = re.search(r'Luas Bangunan\s*(\d+)', text, re.IGNORECASE)

                kt_match = re.search(r'(\d+)\s*Kamar\s*Tidur', text, re.IGNORECASE)
                km_match = re.search(r'(\d+)\s*Kamar\s*Mandi', text, re.IGNORECASE)
                
                lt = float(lt_match.group(1)) if lt_match else None
                lb = float(lb_match.group(1)) if lb_match else None
                kt = int(kt_match.group(1)) if kt_match else None
                km = int(km_match.group(1)) if km_match else None
                
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
        """Navigate to the next page of results."""
        js_code = """
        (() => {
            const nextBtn = document.querySelector('.ui-atomic-pagination__item--next');
            if (nextBtn && !nextBtn.hasAttribute('disabled') && !nextBtn.classList.contains('disabled')) {
                return true;
            }
            return false;
        })();
        """
        has_next = await tab.evaluate(js_code)
        return has_next
