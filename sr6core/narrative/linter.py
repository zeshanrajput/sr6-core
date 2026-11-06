"""
Prose Linter & Anti-Slop Audit Engine for SR6 Quarto Campaign Chapters.
Checks banned AI buzzwords, cognitive buffer verbs, throat-clearer openers, em-dash density, and formatting.
"""

import os
import re
import sys
import subprocess
from typing import Dict, Any, List, Tuple, Optional

# Tier 0: Hard Banned (Corporate Buzzwords & AI Filler Idioms - Quota: 0)
TIER0_HARD_BANNED = [
    "delve", "foster", "leverage", "utilize", "facilitate", "empower",
    "streamline", "robust", "cutting-edge", "paradigm shift", "game changer",
    "this is huge", "this changes everything", "realm", "beacon",
    "multifaceted", "meticulous", "paramount", "transformative",
    "elevate", "embark", "supercharge", "harness", "ever-evolving"
]

BANNED_WORDS = TIER0_HARD_BANNED
BANNED_BUZZWORDS = TIER0_HARD_BANNED

# Tier 1: High-Salience Sensory Clichés (Quota: 1 per 3,000 words; subsequent occurrences flagged)
TIER1_SENSORY_CLICHES = [
    "smell of ozone", "ozone", "burnt copper", "taste of copper", "hot solder",
    "chemical tang of processing", "puddles of stale encryption", "decaying logic in the gutters",
    "systems redlining", "processing at 600%", "logic loops in her head",
    "micro-geometry", "infernal symmetry", "unworldly gravity",
    "neurologically mapped", "evolutionary surrender", "micro-saccadic",
    "silver-chimed", "silvered in the upper registers",
    "tapestry", "mosaic", "intricate", "absolute"
]

# Tier 2: Non-Colloquial / Rare Lexicon Quota (Quota: 1 per chapter / file)
TIER2_RARE_WORDS = [
    "alluvial", "petrichor", "crepuscular", "susurrus", "palimpsest", "labyrinthine",
    "effulgence", "chiaroscuro", "chert", "iridescent", "gossamer", "liminal",
    "sepulchral", "miasma", "vertiginous", "tessellated", "punctate", "incandescent",
    "penumbra", "thalassic", "ossified", "calcified"
]

# Tier 3: Sensory Modifiers & Palette Density (Target: <= 3.5 per 1k words)
TIER3_SENSORY_WORDS = [
    "dark", "darkness", "cold", "sharp", "shadow", "silt", "hum", "hummed",
    "amber", "indigo", "crimson", "neon"
]

PROXIMITY_STOP_WORDS = {
    "the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for", "with",
    "from", "by", "of", "as", "into", "through", "over", "under", "her", "his",
    "their", "its", "my", "your", "our", "it", "she", "he", "they", "i", "you",
    "we", "was", "were", "is", "are", "be", "been", "being", "had", "have", "has",
    "did", "do", "does", "could", "would", "should", "that", "this", "these",
    "those", "then", "there", "when", "where", "why", "how", "all", "any", "both",
    "each", "few", "more", "most", "other", "some", "such", "than", "too", "very",
    "can", "will", "just", "about", "up", "down", "out", "off", "again", "further",
    "before", "after", "above", "below", "between", "not", "no", "nor", "so", "if",
    "while", "who", "whom", "which", "what", "reiko", "indo", "cleo", "aisling",
    "etain", "remy", "janie", "taz", "belle", "nagai", "bast", "brynne", "yuriko",
    "velvet", "venn", "three", "months", "someone", "didn", "don't", "didn't",
    "every", "against", "mother", "father", "toward", "towards", "around", "another",
    "across", "along", "behind", "beside", "without", "within", "inside", "outside",
    "onto", "upon", "underneath", "never", "always", "something", "anything", "nothing",
    "knows", "know", "turned", "said", "asked", "replied"
}

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
    if os.path.exists(file_path) and os.path.isfile(file_path):
        with open(file_path, "r", encoding="utf-8") as f:
            lines = f.readlines()
    else:
        lines = [line + "\n" for line in file_path.splitlines()]

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

    # Build clean lines and token stream for lexical budget & echo analysis
    clean_lines = []
    token_stream = []
    for line_idx, line in enumerate(lines, 1):
        s = line.strip()
        if not s or s.startswith(("#", "<", "```", "---")):
            continue
        clean_lines.append((line_idx, line))
        for m in re.finditer(r'\b[a-zA-Z-]{2,}\b', line):
            token_stream.append((line_idx, m.group(0).lower(), m.group(0), line.strip()))

    # Tier 1: High-Salience Sensory Cliché Budget (Quota: 1 per 3,000 words)
    tier1_allowance = max(1, word_count // 3000)
    tier1_usage = {}
    tier1_overages = {}
    for item in TIER1_SENSORY_CLICHES:
        item_matches = []
        for line_idx, line in clean_lines:
            for _ in re.finditer(r'\b' + re.escape(item) + r'\b', line.lower()):
                item_matches.append((line_idx, line.strip()))
        if item_matches:
            tier1_usage[item] = item_matches
            if len(item_matches) > tier1_allowance:
                tier1_overages[item] = item_matches
                for l_idx, snip in item_matches[tier1_allowance:]:
                    banned_matches.append((l_idx, f"{item} [Quota Exceeded: {len(item_matches)}/{tier1_allowance}]", snip))

    # Tier 2: Non-Colloquial / Rare Lexicon Quota (Quota: 1 per chapter / file)
    tier2_overages = {}
    for rw in TIER2_RARE_WORDS:
        rw_matches = []
        for line_idx, line in clean_lines:
            for _ in re.finditer(r'\b' + re.escape(rw) + r'\b', line.lower()):
                rw_matches.append((line_idx, line.strip()))
        if len(rw_matches) > 1:
            tier2_overages[rw] = rw_matches

    # Tier 3: Sensory Modifiers & Palette Density (Target: <= 3.5 per 1k words)
    tier3_density_alerts = []
    counts_by_token = {}
    for _, tok_lower, _, _ in token_stream:
        counts_by_token[tok_lower] = counts_by_token.get(tok_lower, 0) + 1

    for sw in TIER3_SENSORY_WORDS:
        cnt = counts_by_token.get(sw, 0)
        if cnt >= 4:
            density = (cnt / word_count) * 1000 if word_count else 0
            if density > 3.5:
                tier3_density_alerts.append({
                    "word": sw,
                    "count": cnt,
                    "density": round(density, 1),
                    "target": 3.5
                })

    # Proximity Echo Detection (Bigrams <= 45 words, Content words <= 20 words)
    proximity_echoes = []
    seen_echo_bigrams = set()
    n_tokens = len(token_stream)

    for i in range(n_tokens - 1):
        w1, w2 = token_stream[i][1], token_stream[i + 1][1]
        # Skip if both are common stop words or too short
        # Require both words to be non-stop content words for descriptive bigrams
        if w1 in PROXIMITY_STOP_WORDS or w2 in PROXIMITY_STOP_WORDS:
            continue
        if len(w1) < 3 or len(w2) < 3:
            continue

        bg = (w1, w2)
        if bg in seen_echo_bigrams:
            continue

        for j in range(i + 1, min(i + 45, n_tokens - 1)):
            if (token_stream[j][1], token_stream[j + 1][1]) == bg:
                dist = j - i
                proximity_echoes.append({
                    "type": "bigram",
                    "text": f"{w1} {w2}",
                    "line1": token_stream[i][0],
                    "line2": token_stream[j][0],
                    "distance": dist,
                    "snippet1": token_stream[i][3],
                    "snippet2": token_stream[j][3]
                })
                seen_echo_bigrams.add(bg)
                break

    seen_echo_words = set()
    for i in range(n_tokens):
        w = token_stream[i][1]
        if w in PROXIMITY_STOP_WORDS or len(w) < 5:
            continue
        if w in seen_echo_words:
            continue

        for j in range(i + 2, min(i + 22, n_tokens)):
            if token_stream[j][1] == w:
                dist = j - i
                # Avoid duplicate reporting if already covered by a bigram echo on same lines
                if not any(e["type"] == "bigram" and w in e["text"] and e["line1"] == token_stream[i][0] for e in proximity_echoes):
                    proximity_echoes.append({
                        "type": "word",
                        "text": w,
                        "line1": token_stream[i][0],
                        "line2": token_stream[j][0],
                        "distance": dist,
                        "snippet1": token_stream[i][3],
                        "snippet2": token_stream[j][3]
                    })
                    seen_echo_words.add(w)
                break

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

    is_file = os.path.exists(file_path) and os.path.isfile(file_path)
    md_errors, md_err_note = run_markdownlint(file_path) if is_file else ([], None)

    unicode_artifact_matches = []
    for line_idx, line in enumerate(lines, 1):
        if '\ufffd' in line:
            unicode_artifact_matches.append((line_idx, line.strip()))

    report = {
        "file_path": file_path if is_file else "<raw_text>",
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
        "unicode_artifact_matches": unicode_artifact_matches,
        "tier1_cliche_usage": tier1_usage,
        "tier1_cliche_overages": tier1_overages,
        "tier1_allowance": tier1_allowance,
        "tier2_rare_overages": tier2_overages,
        "tier3_density_alerts": tier3_density_alerts,
        "proximity_echoes": proximity_echoes,
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

    print("\n--- TIER 1: HIGH-SALIENCE CLICHÉ BUDGET (Quota: 1 per 3,000 words) ---")
    tier1_usage = report.get("tier1_cliche_usage", {})
    tier1_allowance = report.get("tier1_allowance", 1)
    if tier1_usage:
        for item, occs in tier1_usage.items():
            if len(occs) > tier1_allowance:
                print(f"  [EXCEEDED QUOTA] '{item}' ({len(occs)} found; Allowance: {tier1_allowance}):")
                for l_no, snip in occs:
                    print(f"    - Line {l_no}: \"{snip}\"")
            else:
                lines_str = ", ".join(str(o[0]) for o in occs)
                print(f"  [OK] '{item}': {len(occs)} / {tier1_allowance} allowed (Line {lines_str})")
    else:
        print("  [OK] Zero high-salience sensory clichés detected.")

    print("\n--- TIER 2: RARE VOCABULARY BUDGET (Allowance: 1 per chapter) ---")
    tier2_overages = report.get("tier2_rare_overages", {})
    if tier2_overages:
        for rw, occs in tier2_overages.items():
            print(f"  [EXCEEDED QUOTA] '{rw}' ({len(occs)} found; Allowance: 1):")
            for l_no, snip in occs:
                print(f"    - Line {l_no}: \"{snip}\"")
    else:
        print("  [OK] Zero rare vocabulary quota overages detected.")

    print("\n--- TIER 3: SENSORY PALETTE DENSITY (Target: <= 3.5 per 1k words) ---")
    tier3_alerts = report.get("tier3_density_alerts", [])
    if tier3_alerts:
        for alert in tier3_alerts:
            print(f"  [DENSITY ALERT] '{alert['word']}': {alert['count']} occurrences ({alert['density']} per 1k words; Target: <= {alert['target']})")
    else:
        print("  [OK] Sensory modifier density within healthy parameters.")

    print("\n--- PROXIMITY ECHO AUDIT (Separation: Bigrams <= 45 words, Content <= 20 words) ---")
    echoes = report.get("proximity_echoes", [])
    if echoes:
        for echo in echoes:
            if echo["type"] == "bigram":
                print(f"  [PROXIMITY ECHO] Line {echo['line1']} -> Line {echo['line2']} ({echo['distance']} words): Bigram '{echo['text']}'")
            else:
                print(f"  [PROXIMITY ECHO] Line {echo['line1']} -> Line {echo['line2']} ({echo['distance']} words): Word '{echo['text']}'")
    else:
        print("  [OK] Zero proximity echoes detected.")

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

    print("\n--- UNICODE CORRUPTION ARTIFACTS (\\ufffd) ---")
    if report.get("unicode_artifact_matches"):
        for line_idx, line in report["unicode_artifact_matches"]:
            print(f"  Line {line_idx} [corrupted char]: \"{line}\"")
    else:
        print("  [OK] Zero corrupted unicode replacement characters detected.")

    print("=" * 65 + "\n")
