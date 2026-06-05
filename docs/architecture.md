# System Architecture

## High-Level Data Flow

```
┌─────────────┐      ┌──────────────┐      ┌──────────────┐      ┌──────────────┐
│  User Input │      │  Geo Module  │      │   Browser    │      │   Scraper    │
│  (lat,lng,  │─────▶│  Coord →     │─────▶│   Manager    │─────▶│   Engine     │
│   radius)   │      │  Area Name   │      │  (nodriver)  │      │  (per-site)  │
└─────────────┘      └──────────────┘      └──────────────┘      └──────┬───────┘
                                                                        │
                                                                        ▼
┌─────────────┐      ┌──────────────┐      ┌──────────────┐      ┌──────────────┐
│   Export    │◀─────│  Data Agent  │◀─────│   Storage    │◀─────│  Pydantic    │
│  JSON/CSV/ │      │  (clean,     │      │  (SQLite)    │      │  Validation  │
│   XLSX     │      │   normalize) │      │              │      │              │
└─────────────┘      └──────────────┘      └──────────────┘      └──────────────┘
```

## Component Responsibilities

### 1. Geo Module (`src/core/geo.py`)
- Converts GPS coordinates (lat/lng) to human-readable area names
- Calculates which listings fall within the search radius
- Maps area names to website-specific location identifiers

### 2. Browser Manager (`src/core/browser.py`)
- Initializes nodriver with stealth configuration
- Manages browser sessions (open, close, rotate)
- Applies anti-detection settings (fingerprint, timing, user-agent)
- Handles free proxy rotation if enabled

### 3. Base Scraper (`src/core/base_scraper.py`)
- Abstract base class that all site-specific scrapers inherit from
- Defines the scraper interface: `build_search_url()`, `extract_listings()`, `get_next_page()`
- Provides shared utilities: delay management, error handling, retry logic

### 4. Site Scrapers (`src/scrapers/*.py`)
- One module per target website
- Implements the BaseScraper interface
- Handles site-specific URL construction, DOM parsing, pagination
- Each scraper is independent and can run alone or in combination

### 5. Data Models (`src/models/property.py`)
- Pydantic models for `PropertyListing`
- Strict validation: required fields, type checking, value ranges
- Normalization: price format, area units, address cleaning

### 6. Storage (`src/storage/database.py`)
- Async SQLite storage layer
- Schema creation, upsert, query
- Deduplication at storage level

### 7. Export (`src/export/exporter.py`)
- JSON, CSV, and XLSX export
- Includes metadata (scrape date, source, coordinates, radius)
- Excel formatting with headers, auto-width, number formatting

### 8. Utilities (`src/utils/`)
- `logging.py` — Structured logging with Rich
- `proxy.py` — Free proxy fetching and rotation

## Execution Flow

```python
async def main(lat, lng, radius_km):
    # 1. Resolve coordinates to area names
    areas = await geo.resolve_areas(lat, lng, radius_km)

    # 2. Initialize browser with stealth config
    browser = await BrowserManager.create()

    # 3. For each target website
    for scraper_cls in get_enabled_scrapers():
        scraper = scraper_cls(browser)

        # 4. For each area name relevant to this site
        for area in areas:
            listings = await scraper.scrape(area, min_listings=100)

            # 5. Validate and store
            for listing in listings:
                validated = PropertyListing(**listing)
                await storage.save(validated)

    # 6. Export results
    await exporter.export_all(formats=["json", "csv", "xlsx"])
```

## Directory Layout

```
src/
├── __init__.py
├── main.py              # Entry point — CLI argument parsing, orchestration
├── config/
│   ├── __init__.py
│   └── settings.py      # YAML + .env config loading
├── core/
│   ├── __init__.py
│   ├── browser.py       # nodriver browser lifecycle
│   ├── geo.py           # Coordinate ↔ area name conversion
│   └── base_scraper.py  # Abstract scraper interface
├── scrapers/
│   ├── __init__.py      # Scraper registry (auto-discovery)
│   └── <site>.py        # One per website
├── models/
│   ├── __init__.py
│   └── property.py      # PropertyListing Pydantic model
├── storage/
│   ├── __init__.py
│   └── database.py      # SQLite persistence
├── export/
│   ├── __init__.py
│   └── exporter.py      # JSON/CSV/XLSX export
└── utils/
    ├── __init__.py
    ├── logging.py        # Rich-based structured logging
    └── proxy.py          # Free proxy fetcher/rotator
```
