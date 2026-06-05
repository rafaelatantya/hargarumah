# OLX Indonesia

- **URL**: https://www.olx.co.id/
- **Status**: ✅ Exploration Complete
- **Last Updated**: 2026-06-05
- **Explored By**: Browser Agent (Opus 4.6)

---

## 1. Overview

OLX Indonesia is a general marketplace with a large property section. Unlike dedicated property portals, OLX uses location codes and category IDs in URLs. Listings are user-generated (not curated). Pagination uses "Load More" button instead of page numbers.

## 2. URL Patterns

### Search URL
```
https://www.olx.co.id/{location-slug}_g{location-id}/dijual-rumah-apartemen_c5158?filter=type_eq_rumah
```

### URL Components
| Component | Description | Example |
|---|---|---|
| `{location-slug}` | Area name (kebab-case) | `bekasi-selatan` |
| `_g{location-id}` | OLX location ID | `_g5001297` |
| `dijual-rumah-apartemen_c5158` | Category: Rumah & Apartemen for sale | Fixed slug |
| `filter=type_eq_rumah` | Filter for houses only | Query param |

### Known Location IDs
| Area | Slug | ID |
|---|---|---|
| Bekasi Selatan | `bekasi-selatan` | `g5001297` |
| Bekasi Kota | `bekasi-kota` | `g4000020` |
| Bandung Kota | `bandung-kota` | `g4000018` |

### Example URLs
```
# Houses in Bekasi Selatan
https://www.olx.co.id/bekasi-selatan_g5001297/dijual-rumah-apartemen_c5158?filter=type_eq_rumah

# All property in Bekasi Kota (broader)
https://www.olx.co.id/bekasi-kota_g4000020/properti_c88

# Houses in Bekasi Kota
https://www.olx.co.id/bekasi-kota_g4000020/dijual-rumah-apartemen_c5158?filter=type_eq_rumah
```

## 3. Search Flow (Step by Step)

### Option A: Direct URL (recommended for scraper)
1. Navigate to the constructed URL directly
2. Page loads with search results
3. Scroll down to see all initial listings
4. Click "muat lainnya" (Load More) button to load additional listings
5. Repeat until button disappears or enough listings collected

### Option B: Location Resolution (for unknown areas)
1. Navigate to OLX homepage
2. Click location search input: `input[placeholder="Cari kota, area, atau lokalitas"]`
3. Type the area name (e.g., "Bekasi Selatan")
4. Wait for autocomplete suggestions in `div._34q3t`
5. Click the matching suggestion
6. Page navigates to the location-specific URL
7. Note the URL's `_gXXXXXXX` portion for future use

## 4. DOM Selectors

### Listing Container
```css
/* Grid of listing cards */
/* Cards are wrapped in anchor tags */
```

### Individual Listing Card
```css
/* Card link — the main clickable element */
a._2cbZ2
```

### Data Fields (from search card)
| Field | Location | Notes |
|---|---|---|
| Title | Card text | Descriptive title, e.g., "Dijual Rumah 2 Lantai Rapi Siap Huni..." |
| Price | Text starting with `Rp` | Format: `Rp 1.500.000.000` (dot-separated, full number) |
| Specs | Text pattern: `X KT - X KM - X m2` | KT=bedrooms, KM=bathrooms, m2=building area |
| Location | Below title/specs | e.g., "Rawalumbu, Bekasi Kota" |
| Post Date | Small text | e.g., "Hari ini", "Kemarin", "17 Mei" |
| Detail URL | `a._2cbZ2` → `href` | Pattern: `/item/{slug}-iid-{item_id}` |
| Image | Card image element | Primary image only in search card |

### Data Fields (from detail page)
| Field | Selector | Notes |
|---|---|---|
| Tipe | Key-value under "Detail" | `Rumah` or `Apartemen` |
| Luas bangunan | Key-value under "Detail" | Building area in m² |
| Luas tanah | Key-value under "Detail" | Land area in m² |
| Kamar tidur | Key-value under "Detail" | Bedrooms |
| Kamar Mandi | Key-value under "Detail" | Bathrooms |
| Sertifikasi | Key-value under "Detail" | e.g., `SHM`, `HGB` |
| Alamat lokasi | Key-value under "Detail" | Full address |

### Pagination (Load More)
```css
/* "muat lainnya" button */
button span:contains("muat lainnya")
```

## 5. Pagination Type

- [ ] URL parameter
- [x] "Load More" button (`muat lainnya`)
- [ ] Infinite scroll
- [ ] Other

### Load More Strategy
1. Scroll to bottom of current listings
2. Find and click the "muat lainnya" button
3. Wait 2-3 seconds for React state update and rendering
4. New listings append to existing list
5. Repeat until button disappears (listings exhausted) or target count reached

## 6. Anti-Bot Measures Observed

| Measure | Detected? | Notes |
|---|---|---|
| Cloudflare | ❌ No | No Cloudflare challenge observed |
| CAPTCHA | ❌ No | Not triggered during exploration |
| Rate Limiting | ⚠️ Unknown | Keep delays between interactions |
| Login Wall | ❌ No | Search results accessible without login |
| JavaScript Challenge | ❌ No | Page renders normally |
| Notification Popup | ⚠️ Yes | "Aktifkan notifikasi" popup may appear — click "Tidak Dulu" |
| Browser Fingerprinting | ⚠️ Likely | Standard analytics present |

## 7. Edge Cases & Gotchas

- **Location ID required**: Unlike Rumah123, OLX requires a location code (`_gXXXXXXX`) in the URL. These must be pre-mapped or resolved via autocomplete interaction.
- **Notification popup**: A "Aktifkan notifikasi" (Enable notifications) popup may appear on any page. Must click "Tidak Dulu" (Not Now) to dismiss.
- **Price format different from Rumah123**: OLX uses full dot-separated numbers (e.g., `Rp 1.500.000.000`) instead of abbreviations like "1,5 Miliar".
- **Load More pagination**: No URL-based pagination. Must interact with the DOM "muat lainnya" button.
- **Spec format**: Listings show specs as `3 KT - 2 KM - 100 m2` on search cards. Land area (`Luas tanah`) is only available on detail pages.
- **Lazy-loaded sidebar**: Filter inputs and sidebar elements are lazy-loaded based on scroll position.

## 8. Screenshots

Screenshots captured during exploration:
- OLX search page for Bekasi Kota properti
- Scrolled views showing listing cards
- Load More button interaction
- "Dijual Rumah & Apartemen" sub-category
- Location autocomplete interaction
- Listing detail page with key-value specs

## 9. Notes

- **Scraper strategy**: For search results, extract title, price, specs preview (KT, KM, m2) from cards. For full details (land area, certificate), navigate to each detail page.
- **Two-pass approach recommended**: First pass = collect listing URLs from search. Second pass = visit each detail page for full data.
- OLX prices are in full IDR format (no "Juta"/"Miliar" abbreviations in search cards).
- Location IDs can be dynamically resolved by typing in the search box and reading autocomplete suggestions.
