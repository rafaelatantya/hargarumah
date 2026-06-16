# HargaRumah — Progress Tracker

> **Baca file ini PERTAMA** sebelum melanjutkan pekerjaan apapun.
> Update file ini setiap kali memulai/menyelesaikan task.

---

## Status Phase

| Phase | Status | Catatan |
|---|---|---|
| Phase 1: Project Setup | ✅ Complete | Scaffolding, docs, dependencies |
| Phase 2: Website Exploration | ✅ Complete | Semua 8 website dieksplorasi |
| Phase 3: Scraper Implementation | ✅ Complete | Semua 8 scraper implemented & tested |
| Phase 4: Full Scraping Run | ✅ Complete | SQLite & exports done, tested full run. Data quality validated with strict filtering. |
| Phase 5: Live Demo | ✅ Complete | Harjamukti demo page functional. 55 listings from 1 scraper, strict-filtered. |
| Phase 6: Animated Demo | ✅ Complete | Remotion + React 19 single-page demo. Ocean sunset dusk palette, 18s timeline (typewriter → log stream → stats → 8 cards). Vite + GitHub Pages deploy wired. |

---

## Phase 3: Scraper Status

| Website | Scraper File | Status | Test |
|---|---|---|---|
| Rumah123 | `src/scrapers/rumah123.py` | ✅ Done | Passed |
| 99.co | `src/scrapers/ninetynine_co.py` | ✅ Done | Passed |
| Pinhome | `src/scrapers/pinhome.py` | ✅ Done | Passed |
| OLX Indonesia | `src/scrapers/olx.py` | ✅ Done | Passed |
| CariProperti | `src/scrapers/cariproperti.py` | ✅ Done | Passed |
| Dekoruma | `src/scrapers/dekoruma.py` | ✅ Done | Passed |
| PasHouses | `src/scrapers/pashouses.py` | ✅ Done | Passed |
| EasyFind | `src/scrapers/easyfind.py` | ✅ Done | Passed |

---

## Phase 4: TODO

- [x] Wire all 8 scrapers into `main.py`
- [x] Add `--site` flag to select specific scraper(s)
- [x] Integrate SQLite storage layer into main flow
- [x] Export results to JSON/CSV/XLSX
- [x] Run full scraping session with coordinates/locations
- [x] Validate data quality across all sources (Strict filtering added)

---

## Session Log

| Tanggal | Agent | Pekerjaan | Hasil |
|---|---|---|---|
| 2026-06-05 | Setup | Phase 1: Scaffolding | ✅ 51 files |
| 2026-06-05 | Opus 4.6 | Phase 2: Explore 5/8 sites | ✅ Rumah123, 99.co, OLX, Pinhome, Dekoruma |
| 2026-06-05 | Gemini 3.1 Pro | Phase 2: Explore 3/8 sites | ✅ PasHouses, CariProperti, EasyFind |
| 2026-06-11 | Gemini 3 Flash | Phase 3: Rumah123 bug analysis | ✅ regex + label fixes |
| 2026-06-13 | Multiple agents | Phase 3: All 8 scrapers | ✅ Batch 1-4 complete |
| 2026-06-13 | Claude Code | Rumah123 reliability fix | ✅ keyword search, 20 listings |
| 2026-06-13 | Claude Code | Tools integration | ✅ claude-mem, graphify |
| 2026-06-14 | Claude Code | Docs cleanup & consolidation | ✅ Merged CLAUDE.md+AGENTS.md, deleted junk |
| 2026-06-14 | Antigravity | Orchestrator & CLI integration | ✅ Wired 8 scrapers, DB, exports. Checked "bekasi selatan". Fixed URL generation. |
| 2026-06-14 | Antigravity | Data Quality Enforcement | ✅ Added strict location filter to orchestrator, purged false-positive listings, validated via 'harjamukti, cimanggis, depok' test. Cleaned up dummy files. |
| 2026-06-16 | Claude Code | Harjamukti Live Demo | ✅ Fresh scrape Rumah123 → 55 listings (strict-filtered). Built `site/harjamukti.html` with sort/filter/search. Hero terminal updated to show real run. Verified all 55 pass filter, 0 missing fields. |
| 2026-06-17 | Claude Code | Animated Remotion Demo | ✅ Vite + React 19 + @remotion/player. 18s composition: typewriter CLI command, log stream, stats, 8 listing cards cascade. Ocean sunset dusk palette (night → dusk purple → coral → gold). GitHub Actions deploy workflow with staging step. Verified all URLs 200 on local server. |

---

## Phase 5: Live Demo (Done)

- [x] Fresh scrape `rumah123` on `harjamukti` → 55 listings (3 pages)
- [x] Strict filter validated: 0 violations (all titles contain "harjamukti")
- [x] `site/harjamukti.html` — fully functional demo with sort/filter/search
- [x] `site/data/harjamukti.json` — slim 25 KB data file
- [x] `site/index.html` hero terminal updated to show real run
- [x] "Lihat live demo" CTA + "55" stat card in results section

To preview:
```bash
cd site && python -m http.server 8000
# then open http://localhost:8000/harjamukti.html
```

---

## Phase 6: Animated Demo (Done)

Single-page animated demo at `/animated/`, built with **Remotion + React 19 + Vite**, palette: **ocean sunset dusk** (night → dusk purple → magenta → coral → gold).

**Composition timeline** (30 fps, 18 s):
- 0–3 s: gradient sky + sun glow, eyebrow + serif title fade in
- 2–6 s: CLI window scales up, command types character-by-character
- 6–11 s: log lines stream in (resolving, browser launch, 55 listings, ok, saved)
- 12–13 s: 4 stat cards (count, min, median, max) stagger in
- 14–18 s: 8 cheapest listings cascade up with spring physics

**Files**:
- `site/animated/` — Vite + TS project
  - `src/Composition.tsx` — Remotion composition
  - `src/App.tsx` — wraps `@remotion/player` (autoplay, loop, no controls)
  - `src/theme.css`, `src/styles.css` — ocean sunset dusk + glassmorphism
  - `src/data.json` — embedded listing data (no fetch needed)
- `site/index.html` — CTA "Lihat live demo" → `animated/`
- `.github/workflows/deploy.yml` — build → stage → upload → deploy

**Deploy mechanics** (GitHub Pages):
- Vite outputs to `site/animated/dist/`
- Workflow stages into `.deploy/animated/` so the live URL is clean `/animated/` (no `/dist/` suffix)
- `.deploy/.nojekyll` disables Jekyll
- Only deployable files staged — `node_modules`, source TS, configs are excluded
- Action: `actions/deploy-pages@v4` with `id-token: write` and `pages: write` perms

**Local dev**:
```bash
cd site/animated && npm run dev    # Vite dev server, port 5173
cd site/animated && npm run build  # outputs to dist/
```

**Verify** (simulated locally):
```
GET /                              -> 200 (12206 B)
GET /animated/                     -> 200 (995 B)
GET /animated/index.html           -> 200 (995 B)
GET /animated/assets/index-*.js    -> 200 (454371 B)
GET /animated/assets/index-*.css   -> 200 (2574 B)
GET /style.css                     -> 200 (11253 B)
GET /script.js                     -> 200 (1311 B)
```

---

## Blocked Items

_(kosong — isi kalau ada website yang tidak bisa di-scrape)_
