#!/usr/bin/env python3
"""
Audio Asset Alignment Utility for SR6 Portfolios.

Ensures that narrative audio files referenced in markdown files (e.g., <audio controls src="audio/31 Grep.mp3">)
are correctly resolved and present in each character's narrative/audio directory, even if GitHub Release assets
were automatically sanitized (e.g., spaces replaced with dots: '31.Grep.mp3').
"""

import os
import re
import shutil
import sys
import urllib.parse
from pathlib import Path


def align_audio_assets(repo_root: Path = None) -> int:
    if repo_root is None:
        repo_root = Path.cwd()

    characters_dir = repo_root / "characters"
    audio_downloads_dir = repo_root / "audio_downloads"

    if not characters_dir.exists():
        print(f"[ERROR] Characters directory not found at {characters_dir}")
        return 1

    char_dirs = [d for d in characters_dir.iterdir() if d.is_dir() and (d / "narrative").exists()]
    if not char_dirs:
        print("[INFO] No characters with narrative directories found.")
        return 0

    aligned_count = 0
    missing_count = 0

    for cdir in char_dirs:
        char_id = cdir.name
        narrative_dir = cdir / "narrative"
        audio_dir = narrative_dir / "audio"
        audio_dir.mkdir(parents=True, exist_ok=True)

        # Scan all .md and .qmd files in narrative_dir
        for root, _, files in os.walk(narrative_dir):
            for file in files:
                if file.endswith((".md", ".qmd")):
                    fpath = Path(root) / file
                    try:
                        content = fpath.read_text(encoding="utf-8", errors="replace")
                    except Exception as e:
                        print(f"[WARN] Failed to read {fpath}: {e}")
                        continue

                    # Search for <audio ... src="audio/..." or src="...mp3"
                    audio_tags = re.findall(
                        r'<audio[^>]+src=["\'](?:.*?/)?([^"\']+\.mp3)["\']',
                        content,
                        re.IGNORECASE,
                    )

                    for raw_src in audio_tags:
                        decoded_name = urllib.parse.unquote(raw_src)
                        target_file = audio_dir / decoded_name

                        if not target_file.exists():
                            # Generate potential candidate filenames
                            # GitHub release assets convert spaces to dots
                            dot_name = decoded_name.replace(" ", ".")
                            candidates = [
                                audio_downloads_dir / decoded_name,
                                audio_downloads_dir / dot_name,
                                audio_downloads_dir / f"{char_id}_{decoded_name}",
                                audio_downloads_dir / f"{char_id}_{dot_name}",
                                audio_dir / dot_name,
                                audio_dir / f"{char_id}_{decoded_name}",
                                audio_dir / f"{char_id}_{dot_name}",
                            ]

                            resolved = False
                            for cand in candidates:
                                if cand.exists() and cand.is_file():
                                    try:
                                        shutil.copy2(cand, target_file)
                                        print(
                                            f"[ALIGNED] {char_id}: {cand.name} -> {target_file.name}"
                                        )
                                        aligned_count += 1
                                        resolved = True
                                        break
                                    except Exception as e:
                                        print(f"[WARN] Failed to copy {cand} to {target_file}: {e}")

                            if not resolved:
                                print(
                                    f"[MISSING] {char_id}: {decoded_name} (referenced in {file})"
                                )
                                missing_count += 1

                        # Also ensure literal raw_src exists if different from decoded_name (e.g., %20)
                        if decoded_name != raw_src and target_file.exists():
                            raw_target = audio_dir / raw_src
                            if not raw_target.exists():
                                try:
                                    shutil.copy2(target_file, raw_target)
                                    print(f"[ALIGNED URL] {char_id}: alias for {raw_src}")
                                except Exception:
                                    pass

                        # Ensure dot-separated version also exists as an alias for compatibility
                        dot_target = audio_dir / decoded_name.replace(" ", ".")
                        if (
                            dot_target.name != target_file.name
                            and target_file.exists()
                            and not dot_target.exists()
                        ):
                            try:
                                shutil.copy2(target_file, dot_target)
                            except Exception:
                                pass

    print(
        f"\nAudio alignment summary: {aligned_count} aligned/aliased, {missing_count} missing."
    )
    return 0


if __name__ == "__main__":
    sys.exit(align_audio_assets())
