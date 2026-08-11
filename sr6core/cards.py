"""
Reference Card Generator and Character Card Deck Exporter for SR6.
Combines CommLink6 XML stat parameters with Rules Vault text descriptions
and character dossier local attributes.
"""

import os
import sqlite3
import html
from typing import Dict, Any, List, Optional, Tuple, Union
from sr6core.rules_db import DEFAULT_DB_PATH, RulesDB
from sr6core.character_manager import CharacterManager


def _extract_item_list(raw_section: Any) -> List[Any]:
    """Helper to safely flatten dossier sections that may be lists or dicts."""
    if not raw_section:
        return []
    if isinstance(raw_section, list):
        return raw_section
    if isinstance(raw_section, dict):
        items = []
        for k, v in raw_section.items():
            if isinstance(v, list):
                items.extend(v)
            elif isinstance(v, dict):
                items.append(v)
        return items
    return []


def _extract_id(item: Any) -> str:
    if isinstance(item, str):
        return item
    if isinstance(item, dict):
        return str(item.get("ref") or item.get("id") or item.get("name") or "")
    return str(item)


def get_item_card(category: str, item_input: Union[str, Dict[str, Any]], db_path: str = DEFAULT_DB_PATH) -> Dict[str, Any]:
    """
    Looks up item stat fields in CommLink XML tables and rules vault text in SQLite.
    Merges local dossier item attributes with database stats.
    Returns structured card object and formatted Markdown/HTML string.
    """
    item_dict = item_input if isinstance(item_input, dict) else {}
    item_id = _extract_id(item_input)
    local_name = item_dict.get("name") if item_dict else (item_input if isinstance(item_input, str) else "")

    if not item_id:
        return {"id": "unknown", "name": "Unknown Item", "category": category, "markdown": ""}

    cat_table_map = {
        "quality": ("ref_qualities", "id"),
        "spell": ("ref_spells", "id"),
        "complex_form": ("ref_complex_forms", "id"),
        "weapon": ("ref_weapons", "id"),
        "cyberware": ("ref_cyberware", "id"),
        "adept_power": ("ref_adept_powers", "id"),
        "vehicle": ("ref_vehicles", "id"),
        "program": ("ref_programs", "id"),
        "gear": ("ref_gear", "id"),
        "meta_echo": ("ref_qualities", "id"),
    }

    stat_row = None
    if os.path.exists(db_path):
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        table_info = cat_table_map.get(category.lower())
        if table_info:
            table, col = table_info
            try:
                # Priority 1: Exact ID/ref match
                stat_row = cursor.execute(f"SELECT * FROM {table} WHERE {col} = ?", (item_id,)).fetchone()
                # Priority 2: Exact name match
                if not stat_row and local_name:
                    stat_row = cursor.execute(f"SELECT * FROM {table} WHERE lower(name) = lower(?)", (local_name,)).fetchone()
                # Priority 3: Name like search excluding pack items
                if not stat_row:
                    stat_row = cursor.execute(
                        f"SELECT * FROM {table} WHERE (name LIKE ? OR name LIKE ?) AND id NOT LIKE 'pack_%'",
                        (f"%{item_id}%", f"%{local_name}%" if local_name else f"%{item_id}%")
                    ).fetchone()
                # Priority 4: Name like search fallback
                if not stat_row:
                    stat_row = cursor.execute(
                        f"SELECT * FROM {table} WHERE name LIKE ? OR name LIKE ?",
                        (f"%{item_id}%", f"%{local_name}%" if local_name else f"%{item_id}%")
                    ).fetchone()
            except Exception:
                pass

        if not stat_row:
            # Fallback search across all ref_ tables
            for t in ["ref_qualities", "ref_spells", "ref_complex_forms", "ref_weapons", "ref_cyberware", "ref_vehicles", "ref_gear"]:
                try:
                    stat_row = cursor.execute(
                        f"SELECT * FROM {t} WHERE id = ? OR lower(name) = lower(?) OR (name LIKE ? AND id NOT LIKE 'pack_%')",
                        (item_id, local_name or item_id, f"%{item_id}%")
                    ).fetchone()
                    if stat_row:
                        break
                except Exception:
                    pass

        conn.close()

    # Search rules vault for narrative description
    rdb = RulesDB(db_path=db_path)
    search_queries = [q for q in [local_name, item_id, item_id.replace("_", " ")] if q]
    vault_rules = []
    for sq in search_queries:
        vault_rules = rdb.search_rules(sq, limit=3)
        if vault_rules:
            break

    vault_text = ""
    source_citation = ""
    if vault_rules:
        best = vault_rules[0]
        raw_val = best.get("content") if isinstance(best, dict) else (best["content"] if best and "content" in best.keys() else "")
        vault_text = str(raw_val or "")
        # Remove YAML frontmatter if present
        if vault_text.startswith("---"):
            parts = vault_text.split("---", 2)
            if len(parts) >= 3:
                vault_text = parts[2].strip()
        source = best.get("source", "SR6 Core") if isinstance(best, dict) else (best["source"] if "source" in best.keys() else "SR6 Core")
        page = best.get("page", "") if isinstance(best, dict) else (best["page"] if "page" in best.keys() else "")
        source_citation = f"[{source}{', Page ' + str(page) if page else ''}]"

    # Merge stats (Local dossier attrs override DB defaults)
    card_name = local_name or item_id.replace("_", " ").title()
    db_stats = {}

    if stat_row:
        row_dict = dict(stat_row)
        card_name = local_name or row_dict.get("name", card_name)
        db_stats = {k: v for k, v in row_dict.items() if k not in ["raw_xml", "id", "name"]}

    # Filter local stats from item_dict
    local_stats = {}
    if item_dict:
        skip_keys = {"ref", "id", "name", "modifications", "framework_host", "ic", "purpose"}
        for k, v in item_dict.items():
            if k not in skip_keys and v not in [None, "", []]:
                local_stats[k] = v

    # Final combined stats dict
    merged_stats = {}
    merged_stats.update(db_stats)
    merged_stats.update(local_stats)  # local dossier stats take priority

    # Custom dossier modifications/page handling
    modifications = item_dict.get("modifications", [])
    custom_page = item_dict.get("page")
    if custom_page and not source_citation:
        source_citation = f"[{custom_page}]"

    # Format Markdown
    md_lines = [f"### [CARD] {card_name} ({category.replace('_', ' ').title()})"]
    if merged_stats:
        stat_items = [f"**{k.replace('_', ' ').title()}**: {v}" for k, v in merged_stats.items() if v not in [None, "", "-"]]
        md_lines.append("> " + " | ".join(stat_items))

    if modifications:
        md_lines.append("> **Modifications**: " + ", ".join(str(m) for m in modifications))

    if vault_text:
        md_lines.append("\n" + vault_text[:600] + ("..." if len(vault_text) > 600 else ""))

    if source_citation:
        md_lines.append(f"\n*Source: {source_citation}*")

    card_md = "\n".join(md_lines)

    return {
        "id": item_id,
        "name": card_name,
        "category": category,
        "stats": merged_stats,
        "modifications": modifications,
        "vault_text": vault_text,
        "citation": source_citation,
        "markdown": card_md
    }


def export_character_card_deck(char_id: str, db_path: str = DEFAULT_DB_PATH) -> Tuple[str, str]:
    """
    Scans a character dossier and generates a full reference card deck in Markdown and HTML formats.
    """
    cm = CharacterManager()
    char = cm.load_character(char_id)
    if not char or "data" not in char:
        raise ValueError(f"Character '{char_id}' not found in portfolio configuration.")

    data = char["data"]
    char_name = data.get("name") or data.get("identity", {}).get("handle", char_id.title())
    archetype = data.get("archetype") or data.get("identity", {}).get("metatype", "Shadowrunner")

    cards = []

    # 1. Qualities
    for q in _extract_item_list(data.get("qualities")):
        cards.append(get_item_card("quality", q, db_path=db_path))

    # 2. Spells
    for s in _extract_item_list(data.get("spells")):
        cards.append(get_item_card("spell", s, db_path=db_path))

    # 3. Complex Forms
    for cf in _extract_item_list(data.get("complex_forms")):
        cards.append(get_item_card("complex_form", cf, db_path=db_path))

    # 4. Meta Echoes / Submersion Echoes
    for me in _extract_item_list(data.get("meta_echoes")):
        cards.append(get_item_card("meta_echo", me, db_path=db_path))

    # 5. Weapons
    for w in _extract_item_list(data.get("weapons")):
        cards.append(get_item_card("weapon", w, db_path=db_path))

    # 6. Cyberware / Bioware
    for c in _extract_item_list(data.get("cyberware")):
        cards.append(get_item_card("cyberware", c, db_path=db_path))

    # 7. Drones & Vehicles
    for v in _extract_item_list(data.get("drones")) + _extract_item_list(data.get("vehicles")):
        cards.append(get_item_card("vehicle", v, db_path=db_path))

    # 8. Programs
    for p in _extract_item_list(data.get("programs")):
        cards.append(get_item_card("program", p, db_path=db_path))

    # Filter out empty cards
    cards = [c for c in cards if c.get("name") and c.get("id") != "unknown"]

    # Generate Deck Markdown
    md_deck_lines = [
        f"# [CARD] Reference Card Deck: {char_name} ({archetype})",
        f"*Total Reference Cards: {len(cards)}*\n",
        "---"
    ]
    for c in cards:
        md_deck_lines.append(c["markdown"])
        md_deck_lines.append("\n---\n")

    full_md = "\n".join(md_deck_lines)

    # Generate Styled HTML Deck
    html_cards = []
    for c in cards:
        stat_badges = "".join([
            f'<span class="badge"><b>{html.escape(k.replace("_", " ").title())}:</b> {html.escape(str(v))}</span> '
            for k, v in c["stats"].items() if v not in [None, "", "-"]
        ])
        mods_badge = ""
        if c.get("modifications"):
            mods_badge = f'<div class="card-mods"><b>Mods:</b> {html.escape(", ".join(str(m) for m in c["modifications"]))}</div>'

        card_html = f"""
        <div class="card">
            <div class="card-header">
                <span class="card-title">{html.escape(c["name"])}</span>
                <span class="card-cat">{html.escape(c["category"].replace('_', ' ').upper())}</span>
            </div>
            <div class="card-stats">{stat_badges}</div>
            {mods_badge}
            <div class="card-body">{html.escape(c["vault_text"][:450])}</div>
            <div class="card-footer">{html.escape(c["citation"])}</div>
        </div>
        """
        html_cards.append(card_html)

    full_html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Reference Cards - {html.escape(char_name)}</title>
    <style>
        body {{ font-family: 'Segoe UI', system-ui, sans-serif; background: #0f172a; color: #f8fafc; padding: 20px; }}
        h1 {{ color: #38bdf8; border-bottom: 2px solid #0284c7; padding-bottom: 10px; }}
        .deck {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(340px, 1fr)); gap: 16px; margin-top: 20px; }}
        .card {{ background: #1e293b; border: 1px solid #334155; border-radius: 8px; padding: 16px; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.3); display: flex; flex-direction: column; justify-content: space-between; }}
        .card-header {{ display: flex; justify-space-between; align-items: center; border-bottom: 1px solid #334155; padding-bottom: 8px; margin-bottom: 12px; }}
        .card-title {{ font-weight: bold; font-size: 1.1em; color: #f1f5f9; }}
        .card-cat {{ font-size: 0.75em; background: #0284c7; color: #fff; padding: 2px 8px; border-radius: 4px; font-weight: bold; }}
        .card-stats {{ margin-bottom: 8px; font-size: 0.85em; }}
        .card-mods {{ margin-bottom: 8px; font-size: 0.8em; color: #38bdf8; background: #0f172a; padding: 4px 8px; border-radius: 4px; }}
        .badge {{ display: inline-block; background: #334155; padding: 2px 6px; border-radius: 4px; margin-right: 4px; margin-bottom: 4px; }}
        .card-body {{ font-size: 0.88em; line-height: 1.4; color: #cbd5e1; white-space: pre-wrap; flex-grow: 1; margin-top: 8px; }}
        .card-footer {{ font-size: 0.8em; color: #38bdf8; margin-top: 12px; font-style: italic; border-top: 1px solid #334155; padding-top: 6px; }}
    </style>
</head>
<body>
    <h1>🃏 Reference Cards: {html.escape(char_name)} ({html.escape(archetype)})</h1>
    <div class="deck">
        {"".join(html_cards)}
    </div>
</body>
</html>
"""

    return full_md, full_html
