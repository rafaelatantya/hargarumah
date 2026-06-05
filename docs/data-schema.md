# Property Listing Data Schema

## PropertyListing Model

This is the canonical data model for all scraped property listings, regardless of source website.

### Required Fields

| Field | Type | Description | Example |
|---|---|---|---|
| `id` | `str` | Unique identifier (source + listing_id) | `"rumah123_12345"` |
| `source` | `str` | Source website name | `"rumah123"` |
| `title` | `str` | Listing title | `"Rumah Minimalis 2 Lantai"` |
| `price_idr` | `int` | Price in IDR (full number, no abbreviation) | `850000000` |
| `url` | `str` | Full URL to the listing page | `"https://rumah123.com/..."` |
| `scraped_at` | `datetime` | When this listing was scraped (UTC) | `"2024-01-15T10:30:00Z"` |

### Optional Fields

| Field | Type | Description | Example |
|---|---|---|---|
| `address` | `str \| None` | Full address string | `"Jl. Raya Bekasi..."` |
| `city` | `str \| None` | City name | `"Bekasi"` |
| `district` | `str \| None` | District/Kecamatan | `"Bekasi Selatan"` |
| `latitude` | `float \| None` | Listing latitude | `-6.2607` |
| `longitude` | `float \| None` | Listing longitude | `106.9894` |
| `property_type` | `str \| None` | Type of property | `"rumah"`, `"apartemen"` |
| `listing_type` | `str \| None` | Sale or rent | `"dijual"`, `"disewa"` |
| `land_area_m2` | `float \| None` | Land area in m² | `120.0` |
| `building_area_m2` | `float \| None` | Building area in m² | `90.0` |
| `bedrooms` | `int \| None` | Number of bedrooms | `3` |
| `bathrooms` | `int \| None` | Number of bathrooms | `2` |
| `floors` | `int \| None` | Number of floors/stories | `2` |
| `garage` | `int \| None` | Number of car spaces | `1` |
| `certificate` | `str \| None` | Certificate type | `"SHM"`, `"HGB"` |
| `condition` | `str \| None` | Property condition | `"baru"`, `"bekas"` |
| `year_built` | `int \| None` | Year built | `2020` |
| `description` | `str \| None` | Full description text | `"Rumah baru..."` |
| `images` | `list[str]` | Image URLs | `["https://..."]` |
| `agent_name` | `str \| None` | Listing agent name | `"PT Agen Properti"` |
| `agent_phone` | `str \| None` | Agent phone number | `"08123456789"` |

### Computed Fields

| Field | Type | Description |
|---|---|---|
| `price_per_m2_land` | `float \| None` | `price_idr / land_area_m2` |
| `price_per_m2_building` | `float \| None` | `price_idr / building_area_m2` |
| `distance_from_center_km` | `float \| None` | Distance from search center |

## Price Normalization Rules

Indonesian property sites display prices in various formats:

| Raw Format | Normalized (IDR) |
|---|---|
| `Rp 850 Jt` | `850000000` |
| `Rp 1,2 M` | `1200000000` |
| `Rp 850.000.000` | `850000000` |
| `850 Juta` | `850000000` |
| `1.2 Miliar` | `1200000000` |
| `Rp 2 T` | `2000000000000` |

### Abbreviations
- `Jt` / `Juta` = × 1,000,000 (million)
- `M` / `Miliar` = × 1,000,000,000 (billion)
- `T` / `Triliun` = × 1,000,000,000,000 (trillion)

## Area Normalization

| Raw Format | Normalized (m²) |
|---|---|
| `120 m²` | `120.0` |
| `120 m2` | `120.0` |
| `LT: 120` | `120.0` (land area) |
| `LB: 90` | `90.0` (building area) |

## Export Formats

### JSON
```json
{
  "metadata": {
    "scraped_at": "2024-01-15T10:30:00Z",
    "center_lat": -6.2607,
    "center_lng": 106.9894,
    "radius_km": 5,
    "total_listings": 150,
    "sources": ["rumah123", "olx", "99co"]
  },
  "listings": [
    {
      "id": "rumah123_12345",
      "source": "rumah123",
      "title": "...",
      "price_idr": 850000000,
      ...
    }
  ]
}
```

### CSV
Flat format with one row per listing, all fields as columns. Metadata in first row as comments.

### XLSX
- Sheet 1: `Listings` — all listings with formatted headers
- Sheet 2: `Summary` — metadata, counts per source, price statistics
- Sheet 3: `Raw` — unformatted data for programmatic use
