"""
Prose Linter & Anti-Slop Audit Engine for SR6 Quarto Campaign Chapters.
Checks banned AI buzzwords, cognitive buffer verbs, throat-clearer openers, em-dash density, and formatting.
"""

import os
import re
import sys
import subprocess
from typing import Dict, Any, List, Tuple, Optional

BANNED_WORDS = [
    "delve", "foster", "leverage", "utilize", "facilitate", "empower",
    "streamline", "robust", "cutting-edge", "paradigm shift", "game changer",
    "this is huge", "this changes everything", "tapestry", "realm", "beacon",
    "multifaceted", "meticulous", "intricate", "paramount", "transformative",
    "elevate", "embark", "supercharge", "harness", "ever-evolving"
]

COGNITIVE_VERBS = ["realized", "felt", "decided", "noticed"]

THROAT_CLEARERS = [
    "here's the thing", "here's what i mean", "let me be clear",
    "i'll be honest", "the uncomfortable truth is", "at the end of the day",
    "when it comes to", "at its core", "in today's world"
]


def run_markdownlint(file_path: str) -> Tuple[List[str], Optional[str]]:
    try:
        cmd = ["npx", "markdownlint-cli", file_path]
        res = subprocess.run(cmd, capture_output=True, text=True, shell=True)
        if res.returncode == 0:
            return [], None
        else:
            errors = [line.strip() for line in res.stdout.splitlines() + res.stderr.splitlines() if line.strip() and "npm warn" not in line]
            return errors, None
    except Exception as e:
        return [], f"Markdownlint note: {e}"


def analyze_prose(file_path: str) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
    if not os.path.exists(file_path):
        return None, f"File not found: {file_path}"

    with open(file_path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    text_content = []
    in_code = False
    for line in lines:
        if line.strip().startswith("```") or line.strip().startswith("#|"):
            in_code = not in_code
            continue
        if in_code or line.strip().startswith("<") or line.strip().startswith("#"):
            continue
        text_content.append(line)

    clean_prose = "".join(text_content)
    words = re.findall(r'\b\w+\b', clean_prose)
    word_count = len(words)

    if word_count == 0:
        return None, "File contains no prose text to analyze."

    em_dashes = len(re.findall(r'—|--', clean_prose))
    em_dash_density = (em_dashes / word_count) * 300 if word_count > 0 else 0

    banned_matches = []
    for line_idx, line in enumerate(lines, 1):
        line_lower = line.lower()
        for bw in BANNED_WORDS:
            if re.search(r'\b' + re.escape(bw) + r'\b', line_lower):
                banned_matches.append((line_idx, bw, line.strip()))

    cognitive_matches = []
    for line_idx, line in enumerate(lines, 1):
        line_lower = line.lower()
        for cv in COGNITIVE_VERBS:
            if re.search(r'\b' + re.escape(cv) + r'\b', line_lower):
                cognitive_matches.append((line_idx, cv, line.strip()))

    throat_matches = []
    for line_idx, line in enumerate(lines, 1):
        line_lower = line.lower()
        for tc in THROAT_CLEARERS:
            if tc in line_lower:
                throat_matches.append((line_idx, tc, line.strip()))

    binary_patterns = [
        r'\bnot\b.*?\bbut\b',
        r'\bno longer\b.*?\bit was\b',
        r'\bthere was no\b.*?\bthere was only\b'
    ]
    binary_matches = []
    for line_idx, line in enumerate(lines, 1):
        if line.strip().startswith("#") or line.strip().startswith("<"):
            continue
        line_lower = line.lower()
        for pat in binary_patterns:
            if re.search(pat, line_lower):
                binary_matches.append((line_idx, line.strip()))
                break

    sentences = [s.strip() for s in re.split(r'[.!?]+', clean_prose) if s.strip()]
    sentence_lengths = [len(re.findall(r'\b\w+\b', s)) for s in sentences if len(re.findall(r'\b\w+\b', s)) > 0]
    avg_sentence_len = sum(sentence_lengths) / len(sentence_lengths) if sentence_lengths else 0

    md_errors, md_err_note = run_markdownlint(file_path)

    report = {
        "file_path": file_path,
        "word_count": word_count,
        "em_dash_count": em_dashes,
        "em_dash_density_per_300": round(em_dash_density, 2),
        "avg_sentence_length": round(avg_sentence_len, 1),
        "banned_matches": banned_matches,
        "cognitive_matches": cognitive_matches,
        "throat_matches": throat_matches,
        "binary_matches": binary_matches,
        "markdownlint_errors": md_errors,
        "markdownlint_note": md_err_note
    }
    return report, None


def print_prose_report(report: Dict[str, Any]):
    print("=" * 65)
    print(f" PROSE LINTER & NO-AI-SLOP AUDIT REPORT")
    print(f" File: {report['file_path']}")
    print("=" * 65)
    print(f" Word Count: {report['word_count']}")
    print(f" Avg Sentence Length: {report['avg_sentence_length']} words")
    print(f" Em-Dashes: {report['em_dash_count']} (Density: {report['em_dash_density_per_300']} per 300 words)")
    if report['em_dash_density_per_300'] > 1.0:
        print("  [WARN] Em-dash density exceeds 1.0 per 300 words!")
    else:
        print("  [OK] Em-dash density is clean.")

    print("\n--- MARKDOWNLINT ERRORS ---")
    if report['markdownlint_errors']:
        for err_msg in report['markdownlint_errors']:
            print(f"  [MARKDOWNLINT ERROR] {err_msg}")
    else:
        print("  [OK] Zero markdownlint formatting errors detected.")

    print("\n--- BANNED BUZZWORDS ---")
    if report['banned_matches']:
        for line_no, word, snippet in report['banned_matches']:
            print(f"  Line {line_no} [{word}]: \"{snippet}\"")
    else:
        print("  [OK] Zero banned buzzwords detected.")

    print("\n--- COGNITIVE BUFFER VERBS ---")
    if report['cognitive_matches']:
        for line_no, word, snippet in report['cognitive_matches']:
            print(f"  Line {line_no} [{word}]: \"{snippet}\"")
    else:
        print("  [OK] Zero cognitive buffer verbs detected.")

    print("\n--- THROAT-CLEARING OPENERS ---")
    if report['throat_matches']:
        for line_no, phrase, snippet in report['throat_matches']:
            print(f"  Line {line_no} [{phrase}]: \"{snippet}\"")
    else:
        print("  [OK] Zero throat-clearing openers detected.")

    print("\n--- BINARY CONTRASTS ('Not X, but Y') ---")
    if report['binary_matches']:
        for line_no, snippet in report['binary_matches']:
            print(f"  Line {line_no}: \"{snippet}\"")
    else:
        print("  [OK] Zero binary contrasts detected.")

    print("=" * 65 + "\n")
