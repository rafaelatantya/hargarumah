# Rumah123

- **URL**: https://www.rumah123.com/
- **Status**: ✅ Exploration Complete
- **Last Updated**: 2026-06-05
- **Explored By**: Browser Agent (Opus 4.6)

---

## 1. Overview

Rumah123.com is one of the largest property listing portals in Indonesia. Part of the REA Group (same parent as 99.co). Covers houses, apartments, land, and commercial properties. The search results page for Bekasi Selatan shows **711 properties** with **20 listings per page** (36 pages total).

## 2. URL Patterns

### Search URL (current implementation)
```
https://www.rumah123.com/jual/cari/?q={keyword}&type=rumah&page={page}
```

> **Note**: The scraper uses keyword search (`/jual/cari/?q=`) instead of the path-based pattern (`/jual/{city}/{district}/rumah/`). This is more reliable — works for any location without needing city/district hierarchy.

### URL Parameters
| Parameter | Description | Example |
|---|---|---|
| `q` | Search keyword (location name) | `?q=harjamukti` |
| `type` | Property type filter | `&type=rumah` |
| `page` | Page number (1-indexed) | `&page=2` |

### Pagination
- Type: **URL parameter** (`&page=N`)
- ~20 listings per page
- Next page button: `a[aria-label="Next page"]`

### Example URLs
```
# Keyword search — page 1
https://www.rumah123.com/jual/cari/?q=harjamukti&type=rumah

# Keyword search — page 2
https://www.rumah123.com/jual/cari/?q=harjamukti&type=rumah&page=2

# Path-based (legacy, still works)
https://www.rumah123.com/jual/bekasi/bekasi-selatan/rumah/
```

## 3. Search Flow (Step by Step)

1. Navigate to `https://www.rumah123.com/jual/cari/?q={keyword}&type=rumah`
2. Page loads with search results immediately — no interaction needed
3. Keyword in the `q` parameter (e.g., `harjamukti`, `bekasi selatan`)
4. Search bar shows "Bekasi Selatan, Bekasi, Jawa Barat" confirming location
5. Results show header: "Menampilkan 1-20 dari 711 properti"
6. Filter chips available: "Properti Baru", "Properti dengan video", "Harga", "Luas Tanah"
7. Keyword tags: "Dekat Akses Transportasi (442)", "Komplek Perumahan (353)"
8. Scroll down to see all 20 listings
9. Pagination bar at the bottom with page numbers and next arrow

## 4. DOM Selectors

### Page Header / Count
```css
/* Text: "Menampilkan 1-20 dari 711 properti" */
/* Located above the listing cards */
```

### Listing Container
```css
/* Cards are rendered in a vertical list layout */
/* Each card is wrapped in a div with intersection observer */
div.ui-organism-intersection__card-container
```

### Individual Listing Card
```css
/* Each card contains: image section + details section */
/* The main clickable link spans the entire card */
a[href^="/properti/"]
```

### Data Fields
| Field | Selector / Location | Notes |
|---|---|---|
| Title | `a[href^="/properti/"]` → text content or `title` attr | Full property title |
| Detail URL | `a[href^="/properti/"]` → `href` attr | Relative URL, prefix with base_url |
| Price | Text containing `Rp` before title | Format: `Rp 2,4 Miliar`, `Rp 920 Juta`, `Rp 900 Juta` |
| Location | Text below title | Format: `Bekasi Selatan, Bekasi` |
| Bedrooms | Specs section, 1st number | Format: `4`, `3`, or `4 + 2` (main + service) |
| Bathrooms | Specs section, 2nd number | Format: `3`, `1`, or `3 + 1` |
| Land Area (LT) | Specs section, text with `LT` | Format: `LT: 211 m²` or `LT\n: 211 m²` |
| Building Area (LB) | Specs section, text with `LB` | Format: `LB: 422 m²` or `LB\n: 422 m²` |
| Image | Card image section | Multiple images per listing (carousel) |
| Property Type | Badge/tag on card | e.g., `Rumah`, `Rumah, Ruko` |
| Tags | Badge/tag on card | e.g., `Bebas Banjir`, `Top Properti` |

### Pagination
```css
/* Pagination bar near bottom of page */
a[aria-label="Next page"]   /* Next page button */
```

## 5. Pagination Type

- [x] URL parameter (`?page=2`)
- [ ] "Load More" button
- [ ] Infinite scroll
- [ ] Other

## 6. Anti-Bot Measures Observed

| Measure | Detected? | Notes |
|---|---|---|
| Cloudflare | ⚠️ Known | Rumah123 uses Cloudflare but nodriver bypassed it in testing |
| CAPTCHA | ❌ No | Not triggered during exploration |
| Rate Limiting | ⚠️ Likely | Keep delays 2-5s between pages |
| Login Wall | ❌ No | Search results accessible without login |
| JavaScript Challenge | ❌ No | Page renders normally |
| Browser Fingerprinting | ⚠️ Likely | Standard web analytics present |

## 7. Edge Cases & Gotchas

- **Sponsored/Top Properti listings**: First few cards may be "Top Properti" or "Official Developer" promoted listings — these have a different card structure (developer carousel with multiple unit types). The scraper should handle or skip these.
- **Native ads**: Google DoubleClick ads are embedded between listing cards. Filter out elements with `href` containing `adclick` or external domains.
- **Price ranges**: Developer listings may show price ranges like "Rp 1,1 Miliar – 7,5 Miliar" instead of a single price.
- **KPR info**: Some cards show mortgage info ("Rp 4 Jutaan (Tenor 20 Tahun)") which should be ignored.
- **Image carousel**: Each listing has multiple images shown as a carousel with dots. The primary image is loaded first.
- **Lazy loading**: Cards use intersection observer for lazy loading images — need to scroll to trigger loading.

## 8. Screenshots

Screenshots captured during exploration:
- Search results page (page 1): Shows header with "711 properti", filter chips, first listings
- Pagination: Page numbers `1, 2, 3, ..., 36` with next arrow
- Page 2: Shows "Menampilkan 21-40 dari 711 properti"

## 9. Notes

- **711 listings** available in Bekasi Selatan alone — more than enough for the 100 minimum target
- URL structure is clean and predictable: `/jual/{city}/{district}/rumah/`
- No login required, no aggressive anti-bot blocking observed
- Recommended approach: Direct URL navigation with `?page=N`, extract card data from DOM
- Keep 2-5 second delays between page loads
- Consider extracting from multiple districts to cover the search radius
