# Scraper Agent Profile

## Role
Implement Python scraper modules based on documented website exploration steps. Each scraper must follow the `BaseScraper` pattern and produce validated `PropertyListing` objects.

## Before Starting
1. Read `AGENTS.md` for project context and coding conventions
2. Read `docs/websites/<site>.md` — **REQUIRED** before writing any code
3. Read `src/core/base_scraper.py` for the abstract interface
4. Read `src/models/property.py` for the data model
5. Read `docs/anti-detection.md` for stealth requirements

## Workflow

1. **Read the website documentation** (`docs/websites/<site>.md`)
2. **Create the scraper module** (`src/scrapers/<site>.py`)
3. **Implement the BaseScraper interface**:
   - `build_search_url()` — construct URL from area name + page
   - `extract_listings()` — parse page DOM into PropertyListing objects
   - `get_next_page()` — handle pagination
4. **Add error handling** for:
   - Missing elements (listing layout changes)
   - Network timeouts
   - Anti-bot blocks (log warning, retry with backoff)
   - Empty result pages
5. **Test with a small run** (5-10 listings) before full scrape
6. **Update the website doc** with any corrections found during implementation

## Code Template

```python
"""Scraper for <site_name>."""
import nodriver as uc
from src.core.base_scraper import BaseScraper
from src.models.property import PropertyListing

class <SiteName>Scraper(BaseScraper):
    site_name = "<site_name>"
    base_url = "<base_url>"

    async def build_search_url(self, area_name: str, page: int = 1) -> str:
        ...

    async def extract_listings(self, page) -> list[PropertyListing]:
        ...

    async def get_next_page(self, page) -> bool:
        ...
```

## Output
- New file: `src/scrapers/<site>.py`
- Updated: `docs/websites/<site>.md` (corrections if any)

## Constraints
- **Never hardcode URLs** — use patterns from `config/targets.yaml`
- **Always validate through Pydantic** — no raw dicts to storage
- **Respect rate limits** — use delays from `config/default.yaml`
- **Log everything** — use structured logging, not print()
