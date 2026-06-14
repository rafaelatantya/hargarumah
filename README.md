# HargaRumah 🏠

> Indonesian property price scraper — collects house & apartment listings from 8 real estate websites given a GPS coordinate and search radius.

## Overview

HargaRumah automates property price collection from 8 Indonesian real estate websites using **nodriver** (stealth browser automation via Chrome DevTools Protocol). Given GPS coordinates and a radius, it finds and extracts property listings with pricing, specs, and location data.

## Features

- 🎯 **Coordinate-based search** — Provide lat/lng + radius, get properties in that area
- 🕵️ **Stealth scraping** — Uses nodriver (CDP-based, no WebDriver flags) to avoid bot detection
- 🌐 **8 target sites** — Rumah123, 99.co, Pinhome, OLX, CariProperti, Dekoruma, PasHouses, EasyFind
- 📊 **Multiple exports** — JSON, CSV, and Excel (XLSX)
- 🔄 **Free proxy rotation** — Optional free proxy support for IP diversity

## Quick Start

### Prerequisites
- Python 3.11+
- Google Chrome or Chromium
- [uv](https://docs.astral.sh/uv/) package manager

### Installation

```bash
git clone <repo-url>
cd hargarumah
uv sync
cp .env.example .env
```

### Usage

```bash
# Search by keyword (default: Rumah123)
uv run python main.py harjamukti

# With custom limits
uv run python main.py "bekasi selatan" --min 20 --pages 3
```

## Target Websites

| Website | URL | Scraper | Pagination |
|---|---|---|---|
| Rumah123 | rumah123.com | ✅ `rumah123.py` | `?page=N` |
| 99.co | 99.co | ✅ `ninetynine_co.py` | `?hlmn=N` |
| Pinhome | pinhome.id | ✅ `pinhome.py` | `?page=N` |
| OLX Indonesia | olx.co.id | ✅ `olx.py` | Load More |
| CariProperti | cariproperti.com | ✅ `cariproperti.py` | AJAX Next |
| Dekoruma | dekoruma.com | ✅ `dekoruma.py` | `?page=N` |
| PasHouses | pashouses.id | ✅ `pashouses.py` | URL path `/N` |
| EasyFind | easyfind.id | ✅ `easyfind.py` | `?page=N` |

## Project Structure

```
hargarumah/
├── main.py           # CLI entry point
├── src/
│   ├── config/       # Settings (YAML + .env)
│   ├── core/         # Browser manager, base scraper, geo utils
│   ├── scrapers/     # 8 site-specific scraper modules
│   ├── models/       # PropertyListing Pydantic model
│   ├── storage/      # SQLite persistence
│   ├── export/       # JSON/CSV/XLSX exporters
│   └── utils/        # Logging, proxy rotation
├── config/           # YAML configs (targets, browser profiles, defaults)
├── docs/             # Architecture, anti-detection, data schema, per-site guides
└── tests/            # Test suite
```

See [docs/README.md](docs/README.md) for full documentation index.

## License

MIT
