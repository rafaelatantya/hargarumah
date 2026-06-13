import logging
import re
import asyncio
from typing import Any

from src.core.base_scraper import BaseScraper
from src.models.property import PropertyListing

logger = logging.getLogger(__name__)

class EasyfindScraper(BaseScraper):
    """Scraper for Easyfind.id"""

    site_name = "easyfind"
    base_url = "https://www.easyfind.id"

    async def build_search_url(self, area_name: str, page: int = 1) -> str:
        """Construct the search URL for a given area and page number."""
        area_key = area_name.lower().replace("_", "-")
        query_area = area_name.replace("-", " ")
        
        # Easyfind uses search parameters
        city_param = "Kota Bekasi" # Defaulting for simplicity per spec
        if "/" in area_key:
            parts = area_key.split("/")
            if "jakarta" in parts[0]:
                city_param = f"Kota {parts[0].replace('-', ' ').title()}"
            query_area = parts[1].replace("-", " ")
            
        url = f"{self.base_url}/properties?query=Rumah+{query_area}&city={city_param.replace(' ', '+')}&page={page}"
        return url

    async def extract_listings(self, tab: Any) -> list[PropertyListing]:
        """Extract property listings from the current page."""
        
        js_code = """
        (() => {
            try {
                const listings = [];
                const cards = document.querySelectorAll('a[href^="/properties/"]');
                
                for (const card of cards) {
                    try {
                        const href = card.getAttribute('href');
                        if (!href) continue;
                        
                        const titleEl = card.querySelector('h3');
                        const title = titleEl ? titleEl.innerText : '';
                        
                        let priceText = '';
                        const divs = card.querySelectorAll('div');
                        for (const div of divs) {
                            if (div.innerText.includes('Juta') || div.innerText.includes('Milyar')) {
                                priceText = div.innerText;
                                break;
                            }
                        }
                        
                        const locEl = card.querySelector('figure');
                        const location = locEl ? locEl.innerText : '';
                        
                        listings.push({
                            url: 'https://www.easyfind.id' + href,
                            title: title,
                            location: location,
                            priceText: priceText
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
                    
                price_idr = PropertyListing.parse_indonesian_price(price_text)
                if not price_idr:
                    continue
                    
                listing_id = url.split('/')[-1]
                
                listing = PropertyListing(
                    id=listing_id,
                    source=self.site_name,
                    title=title,
                    price_idr=price_idr,
                    url=url,
                    land_area_m2=None, # Extracted from detail page usually for Easyfind
                    building_area_m2=None,
                    bedrooms=None,
                    bathrooms=None,
                    property_type="rumah",
                    listing_type="dijual"
                )
                listings.append(listing)
            except Exception as e:
                self._logger.warning(f"Failed to parse Easyfind listing {url}: {e}")
                
        return listings

    async def get_next_page(self, tab: Any) -> bool:
        """Handled by URL structure"""
        js_code = """
        (() => {
            return document.querySelectorAll('a[href^="/properties/"]').length > 0;
        })();
        """
        has_next = await tab.evaluate(js_code)
        return has_next
