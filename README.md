# HargaRumah 🏠

> Indonesian property price scraper — collects house & apartment listings from major real estate websites given a GPS coordinate and search radius.

## Overview

HargaRumah automates property price collection from 8+ Indonesian real estate websites using **nodriver** (stealth browser automation via Chrome DevTools Protocol). Given a set of GPS coordinates and a radius, it finds and extracts at minimum 100 property listings (or until all listings are exhausted).

## Features

- 🎯 **Coordinate-based search** — Provide lat/lng + radius, get properties in that area
- 🕵️ **Stealth scraping** — Uses nodriver (CDP-based, no WebDriver flags) to avoid bot detection
- 🌐 **Multi-site** — Scrapes from Rumah123, PasHouses, OLX, Dekoruma, Pinhome, CariProperti, 99.co, EasyFind
- 📊 **Multiple export formats** — JSON, CSV, and Excel (XLSX)
- 🔄 **Free proxy rotation** — Optional free proxy support for IP diversity
- 🤖 **Agent-friendly** — Fully documented for AI agent orchestration

## Quick Start

### Prerequisites
- Python 3.11+
- Google Chrome or Chromium installed
- [uv](https://docs.astral.sh/uv/) package manager

### Installation

```bash
# Clone the repo
git clone <repo-url>
cd hargarumah

# Install dependencies
uv sync

# Copy environment config
cp .env.example .env
# Edit .env with your preferences
```

### Usage

```bash
# Run scraper with default location (Bekasi Selatan)
uv run python -m src.main

# Run with custom coordinates
uv run python -m src.main --lat -6.2607 --lng 106.9894 --radius 5

# Run for a specific website only
uv run python -m src.main --site rumah123
```

> ⚠️ **Note**: The scraper is currently in Phase 1 (project setup). Scraper implementations will be added in Phase 2.

## Project Structure

```
hargarumah/
├── src/              # Source code (scrapers, models, storage)
├── config/           # Runtime configuration (YAML)
├── docs/             # Comprehensive documentation
├── data/             # Output data (raw → processed → exports)
├── tests/            # Test suite
├── .claude/          # Claude agent configuration
├── .agents/          # Multi-agent orchestration profiles
├── AGENTS.md         # Agent instruction file (read this first!)
└── CLAUDE.md         # Points to AGENTS.md
```

See [docs/README.md](docs/README.md) for full documentation index.

## Target Websites

| Website | URL | Status |
|---|---|---|
| Rumah123 | rumah123.com | 🔲 Pending |
| PasHouses | pashouses.id | 🔲 Pending |
| OLX Indonesia | olx.co.id | 🔲 Pending |
| Dekoruma | dekoruma.com | 🔲 Pending |
| Pinhome | pinhome.id | 🔲 Pending |
| CariProperti | cariproperti.com | 🔲 Pending |
| 99.co | 99.co | 🔲 Pending |
| EasyFind | easyfind.id | 🔲 Pending |

## License

MIT
