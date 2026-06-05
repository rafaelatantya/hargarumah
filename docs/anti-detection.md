# Anti-Detection & Stealth Guide

## Why Stealth Matters

Indonesian property websites use various anti-bot measures:
- **Cloudflare** (rumah123, 99.co)
- **Rate limiting** (most sites)
- **JavaScript challenges** (OLX, Dekoruma)
- **Browser fingerprinting** (modern sites)

## Our Approach: nodriver (CDP)

We use **nodriver** instead of Selenium/Playwright because it communicates directly with Chrome via the **Chrome DevTools Protocol**, which means:

- ✅ No `navigator.webdriver = true` flag
- ✅ No chromedriver binary to detect
- ✅ No Selenium-specific DOM properties
- ✅ Real Chrome browser with real fingerprint
- ✅ Passes most JavaScript-based bot detection

## Stealth Configuration

### Browser Initialization

```python
import nodriver as uc

browser = await uc.start(
    headless=False,        # Headed mode is stealthier
    lang="id-ID",          # Match target locale
    sandbox=True,          # Keep sandbox enabled
)
```

### Why NOT Headless?

Headless mode is more easily detected by:
- `navigator.plugins` being empty
- `navigator.languages` differences
- WebGL renderer string differences
- Different `window.outerHeight` vs `window.innerHeight` ratios

**Recommendation**: Use headed mode for exploration, headless only for production batch runs after confirming it works.

## Human-Like Behavior

### Timing

| Action | Delay |
|---|---|
| Between page navigations | 2-5 seconds (random) |
| Before clicking an element | 0.5-1.5 seconds (random) |
| After page load (wait for content) | 1-3 seconds |
| Between scraping sessions | 30-120 seconds |
| Between different websites | 60-300 seconds |

### Scrolling

- Scroll gradually (not instant jump to bottom)
- Random scroll amounts (300-700 pixels)
- Pause at random points while scrolling
- Some pages load content on scroll (infinite scroll)

### Mouse Movement

- nodriver handles realistic mouse events internally via CDP
- Still add small random delays before interactions

## Rate Limiting Rules

| Website | Max Requests/min | Notes |
|---|---|---|
| Rumah123 | 10 | Cloudflare protected |
| PasHouses | 15 | Lighter protection |
| OLX | 8 | Aggressive rate limiting |
| Dekoruma | 12 | Moderate |
| Pinhome | 12 | Moderate |
| CariProperti | 15 | Lighter |
| 99.co | 10 | Cloudflare protected |
| EasyFind | 15 | Lighter |

> These are conservative estimates. Adjust based on actual behavior observed during exploration.

## Free Proxy Rotation (Optional)

When `USE_FREE_PROXY=true` in `.env`, the system fetches free proxies from public proxy lists. This provides IP diversity but comes with tradeoffs:

### Pros
- IP rotation reduces risk of IP-based blocking
- Free — no subscription needed

### Cons
- Free proxies are slow and unreliable
- Many are already blacklisted
- May introduce connection failures

### Implementation

```python
# src/utils/proxy.py handles:
# 1. Fetch free proxy list from public APIs
# 2. Validate proxies (check if alive + not blocked)
# 3. Rotate per-request or per-session
# 4. Fallback to direct connection on proxy failure
```

### Free Proxy Sources
- `https://api.proxyscrape.com/v2/` — HTTP/SOCKS proxies
- `https://www.proxy-list.download/api/v1/get` — Various protocols
- Fallback: direct connection with extended delays

## Session Management

1. **Rotate sessions**: Don't use the same browser session for too many requests
2. **Clear cookies periodically**: Prevents session-based fingerprinting
3. **New browser instance**: Create fresh browser after every 50-100 pages
4. **User-agent consistency**: Keep the same UA within a session (don't rotate mid-session)

## If You Get Blocked

1. **CAPTCHA**: Log it, skip the page, try again later with a different session
2. **403/429**: Back off exponentially (1min → 2min → 5min → 10min)
3. **IP block**: Switch proxy or wait 30+ minutes
4. **JavaScript challenge**: Usually passes with nodriver; if not, log and report
5. **Login wall**: Document it as a blocker in the website doc

## Configuration

All timing and rate limiting values are in `config/default.yaml` and `config/browser_profiles.yaml`.
Per-site overrides are in `config/targets.yaml`.
