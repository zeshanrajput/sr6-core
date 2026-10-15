"""
Tabletop Automation & Prose Combat Ledger Parser for SR6 Core.
Extracts ammunition fired, physical/stun damage taken, drain/fading suffered,
and financial transactions from chapter prose, generating proposed YAML diffs.
"""

import os
import re
from typing import Dict, Any, List, Optional, Tuple


def parse_combat_ledger_prose(text_or_path: str) -> Dict[str, Any]:
    """
    Parses narrative prose and embedded Quarto Python cells to extract
    ammo expenditures, damage tracks, drain/fading, and rewards.
    """
    content = text_or_path
    target_name = "Prose Snippet"
    if os.path.exists(text_or_path) and os.path.isfile(text_or_path):
        target_name = text_or_path
        with open(text_or_path, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()

    ammo_spent: Dict[str, int] = {}
    damage_taken = {"physical": 0, "stun": 0, "drain_stun": 0, "fading_stun": 0}
    karma_delta = 0
    nuyen_delta = 0
    contacts_updated: List[Dict[str, Any]] = []
    sprites_added: List[Dict[str, Any]] = []

    # 1. Parse Embedded Quarto Python Cells: {python} inc('Key', Value)
    python_inc_matches = re.findall(r"inc\s*\(\s*['\"]([^'\"]+)['\"]\s*,\s*(-?\d+)\s*\)", content)
    for key, val_str in python_inc_matches:
        val = int(val_str)
        k_lower = key.lower()
        if "karma" in k_lower:
            karma_delta += val
        elif "nuyen" in k_lower or "¥" in k_lower:
            nuyen_delta += val
        elif "ammo" in k_lower or "apds" in k_lower or "gel" in k_lower:
            ammo_spent[key] = ammo_spent.get(key, 0) + abs(val)

    # 2. Parse inc_many calls: inc_many(('Karma', 5), ('Nuyen', 5000))
    inc_many_matches = re.findall(r"inc_many\s*\(\s*(.*?)\s*\)", content)
    for match_group in inc_many_matches:
        pairs = re.findall(r"\(\s*['\"]([^'\"]+)['\"]\s*,\s*(-?\d+)\s*\)", match_group)
        for key, val_str in pairs:
            val = int(val_str)
            k_lower = key.lower()
            if "karma" in k_lower:
                karma_delta += val
            elif "nuyen" in k_lower or "¥" in k_lower:
                nuyen_delta += val

    # 3. Parse Prose Ammo Actions: e.g. "Fired 6 APDS rounds", "expended 12 regular rounds", "shot 3 Gel bullets"
    ammo_patterns = [
        (r"(?:fired|expended|shot|burned|spent)\s+(\d+)\s+(?:rounds\s+of\s+)?(apds|gel|regular|flechette|explosive|ex-explosive|stick-n-shock|tracer)\s*(?:rounds|bullets|ammo)?", 1, 2),
        (r"(\d+)\s+(apds|gel|regular|flechette|explosive|ex-explosive|stick-n-shock|tracer)\s+(?:rounds|bullets|ammo)\s+(?:fired|expended|spent)", 1, 2)
    ]
    for pat, count_idx, type_idx in ammo_patterns:
        matches = re.findall(pat, content, re.IGNORECASE)
        for m in matches:
            count = int(m[count_idx - 1])
            ammo_type = m[type_idx - 1].upper()
            ammo_spent[ammo_type] = ammo_spent.get(ammo_type, 0) + count

    # 4. Parse Prose Damage Actions: e.g. "took 3 boxes of physical damage", "suffered 2 boxes stun", "took 4 stun drain"
    phys_patterns = [
        r"(?:took|suffered|sustained|absorbed)\s+(\d+)\s+(?:boxes\s+(?:of\s+)?)?physical\s+(?:damage|wounds?)",
        r"(\d+)\s+(?:boxes\s+(?:of\s+)?)?physical\s+(?:damage|wounds?)\s+(?:taken|sustained)"
    ]
    for pat in phys_patterns:
        for m in re.findall(pat, content, re.IGNORECASE):
            damage_taken["physical"] += int(m)

    stun_patterns = [
        r"(?:took|suffered|sustained)\s+(\d+)\s+(?:boxes\s+(?:of\s+)?)?stun\s+(?:damage|wounds?)",
        r"(\d+)\s+(?:boxes\s+(?:of\s+)?)?stun\s+(?:damage|wounds?)\s+(?:taken|sustained)"
    ]
    for pat in stun_patterns:
        for m in re.findall(pat, content, re.IGNORECASE):
            damage_taken["stun"] += int(m)

    drain_patterns = [
        r"(?:drain|fading)(?:\s+resisted)?:\s*(\d+)\s+(?:stun|physical)",
        r"(\d+)\s+(?:boxes\s+(?:of\s+)?)?(?:stun\s+)?(?:drain|fading)"
    ]
    for pat in drain_patterns:
        for m in re.findall(pat, content, re.IGNORECASE):
            damage_taken["drain_stun"] += int(m)

    # 5. Parse Prose Karma / Nuyen rewards: e.g. "Earned 8 Karma and 15,000 Nuyen", "15,000 Nuyen"
    if not python_inc_matches:
        # Check compound "X karma and Y nuyen"
        compound_matches = re.findall(r"(?:earned|gained|awarded|received)\s+(\d+)\s+karma\s+(?:and|,)\s+([\d,]+)\s*(?:¥|nuyen)", content, re.IGNORECASE)
        for k_val, n_val in compound_matches:
            karma_delta += int(k_val)
            nuyen_delta += int(n_val.replace(",", ""))

        if not compound_matches:
            prose_karma = re.findall(r"(?:earned|gained|awarded|received)\s+(\d+)\s+karma", content, re.IGNORECASE)
            if prose_karma:
                karma_delta += sum(int(k) for k in prose_karma)

            prose_nuyen = re.findall(r"(?:earned|gained|paid|reward(?:ed)?)\s+(?:¥|nuyen\s+)?([\d,]+)\s*(?:¥|nuyen)", content, re.IGNORECASE)
            if prose_nuyen:
                for n_str in prose_nuyen:
                    clean_n = int(n_str.replace(",", ""))
                    nuyen_delta += clean_n
            else:
                # Fallback for standalone "15,000 Nuyen" or "¥15,000"
                standalone_nuyen = re.findall(r"([\d,]+)\s*(?:¥|nuyen)\b", content, re.IGNORECASE)
                for n_str in standalone_nuyen:
                    clean_n = int(n_str.replace(",", ""))
                    if clean_n > 0:
                        nuyen_delta += clean_n

    # Generate Proposed YAML Diff
    proposed_yaml_diff = _generate_yaml_patch(ammo_spent, damage_taken, karma_delta, nuyen_delta)

    return {
        "target": target_name,
        "ammo_spent": ammo_spent,
        "damage_taken": damage_taken,
        "karma_delta": karma_delta,
        "nuyen_delta": nuyen_delta,
        "proposed_yaml_diff": proposed_yaml_diff,
        "has_changes": bool(ammo_spent or any(damage_taken.values()) or karma_delta or nuyen_delta)
    }


def _generate_yaml_patch(ammo: Dict[str, int], damage: Dict[str, int], karma: int, nuyen: int) -> str:
    lines = ["# Proposed character_master.yaml State Patch"]
    if karma != 0:
        lines.append(f"karma_free_delta: {karma:+d}")
    if nuyen != 0:
        lines.append(f"nuyen_balance_delta: {nuyen:+d}")
    if any(damage.values()):
        lines.append("damage_tracks:")
        if damage["physical"] > 0:
            lines.append(f"  physical_wounds_add: +{damage['physical']}")
        if damage["stun"] > 0 or damage["drain_stun"] > 0:
            total_stun = damage["stun"] + damage["drain_stun"]
            lines.append(f"  stun_wounds_add: +{total_stun}")
    if ammo:
        lines.append("ammunition_expended:")
        for atype, count in ammo.items():
            lines.append(f"  {atype.lower()}: -{count}")
    return "\n".join(lines)


def format_ledger_patch_markdown(report: Dict[str, Any]) -> str:
    """Formats the ledger parse report into clear Markdown diffs."""
    md = [
        f"# 🎯 Tabletop Action & Combat Ledger Report",
        f"- **Target Source**: `{report['target']}`\n",
        f"### Extracted State Changes\n",
        f"| Dimension | Delta / Action | Proposed Tabletop State |",
        f"| :--- | :---: | :--- |",
        f"| **Karma** | `{report['karma_delta']:+d}` | Adjust `karmaFree` & `lifetimeKarma` |",
        f"| **Nuyen** | `{report['nuyen_delta']:+d}` | Adjust available Nuyen balance |",
        f"| **Physical Damage** | `+{report['damage_taken']['physical']}` boxes | Add to Physical Damage Track |",
        f"| **Stun Damage & Drain** | `+{report['damage_taken']['stun'] + report['damage_taken']['drain_stun']}` boxes | Add to Stun Damage Track |",
    ]

    if report["ammo_spent"]:
        ammo_str = ", ".join(f"{k}: -{v}" for k, v in report["ammo_spent"].items())
        md.append(f"| **Ammunition** | `{ammo_str}` | Decrement magazine counts in inventory |")

    md.append(f"\n### 📝 Proposed YAML Diff (`character_master.yaml`)\n```yaml\n{report['proposed_yaml_diff']}\n```")
    return "\n".join(md)
