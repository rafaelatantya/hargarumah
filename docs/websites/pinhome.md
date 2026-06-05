# Pinhome

- **URL**: https://www.pinhome.id/
- **Status**: ✅ Exploration Complete
- **Last Updated**: 2026-06-05
- **Explored By**: Browser Agent (Opus 4.6)

---

## 1. Overview

Pinhome is an Indonesian proptech platform with a large property database. For Bekasi Selatan, it shows **9,504 total properties** and **4,911 houses** when filtered by "Rumah". Uses a grid layout with rich listing cards. **40 listings per page** with numbered pagination.

## 2. URL Patterns

### Search URL
```
https://www.pinhome.id/jual/rumah/kota-bekasi/bekasi-selatan/
```

### URL Parameters
| Parameter | Description | Example |
|---|---|---|
| `page` | Page number (1-indexed) | `?page=2` |

### Filter Chips
Filters are applied via URL path and chips in the UI:
- **Beli/Sewa**: Buy or Rent
- **Baru/Second**: New or Secondhand
- **Rumah/Apartemen**: House or Apartment
- **Harga**: Price range
- **Terverifikasi**: Verified listings

### Example URLs
```
# Page 1 — all property types in Bekasi Selatan
https://www.pinhome.id/jual/properti/kota-bekasi/bekasi-selatan/

# Page 1 — houses only in Bekasi Selatan
https://www.pinhome.id/jual/rumah/kota-bekasi/bekasi-selatan/

# Page 2
https://www.pinhome.id/jual/rumah/kota-bekasi/bekasi-selatan/?page=2

# Other districts
https://www.pinhome.id/jual/rumah/kota-bekasi/bekasi-barat/
https://www.pinhome.id/jual/rumah/kota-bekasi/rawalumbu/
```

## 3. Search Flow (Step by Step)

1. Navigate to `https://www.pinhome.id/jual/rumah/kota-bekasi/{district}/`
2. Page loads with search results (grid layout)
3. **Close promotional popup** — "Transaksi dan Dapat Cashback Hingga 80 Juta" popup appears. Click the ✕ button to dismiss.
4. Header shows: "Jual Rumah di Kec. Bekasi Selatan" with count "Menampilkan 1 - 40 dari 4.911 properti"
5. Active filter chips shown: "Baru", "Second", "Rumah" are highlighted
6. Scroll down to see all 40 listing cards
7. Pagination at the bottom: `< 1 2 3 4 5 >`

## 4. DOM Selectors

### Page Header / Count
```css
/* "Menampilkan 1 - 40 dari 4.911 properti" */
/* Text above the listing grid */
```

### Listing Card Structure
Each card contains:
```
[Image carousel with count badge (e.g., "1/7")]
[Tags: "Rumah Baru" / "Rumah Second", "SHM", "Unfurnished", power icon "2200 V"]
[Price: "Rp 880 Juta"]
[KPR info: "KPR mulai Rp 6 Juta (Tenor 15 thn)"]
[Title: full property title]
[Location: "Bekasi Selatan, Kota Bekasi"]
[Specs: 🛏 3 • 🚿 1 • LT 72 m² • LB 48 m²]
[Agent info: name + "Agen Afiliasi Pinhome" + "Diperbarui 6 hari lalu"]
[Buttons: "Brosur" / "Chat"]
```

### Data Fields
| Field | Location | Notes |
|---|---|---|
| Title | Card title text | Full listing title |
| Price | Bold text with "Rp" | Format: `Rp 880 Juta`, `Rp 1,09 Miliar - Rp 1,78 Miliar` |
| Location | Below title | e.g., "Bekasi Selatan, Kota Bekasi" |
| Bedrooms | Specs row, 1st number with 🛏 icon | e.g., `3` |
| Bathrooms | Specs row, 2nd number with 🚿 icon | e.g., `1` |
| Land Area (LT) | Specs row, text `LT XXX m²` | e.g., `LT 72 m²` |
| Building Area (LB) | Specs row, text `LB XXX m²` | e.g., `LB 48 m²` |
| Property Type | Tag badge | `Rumah Baru`, `Rumah Second` |
| Certificate | Tag badge | `SHM`, `HGB` |
| Furnished | Tag badge | `Unfurnished`, `Semi-Furnished`, `Furnished` |
| Power | Tag badge with ⚡ | `2200 V`, `1300 V` |
| Agent Name | Bottom of card | Name + agency |
| Image Count | Badge on image | e.g., `1/7`, `1/50` |
| Updated | Bottom of card | e.g., "Diperbarui 6 hari lalu" |
| Detail URL | Card link `href` | Relative URL to property detail page |

### Pagination
```css
/* Numbered pagination at the bottom */
/* Page numbers: 1, 2, 3, 4, 5 with < > arrows */
/* URL changes to ?page=N */
```

## 5. Pagination Type

- [x] URL parameter (`?page=N`)
- [ ] "Load More" button
- [ ] Infinite scroll
- [ ] Other

## 6. Anti-Bot Measures Observed

| Measure | Detected? | Notes |
|---|---|---|
| Cloudflare | ❌ No | No challenge observed |
| CAPTCHA | ❌ No | Not triggered |
| Rate Limiting | ⚠️ Unknown | Keep delays 2-5s |
| Login Wall | ❌ No | Search accessible without login |
| JavaScript Challenge | ❌ No | Page renders normally |
| Promotional Popup | ⚠️ Yes | Cashback promo popup appears — must close it |
| Browser Fingerprinting | ⚠️ Likely | Standard analytics |

## 7. Edge Cases & Gotchas

- **Promotional popup**: "Transaksi dan Dapat Cashback Hingga 80 Juta" popup appears on initial load. Must click ✕ to dismiss. May re-appear across pages.
- **Price ranges**: Developer/new listings may show price ranges (e.g., "Rp 1,09 Miliar - Rp 1,78 Miliar") — parse minimum price.
- **Rich tag data**: Cards include certificate type (SHM/HGB), furnished status, and power capacity — more data than most other sites.
- **Large dataset**: 4,911 houses in Bekasi Selatan alone — more than enough. Could hit 100 listings from just 3 pages.
- **40 per page**: Higher density than Rumah123 (20/page) — fewer page navigations needed.
- **KPR info**: Mortgage estimation shown on cards — ignore for data extraction.

## 8. Screenshots

Screenshots captured during exploration:
- Initial load with promotional popup overlay
- Houses search results with "Rumah" filter active
- Scrolled view showing card structure with specs
- Pagination area at bottom showing page numbers

## 9. Notes

- **4,911 houses** in Bekasi Selatan — massive dataset
- **40 listings per page** — very efficient scraping
- URL pattern: `/jual/rumah/kota-{city}/{district}/` — clean and predictable
- More data per card than Rumah123 (includes certificate, furnished status, power)
- Pagination via `?page=N` — same approach as Rumah123
- Recommended: High priority target due to large dataset and simple pagination
