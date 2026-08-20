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
    "elevate", "embark", "supercharge", "harness", "ever-evolving",
    "ozone", "smell of ozone", "hot solder", "chemical tang of processing",
    "puddles of stale encryption", "decaying logic in the gutters",
    "systems redlining", "processing at 600%",
    "micro-geometry", "infernal symmetry", "unworldly gravity",
    "neurologically mapped", "evolutionary surrender", "micro-saccadic",
    "silver-chimed", "silvered in the upper registers"
]

COGNITIVE_VERBS = ["realized", "felt", "decided", "noticed"]

THROAT_CLEARERS = [
    "here's the thing", "here's what i mean", "let me be clear",
    "i'll be honest", "the uncomfortable truth is", "at the end of the day",
    "when it comes to", "at its core", "in today's world",
    "let that sink in", "make no mistake", "and that's okay",
    "full stop", "here's the problem though", "here's what i find interesting"
]

LORE_PREACH_PATTERNS = [
    r'\bmulti-million nuyen (?:marvel|asset|lungs|body|cage)\b',
    r'\balgorithmically (?:optimized|calculated)\b',
    r'\b(?:designed|calibrated) for (?:a|an) (?:megacorp|corporate) boardroom\b',
    r'\bmitsuhama spent \w+ years\b',
    r'\bcarrying a face that belongs to\b',
    r'\btwo distinct strangers, and he was the negative space\b'
]

SENSELESS_NEGATIVE_PATTERNS = [
    r'\bdid not look up\b',
    r'\bdid not look back\b',
    r'\bdid not say a word\b',
    r'\bdidn\'t look up\b',
    r'\bdidn\'t say a word\b',
    r'\bdid not hesitate\b',
    r'\bwithout hesitating\b',
    r'\bwithout looking up\b',
    r'\bwithout a word\b',
    r'\bwithout saying a word\b',
    r'\bnever looked up\b',
    r'\bnever said a word\b'
]

SCENT_TRIO_PATTERNS = [
    r'\bsmell(?:ed|s)? of [^,]+,\s*[^,]+,\s*and\s*[^.]+\b',
    r'\bodors? of [^,]+,\s*[^,]+,\s*and\s*[^.]+\b',
    r'\btaste(?:d|s)? of [^,]+,\s*[^,]+,\s*and\s*[^.]+\b'
]

OMNISCIENT_POV_PATTERNS = [
    r'\b[sS]?he knew (?:the|that|what|how|why|her|his)\b',
    r'\b[sS]?he had read (?:the|her|his|their)\b',
    r'\b[sS]?he had accepted (?:the|her|his|their)\b',
    r'\b[sS]?he was thinking\b',
    r'\b[sS]?he was waiting for the cue with\b'
]




def run_markdownlint(file_path: str) -> Tuple[List[str], Optional[str]]:
    try:
        # Check for .markdownlint.json in file's directory or repository roots
        dir_name = os.path.dirname(file_path)
        config_path = None
        current = dir_name
        while current and current != os.path.dirname(current):
            candidate = os.path.join(current, ".markdownlint.json")
            if os.path.exists(candidate):
                config_path = candidate
                break
            current = os.path.dirname(current)

        cmd = ["npx", "markdownlint-cli"]
        if config_path:
            cmd.extend(["--config", config_path])
        cmd.append(file_path)

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
        r'\bno longer\b.*?\b(?:it was|instead|rather)\b',
        r'\bthere was no\b.*?\bthere was only\b',
        r'\b(?:did not|was not|were not|could not|would not|had not|is not|are not|refused to|never)\b.*?\b(?:instead|rather)\b',
        r'\b(?:not because|not out of|not for|not to)\b.*?\b(?:but because|but out of|but for|but as|but to)\b',
        r'\bnot a\b.*?\b(?:not a|not an)\b.*?\ba\b',
        r'\bstops? being\b.*?\bstarts? being\b',
        r'\bceases? to be\b.*?\bbecomes?\b',
        r'\bnot just\b.*?\bbut (?:also|rather)\b',
        r'\b(?:isn\'t|wasn\'t) the problem\b.*?\bis\b'
    ]
    binary_matches = []
    for line_idx, line in enumerate(lines, 1):
        if line.strip().startswith("#") or line.strip().startswith("<") or line.strip().startswith("```"):
            continue
        line_lower = line.lower()
        for pat in binary_patterns:
            if re.search(pat, line_lower):
                binary_matches.append((line_idx, line.strip()))
                break

    # Multi-line & cross-sentence sliding window detection
    non_blank_lines = []
    for line_idx, line in enumerate(lines, 1):
        s = line.strip()
        if not s or s.startswith("#") or s.startswith("<") or s.startswith("```") or s.startswith("---"):
            continue
        non_blank_lines.append((line_idx, s))

    negation_starters = [
        r"^\s*(?:she|he|it|they|her\s+\w+|his\s+\w+|their\s+\w+|the\s+\w+)\s+(?:was not|were not|did not|could not|had not|is not|are not)\b",
        r"^\s*(?:there was no|there were no)\b",
        r"^\s*(?:it was not|this was not)\b",
    ]

    for i in range(len(non_blank_lines) - 1):
        prev_idx, prev_text = non_blank_lines[i]
        curr_idx, curr_text = non_blank_lines[i + 1]

        if curr_idx - prev_idx <= 3:
            combined = f"{prev_text} {curr_text}"
            combined_lower = combined.lower()

            negation_patterns = [
                r'\bdid not\b', r'\bwas not\b', r'\bwere not\b', r'\bcould not\b',
                r'\bwould not\b', r'\bhad not\b', r'\bnever\b', r'\bno longer\b',
                r'\bthere was no\b', r'\brefused to\b'
            ]
            pivot_patterns = [
                r'^\s*instead\b', r'^\s*rather\b', r'\binstead,\b', r'\brather,\b'
            ]

            has_negation = any(re.search(np, prev_text.lower()) for np in negation_patterns)
            has_pivot = any(re.search(pp, curr_text.lower()) for pp in pivot_patterns)

            if has_negation and has_pivot:
                already_reported = any(m[0] == prev_idx or m[0] == curr_idx for m in binary_matches)
                if not already_reported:
                    snippet = f"{prev_text} [Pivot:] {curr_text}"
                    binary_matches.append((prev_idx, snippet))
            else:
                # Check for split negative foil (e.g. "She was not X. Her form was Y.")
                prev_is_neg_starter = any(re.search(ns, prev_text, re.IGNORECASE) for ns in negation_starters)
                curr_is_direct_desc = re.search(r"^\s*(?:she|he|it|they|her|his|their|the\s+\w+)\s+(?:was|were|traveled|stood|opened|surged|materialized|held|lay)\b", curr_text, re.IGNORECASE)

                if prev_is_neg_starter and curr_is_direct_desc:
                    already_reported = any(m[0] == prev_idx or m[0] == curr_idx for m in binary_matches)
                    if not already_reported:
                        snippet = f"{prev_text} [Split contrast:] {curr_text}"
                        binary_matches.append((prev_idx, snippet))
                else:
                    for pat in binary_patterns:
                        if re.search(pat, combined_lower):
                            already_reported = any(m[0] == prev_idx or m[0] == curr_idx for m in binary_matches)
                            if not already_reported:
                                binary_matches.append((prev_idx, combined))
                                break

    lore_preach_matches = []
    for line_idx, line in enumerate(lines, 1):
        if line.strip().startswith("#") or line.strip().startswith("<") or line.strip().startswith("```"):
            continue
        line_lower = line.lower()
        for pat in LORE_PREACH_PATTERNS:
            if re.search(pat, line_lower):
                lore_preach_matches.append((line_idx, line.strip()))
                break

    senseless_negative_matches = []
    for line_idx, line in enumerate(lines, 1):
        if line.strip().startswith("#") or line.strip().startswith("<") or line.strip().startswith("```"):
            continue
        line_lower = line.lower()
        for pat in SENSELESS_NEGATIVE_PATTERNS:
            if re.search(pat, line_lower):
                senseless_negative_matches.append((line_idx, line.strip()))
                break

    scent_trio_matches = []
    for line_idx, line in enumerate(lines, 1):
        if line.strip().startswith("#") or line.strip().startswith("<") or line.strip().startswith("```"):
            continue
        line_lower = line.lower()
        for pat in SCENT_TRIO_PATTERNS:
            if re.search(pat, line_lower):
                scent_trio_matches.append((line_idx, line.strip()))
                break

    omniscient_pov_matches = []
    for line_idx, line in enumerate(lines, 1):
        if line.strip().startswith("#") or line.strip().startswith("<") or line.strip().startswith("```"):
            continue
        line_lower = line.lower()
        for pat in OMNISCIENT_POV_PATTERNS:
            if re.search(pat, line_lower):
                omniscient_pov_matches.append((line_idx, line.strip()))
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
        "lore_preach_matches": lore_preach_matches,
        "senseless_negative_matches": senseless_negative_matches,
        "scent_trio_matches": scent_trio_matches,
        "omniscient_pov_matches": omniscient_pov_matches,
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

    print("\n--- BANNED BUZZWORDS & SENSORY CLICHES ---")
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

    print("\n--- LORE PREACH & META-EXPOSITION ---")
    if report['lore_preach_matches']:
        for line_no, snippet in report['lore_preach_matches']:
            print(f"  Line {line_no}: \"{snippet}\"")
    else:
        print("  [OK] Zero lore-preach or meta-exposition patterns detected.")

    print("\n--- SENSELESS NEGATIVES & NON-ACTIONS ---")
    if report["senseless_negative_matches"]:
        for line_idx, line in report["senseless_negative_matches"]:
            print(f"  Line {line_idx} [senseless negative]: \"{line}\"")
    else:
        print("  [OK] Zero senseless negative non-actions detected.")

    print("\n--- FORMULAIC SENSORY TRIOS ('Smelled of X, Y, and Z') ---")
    if report.get("scent_trio_matches"):
        for line_idx, line in report["scent_trio_matches"]:
            print(f"  Line {line_idx} [sensory trio]: \"{line}\"")
    else:
        print("  [OK] Zero formulaic sensory trios detected.")

    print("\n--- OMNISCIENT POV LEAKS (3rd Person Deep Limited) ---")
    if report.get("omniscient_pov_matches"):
        for line_idx, line in report["omniscient_pov_matches"]:
            print(f"  Line {line_idx} [omniscient leak]: \"{line}\"")
    else:
        print("  [OK] Zero omniscient POV leaks detected.")

    print("=" * 65 + "\n")
