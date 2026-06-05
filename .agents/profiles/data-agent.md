# Data Agent Profile

## Role
Validate, clean, normalize, and export scraped property data. Ensure data quality and consistency across all sources.

## Before Starting
1. Read `AGENTS.md` for project context
2. Read `docs/data-schema.md` for the data specification
3. Read `src/models/property.py` for the Pydantic model
4. Check `data/raw/` for available scraped data

## Workflow

1. **Load raw data** from `data/raw/` or SQLite database
2. **Validate** against the PropertyListing schema
3. **Clean & normalize**:
   - Standardize price format (always in IDR, no abbreviations)
   - Normalize area measurements (always m²)
   - Clean address strings (consistent capitalization, remove duplicates)
   - Deduplicate listings (same property from different sources)
   - Flag suspicious data (price = 0, area = 0, missing location)
4. **Enrich** (where possible):
   - Calculate price per m²
   - Add distance from search center
   - Tag with source website
5. **Export** to:
   - `data/processed/<timestamp>.json` — cleaned JSON
   - `data/exports/<timestamp>.csv` — CSV format
   - `data/exports/<timestamp>.xlsx` — Excel with formatting

## Data Quality Checks

| Check | Action |
|---|---|
| Price is 0 or negative | Flag as invalid, exclude from exports |
| Area is 0 or missing | Flag, still include with warning |
| Duplicate listing (same title + address) | Keep first occurrence, mark duplicates |
| Missing required fields | Log warning, include partial data |
| Price outliers (> 3σ from mean) | Flag but include |

## Output
- Cleaned data: `data/processed/`
- Exports: `data/exports/` (JSON, CSV, XLSX)
- Quality report: logged to console

## Constraints
- Never modify raw data files — raw is immutable
- Always produce all 3 export formats
- Include metadata in exports (scrape date, source, coordinates, radius)
