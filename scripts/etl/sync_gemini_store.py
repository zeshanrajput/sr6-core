#!/usr/bin/env python3
"""
ETL Pipeline: Google Gemini File Search Store Sync.
Synchronizes local rules vault markdown chunks with Google Gemini Vector Store.

Usage:
    python scripts/etl/sync_gemini_store.py [--skip-updates] [--workers 10]
"""

import sys
import os
import argparse

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from sr6core.vault.gemini_sync import sync_gemini_store


def main():
    parser = argparse.ArgumentParser(description="Synchronize local markdown rules vault to Google Gemini Store")
    parser.add_argument("--skip-updates", action="store_true", help="Skip updating files with identical hash")
    parser.add_argument("--workers", type=int, default=10, help="Concurrent upload workers")
    args = parser.parse_args()

    print("[*] Synchronizing rules vault to Google Gemini Store...")
    try:
        res = sync_gemini_store(skip_updates=args.skip_updates, max_workers=args.workers)
        print("[OK] Sync completed successfully.")
        print(f"     Uploaded: {res.get('uploaded', 0)}")
        print(f"     Updated : {res.get('updated', 0)}")
        print(f"     Skipped : {res.get('skipped', 0)}")
    except Exception as e:
        print(f"[Error] Failed to sync to Gemini: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
