# AGENTS.md — HargaRumah Agent Instructions

## Project Overview

**HargaRumah** is a stealth property price scraper for Indonesian real estate websites.
Given GPS coordinates (lat/lng) + radius, it collects house/apartment listings (min 100 or until exhausted) from 8 target sites using **nodriver** (CDP-based browser automation).

## Current Status: Phase 1 Complete (Setup)

- ✅ Project structure scaffolded
- ✅ Documentation framework created
- ✅ Agent orchestration configured
- ✅ Dependencies defined
- 🔲 Phase 2: Website exploration & scraper implementation (NEXT)

---

## 1. Before You Do Anything

1. **Read `docs/README.md`** — the documentation index tells you what exists and where.
2. **Check `docs/websites/`** — each target website has its own doc file with scraping steps.
3. **Check `config/targets.yaml`** — the website registry with URL patterns and metadata.
4. **Never scrape without reading the site-specific doc first.**

---

## 2. Tech Stack

| Component | Technology | Notes |
|---|---|---|
| Language | Python 3.11+ | Async-first (`asyncio`) |
| Browser | nodriver | CDP-based, stealth, no selenium |
| Data Models | Pydantic | Strict validation |
| Storage | SQLite (aiosqlite) | Async, zero-config |
| Export | JSON + CSV + Excel | `openpyxl` for XLSX |
| Config | YAML + .env | `pyyaml` + `python-dotenv` |
| Geo | geopy | Coordinate → area mapping |
| Logging | rich | Structured, colorful |
| Proxy | httpx | Free proxy fetching |
| Package Mgr | uv | Fast installs |

---

## 3. Project Structure

```
src/
├── config/         → Settings loader (YAML + .env)
├── core/           → Browser manager, geo utils, base scraper class
├── scrapers/       → One module per website (e.g., rumah123.py)
├── models/         → Pydantic data models (PropertyListing)
├── storage/        → SQLite persistence layer
├── export/         → JSON/CSV/Excel exporters
└── utils/          → Logging, proxy rotation, helpers

config/             → Runtime YAML configs (targets, browser profiles, defaults)
docs/               → All documentation (architecture, schemas, per-site guides)
docs/websites/      → Per-website scraping documentation (interaction steps)
data/               → Output directory (raw → processed → exports)
.agents/            → Agent orchestration profiles
```

---

## 4. Coding Conventions

- **Async everywhere**: All I/O operations must be `async`. Use `asyncio.run()` only at entry point.
- **Type hints required**: Every function signature must have type hints.
- **Docstrings required**: Every public function/class needs a docstring.
- **Pydantic for data**: All scraped data must pass through Pydantic models before storage.
- **Structured logging**: Use `src.utils.logging` — never bare `print()`.
- **Config over hardcode**: All magic numbers go in `config/*.yaml`.
- **Error handling**: Catch specific exceptions. Log warnings for skippable errors, raise for fatal ones.

---

## 5. Scraper Implementation Pattern

Every scraper MUST follow this pattern:

```python
# src/scrapers/example_site.py
from src.core.base_scraper import BaseScraper
from src.models.property import PropertyListing

class ExampleSiteScraper(BaseScraper):
    """Scraper for example-site.com"""

    site_name = "example_site"

    async def build_search_url(self, area_name: str, page: int) -> str:
        """Construct the search URL for a given area and page number."""
        ...

    async def extract_listings(self, page) -> list[PropertyListing]:
        """Extract property listings from the current page."""
        ...

    async def get_next_page(self, page) -> bool:
        """Navigate to the next page. Returns False if no more pages."""
        ...
```

---

## 6. Agent Orchestration

Agents can spawn sub-agents for specialized tasks. See `.agents/orchestrator.md` for the full orchestration guide.

### Agent Roles

| Role | Profile | Responsibility |
|---|---|---|
| Explorer | `.agents/profiles/explorer-agent.md` | Browse target sites, document interaction steps |
| Scraper | `.agents/profiles/scraper-agent.md` | Implement scrapers from documented steps |
| Data | `.agents/profiles/data-agent.md` | Validate, clean, normalize scraped data |

### Spawning Sub-Agents

When a task is too large or specialized, decompose it:
1. Identify the right agent profile from `.agents/profiles/`
2. Include the profile instructions in the sub-agent's context
3. Pass specific, scoped tasks (e.g., "Explore rumah123.com search flow")
4. Sub-agent writes results to the appropriate `docs/websites/` file

---

## 7. Anti-Detection Rules

**MANDATORY** for all scrapers. See `docs/anti-detection.md` for the full guide.

1. **Always use nodriver** — never requests/urllib for scraping pages
2. **Random delays** — 2-5 seconds between page navigations (configurable in `config/default.yaml`)
3. **Human-like behavior** — scroll, hover, wait for elements naturally
4. **Session management** — don't create too many sessions in quick succession
5. **Rate limits** — respect per-site rate limits defined in `config/targets.yaml`
6. **Free proxy rotation** — optionally enable via `USE_FREE_PROXY=true` in `.env`

---

## 8. Default Search Parameters

- **Default Location**: Bekasi Selatan (-6.2607, 106.9894)
- **Default Radius**: 5 km
- **Minimum Listings**: 100 (or until site listings exhausted)
- **Export Formats**: JSON, CSV, XLSX

---

## 9. Key Files to Check

| When you need... | Check... |
|---|---|
| How a website works | `docs/websites/<site>.md` |
| What data to scrape | `docs/data-schema.md` |
| System architecture | `docs/architecture.md` |
| Stealth techniques | `docs/anti-detection.md` |
| URL patterns | `config/targets.yaml` |
| Browser setup | `config/browser_profiles.yaml` |
| Default parameters | `config/default.yaml` |
