import asyncio
import sys
import io
import logging
import argparse
import os

from src.core.orchestrator import run_scrapers

# Fix Windows Unicode encode errors in the terminal
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
logging.basicConfig(level=logging.WARNING, format='%(levelname)s: %(message)s')

def main():
    parser = argparse.ArgumentParser(description="HargaRumah CLI - Auto Scrape Properti")
    parser.add_argument("keyword", nargs="?", help="Lokasi/alamat yang dicari (contoh: harjamukti)")
    parser.add_argument("--site", type=str, default="all", help="Target situs. Default: all (contoh: rumah123, olx)")
    parser.add_argument("--min", type=int, default=10, help="Target minimum listing per situs")
    args = parser.parse_args()

    keyword = args.keyword
    if not keyword:
        print("=======================================")
        print("   HARGARUMAH - AUTO SCRAPER CLI")
        print("=======================================")
        keyword = input("Masukkan lokasi / alamat lengkap yang ingin dicari:\n> ").strip()

    if not keyword:
        print("Error: Lokasi tidak boleh kosong.")
        sys.exit(1)

    try:
        asyncio.run(run_scrapers(keyword, site_filter=args.site, min_listings=args.min))
    finally:
        # Prevent Windows asyncio "I/O operation on closed pipe" error during garbage collection
        if sys.platform == 'win32':
            sys.stderr = open(os.devnull, 'w')

if __name__ == "__main__":
    main()
