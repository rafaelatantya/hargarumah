"""Sanity check: harjamukti.json is valid + files present."""
import json
from pathlib import Path

SITE = Path(__file__).resolve().parent.parent / "site"

print("Files:")
for p in ["harjamukti.html", "index.html", "data/harjamukti.json"]:
    full = SITE / p
    print(f"  {p:30s} {'OK' if full.exists() else 'MISSING':10s} {full.stat().st_size:>8} B")

with open(SITE / "data" / "harjamukti.json", encoding="utf-8") as f:
    d = json.load(f)

print(f"\nListings: {len(d['listings'])}")
print(f"Median: Rp {d['metadata']['median_price']:,}")
print(f"Keys:   {list(d['listings'][0].keys())}")

# Validate that each listing has the required fields
required = ["id", "title", "price_idr", "url"]
missing = []
for l in d["listings"]:
    for r in required:
        if not l.get(r):
            missing.append((l.get("id"), r))
print(f"Missing required fields: {len(missing)}")

# Check that all titles contain 'harjamukti' (strict filter check)
not_hj = [l for l in d["listings"] if "harjamukti" not in l["title"].lower()]
print(f"Strict filter violations (no 'harjamukti' in title): {len(not_hj)}")
