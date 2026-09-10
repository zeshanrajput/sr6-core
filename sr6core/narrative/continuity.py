"""
Campaign Timeline & Story Continuity Engine for SR6.
Indexes entity appearances, track character foils, and calculates narrative chapter statistics.
"""

import os
import re
import glob
from typing import Dict, Any, Tuple, Optional


def build_continuity_report(repo_dir: str) -> Tuple[Dict[str, Any], Optional[str]]:
    if not os.path.exists(repo_dir):
        return {}, f"Repository directory '{repo_dir}' not found."

    chapters_dir = os.path.join(repo_dir, "chapters")
    chapter_files = sorted(glob.glob(os.path.join(chapters_dir, "*.*")))
    chapter_files = [f for f in chapter_files if f.endswith(".md") or f.endswith(".qmd")]

    chapter_summaries = []
    total_words = 0

    for chap_path in chapter_files:
        chap_name = os.path.basename(chap_path)
        with open(chap_path, "r", encoding="utf-8") as f:
            content = f.read()

        title_match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
        title = title_match.group(1) if title_match else chap_name
        words = len(re.findall(r'\b\w+\b', content))
        total_words += words
        chapter_summaries.append({
            "filename": chap_name,
            "title": title,
            "word_count": words,
            "path": chap_path
        })

    report = {
        "repo_dir": repo_dir,
        "chapter_count": len(chapter_summaries),
        "total_word_count": total_words,
        "chapters": chapter_summaries
    }
    return report, None


def print_continuity_report(report: Dict[str, Any]):
    print("=" * 65)
    print(" CAMPAIGN STORY CONTINUITY REPORT")
    print(f" Repo: {report['repo_dir']}")
    print("=" * 65)
    print(f" Total Chapters        : {report['chapter_count']}")
    print(f" Total Anthology Words : {report['total_word_count']:,} words")
    print("\nChapter Breakdown:")
    for ch in report.get("chapters", []):
        print(f" - {ch['filename']:<25} | Words: {ch['word_count']:<6,} | Title: {ch['title']}")
    print("=" * 65 + "\n")
