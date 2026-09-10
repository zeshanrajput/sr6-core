#!/usr/bin/env python3
"""
ETL Pipeline: Web FAQ Importer.
Scrapes and imports official Shadowrun 6e FAQ entries into Markdown and the SQLite vault.

Usage:
    python scripts/etl/import_faq.py [--url URL] [--html HTML_FILE]
"""

import sys
import os
import argparse

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from sr6core.vault.web_importer import import_faq_url, import_faq_file


def main():
    parser = argparse.ArgumentParser(description="Import official SR6 FAQ into converted_md and vault")
    parser.add_argument("--url", type=str, default="https://shadowrunsixthworld.com/shadowrun-sixth-world-faq/", help="FAQ URL to fetch")
    parser.add_argument("--html", type=str, default=None, help="Local HTML file path")
    args = parser.parse_args()

    if args.html:
        print(f"[*] Importing FAQ from local file: {args.html}")
        chunks = import_faq_file(args.html)
    else:
        print(f"[*] Fetching FAQ from: {args.url}")
        chunks = import_faq_url(args.url)

    print(f"[OK] Successfully imported {len(chunks)} FAQ rules into vault.")


if __name__ == "__main__":
    main()
