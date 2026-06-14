# HargaRumah Documentation Index

> **Agents: Baca [`progress.md`](./progress.md) PERTAMA sebelum melakukan apapun.**

## Documentation Map

| Document | Path | Description |
|---|---|---|
| **🔴 Progress Tracker** | [`progress.md`](./progress.md) | Status terkini + handoff protocol |
| **Agent Instructions** | [`CLAUDE.md`](../CLAUDE.md) | Project rules, conventions |
| **Architecture** | [`architecture.md`](./architecture.md) | System design, data flow |
| **Anti-Detection** | [`anti-detection.md`](./anti-detection.md) | Stealth scraping strategies |
| **Data Schema** | [`data-schema.md`](./data-schema.md) | Output data specification |
| **Website Guides** | [`websites/`](./websites/) | Per-site scraping documentation |

## Website Documentation

| Website | Doc File | Scraper | Status |
|---|---|---|---|
| Rumah123 | [`rumah123.md`](./websites/rumah123.md) | `rumah123.py` | ✅ Implemented |
| 99.co | [`99co.md`](./websites/99co.md) | `ninetynine_co.py` | ✅ Implemented |
| Pinhome | [`pinhome.md`](./websites/pinhome.md) | `pinhome.py` | ✅ Implemented |
| OLX Indonesia | [`olx.md`](./websites/olx.md) | `olx.py` | ✅ Implemented |
| CariProperti | [`cariproperti.md`](./websites/cariproperti.md) | `cariproperti.py` | ✅ Implemented |
| Dekoruma | [`dekoruma.md`](./websites/dekoruma.md) | `dekoruma.py` | ✅ Implemented |
| PasHouses | [`pashouses.md`](./websites/pashouses.md) | `pashouses.py` | ✅ Implemented |
| EasyFind | [`easyfind.md`](./websites/easyfind.md) | `easyfind.py` | ✅ Implemented |

## Configuration Files

| File | Path | Description |
|---|---|---|
| Target Registry | [`config/targets.yaml`](../config/targets.yaml) | Website URLs, rate limits, pagination types |
| Browser Profiles | [`config/browser_profiles.yaml`](../config/browser_profiles.yaml) | Fingerprint rotation configs |
| Defaults | [`config/default.yaml`](../config/default.yaml) | Scraping parameters |

## Adding a New Website

1. Copy `websites/_template.md` → `websites/<new-site>.md`
2. Explore the site and fill in the template
3. Add entry to `config/targets.yaml`
4. Implement scraper in `src/scrapers/<new-site>.py` following `BaseScraper`
5. Update this README's website table
