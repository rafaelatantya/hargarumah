# Agent Orchestration Guide

## Overview

HargaRumah uses a multi-agent pattern where a **Planner** decomposes work into tasks for **Specialist** agents. This document defines how agents coordinate.

## Orchestration Flow

```
User Request
    │
    ▼
┌──────────┐
│ Planner  │ ← Reads AGENTS.md + docs/README.md
│ Agent    │ ← Decomposes task into sub-tasks
└────┬─────┘
     │ spawns
     ├───────────────┬──────────────────┐
     ▼               ▼                  ▼
┌──────────┐  ┌──────────┐     ┌──────────┐
│ Explorer │  │ Scraper  │     │  Data    │
│ Agent    │  │ Agent    │     │  Agent   │
└──────────┘  └──────────┘     └──────────┘
     │               │                │
     ▼               ▼                ▼
  docs/websites/  src/scrapers/   data/processed/
  (interaction    (implementation) (validated data)
   steps docs)
```

## Agent Profiles

### Explorer Agent (`.agents/profiles/explorer-agent.md`)
- **Purpose**: Manually browse target websites, document how search/listing pages work
- **Input**: Target website name + coordinates
- **Output**: Updated `docs/websites/<site>.md` with step-by-step interaction guide
- **Tools**: Browser subagent for real navigation

### Scraper Agent (`.agents/profiles/scraper-agent.md`)
- **Purpose**: Implement scraper code based on documented exploration steps
- **Input**: Completed `docs/websites/<site>.md`
- **Output**: New module in `src/scrapers/<site>.py`
- **Prerequisite**: Explorer must have documented the site first

### Data Agent (`.agents/profiles/data-agent.md`)
- **Purpose**: Validate scraped data, normalize formats, handle edge cases
- **Input**: Raw scraped data in `data/raw/`
- **Output**: Cleaned data in `data/processed/`, exports in `data/exports/`
- **Tools**: Python data processing

## Coordination Rules

1. **Sequential dependency**: Explorer → Scraper → Data (for each website)
2. **Parallel by site**: Different websites can be explored/scraped in parallel
3. **Documentation first**: No scraper code without completed website docs
4. **Single responsibility**: Each agent handles ONE website at a time
5. **Error reporting**: If a site is blocked or changed, agent updates the website doc with findings

## Task Decomposition Template

When planning a scraping session:

```markdown
## Session: [date] - [location description]

### Coordinates: lat, lng | Radius: X km

#### Website Tasks:
1. [ ] Explore rumah123.com → docs/websites/rumah123.md
2. [ ] Implement rumah123 scraper → src/scrapers/rumah123.py
3. [ ] Explore olx.co.id → docs/websites/olx.md
4. [ ] Implement olx scraper → src/scrapers/olx.py
... (repeat for each site)

#### Data Tasks:
5. [ ] Validate all raw data → data/processed/
6. [ ] Export to JSON + CSV + XLSX → data/exports/
```

## Communication Between Agents

Agents communicate through **files**, not messages:
- Explorer writes to `docs/websites/<site>.md`
- Scraper reads from `docs/websites/<site>.md`, writes to `src/scrapers/<site>.py`
- Data Agent reads from `data/raw/`, writes to `data/processed/` and `data/exports/`
- All agents can update `AGENTS.md` section "Current Status" to report progress
