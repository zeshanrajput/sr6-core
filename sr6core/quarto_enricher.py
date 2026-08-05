"""
Quarto Story Book Shortcode & Dynamic Dossier Appendix Generator for SR6.
Expands shortcodes ({{< rule "Name" >}}) into styled HTML callouts with stats & citations,
and builds live character dossier appendices for Quarto narrative books.
"""

import os
import re
import sqlite3
from typing import Dict, Any, List, Optional, Tuple

from sr6core.rules_db import DEFAULT_DB_PATH, RulesDB
from sr6core.character_manager import CharacterManager


def expand_quarto_shortcodes(content: str, db_path: str = DEFAULT_DB_PATH) -> str:
    db = RulesDB(db_path=db_path)

    def shortcode_replacer(match: re.Match) -> str:
        s_type = match.group(1).lower().strip()
        target = match.group(2).strip().strip("'\"")

        enriched = db.get_enriched_item(target)
        if not enriched:
            return match.group(0)

        name = enriched["name"]
        item_type = enriched["item_type"].upper()
        cdata = enriched.get("commlink_data") or {}
        vdata = enriched.get("rules_vault") or {}

        stats_lines = []
        for k, v in cdata.items():
            if k not in ["raw_xml"] and v is not None:
                stats_lines.append(f"**{k.title()}**: {v}")

        stat_str = " | ".join(stats_lines) if stats_lines else "N/A"
        book_citation = f"*{vdata.get('source', 'SR6')} (p. {vdata.get('page', 'N/A')})*" if vdata else "*SR6 Core Rules*"

        callout = (
            f"\n::: {{.callout-note icon=false title=\"{name} [{item_type}]\"}}\n"
            f"**Stats**: {stat_str}  \n"
            f"**Citation**: {book_citation}  \n\n"
            f"{vdata.get('content', '').strip()}\n"
            f":::\n"
        )
        return callout

    pattern = r"\{\{\<\s*(rule|quality|spell|gear)\s+[\"']?([^\"'>]+)[\"']?\s*\>\}\}"
    return re.sub(pattern, shortcode_replacer, content)


def generate_character_dossier_appendix(char_id: str, output_qmd_path: str) -> bool:
    cm = CharacterManager()
    char_data = cm.get_character_data(char_id)
    if not char_data:
        return False

    db = RulesDB()
    identity = char_data.get("identity", {})
    attrs = char_data.get("attributes", {})

    lines = [
        "---",
        f"title: \"Appendix: Character Dossier - {identity.get('handle', char_id.title())}\"",
        "format: html",
        "---\n",
        f"# Character Dossier: {identity.get('handle', char_id.title())}\n",
        f"**Real Name**: {identity.get('real_name', 'N/A')}  ",
        f"**Metatype**: {identity.get('metatype', 'Human')}  ",
        f"**Role**: {identity.get('role', 'Shadowrunner')}  \n",
        "## Attributes\n",
        "| Attribute | Rating |",
        "| :--- | :--- |"
    ]

    for k, v in attrs.items():
        lines.append(f"| {k.upper()} | {v} |")

    lines.append("\n## Qualities & Rules Citations\n")
    pos_q = char_data.get("qualities", {}).get("positive", [])
    neg_q = char_data.get("qualities", {}).get("negative", [])

    for q in pos_q + neg_q:
        q_name = q.get("name", "Unknown Quality")
        enriched = db.get_enriched_item(q_name)
        cite_str = "SR6 Core"
        if enriched and enriched.get("rules_vault"):
            cite_str = f"{enriched['rules_vault'].get('source', 'SR6')} (p. {enriched['rules_vault'].get('page', 'N/A')})"
        karma = q.get("karma", 5)
        lines.append(f"- **{q_name}** ({karma} Karma) — [{cite_str}]")

    lines.append("\n## Skills\n")
    for s in char_data.get("skills", []):
        lines.append(f"- **{s.get('name', s.get('id', 'Skill'))}**: Rating {s.get('rating', 1)}")

    os.makedirs(os.path.dirname(output_qmd_path) or ".", exist_ok=True)
    with open(output_qmd_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")

    return True
