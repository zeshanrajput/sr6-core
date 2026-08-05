"""
Rules Computation & Resolution Engine for SR6.
Bridges SQLite RulesDB, frontmatter parsing, namespace scoping, and rules resolution.
"""

import os
import re
import json
from typing import Dict, Any, List, Optional, Set

from sr6core.rules_db import RulesDB, DEFAULT_DB_PATH


def normalize_name(name: str) -> str:
    """Normalizes string for fuzzy rule lookup (lowercase, stripped punctuation)."""
    if not name:
        return ""
    return re.sub(r'[^a-z0-9]', '', str(name).lower())


class RulesEngine:
    def __init__(self, db_path: str = DEFAULT_DB_PATH):
        self.db = RulesDB(db_path=db_path)

    def search_rules(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        return self.db.search_rules(query, limit=limit)

    def get_rule(self, rule_id: str) -> Optional[Dict[str, Any]]:
        return self.db.query_rule(rule_id)


def get_weapon_stats(item_id: str, db_path: str = DEFAULT_DB_PATH) -> Optional[Dict[str, Any]]:
    """
    Queries rules_index.db for weapon combat stats.
    Returns dictionary with id, name, dv, ar (list of int/None), mode, ammo, source.
    """
    import xml.etree.ElementTree as ET
    db = RulesDB(db_path=db_path)
    cursor = db.conn.cursor()

    row = cursor.execute(
        "SELECT id, name, category, source, raw_xml FROM ref_gear WHERE id = ? OR lower(id) = ?",
        (item_id, item_id.lower())
    ).fetchone()

    if not row:
        return None

    w_id, name, category, source, raw_xml = row["id"], row["name"], row["category"], row["source"], row["raw_xml"]

    dmg, attack_list, mode, ammo = "0P", [], "SS", "—"
    if raw_xml:
        try:
            root = ET.fromstring(raw_xml)
            weapon_node = root.find("weapon")
            if weapon_node is not None:
                dmg = weapon_node.get("dmg", "0P")
                attack_raw = weapon_node.get("attack", "")
                if attack_raw:
                    for p in attack_raw.rstrip(",").split(","):
                        attack_list.append(int(p) if p.isdigit() else None)
                mode = weapon_node.get("mode", "SS")
                ammo = weapon_node.get("ammo", "—")
        except Exception:
            pass

    return {
        "id": w_id,
        "name": name,
        "category": category,
        "source": source.replace("_", " ").title() if source else "SR6 Core",
        "dv": dmg,
        "ar": attack_list,
        "mode": mode,
        "ammo": ammo
    }


def render_weapon_card(item_id: str, db_path: str = DEFAULT_DB_PATH) -> str:
    """
    Queries rules_index.db for weapon combat stats and renders an HTML callout box.
    Ignores purchase attributes (cost/avail) and displays combat stats & source.
    """
    w = get_weapon_stats(item_id, db_path=db_path)
    if not w:
        return f"*(Weapon '{item_id}' not found in database)*"

    ar_str = " / ".join([str(x) if x is not None else "—" for x in w["ar"]]) if w["ar"] else "—"

    callout = (
        f'::: {{.callout-note icon=false title="{w["name"]} [{w["category"].upper()}]"}}\n'
        f'**Combat Stats**: **ID**: `{w["id"]}` | **DV**: {w["dv"]} | **AR**: {ar_str} | **Mode**: {w["mode"]} | **Ammo**: {w["ammo"]}  \n'
        f'**Citation**: *{w["source"]}*\n'
        f':::\n'
    )
    return callout


def render_rule_card(rule_id: str, db_path: str = DEFAULT_DB_PATH) -> str:
    """
    Queries rules_index.db for a rules vault entry by ID or topic (e.g. 'KK-0044')
    and renders an HTML callout box with its content and citation.
    """
    db = RulesDB(db_path=db_path)
    rule = db.query_rule(rule_id)
    if not rule:
        matches = db.search_rules(rule_id, limit=1)
        if matches:
            rule = matches[0]

    if not rule:
        return f"*(Rule '{rule_id}' not found in Rules Vault)*"

    topic = rule.get("topic", rule_id)
    source = rule.get("source", "SR6 Core")
    page = rule.get("page", "N/A")
    raw_content = rule.get("content", "")

    # Strip YAML frontmatter if present
    content_body = raw_content
    if content_body.startswith("---"):
        end_idx = content_body.find("---", 3)
        if end_idx != -1:
            content_body = content_body[end_idx + 3:].strip()

    # Remove H2 header title if redundant
    content_body = re.sub(r"^##\s+.*\n+", "", content_body).strip()

    callout = (
        f'::: {{.callout-note icon=false title="{topic}"}}\n'
        f'{content_body}\n\n'
        f'**Citation**: *{source}* (p. {page})\n'
        f':::\n'
    )
    return callout






