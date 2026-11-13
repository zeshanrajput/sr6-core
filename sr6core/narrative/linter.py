"""
Prose Linter & Anti-Slop Audit Engine for SR6 Quarto Campaign Chapters.
Checks banned AI buzzwords, cognitive buffer verbs, throat-clearer openers, em-dash density, and formatting.
"""

import os
import re
import sys
import math
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
            raw_errors = [
                line.strip()
                for line in res.stdout.splitlines() + res.stderr.splitlines()
                if line.strip() and "npm warn" not in line
            ]
            errors = [
                line for line in raw_errors
                if "MD013" not in line
                and not ("MD033" in line and "[Element: audio]" in line)
            ]
            return errors, None
    except Exception as e:
        return [], f"Markdownlint note: {e}"


def split_paragraph_into_sentences(para_text: str) -> List[str]:
    text = para_text.strip()
    if not text:
        return []
    # Protect common abbreviations and titles from premature splitting
    for h in ["Mr.", "Mrs.", "Ms.", "Dr.", "Prof.", "Capt.", "Lt.", "Col.", "Gen.", "Sgt.", "Sr.", "Jr."]:
        text = text.replace(h + " ", h[:-1] + "@DOT@ ")

    pattern = r'(?:(?<=[.!?])|(?<=[.!?]["*\u201d\u2019\']))\s+(?=[A-Z0-9"*\u201c\u2018`])'
    splits = [s.strip().replace("@DOT@", ".") for s in re.split(pattern, text) if s.strip()]
    return splits if splits else [para_text.strip()]


def _extract_file_tokens(filepath: str) -> List[str]:
    try:
        with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
            lines = f.readlines()
    except Exception:
        return []
    text_content = []
    in_code = False
    for line in lines:
        s = line.strip()
        if s.startswith("```") or s.startswith("#|"):
            in_code = not in_code
            continue
        if in_code or s.startswith("<") or s.startswith("#"):
            continue
        text_content.append(s)
    clean_text = " ".join(text_content).lower()
    return re.findall(r'[a-z]{3,}', clean_text)


def _build_valid_3grams(tokens: List[str]) -> List[str]:
    tg = []
    for i in range(len(tokens) - 2):
        w1, w2, w3 = tokens[i], tokens[i + 1], tokens[i + 2]
        valid_words = sum(1 for w in (w1, w2, w3) if w not in PROXIMITY_STOP_WORDS and len(w) >= 4)
        if valid_words >= 2:
            tg.append(f"{w1} {w2} {w3}")
    return tg


TIER_BENCHMARKS: Dict[int, Dict[str, Any]] = {
    1: {"label": "Tier 1 (Keystone)", "min_words": 2000, "target_words": "2,500–4,500+", "passing_score": 9.0, "min_braided_ratio": 45.0},
    2: {"label": "Tier 2 (Standard Scene)", "min_words": 1000, "target_words": "1,200–2,500", "passing_score": 8.5, "min_braided_ratio": 35.0},
    3: {"label": "Tier 3 (Micro-Slice / Vignette)", "min_words": 400, "target_words": "500–1,000", "passing_score": 8.0, "min_braided_ratio": 25.0},
}

CLUSTER_SATURATION_STOP_WORDS = PROXIMITY_STOP_WORDS | {
    "here", "into", "over", "back", "down", "only", "even", "them", "they",
    "have", "been", "were", "like", "make", "made", "take", "took", "look",
    "eyes", "hand", "face", "head", "time", "still", "first", "last", "long",
    "little", "thing", "much", "well", "many", "good", "very", "such", "also",
    "most", "both", "through", "where", "away", "came", "come", "went", "going",
    "want", "tell", "told", "felt", "feel", "kept", "keep", "left", "right",
    "must", "need", "used", "seem", "seemed", "word",
}


def _infer_char_id_from_path(file_path: str) -> Optional[str]:
    norm = file_path.replace("\\", "/")
    m = re.search(r'(?:^|/)characters/(?:lab/)?([^/]+)/', norm)
    if m and m.group(1) != "lab":
        return m.group(1)
    return None


def _load_voice_spec_cliches(char_id: Optional[str]) -> List[str]:
    if not char_id:
        return []
    try:
        from sr6core.narrative.sync import resolve_character_dir
        char_dir = resolve_character_dir(char_id)
    except Exception:
        char_dir = None
    if not char_dir:
        return []
    voice_spec = char_dir / "reference" / "voice_spec.md"
    if not voice_spec.exists():
        return []
    try:
        raw_lines = voice_spec.read_text(encoding="utf-8").splitlines()
    except Exception:
        return []

    cliches: List[str] = []
    in_banned = False
    banned_indent = 0
    for line in raw_lines:
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        indent = len(line) - len(line.lstrip())
        if stripped.startswith("banned_cliches:"):
            in_banned = True
            banned_indent = indent
            continue
        if in_banned:
            if indent <= banned_indent and not stripped.startswith("-"):
                in_banned = False
                continue
            if stripped.startswith("- "):
                item = stripped[2:].strip()
                # Extract quoted phrase when present, skipping meta instructions
                qm = re.match(r'^"([^"]+)"', item) or re.match(r"^'([^']+)'", item)
                phrase = qm.group(1) if qm else item
                phrase = re.sub(r'\.\.\.$', '', phrase).strip()
                lower_p = phrase.lower()
                if not phrase or "used as" in lower_p or "crutches" in lower_p or "[" in phrase:
                    continue
                cliches.append(phrase)
    return cliches


def analyze_prose(
    file_path: str,
    window: int = 3,
    tier: Optional[int] = None,
    char_id: Optional[str] = None,
) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
    is_file = os.path.exists(file_path) and os.path.isfile(file_path)
    if is_file:
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

    # Ellipses count & gate
    ellipses_matches = re.findall(r'\.{3,}|…', clean_prose)
    ellipses_count = len(ellipses_matches)
    ellipses_per_300 = round((ellipses_count / word_count) * 300, 2) if word_count > 0 else 0.0
    ellipses_valid = bool(ellipses_per_300 <= 0.60)

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

    # Cluster Saturation Alerts (>= 4 occurrences of a 4+ letter content word within 250 tokens)
    cluster_saturation_alerts: List[Dict[str, Any]] = []
    word_positions: Dict[str, List[int]] = {}
    for idx, (_l_no, w_low, _raw_w, _snip) in enumerate(token_stream):
        if len(w_low) < 4 or w_low in CLUSTER_SATURATION_STOP_WORDS:
            continue
        word_positions.setdefault(w_low, []).append(idx)

    for w_low, idxs in word_positions.items():
        if len(idxs) < 4:
            continue
        best_count = 0
        best_start_pos = 0
        best_end_pos = 0
        r = 0
        for l in range(len(idxs)):
            while r + 1 < len(idxs) and idxs[r + 1] - idxs[l] <= 250:
                r += 1
            cnt = r - l + 1
            if cnt >= 4 and cnt > best_count:
                best_count = cnt
                best_start_pos = l
                best_end_pos = r
        if best_count >= 4:
            cluster_saturation_alerts.append({
                "word": w_low,
                "count": best_count,
                "window_tokens": idxs[best_end_pos] - idxs[best_start_pos] + 1,
                "line_start": token_stream[idxs[best_start_pos]][0],
                "line_end": token_stream[idxs[best_end_pos]][0],
            })
    cluster_saturation_alerts.sort(key=lambda x: (x["count"], -x["window_tokens"]), reverse=True)

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

    if sentence_lengths and avg_sentence_len > 0:
        sentence_len_std = math.sqrt(sum((x - avg_sentence_len) ** 2 for x in sentence_lengths) / len(sentence_lengths))
        burstiness_cv = round(sentence_len_std / avg_sentence_len, 2)
    else:
        sentence_len_std = 0.0
        burstiness_cv = 0.0

    # Paragraph Braiding & Multi-Speaker Detection
    paragraphs: List[Tuple[int, str]] = []
    current_para_lines: List[str] = []
    current_para_start: int = 0
    in_code_block = False
    in_frontmatter = False

    for line_idx, line in enumerate(lines, 1):
        s = line.strip()
        if line_idx == 1 and s.startswith("---"):
            in_frontmatter = True
            continue
        if in_frontmatter:
            if s.startswith("---"):
                in_frontmatter = False
            continue

        if s.startswith("```") or s.startswith("#|"):
            in_code_block = not in_code_block
            if current_para_lines:
                p_text = " ".join(current_para_lines).strip()
                if p_text:
                    paragraphs.append((current_para_start, p_text))
                current_para_lines = []
                current_para_start = 0
            continue

        if in_code_block:
            continue

        if not s or s.startswith(("#", "<", "---", ":::", "{%")):
            if current_para_lines:
                p_text = " ".join(current_para_lines).strip()
                if p_text:
                    paragraphs.append((current_para_start, p_text))
                current_para_lines = []
                current_para_start = 0
            continue

        if not current_para_lines:
            current_para_start = line_idx
        current_para_lines.append(s)

    if current_para_lines:
        p_text = " ".join(current_para_lines).strip()
        if p_text:
            paragraphs.append((current_para_start, p_text))

    paragraph_count = len(paragraphs)
    braided_paragraph_count = 0
    single_sentence_paragraphs: List[Tuple[int, str]] = []

    for p_start, p_text in paragraphs:
        p_sents = split_paragraph_into_sentences(p_text)
        n_sents = len(p_sents)
        if 3 <= n_sents <= 6:
            braided_paragraph_count += 1
        elif n_sents == 1:
            single_sentence_paragraphs.append((p_start, p_text))

    braided_ratio = round((braided_paragraph_count / paragraph_count) * 100, 1) if paragraph_count else 0.0
    single_sentence_per_1k = round((len(single_sentence_paragraphs) / word_count) * 1000, 2) if word_count else 0.0

    # Multi-speaker paragraph detection
    multi_speaker_paragraphs: List[Tuple[int, str]] = []
    dialogue_verbs = r'(?:said|sent|replied|asked|transmitted|murmured|whispered|muttered|growled|snapped|shouted|commanded|countered|called)'
    stop_names = {
        "The", "He", "She", "They", "It", "Then", "There", "When", "What", "Who", "Where",
        "Why", "How", "And", "But", "Or", "If", "As", "In", "On", "At", "To", "For", "With"
    }

    for start_line, p_text in paragraphs:
        # Check (a): acoustic speech AND mindspeech
        acoustic_quotes = re.findall(r'["“]([^"”]+)["”]', p_text)
        has_acoustic = any(len(re.findall(r'\b\w+\b', q)) >= 2 for q in acoustic_quotes)

        mindspeech_spans = re.findall(r'(?<!\*)\*([^*\n]+)\*(?!\*)', p_text)
        has_mindspeech = False
        for span in mindspeech_spans:
            s_clean = span.strip()
            w_list = re.findall(r'\b\w+\b', s_clean)
            if len(w_list) >= 4:
                has_mindspeech = True
                break
            if bool(re.search(r'[.?!]$', s_clean)) and len(w_list) >= 1:
                has_mindspeech = True
                break
            if bool(re.search(r'[,]$', s_clean)) and len(w_list) >= 2:
                has_mindspeech = True
                break

        if has_acoustic and has_mindspeech:
            multi_speaker_paragraphs.append((start_line, p_text))
            continue

        # Check (b): two or more separate quoted speech segments attributed to distinct capitalized speaker names
        if len(acoustic_quotes) >= 2:
            speakers = set()
            for m in re.finditer(rf'\b([A-Z][a-zA-Z0-9_-]+)\s+{dialogue_verbs}\b', p_text):
                name = m.group(1)
                if name not in stop_names:
                    speakers.add(name)
            for m in re.finditer(rf'\b{dialogue_verbs}\s+([A-Z][a-zA-Z0-9_-]+)\b', p_text):
                name = m.group(1)
                if name not in stop_names:
                    speakers.add(name)

            if len(speakers) >= 2:
                multi_speaker_paragraphs.append((start_line, p_text))

    # Cross-Chapter Echo Window
    cross_chapter_echoes = []
    if is_file and window > 0:
        base_name = os.path.basename(file_path)
        m_track = re.match(r'^(\d{1,3})[\s_-]+', base_name)
        if m_track:
            curr_track = int(m_track.group(1))
            dir_name = os.path.dirname(os.path.abspath(file_path))
            if os.path.isdir(dir_name):
                sibling_files = []
                for fname in sorted(os.listdir(dir_name)):
                    if fname == base_name:
                        continue
                    if not (fname.endswith(".md") or fname.endswith(".qmd")):
                        continue
                    sm = re.match(r'^(\d{1,3})[\s_-]+', fname)
                    if sm:
                        s_track = int(sm.group(1))
                        if (curr_track - window) <= s_track <= (curr_track - 1):
                            sibling_files.append((fname, os.path.join(dir_name, fname)))

                if sibling_files:
                    curr_tokens = re.findall(r'[a-z]{3,}', clean_prose.lower())
                    curr_3grams_list = _build_valid_3grams(curr_tokens)
                    curr_3gram_counts: Dict[str, int] = {}
                    for phrase in curr_3grams_list:
                        curr_3gram_counts[phrase] = curr_3gram_counts.get(phrase, 0) + 1

                    phrase_to_siblings: Dict[str, List[str]] = {p: [] for p in curr_3gram_counts}

                    for s_fname, s_path in sibling_files:
                        s_tokens = _extract_file_tokens(s_path)
                        s_3grams = set(_build_valid_3grams(s_tokens))
                        for phrase in curr_3gram_counts:
                            if phrase in s_3grams:
                                phrase_to_siblings[phrase].append(s_fname)

                    flagged = []
                    for phrase, cnt in curr_3gram_counts.items():
                        matched_sibs = phrase_to_siblings.get(phrase, [])
                        if len(matched_sibs) >= 2:
                            flagged.append({
                                "phrase": phrase,
                                "chapters": matched_sibs,
                                "count_in_current": cnt
                            })

                    flagged.sort(key=lambda x: (x["count_in_current"], len(x["chapters"])), reverse=True)
                    cross_chapter_echoes = flagged[:10]

    md_errors, md_err_note = run_markdownlint(file_path) if is_file else ([], None)

    unicode_artifact_matches = []
    for line_idx, line in enumerate(lines, 1):
        if '\ufffd' in line:
            unicode_artifact_matches.append((line_idx, line.strip()))

    buzzwords_found = [{"line": l, "word": w, "snippet": s} for l, w, s in banned_matches]
    cognitive_buffers_found = [{"line": l, "word": w, "snippet": s} for l, w, s in cognitive_matches]

    redlines: List[str] = []
    for l_no, w, snip in banned_matches:
        redlines.append(f"Line {l_no}: Forbidden buzzword or overage '{w}'.")

    for item, occs in tier1_overages.items():
        if len(occs) > tier1_allowance:
            redlines.append(f"High-salience cliché '{item}' exceeded quota ({len(occs)} found; allowance: {tier1_allowance}).")

    for rw, occs in tier2_overages.items():
        redlines.append(f"Rare vocabulary '{rw}' exceeded quota ({len(occs)} found; allowance: 1).")

    for echo in proximity_echoes:
        redlines.append(f"Proximity echo for '{echo['text']}' between lines {echo['line1']} and {echo['line2']} ({echo['distance']} words apart).")

    if not ellipses_valid:
        redlines.append(f"Ellipses density ({ellipses_per_300:.2f}/300 words) exceeds ceiling of 0.60 per 300 words.")

    for l_no, snip in unicode_artifact_matches:
        redlines.append(f"Line {l_no}: Corrupted unicode replacement character (\\ufffd).")

    for l_no, p_text in multi_speaker_paragraphs:
        redlines.append(f"Line {l_no}: Multi-speaker dialogue in single paragraph violates one-speaker-per-paragraph discipline.")

    resolved_char_id = char_id or (_infer_char_id_from_path(file_path) if is_file else None)
    tier_targets = TIER_BENCHMARKS.get(tier) if tier in TIER_BENCHMARKS else None
    tier_warnings: List[str] = []
    if tier_targets:
        if word_count < tier_targets["min_words"]:
            tier_warnings.append(
                f"{tier_targets['label']} word count ({word_count}) is below minimum benchmark "
                f"({tier_targets['min_words']}; target {tier_targets['target_words']})."
            )
        if braided_ratio < tier_targets["min_braided_ratio"]:
            tier_warnings.append(
                f"{tier_targets['label']} paragraph braiding ({braided_ratio}%) is below benchmark "
                f"({tier_targets['min_braided_ratio']}%)."
            )

    voice_spec_warnings: List[str] = []
    spec_cliches = _load_voice_spec_cliches(resolved_char_id)
    if spec_cliches:
        for line_idx, line in clean_lines:
            line_low = line.lower()
            for sc in spec_cliches:
                if sc.lower() in line_low:
                    voice_spec_warnings.append(
                        f"Line {line_idx} [{resolved_char_id} voice_spec]: Matched banned cliche '{sc}'."
                    )

    gates_passed = bool(
        len(banned_matches) == 0
        and len(tier1_overages) == 0
        and len(tier2_overages) == 0
        and len(proximity_echoes) == 0
        and ellipses_valid
        and len(unicode_artifact_matches) == 0
        and len(multi_speaker_paragraphs) == 0
    )

    report = {
        "file_path": file_path if is_file else "<raw_text>",
        "char_id": resolved_char_id,
        "tier": tier if tier in TIER_BENCHMARKS else None,
        "tier_targets": tier_targets,
        "tier_warnings": tier_warnings,
        "voice_spec_warnings": voice_spec_warnings,
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
        "cluster_saturation_alerts": cluster_saturation_alerts,
        "markdownlint_errors": md_errors,
        "markdownlint_note": md_err_note,
        "ellipses_count": ellipses_count,
        "ellipses_per_300": ellipses_per_300,
        "ellipses_valid": ellipses_valid,
        "buzzwords_found": buzzwords_found,
        "cognitive_buffers_found": cognitive_buffers_found,
        "paragraph_count": paragraph_count,
        "braided_paragraph_count": braided_paragraph_count,
        "braided_ratio": braided_ratio,
        "single_sentence_paragraphs": single_sentence_paragraphs,
        "single_sentence_per_1k": single_sentence_per_1k,
        "multi_speaker_paragraphs": multi_speaker_paragraphs,
        "sentence_len_std": round(sentence_len_std, 2),
        "burstiness_cv": burstiness_cv,
        "cross_chapter_echoes": cross_chapter_echoes,
        "redlines": redlines,
        "gates_passed": gates_passed,
    }
    return report, None


def print_prose_report(report: Dict[str, Any]):
    print("=" * 65)
    print(f" PROSE LINTER & NO-AI-SLOP AUDIT REPORT")
    print(f" File: {report['file_path']}")
    print("=" * 65)

    gates_passed = report.get("gates_passed", False)
    status_str = "[PASS] READY FOR PUBLICATION" if gates_passed else "[FAIL] REVISION REQUIRED"
    print(f" Editorial Status: {status_str}")

    print("\n--- EDITORIAL READINESS GATES ---")
    if gates_passed:
        print("  [PASS] All editorial readiness gates passed.")
    else:
        redlines = report.get("redlines", [])
        print(f"  [FAIL] Editorial gates triggered {len(redlines)} redline(s):")
        for r in redlines:
            print(f"    - {r}")

    print("\n--- CRAFT TELEMETRY PROFILE ---")
    print(f"  Word Count: {report['word_count']}")
    print(f"  Avg Sentence Length: {report['avg_sentence_length']} words")
    print(f"  Sentence Length Std Dev: {report.get('sentence_len_std', 0.0)}")
    print(f"  Sentence Burstiness (CV): {report.get('burstiness_cv', 0.0)}")
    ell_status = "[OK]" if report.get("ellipses_valid", True) else "[EXCEEDS BUDGET]"
    print(f"  Ellipses: {report.get('ellipses_count', 0)} ({report.get('ellipses_per_300', 0.0)} per 300 words, Budget: <= 0.60) {ell_status}")
    print(f"  Em-Dashes: {report['em_dash_count']} (Density: {report['em_dash_density_per_300']} per 300 words)")
    if report['em_dash_density_per_300'] > 1.0:
        print("    [WARN] Em-dash density exceeds 1.0 per 300 words!")
    else:
        print("    [OK] Em-dash density is clean.")

    para_cnt = report.get("paragraph_count", 0)
    braided_cnt = report.get("braided_paragraph_count", 0)
    braided_pct = report.get("braided_ratio", 0.0)
    print(f"  Paragraph Braiding: {braided_cnt} / {para_cnt} paragraphs ({braided_pct}% braided [3-6 sentences])")

    single_paras = report.get("single_sentence_paragraphs", [])
    single_rate = report.get("single_sentence_per_1k", 0.0)
    print(f"  Single-Sentence Paragraphs: {len(single_paras)} ({single_rate} per 1k words, Ceiling: <= 1-2 per 1k)")
    if single_paras:
        for l_no, p_text in single_paras[:5]:
            snippet = p_text[:70] + "..." if len(p_text) > 70 else p_text
            print(f"    - Line {l_no}: \"{snippet}\"")
        if len(single_paras) > 5:
            print(f"    ... and {len(single_paras) - 5} more.")

    multi_speakers = report.get("multi_speaker_paragraphs", [])
    if multi_speakers:
        print(f"  [MULTI-SPEAKER VIOLATIONS] {len(multi_speakers)} paragraph(s) contain multi-speaker dialogue:")
        for l_no, p_text in multi_speakers:
            snippet = p_text[:70] + "..." if len(p_text) > 70 else p_text
            print(f"    - Line {l_no}: \"{snippet}\"")
    else:
        print("  [OK] One-speaker-per-paragraph discipline maintained.")

    cross_echoes = report.get("cross_chapter_echoes", [])
    if cross_echoes:
        print(f"\n--- CROSS-CHAPTER ECHOES (Window: 3 preceding chapters) ---")
        for ce in cross_echoes:
            chaps = ", ".join(ce.get("chapters", []))
            print(f"  - '{ce['phrase']}' (found {ce.get('count_in_current', 1)}x in current chapter, echoes in: {chaps})")
    else:
        print("\n--- CROSS-CHAPTER ECHOES ---")
        print("  [OK] Zero cross-chapter recurring phrase echoes detected.")

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

    print("\n--- CLUSTER SATURATION ALERTS (>= 4 occurrences within 250 tokens) ---")
    cluster_alerts = report.get("cluster_saturation_alerts", [])
    if cluster_alerts:
        for ca in cluster_alerts:
            print(
                f"  [CLUSTER WARNING] '{ca['word']}': {ca['count']}x across {ca['window_tokens']} tokens "
                f"(Lines {ca['line_start']}-{ca['line_end']})"
            )
    else:
        print("  [OK] Zero lexical cluster saturation spikes detected.")

    if report.get("tier_targets") or report.get("char_id"):
        tier_targets = report.get("tier_targets")
        header = tier_targets["label"] if tier_targets else "Character Calibration"
        char_label = report.get("char_id") or "unspecified"
        print(f"\n--- TIER & VOICE CALIBRATION ({header} | Char: {char_label}) ---")
        if tier_targets:
            print(
                f"  Benchmark: {tier_targets['target_words']} words | "
                f"Passing >= {tier_targets['passing_score']}/10 | "
                f"Min Braiding >= {tier_targets['min_braided_ratio']}%"
            )
        tier_warns = report.get("tier_warnings", [])
        voice_warns = report.get("voice_spec_warnings", [])
        if tier_warns or voice_warns:
            for tw in tier_warns:
                print(f"  [TIER WARNING] {tw}")
            for vw in voice_warns:
                print(f"  [VOICE SPEC WARNING] {vw}")
        else:
            print("  [OK] Tier benchmarks and voice_spec rules satisfied.")

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
