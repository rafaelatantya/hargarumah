# HargaRumah Documentation Index

> **Agents: Read this file FIRST before doing any work.**
> **Jika melanjutkan pekerjaan yang sudah dimulai agent sebelumnya → baca [`progress.md`](./progress.md) SEKARANG.**

This is the documentation hub for the HargaRumah property price scraper project.

## Documentation Map

| Document | Path | Description |
|---|---|---|
| **🔴 Progress Tracker** | [`progress.md`](./progress.md) | Status per website + agent handoff protocol |
| **Agent Instructions** | [`AGENTS.md`](../AGENTS.md) | Project rules, conventions, how to work |
| **Architecture** | [`architecture.md`](./architecture.md) | System design, data flow, component map |
| **Anti-Detection** | [`anti-detection.md`](./anti-detection.md) | Stealth scraping strategies |
| **Data Schema** | [`data-schema.md`](./data-schema.md) | Output data specification |
| **Website Guides** | [`websites/`](./websites/) | Per-site scraping documentation |

## Website Documentation

Each target website has its own documentation file:

| Website | Doc File | Status |
|---|---|---|
| Rumah123 | [`websites/rumah123.md`](./websites/rumah123.md) | ✅ Explored |
| PasHouses | [`websites/pashouses.md`](./websites/pashouses.md) | 🔲 Not explored |
| OLX Indonesia | [`websites/olx.md`](./websites/olx.md) | ✅ Explored |
| Dekoruma | [`websites/dekoruma.md`](./websites/dekoruma.md) | ✅ Explored (pagination TBD) |
| Pinhome | [`websites/pinhome.md`](./websites/pinhome.md) | ✅ Explored |
| CariProperti | [`websites/cariproperti.md`](./websites/cariproperti.md) | 🔲 Not explored |
| 99.co | [`websites/99co.md`](./websites/99co.md) | ✅ Explored |
| EasyFind | [`websites/easyfind.md`](./websites/easyfind.md) | 🔲 Not explored |

## Configuration Files

| File | Path | Description |
|---|---|---|
| Target Registry | [`config/targets.yaml`](../config/targets.yaml) | Website URLs & metadata |
| Browser Profiles | [`config/browser_profiles.yaml`](../config/browser_profiles.yaml) | Fingerprint configs |
| Defaults | [`config/default.yaml`](../config/default.yaml) | Scraping parameters |

## How to Add a New Website

1. Copy `websites/_template.md` to `websites/<new-site>.md`
2. Have an Explorer Agent browse the site and fill in the template
3. Add the site to `config/targets.yaml`
4. Implement scraper in `src/scrapers/<new-site>.py` following `BaseScraper`
5. Update this README's website table
