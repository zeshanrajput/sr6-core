"""
Audio Narration Pre-Flight Engine for SR6 Campaign Chapters.
Scans prose drafts prior to TTS synthesis to detect:
1. English heteronyms with multiple pronunciations (bow, lead, tear, wind, wound, etc.)
   flagging whether they are mapped in reference/pronunciations.yaml.
2. Unmapped proper nouns, character names, and italicized lore terms requiring phonetic pronunciation entries.
"""

import os
import re
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple, Set

from sr6core.narrative.narration import get_pronunciation_dictionary
from sr6core.narrative.linter import PROXIMITY_STOP_WORDS

COMMON_TTS_HETERONYMS = [
    "bow", "bows", "bowed", "bowing",
    "lead", "leads",
    "tear", "tears",
    "wind", "winds", "winding",
    "wound", "wounds",
    "read",
    "live", "lives",
    "row", "rows",
    "close",
    "use",
    "separate",
    "deliberate",
    "intimate",
]

HETERONYM_REGEX = re.compile(
    r"\b(" + "|".join(COMMON_TTS_HETERONYMS) + r")\b", re.IGNORECASE
)

ITALIC_LORE_REGEX = re.compile(
    r"(?<!\*)\*([A-Za-z0-9\u00C0-\u024F][^*]*?[A-Za-z0-9\u00C0-\u024F])\*(?!\*)"
)

CAPITALIZED_TOKEN_REGEX = re.compile(
    r"\b[A-Z\u00C0-\u00D6\u00D8-\u00DE][A-Za-z0-9\u00C0-\u024F\'-]*\b"
)

EXTRA_STOP_WORDS = {
    "monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday",
    "january", "february", "march", "april", "may", "june", "july", "august",
    "september", "october", "november", "december",
    "mr", "mrs", "ms", "dr", "sir", "madam", "ma'am", "lady", "lord", "god", "gods",
    "mom", "dad", "mother", "father", "uncle", "aunt", "sister", "brother",
    "one", "two", "three", "four", "five", "six", "seven", "eight", "nine", "ten",
    "first", "second", "third", "fourth", "fifth",
    "north", "south", "east", "west",
    "chapter", "beat", "part", "act", "volume", "book", "section", "page",
    "yes", "no", "oh", "ah", "okay", "ok", "hey", "hi", "hello", "goodbye", "bye",
    "please", "sorry", "thank", "thanks", "well", "wait", "look", "right", "sure",
    "fine", "now", "then", "here", "there", "maybe", "perhaps", "never", "always",
    "everyone", "everything", "someone", "something", "anyone", "anything", "nobody",
    "nothing", "hell", "damn", "christ", "jesus", "amen",
    "street", "avenue", "road", "boulevard", "lane", "drive", "way", "ave", "blvd",
    "jr", "sr", "ii", "iii", "iv", "vi", "vii", "viii", "am", "pm", "us", "usa", "uk",
}


def _is_sentence_or_quote_start(line: str, start_pos: int) -> bool:
    """
    Checks if a token at start_pos is at the beginning of a line,
    the beginning of a spoken quote, or after sentence-ending punctuation.
    """
    prefix = line[:start_pos]
    stripped = prefix.rstrip("\"'“‘*_( [{<")
    if not stripped.strip():
        return True

    # Preceded by opening quote mark after comma/colon/dash
    quote_chars = "\"\"''“‘"
    has_quote = any(c in quote_chars for c in prefix[len(stripped):])
    if has_quote and stripped.rstrip().endswith((",", ":", ";", "--", "—")):
        return True

    # Preceded by sentence-ending punctuation (. ! ?)
    if stripped.rstrip().endswith((".", "!", "?")):
        return True

    return False


def _clean_line_for_scanning(line: str) -> str:
    """Strips HTML tags, links, images, and headers while preserving italic markers and text."""
    # Strip HTML tags
    cleaned = re.sub(r"<[^>]+>", "", line)
    # Strip Markdown image embeds
    cleaned = re.sub(r"!\[.*?\]\(.*?\)", "", cleaned)
    # Convert Markdown links [text](url) to text
    cleaned = re.sub(r"\[(.*?)\]\(.*?\)", r"\1", cleaned)
    # Strip standalone URLs
    cleaned = re.sub(r"https?://\S+", "", cleaned)
    # Strip header markers (# Title -> Title)
    cleaned = re.sub(r"^#{1,6}\s*", "", cleaned)
    # Strip blockquote markers
    cleaned = re.sub(r"^>\s*", "", cleaned)
    # Strip list markers
    cleaned = re.sub(r"^[\*\-\+]\s+", "", cleaned)
    cleaned = re.sub(r"^\d+\.\s+", "", cleaned)
    # Strip inline backticks (`code` -> code)
    cleaned = re.sub(r"`([^`]+)`", r"\1", cleaned)
    return cleaned


def scan_audio_prep(file_path: str) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
    """
    Scans a chapter markdown file or raw prose string for:
    1. Common TTS heteronyms (flagging whether they exist in pronunciations.yaml).
    2. Unmapped proper nouns, character names, and italicized lore terms.

    Returns:
        (report_dict, None) on success, or (None, error_str) on failure.
    """
    try:
        if os.path.exists(file_path) and os.path.isfile(file_path):
            with open(file_path, "r", encoding="utf-8") as f:
                lines = f.readlines()
            resolved_target = str(Path(file_path).resolve())
        else:
            lines = [l + "\n" for l in file_path.splitlines()]
            resolved_target = "<raw_text>"
    except Exception as e:
        return None, f"Failed to read target for audio prep scan: {e}"

    # Load pronunciation dictionary
    try:
        terms, patterns = get_pronunciation_dictionary()
    except Exception:
        terms, patterns = {}, []

    terms_lower: Dict[str, str] = {k.lower(): v for k, v in terms.items()}

    # Build comprehensive stop words set
    stop_words: Set[str] = set(PROXIMITY_STOP_WORDS)
    stop_words.update(EXTRA_STOP_WORDS)

    heteronyms: List[Dict[str, Any]] = []
    unmapped_occurrences: Dict[str, List[int]] = {}
    mapped_lore_dict: Dict[str, Dict[str, Any]] = {}

    in_frontmatter = False
    in_code = False

    for idx, raw_line in enumerate(lines, 1):
        stripped = raw_line.strip()

        # Handle frontmatter
        if idx == 1 and stripped == "---":
            in_frontmatter = True
            continue
        if in_frontmatter:
            if stripped == "---":
                in_frontmatter = False
            continue

        # Handle code blocks
        if stripped.startswith("```"):
            in_code = not in_code
            continue
        if in_code:
            continue

        cleaned_line = _clean_line_for_scanning(raw_line)
        if not cleaned_line.strip():
            continue

        # 1. Heteronym Scan
        for m in HETERONYM_REGEX.finditer(cleaned_line):
            w = m.group(0)
            w_low = w.lower()
            mapped_val = terms_lower.get(w_low)
            heteronyms.append({
                "line": idx,
                "word": w,
                "mapped_to": mapped_val,
                "snippet": raw_line.strip(),
            })

        # 2. Italicized Lore Terms Scan (*Word* or *Word Word*, 1-3 words)
        italic_spans: List[Tuple[int, int]] = []
        for m in ITALIC_LORE_REGEX.finditer(cleaned_line):
            content = m.group(1).strip()
            # Skip dialogue sentences ending in sentence punctuation
            if content.endswith((".", "?", "!")):
                continue
            words = content.split()
            if 1 <= len(words) <= 3:
                term = content.strip("\"'‘“,”’;: ")
                t_low = term.lower()
                if len(term) <= 1:
                    continue
                italic_spans.append((m.start(), m.end()))
                if t_low in terms_lower:
                    if term not in mapped_lore_dict:
                        mapped_lore_dict[term] = {"mapped_to": terms_lower[t_low], "lines": []}
                    mapped_lore_dict[term]["lines"].append(idx)
                elif t_low not in stop_words:
                    unmapped_occurrences.setdefault(term, []).append(idx)

        # 3. Mid-Sentence & Known Capitalized Tokens Scan
        for m in CAPITALIZED_TOKEN_REGEX.finditer(cleaned_line):
            start_pos = m.start()
            if any(s <= start_pos and m.end() <= e for s, e in italic_spans):
                continue

            raw_token = m.group(0)
            token = re.sub(r"'s$", "", raw_token).strip("\"'‘“”-")
            if len(token) <= 1:
                continue

            t_low = token.lower()
            if t_low in terms_lower:
                if token not in mapped_lore_dict:
                    mapped_lore_dict[token] = {"mapped_to": terms_lower[t_low], "lines": []}
                mapped_lore_dict[token]["lines"].append(idx)
                continue

            if _is_sentence_or_quote_start(cleaned_line, start_pos):
                continue

            if t_low in stop_words:
                continue

            unmapped_occurrences.setdefault(token, []).append(idx)

    # Aggregate unmapped terms
    unmapped_terms: List[Dict[str, Any]] = []
    for term, line_nums in unmapped_occurrences.items():
        unique_lines = sorted(list(set(line_nums)))
        unmapped_terms.append({
            "term": term,
            "count": len(line_nums),
            "lines": unique_lines,
        })
    unmapped_terms.sort(key=lambda x: (-x["count"], x["term"]))

    # Aggregate mapped lore terms
    mapped_lore_terms: List[Dict[str, Any]] = []
    for term, data in mapped_lore_dict.items():
        unique_lines = sorted(list(set(data["lines"])))
        mapped_lore_terms.append({
            "term": term,
            "mapped_to": data["mapped_to"],
            "count": len(data["lines"]),
            "lines": unique_lines,
        })
    mapped_lore_terms.sort(key=lambda x: (-x["count"], x["term"]))

    report: Dict[str, Any] = {
        "file_path": resolved_target,
        "total_lines": len(lines),
        "heteronyms": heteronyms,
        "unmapped_terms": unmapped_terms,
        "mapped_lore_terms": mapped_lore_terms,
    }
    return report, None


def print_audio_prep_report(report: Dict[str, Any]) -> None:
    """Prints a clean Rich/ASCII audit report of TTS heteronyms and unmapped terms."""
    file_path = report.get("file_path", "<unknown>")
    total_lines = report.get("total_lines", 0)
    heteronyms = report.get("heteronyms", [])
    unmapped = report.get("unmapped_terms", [])
    mapped_lore = report.get("mapped_lore_terms", [])

    try:
        from rich.console import Console
        from rich.table import Table
        from rich.panel import Panel

        console = Console()
        console.print(
            Panel(
                f"[bold cyan]Audio Narration Pre-Flight Audit[/bold cyan]\n"
                f"Target: [bold white]{file_path}[/bold white] ({total_lines} lines)\n"
                f"Heteronyms Flagged: [yellow]{len(heteronyms)}[/yellow] | "
                f"Unmapped Terms: [red]{len(unmapped)}[/red] | "
                f"Mapped Lore Terms: [green]{len(mapped_lore)}[/green]",
                border_style="cyan",
            )
        )

        # 1. Heteronyms Table
        if heteronyms:
            t_het = Table(
                title="TTS Heteronyms Audit (Potential Mispronunciations)",
                border_style="yellow",
            )
            t_het.add_column("Line", style="cyan", justify="right", width=6)
            t_het.add_column("Word", style="bold yellow", width=12)
            t_het.add_column("YAML Mapping Status", style="green", width=24)
            t_het.add_column("Context Snippet", style="dim", overflow="fold")

            for h in heteronyms:
                status = (
                    f"[green]Mapped: '{h['mapped_to']}'[/green]"
                    if h.get("mapped_to")
                    else "[red]Unmapped[/red]"
                )
                snippet = h.get("snippet", "")
                if len(snippet) > 80:
                    snippet = snippet[:77] + "..."
                t_het.add_row(str(h["line"]), h["word"], status, snippet)
            console.print(t_het)
        else:
            console.print("[green]No English TTS heteronyms detected.[/green]")

        # 2. Unmapped Terms Table
        if unmapped:
            t_unm = Table(
                title="Unmapped Proper Nouns & Italicized Lore Terms",
                border_style="red",
            )
            t_unm.add_column("Term", style="bold red", width=24)
            t_unm.add_column("Count", style="cyan", justify="right", width=6)
            t_unm.add_column("Lines", style="dim", overflow="fold")

            for u in unmapped:
                lines_str = ", ".join(str(l) for l in u["lines"][:10])
                if len(u["lines"]) > 10:
                    lines_str += f" (+{len(u['lines']) - 10} more)"
                t_unm.add_row(u["term"], str(u["count"]), lines_str)
            console.print(t_unm)
        else:
            console.print("[green]No unmapped proper nouns or lore terms detected.[/green]")

        # 3. Mapped Lore Terms
        if mapped_lore:
            t_map = Table(
                title="Active Pronunciation Mappings Detected", border_style="green"
            )
            t_map.add_column("Lore Term", style="bold green", width=24)
            t_map.add_column("Pronunciation", style="cyan", width=24)
            t_map.add_column("Count", justify="right", width=6)
            for m in mapped_lore[:15]:
                t_map.add_row(m["term"], str(m.get("mapped_to", "")), str(m["count"]))
            console.print(t_map)

    except Exception:
        # Fallback to plain ASCII
        print(f"=== Audio Prep Report: {file_path} ({total_lines} lines) ===")
        print(f"Heteronyms ({len(heteronyms)}):")
        for h in heteronyms:
            status = f"Mapped: '{h['mapped_to']}'" if h.get("mapped_to") else "UNMAPPED"
            print(f"  Line {h['line']}: {h['word']} [{status}] -> {h.get('snippet', '')[:60]}")
        print(f"\nUnmapped Proper Nouns / Lore Terms ({len(unmapped)}):")
        for u in unmapped:
            print(f"  {u['term']} (count: {u['count']}) -> Lines: {u['lines']}")
