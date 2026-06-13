import logging
import re
from typing import Any

from src.core.base_scraper import BaseScraper
from src.models.property import PropertyListing

logger = logging.getLogger(__name__)


class PinhomeScraper(BaseScraper):
    """Scraper for Pinhome.id"""

    site_name = "pinhome"
    base_url = "https://www.pinhome.id"

    async def build_search_url(self, area_name: str, page: int = 1) -> str:
        """Construct the search URL for a given area and page number."""
        if "/" in area_name:
            parts = area_name.split("/")
            if len(parts) >= 2:
                city, district = parts[-2], parts[-1]
            else:
                city, district = "bekasi", area_name
        else:
            city = "bekasi"
            district = area_name

        city_lower = city.lower()
        district_lower = district.lower().replace("_", "-")

        # Map to proper Pinhome geography path: {province}/{city}/{district}
        if "bekasi" in city_lower:
            province = "jawa-barat"
            city_path = "bekasi"
        elif "jakarta-selatan" in city_lower:
            province = "dki-jakarta"
            city_path = "jakarta-selatan"
        elif "jakarta-barat" in city_lower:
            province = "dki-jakarta"
            city_path = "jakarta-barat"
        elif "jakarta-timur" in city_lower:
            province = "dki-jakarta"
            city_path = "jakarta-timur"
        elif "jakarta-utara" in city_lower:
            province = "dki-jakarta"
            city_path = "jakarta-utara"
        elif "jakarta-pusat" in city_lower:
            province = "dki-jakarta"
            city_path = "jakarta-pusat"
        elif "tangerang-selatan" in city_lower:
            province = "banten"
            city_path = "tangerang-selatan"
        elif "tangerang" in city_lower:
            province = "banten"
            city_path = "tangerang"
        elif "depok" in city_lower:
            province = "jawa-barat"
            city_path = "depok"
        elif "bogor" in city_lower:
            province = "jawa-barat"
            city_path = "bogor"
        elif "bandung" in city_lower:
            province = "jawa-barat"
            city_path = "bandung"
        else:
            province = "jawa-barat"
            city_path = city_lower

        url = f"{self.base_url}/jual/rumah/{province}/{city_path}/{district_lower}/"
        if page > 1:
            url += f"?page={page}"
        return url

    async def extract_listings(self, tab: Any) -> list[PropertyListing]:
        """Extract property listings from the current page."""

        # 1. Close popup if visible
        close_popup_js = """
        (() => {
            try {
                const closeBtns = Array.from(document.querySelectorAll('button, div, span, a')).filter(el => {
                    const cls = (el.className || '').toString().toLowerCase();
                    const id = (el.id || '').toString().toLowerCase();
                    const txt = el.innerText || '';
                    return cls.includes('close') || id.includes('close') || txt === '✕' || txt.toLowerCase() === 'tutup' || txt.toLowerCase().includes('close');
                });
                for (const btn of closeBtns) {
                    try {
                        btn.click();
                    } catch (err) {}
                }
            } catch (e) {}
        })();
        """
        await tab.evaluate(close_popup_js)

        # 2. Scroll to load lazy content
        await self.browser.scroll_page(tab, scroll_count=6)

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

                        // Check if it is a property detail page link
                        const isDetail = url.includes('/dijual/rumah-baru/') || url.includes('/dijual/rumah-sekunder/');
                        if (!isDetail) continue;

                        seen.add(url);

                        let card = link.parentElement;
                        let foundCard = false;
                        for (let i = 0; i < 10; i++) {
                            if (card && card.className && (
                                card.className.includes('pin-card__base') ||
                                card.className.includes('card-list-wrapper') ||
                                card.className.includes('pin-card_standard')
                            )) {
                                foundCard = true;
                                break;
                            }
                            if (card) card = card.parentElement;
                        }
                        if (!foundCard) {
                            card = link.parentElement?.parentElement?.parentElement || link;
                        }

                        let title = '';
                        const titleEl = card.querySelector('h1, h2, h3, h4, h5, [class*="title"], [class*="Title"]');
                        if (titleEl) {
                            title = titleEl.innerText;
                        } else {
                            title = link.title || link.innerText || 'No title';
                        }

                        let price = '';
                        const priceMatch = card.innerText.match(/Rp\\s*[\\d.,]+\\s*[A-Za-z]*/);
                        if (priceMatch) {
                            price = priceMatch[0];
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
            with open("pinhome_debug.html", "w", encoding="utf-8") as f:
                f.write(html)
            self._logger.warning("No listings found, dumped HTML to pinhome_debug.html")
            return listings

        for raw in raw_listings:
            try:
                url = raw.get("url", "")
                if "error" in raw or not url:
                    continue

                # Extract listing ID (slug at end of path)
                listing_id = url.split('/')[-1] if url.split('/')[-1] else url.split('/')[-2]

                title = raw.get("title", "").strip()
                if not title:
                    title = raw.get("fullText", "").split("\n")[0]

                price_text = raw.get("priceText", "")
                if not price_text:
                    continue

                price_idr = PropertyListing.parse_indonesian_price(price_text)

                text = raw.get("fullText", "")
                lines = [line.strip() for line in text.split('\n') if line.strip()]

                lt = None
                lb = None
                kt = None
                km = None

                # Area parser helper
                def parse_area(val_str: str) -> float | None:
                    num_match = re.search(r'([\d.,]+)', val_str)
                    if num_match:
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

                # Parse LT, LB
                lt_match = re.search(r'LT\s*([\d.,]+)', text, re.IGNORECASE)
                lb_match = re.search(r'LB\s*([\d.,]+)', text, re.IGNORECASE)
                lt = parse_area(lt_match.group(1)) if lt_match else None
                lb = parse_area(lb_match.group(1)) if lb_match else None

                # Parse KT, KM (explicit tags)
                kt_match = re.search(r'(\d+)\s*(?:KT|Kamar Tidur|🛏)', text, re.IGNORECASE)
                km_match = re.search(r'(\d+)\s*(?:KM|Kamar Mandi|🚿)', text, re.IGNORECASE)

                if kt_match:
                    kt = int(kt_match.group(1))
                if km_match:
                    km = int(km_match.group(1))

                # Structure-based preceding sequential lines (e.g. 3 \n 1 \n LT 58 m2)
                lt_index = -1
                for idx, line in enumerate(lines):
                    if "LT" in line:
                        lt_index = idx
                        break

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
                    if len(spec_lines) >= 1 and kt is None:
                        kt = parse_spec_num(spec_lines[0])
                    if len(spec_lines) >= 2 and km is None:
                        km = parse_spec_num(spec_lines[1])

                # Fallback to specs single-line layout (e.g. 3 • 1 • LT 72 m² • LB 48 m²)
                if kt is None or km is None:
                    for line in lines:
                        if "LT" in line:
                            prefix = line.split("LT")[0]
                            nums = re.findall(r'(\d+)', prefix)
                            if len(nums) >= 1 and kt is None:
                                kt = int(nums[0])
                            if len(nums) >= 2 and km is None:
                                km = int(nums[1])
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
            const pagination = document.querySelector('[class*="pagination"], [class*="Pagination"]');
            if (!pagination) return false;

            const nextBtn = pagination.querySelector('a:last-child, button:last-child, [class*="next"], [class*="Next"]');
            if (nextBtn && !nextBtn.classList.contains('disabled') && !nextBtn.hasAttribute('disabled') && !nextBtn.parentElement.classList.contains('disabled')) {
                return true;
            }
            return false;
        })();
        """
        has_next = await tab.evaluate(js_code)
        return has_next
