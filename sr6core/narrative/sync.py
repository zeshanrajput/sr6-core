"""
Narrative Context Synchronization Engine for SR6 Character Portfolios.
Synchronizes chapter registries across _quarto.yml, index.qmd, and reference/story_continuity.md,
ensuring clean chapter ordering, audio tag alignment, and zero unicode corruption artifacts.
"""

import os
import re
from pathlib import Path
from typing import Dict, Any, List, Tuple, Optional


def resolve_character_dir(target: str) -> Optional[Path]:
    """Resolves character directory from path, name, or character ID."""
    p = Path(target).resolve()
    if p.exists() and p.is_dir():
        if (p / "_quarto.yml").exists() or (p / "narrative").exists():
            return p
        for cand in ["characters/" + target, "characters/" + p.name]:
            cp = Path(cand).resolve()
            if cp.exists() and cp.is_dir():
                return cp

    cwd = Path.cwd()
    cand1 = cwd / "characters" / target
    if cand1.exists() and cand1.is_dir():
        return cand1

    repo_root = Path(__file__).resolve().parent.parent.parent
    cand2 = repo_root / "characters" / target
    if cand2.exists() and cand2.is_dir():
        return cand2

    return None


def sync_narrative_context(target: str = ".") -> Tuple[Dict[str, Any], Optional[str]]:
    """
    Scans narrative chapters for a character and synchronizes:
      1. _quarto.yml (Narrative Log chapters list)
      2. index.qmd (Background & Campaign Narratives list)
      3. reference/story_continuity.md (Chapter breakdown table, total word count)
      4. Auto-cleans any U+FFFD unicode corruption artifacts.
    """
    char_dir = resolve_character_dir(target)
    if not char_dir:
        return {}, f"Could not resolve character directory from '{target}'."

    char_id = char_dir.name

    narrative_dir = char_dir / "narrative"
    if not narrative_dir.exists():
        narrative_dir = char_dir / "chapters"
    if not narrative_dir.exists():
        return {}, f"No narrative/ or chapters/ directory found in '{char_dir}'."

    dir_rel_name = narrative_dir.name

    chapter_files: List[Path] = []
    for f in narrative_dir.iterdir():
        if f.is_file() and (f.suffix in [".md", ".qmd"]):
            if re.match(r'^\d{1,3}[\s_-]+', f.name):
                chapter_files.append(f)

    if not chapter_files:
        return {}, f"No numbered narrative chapters found in '{narrative_dir}'."

    def get_track_num(p: Path) -> int:
        m = re.match(r'^(\d{1,3})[\s_-]+', p.name)
        return int(m.group(1)) if m else 999

    chapter_files.sort(key=get_track_num)

    chapters_meta = []
    total_words = 0
    cleaned_unicode_files = []

    for cf in chapter_files:
        track = get_track_num(cf)
        raw_text = cf.read_text(encoding="utf-8", errors="replace")
        
        # Check and clean U+FFFD
        if '\ufffd' in raw_text:
            cleaned_text = raw_text.replace('\ufffd', '')
            cf.write_text(cleaned_text, encoding="utf-8")
            cleaned_unicode_files.append(cf.name)
            raw_text = cleaned_text

        # Extract title from # Header
        title_m = re.search(r'^#\s+(.+)$', raw_text, re.MULTILINE)
        if title_m:
            title = title_m.group(1).strip()
            clean_title = re.sub(r'^\d{1,3}\.\s*', '', title)
        else:
            base_slug = cf.stem
            clean_title = re.sub(r'^\d{1,3}[\s_-]+', '', base_slug).replace('_', ' ').title()

        audio_m = re.search(r'<audio[^>]+src=["\'](?:.*?/)?([^"\']+\.mp3)["\']', raw_text, re.IGNORECASE)
        audio_file = audio_m.group(1) if audio_m else None

        words = len(re.findall(r'\b\w+\b', raw_text))
        total_words += words

        chapters_meta.append({
            "track": track,
            "filename": cf.name,
            "title": clean_title,
            "full_title": f"{track:02d}. {clean_title}" if not clean_title.startswith(f"{track}.") else clean_title,
            "words": words,
            "audio_file": audio_file,
            "path": cf
        })

    updated_files = []

    # 1. Update _quarto.yml
    quarto_file = char_dir / "_quarto.yml"
    if quarto_file.exists():
        q_text = quarto_file.read_text(encoding="utf-8", errors="replace")
        if '\ufffd' in q_text:
            q_text = q_text.replace('\ufffd', '')
            cleaned_unicode_files.append("_quarto.yml")

        q_lines = q_text.splitlines()
        new_q_lines = []
        in_narrative_log = False
        narrative_chapters_written = False

        i = 0
        while i < len(q_lines):
            line = q_lines[i]
            if re.search(r'part:\s*["\']Narrative Log["\']', line):
                in_narrative_log = True
                new_q_lines.append(line)
                i += 1
                if i < len(q_lines) and re.search(r'^\s*chapters:', q_lines[i]):
                    new_q_lines.append(q_lines[i])
                    indent = "        "
                    for cm in chapters_meta:
                        new_q_lines.append(f"{indent}- {dir_rel_name}/{cm['filename']}")
                    narrative_chapters_written = True
                    i += 1
                    # Skip existing chapter entries under narrative log
                    while i < len(q_lines) and re.match(r'^\s*-\s+' + re.escape(dir_rel_name) + r'/', q_lines[i]):
                        i += 1
                    continue
            elif in_narrative_log and re.search(r'^\s*-\s*part:', line):
                in_narrative_log = False
                new_q_lines.append(line)
                i += 1
            else:
                new_q_lines.append(line)
                i += 1

        if narrative_chapters_written:
            quarto_file.write_text("\n".join(new_q_lines) + "\n", encoding="utf-8")
            updated_files.append("_quarto.yml")

    # 2. Update index.qmd (Append any missing chapters without altering existing entries)
    index_file = char_dir / "index.qmd"
    if index_file.exists():
        idx_text = index_file.read_text(encoding="utf-8", errors="replace")
        if '\ufffd' in idx_text:
            idx_text = idx_text.replace('\ufffd', '')
            cleaned_unicode_files.append("index.qmd")

        idx_lines = idx_text.splitlines()
        new_idx_lines = []
        narrative_entries_seen = set()

        # Find existing referenced chapter filenames
        for line in idx_lines:
            m = re.search(r'\[(.*?)\]\((?:' + re.escape(dir_rel_name) + r'/)?([^)]+)\)', line)
            if m:
                narrative_entries_seen.add(m.group(2).strip())

        # Determine which chapters need to be appended
        missing_chapters = [cm for cm in chapters_meta if cm["filename"] not in narrative_entries_seen]

        if missing_chapters:
            # Find insertion point: after the last bullet in section 2
            in_section_2 = False
            last_bullet_idx = -1
            for idx, line in enumerate(idx_lines):
                if re.search(r'###\s+2\.\s+Background\s+&\s+Campaign\s+Narratives', line):
                    in_section_2 = True
                elif in_section_2 and line.startswith("###"):
                    break
                elif in_section_2 and line.strip().startswith("* **"):
                    last_bullet_idx = idx

            if last_bullet_idx != -1:
                insert_lines = []
                for mc in missing_chapters:
                    insert_lines.append(f"* **[{mc['track']}. {mc['title']}]({dir_rel_name}/{mc['filename']})**: Narrative chapter covering {mc['title']}.")
                
                idx_lines = idx_lines[:last_bullet_idx + 1] + insert_lines + idx_lines[last_bullet_idx + 1:]
                index_file.write_text("\n".join(idx_lines) + "\n", encoding="utf-8")
                updated_files.append("index.qmd")

    # 3. Update reference/story_continuity.md
    continuity_file = char_dir / "reference" / "story_continuity.md"
    if continuity_file.exists():
        cont_text = continuity_file.read_text(encoding="utf-8", errors="replace")
        if '\ufffd' in cont_text:
            cont_text = cont_text.replace('\ufffd', '')
            cleaned_unicode_files.append("reference/story_continuity.md")

        # Locate Section 3 table bounds
        table_start_m = re.search(r'(\|\s*Chapter File\s*\|\s*Title\s*\|\s*Word Count\s*\|\s*Status\s*\|\n\|\s*---\s*\|\s*---\s*\|\s*---\s*\|\s*---\s*\|\n)', cont_text)
        if table_start_m:
            table_header_end = table_start_m.end()
            # Find where table rows end (first blank line or line not starting with |)
            after_header = cont_text[table_header_end:]
            row_lines = []
            rest_of_file = ""
            lines_after = after_header.splitlines(keepends=True)
            for i, l in enumerate(lines_after):
                if l.startswith("|"):
                    row_lines.append(l)
                else:
                    rest_of_file = "".join(lines_after[i:])
                    break

            # Parse existing filenames in table
            existing_rows = {}
            for r in row_lines:
                m = re.search(r'\|\s*\[([^\]]+)\]', r)
                if m:
                    existing_rows[m.group(1)] = r

            new_table_rows = []
            for cm in chapters_meta:
                cname = cm["filename"]
                if cname in existing_rows:
                    # Update word count in existing row
                    row_str = existing_rows[cname]
                    # Replace word count column: | link | title | word count | status |
                    parts = [p.strip() for p in row_str.split("|")]
                    if len(parts) >= 5:
                        parts[3] = f"{cm['words']:,}"
                        new_table_rows.append(f"| {' | '.join(parts[1:-1])} |\n")
                    else:
                        new_table_rows.append(row_str)
                else:
                    rel_link = f"[{cm['filename']}](file:///c:/GitHub/sr6{char_id}/chapters/{cm['filename']})"
                    new_table_rows.append(f"| {rel_link} | {cm['track']}. {cm['title']} | {cm['words']:,} | Verified |\n")

            # Update total word count line in rest_of_file
            rest_of_file = re.sub(
                r'\*\*Total Anthology Word Count:\*\*.*?(?=\n\n|\n---|\Z)',
                f"**Total Anthology Word Count:** {total_words:,} words across {len(chapters_meta)} chapters.",
                rest_of_file,
                flags=re.DOTALL
            )

            new_cont_text = cont_text[:table_header_end] + "".join(new_table_rows) + rest_of_file
            continuity_file.write_text(new_cont_text, encoding="utf-8")
            updated_files.append("reference/story_continuity.md")

    report = {
        "character_id": char_id,
        "character_dir": str(char_dir),
        "chapter_count": len(chapters_meta),
        "total_words": total_words,
        "chapters": chapters_meta,
        "updated_files": updated_files,
        "cleaned_unicode_files": list(set(cleaned_unicode_files))
    }

    return report, None


def print_sync_report(report: Dict[str, Any]):
    print("=" * 65)
    print(" NARRATIVE CONTEXT SYNCHRONIZATION REPORT")
    print(f" Character : {report['character_id'].upper()} ({report['character_dir']})")
    print("=" * 65)
    print(f" Total Chapters Synchronized : {report['chapter_count']}")
    print(f" Total Anthology Word Count  : {report['total_words']:,} words")
    
    print("\nUpdated Project Files:")
    for uf in report.get("updated_files", []):
        print(f"  [OK] Updated {uf}")

    if report.get("cleaned_unicode_files"):
        print("\nCleaned Unicode Artifacts (\\ufffd):")
        for cf in report["cleaned_unicode_files"]:
            print(f"  [FIXED] Stripped replacement chars from {cf}")

    print("\nChapter Index:")
    for ch in report.get("chapters", []):
        audio_tag = f" [audio: {ch['audio_file']}]" if ch.get("audio_file") else ""
        print(f"  Track {ch['track']:02d}: {ch['title']:<24} | {ch['words']:>5,} words | {ch['filename']}{audio_tag}")

    print("=" * 65 + "\n")
