"""
Clean-Room Narrative Story Packet Assembler for SR6 Core.
Assembles focused creative packets for clean-room beat-by-beat narrative drafting,
firewalling out evaluation rubrics and scorecard policing while injecting character voice,
consecrated capital telemetry, preceding prose, beat outlines, callbacks, and rules context.
"""

import os
import re
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple

from sr6core.narrative.sync import resolve_character_dir


def _slice_voice_spec(char_dir: Path) -> str:
    """
    Extracts voice essence sections while firewalling out evaluation rubrics,
    scorecard policing, and benchmark thresholds.
    """
    vspec_path = char_dir / "reference" / "voice_spec.md"
    if not vspec_path.is_file():
        vspec_path = char_dir / "voice_spec.md"
    if not vspec_path.is_file():
        return "*No voice_spec.md found for character.*"

    text = vspec_path.read_text(encoding="utf-8")
    parts = re.split(r"(?m)(?=^##\s+)", text)
    if not parts:
        return text

    exclude_terms = [
        "tiered chapter architecture",
        "evaluation benchmarks",
        "scorecard",
        "audit",
    ]
    include_terms = [
        "mandate",
        "consecrated",
        "identity",
        "cognitive bias",
        "chronological growth arcs",
        "voice schema overrides",
        "technical vocabulary",
        "domain rules",
    ]

    allowed_domains = {"domain_1", "domain_4", "domain_5", "domain_6", "domain_7"}

    included_sections: List[str] = []

    # Include preamble / top header if present
    intro = parts[0].strip()
    if intro and not intro.startswith("##"):
        clean_intro = "\n".join(
            l for l in intro.splitlines() if "passing_threshold" not in l.lower()
        ).strip()
        if clean_intro:
            included_sections.append(clean_intro)

    for part in parts[1:]:
        hm = re.match(r"^##\s+(.+)$", part, re.MULTILINE)
        if not hm:
            continue
        heading = hm.group(1).strip()
        hl = heading.lower()

        # Hard exclusion of evaluation rubrics / tier scorecards
        if any(ex in hl for ex in exclude_terms):
            continue

        # Inclusion check
        if not any(inc in hl for inc in include_terms):
            continue

        # Strip any passing_threshold lines
        lines = [l for l in part.splitlines() if "passing_threshold" not in l.lower()]

        # Filter chronological growth arcs to keep only the latest arc block
        if "chronological growth arcs" in hl:
            arc_keys: List[str] = []
            in_arcs = False
            for l in lines:
                if "arc_chronology:" in l:
                    in_arcs = True
                    continue
                if in_arcs:
                    m = re.match(r"^  ([a-zA-Z0-9_]+):", l)
                    if m:
                        arc_keys.append(m.group(1))
                    elif re.match(r"^[^\s]", l) and l.strip() != "```":
                        in_arcs = False

            arc_candidates = [k for k in arc_keys if k.startswith("arc_")]
            last_arc = arc_candidates[-1] if arc_candidates else (arc_keys[-1] if arc_keys else None)

            if last_arc:
                filtered_lines: List[str] = []
                in_arcs = False
                include_curr = True
                for l in lines:
                    if "arc_chronology:" in l:
                        in_arcs = True
                        filtered_lines.append(l)
                        continue
                    if in_arcs:
                        m = re.match(r"^  ([a-zA-Z0-9_]+):", l)
                        if m:
                            include_curr = (m.group(1) == last_arc)
                        elif re.match(r"^[^\s]", l) and l.strip() != "```":
                            in_arcs = False
                            include_curr = True
                        if include_curr:
                            filtered_lines.append(l)
                    else:
                        filtered_lines.append(l)
                lines = filtered_lines

        # Filter technical vocabulary to keep authorized domains
        if "technical vocabulary" in hl or "domain rules" in hl:
            filtered_lines = []
            in_rules = False
            include_curr = True
            for l in lines:
                if "domain_vocabulary_rules:" in l:
                    in_rules = True
                    filtered_lines.append(l)
                    continue
                if in_rules:
                    m = re.match(r"^  ([a-zA-Z0-9_]+):", l)
                    if m:
                        rule_name = m.group(1).lower()
                        if rule_name.startswith("domain_"):
                            include_curr = any(rule_name.startswith(ad) for ad in allowed_domains)
                        else:
                            include_curr = True
                    elif re.match(r"^[^\s]", l) and l.strip() != "```":
                        in_rules = False
                        include_curr = True
                    if include_curr:
                        filtered_lines.append(l)
                else:
                    filtered_lines.append(l)
            lines = filtered_lines

        section_text = "\n".join(lines).strip()
        if section_text:
            included_sections.append(section_text)

    return "\n\n---\n\n".join(included_sections)


def _get_resource_pressure_snippet(char_id: str) -> str:
    """Fetches deterministic resource pressure telemetry as compact YAML."""
    try:
        from sr6core.character.resource_pressure import (
            calculate_resource_pressure,
            format_resource_pressure_yaml,
        )
        telemetry = calculate_resource_pressure(char_id)
        if telemetry:
            return format_resource_pressure_yaml(telemetry).strip()
    except Exception as e:
        return f"# Resource pressure telemetry unavailable for '{char_id}': {e}"
    return f"# No resource pressure telemetry found for '{char_id}'."


def _resolve_chapter_file(char_dir: Path, chapter_path: str) -> Optional[Path]:
    """Resolves chapter file path from absolute, relative, or narrative subdirectories."""
    p = Path(chapter_path)
    if p.is_file():
        return p
    if (char_dir / chapter_path).is_file():
        return char_dir / chapter_path
    if (char_dir / "narrative" / chapter_path).is_file():
        return char_dir / "narrative" / chapter_path
    if (char_dir / "chapters" / chapter_path).is_file():
        return char_dir / "chapters" / chapter_path

    # Try matching filename or stem in narrative / chapters
    target_name = p.name.lower()
    for sub in ["narrative", "chapters"]:
        d = char_dir / sub
        if d.is_dir():
            for cand in d.iterdir():
                if cand.is_file():
                    if cand.name.lower() == target_name or cand.stem.lower() == target_name:
                        return cand
    return None


def _slice_target_chapter(
    chapter_file: Optional[Path], chapter_path: str, beat: Optional[int]
) -> str:
    """Extracts drafted prose trailing slice and target beat outline."""
    if not chapter_file or not chapter_file.is_file():
        return f"[Target chapter file not found: '{chapter_path}']"

    raw_text = chapter_file.read_text(encoding="utf-8")

    # Skip frontmatter if present
    body = raw_text
    if body.startswith("---"):
        fm_end = body.find("\n---", 3)
        if fm_end != -1:
            body = body[fm_end + 4:].lstrip("\r\n")

    # Check for divider '---' separating prose from beat outline
    divider_match = re.search(r"(?m)^---\s*$", body)
    if divider_match:
        prose_part = body[:divider_match.start()].strip()
        outline_part = body[divider_match.end():].strip()

        prose_lines = prose_part.splitlines()
        if len(prose_lines) > 60:
            prose_content = "\n".join(prose_lines[-60:])
        else:
            prose_content = prose_part

        outline_content = ""
        if beat is not None:
            beat_pat = re.compile(
                rf"(?i)(?:^|\n)(?:[#*>\-\s]*)\bBeat\s+{beat}\b[:\s\-\.][^\n]*\n(.*?)(?=\n(?:[#*>\-\s]*)\bBeat\s+\d+\b[:\s\-\.]|\Z)",
                re.DOTALL,
            )
            bm = beat_pat.search(outline_part)
            if bm:
                outline_content = bm.group(0).strip()
            else:
                outline_content = outline_part
        else:
            outline_content = outline_part

        return (
            f"### Preceding Drafted Prose (Trailing Excerpt)\n\n"
            f"{prose_content}\n\n"
            f"### Target Beat Outline\n\n"
            f"{outline_content}"
        )
    else:
        lines = body.splitlines()
        if len(lines) <= 80:
            return body.strip()
        return "\n".join(lines[-60:]).strip()


def _get_callbacks_slice(char_dir: Path, callbacks: List[str]) -> str:
    """Finds referenced callback chapters and extracts titles and opening lines."""
    excerpts: List[str] = []
    search_dirs = [char_dir / "narrative", char_dir / "chapters"]

    for cb in callbacks:
        cb_str = str(cb).strip()
        found_file: Optional[Path] = None

        for sdir in search_dirs:
            if not sdir.is_dir():
                continue
            for f in sorted(sdir.iterdir()):
                if not f.is_file():
                    continue
                # Match ^0*{cb}[\s_-]+ or containing {cb}
                if re.match(rf"^0*{re.escape(cb_str)}[\s_\-]+", f.name, re.IGNORECASE):
                    found_file = f
                    break
                if f" {cb_str} " in f" {f.stem} " or f.stem.startswith(f"{cb_str} "):
                    found_file = f
                    break
            if found_file:
                break

        if not found_file:
            # Fallback containment search
            for sdir in search_dirs:
                if not sdir.is_dir():
                    continue
                for f in sorted(sdir.iterdir()):
                    if f.is_file() and cb_str in f.name:
                        found_file = f
                        break
                if found_file:
                    break

        if found_file and found_file.is_file():
            flines = found_file.read_text(encoding="utf-8").splitlines()
            title = found_file.stem
            for line in flines:
                if line.strip().startswith("# "):
                    title = line.strip()[2:].strip()
                    break
            first_40 = "\n".join(flines[:40]).strip()
            excerpts.append(f"#### Callback: Chapter {cb_str} - {title}\n\n{first_40}")
        else:
            excerpts.append(f"#### Callback: Chapter {cb_str}\n\n*[Chapter {cb_str} not found in narrative logs]*")

    return "\n\n---\n\n".join(excerpts)


def _get_items_slice(items: List[str]) -> str:
    """Queries RulesDB and RAGEngine for canonical rules excerpts."""
    excerpts: List[str] = []

    for item in items:
        clean_item = item.strip()
        if not clean_item:
            continue

        item_excerpt = ""
        # 1. Try RulesDB
        try:
            from sr6core.rules.db import RulesDB
            rdb = RulesDB()
            enriched = rdb.get_enriched_item(clean_item)
            if enriched:
                name = enriched.get("name", clean_item)
                itype = enriched.get("item_type", "item")
                desc = ""
                if enriched.get("rules_vault"):
                    desc = enriched["rules_vault"].get("content", "")
                elif enriched.get("commlink_data"):
                    import yaml
                    desc = yaml.dump(enriched["commlink_data"], sort_keys=False)
                desc_lines = [l.strip() for l in desc.splitlines() if l.strip()][:5]
                item_excerpt = f"- **{name}** ({itype}):\n  " + "\n  ".join(desc_lines)
        except Exception:
            pass

        # 2. Fallback to RAGEngine
        if not item_excerpt:
            try:
                from sr6core.rag.engine import RAGEngine
                engine = RAGEngine()
                hits = engine.search(clean_item, limit=2)
                if hits:
                    top = hits[0]
                    topic = top.get("topic", clean_item)
                    source = top.get("source", "SR6")
                    content = top.get("content", "")
                    content_lines = [l.strip() for l in content.splitlines() if l.strip()][:5]
                    item_excerpt = f"- **{topic}** ({source}):\n  " + "\n  ".join(content_lines)
            except Exception:
                pass

        if not item_excerpt:
            item_excerpt = f"- **{clean_item}**: [No offline rules vault entry found]"

        excerpts.append(item_excerpt)

    return "\n\n".join(excerpts)


def build_story_packet(
    char_id: str,
    chapter_path: str,
    beat: Optional[int] = None,
    callbacks: Optional[List[str]] = None,
    items: Optional[List[str]] = None,
) -> Tuple[str, Optional[str]]:
    """
    Builds a focused clean-room story packet for a narrative drafting beat.
    Firewalls out evaluation rubrics and scorecard policing while injecting character voice,
    resource pressure, target chapter / beat outline, historical callbacks, and rules context.
    """
    char_dir = resolve_character_dir(char_id)
    if not char_dir:
        return "", f"Could not resolve character '{char_id}'."

    chapter_file = _resolve_chapter_file(char_dir, chapter_path)
    target_display = chapter_file.name if chapter_file else Path(chapter_path).name

    # 1. Voice Essence Slice
    voice_essence = _slice_voice_spec(char_dir)

    # 2. Resource Pressure Telemetry
    pressure_yaml = _get_resource_pressure_snippet(char_id)

    # 3. Target Chapter & Beat Outline
    chapter_slice = _slice_target_chapter(chapter_file, chapter_path, beat)

    # 4. Historical Callbacks
    callbacks_md = ""
    if callbacks:
        callbacks_md = _get_callbacks_slice(char_dir, callbacks)

    # 5. Items & Rules
    items_md = ""
    if items:
        items_md = _get_items_slice(items)

    # Assembly
    packet_lines = [
        f"# Clean-Room Story Packet: {char_dir.name.title()}",
        f"**Target Chapter**: `{target_display}`",
        f"**Target Beat**: {f'Beat {beat}' if beat is not None else 'Active Outline'}",
        "",
        "## Character Voice Essence",
        voice_essence,
        "",
        "## Resource Pressure Telemetry",
        "```yaml",
        pressure_yaml,
        "```",
        "",
        "## Target Chapter & Beat Outline",
        chapter_slice,
    ]

    if callbacks_md:
        packet_lines.extend([
            "",
            "## Historical Callbacks",
            callbacks_md,
        ])

    if items_md:
        packet_lines.extend([
            "",
            "## Canonical Rules & Hardware Excerpts",
            items_md,
        ])

    packet_lines.append("")
    return "\n".join(packet_lines), None
