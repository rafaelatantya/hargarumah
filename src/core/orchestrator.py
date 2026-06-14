"""Orchestration logic for running multiple scrapers."""

import re
import sys
import logging
from typing import List
from pathlib import Path

from src.core.browser import BrowserManager
from src.scrapers import get_scrapers
from src.models.property import PropertyListing
from src.storage.database import Database
from src.export.exporter import export_all
from src.core.geo import find_areas_within_radius

logger = logging.getLogger(__name__)

def generate_search_levels(address: str) -> list[str]:
    """
    Memecah alamat dengan cara mencopot bagian spesifik dari depan ke belakang.
    """
    text = address.encode('ascii', 'ignore').decode('ascii').strip()

    # Kunci untuk URL construction yang lebih baik
    text = text.replace(" ", "-").lower()

    norm_text = text
    norm_text = re.sub(r'\bbks\b', 'bekasi', norm_text, flags=re.IGNORECASE)
    norm_text = re.sub(r'\bjkt\b', 'jakarta', norm_text, flags=re.IGNORECASE)
    norm_text = norm_text.replace('sel.', 'selatan').replace('tim.', 'timur').replace('bar.', 'barat').replace('ut.', 'utara')

    levels = []

    # Original address hyphenated
    levels.append(norm_text)

    # Remove city/district/kecamatan indicators
    clean_text = norm_text.replace('kecamatan-', '').replace('kec.-', '').replace('kota-', '').replace('kabupaten-', '').replace('kab.-', '')
    if clean_text != norm_text:
        levels.append(clean_text)

    # Just the parts (split by - and try different combinations)
    parts = clean_text.split("-")
    if len(parts) > 1:
        # e.g. "bekasi-selatan" -> "selatan"
        for i in range(1, len(parts)):
            levels.append("-".join(parts[i:]))

    return list(dict.fromkeys(levels)) # deduplicate


async def run_scrapers(full_address: str, site_filter: str = "all", min_listings: int = 10) -> list[PropertyListing]:
    """
    Menjalankan proses scraping untuk beberapa website dengan strategi recursive search.
    """
    print(f"\n[+] Memulai pencarian properti untuk alamat:\n    '{full_address}'\n")

    search_levels = generate_search_levels(full_address)
    print("[*] Level pencarian berjenjang yang akan digunakan:")
    for idx, lvl in enumerate(search_levels):
        print(f"    Lvl {idx+1}: '{lvl}'")
    print()

    scraper_classes = get_scrapers(site_filter)

    if not scraper_classes:
        from src.scrapers import get_available_names
        print(f"[!] Error: Tidak ada scraper valid yang dipilih. Tersedia: {', '.join(get_available_names())}")
        sys.exit(1)

    print(f"[*] Akan menjalankan {len(scraper_classes)} scraper: {', '.join([s[0] for s in scraper_classes])}\n")

    browser = await BrowserManager.create()
    all_results: list[PropertyListing] = []
    seen_ids = set()

    try:
        for name, ScraperClass in scraper_classes:
            print(f"[*] Menjalankan scraper {name}...")

            # Instansiasi scraper dengan browser yang sama
            scraper = ScraperClass(browser)
            site_results = []

            for level_idx, keyword in enumerate(search_levels):
                target_remaining = min_listings - len(site_results)
                if target_remaining <= 0:
                    break

                print(f"    -> Mencari level {level_idx+1}: '{keyword}' (butuh {target_remaining} lagi)")
                try:
                    listings = await scraper.scrape(keyword, min_listings=target_remaining)

                    new_count = 0
                    for l in listings:
                        if l.id not in seen_ids:
                            seen_ids.add(l.id)
                            site_results.append(l)
                            all_results.append(l)
                            new_count += 1

                    print(f"       Dapat {new_count} listing baru di level ini.")
                except Exception as e:
                    print(f"       Error di level '{keyword}': {e}")

            print(f"    => Total dari {name}: {len(site_results)} listing.\n")

        print(f"[+] Pencarian selesai. Total {len(all_results)} listing unik ditemukan dari {len(scraper_classes)} situs.\n")

        # --- STORAGE & EXPORT LAYER ---
        if all_results:
            print("[*] Menyimpan data ke SQLite Database...")
            db = Database()
            await db.connect()
            inserted_count = await db.save_many(all_results)
            await db.close()
            print(f"    -> Tersimpan: {inserted_count} listing baru di database.")

            print("[*] Mengekspor hasil ke JSON, CSV, dan XLSX...")
            # Simulasi koordinat pusat (karena input kita alamat teks, bukan koordinat)
            # Default kita pasang koordinat nol, atau jika ada geo resolver bisa disesuaikan
            center_lat, center_lng, radius = 0.0, 0.0, 0.0

            # Convert models to dict for exporter
            dict_listings = [listing.model_dump(mode="json") for listing in all_results]

            exports = await export_all(
                listings=dict_listings,
                center_lat=center_lat,
                center_lng=center_lng,
                radius_km=radius
            )
            print("    -> Export selesai:")
            for fmt, path in exports.items():
                print(f"       [{fmt.upper()}] {path}")
            print()

        _print_summary(scraper_classes, all_results, min_listings)

    finally:
        await browser.close()

    return all_results


def _print_summary(scraper_classes: list[tuple[str, type]], all_results: list[PropertyListing], min_listings: int):
    """Mencetak ringkasan hasil secara per-situs ke terminal."""
    for name, _ in scraper_classes:
        # Ambil hanya hasil dari site ini berdasarkan substring di attribute source
        site_list = [l for l in all_results if l.source.lower() == name.replace('.co', 'co').replace('.', '').lower()]
        if not site_list:
            site_list = [l for l in all_results if l.source.lower() in name.lower() or name.lower() in l.source.lower()]

        limit = min(len(site_list), min_listings)
        if limit == 0:
            print(f"=== {name.upper()}: Tidak ada hasil ===")
            print()
            continue

        print(f"=== Menampilkan {limit} Hasil dari {name.upper()} ===")
        for i, l in enumerate(site_list[:limit]):
            print(f"{i+1}. {l.title[:60]}")
            print(f"   Harga: Rp {l.price_idr:,.0f}" if l.price_idr else "   Harga: N/A")
            specs = []
            if l.bedrooms: specs.append(f"{l.bedrooms} KT")
            if l.bathrooms: specs.append(f"{l.bathrooms} KM")
            if l.land_area_m2: specs.append(f"LT: {l.land_area_m2} m2")
            if l.building_area_m2: specs.append(f"LB: {l.building_area_m2} m2")
            if specs: print(f"   Spek: {' | '.join(specs)}")
            print(f"   Link: {l.url}")
            print()
