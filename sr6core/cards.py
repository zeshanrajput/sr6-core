"""
Reference Card Generator and Character Card Deck Exporter for SR6.
Generates focused, high-precision card stacks for character dossiers:
  - Base Attributes & Core Pools Card
  - Active Skills Card
  - Qualities (Positive & Negative)
  - Spells / Powers / Complex Forms (with dedicated rule extraction)
  - Submersion Echoes (with exact sub-item chunk extraction from HnS and Core)
  - Weapons (with accessory arrays & firing modes)
  - Armor & Defense
  - Cyberware / Bioware
  - Drones & Vehicles (with installed mods and Inhabited Action Pools)

Note: Contacts, Generic Gear, and Programs are excluded from the physical card deck.
"""

import os
import re
import sqlite3
import html
from typing import Dict, Any, List, Optional, Tuple, Union
from sr6core.rules_db import DEFAULT_DB_PATH, RulesDB
from sr6core.character_manager import CharacterManager
from sr6core.oids import resolve_canonical_oid
from sr6core.exporters.pdf_deck import generate_pdf_card_deck
from sr6core.log_engine import get_log_totals
from sr6core.modifiers import ModifierEngine
from sr6core.vehicles import parse_vehicle_modifications, calculate_drone_action_pools


def _extract_item_list(raw_section: Any) -> List[Any]:
    """Helper to safely flatten dossier sections that may be nested lists or dicts."""
    if not raw_section:
        return []
    if isinstance(raw_section, list):
        items = []
        for elem in raw_section:
            if isinstance(elem, list):
                items.extend(_extract_item_list(elem))
            else:
                items.append(elem)
        return items
    if isinstance(raw_section, dict):
        items = []
        for k, v in raw_section.items():
            if isinstance(v, list):
                items.extend(_extract_item_list(v))
            elif isinstance(v, dict):
                items.append(v)
            elif isinstance(v, str):
                items.append({"name": v, "id": v})
        return items
    return []


def _extract_id(item: Any) -> str:
    if isinstance(item, str):
        return item
    if isinstance(item, dict):
        return str(item.get("ref") or item.get("id") or item.get("name") or "")
    return str(item)


def _clean_card_text(raw_text: str, item_name: str, category: str = "") -> str:
    """
    Cleans up rules markdown text and extracts the precise subsection when a rule
    page covers multiple items (e.g. Echoes, Complex Forms, Multi-Weapon pages).
    """
    if not raw_text:
        return ""

    # Remove YAML frontmatter if present
    text = raw_text
    if text.startswith("---"):
        parts = text.split("---", 2)
        if len(parts) >= 3:
            text = parts[2].strip()

    # Clean picture tags and picture text
    text = re.sub(r"==> picture \[.*?\] intentionally omitted <==", "", text)
    text = re.sub(r"\*\*----- Start of picture text -----.*?\*\*----- End of picture text -----\*\*", "", text, flags=re.DOTALL)

    clean_name = item_name.strip()
    # Normalize common name suffixes like "Array (2x Link-Fired)" or "(Seattle Retrans Relay)"
    base_name = re.sub(r"\s*\(.*?\)", "", clean_name).strip()

    # If searching for an echo, quality, or weapon in a composite list, extract the specific bold item
    patterns = [
        # Match "- **Item Name:** content..." or "**Item Name:** content..."
        rf"(?:^|\n)(?:[#]+\s*{re.escape(clean_name)}[^\n]*|\*\*|\-\s*\*\*){re.escape(clean_name)}:?\*\*(.*?)(?=\n[#]+\s|\n\-\s*\*\*|\n\*\*[A-Z][a-zA-Z\s\-]+:?\*\*|\Z)",
        rf"(?:^|\n)(?:[#]+\s*{re.escape(base_name)}[^\n]*|\*\*|\-\s*\*\*){re.escape(base_name)}:?\*\*(.*?)(?=\n[#]+\s|\n\-\s*\*\*|\n\*\*[A-Z][a-zA-Z\s\-]+:?\*\*|\Z)",
    ]

    for p in patterns:
        match = re.search(p, text, re.DOTALL | re.IGNORECASE)
        if match:
            extracted = match.group(0).strip()
            extracted = re.sub(r"^[#]+\s*[^\n]*\n+", "", extracted)
            extracted = re.sub(r"^\-\s*", "", extracted)
            return extracted.strip()

    # For multi-item weapon pages like Ares Predator VI that also contain Slivergun text,
    # split at the next ## header
    headers = re.split(r"\n##\s+", text)
    if len(headers) > 1:
        for h in headers:
            first_line = h.split("\n", 1)[0].lower()
            if base_name.lower() in first_line or clean_name.lower() in first_line:
                return h.strip()

    return text.strip()


def get_base_attributes_card(char_data: Dict[str, Any], char_repo_path: Optional[str] = None) -> Dict[str, Any]:
    """Generates the primary character Card 1: Core Attributes & Derived Pools."""
    identity = char_data.get("identity", {})
    attrs = char_data.get("attributes", {})

    totals = get_log_totals(char_repo_path) if char_repo_path and os.path.exists(char_repo_path) else {}

    handle = identity.get("handle", "Unknown")
    metatype = identity.get("metatype", "Human")
    stream = identity.get("stream", "N/A")

    wil = int(attrs.get("willpower", 1))
    log_val = int(attrs.get("logic", 1))
    int_val = int(attrs.get("intuition", 1))
    cha = int(attrs.get("charisma", 1))
    edg = int(attrs.get("edge", 1))
    res = int(attrs.get("resonance", 0))
    mag = int(attrs.get("magic", 0))
    ess = float(attrs.get("essence", 6.0))

    submersion = totals.get("Submersion_Grade", 7)
    nuyen = totals.get("Nuyen", 5000)
    karma_avail = totals.get("Karma", 0)

    asdf = ModifierEngine.get_living_persona_asdf(char_data)
    mdef = ModifierEngine.get_full_matrix_defense(char_data)
    matrix_init = ModifierEngine.get_matrix_initiative(char_data)

    # For AI characters, physical attributes map to ASDF:
    att_str = asdf.get("attack", 7)
    slz_rea = asdf.get("sleaze", 9)
    dp_agi = asdf.get("data_processing", 7)
    fw_bod = asdf.get("firewall", 9)

    composure = wil + cha
    judge_intentions = int_val + wil
    memory = log_val + wil
    lift_carry = fw_bod + att_str
    phys_boxes = 8 + ((fw_bod + 1) // 2)
    stun_boxes = 8 + ((wil + 1) // 2)

    stats = {
        "ATT (STR)": att_str, "SLZ (REA)": slz_rea, "DP (AGI)": dp_agi, "FW (BOD)": fw_bod,
        "WIL": wil, "LOG": log_val, "INT": int_val, "CHA": cha,
        "EDG": edg, "RES / MAG": f"{res}/{mag}" if mag else res, "ESS": ess,
        "Submersion": f"Grade {submersion}",
        "Nuyen & Karma": f"{nuyen:,}¥ | {karma_avail} Karma",
        "Composure": composure,
        "Judge Intentions": judge_intentions,
        "Memory": memory,
        "Lift & Carry": lift_carry,
        "Matrix Initiative": matrix_init,
        "Condition Boxes": f"Phys [{phys_boxes}] | Stun [{stun_boxes}]",
    }

    if asdf:
        stats["ASDF Ratings"] = f"A:{att_str} S:{slz_rea} D:{dp_agi} F:{fw_bod}"
        stats["Full Matrix Def"] = f"{mdef['pool']}d6 ({mdef['effective_hits']} Hits)"

    vault_text = (
        f"Runner: {handle} ({metatype}) | Stream: {stream}\n"
        f"Submersion Grade {submersion} | Available Funds: {nuyen:,}¥ | Active Karma: {karma_avail} Pool\n"
        f"Derived Pools: Composure [{composure}], Judge Intentions [{judge_intentions}], Memory [{memory}], Lift/Carry [{lift_carry}].\n"
        f"Full Matrix Defense: {mdef['pool']}d6 [{mdef['breakdown']}]."
    )

    md_lines = [
        f"### [CARD] {handle.upper()} - BASE ATTRIBUTES & POOLS (Core)",
        "> " + " | ".join(f"**{k}**: {v}" for k, v in stats.items()),
        f"\n{vault_text}",
        f"\n*Source: [SR6 Core Rulebook, Character Dossier]*"
    ]

    return {
        "id": "card_base_attributes",
        "name": f"{handle} - Core Attributes",
        "category": "Core / Attributes",
        "stats": stats,
        "modifications": [],
        "vault_text": vault_text,
        "citation": "[SR6 Core]",
        "markdown": "\n".join(md_lines)
    }


def get_skills_card(char_data: Dict[str, Any]) -> Dict[str, Any]:
    """Generates Card 2: Active Skills & Effective Table Dice Pools."""
    identity = char_data.get("identity", {})
    skills = char_data.get("skills", [])
    handle = identity.get("handle", "Unknown")

    stats = {}
    skill_desc_lines = []
    for s in skills:
        if not isinstance(s, dict):
            continue
        s_name = s.get("name", "Skill")
        s_attr = s.get("attribute", "logic")
        s_rating = int(s.get("rating", 1))
        spec = s.get("specialization")

        calc = ModifierEngine.calculate_skill_pool(
            char_data,
            skill_name=s_name,
            skill_rating=s_rating,
            linked_attribute=s_attr,
            specialization=spec
        )
        spec_str = f" (+2 {spec})" if spec else ""
        stats[s_name] = f"{calc['effective_pool']}d6"
        skill_desc_lines.append(f"- **{s_name}{spec_str}**: **{calc['effective_pool']}d6** [{calc['breakdown']}]")

    vault_text = "Active Skills & Table-Relevant Effective Dice Pools:\n" + "\n".join(skill_desc_lines)
    md_lines = [
        f"### [CARD] {handle.upper()} - ACTIVE SKILLS & DICE POOLS (Skills)",
        "> " + " | ".join(f"**{k}**: {v}" for k, v in stats.items()),
        f"\n{vault_text}",
        f"\n*Source: [SR6 Core Rulebook, Skills]*"
    ]

    return {
        "id": "card_skills",
        "name": f"{handle} - Active Skills",
        "category": "Active Skills",
        "stats": stats,
        "modifications": [],
        "vault_text": vault_text,
        "citation": "[SR6 Core Rulebook, p. 92]",
        "markdown": "\n".join(md_lines)
    }


def get_item_card(category: str, item_input: Union[str, Dict[str, Any]], db_path: str = DEFAULT_DB_PATH, char_data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Looks up item stat fields in CommLink XML tables and rules vault text in SQLite.
    Resolves canonical OIDs and merges local dossier item attributes.
    """
    item_dict = item_input if isinstance(item_input, dict) else {}
    raw_id = _extract_id(item_input)
    local_name = item_dict.get("name") if item_dict else (item_input if isinstance(item_input, str) else "")

    if not raw_id:
        return {"id": "unknown", "name": "Unknown Item", "category": category, "markdown": ""}

    canonical_oid, stat_row = resolve_canonical_oid(category, raw_id, db_path=db_path)

    # Search rules vault for narrative description
    rdb = RulesDB(db_path=db_path)
    
    # Specific targeted queries based on category and clean names
    clean_search_name = re.sub(r"\s*\(.*?\)", "", local_name or raw_id).strip()
    search_queries = [
        clean_search_name,
        local_name,
        raw_id,
        raw_id.replace("_", " "),
        canonical_oid
    ]
    
    # Special query hints for specific difficult items
    if category == "complex_form" and clean_search_name.lower() == "cleaner":
        search_queries = ["Cleaner", "Complex Forms"]
    elif category == "meta_echo":
        search_queries = [clean_search_name, "New Echoes", "Increased Maximum Resonance", "Echoes"]
    elif "skinshield" in clean_search_name.lower():
        search_queries = ["Securetech SkinShield", "SkinShield"]
    elif "invisi" in clean_search_name.lower():
        search_queries = ["SecureTech Invisi-Shield Armor", "Invisi-Shield"]
    elif "butler" in clean_search_name.lower():
        search_queries = ["Shiawase Bi-Drone Butler", "Butler"]
    elif "man-at-arms" in clean_search_name.lower() or "manatarms" in clean_search_name.lower():
        search_queries = ["Shiawase Bi-Drone Man-At-Arms", "Man-At-Arms"]
    elif "sky commander" in clean_search_name.lower():
        search_queries = ["Federated-Boeing Sky Commander", "Sky Commander"]
    elif "crimson wasp" in clean_search_name.lower():
        search_queries = ["rEVOlution Arms Crimson Wasp", "Crimson Wasp"]
    elif "red fox" in clean_search_name.lower():
        search_queries = ["rEVOlution Arms Red Fox", "Red Fox"]
    elif "predator" in clean_search_name.lower():
        search_queries = ["Ares Predator VI", "Predator VI"]

    raw_vault_text = ""
    source_citation = ""

    # Special Precision Handler for Meta Echoes
    if category == "meta_echo":
        hns_rule = rdb.query_rule("HnS-0205")
        core_rule = rdb.query_rule("6WB-0887") or rdb.query_rule("SR6H-0884")
        hns_text = hns_rule.get("content", "") if hns_rule else ""
        core_text = core_rule.get("content", "") if core_rule else ""
        
        pattern = rf"(?:^|\n)(?:[#]+\s*{re.escape(clean_search_name)}[^\n]*|\*\*|\-\s*\*\*){re.escape(clean_search_name)}:?\*\*(.*?)(?=\n[#]+\s|\n\-\s*\*\*|\n\*\*[A-Z][a-zA-Z\s\-]+:?\*\*|\Z)"
        m = re.search(pattern, hns_text, re.DOTALL | re.IGNORECASE)
        if m:
            raw_vault_text = m.group(0).strip()
            source_citation = "[Hack and Slash, p. 70]"
        else:
            m2 = re.search(pattern, core_text, re.DOTALL | re.IGNORECASE)
            if m2:
                raw_vault_text = m2.group(0).strip()
                source_citation = "[SR6 Core Rulebook, p. 195]"

    # Special Precision Handler for Cleaner Complex Form
    elif category == "complex_form" and clean_search_name.lower() == "cleaner":
        raw_vault_text = (
            "Cleaner targets a device and makes an Electronics + Resonance vs. 2 x device rating (or Firewall) test. "
            "Each net hit reduces the target's Overwatch Score (OS) by 1. If used on a living persona or persona on a commlink, "
            "it directly decreases the accumulated OS from illicit matrix actions."
        )
        source_citation = "[SR6 Core Rulebook, p. 192]"

    # Special Precision Handler for Ares Predator VI (exclude Slivergun text)
    elif "predator" in clean_search_name.lower():
        pred_rule = rdb.query_rule("6WB-1179") or rdb.query_rule("SR6H-1177")
        if pred_rule:
            raw_vault_text = (
                "The Predator V rode on the laurels of its name. The Predator VI is genuine innovation built into "
                "the standard heavy pistol platform, boasting integrated smartgun connectivity, superior stopping power (3P), "
                "and modular accessory compatibility."
            )
            source_citation = "[SR6 Core Rulebook, p. 256]"

    # General Search across SQLite Rules Vault
    if not raw_vault_text:
        vault_rules = []
        for sq in search_queries:
            if not sq:
                continue
            vault_rules = rdb.search_rules(sq, limit=3, category=category)
            if vault_rules:
                break

        if vault_rules:
            best = vault_rules[0]
            raw_val = best.get("content") if isinstance(best, dict) else (best["content"] if best and "content" in best.keys() else "")
            raw_vault_text = str(raw_val or "")
            source = best.get("source", "SR6 Core") if isinstance(best, dict) else (best["source"] if "source" in best.keys() else "SR6 Core")
            page = best.get("page", "") if isinstance(best, dict) else (best["page"] if "page" in best.keys() else "")
            if not source_citation:
                source_citation = f"[{source}{', Page ' + str(page) if page else ''}]"

    # Precision extraction & cleaning of subsection
    vault_text = _clean_card_text(raw_vault_text, clean_search_name, category=category)

    # Merge stats
    card_name = local_name or raw_id.replace("_", " ").title()
    db_stats = {}

    if stat_row:
        card_name = local_name or stat_row.get("name", card_name)
        db_stats = {k: v for k, v in stat_row.items() if k not in ["raw_xml", "id", "name"]}

    # Filter local stats from item_dict
    local_stats = {}
    if item_dict:
        skip_keys = {"ref", "id", "name", "modifications", "accessories", "framework_host", "ic", "purpose", "page"}
        for k, v in item_dict.items():
            if k not in skip_keys and v not in [None, "", []]:
                local_stats[k] = v

    # Dynamic Vehicle Stats Calculation
    if category == "vehicle" and item_dict:
        vprof = parse_vehicle_modifications(item_dict, char_data=char_data)
        local_stats["body"] = f"{vprof['augmented_body']} (Inhabited: {vprof['inhabited_body']})"
        local_stats["armor"] = vprof["augmented_armor"]
        local_stats["sensor"] = vprof["augmented_sensor"]
        local_stats["handling"] = vprof["handling_str"]
        local_stats["accel"] = vprof["accel_str"]
        local_stats["speed"] = vprof["speed_str"]
        local_stats["pilot"] = vprof["pilot_str"]

    merged_stats = {}
    merged_stats.update(db_stats)
    merged_stats.update(local_stats)

    modifications = item_dict.get("accessories", item_dict.get("modifications", []))
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

    if category == "vehicle" and char_data:
        pools = calculate_drone_action_pools(char_data, item_dict, mode="inhabited_override")
        md_lines.append(f"> **Inhabited Action Pools**: Piloting: **{pools['piloting']['pool']}d6** | Gunnery: **{pools['gunnery']['pool']}d6** | Evasion: **{pools['evasion']['pool']}d6** | Perception: **{pools['perception']['pool']}d6** | Stealth: **{pools['stealth']['pool']}d6**")

    if vault_text:
        md_lines.append("\n" + vault_text[:600] + ("..." if len(vault_text) > 600 else ""))

    if source_citation:
        md_lines.append(f"\n*Source: {source_citation}*")

    return {
        "id": canonical_oid,
        "name": card_name,
        "category": category,
        "stats": merged_stats,
        "modifications": modifications,
        "vault_text": vault_text,
        "citation": source_citation,
        "markdown": "\n".join(md_lines)
    }


def build_character_cards(char_id: str, db_path: str = DEFAULT_DB_PATH) -> List[Dict[str, Any]]:
    """Constructs the curated, table-relevant reference card stack for a character."""
    cm = CharacterManager()
    char = cm.load_character(char_id)
    if not char or "data" not in char:
        return []

    data = char["data"]
    repo_path = cm.get_character_repo_dir(char_id)
    cards = []

    # 1. Base Attributes Card
    cards.append(get_base_attributes_card(data, char_repo_path=repo_path))

    # 2. Active Skills Card
    cards.append(get_skills_card(data))

    # 3. Qualities (Positive & Negative)
    for q in _extract_item_list(data.get("qualities")):
        cards.append(get_item_card("quality", q, db_path=db_path, char_data=data))

    # 4. Spells
    for s in _extract_item_list(data.get("spells")):
        cards.append(get_item_card("spell", s, db_path=db_path, char_data=data))

    # 5. Complex Forms
    for cf in _extract_item_list(data.get("complex_forms")):
        cards.append(get_item_card("complex_form", cf, db_path=db_path, char_data=data))

    # 6. Meta Echoes / Submersion Echoes
    for me in _extract_item_list(data.get("meta_echoes")):
        cards.append(get_item_card("meta_echo", me, db_path=db_path, char_data=data))

    # 7. Weapons (Ranged & Melee)
    for w in _extract_item_list(data.get("weapons")):
        cards.append(get_item_card("weapon", w, db_path=db_path, char_data=data))

    # 8. Armor & Ballistics
    for a in _extract_item_list(data.get("armors", data.get("armor", []))):
        cards.append(get_item_card("armor", a, db_path=db_path, char_data=data))

    # 9. Cyberware / Bioware / Augmentations
    all_augmentations = _extract_item_list(data.get("cyberware")) + _extract_item_list(data.get("bioware")) + _extract_item_list(data.get("augmentations"))
    for c in all_augmentations:
        cards.append(get_item_card("cyberware", c, db_path=db_path, char_data=data))

    # 10. Drones & Vehicles
    for v in _extract_item_list(data.get("drones")) + _extract_item_list(data.get("vehicles")):
        cards.append(get_item_card("vehicle", v, db_path=db_path, char_data=data))

    return [c for c in cards if c.get("name") and c.get("id") != "unknown"]


def export_character_card_deck(char_id: str, db_path: str = DEFAULT_DB_PATH) -> Tuple[str, str]:
    """Generates Markdown and HTML reference card decks."""
    cards = build_character_cards(char_id, db_path=db_path)
    cm = CharacterManager()
    char = cm.load_character(char_id)
    char_name = char["data"].get("identity", {}).get("handle", char_id.title()) if char else char_id.title()

    md_deck_lines = [
        f"# [CARD] Reference Card Deck: {char_name}",
        f"*Total Cards in Deck: {len(cards)}*\n",
        "---"
    ]
    for c in cards:
        md_deck_lines.append(c["markdown"])
        md_deck_lines.append("\n---\n")

    return "\n".join(md_deck_lines), ""


def export_character_card_deck_pdf(
    char_id: str,
    output_path: str,
    card_size: str = "postcard_4x5.5",
    db_path: str = DEFAULT_DB_PATH
) -> str:
    """Generates a ReportLab PDF card deck formatted for physical printing."""
    cards = build_character_cards(char_id, db_path=db_path)
    cm = CharacterManager()
    char = cm.load_character(char_id)
    char_name = char["data"].get("identity", {}).get("handle", char_id.title()) if char else char_id.title()
    return generate_pdf_card_deck(cards, output_path, card_size=card_size, char_name=char_name)
