#!/usr/bin/env python3
"""
ETL Pipeline: PDF Rulebook Converter.
Converts official Shadowrun 6e PDF rulebooks into clean Markdown files using Docling or PyMuPDF.

Usage:
    python scripts/etl/convert_pdf.py [--single PDF_NAME] [--engine auto|docling|pymupdf] [--cuda]
"""

import sys
import os
import argparse

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from sr6core.vault.pdf_converter import convert_all_pdfs, convert_pdf_to_markdown


def main():
    parser = argparse.ArgumentParser(description="Convert Shadowrun 6e PDF rulebooks to Markdown")
    parser.add_argument("--single", type=str, default=None, help="Single PDF filename in input directory")
    parser.add_argument("--regenerate", action="store_true", help="Force regenerate existing markdown files")
    parser.add_argument("--engine", type=str, choices=["docling", "pymupdf", "auto"], default="auto", help="Conversion engine")
    parser.add_argument("--cuda", action="store_true", default=True, help="Enable CUDA acceleration for Docling")
    parser.add_argument("--cpu", dest="cuda", action="store_false", help="Disable CUDA and force CPU for Docling")
    parser.add_argument("--curated-core", action="store_true", help="Curate core rulebooks")
    parser.add_argument("--no-post-process", dest="post_process", action="store_false", default=True, help="Disable post-processing")
    parser.add_argument("--input-dir", type=str, default=None, help="Input directory containing PDFs")
    parser.add_argument("--output-dir", type=str, default=None, help="Output directory for markdown files")
    args = parser.parse_args()

    print(f"[*] PDF Converter Engine: {args.engine} (CUDA: {args.cuda})")
    if args.single:
        in_dir = args.input_dir or os.path.join(os.path.expanduser("~"), "OneDrive", "Desktop", "SR6", "ebooks")
        out_dir = args.output_dir or os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "converted_md")
        pdf_path = os.path.join(in_dir, args.single)
        out_path = os.path.join(out_dir, f"{os.path.splitext(args.single)[0]}.md")
        out, elapsed = convert_pdf_to_markdown(pdf_path, out_path, engine=args.engine, use_cuda=args.cuda, post_process=args.post_process)
        print(f"[OK] Converted {args.single} in {elapsed:.2f}s -> {out}")
    else:
        results = convert_all_pdfs(
            input_dir=args.input_dir,
            output_dir=args.output_dir,
            engine=args.engine,
            regenerate=args.regenerate,
            use_cuda=args.cuda,
            curated_core=args.curated_core,
            post_process=args.post_process
        )
        print(f"[OK] Converted {len(results)} rulebooks.")


if __name__ == "__main__":
    main()
