"""
Narrative Context Synchronization Engine for SR6 Character Portfolios.
Synchronizes chapter registries across _quarto.yml, index.qmd, and reference/story_continuity.md,
ensuring clean chapter ordering, audio tag alignment, entity appearance indexing, and zero unicode corruption artifacts.
"""

import os
import re
import urllib.parse
from pathlib import Path
from typing import Dict, Any, List, Tuple, Optional, Set


def derive_entity_tokens(raw_name: str) -> List[str]:
    """Derives precise search tokens from an entity or construct name for prose matching."""
    cleaned = re.sub(r'[*`_]', '', raw_name).strip()

    # Skip macro / generic rows that should not auto-index against broad text
    if any(k in cleaned.lower() for k in ["corporate tie", "regional dossiers", "megacorps", "megacorporate"]):
        return []

    # Special-cased known multi-entities or constructs
    if "aisling" in cleaned.lower() and ("étaín" in cleaned.lower() or "etain" in cleaned.lower()):
        return ["Aisling", "Étaín", "Etain"]

    if "~" in cleaned:
        return ["~", "Tilde"]

    if "river people" in cleaned.lower():
        return ["River People", "Mississippi Renovation"]

    if "resonance realms" in cleaned.lower():
        return ["Resonance Realms", "UnITy"]

    if "man-at-arms" in cleaned.lower():
        return ["Man-at-Arms", "Goshintai"]

    if "seattle shadow chapters" in cleaned.lower():
        return ["Seattle Shadow Chapters", "Shadow Chapters"]

    if "takahashi satomi" in cleaned.lower():
        return ["Takahashi Satomi", "Satomi"]

    if "ni ni xiaolu" in cleaned.lower():
        return ["Ni Ni Xiaolu", "Xiaolu"]

    if "liao fa ren" in cleaned.lower():
        return ["Liao Fa Ren", "Fa Ren"]

    if "sigrûn" in cleaned.lower() or "sigrun" in cleaned.lower():
        return ["Sigrûn", "Sigrun"]

    tokens = set()

    # Extract parenthetical content (e.g. ("The Curator") or (Suzuki Ken))
    parens = re.findall(r'\((.*?)\)', cleaned)
    for p in parens:
        p_clean = re.sub(r'["\']', '', p).strip()
        if p_clean and not re.search(r'\b(connection|loyalty|tier|archive)\b', p_clean, re.IGNORECASE):
            tokens.add(p_clean)
            no_title = re.sub(r'^(?:Mr\.|Ms\.|The)\s+', '', p_clean).strip()
            if no_title:
                tokens.add(no_title)

    # Base part without parentheticals
    base = re.sub(r'\(.*?\)', '', cleaned).strip()
    parts = re.split(r'[/&]', base)
    stop_words = {
        "the", "mct", "tie", "host", "mind", "peer", "will", "van", "doc", "web", "tea",
        "river", "people", "resonance", "realms", "tradition", "shamanism", "chapters",
        "shadow", "corp", "corps", "man", "arms"
    }

    for part in parts:
        part_clean = re.sub(r'["\']', '', part).strip()
        if not part_clean:
            continue
        no_title = re.sub(r'^(?:Mr\.|Ms\.|The)\s+', '', part_clean).strip()
        if no_title:
            tokens.add(no_title)
        tokens.add(part_clean)

        words = no_title.split()
        if len(words) == 2:
            w1, w2 = words[0], words[1]
            if len(w1) >= 3 and w1.lower() not in stop_words:
                tokens.add(w1)
            if len(w2) >= 3 and w2.lower() not in stop_words:
                tokens.add(w2)

    res = [t for t in tokens if t == "~" or len(t) >= 2]
    return sorted(res, key=lambda x: -len(x))


def is_chapter_referenced(cm: Dict[str, Any], cell: str) -> bool:
    """Checks whether a chapter track or filename is already referenced in an appearances cell."""
    t = cm['track']
    if cm['filename'] in cell or urllib.parse.quote(cm['filename'], safe='') in cell:
        return True
    pattern = rf'\[0*{t}(?:[_\s-][^\]]*)?\]\('
    if re.search(pattern, cell):
        return True
    if re.search(rf'\b(?:Chapter|Ch\.?)\s+0*{t}\b', cell, re.IGNORECASE):
        return True
    return False


def matches_entity_in_prose(tokens: List[str], text: str) -> bool:
    """Checks if any entity search token matches within chapter prose using word boundaries."""
    for tok in tokens:
        if tok == "~":
            if "`~`" in text or re.search(r'(?:`~`|(?<=\s)~(?:[\s.,;:!?\)]|$))', text):
                return True
        else:
            if re.search(rf'\b{re.escape(tok)}\b', text):
                return True
    return False


def process_continuity_table(
    table_lines: List[str],
    chapters_meta: List[Dict[str, Any]],
    chapter_prose: Dict[str, str],
    section_name: str,
    char_id: str
) -> Tuple[List[str], List[Dict[str, Any]]]:
    """Auto-indexes entity appearances in a single Section 1 or Section 2 markdown table."""
    if len(table_lines) < 2:
        return table_lines, []

    header_line = table_lines[0]
    sep_line = table_lines[1]
    data_lines = table_lines[2:]

    header_cols = [c.strip() for c in header_line.split("|")[1:-1]]
    app_col_idx = -1
    for idx, col in enumerate(header_cols):
        if re.match(r'^(?:Key\s+)?Chapter\s+Appearances$', col, re.IGNORECASE):
            app_col_idx = idx
            break

    if app_col_idx == -1:
        # Table does not track chapter appearances (e.g. Focus & Narrative Anchor, File Appearances)
        return table_lines, []

    # Detect style across data lines: Style A ([03](...)) vs Style B ([03_dark_wings.md](...))
    style = "filename"
    for row in data_lines:
        cols = [c.strip() for c in row.split("|")[1:-1]]
        if app_col_idx < len(cols):
            cell = cols[app_col_idx]
            if re.search(r'\[\d{2}\]\(file://', cell):
                style = "track"
                break
            elif re.search(r'\[[^\]]+\.(?:md|qmd)\]\(file://', cell):
                style = "filename"
                break

    new_data_lines = []
    links_added = []

    for row in data_lines:
        cols = [c.strip() for c in row.split("|")[1:-1]]
        if len(cols) <= app_col_idx:
            new_data_lines.append(row)
            continue

        entity_name_raw = cols[0]
        cell_appearances = cols[app_col_idx]

        # Skip rows marked as Archive or Throughout Anthology
        if re.search(r'\bArchive\b', row, re.IGNORECASE):
            new_data_lines.append(row)
            continue

        if 'throughout anthology' in cell_appearances.lower():
            new_data_lines.append(row)
            continue

        # Skip macro rows with no chapter links
        if re.search(r'\bMacro\b', row, re.IGNORECASE) and not re.search(r'\[.*?\]\(file://', cell_appearances):
            new_data_lines.append(row)
            continue

        # Skip rows where appearance cell has no links and is not a 'none logged' placeholder
        if not re.search(r'\[.*?\]\(file://', cell_appearances) and not re.search(r'none logged', cell_appearances, re.IGNORECASE):
            new_data_lines.append(row)
            continue

        tokens = derive_entity_tokens(entity_name_raw)
        if not tokens:
            new_data_lines.append(row)
            continue

        clean_entity_name = re.sub(r'[*`_]', '', entity_name_raw).strip()

        new_links = []
        for cm in chapters_meta:
            if is_chapter_referenced(cm, cell_appearances):
                continue
            prose = chapter_prose.get(cm["filename"], "")
            if matches_entity_in_prose(tokens, prose):
                abs_chap_posix = cm['path'].resolve().as_posix()
                if re.match(r'^[A-Z]:', abs_chap_posix):
                    abs_chap_posix = abs_chap_posix[0].lower() + abs_chap_posix[1:]
                encoded_uri = urllib.parse.quote(abs_chap_posix, safe=':/')

                if style == "track":
                    link = f"[{cm['track']:02d}](file:///{encoded_uri})"
                else:
                    link = f"[{cm['filename']}](file:///{encoded_uri})"

                new_links.append(link)
                links_added.append({
                    "entity": clean_entity_name,
                    "track": cm["track"],
                    "chapter": cm["filename"],
                    "section": section_name
                })

        if not new_links:
            new_data_lines.append(row)
            continue

        if re.search(r'none logged(?: in narrative chapters)?', cell_appearances, re.IGNORECASE):
            new_cell = re.sub(
                r'none logged(?: in narrative chapters)?',
                ", ".join(new_links),
                cell_appearances,
                count=1,
                flags=re.IGNORECASE
            )
        else:
            link_matches = list(re.finditer(r'\[[^\]]+\]\([^)]+\)', cell_appearances))
            if link_matches:
                end_pos = link_matches[-1].end()
                new_cell = cell_appearances[:end_pos] + ", " + ", ".join(new_links) + cell_appearances[end_pos:]
            else:
                new_cell = cell_appearances + ", " + ", ".join(new_links)

        cols[app_col_idx] = new_cell
        new_data_lines.append(f"| {' | '.join(cols)} |\n")

    return [header_line, sep_line] + new_data_lines, links_added


def update_continuity_entity_tables(
    cont_text: str,
    chapters_meta: List[Dict[str, Any]],
    chapter_prose: Dict[str, str],
    char_id: str
) -> Tuple[str, List[Dict[str, Any]]]:
    """Updates entity and construct appearances in Section 1 and Section 2 of story_continuity.md."""
    lines = cont_text.splitlines(keepends=True)
    output_lines = []
    entity_links_added = []
    in_target_section = False
    current_section_name = ""

    i = 0
    while i < len(lines):
        line = lines[i]
        sec_m = re.match(r'^##\s+([12])\.\s+(.*)$', line)
        if sec_m:
            in_target_section = True
            current_section_name = f"## {sec_m.group(1)}. {sec_m.group(2).strip()}"
            output_lines.append(line)
            i += 1
            continue

        if in_target_section and re.match(r'^##\s+', line):
            in_target_section = False
            current_section_name = ""
            output_lines.append(line)
            i += 1
            continue

        if in_target_section and line.startswith("|") and (i + 1 < len(lines)) and lines[i+1].startswith("|"):
            table_lines = []
            while i < len(lines) and lines[i].startswith("|"):
                table_lines.append(lines[i])
                i += 1

            processed, added = process_continuity_table(
                table_lines, chapters_meta, chapter_prose, current_section_name, char_id
            )
            entity_links_added.extend(added)
            output_lines.extend(processed)
            continue

        output_lines.append(line)
        i += 1

    return "".join(output_lines), entity_links_added


def check_bible_drift(char_dir: Path, chapters_meta: List[Dict[str, Any]]) -> List[str]:
    """Checks storyboard.md Post-Session Story Queue and voice_spec.md chapter_tiers for drift."""
    alerts = []

    # 1. storyboard.md Post-Session Story Queue
    storyboard_path = char_dir / "reference" / "storyboard.md"
    if storyboard_path.exists():
        sb_text = storyboard_path.read_text(encoding="utf-8", errors="replace")
        queue_m = re.search(r'##\s*(?:[IVXLCDM]+\.\s*)?Post-Session\s+Story\s+Queue.*?(?=\n##|\Z)', sb_text, re.DOTALL | re.IGNORECASE)
        if queue_m:
            queue_text = queue_m.group(0)
            queue_tracks = set(int(t) for t in re.findall(r'\bChapter\s+(\d{1,3})\b', queue_text, re.IGNORECASE))
            for cm in chapters_meta:
                if cm["track"] in queue_tracks:
                    alerts.append(
                        f"Chapter {cm['track']} ({cm['filename']}) exists on disk but is still listed in storyboard.md Post-Session Story Queue."
                    )

    # 2. voice_spec.md chapter_tiers
    voice_spec_path = char_dir / "reference" / "voice_spec.md"
    if voice_spec_path.exists():
        vs_text = voice_spec_path.read_text(encoding="utf-8", errors="replace")
        tiers_m = re.search(r'chapter_tiers:\s*\n(.*?)(?=\n\w|\n##|\Z)', vs_text, re.DOTALL)
        if tiers_m:
            tiers_text = tiers_m.group(1)
            registered_tracks = set(int(t) for t in re.findall(r'-\s*["\']?(\d{1,3})[\s_-]+', tiers_text))
            for cm in chapters_meta:
                if cm["track"] not in registered_tracks:
                    alerts.append(
                        f"Chapter {cm['track']} ({cm['filename']}) is not registered in voice_spec.md chapter_tiers."
                    )

    return alerts


def resolve_character_dir(target: str) -> Optional[Path]:
    """Resolves character directory from path, name, or character ID."""
    p = Path(target).resolve()
    if p.exists() and p.is_dir():
        if (p / "_quarto.yml").exists() or (p / "narrative").exists():
            return p
        for cand in ["characters/" + target, "characters/" + p.name, "characters/lab/" + target, "characters/lab/" + p.name]:
            cp = Path(cand).resolve()
            if cp.exists() and cp.is_dir():
                return cp

    cwd = Path.cwd()
    cand1 = cwd / "characters" / target
    if cand1.exists() and cand1.is_dir():
        return cand1
    cand1_lab = cwd / "characters" / "lab" / target
    if cand1_lab.exists() and cand1_lab.is_dir():
        return cand1_lab

    repo_root = Path(__file__).resolve().parent.parent.parent
    cand2 = repo_root / "characters" / target
    if cand2.exists() and cand2.is_dir():
        return cand2
    cand2_lab = repo_root / "characters" / "lab" / target
    if cand2_lab.exists() and cand2_lab.is_dir():
        return cand2_lab

    return None


def optimize_character_images(char_dir: Path) -> Dict[str, Any]:
    """Converts .jpg/.jpeg images in images/ to .webp and updates text references."""
    images_dir = char_dir / "images"
    if not images_dir.exists() or not images_dir.is_dir():
        return {"converted_images": [], "updated_ref_files": [], "bytes_saved": 0}

    converted_images: List[Dict[str, Any]] = []
    name_pairs: Set[Tuple[str, str]] = set()
    bytes_saved = 0

    jpeg_files = sorted(
        p for p in images_dir.rglob("*")
        if p.is_file() and p.suffix.lower() in (".jpg", ".jpeg")
    )

    if jpeg_files:
        from PIL import Image, ImageOps

        for img_path in jpeg_files:
            webp_path = img_path.with_suffix(".webp")
            old_size = img_path.stat().st_size
            with Image.open(img_path) as img:
                transposed = ImageOps.exif_transpose(img)
                if transposed.mode not in ("RGB", "RGBA"):
                    transposed = transposed.convert("RGB")
                transposed.save(webp_path, format="WEBP", quality=85, method=6)

            if not webp_path.exists() or webp_path.stat().st_size <= 0:
                raise RuntimeError(f"Failed to encode WebP image for {img_path}")

            new_size = webp_path.stat().st_size
            saved = old_size - new_size
            bytes_saved += saved
            img_path.unlink()

            name_pairs.add((img_path.name, webp_path.name))
            converted_images.append({
                "old": img_path.relative_to(char_dir).as_posix(),
                "new": webp_path.relative_to(char_dir).as_posix(),
                "old_bytes": old_size,
                "new_bytes": new_size,
                "bytes_saved": saved,
            })

    # Also ensure stale .jpg/.jpeg references matching existing .webp assets are rewritten
    for webp_path in images_dir.rglob("*.webp"):
        if webp_path.is_file():
            name_pairs.add((f"{webp_path.stem}.jpeg", webp_path.name))
            name_pairs.add((f"{webp_path.stem}.jpg", webp_path.name))

    updated_ref_files: List[str] = []
    if name_pairs:
        skip_dirs = {"_book", ".quarto", "site_libs", "output", "scratch"}
        variants: List[Tuple[str, str]] = []
        for old_name, new_name in sorted(name_pairs):
            cand_pairs = [
                (old_name, new_name),
                (old_name.replace(" ", "%20"), new_name.replace(" ", "%20")),
                (urllib.parse.quote(old_name, safe=""), urllib.parse.quote(new_name, safe="")),
            ]
            for old_v, new_v in cand_pairs:
                if old_v != new_v and (old_v, new_v) not in variants:
                    variants.append((old_v, new_v))

        for doc_path in sorted(char_dir.rglob("*")):
            if not doc_path.is_file() or doc_path.suffix.lower() not in (".md", ".qmd", ".yaml", ".yml"):
                continue
            rel_parts = set(doc_path.relative_to(char_dir).parts[:-1])
            if rel_parts & skip_dirs:
                continue

            original = doc_path.read_text(encoding="utf-8", errors="replace")
            updated = original
            for old_v, new_v in variants:
                if old_v in updated:
                    updated = updated.replace(old_v, new_v)

            if updated != original:
                doc_path.write_text(updated, encoding="utf-8")
                updated_ref_files.append(doc_path.relative_to(char_dir).as_posix())

    return {
        "converted_images": converted_images,
        "updated_ref_files": updated_ref_files,
        "bytes_saved": bytes_saved,
    }


def sync_narrative_context(target: str = ".") -> Tuple[Dict[str, Any], Optional[str]]:
    """
    Scans narrative chapters for a character and synchronizes:
      1. _quarto.yml (Narrative Log chapters list)
      2. index.qmd (Background & Campaign Narratives list)
      3. reference/story_continuity.md (Section 1 & 2 entity index, Section 3 chapter index & word counts)
      4. Auto-cleans any U+FFFD unicode corruption artifacts.
      5. Generates bible drift alerts against storyboard.md and voice_spec.md.
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
    chapter_prose = {}
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

        audio_m = re.search(r'<audio[^>]+src=(["\'])(?:.*?/)?(.*?\.mp3)\1', raw_text, re.IGNORECASE)
        audio_file = audio_m.group(2) if audio_m else None

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
        chapter_prose[cf.name] = raw_text

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

        has_narrative_log = any(re.search(r'part:\s*["\']Narrative Log["\']', l) for l in q_lines)

        if has_narrative_log:
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
        else:
            # Support multi-part layouts (e.g., "Out-of-Session Narratives") by appending missing chapters
            existing_q_files = set()
            for l in q_lines:
                m = re.match(r'^\s*-\s+' + re.escape(dir_rel_name) + r'/(.+?)\s*$', l)
                if m:
                    existing_q_files.add(m.group(1))

            missing_q_chapters = [cm for cm in chapters_meta if cm["filename"] not in existing_q_files]
            if missing_q_chapters:
                i = 0
                in_target_part = False
                while i < len(q_lines):
                    line = q_lines[i]
                    new_q_lines.append(line)
                    if re.search(r'part:\s*["\']Out-of-Session Narratives["\']', line):
                        in_target_part = True
                    elif in_target_part and re.match(r'^\s*-\s+' + re.escape(dir_rel_name) + r'/', line):
                        # Check if next line leaves the chapter list
                        next_is_entry = (i + 1 < len(q_lines)) and re.match(r'^\s*-\s+' + re.escape(dir_rel_name) + r'/', q_lines[i + 1])
                        if not next_is_entry:
                            indent = line[:len(line) - len(line.lstrip())]
                            for cm in missing_q_chapters:
                                new_q_lines.append(f"{indent}- {dir_rel_name}/{cm['filename']}")
                            narrative_chapters_written = True
                            in_target_part = False
                    elif in_target_part and re.search(r'^\s*-\s*part:', line):
                        in_target_part = False
                    i += 1
            else:
                new_q_lines = q_lines

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
    entity_links_added = []
    if continuity_file.exists():
        cont_text = continuity_file.read_text(encoding="utf-8", errors="replace")
        original_cont_text = cont_text
        if '\ufffd' in cont_text:
            cont_text = cont_text.replace('\ufffd', '')
            cleaned_unicode_files.append("reference/story_continuity.md")

        # 3a. Auto-index Section 1 & Section 2 entity tables
        cont_text, entity_links_added = update_continuity_entity_tables(
            cont_text, chapters_meta, chapter_prose, char_id
        )

        # 3b. Locate Section 3 table bounds
        table_start_m = re.search(r'(\|\s*Chapter File\s*\|\s*Title\s*\|\s*Word Count\s*\|\s*Status\s*\|\n\|\s*---\s*\|\s*---\s*\|\s*---\s*\|\s*---\s*\|\n)', cont_text)
        if table_start_m:
            table_header_end = table_start_m.end()
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

            existing_rows = {}
            for r in row_lines:
                m = re.search(r'\|\s*\[([^\]]+)\]', r)
                if m:
                    existing_rows[m.group(1)] = r

            new_table_rows = []
            for cm in chapters_meta:
                cname = cm["filename"]
                abs_chap_posix = cm['path'].resolve().as_posix()
                if re.match(r'^[A-Z]:', abs_chap_posix):
                    abs_chap_posix = abs_chap_posix[0].lower() + abs_chap_posix[1:]
                encoded_uri = urllib.parse.quote(abs_chap_posix, safe=':/')

                if cname in existing_rows:
                    row_str = existing_rows[cname]
                    parts = [p.strip() for p in row_str.split("|")]
                    if len(parts) >= 5:
                        # Fix broken legacy paths (e.g. sr6{char_id}/chapters/)
                        if f"sr6{char_id}/chapters/" in parts[1] or "sr6{char_id}/chapters/" in parts[1] or re.search(r'sr6(?:' + re.escape(char_id) + r'|\{char_id\})/chapters/', parts[1]):
                            parts[1] = f"[{cname}](file:///{encoded_uri})"
                        parts[3] = f"{cm['words']:,}"
                        new_table_rows.append(f"| {' | '.join(parts[1:-1])} |\n")
                    else:
                        new_table_rows.append(row_str)
                else:
                    rel_link = f"[{cm['filename']}](file:///{encoded_uri})"
                    new_table_rows.append(f"| {rel_link} | {cm['track']}. {cm['title']} | {cm['words']:,} | Verified |\n")

            # Update total word count line in rest_of_file
            rest_of_file = re.sub(
                r'\*\*Total Anthology Word Count:\*\*.*?(?=\n\n|\n---|\Z)',
                f"**Total Anthology Word Count:** {total_words:,} words across {len(chapters_meta)} chapters.",
                rest_of_file,
                flags=re.DOTALL
            )

            cont_text = cont_text[:table_header_end] + "".join(new_table_rows) + rest_of_file

        if cont_text != original_cont_text:
            continuity_file.write_text(cont_text, encoding="utf-8")
            if "reference/story_continuity.md" not in updated_files:
                updated_files.append("reference/story_continuity.md")

    # 4. Optimize JPEG gallery images -> WebP & rewrite markdown references
    image_optimization = optimize_character_images(char_dir)
    for ref_file in image_optimization.get("updated_ref_files", []):
        if ref_file not in updated_files:
            updated_files.append(ref_file)

    # 5. Check Bible Drift
    bible_drift_alerts = check_bible_drift(char_dir, chapters_meta)

    report = {
        "character_id": char_id,
        "character_dir": str(char_dir),
        "chapter_count": len(chapters_meta),
        "total_words": total_words,
        "chapters": chapters_meta,
        "updated_files": updated_files,
        "cleaned_unicode_files": list(set(cleaned_unicode_files)),
        "entity_links_added": entity_links_added,
        "image_optimization": image_optimization,
        "bible_drift_alerts": bible_drift_alerts,
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

    if report.get("entity_links_added"):
        print(f"\nAuto-Indexed Entity Appearances ({len(report['entity_links_added'])} added):")
        for item in report["entity_links_added"]:
            if isinstance(item, dict):
                print(f"  [LINKED] {item.get('entity')}: Track {item.get('track', '?')} ({item.get('chapter', '?')})")
            else:
                print(f"  [LINKED] {item}")

    if report.get("bible_drift_alerts"):
        print(f"\nBible Drift Alerts ({len(report['bible_drift_alerts'])}):")
        for alert in report["bible_drift_alerts"]:
            print(f"  [ALERT] {alert}")

    img_opt = report.get("image_optimization") or {}
    if img_opt.get("converted_images"):
        saved_kb = img_opt.get("bytes_saved", 0) / 1024.0
        print(f"\nImage Optimization (-> WebP, {saved_kb:.1f} KB saved):")
        for item in img_opt["converted_images"]:
            item_saved_kb = item.get("bytes_saved", 0) / 1024.0
            print(f"  [WEBP] {item['old']} -> {item['new']} ({item_saved_kb:.1f} KB saved)")

    print("\nChapter Index:")
    for ch in report.get("chapters", []):
        audio_tag = f" [audio: {ch['audio_file']}]" if ch.get("audio_file") else ""
        print(f"  Track {ch['track']:02d}: {ch['title']:<24} | {ch['words']:>5,} words | {ch['filename']}{audio_tag}")

    print("=" * 65 + "\n")
