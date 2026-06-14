# CLAUDE.md — Agent Entry Point

> ⚠️ **SEBELUM MELAKUKAN APAPUN: Baca [`docs/progress.md`](./docs/progress.md).**
> ⚠️ **SEBELUM MENGAKHIRI SESI: Update `docs/progress.md` dengan status terakhir.**

---

## Project Overview

**HargaRumah** — stealth property price scraper for 8 Indonesian real estate websites.
Input: GPS coordinates (lat/lng) + radius → Output: min 100 property listings per site.
Browser automation: **nodriver** (CDP-based, no WebDriver flags).

**Current Status**: Phase 3 Complete — all 8 scrapers implemented & tested. Phase 4 (Full Run) next.

---

## Tech Stack

| Component | Technology |
|---|---|
| Language | Python 3.11+ (async-first) |
| Browser | nodriver (CDP) |
| Models | Pydantic v2 |
| Storage | SQLite (aiosqlite) |
| Export | JSON, CSV, XLSX |
| Config | YAML + .env |
| Package Mgr | uv |

---

## Project Structure

```
src/
├── config/settings.py     # YAML + .env config loader
├── core/
│   ├── browser.py         # nodriver browser lifecycle
│   ├── base_scraper.py    # Abstract scraper interface
│   └── geo.py             # Coordinate ↔ area name mapping
├── scrapers/              # One module per website (8 total)
├── models/property.py     # PropertyListing Pydantic model
├── storage/database.py    # SQLite persistence (async)
├── export/exporter.py     # JSON/CSV/XLSX export
└── utils/
    ├── logging.py         # Rich structured logging
    └── proxy.py           # Free proxy rotation

config/                    # Runtime YAML configs
docs/                      # Architecture, anti-detection, data schema
docs/websites/             # Per-site scraping guides
```

---

## Coding Conventions

- **Async everywhere** — all I/O must be `async`. `asyncio.run()` only at entry point.
- **Type hints required** — every function signature.
- **Pydantic for data** — all scraped data validated through `PropertyListing` before storage.
- **Structured logging** — use `src.utils.logging`, never bare `print()`.
- **Config over hardcode** — magic numbers go in `config/*.yaml`.
- **Error handling** — catch specific exceptions. Log warnings for skippable, raise for fatal.

---

## Scraper Pattern

Every scraper inherits `BaseScraper` and implements:

```python
class MySiteScraper(BaseScraper):
    site_name = "my_site"
    base_url = "https://..."

    async def build_search_url(self, area_name: str, page: int = 1) -> str: ...
    async def extract_listings(self, tab) -> list[PropertyListing]: ...
    async def get_next_page(self, tab) -> bool: ...
```

All scrapers use `tab.evaluate(js_code)` → JSON.stringify → `json.loads()` for DOM extraction.

---

## Anti-Detection Rules (mandatory)

1. **Always use nodriver** — never requests/urllib for page scraping
2. **Random delays** — 2-5s between navigations (see `config/default.yaml`)
3. **Human-like behavior** — scroll, hover, wait naturally
4. **Session rotation** — new browser every 100 pages
5. **Rate limits** — respect per-site limits in `config/targets.yaml`

Full guide: [`docs/anti-detection.md`](./docs/anti-detection.md)

---

## Key References

| Need | File |
|---|---|
| Where work left off | [`docs/progress.md`](./docs/progress.md) |
| How a website works | [`docs/websites/<site>.md`](./docs/websites/) |
| What data to scrape | [`docs/data-schema.md`](./docs/data-schema.md) |
| System architecture | [`docs/architecture.md`](./docs/architecture.md) |
| URL patterns & rate limits | [`config/targets.yaml`](./config/targets.yaml) |
| Browser fingerprints | [`config/browser_profiles.yaml`](./config/browser_profiles.yaml) |
| Default parameters | [`config/default.yaml`](./config/default.yaml) |

---

## Default Search Parameters

- **Location**: Bekasi Selatan (-6.2607, 106.9894)
- **Radius**: 5 km
- **Min Listings**: 100 per site
- **Export**: JSON + CSV + XLSX
