# Website Scraping Documentation Template

> Copy this file to `<site-name>.md` and fill in each section during exploration.

## Site: [Website Name]

- **URL**: [base URL]
- **Status**: 🔲 Not Explored / 🔨 In Progress / ✅ Complete / ❌ Blocked
- **Last Updated**: [date]
- **Explored By**: [agent/human]

---

## 1. Overview

Brief description of the website, what type of listings it has, and any notable features.

## 2. URL Patterns

### Search URL
```
[Full URL pattern with parameters]
```

### URL Parameters
| Parameter | Description | Example |
|---|---|---|
| | | |

### Example URLs
```
[Real example URLs for Bekasi Selatan searches]
```

## 3. Search Flow (Step by Step)

1. Navigate to [URL]
2. [What to click/type to start a search]
3. [How to set location filter]
4. [How to set property type filter]
5. [How results are displayed]
6. [How pagination works]

## 4. DOM Selectors

### Listing Container
```css
[CSS selector for the listings container]
```

### Individual Listing Card
```css
[CSS selector for each listing card]
```

### Data Fields
| Field | Selector | Notes |
|---|---|---|
| Title | `[selector]` | |
| Price | `[selector]` | Format: [describe] |
| Location | `[selector]` | |
| Land Area | `[selector]` | |
| Building Area | `[selector]` | |
| Bedrooms | `[selector]` | |
| Bathrooms | `[selector]` | |
| Image | `[selector]` | |
| Detail URL | `[selector]` | |

### Pagination
```css
[CSS selector for next page / load more button]
```

## 5. Pagination Type

- [ ] URL parameter (`?page=2`)
- [ ] "Load More" button
- [ ] Infinite scroll
- [ ] Other: [describe]

## 6. Anti-Bot Measures Observed

| Measure | Detected? | Notes |
|---|---|---|
| Cloudflare | | |
| CAPTCHA | | |
| Rate Limiting | | |
| Login Wall | | |
| JavaScript Challenge | | |
| Browser Fingerprinting | | |

## 7. Edge Cases & Gotchas

- [Any quirks, inconsistencies, or special handling needed]

## 8. Screenshots

[Embed screenshots of key pages/states if available]

## 9. Notes

[Any additional observations]
