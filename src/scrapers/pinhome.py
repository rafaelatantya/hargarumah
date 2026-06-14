import logging
import re
from typing import Any

from src.core.base_scraper import BaseScraper
from src.models.property import PropertyListing

logger = logging.getLogger(__name__)


class PinhomeScraper(BaseScraper):
    """Scraper for Pinhome.id

    As of June 2026, Pinhome no longer supports city/district URL filtering.
    The browse page is simply /jual/rumah/ with ?page=N pagination.
    Detail links use /dijual/rumah-baru/ and /dijual/rumah-sekunder/unit/.
    """

    site_name = "pinhome"
    base_url = "https://www.pinhome.id"

    async def build_search_url(self, area_name: str, page: int = 1) -> str:
        """Construct the search URL.
        Pinhome supports keyword search via ?keyword= parameter.
        """
        keyword = area_name.replace("/", " ").replace("_", " ").replace("-", " ").strip()
        url = f"{self.base_url}/jual/rumah/?keyword={keyword}"
        if page > 1:
            url += f"&page={page}"
        return url

    async def extract_listings(self, tab: Any) -> list[PropertyListing]:
        """Extract property listings from the current page."""

        # 1. Close popup if visible
        close_popup_js = """
        (() => {
            try {
                // Close any overlay/modal with close buttons
                const closeBtns = Array.from(document.querySelectorAll('button, div, span')).filter(el => {
                    const txt = (el.innerText || '').trim();
                    return txt === '✕' || txt === 'X' || txt.toLowerCase() === 'tutup';
                });
                for (const btn of closeBtns) {
                    try { btn.click(); } catch (e) {}
                }
            } catch (e) {}
        })();
        """
        await tab.evaluate(close_popup_js)

        # 2. Scroll to load lazy content
        await self.browser.scroll_page(tab, scroll_count=8)

        # 3. Extract card listings via JS
        js_code = """
        (() => {
            try {
                const listings = [];
                const links = document.querySelectorAll('a');
                const seen = new Set();
                for (const link of links) {
                    try {
                        const url = link.href;
                        if (!url || seen.has(url)) continue;

                        // Match property detail links
                        const isDetail = url.includes('/dijual/rumah-baru/') || url.includes('/dijual/rumah-sekunder/');
                        if (!isDetail) continue;

                        seen.add(url);

                        // Walk up to find the card container
                        let card = link;
                        for (let i = 0; i < 8; i++) {
                            if (card.parentElement) {
                                card = card.parentElement;
                                // Stop when we find a container with enough text
                                if (card.innerText && card.innerText.length > 100 &&
                                    card.innerText.includes('Rp')) {
                                    break;
                                }
                            }
                        }

                        const fullText = card.innerText || '';
                        if (!fullText || !fullText.includes('Rp')) continue;

                        listings.push({
                            url: url,
                            fullText: fullText
                        });
                    } catch (innerErr) {}
                }
                return JSON.stringify(listings);
            } catch (err) {
                return JSON.stringify([]);
            }
        })();
        """

        raw_result = await tab.evaluate(js_code)
        import json
        raw_listings = json.loads(raw_result)

        listings = []
        if not raw_listings:
            html = await tab.evaluate("document.body.innerHTML")
            with open("pinhome_debug.html", "w", encoding="utf-8") as f:
                f.write(html)
            self._logger.warning("No listings found, dumped HTML to pinhome_debug.html")
            return listings

        for raw in raw_listings:
            try:
                url = raw.get("url", "")
                if not url:
                    continue

                # Extract listing ID from URL slug
                parts = url.rstrip("/").split("/")
                listing_id = parts[-1] if parts[-1] else parts[-2]

                text = raw.get("fullText", "")
                lines = [line.strip() for line in text.split('\n') if line.strip()]
                if not lines:
                    continue

                # Extract title: find the longest descriptive line
                title = None
                for line in lines:
                    if "Rp" in line or "KPR" in line or "Brosur" in line or "Chat" in line:
                        continue
                    if "Diperbarui" in line or "Agen" in line or "Developer" in line:
                        continue
                    if len(line) > 20 and not re.match(r'^\d', line):
                        title = line
                        break
                if not title:
                    # Fallback: use lines that look like a property name
                    for line in lines:
                        if len(line) > 10 and "Rp" not in line and "LT" not in line:
                            title = line
                            break
                if not title:
                    title = listing_id

                # Extract price - first "Rp" line
                price_text = None
                for line in lines:
                    if "Rp" in line and "KPR" not in line:
                        price_text = line
                        break

                if not price_text:
                    continue

                # For price ranges like "Rp 1,09 Miliar - Rp 1,78 Miliar", take the first
                price_text_clean = price_text.split(" - ")[0].strip()
                price_idr = PropertyListing.parse_indonesian_price(price_text_clean)

                lt = lb = kt = km = None

                # Parse LT/LB from text
                lt_match = re.search(r'LT\s*([\d.,]+)', text, re.IGNORECASE)
                lb_match = re.search(r'LB\s*([\d.,]+)', text, re.IGNORECASE)
                if lt_match:
                    lt = self._parse_area(lt_match.group(1))
                if lb_match:
                    lb = self._parse_area(lb_match.group(1))

                # Parse KT/KM - look for lines with just numbers before LT
                # Pattern in body: "3-5\n2-4\nLT 88 - 262 m²\nLB 75 - 184 m²"
                # or "2\n1\nLT 244 m²\nLB 90 m²"
                for idx, line in enumerate(lines):
                    if "LT" in line and "LT" == line[:2].upper():
                        # Look backward for number-only lines
                        nums_before = []
                        for back in range(1, 4):
                            prev_idx = idx - back
                            if prev_idx < 0:
                                break
                            prev = lines[prev_idx].strip()
                            # Match "3", "3-5", "2-4" patterns
                            if re.match(r'^\d+(?:\s*[-]\s*\d+)?$', prev):
                                nums_before.insert(0, prev)
                            else:
                                break
                        if len(nums_before) >= 2 and kt is None:
                            # First is bedrooms, second is bathrooms
                            kt = self._parse_range_first(nums_before[0])
                            km = self._parse_range_first(nums_before[1])
                        elif len(nums_before) == 1 and kt is None:
                            kt = self._parse_range_first(nums_before[0])
                        break

                # Location extraction
                location = None
                for line in lines:
                    if "," in line and ("Kota" in line or "Kab" in line):
                        location = line
                        break

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
                    address=location,
                    property_type="rumah",
                    listing_type="dijual"
                )
                listings.append(listing)
            except Exception as e:
                self._logger.warning(f"Failed to parse listing {raw.get('url')}: {e}")

        return listings

    async def get_next_page(self, tab: Any) -> bool:
        """Check if there is a next page."""
        js_code = """
        (() => {
            // Look for pagination with a "next" or ">" button
            const allLinks = document.querySelectorAll('a');
            for (const a of allLinks) {
                const text = (a.innerText || '').trim();
                if (text === '>' || text === 'Next' || text === '»') {
                    return true;
                }
            }
            // Also check for numbered pagination where current page < last page
            const pageNums = document.querySelectorAll('[class*="pagination"] a, [class*="Pagination"] a');
            if (pageNums.length > 0) {
                return true;
            }
            return false;
        })();
        """
        has_next = await tab.evaluate(js_code)
        return has_next

    @staticmethod
    def _parse_area(val_str: str) -> float | None:
        """Parse area value like '72', '1,200', '88 - 262' (takes first)."""
        # Take first number in a range
        val_str = val_str.split("-")[0].strip()
        num_match = re.search(r'([\d.,]+)', val_str)
        if num_match:
            clean = num_match.group(1)
            if ',' in clean and '.' in clean:
                clean = clean.replace('.', '').replace(',', '.')
            elif ',' in clean:
                clean = clean.replace(',', '.')
            try:
                return float(clean)
            except ValueError:
                pass
        return None

    @staticmethod
    def _parse_range_first(val_str: str) -> int | None:
        """Parse '3' or '3-5' and return the first number."""
        m = re.match(r'(\d+)', val_str.strip())
        return int(m.group(1)) if m else None
