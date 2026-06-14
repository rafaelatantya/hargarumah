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
    Contoh request:
    Input: "Jl. Taman Anggrek Bulan 15-8 RT.002/RW.014, Jaka Setia, Kec. Bekasi Sel., Kota Bks"
    Lvl 1: "Jl. Taman Anggrek Bulan 15-8 RT.002/RW.014, Jaka Setia, Kec. Bekasi Sel., Kota Bks"
    Lvl 2: "RT.002/RW.014, Jaka Setia, Kec. Bekasi Sel., Kota Bks"
    Lvl 3: "Jaka Setia, Kec. Bekasi Sel., Kota Bks"
    Lvl 4: "Kec. Bekasi Sel., Kota Bks"
    Lvl 5: "Kota Bks"
    """
    text = address.encode('ascii', 'ignore').decode('ascii').strip()

    norm_text = text
    norm_text = re.sub(r'\bbks\b', 'Bekasi', norm_text, flags=re.IGNORECASE)
    norm_text = re.sub(r'\bjkt\b', 'Jakarta', norm_text, flags=re.IGNORECASE)
    norm_text = norm_text.replace('Sel.', 'Selatan').replace('Tim.', 'Timur').replace('Bar.', 'Barat').replace('Ut.', 'Utara')

    levels = []

    if "," in norm_text:
        parts = [p.strip() for p in norm_text.split(",")]

        first_part = parts[0]
        rt_match = re.search(r'(RT\.?\s*\d+/?RW\.?\s*\d+)', first_part, re.IGNORECASE)

        base_parts = []
        if rt_match:
            rt_str = rt_match.group(1)
            jalan_str = first_part.replace(rt_str, '').strip()
            if jalan_str:
                base_parts.append(jalan_str)
            base_parts.append(rt_str)
        else:
            base_parts.append(first_part)

        all_parts = base_parts + parts[1:]

        for i in range(len(all_parts)):
            level_str = " ".join(all_parts[i:])
            level_str = " ".join(level_str.split())
            if level_str and level_str not in levels:
                levels.append(level_str)

        clean_kec = re.sub(r'Kec\.|Kecamatan', '', all_parts[-2] if len(all_parts) >= 2 else '').strip()
        clean_kota = re.sub(r'Kota|Kab\.|Kabupaten', '', all_parts[-1] if len(all_parts) >= 1 else '').strip()
        pure_level = f"{clean_kec} {clean_kota}".strip()
        pure_level = " ".join(pure_level.split())
        if pure_level and pure_level not in levels:
            levels.append(pure_level)

    else:
        words = norm_text.split()
        for i in range(0, len(words), max(1, len(words)//3)):
            level_str = " ".join(words[i:])
            if level_str and level_str not in levels:
                levels.append(level_str)

    return levels


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
