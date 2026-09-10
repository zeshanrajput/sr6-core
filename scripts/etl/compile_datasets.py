#!/usr/bin/env python3
"""
ETL Pipeline: CommLink6 Dataset Compiler.
Extracts XML game datasets from CommLink6 JAR releases and indexes them into SQLite.

Usage:
    python scripts/etl/compile_datasets.py [--jar PATH_TO_JAR]
"""

import sys
import os
import argparse

# Add repo root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from sr6core.dataset_compiler import compile_commlink_datasets, find_latest_commlink_jar, get_dataset_info


def main():
    parser = argparse.ArgumentParser(description="Compile CommLink6 JAR XML datasets into ~/.sr6/rules_index.db")
    parser.add_argument("--jar", type=str, default=None, help="Path to CommLink6 JAR file")
    args = parser.parse_args()

    jar_path = args.jar or find_latest_commlink_jar()
    if not jar_path:
        print("[Error] No CommLink6 JAR found. Please specify --jar /path/to/commlink6.jar")
        sys.exit(1)

    print(f"[*] Extracting datasets from: {jar_path}")
    ok, msg = compile_commlink_datasets(jar_path=jar_path)
    print(f"[{'OK' if ok else 'FAIL'}] {msg}")

    info = get_dataset_info()
    print("\n--- Current Database Summary ---")
    for k, v in info.items():
        print(f"  {k:<20}: {v}")


if __name__ == "__main__":
    main()
