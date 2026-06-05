# Dekoruma

- **URL**: https://www.dekoruma.com/properti
- **Status**: ✅ Exploration Complete
- **Last Updated**: 2026-06-05
- **Explored By**: Browser Agent (Opus 4.6)

---

## 1. Overview

Dekoruma is an Indonesian interior design and property platform. The property section (`/properti`) has a search interface with location-based filtering. For Bekasi Selatan, it shows **3,997 properties**. Cards show price in abbreviated format (e.g., "Rp3M"), with property type tags, specs, and agent info.

## 2. URL Patterns

### Search URL
```
https://www.dekoruma.com/properti/dijual/{city}/{district}
```

### Search Flow URL Construction
The search starts at `/properti`, then after searching for a location, navigates to:
```
https://www.dekoruma.com/properti/dijual/bekasi/bekasi-selatan
```

### Breadcrumb
```
Properti > Dijual > Bekasi > Bekasi Selatan
```

### URL Parameters
| Parameter | Description | Example |
|---|---|---|
| TBD | Pagination — needs further exploration | |

### Example URLs
```
# Bekasi Selatan - all property types
https://www.dekoruma.com/properti/dijual/bekasi/bekasi-selatan

# Other districts (predicted pattern)
https://www.dekoruma.com/properti/dijual/bekasi/bekasi-barat
https://www.dekoruma.com/properti/dijual/bekasi/rawalumbu
```

## 3. Search Flow (Step by Step)

### Option A: Direct URL
1. Navigate to `https://www.dekoruma.com/properti/dijual/bekasi/bekasi-selatan`
2. Page loads with search results directly

### Option B: Via Search Form
1. Navigate to `https://www.dekoruma.com/properti`
2. Landing page shows hero section + search form
3. Form has tabs: "Dijual" / "Disewa"
4. Search input: `input[placeholder="Mau cari properti dimana?"]`
5. Type "Bekasi Selatan"
6. Select from autocomplete dropdown
7. Filter dropdowns: "Semua Properti", "Semua Status", "Semua Harga"
8. Click "Cari Properti" button
9. Redirects to search results page

## 4. DOM Selectors

### Page Header / Count
```css
/* "Properti Dijual di Bekasi Selatan" */
/* "3997 properti ditemukan:" */
```

### Listing Card Structure
Each card in a 2-column grid:
```
[Image with "NEW" badge (yellow circle)]
[Property type tag: "Rumah" / "Ruko"]
[Title: property name/description]
[Location: "Bekasi Selatan, Bekasi"]
[Price: "Rp3M", "Rp2,3M"]
[Specs row 1: 🛏 6  🚿 6  🚗 4]
[Specs row 2: LT 200m²  LB 330m²]
[Agent: avatar + "2 hari lalu" + "Yane Li • Century 21"]
```

### Data Fields
| Field | Location | Notes |
|---|---|---|
| Title | Card title text | Property description |
| Price | Bold text | Format: `Rp3M`, `Rp2,3M`, `Rp850Jt` — abbreviated |
| Location | Below title | e.g., "Bekasi Selatan, Bekasi" |
| Property Type | Tag badge | `Rumah`, `Ruko`, etc. |
| Bedrooms | Specs row, bed icon | Number e.g., `6` |
| Bathrooms | Specs row, bath icon | Number e.g., `6` |
| Garage/Cars | Specs row, car icon | Number e.g., `4` |
| Land Area (LT) | Specs row, `LT XXXm²` | e.g., `LT 200m²` |
| Building Area (LB) | Specs row, `LB XXXm²` | e.g., `LB 330m²` |
| Agent Name | Bottom of card | Name + agency |
| Updated | Bottom of card | e.g., "2 hari lalu" |
| Image | Card image | With "NEW" badge overlay |
| Detail URL | Card link | Points to individual listing page |

## 5. Pagination Type

- [ ] URL parameter — needs confirmation
- [ ] "Load More" button — needs confirmation
- [ ] Infinite scroll — needs confirmation
- [x] **Needs further exploration** — agent quota ran out before pagination could be tested

## 6. Anti-Bot Measures Observed

| Measure | Detected? | Notes |
|---|---|---|
| Cloudflare | ❌ No | No challenge observed |
| CAPTCHA | ❌ No | Not triggered |
| Rate Limiting | ⚠️ Unknown | Keep delays 2-5s |
| Login Wall | ❌ No | Search accessible without login |
| JavaScript Challenge | ❌ No | Page renders normally |
| Browser Fingerprinting | ⚠️ Likely | Standard analytics |

## 7. Edge Cases & Gotchas

- **Price format**: Uses abbreviated format WITHOUT spaces — `Rp3M` instead of `Rp 3 M`. Also uses `Rp2,3M` with comma. The price parser needs to handle this format.
- **"M" abbreviation**: `M` = Miliar (billion IDR), different from some sites that use "M" for Juta.
- **Garage/car count**: Unlike most other sites, Dekoruma shows car spaces (🚗) in addition to bedrooms/bathrooms.
- **NEW badge**: Many listings have a yellow "NEW" badge overlay on the image.
- **"Lihat Peta Sekitar"**: Map view option available — potential for coordinate-based filtering.
- **Pagination**: Not fully explored — needs follow-up to determine if it's URL param, load more, or infinite scroll.

## 8. Screenshots

Screenshots captured during exploration:
- Landing page with search form ("Mau cari properti dimana?")
- Search results for Bekasi Selatan (3,997 properties, 2-column grid)

## 9. Notes

- **3,997 properties** in Bekasi Selatan — large dataset
- Price format is unique: `Rp3M`, `Rp2,3M` — no spaces, comma decimal
- 2-column grid layout
- Clean URL pattern: `/properti/dijual/{city}/{district}`
- **TODO**: Pagination mechanism needs follow-up exploration (ran out of quota)
- Search starts at `/properti` → form submission → redirects to `/properti/dijual/{city}/{district}`
