import logging
import re
from typing import Any

from src.core.base_scraper import BaseScraper
from src.models.property import PropertyListing

logger = logging.getLogger(__name__)


class Rumah123Scraper(BaseScraper):
    """Scraper for Rumah123.com"""

    site_name = "rumah123"
    base_url = "https://www.rumah123.com"

    async def build_search_url(self, area_name: str, page: int = 1) -> str:
        """Construct the search URL using Rumah123's keyword search.

        Uses /jual/cari/?q=<keyword>&type=rumah which works for ANY location
        without needing to know city/district hierarchy.
        """
        # Clean up the keyword: replace slashes/underscores with spaces
        keyword = area_name.replace("/", " ").replace("_", " ").replace("-", " ").strip()

        url = f"{self.base_url}/jual/cari/?q={keyword}&type=rumah"
        if page > 1:
            url += f"&page={page}"
        return url

    async def extract_listings(self, tab: Any) -> list[PropertyListing]:
        """Extract property listings from the current page."""
        js_code = """
        (() => {
            try {
                const listings = [];
                const links = document.querySelectorAll('a[href*="/properti/"]');
                const seen = new Set();
                for (const link of links) {
                    try {
                        const url = link.href;
                        if (seen.has(url)) continue;
                        seen.add(url);
                        
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
                        
                        let title = link.title || link.innerText || 'No title';
                        
                        let price = '';
                        if (card && card.innerText) {
                            const match = card.innerText.match(/Rp\\s*[\\d.,]+\\s*[A-Za-z]*/);
                            if (match) {
                                price = match[0];
                            }
                        }
                        
                        listings.push({
                            url: url,
                            title: title,
                            priceText: price,
                            fullText: card ? card.innerText : ''
                        });
                    } catch (innerErr) {
                        listings.push({error: innerErr.toString(), url: link.href});
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
            html = await tab.evaluate("document.body.innerHTML")
            with open("rumah123_debug.html", "w", encoding="utf-8") as f:
                f.write(str(html))
            self._logger.warning("No listings found, dumped HTML to rumah123_debug.html")
            return listings
            
        for raw in raw_listings:
            try:
                url = raw.get("url", "")
                if not url or "googleads" in url or "adclick" in url or "doubleclick" in url or "/perumahan-baru/" in url:
                    continue

                # Extract listing ID from URL (e.g., .../properti/bekasi/hos1234567/)
                id_match = re.search(r'(hos|apt|lan|com|pro)\d+', url, re.IGNORECASE)
                listing_id = id_match.group(0) if id_match else url.split('/')[-2] if url.endswith('/') else url.split('/')[-1]

                title = raw.get("title", "").strip()
                if not title or title.lower() == "no title" or title.lower() == "loading...":
                    # fallback to first line of text
                    full_text = raw.get("fullText", "")
                    if full_text:
                        lines_temp = [l.strip() for l in full_text.split("\n") if l.strip()]
                        title = lines_temp[0] if lines_temp else "No title"
                    else:
                        title = "No title"

                price_text = raw.get("priceText", "")
                if not price_text:
                    continue

                price_idr = PropertyListing.parse_indonesian_price(price_text)

                text = raw.get("fullText", "")

                # Parse LT, LB, KT, KM
                lt = None
                lb = None
                kt = None
                km = None

                # 1. Structure-based sequential line parsing
                lines = [line.strip() for line in text.split('\n') if line.strip()]
                lt_index = -1
                lb_index = -1
                for idx, line in enumerate(lines):
                    if line.startswith("LT:"):
                        lt_index = idx
                    elif line.startswith("LB:"):
                        lb_index = idx

                def parse_area(val_str: str) -> float | None:
                    num_match = re.search(r'([\d.,]+)', val_str)
                    if num_match:
                        # Extract and clean area number
                        clean_str = num_match.group(1)
                        if ',' in clean_str and '.' in clean_str:
                            clean_str = clean_str.replace('.', '').replace(',', '.')
                        elif ',' in clean_str:
                            clean_str = clean_str.replace(',', '.')
                        try:
                            return float(clean_str)
                        except ValueError:
                            pass
                    return None

                def parse_spec_num(val_str: str) -> int | None:
                    num_match = re.match(r'^\s*(\d+)', val_str)
                    return int(num_match.group(1)) if num_match else None

                if lt_index != -1 and lt_index + 1 < len(lines):
                    lt = parse_area(lines[lt_index + 1])
                if lb_index != -1 and lb_index + 1 < len(lines):
                    lb = parse_area(lines[lb_index + 1])

                if lt_index != -1:
                    spec_lines = []
                    for offset in range(1, 5):
                        idx = lt_index - offset
                        if idx < 0:
                            break
                        line = lines[idx]
                        if re.match(r'^\s*\d+\s*(?:\+\s*\d+)?\s*$', line):
                            spec_lines.append(line)
                        else:
                            break
                    spec_lines.reverse()
                    if len(spec_lines) >= 1:
                        kt = parse_spec_num(spec_lines[0])
                    if len(spec_lines) >= 2:
                        km = parse_spec_num(spec_lines[1])

                # 2. Fallbacks using corrected regexes
                if lt is None:
                    lt_match = re.search(r'LT\s*:\s*(\d+)', text, re.IGNORECASE)
                    lt = float(lt_match.group(1)) if lt_match else None

                if lb is None:
                    lb_match = re.search(r'LB\s*:\s*(\d+)', text, re.IGNORECASE)
                    lb = float(lb_match.group(1)) if lb_match else None

                if kt is None:
                    kt_match = re.search(r'(\d+)\s*(?:\+\s*\d+\s*)?\n*(?:KT|Kamar Tidur)', text, re.IGNORECASE)
                    kt = int(kt_match.group(1)) if kt_match else None

                if km is None:
                    km_match = re.search(r'(\d+)\s*(?:\+\s*\d+\s*)?\n*(?:KM|Kamar Mandi)', text, re.IGNORECASE)
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
        """Check if there is a next page of results.

        BaseScraper.scrape() handles navigation by calling build_search_url
        with the incremented page number — we just need to report whether
        more pages exist.
        """
        js_code = """
        (() => {
            // Check for next page link in pagination
            const links = document.querySelectorAll('a');
            for (const a of links) {
                const href = a.getAttribute('href') || '';
                const text = (a.innerText || '').trim();
                // Look for next-page indicators
                if ((href.includes('page=') && (text === '>' || text === '»' || text === 'Next' || text.includes('Selanjutnya'))) ||
                    a.getAttribute('aria-label') === 'Next page') {
                    return true;
                }
            }
            // Fallback: check if a page=N+1 link exists
            const curUrl = window.location.href;
            const curPage = parseInt((curUrl.match(/page=(\\d+)/) || [0, 1])[1]);
            for (const a of links) {
                const href = a.getAttribute('href') || '';
                const m = href.match(/page=(\\d+)/);
                if (m && parseInt(m[1]) === curPage + 1) return true;
            }
            return false;
        })();
        """
        has_next = await tab.evaluate(js_code)
        return has_next
