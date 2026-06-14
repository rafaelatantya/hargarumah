# Graph Report - hargarumah  (2026-06-14)

## Corpus Check
- 54 files · ~335,447 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 1507 nodes · 2336 edges · 89 communities (69 shown, 20 thin omitted)
- Extraction: 98% EXTRACTED · 2% INFERRED · 0% AMBIGUOUS · INFERRED: 57 edges (avg confidence: 0.5)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `c60c3f1a`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- [[_COMMUNITY_Community 0|Community 0]]
- [[_COMMUNITY_Community 1|Community 1]]
- [[_COMMUNITY_Community 2|Community 2]]
- [[_COMMUNITY_Community 3|Community 3]]
- [[_COMMUNITY_Community 4|Community 4]]
- [[_COMMUNITY_Community 5|Community 5]]
- [[_COMMUNITY_Community 7|Community 7]]
- [[_COMMUNITY_Community 8|Community 8]]
- [[_COMMUNITY_Community 9|Community 9]]
- [[_COMMUNITY_Community 10|Community 10]]
- [[_COMMUNITY_Community 11|Community 11]]
- [[_COMMUNITY_Community 12|Community 12]]
- [[_COMMUNITY_Community 13|Community 13]]
- [[_COMMUNITY_Community 14|Community 14]]
- [[_COMMUNITY_Community 15|Community 15]]
- [[_COMMUNITY_Community 16|Community 16]]
- [[_COMMUNITY_Community 17|Community 17]]
- [[_COMMUNITY_Community 18|Community 18]]
- [[_COMMUNITY_Community 19|Community 19]]
- [[_COMMUNITY_Community 20|Community 20]]
- [[_COMMUNITY_Community 21|Community 21]]
- [[_COMMUNITY_Community 22|Community 22]]
- [[_COMMUNITY_Community 23|Community 23]]
- [[_COMMUNITY_Community 24|Community 24]]
- [[_COMMUNITY_Community 25|Community 25]]
- [[_COMMUNITY_Community 26|Community 26]]
- [[_COMMUNITY_Community 27|Community 27]]
- [[_COMMUNITY_Community 28|Community 28]]
- [[_COMMUNITY_Community 29|Community 29]]
- [[_COMMUNITY_Community 30|Community 30]]
- [[_COMMUNITY_Community 31|Community 31]]
- [[_COMMUNITY_Community 32|Community 32]]
- [[_COMMUNITY_Community 33|Community 33]]
- [[_COMMUNITY_Community 34|Community 34]]
- [[_COMMUNITY_Community 35|Community 35]]
- [[_COMMUNITY_Community 36|Community 36]]
- [[_COMMUNITY_Community 37|Community 37]]
- [[_COMMUNITY_Community 38|Community 38]]
- [[_COMMUNITY_Community 39|Community 39]]
- [[_COMMUNITY_Community 40|Community 40]]
- [[_COMMUNITY_Community 41|Community 41]]
- [[_COMMUNITY_Community 42|Community 42]]
- [[_COMMUNITY_Community 43|Community 43]]
- [[_COMMUNITY_Community 44|Community 44]]
- [[_COMMUNITY_Community 45|Community 45]]
- [[_COMMUNITY_Community 46|Community 46]]
- [[_COMMUNITY_Community 47|Community 47]]
- [[_COMMUNITY_Community 48|Community 48]]
- [[_COMMUNITY_Community 49|Community 49]]
- [[_COMMUNITY_Community 50|Community 50]]
- [[_COMMUNITY_Community 51|Community 51]]
- [[_COMMUNITY_Community 52|Community 52]]
- [[_COMMUNITY_Community 53|Community 53]]
- [[_COMMUNITY_Community 54|Community 54]]
- [[_COMMUNITY_Community 55|Community 55]]
- [[_COMMUNITY_Community 56|Community 56]]
- [[_COMMUNITY_Community 57|Community 57]]
- [[_COMMUNITY_Community 58|Community 58]]
- [[_COMMUNITY_Community 59|Community 59]]
- [[_COMMUNITY_Community 60|Community 60]]
- [[_COMMUNITY_Community 61|Community 61]]
- [[_COMMUNITY_Community 62|Community 62]]
- [[_COMMUNITY_Community 63|Community 63]]
- [[_COMMUNITY_Community 64|Community 64]]
- [[_COMMUNITY_Community 65|Community 65]]
- [[_COMMUNITY_Community 66|Community 66]]
- [[_COMMUNITY_Community 67|Community 67]]
- [[_COMMUNITY_Community 68|Community 68]]
- [[_COMMUNITY_Community 69|Community 69]]
- [[_COMMUNITY_Community 70|Community 70]]
- [[_COMMUNITY_Community 71|Community 71]]
- [[_COMMUNITY_Community 72|Community 72]]
- [[_COMMUNITY_Community 73|Community 73]]
- [[_COMMUNITY_Community 74|Community 74]]
- [[_COMMUNITY_Community 75|Community 75]]
- [[_COMMUNITY_Community 76|Community 76]]
- [[_COMMUNITY_Community 77|Community 77]]
- [[_COMMUNITY_Community 78|Community 78]]
- [[_COMMUNITY_Community 79|Community 79]]
- [[_COMMUNITY_Community 80|Community 80]]
- [[_COMMUNITY_Community 81|Community 81]]
- [[_COMMUNITY_Community 82|Community 82]]
- [[_COMMUNITY_Community 83|Community 83]]
- [[_COMMUNITY_Community 84|Community 84]]
- [[_COMMUNITY_Community 85|Community 85]]
- [[_COMMUNITY_Community 86|Community 86]]

## God Nodes (most connected - your core abstractions)
1. `normalizeParams()` - 59 edges
2. `PropertyListing` - 48 edges
3. `create()` - 44 edges
4. `get()` - 42 edges
5. `BaseScraper` - 42 edges
6. `toString()` - 40 edges
7. `parse()` - 35 edges
8. `_addCheck()` - 33 edges
9. `returnCannedResponse()` - 29 edges
10. `start()` - 21 edges

## Surprising Connections (you probably didn't know these)
- `Path` --uses--> `PropertyListing`  [INFERRED]
  src/storage/database.py → src/models/property.py
- `run_scrapers()` --calls--> `Rumah123Scraper`  [EXTRACTED]
  main.py → src/scrapers/rumah123.py
- `BaseScraper` --uses--> `BrowserManager`  [INFERRED]
  src/core/base_scraper.py → src/core/browser.py
- `BaseScraper` --uses--> `PropertyListing`  [INFERRED]
  src/core/base_scraper.py → src/models/property.py
- `CariPropertiScraper` --uses--> `BaseScraper`  [INFERRED]
  src/scrapers/cariproperti.py → src/core/base_scraper.py

## Import Cycles
- None detected.

## Communities (89 total, 20 thin omitted)

### Community 0 - "Community 0"
Cohesion: 0.09
Nodes (22): 1. Overview, 2. URL Patterns, 3. Search Flow (Step by Step), 4. DOM Selectors, 5. Pagination Type, 6. Anti-Bot Measures Observed, 7. Edge Cases & Gotchas, 8. Screenshots (+14 more)

### Community 1 - "Community 1"
Cohesion: 0.10
Nodes (14): ProxyInfo, ProxyPool, Free proxy fetcher and rotator.  Fetches free proxies from public APIs, validate, Get the next proxy URL from the pool (round-robin rotation).          Returns:, Get a random proxy URL from the pool.          Returns:             Proxy URL st, Report that a proxy failed., Report that a proxy succeeded (resets failure count)., Check if the proxy pool should be refreshed. (+6 more)

### Community 2 - "Community 2"
Cohesion: 0.11
Nodes (11): Path, PropertyListing, Database, SQLite storage layer — async database operations for property listings., Save multiple listings to the database.          Args:             listings: Lis, Retrieve all listings from the database.          Args:             source: Opti, Count total listings in the database.          Args:             source: Optiona, Async SQLite database for storing scraped property listings.      Provides CRUD (+3 more)

### Community 3 - "Community 3"
Cohesion: 0.09
Nodes (21): 1. Overview, 2. URL Patterns, 3. Search Flow (Step by Step), 4. DOM Selectors, 5. Pagination Type, 6. Anti-Bot Measures Observed, 7. Edge Cases & Gotchas, 8. Screenshots (+13 more)

### Community 4 - "Community 4"
Cohesion: 0.10
Nodes (19): Anti-Detection & Stealth Guide, Browser Initialization, Configuration, Cons, Free Proxy Rotation (Optional), Free Proxy Sources, Human-Like Behavior, If You Get Blocked (+11 more)

### Community 5 - "Community 5"
Cohesion: 0.10
Nodes (19): 1. Overview, 2. URL Patterns, 3. Search Flow (Step by Step), 4. DOM Selectors, 5. Pagination Type, 6. Anti-Bot Measures Observed, 7. Edge Cases & Gotchas, 8. Screenshots (+11 more)

### Community 7 - "Community 7"
Cohesion: 0.11
Nodes (18): 1. Overview, 2. URL Patterns, 3. Search Flow (Step by Step), 4. DOM Selectors, 5. Pagination Type, 6. Anti-Bot Measures Observed, 7. Edge Cases & Gotchas, 8. Screenshots (+10 more)

### Community 8 - "Community 8"
Cohesion: 0.11
Nodes (18): 1. Overview, 2. URL Patterns, 3. Search Flow (Step by Step), 4. DOM Selectors, 5. Pagination Type, 6. Anti-Bot Measures Observed, 7. Edge Cases & Gotchas, 8. Screenshots (+10 more)

### Community 9 - "Community 9"
Cohesion: 0.11
Nodes (17): 1. Overview, 2. URL Patterns, 3. Search Flow (Step by Step), 4. DOM Selectors, 5. Pagination Type, 6. Anti-Bot Measures Observed, 7. Edge Cases & Gotchas, 8. Screenshots (+9 more)

### Community 10 - "Community 10"
Cohesion: 0.16
Nodes (16): BaseModel, BrowserSettings, GeoSettings, load_settings(), _load_yaml(), ProxySettings, Settings loader — combines YAML config files with .env overrides., Default geographic search parameters. (+8 more)

### Community 11 - "Community 11"
Cohesion: 0.06
Nodes (42): addIssueToContext(), assertNever(), datetimeRegex(), decideAdditionalProperties(), dirty(), floatSafeRemainder2(), G(), _getCached() (+34 more)

### Community 12 - "Community 12"
Cohesion: 0.24
Nodes (16): _build_metadata(), _ensure_dir(), export_all(), export_csv(), export_json(), export_xlsx(), _generate_filename(), Data exporter — exports property listings to JSON, CSV, and Excel formats. (+8 more)

### Community 13 - "Community 13"
Cohesion: 0.05
Nodes (39): _boolean(), boolean2(), _cidrv4(), _cidrv6(), _custom(), date2(), datetime2(), discriminatedUnion() (+31 more)

### Community 14 - "Community 14"
Cohesion: 0.20
Nodes (7): EasyFindScraper, Scraper for EasyFind.id, Construct the search URL for a given area and page number., Check if current page has property cards to decide if we should proceed to next, Extract property listings from the current page., Any, PropertyListing

### Community 15 - "Community 15"
Cohesion: 0.12
Nodes (15): ABC, BaseScraper, Abstract base scraper — defines the interface all site-specific scrapers must im, Abstract base class for all property website scrapers.      Every site-specific, Construct the search URL for a given area and page number.          Args:, Extract property listings from the current page.          Args:             tab:, Navigate to the next page of results.          Args:             tab: The curren, Main scraping orchestration method.          Iterates through search result page (+7 more)

### Community 16 - "Community 16"
Cohesion: 0.14
Nodes (13): 1. Geo Module (`src/core/geo.py`), 2. Browser Manager (`src/core/browser.py`), 3. Base Scraper (`src/core/base_scraper.py`), 4. Site Scrapers (`src/scrapers/*.py`), 5. Data Models (`src/models/property.py`), 6. Storage (`src/storage/database.py`), 7. Export (`src/export/exporter.py`), 8. Utilities (`src/utils/`) (+5 more)

### Community 17 - "Community 17"
Cohesion: 0.14
Nodes (8): PropertyListing, Property listing data model — the canonical representation of a scraped property, Parse Indonesian price text to an integer value in IDR.          Handles formats, Pydantic model for a single property listing.      All scraped property data mus, Calculate price per m² of land area., Calculate price per m² of building area., Strip and normalize whitespace in title., Normalize property type to lowercase.

### Community 18 - "Community 18"
Cohesion: 0.20
Nodes (7): NinetynineCoScraper, Scraper for 99.co Indonesia, Navigate to the next page of results., Construct the search URL for a given area and page number., Extract property listings from the current page., Any, PropertyListing

### Community 19 - "Community 19"
Cohesion: 0.15
Nodes (12): Abbreviations, Area Normalization, Computed Fields, CSV, Export Formats, JSON, Optional Fields, Price Normalization Rules (+4 more)

### Community 20 - "Community 20"
Cohesion: 0.22
Nodes (8): CariPropertiScraper, Click the 'Next' button to navigate to the next page of results., Scraper for CariProperti.com      Handles:     1. AJAX Pagination: Uses "Next" b, Override scrape to handle AJAX pagination instead of URL page reloading., Construct the search URL. Note: CariProperti doesn't use page numbers in URL., Extract property listings from the currently loaded/scrolled page., Any, PropertyListing

### Community 21 - "Community 21"
Cohesion: 0.20
Nodes (9): Agent baru:, Agent lama (sebelum berhenti):, Blocked Items, Handoff Protocol, HargaRumah — Progress Tracker, Phase 3: Scraper Status, Phase 4: TODO, Session Log (+1 more)

### Community 22 - "Community 22"
Cohesion: 0.10
Nodes (27): addErrorMessage(), addFormat(), addPattern(), emoji(), escapeLiteralCheckValue(), escapeNonAlphaNumeric(), parseAnyDef(), parseArrayDef() (+19 more)

### Community 23 - "Community 23"
Cohesion: 0.11
Nodes (12): BrowserManager, Initialize the scraper with a browser manager.          Args:             browse, BrowserManager, Browser manager — nodriver browser lifecycle with stealth configuration., Close the browser instance and cleanup., Check if the browser session is currently active., Manages the nodriver browser instance with stealth settings.      Handles browse, Create and initialize a new BrowserManager instance.          Args: (+4 more)

### Community 24 - "Community 24"
Cohesion: 0.16
Nodes (25): activeFileDelete(), activeFileGet(), activeFilePatch(), activeFilePost(), activeFilePut(), commandPost(), executeCommand(), getActiveFile() (+17 more)

### Community 25 - "Community 25"
Cohesion: 0.20
Nodes (7): OlxScraper, Scraper for OLX Indonesia, Navigate to the next page of results using 'Load More' button., Construct the search URL for a given area. Note: OLX uses load more, not pages., Extract property listings from the current page., Any, PropertyListing

### Community 26 - "Community 26"
Cohesion: 0.18
Nodes (10): Features, HargaRumah 🏠, Installation, License, Overview, Prerequisites, Project Structure, Quick Start (+2 more)

### Community 27 - "Community 27"
Cohesion: 0.20
Nodes (7): PashousesScraper, Scraper for Pashouses.id, Construct the search URL for a given area and page number., Navigate to the next page of results., Extract property listings from the current page., Any, PropertyListing

### Community 28 - "Community 28"
Cohesion: 0.18
Nodes (9): main(), run_scrapers(), Scraper for Rumah123.com, Construct the search URL using Rumah123's keyword search.          Uses /jual/ca, Check if there is a next page of results.          BaseScraper.scrape() handles, Extract property listings from the current page., Rumah123Scraper, Any (+1 more)

### Community 29 - "Community 29"
Cohesion: 0.24
Nodes (9): AreaInfo, find_areas_within_radius(), haversine_distance(), Geo utilities — coordinate-to-area-name mapping and distance calculations., Reverse geocode coordinates to get a human-readable location name.      Uses Nom, Information about a geographic area relevant for property search., Calculate the great-circle distance between two points (in km).      Args:, Find known areas within a given radius from the center point.      Args: (+1 more)

### Community 30 - "Community 30"
Cohesion: 0.16
Nodes (9): PinhomeScraper, Scraper for Pinhome.id      As of June 2026, Pinhome no longer supports city/dis, Check if there is a next page., Construct the search URL.         Pinhome supports keyword search via ?keyword=, Parse area value like '72', '1,200', '88 - 262' (takes first)., Parse '3' or '3-5' and return the first number., Extract property listings from the current page., Any (+1 more)

### Community 31 - "Community 31"
Cohesion: 0.20
Nodes (9): 1. URL Patterns, 2. Filtering, 3. Pagination (Infinite Scroll), Anti-Detection & Bot Protection, CariProperti Scraper Guide (cariproperti.com), Extraction logic, Key CSS Selectors, Search and Navigation Flow (+1 more)

### Community 32 - "Community 32"
Cohesion: 0.22
Nodes (8): 1. URL Patterns, 2. Pagination, Anti-Detection & Bot Protection, EasyFind Scraper Guide (easyfind.id), Extraction logic, Key CSS Selectors, Search and Navigation Flow, Website Overview

### Community 33 - "Community 33"
Cohesion: 0.22
Nodes (8): 1. Static Area Slugs (Preferred), 2. Keyword Search (Fallback), Anti-Detection & Bot Protection, Extraction logic, Key CSS Selectors, Pashouses Scraper Guide (pashouses.id), Search and Navigation Flow, Website Overview

### Community 34 - "Community 34"
Cohesion: 0.10
Nodes (24): finite(), floatSafeRemainder(), _gt(), _gte(), _int(), jsonStringifyReplacer(), _length(), _lt() (+16 more)

### Community 35 - "Community 35"
Cohesion: 0.09
Nodes (23): _addCheck(), _base64(), _base64url(), cidr(), _cuid(), _cuid2(), date(), datetime() (+15 more)

### Community 36 - "Community 36"
Cohesion: 0.10
Nodes (20): aborted(), clone(), describe(), extend(), handleIntersectionResults(), handlePipeResult(), isObject(), isPlainObject() (+12 more)

### Community 37 - "Community 37"
Cohesion: 0.29
Nodes (6): Logger, get_logger(), Structured logging setup using Rich for beautiful console output., Configure structured logging with Rich handler.      Args:         level: Log le, Get a named logger instance.      Args:         name: Logger name (typically __n, setup_logging()

### Community 38 - "Community 38"
Cohesion: 0.33
Nodes (5): Adding a New Website, Configuration Files, Documentation Map, HargaRumah Documentation Index, Website Documentation

### Community 39 - "Community 39"
Cohesion: 0.11
Nodes (19): clear(), close(), configureHttpServerTimeouts(), en_default(), error(), errorHandler(), finalizeIssue(), isEmpty() (+11 more)

### Community 40 - "Community 40"
Cohesion: 0.11
Nodes (19): "node_modules/node-forge/lib/aes.js"(), "node_modules/node-forge/lib/cipher.js"(), "node_modules/node-forge/lib/des.js"(), "node_modules/node-forge/lib/hmac.js"(), "node_modules/node-forge/lib/md5.js"(), "node_modules/node-forge/lib/mgf1.js"(), "node_modules/node-forge/lib/pbe.js"(), "node_modules/node-forge/lib/pbkdf2.js"() (+11 more)

### Community 41 - "Community 41"
Cohesion: 0.20
Nodes (9): Anti-Detection Rules (mandatory), CLAUDE.md — Agent Entry Point, Coding Conventions, Default Search Parameters, Key References, Project Overview, Project Structure, Scraper Pattern (+1 more)

### Community 42 - "Community 42"
Cohesion: 0.15
Nodes (18): abort(), _cleanupTaskProgressHandler(), _cleanupTimeout(), _clearTaskQueue(), closeSSEStream(), closeStandaloneSSEStream(), fromError(), get() (+10 more)

### Community 43 - "Community 43"
Cohesion: 0.12
Nodes (18): and(), args(), _array(), create(), exclude(), extract(), "node_modules/body-parser/index.js"(), "node_modules/body-parser/lib/types/urlencoded.js"() (+10 more)

### Community 46 - "Community 46"
Cohesion: 0.13
Nodes (18): cancelTask(), compile(), createMessage(), elicitInput(), format(), getTask(), getTaskResult(), getValidator() (+10 more)

### Community 47 - "Community 47"
Cohesion: 0.14
Nodes (16): addMcpTool(), addPublicRoute(), addRoute(), assertRegistered(), buildServer(), _createRegisteredTool(), getZodSchemaObject(), issueToolNameWarning() (+8 more)

### Community 48 - "Community 48"
Cohesion: 0.12
Nodes (16): appendFileContent(), "node_modules/iconv-lite/encodings/dbcs-codec.js"(), "node_modules/iconv-lite/encodings/utf16.js"(), "node_modules/iconv-lite/encodings/utf7.js"(), "node_modules/iconv-lite/lib/bom-handling.js"(), "node_modules/iconv-lite/lib/streams.js"(), "node_modules/@modelcontextprotocol/sdk/node_modules/iconv-lite/encodings/dbcs-codec.js"(), "node_modules/@modelcontextprotocol/sdk/node_modules/iconv-lite/encodings/internal.js"() (+8 more)

### Community 49 - "Community 49"
Cohesion: 0.27
Nodes (15): assertCanSetRequestHandler(), assertRequestHandlerCapability(), getLiteralValue(), getMethodLiteral(), getMethodValue(), getObjectShape(), isPlainObject2(), mergeCapabilities() (+7 more)

### Community 57 - "Community 57"
Cohesion: 0.19
Nodes (15): deleteVaultFile(), extractVaultPath(), isContentType(), isPatchOperation(), isPatchTargetScope(), isPatchTargetType(), moveVaultFile(), patchFileSection() (+7 more)

### Community 58 - "Community 58"
Cohesion: 0.15
Nodes (13): debounce(), flatten(), formErrors(), handle(), loadSettings(), "node_modules/express/lib/application.js"(), "node_modules/express/lib/router/index.js"(), "node_modules/express/lib/router/route.js"() (+5 more)

### Community 59 - "Community 59"
Cohesion: 0.20
Nodes (11): assertNotificationCapability(), certificateGet(), _enqueueTaskMessage(), notification(), _onrequest(), openapiYamlGet(), requestTaskStore(), send() (+3 more)

### Community 60 - "Community 60"
Cohesion: 0.25
Nodes (11): connect(), handleDeleteRequest(), handleGetRequest(), handlePostRequest(), handleRequest(), handleUnsupportedRequest(), _maybeWritePrimingEvent(), replayEvents() (+3 more)

### Community 61 - "Community 61"
Cohesion: 0.22
Nodes (9): brand(), _catch(), createZodEnum(), _default(), keyof(), pipe(), preprocess(), processCreateParams() (+1 more)

### Community 62 - "Community 62"
Cohesion: 0.22
Nodes (8): author, authorUrl, description, id, isDesktopOnly, minAppVersion, name, version

### Community 63 - "Community 63"
Cohesion: 0.29
Nodes (8): add(), authenticationMiddleware(), display(), getCertificateIsUptoStandards(), getCertificateValidityDays(), "node_modules/node-forge/lib/rsa.js"(), requestIsAuthenticated(), root()

### Community 64 - "Community 64"
Cohesion: 0.29
Nodes (8): buildBacklinksIndex(), getDocumentMapObject(), getFileMetadataObject(), isTruthy(), listVaultDirectory(), searchJsonLogic(), _vaultGet(), waitForFileCache()

### Community 65 - "Community 65"
Cohesion: 0.25
Nodes (8): emit(), getEnumValues(), isTransforming(), mapMiniTarget(), "node_modules/send/index.js"(), process(), toJSONSchema(), toJsonSchemaCompat()

### Community 66 - "Community 66"
Cohesion: 0.36
Nodes (8): getParseErrorMessage(), getSchemaDescription(), isZ4Schema(), normalizeObjectSchema(), safeParseAsync(), safeParseAsync3(), validateToolInput(), validateToolOutput()

### Community 67 - "Community 67"
Cohesion: 0.25
Nodes (8): has(), isDate(), "node_modules/node-forge/lib/log.js"(), "node_modules/object-inspect/index.js"(), "node_modules/side-channel/index.js"(), "node_modules/side-channel-list/index.js"(), "node_modules/side-channel-map/index.js"(), "node_modules/side-channel-weakmap/index.js"()

### Community 68 - "Community 68"
Cohesion: 0.38
Nodes (7): _createRegisteredResource(), _createRegisteredResourceTemplate(), isConnected(), registerResource(), resource(), sendResourceListChanged(), sendToolListChanged()

### Community 69 - "Community 69"
Cohesion: 0.40
Nodes (6): _createRegisteredPrompt(), object2(), objectFromShape(), prompt(), registerPrompt(), sendPromptListChanged()

### Community 70 - "Community 70"
Cohesion: 0.40
Nodes (5): addResourceSpec(), $constructor(), createDefaultAjvInstance(), registerResources(), setNotificationHandler()

### Community 71 - "Community 71"
Cohesion: 0.40
Nodes (5): createCompletionResult(), getCompleter(), handlePromptCompletion(), handleResourceCompletion(), isCompletable()

### Community 72 - "Community 72"
Cohesion: 0.40
Nodes (5): _normalize(), _overwrite(), _toLowerCase(), _toUpperCase(), _trim()

### Community 73 - "Community 73"
Cohesion: 0.50
Nodes (4): handleArrayResult(), handleObjectResult(), handleOptionalObjectResult(), prefixIssues()

### Community 74 - "Community 74"
Cohesion: 0.67
Nodes (3): check(), custom2(), superRefine()

### Community 75 - "Community 75"
Cohesion: 0.67
Nodes (3): deepPartial(), deepPartialify(), unwrap()

## Knowledge Gaps
- **183 isolated node(s):** `id`, `name`, `version`, `minAppVersion`, `description` (+178 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **20 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `PropertyListing` connect `Community 17` to `Community 2`, `Community 10`, `Community 14`, `Community 15`, `Community 18`, `Community 20`, `Community 23`, `Community 25`, `Community 27`, `Community 28`, `Community 30`?**
  _High betweenness centrality (0.008) - this node is a cross-community bridge._
- **Why does `BaseScraper` connect `Community 15` to `Community 14`, `Community 17`, `Community 18`, `Community 20`, `Community 23`, `Community 25`, `Community 27`, `Community 28`, `Community 30`?**
  _High betweenness centrality (0.003) - this node is a cross-community bridge._
- **Why does `EasyFindScraper` connect `Community 14` to `Community 17`, `Community 15`?**
  _High betweenness centrality (0.001) - this node is a cross-community bridge._
- **Are the 30 inferred relationships involving `PropertyListing` (e.g. with `BrowserManager` and `BaseScraper`) actually correct?**
  _`PropertyListing` has 30 INFERRED edges - model-reasoned connections that need verification._
- **Are the 26 inferred relationships involving `BaseScraper` (e.g. with `BrowserManager` and `PropertyListing`) actually correct?**
  _`BaseScraper` has 26 INFERRED edges - model-reasoned connections that need verification._
- **What connects `id`, `name`, `version` to the rest of the system?**
  _290 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `Community 0` be split into smaller, more focused modules?**
  _Cohesion score 0.08695652173913043 - nodes in this community are weakly interconnected._