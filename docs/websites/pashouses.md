# Pashouses Scraper Guide (pashouses.id)

## Website Overview
- **Domain**: `pashouses.id`
- **Target Area**: Indonesia real estate (strictly Jabodetabek: Jakarta, Tangerang, Tangerang Selatan, Bekasi, Bogor, Depok).
- **Listing Type**: Sale only (Rumah/Apartemen Dijual).
- **Status**: ✅ Exploration Complete
- **Last Updated**: 2026-06-05
- **Explored By**: Browser Agent (Gemini 3.1 Pro)

## Search and Navigation Flow
Pashouses supports two primary navigation flows:

### 1. Static Area Slugs (Preferred)
The website has a clean hierarchical path structure for regions, cities, and districts.
- **Base URL**: `https://pashouses.id/rumah-dijual/area`
- **City Level**: `https://pashouses.id/rumah-dijual/area/<city-slug>`
  - Examples: `/area/bekasi`, `/area/jakarta`, `/area/kabupaten-bekasi`
- **District Level**: `https://pashouses.id/rumah-dijual/area/<city-slug>/<district-slug>`
  - Examples: `/area/bekasi/bekasi-selatan`, `/area/kabupaten-bekasi/cikarang-selatan`
- **Pagination**:
  - Page 1: `https://pashouses.id/rumah-dijual/area/<city-slug>/<district-slug>`
  - Page 2+: `https://pashouses.id/rumah-dijual/area/<city-slug>/<district-slug>/<page_number>`
  - Examples: `/area/bekasi/bekasi-selatan/2`, `/area/bekasi/bekasi-selatan/3`
  - 20 listings per page.

### 2. Keyword Search (Fallback)
If the district/city cannot be cleanly mapped to a static slug, use the keyword search:
- **Search URL**: `https://pashouses.id/rumah-dijual/area?keyword=<district>+<city>`
- **Behavior**: This page displays filtered listings but might use dynamic client-side pagination or infinite scroll (scrolling down triggers load).

---

## Key CSS Selectors

| Element | Selector | Description |
| --- | --- | --- |
| **Card Container** | `div.flex.flex-col` (under listing section) | The parent container holding all listing cards. |
| **Listing Card** | `a[href^="/rumah/"]` | Each individual listing card is an anchor link pointing to `/rumah/...`. |
| **URL / Link** | Attribute `href` of the card | Points to the detail page (e.g., `/rumah/perumahan-taman-cikas-blok-c9-no-20`). |
| **Title** | `h2` | Inside the card, contains the property name. |
| **Price** | `span` containing `Rp` | The first span element inside the card matching `Rp` price format. |
| **Location** | `p` immediately after `h2` | Text format: `<District>, <City>` (e.g., `Bekasi Selatan, Kota Bekasi`). |
| **Land Area (LT)** | `p` containing `LT` | Text format: `LT\n<value>\nm²`. |
| **Building Area (LB)** | `p` containing `LB` | Text format: `LB\n<value>\nm²`. |
| **Bathrooms (KM)** | `p` containing `KM` | Text format: `KM\n<value>`. |
| **Bedrooms (KT)** | `p` containing `KT` | Text format: `KT\n<value>`. |
| **Pagination Buttons**| `a[href*="/area/"]` at the bottom | Standard page links at the bottom (only on paginated views). |

---

## Extraction logic
For each card found via `a[href^="/rumah/"]`:
1. **Title**: Extract the text of the `h2` tag.
2. **Price**: Find the inner text of the `span` containing `Rp` and clean it (remove `Rp` and dots) to get an integer.
3. **URL**: Prepend `https://pashouses.id` to the `href` attribute.
4. **Location**: Extract the text of the `p` tag below `h2`. Split by `,` to get District and City.
5. **Specs**:
   - Loop through `p` tags in the specs section.
   - Match `LT` to get Land Area.
   - Match `LB` to get Building Area.
   - Match `KM` to get Bathrooms.
   - Match `KT` to get Bedrooms.

---

## Anti-Detection & Bot Protection
- No severe bot detection (like Cloudflare or CAPTCHA) was encountered during exploration.
- **Recommendations**:
  - Use `nodriver` as required by the project.
  - Implement a random delay of 2-5 seconds between navigating pages.
  - Mimic human scrolling when navigating to trigger any lazy loading if fallback keyword search is used.
