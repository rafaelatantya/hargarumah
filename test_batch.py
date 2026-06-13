import asyncio
import logging
import sys

from src.core.browser import BrowserManager
from src.scrapers.cariproperti import CariPropertiScraper

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(name)s] %(levelname)s: %(message)s")

async def test_cariproperti():
    browser = await BrowserManager.create()
    try:
        scraper = CariPropertiScraper(browser)
        # CariProperti uses area slug like "bekasi"
        listings = await scraper.scrape("bekasi", min_listings=10)
        print(f"\n[CariProperti] Scraped {len(listings)} listings:")
        for i, lst in enumerate(listings[:10]):
            print(f"  {i+1}. {lst.title} - Rp {lst.price_idr:,} - {lst.url}")
            print(f"     LT: {lst.land_area_m2} | LB: {lst.building_area_m2} | KT: {lst.bedrooms} | KM: {lst.bathrooms}")
    finally:
        await browser.close()

if __name__ == "__main__":
    asyncio.run(test_cariproperti())
