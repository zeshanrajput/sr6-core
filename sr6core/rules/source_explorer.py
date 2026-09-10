"""
Sourcebook Text & Page Explorer for SR6 Core.
Provides instant lookup across all 72 markdown books in converted_md/ using short book codes and fuzzy resolution.
"""

import os
import re
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple

BOOK_ACRONYMS: Dict[str, str] = {
    "6wc": "CAT28005_Sixth_World_Companion.md",
    "companion": "CAT28005_Sixth_World_Companion.md",
    "bs": "CAT28007_Body_Shop.md",
    "bodyshop": "CAT28007_Body_Shop.md",
    "crb": "CAT28000S_SR6 Core City Edition Seattle.md",
    "core": "CAT28000S_SR6 Core City Edition Seattle.md",
    "seattle": "CAT28000S_SR6 Core City Edition Seattle.md",
    "berlin": "CAT28000B_SR6 Berlin Edition.md",
    "hns": "CAT28006_Hack_and_Slash.md",
    "hack": "CAT28006_Hack_and_Slash.md",
    "dc": "CAT28004_Double_Clutch.md",
    "doubleclutch": "CAT28004_Double_Clutch.md",
    "fs": "CAT28002_Firing_Squad.md",
    "firingsquad": "CAT28002_Firing_Squad.md",
    "sw": "CAT28003_Street_Wyrd.md",
    "streetwyrd": "CAT28003_Street_Wyrd.md",
    "cn": "CAT28450_Collapsing_Now.md",
    "collapsingnow": "CAT28450_Collapsing_Now.md",
    "pp": "CAT28451_Power_Plays.md",
    "powerplays": "CAT28451_Power_Plays.md",
    "nv": "CAT28452_Null_Value.md",
    "nullvalue": "CAT28452_Null_Value.md",
    "fp": "CAT28453_Falling_Point.md",
    "fallingpoint": "CAT28453_Falling_Point.md",
    "wn": "CAT28404_Whisper_Nets.md",
    "whispernets": "CAT28404_Whisper_Nets.md",
    "so": "CAT28009_Smooth_Operations.md",
    "smoothoperations": "CAT28009_Smooth_Operations.md",
    "da": "CAT28011_Shadowrun_Deadly_Arts.md",
    "deadlyarts": "CAT28011_Shadowrun_Deadly_Arts.md",
    "wl": "CAT28008_Wild_Life.md",
    "wildlife": "CAT28008_Wild_Life.md",
    "ec": "CAT28100_Emerald_City.md",
    "emeraldcity": "CAT28100_Emerald_City.md",
    "aw": "CAT28101_Astral_Ways.md",
    "astralways": "CAT28101_Astral_Ways.md",
    "srm": "391504-Missions_SR6_Guide_v2_4.md",
    "missions": "391504-Missions_SR6_Guide_v2_4.md",
    "faq": "Shadowrun_Sixth_World_FAQ.md",
    "nofuture": "CAT27453_No Future 6E.md",
    "streetpedia": "CAT27454_NeoA Streetpedia.md",
    "krime": "E-CAT27002S_Krime Katalog.md",
}


def get_converted_md_dir() -> Path:
    """Returns the path to converted_md directory."""
    from sr6core.rules_db import get_default_converted_dir
    return Path(get_default_converted_dir())


def resolve_book_file(book_query: str) -> Tuple[Optional[Path], str]:
    """
    Resolves a book query (code, acronym, or partial filename) to an existing file in converted_md.
    Returns (Path, resolved_label).
    """
    conv_dir = get_converted_md_dir()
    if not conv_dir.exists():
        return None, f"converted_md directory not found at '{conv_dir}'"

    clean_query = book_query.strip().lower().replace(" ", "").replace("_", "").replace("-", "")

    # 1. Exact acronym / alias lookup
    if clean_query in BOOK_ACRONYMS:
        candidate = conv_dir / BOOK_ACRONYMS[clean_query]
        if candidate.exists():
            return candidate, candidate.name

    # 2. Match against filenames in converted_md
    all_files = list(conv_dir.glob("*.md"))
    for f in all_files:
        clean_name = f.stem.lower().replace(" ", "").replace("_", "").replace("-", "")
        if clean_query == clean_name or clean_query in clean_name:
            return f, f.name

    # 3. Fuzzy search on words
    for f in all_files:
        words = re.findall(r"\w+", clean_query)
        if all(w in f.stem.lower() for w in words):
            return f, f.name

    available = ", ".join(sorted(set(list(BOOK_ACRONYMS.keys())[:15])))
    return None, f"Could not find book matching '{book_query}'. Try common codes: {available}, etc."


def search_source_book(
    book_query: str,
    search_query: str,
    context_lines: int = 15,
    max_matches: int = 3,
) -> Dict[str, Any]:
    """
    Searches a specific sourcebook in converted_md and returns excerpt blocks around matches.
    """
    book_path, label = resolve_book_file(book_query)
    if not book_path:
        return {"error": label, "matches": []}

    try:
        with open(book_path, "r", encoding="utf-8", errors="replace") as f:
            lines = f.readlines()
    except Exception as e:
        return {"error": f"Failed to read '{book_path}': {e}", "matches": []}

    pattern = re.compile(re.escape(search_query.strip()), re.IGNORECASE)
    matching_indices = []
    for i, line in enumerate(lines):
        if pattern.search(line):
            matching_indices.append(i)
            if len(matching_indices) >= max_matches * 3:
                break

    if not matching_indices:
        return {
            "book": label,
            "book_path": str(book_path),
            "search_query": search_query,
            "matches": [],
            "message": f"No matches found for '{search_query}' in {label}."
        }

    # Cluster close matches to avoid overlapping excerpts
    clusters: List[Tuple[int, int]] = []
    for idx in matching_indices:
        start = max(0, idx - context_lines)
        end = min(len(lines), idx + context_lines + 1)
        if clusters and start <= clusters[-1][1]:
            # Merge with previous cluster
            clusters[-1] = (clusters[-1][0], max(clusters[-1][1], end))
        else:
            clusters.append((start, end))
        if len(clusters) >= max_matches:
            break

    match_results = []
    for start, end in clusters:
        snippet_lines = []
        for line_num in range(start, end):
            prefix = ">> " if line_num in matching_indices else "   "
            snippet_lines.append(f"{line_num + 1:5d} | {prefix}{lines[line_num].rstrip()}")
        match_results.append({
            "start_line": start + 1,
            "end_line": end,
            "snippet": "\n".join(snippet_lines),
            "raw_text": "".join(lines[start:end])
        })

    return {
        "book": label,
        "book_path": str(book_path),
        "search_query": search_query,
        "matches": match_results,
        "total_matches": len(matching_indices)
    }


def format_source_results(result: Dict[str, Any], fmt: str = "markdown") -> str:
    """Formats source search results for display."""
    if "error" in result:
        return f"[Error] {result['error']}"

    if not result.get("matches"):
        return f"No occurrences of '{result.get('search_query')}' found in **{result.get('book')}**."

    out = [f"### Excerpts from {result['book']} (Found in {result['total_matches']} places)\n"]
    out.append(f"*File*: `{result['book_path']}`\n")

    for i, m in enumerate(result["matches"], 1):
        out.append(f"#### Match #{i} (Lines {m['start_line']}–{m['end_line']}):")
        out.append("```markdown")
        out.append(m["snippet"])
        out.append("```\n")

    return "\n".join(out)
