"""Extract slim data from latest Harjamukti export and write site/data/harjamukti.json."""
import json
import glob
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = ROOT / "site" / "data"
OUT_DIR.mkdir(parents=True, exist_ok=True)

# Find latest export
files = sorted(glob.glob(str(ROOT / "data" / "exports" / "hargarumah_*.json")))
latest = files[-1]

with open(latest, encoding="utf-8") as f:
    d = json.load(f)

ls = d.get("listings", [])

# Slim to minimum fields
out = []
for l in ls:
    out.append({
        "id": l.get("id"),
        "title": l.get("title"),
        "price_idr": l.get("price_idr"),
        "url": l.get("url"),
        "land_area_m2": l.get("land_area_m2"),
        "building_area_m2": l.get("building_area_m2"),
        "bedrooms": l.get("bedrooms"),
        "bathrooms": l.get("bathrooms"),
        "property_type": l.get("property_type"),
    })

# Stats
prices = sorted([o["price_idr"] for o in out if o["price_idr"]])
med = prices[len(prices) // 2]
lt = [o["land_area_m2"] for o in out if o["land_area_m2"]]

print(f"Source file: {latest}")
print(f"Count: {len(out)}")
print(f"Min:  Rp {min(prices):,}")
print(f"Max:  Rp {max(prices):,}")
print(f"Med:  Rp {med:,}")
print(f"LT min/max: {min(lt)} / {max(lt)}")

# Write slim JSON
out_path = OUT_DIR / "harjamukti.json"
with open(out_path, "w", encoding="utf-8") as f:
    json.dump({
        "metadata": {
            "keyword": "harjamukti",
            "source": "rumah123",
            "scraped_at": d["metadata"]["scraped_at"],
            "count": len(out),
            "min_price": min(prices),
            "max_price": max(prices),
            "median_price": med,
        },
        "listings": out,
    }, f, ensure_ascii=False, indent=2)

print(f"Wrote {out_path}")
