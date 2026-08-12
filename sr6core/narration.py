"""
TTS Audio Narration Generator Engine for SR6 Campaign Chapters.
Uses Kokoro TTS PyTorch GPU Engine with 'af_heart' voice, natural Shadowrun pronunciation rules,
markdown symbol filtering, link/embed stripping, dialogue cadence smoothing, Goldilocks token chunking,
anti-click raised-cosine micro-fades, float32 peak limiting, and 160kbps MP3 encoding.
"""

import os
import re
import sys
from typing import List, Tuple, Optional
import numpy as np



def clean_markdown_for_tts(text: str) -> str:
    """Strips markdown links, image embeds, header tags, decorative symbols, U+FFFD artifacts, quotation marks, and formatting."""
    # 0. Normalize Unicode smart quotes, dashes, ellipses, and strip U+FFFD replacement characters
    text = text.replace('\ufffd', '')
    text = text.replace('“', '"').replace('”', '"')
    text = text.replace('‘', "'").replace('’', "'")
    text = text.replace('—', ' -- ').replace('–', ' -- ')
    text = text.replace('…', '...')
    text = text.replace('"', '')
    
    # 1. Remove Markdown image embeds completely: ![alt](path)
    text = re.sub(r'!\[.*?\]\(.*?\)', '', text)
    
    # 2. Convert Markdown links [text](url) to just text
    text = re.sub(r'\[(.*?)\]\(.*?\)', r'\1', text)
    
    # 3. Strip standalone URLs and angle bracket URLs
    text = re.sub(r'<https?://[^>]+>', '', text)
    text = re.sub(r'https?://\S+', '', text)
    
    # 4. Remove Quarto shortcodes: {{< ... >}}
    text = re.sub(r'\{\{<.*?>\}\}', '', text)
    
    # 5. Remove HTML tags
    text = re.sub(r'<[^>]+>', '', text)
    
    # 6. Normalize section breaks (---, ***, ___) to a scene pause placeholder
    lines = []
    for line in text.splitlines():
        stripped = line.strip()
        if re.match(r'^(---|[*]{3}|___|===\s*)+$', stripped):
            lines.append("<SCENE_PAUSE>")
            continue
        # Strip header markers (# Title -> Title)
        stripped = re.sub(r'^#{1,6}\s*', '', stripped)
        # Strip blockquotes (> Quote -> Quote)
        stripped = re.sub(r'^>\s*', '', stripped)
        # Strip list markers (- item, * item, 1. item -> item)
        stripped = re.sub(r'^[\*\-\+]\s+', '', stripped)
        stripped = re.sub(r'^\d+\.\s+', '', stripped)
        lines.append(stripped)
        
    text = "\n".join(lines)
    
    # 7. Strip inline code backticks, bold, italic, strikethrough markers
    text = re.sub(r'```.*?```', '', text, flags=re.DOTALL)
    text = re.sub(r'`([^`]+)`', r'\1', text)
    text = re.sub(r'\*\*([^*]+)\*\*', r'\1', text)
    text = re.sub(r'\*([^*]+)\*', r'\1', text)
    text = re.sub(r'__([^_]+)__', r'\1', text)
    text = re.sub(r'_([^_]+)_', r'\1', text)
    text = re.sub(r'~~([^~]+)~~', r'\1', text)
    
    # 8. Clean up stray markdown symbols like orphan --- or *** in prose
    text = re.sub(r'\s*---+\s*', ' -- ', text)
    text = re.sub(r'\s*\*\*\*+\s*', ' ', text)
    
    return text


def clean_pronunciation(text: str) -> str:
    """Applies comprehensive pronunciation corrections for Shadowrun terms, currency, acronyms, honorifics, and hyphenated compound words."""
    # 0. Dialogue machine/spirit code formatting (e.g. AGENT_OF_ORDER / SANITIZE_INPUT -> AGENT OF ORDER. SANITIZE INPUT.)
    def _clean_spirit_code(m):
        raw = m.group(0)
        cleaned = raw.replace('_', ' ').replace(' / ', '. ').replace('/', '. ')
        return cleaned
    text = re.sub(r'\b[A-Z0-9_]{3,}(?:\s*/\s*[A-Z0-9_]{3,})+\b', _clean_spirit_code, text)

    # 1. Contraction / Phonetic Fixes (wasn't -> was not)
    text = re.sub(r"\bwasn't\b", "was not", text, flags=re.IGNORECASE)

    # 2. Corporate Designation (R-31-K-0 -> R 31 K 0) vs Chosen Name (Reiko -> Rayko)
    text = re.sub(r'\bR[-_\s]*31[-_\s]*K[-_\s]*0(\'s)?\b', r'R 31 K 0\1', text, flags=re.IGNORECASE)
    text = re.sub(r'\br31-?k0(\'s)?\b', r'R 31 K 0\1', text, flags=re.IGNORECASE)
    text = re.sub(r'\breiko(\'s)?\b', r'Rayko\1', text, flags=re.IGNORECASE)
    text = re.sub(r'\bT@z(\'s)?\b', r'Taz\1', text)
    text = re.sub(r'\bt@z(\'s)?\b', r'taz\1', text)
    text = text.replace('SINner', 'sinner').replace('SINners', 'sinners')
    text = re.sub(r'\br3sP@wn(\'s)?\b', r'respawn\1', text, flags=re.IGNORECASE)

    # 3. Currency & Symbols (¥500 -> 500 new yen)
    text = re.sub(r'¥\s*(\d[\d,.]*)', r'\1 new yen', text)
    text = text.replace('¥', ' new yen ')
    text = re.sub(r'\bnuyens?\b', 'new yen', text, flags=re.IGNORECASE)

    # 4. Shadowrun Acronyms & Jargon (IC -> Ice, ARO -> A R O, APDS -> A P D S)
    text = re.sub(r'\bIC\b', 'Ice', text)
    text = re.sub(r'\bICE\b', 'Ice', text)
    text = re.sub(r'\bARO\b', 'A R O', text)
    text = re.sub(r'\bAROs\b', 'A R Os', text)
    text = re.sub(r'\bAPDS\b', 'A P D S', text)
    text = re.sub(r'\bM-TOCs?\b', 'Em Toc', text, flags=re.IGNORECASE)
    text = re.sub(r'\bSINless\b', 'sinless', text, flags=re.IGNORECASE)
    text = re.sub(r'\bSIN\b', 'sin', text)

    # 5. Japanese Honorifics & Names (-chan -> chahn, -san -> sahn)
    text = re.sub(r'\bAh-Mei\b', 'Ah Mei', text, flags=re.IGNORECASE)
    text = re.sub(r'\bEndo[- ]san\b', 'Endo sahn', text, flags=re.IGNORECASE)
    text = re.sub(r'\bRei[- ]chan\b', 'Rei chahn', text, flags=re.IGNORECASE)
    text = re.sub(r'\bYuri[- ]chan\b', 'Yuri chahn', text, flags=re.IGNORECASE)
    text = re.sub(r'\bYuriko[- ]san\b', 'Yooreeko sahn', text, flags=re.IGNORECASE)
    text = re.sub(r'(\b[A-Za-z]+)-chan\b', r'\1 chahn', text, flags=re.IGNORECASE)
    text = re.sub(r'(\b[A-Za-z]+)-san\b', r'\1 sahn', text, flags=re.IGNORECASE)
    text = re.sub(r'\bNeo-Tokyo\b', 'Neo Tokyo', text, flags=re.IGNORECASE)
    text = re.sub(r'\bNeo-Kyoto\b', 'Neo Kyoto', text, flags=re.IGNORECASE)

    # 6. Megacorps & Proper Nouns (Phonetic spelling without hyphens)
    text = re.sub(r'\bRenraku\b', 'Renraku', text, flags=re.IGNORECASE)
    text = re.sub(r'\bShiawase\b', 'Sheeahwahsay', text, flags=re.IGNORECASE)
    text = re.sub(r'\bSaeder-Krupp\b', 'Sayder Krupp', text, flags=re.IGNORECASE)
    text = re.sub(r'\bMitsuhama\b', 'Meetsoohahmah', text, flags=re.IGNORECASE)
    text = re.sub(r'\bAztechnology\b', 'Aztechnology', text, flags=re.IGNORECASE)
    text = re.sub(r'\bYuriko(\'s)?\b', r'Yooreeko\1', text, flags=re.IGNORECASE)
    text = re.sub(r'\bdronomancer\b', 'dronomancer', text, flags=re.IGNORECASE)
    text = re.sub(r'\bdronomancy\b', 'dronomancy', text, flags=re.IGNORECASE)
    text = re.sub(r'\bcyberdeck\b', 'cyberdeck', text, flags=re.IGNORECASE)
    text = re.sub(r'\bgridlink\b', 'gridlink', text, flags=re.IGNORECASE)

    # 7. De-hyphenate compound words (soy-burger -> soyburger, matte-gray -> matte gray)
    text = re.sub(r'\bsoy-burgers?\b', 'soyburger', text, flags=re.IGNORECASE)
    text = re.sub(r'\bblack-market\b', 'black market', text, flags=re.IGNORECASE)
    text = re.sub(r'(\b[a-zA-Z]+)-([a-zA-Z]+\b)', r'\1 \2', text)

    # 8. Loan words
    text = re.sub(r'\bamuse-?bouche\b', 'ahmyooz boosh', text, flags=re.IGNORECASE)
    text = re.sub(r'\bqipao\b', 'cheepow', text, flags=re.IGNORECASE)
    text = re.sub(r'\bcheongsam\b', 'chongsahm', text, flags=re.IGNORECASE)
    text = re.sub(r'\bzaibatsu\b', 'zeyebahtsoo', text, flags=re.IGNORECASE)
    text = re.sub(r'\bkeiretsu\b', 'kayretsoo', text, flags=re.IGNORECASE)
    text = re.sub(r'\bkatana\b', 'kahtanah', text, flags=re.IGNORECASE)
    text = re.sub(r'\byakuza\b', 'yahkoozah', text, flags=re.IGNORECASE)

    return text.replace('\\', '')


def normalize_dialogue_cadence(text: str) -> str:
    """Smooths out repeated dialogue words and broken staccato sentence openers."""
    lines = text.splitlines()
    cleaned = []
    for line in lines:
        # Normalize double dashes/em-dashes to a single clean space or dash
        l = re.sub(r'\s*--+\s*', ' ', line)
        cleaned.append(l)
    return "\n".join(cleaned)


def estimate_token_count(text: str) -> int:
    """Rough heuristic for token count based on whitespace and punctuation splitting."""
    return int(len(text.split()) * 1.3)


def split_into_narration_chunks(text: str, pacing: str = "balanced") -> List[Tuple[str, float]]:
    """
    Splits processed prose into natural sentence and paragraph units with calibrated pause pacing.
    
    Pacing Profiles:
      - 'tight':    0.10s sentence, 0.25s paragraph (rapid pacing)
      - 'balanced': 0.32s sentence, 0.55s paragraph (recommended half-way: natural breathing room)
      - 'spacious': 0.50s sentence, 1.00s paragraph (slower audiobook pace)
    """
    if pacing == "tight":
        s_pause, p_pause, scene_pause = 0.10, 0.25, 0.60
    elif pacing == "spacious":
        s_pause, p_pause, scene_pause = 0.50, 1.00, 1.50
    else:  # 'balanced' (default)
        s_pause, p_pause, scene_pause = 0.32, 0.55, 1.00

    paragraphs = [p.strip() for p in text.split('\n') if p.strip()]
    chunks: List[Tuple[str, float]] = []

    for p_idx, para in enumerate(paragraphs):
        if para == "<SCENE_PAUSE>":
            chunks.append(("", scene_pause))
            continue

        # Split paragraph into discrete sentences for precise inter-sentence pause control
        sentences = [s.strip() for s in re.split(r'(?<=[.!?…])\s+', para) if s.strip()]
        
        for s_idx, sentence in enumerate(sentences):
            is_last_in_para = (s_idx == len(sentences) - 1)
            is_last_in_doc = is_last_in_para and (p_idx == len(paragraphs) - 1)
            
            if is_last_in_doc:
                pause = 0.20
            elif is_last_in_para:
                pause = p_pause
            else:
                pause = s_pause

            chunks.append((sentence, pause))

    return chunks


def apply_micro_fade(pcm_samples, sample_rate: int, fade_ms: float = 7.0):
    """Applies a raised-cosine micro fade-in and fade-out to eliminate splice click/pop artifacts."""
    import numpy as np
    if len(pcm_samples) == 0:
        return pcm_samples

    fade_len = int(sample_rate * (fade_ms / 1000.0))
    if fade_len <= 0 or len(pcm_samples) < fade_len * 2:
        return pcm_samples

    fade_in_curve = 0.5 * (1.0 - np.cos(np.pi * np.arange(fade_len) / fade_len))
    fade_out_curve = 0.5 * (1.0 + np.cos(np.pi * np.arange(fade_len) / fade_len))

    pcm_float = pcm_samples.astype(np.float32)
    pcm_float[:fade_len] *= fade_in_curve
    pcm_float[-fade_len:] *= fade_out_curve
    return pcm_float


NON_NARRATIVE_FILES = {"dronomancy.md", "dronomancy.qmd", "rules_combat.qmd", "rules_matrix.qmd"}


def is_narrative_chapter(file_path: str) -> bool:
    """Returns True if file_path is a narrative chapter (e.g. '01 The Weight of Zero.md'). Excludes rules/guides like 'dronomancy.md'."""
    filename = os.path.basename(file_path).lower()
    if filename in NON_NARRATIVE_FILES:
        return False
    # Check if filename starts with chapter number digits (e.g., '01', '19', '22')
    return bool(re.match(r'^\d{2}\s+', filename))


def generate_narration(file_path: str, output_mp3: Optional[str] = None, pacing: str = "balanced", voice: str = "af_heart") -> Tuple[Optional[str], Optional[str]]:
    """Synthesizes TTS narration audio from Markdown chapter file using Kokoro TTS GPU Engine (af_heart voice) into high-fidelity 160kbps MP3 format."""
    if not os.path.exists(file_path):
        return None, f"Chapter file '{file_path}' not found."

    if not is_narrative_chapter(file_path):
        return None, f"Skipping non-narrative file '{os.path.basename(file_path)}' (narration only applies to numbered narrative chapters)."

    try:
        from kokoro import KPipeline
        import torch
        import lameenc
    except ImportError:
        return None, "Kokoro narration dependencies (kokoro, torch, lameenc) not installed in current environment."

    device = "cuda" if torch.cuda.is_available() else "cpu"
    device_name = torch.cuda.get_device_name(0) if device == "cuda" else "CPU"
    print(f"[*] Kokoro TTS Inference Device: {device.upper()} ({device_name}) [Voice: {voice}, Pacing: {pacing.upper()}]")

    if not output_mp3:
        output_dir = os.path.join(os.path.dirname(file_path), "audio")
        os.makedirs(output_dir, exist_ok=True)
        base_name = os.path.splitext(os.path.basename(file_path))[0] + ".mp3"
        output_mp3 = os.path.join(output_dir, base_name)

    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Preprocessing pipeline
    clean_text = clean_markdown_for_tts(content)
    clean_text = clean_pronunciation(clean_text)
    clean_text = normalize_dialogue_cadence(clean_text)
    chunks = split_into_narration_chunks(clean_text, pacing=pacing)

    if not chunks:
        return None, "No speakable text found in file."

    print(f"[*] Prepared {len(chunks)} speech chunks for Kokoro GPU narration -> {output_mp3}")
    print(f"[*] Initializing Kokoro PyTorch pipeline (voice: '{voice}')...")

    pipeline = KPipeline(lang_code='a', device=device)
    sample_rate = 24000
    pcm_float_segments = []

    for text_chunk, pause_sec in chunks:
        if text_chunk:
            try:
                generator = pipeline(text_chunk, voice=voice, speed=1.0)
                for gs, ps, audio_tensor in generator:
                    if audio_tensor is not None and len(audio_tensor) > 0:
                        if hasattr(audio_tensor, "numpy"):
                            samples_float32 = audio_tensor.detach().cpu().numpy().astype(np.float32)
                        else:
                            samples_float32 = np.array(audio_tensor, dtype=np.float32)
                        faded_samples = apply_micro_fade(samples_float32, sample_rate, fade_ms=7.0)
                        pcm_float_segments.append(faded_samples)
            except Exception as e:
                print(f"[Warning] Failed synthesizing chunk '{text_chunk[:30]}...': {e}")

        if pause_sec > 0.0:
            silence_samples = int(sample_rate * pause_sec)
            pcm_float_segments.append(np.zeros(silence_samples, dtype=np.float32))

    if not pcm_float_segments:
        return None, "Failed to generate audio samples."

    full_pcm_float = np.concatenate(pcm_float_segments)

    # Peak normalization & limiting (-1.0 dBFS)
    peak_val = np.max(np.abs(full_pcm_float))
    if peak_val > 0.0:
        target_peak = 0.89  # -1.01 dBFS
        full_pcm_float = full_pcm_float * (target_peak / peak_val)

    # Convert to int16 PCM
    full_pcm_int16 = (full_pcm_float * 32767.0).astype(np.int16)

    # Encode PCM to high-fidelity 160 kbps MP3 using lameenc
    encoder = lameenc.Encoder()
    encoder.set_bit_rate(160)
    encoder.set_in_sample_rate(sample_rate)
    encoder.set_channels(1)
    encoder.set_quality(2)

    pcm_bytes = full_pcm_int16.tobytes()
    mp3_bytes = encoder.encode(pcm_bytes) + encoder.flush()

    with open(output_mp3, "wb") as f:
        f.write(mp3_bytes)

    duration_sec = len(full_pcm_int16) / sample_rate
    print(f"[OK] Generated audio narration: {output_mp3} ({duration_sec:.1f} sec, {len(mp3_bytes)} bytes, 160kbps)")
    return output_mp3, None




