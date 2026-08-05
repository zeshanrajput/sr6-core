"""
TTS Audio Narration Generator Engine for SR6 Campaign Chapters.
Uses Sherpa-ONNX / Kokoro multi-lingual model with natural Shadowrun pronunciation rules.
"""

import os
import re
import sys
import tarfile
import urllib.request
from typing import Dict, Any, List, Tuple, Optional

MODEL_URL = "https://github.com/k2-fsa/sherpa-onnx/releases/download/tts-models/kokoro-multi-lang-v1_0.tar.bz2"
MODEL_DIR = "kokoro-multi-lang-v1_0"


def find_kokoro_model_dir() -> Optional[str]:
    """Resolves local directory path for Kokoro TTS models."""
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    search_dirs = [
        os.path.join(base_dir, "kokoro-multi-lang-v1_0"),
        os.path.join(base_dir, "kokoro-en-v0_19"),
        os.path.join(os.getcwd(), "kokoro-multi-lang-v1_0"),
        os.path.join(os.getcwd(), "kokoro-en-v0_19"),
        r"C:\GitHub\sr6-core\kokoro-multi-lang-v1_0",
        r"C:\GitHub\sr6-core\kokoro-en-v0_19",
        r"C:\GitHub\sr6yuriko\kokoro-multi-lang-v1_0",
        r"C:\GitHub\sr6yuriko\kokoro-en-v0_19",
    ]
    for candidate in search_dirs:
        if os.path.exists(candidate) and os.path.exists(os.path.join(candidate, "model.onnx")):
            return candidate
    return None


def clean_pronunciation(text: str) -> str:
    """Applies pronunciation corrections for Shadowrun terms."""
    text = re.sub(r'\br31-?k0\b', 'Rayko', text, flags=re.IGNORECASE)
    text = re.sub(r'\breiko\b', 'Rayko', text, flags=re.IGNORECASE)
    text = text.replace('T@z', 'Taz').replace('t@z', 'taz')
    text = text.replace('SINner', 'sinner').replace('SINners', 'sinners')
    text = re.sub(r'\bnuyens\b', 'new yens', text, flags=re.IGNORECASE)
    text = re.sub(r'\bnuyen\b', 'new yen', text, flags=re.IGNORECASE)
    text = re.sub(r'\br3sP@wn\b', 'respawn', text, flags=re.IGNORECASE)
    text = re.sub(r'\br3sp@wn\b', 'respawn', text, flags=re.IGNORECASE)
    return text.replace('\\', '')


def split_into_narration_chunks(text: str) -> List[Tuple[str, float]]:
    raw_tokens = re.split(r'((?<=[.!?…])\s+|(?<=[:;])\s+|(?<=[,])\s+)', text)
    chunks = []
    current_str = ""

    for token in raw_tokens:
        if not token:
            continue
        current_str += token
        stripped = current_str.strip()
        if not stripped:
            continue

        pause = 0.0
        if stripped.endswith('...') or stripped.endswith('…') or stripped.endswith('--'):
            pause = 0.35
        elif stripped.endswith('?') or stripped.endswith('!'):
            pause = 0.55
        elif stripped.endswith('.'):
            pause = 0.48
        elif stripped.endswith('"') or stripped.endswith('”'):
            pause = 0.35
        elif stripped.endswith(':') or stripped.endswith(';'):
            pause = 0.25
        elif stripped.endswith(','):
            pause = 0.18

        if pause > 0.0 or len(current_str) > 120:
            chunks.append((stripped, pause if pause > 0.0 else 0.30))
            current_str = ""

    if current_str.strip():
        chunks.append((current_str.strip(), 0.40))

    return chunks


def generate_narration(file_path: str, output_mp3: Optional[str] = None) -> Tuple[Optional[str], Optional[str]]:
    if not os.path.exists(file_path):
        return None, f"Chapter file '{file_path}' not found."

    model_dir = find_kokoro_model_dir()
    if not model_dir:
        return None, f"Kokoro model directory not found. Expected in sr6-core root ('kokoro-multi-lang-v1_0' or 'kokoro-en-v0_19')."

    try:
        import sherpa_onnx
        import numpy as np
        import lameenc
    except ImportError:
        return None, "TTS narration dependencies (sherpa-onnx, numpy, lameenc) not installed in current environment."

    if not output_mp3:
        output_mp3 = file_path.rsplit(".", 1)[0] + "_narration.mp3"

    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    lines = [line.strip() for line in content.splitlines() if line.strip() and not line.startswith("#") and not line.startswith("<")]
    prose = " ".join(lines)
    clean_prose = clean_pronunciation(prose)
    chunks = split_into_narration_chunks(clean_prose)

    print(f"[*] Found Kokoro TTS model at: {model_dir}")
    print(f"[*] Prepared {len(chunks)} speech chunks for narration rendering -> {output_mp3}")
    return output_mp3, None

