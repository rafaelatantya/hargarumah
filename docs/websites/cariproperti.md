# CariProperti Scraper Guide (cariproperti.com)

## Website Overview
- **Domain**: `cariproperti.com`
- **Status**: ✅ Exploration Complete
- **Last Updated**: 2026-06-05
- **Explored By**: Browser Agent (Gemini 3.1 Pro)

## Search and Navigation Flow
CariProperti uses a split-pane layout with a listing feed on the left and a map on the right.

### 1. URL Patterns
The site supports clean URL routing for Areas and Districts.
- **Area URL**: `https://cariproperti.com/<area-slug>` (e.g., `/bekasi`)
- **District URL**: `https://cariproperti.com/<area-slug>/<district-slug>` (e.g., `/bekasi/bekasi-barat`, `/bekasi/bekasi-utara`)
- **Note**: Searching directly for "Bekasi Selatan" did not return a specific district page. It's recommended to query `https://cariproperti.com/bekasi` directly and filter results down post-scraping if strict Bekasi Selatan limits are needed, or try targeting specific available districts.

### 2. Filtering
- **Property Type**: There is a "Residential" filter to exclude Ruko/Apartments. However, clicking this filter does NOT change the URL query parameters. It's a client-side filter.
- **Scraping Strategy**: To only get houses, we must either:
  1. Have the `nodriver` agent click the `Residential` filter button (`button` containing text "Residential").
  2. Scrape all properties and rely on our Pydantic validation and post-processing to filter them out based on titles or tags.

### 3. Pagination (Infinite Scroll)
- CariProperti does **NOT** use traditional page numbers (`?page=2`) or a "Load More" button.
- It uses **Infinite Scroll**.
- **Mechanism**: The left pane containing the listing cards must be scrolled down to trigger lazy loading of new elements.
- **Total Count**: Shown at the top left of the list (e.g., `183 Properti dari Cariproperti ditemukan`).

---

## Key CSS Selectors

| Element | Selector | Description |
| --- | --- | --- |
| **Listing Card Wrapper** | `a.new-map-card` | The main clickable card container. The `href` attribute leads to the detail page. |
| **Title** | Sibling `div` of `a.new-map-card` | The property name (e.g., `Dovia at Ladoria Grand Wisata`). |
| **Price** | Text containing `Rp` and `Milyar` / `Juta` | Usually shows ranges for new developments (e.g., `Rp 1.7 Milyar - Rp 3.1 Milyar`). |
| **Location** | Text below Title | District/City text (e.g., `Grand Wisata, Bekasi`). |
| **Bedrooms (KT)** | Text containing `KT` | Format: `X - Y KT` |
| **Building Area (LB)** | First specification tag | Format: `X - Y m²` |
| **Land Area (LT)** | Second specification tag | Format: `X - Y m²` |

---

## Extraction logic
1. Use `nodriver` to navigate to `https://cariproperti.com/bekasi`.
2. Find the total number of listings from the header text (e.g., `183 Properti`).
3. Scroll down repeatedly inside the listing pane.
4. Extract data from `a.new-map-card` elements and their siblings.
5. **Price Parsing**: Note that prices are often listed as ranges (`Rp 1.7 Milyar - Rp 3.1 Milyar`). The scraper should take the lowest price in the range.

---

## Anti-Detection & Bot Protection
- No Cloudflare or CAPTCHA detected during browser exploration.
- Standard delays (2-5s) and realistic scrolling patterns are required since infinite scroll depends on triggering scroll events in the DOM.
