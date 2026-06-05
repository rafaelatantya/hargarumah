# EasyFind Scraper Guide (easyfind.id)

## Website Overview
- **Domain**: `easyfind.id`
- **Status**: ✅ Exploration Complete
- **Last Updated**: 2026-06-05
- **Explored By**: Browser Agent (Gemini 3.1 Pro)

## Search and Navigation Flow
EasyFind provides a search page with query parameters for filtering.

### 1. URL Patterns
- **Base Search URL**: `https://www.easyfind.id/properties`
- **Search Parameters**:
  - `query`: Text search (e.g. `Rumah Bekasi`)
  - `city`: City filter (e.g. `Kota Bekasi`)
  - `page`: Pagination (e.g. `3`)
- **Example URL**: `https://www.easyfind.id/properties?query=Rumah+Bekasi&city=Kota+Bekasi&page=1`
- **Note**: The site might not have a strict "Bekasi Selatan" district filter out of the box in the URL structure. It's safer to query `city=Kota Bekasi` with a keyword like `Bekasi Selatan` and parse the results.

### 2. Pagination
- **Mechanism**: Standard URL query parameter `&page=N`.
- **Items Per Page**: 18 listings are shown per page.
- **Total Count**: There is NO explicit "Total Listings" counter string on the page. The scraper must iterate through pages until no more items are found or a 404 is hit.

---

## Key CSS Selectors

| Element | Selector | Description |
| --- | --- | --- |
| **Listing Card Wrapper** | `a[href^="/properties/"]` | The clickable anchor tag that wraps the entire listing card. |
| **Title** | `h3` inside the card wrapper | The title of the property. |
| **Price** | `div` containing `Juta` or `Milyar` inside the card wrapper | The price string (e.g., `1.8 Milyar`). |
| **Location** | `figure` inside the card wrapper | Address or location text. |

---

## Extraction logic
1. Use `nodriver` to navigate to `https://www.easyfind.id/properties?query=Rumah+Bekasi+Selatan&city=Kota+Bekasi`.
2. Extract data from all `a[href^="/properties/"]` elements.
3. Find the Title inside the `h3` of the card.
4. Find the Price by looking for text nodes containing `Juta` or `Milyar`.
5. Find Location from the `figure` tag inside the card.
6. Increment the `page` query parameter by 1 and navigate to the next page.
7. Stop when no `a[href^="/properties/"]` cards are found on the loaded page.

---

## Anti-Detection & Bot Protection
- No Cloudflare, Captchas, or Popups detected.
- Page loads cleanly. Standard 2-5s delay between page navigation is recommended to avoid rate limits.
