"""
CommLink 6 XML Serializer & Exporter for SR6 Core.
Generates 100% CommLink 6 / Genesis-compliant character XML files strictly matching
the CommLink 6 Java Unmarshaller3 / SimplePersist schema (de.rpgframework.shadowrun6).

Enables one-way deterministic character export from SR6 Core master YAML and Quarto
downtime transaction ledgers directly into CommLink 6 player save folders.
"""

import os
import re
import glob
import uuid
import sqlite3
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple

from sr6core.rules.db import DEFAULT_DB_PATH
from sr6core.character.ledger import get_log_totals
from sr6core.srm_contacts import get_official_srm_contact
from sr6core.character.contacts import normalize_contacts_list
from sr6core.config import DEFAULT_COMMLINK_PLAYER_DIR, get_character_configs

MONTH_MAP = {
    "jan": "01", "january": "01",
    "feb": "02", "february": "02",
    "mar": "03", "march": "03",
    "apr": "04", "april": "04",
    "may": "05",
    "jun": "06", "june": "06",
    "jul": "07", "july": "07",
    "aug": "08", "august": "08",
    "sep": "09", "september": "09",
    "oct": "10", "october": "10",
    "nov": "11", "november": "11",
    "dec": "12", "december": "12"
}

CONTACT_TYPE_ENUMS = {
    "STREET", "CRIMINAL", "CORPORATE", "MAGIC", "MATRIX", "MEDICAL", "ACADEMIC", "MEDIA", "GOVERNMENT"
}

KNOWN_CHAR_ALIASES = {
    "yuriko": "reiko",
    "yuriko_star": "reiko",
    "yuriko star": "reiko",
    "reiko": "reiko",
    "union": "venn",
    "venn": "venn",
    "velvet": "velvet"
}

QUALITY_CHOICE_UUIDS = {
    "exceptional_attribute": "4096584c-eb76-49b2-be6b-1a6c0ca9e50a",
    "metagenetic_attribute_improvement": "dbb18bb4-89a4-4435-bede-3077ee600bc5",
    "allergy": "794d4562-8ca6-4958-81df-cf3cee81087d",
    "sprite_bane": "75f01ecc-60f3-4b5b-98de-c80008ebffec",
    "mentor_spirit": "b69f8371-fa0e-435c-b344-8fc6d64e1fb3",
    "spirit_affinity": "e19ecf4c-1508-406e-9a40-70cf09907bc3",
    "spirit_bane": "281aba04-1bd9-4d84-b6f4-f7bb97d217f0",
    "sprite_affinity": "c073da22-050d-4349-8c6c-3519c2a7368d",
}

# CommLink 6 Mentor Spirits that grant an adept power requiring a choice, but lack default decisions in mentorspirits.xml:
# - wise_warrior: improved_ability_combat (UUID 97fb1dcd-14e4-456c-aad7-17a7bf8cbbae) -> close_combat, firearms, exotic_weapons
# - firebringer: improved_ability (UUID 05054102-0183-482a-9e2b-84bc8d5f153f) -> athletics, con, etc.
# - seducer: improved_ability (UUID 05054102-0183-482a-9e2b-84bc8d5f153f) -> athletics, con, etc.
MENTOR_SPIRIT_ADEPT_CHOICES = {
    "wise_warrior": ("97fb1dcd-14e4-456c-aad7-17a7bf8cbbae", ["close_combat", "firearms", "exotic_weapons"]),
    "firebringer": ("05054102-0183-482a-9e2b-84bc8d5f153f", ["con", "influence", "athletics"]),
    "seducer": ("05054102-0183-482a-9e2b-84bc8d5f153f", ["con", "influence", "athletics"]),
}

COMMLINK_ADEPT_POWER_MAP = {
    "command_presence": "commanding_voice",
    "authoritative_tone": "authorative_tone",
}

COMMLINK_VALID_ADEPT_POWERS = {
    "improved_sense", "elemental_weapon", "archers_focus", "spell_resistance",
    "lie_detector", "animal_empathy", "analytics", "critical_strike",
    "spell_shroud", "distance_grasp", "nimble_fingers", "improved_reflexes",
    "adept_spell", "improved_ability", "attribute_boost", "great_leap",
    "enthralling_performance", "facial_sculpt", "kinesics_mastery", "sustenance",
    "nerve_strke", "quick_strike", "mystic_armor", "freefall",
    "danger_sense", "three_dimensional_memory", "authorative_tone", "elemental_missile",
    "killing_hands", "living_focus", "astral_perception", "combat_sense",
    "rapid_healing", "iron_will", "pheromone_control", "enhanced_accuracy",
    "dash", "improved_physical_attribute", "quick_draw", "sharp_tongue",
    "blind_fighting", "linguistics", "adept_accident", "missile_mastery",
    "improved_ability_combat", "vocal_control", "ventriloquism", "penetrating_strike",
    "maneuver", "charismatic_endurance", "precise_throw", "pain_resistance",
    "enhanced_perception", "delayed_damage", "counterstrike", "empathic_sense",
    "attribute_boost_mental", "improved_mental_attribute", "countermagic", "kinesics",
    "wall_running", "aid_sorcery", "berserk", "air_dance",
    "cosmetic_control", "side_step", "adrenaline_boost", "commanding_voice",
    "calming_voice", "distance_strike", "traceless_walk", "power_throw",
    "momentum", "missile_parry", "cloak", "pain_relief",
    "elemental_strike", "direction_sense", "cool_resolve", "empathic_healing",
}

COMMLINK_VALID_FOCI = {
    "sustaining_focus", "masking_focus", "weapon_focus", "raptor_skull",
    "banishing_focus", "summoning_focus", "counterspelling_focus", "centering_focus",
    "qi_focus", "ritualspellcasting_focus", "alchemical_focus", "disenchanting_focus",
    "spell_shaping_focus", "flexible_signature_focus", "spellcasting_focus", "athame",
    "power_focus"
}

CYBERLIMB_DEFAULT_VARIANTS = {
    "cyberarm": "fullarm_obvious",
    "cyberleg": "fullleg_obvious",
    "cybertorso": "torso_obvious",
    "cyberskull": "skull_obvious",
}


def resolve_cyberlimb_variant(item_ref: str, item_dict: Dict[str, Any]) -> Optional[str]:
    """Resolves required variant attribute for cyberlimb templates in CommLink 6 SimplePersist."""
    ref = item_ref.lower()
    if ref not in CYBERLIMB_DEFAULT_VARIANTS:
        return None

    if "variant" in item_dict and item_dict["variant"]:
        return str(item_dict["variant"])

    name_and_notes = (str(item_dict.get("name", "")) + " " + str(item_dict.get("notes", ""))).lower()
    is_synthetic = "synth" in name_and_notes
    type_suffix = "synthetic" if is_synthetic else "obvious"

    if ref == "cyberarm":
        prefix = "forearm" if "forearm" in name_and_notes else "fullarm"
        return f"{prefix}_{type_suffix}"
    elif ref == "cyberleg":
        prefix = "lowerleg" if ("lower" in name_and_notes or "calf" in name_and_notes) else "fullleg"
        return f"{prefix}_{type_suffix}"
    elif ref == "cybertorso":
        return f"torso_{type_suffix}"
    elif ref == "cyberskull":
        return f"skull_{type_suffix}"

    return CYBERLIMB_DEFAULT_VARIANTS.get(ref)

SIN_RATING_ENUM_MAP = {
    "1": "ANYONE",
    "2": "ROUGH_MATCH",
    "3": "GOOD_MATCH",
    "4": "SUPERFICIALLY_PLAUSIBLE",
    "5": "HIGHLY_PLAUSIBLE",
    "6": "SECOND_LIFE",
    1: "ANYONE",
    2: "ROUGH_MATCH",
    3: "GOOD_MATCH",
    4: "SUPERFICIALLY_PLAUSIBLE",
    5: "HIGHLY_PLAUSIBLE",
    6: "SECOND_LIFE",
}

CANONICAL_REF_ALIASES = {
    "cyberpsychosis": "cyber_psychosis",
    "authoritative_tone": "authorative_tone",
    # Drones & Vehicles
    "mctgnat": "mct_gnat",
    "mct_gnat": "mct_gnat",
    "mcthornet": "mct_hornet",
    "mct_hornet": "mct_hornet",
    "federatedboeingskycommander_seattle": "boing_sky_commander",
    "federated_boeing_sky_commander": "boing_sky_commander",
    "federated_boeing_sky_commander_(seattle_retrans_relay)": "boing_sky_commander",
    "boing_sky_commander": "boing_sky_commander",
    "shiawasebdmanatarms": "shiawase_BD_man_at_arms",
    "shiawase_bd_man_at_arms": "shiawase_BD_man_at_arms",
    "shiawase_man_at_arms": "shiawase_BD_man_at_arms",
    "kwonshamdreamgenie": "kwonsham_dream_genie",
    "kwonsham_dream_genie": "kwonsham_dream_genie",
    "vulcansystemsutilityone": "vulcan_utility_one",
    "vulcan_systems_utility_one": "vulcan_utility_one",
    "vulcan_utility_one": "vulcan_utility_one",
    # Matrix Devices & Commlinks
    "m_toc_ii": "mtoc_mark2",
    "m_toc_mark_ii": "mtoc_mark2",
    "mtoc_ii": "mtoc_mark2",
    "mtoc_mark_ii": "mtoc_mark2",
    "mtoc_mark2": "mtoc_mark2",
    "essy_motors_dronemaster_rcc": "essy_motors_drone_master",
    "essy_motors_dronemaster": "essy_motors_drone_master",
    "essy_motors_drone_master": "essy_motors_drone_master",
    "essy_motors_drone_master_rcc": "essy_motors_drone_master",
}

COMMLINK_DATA_STRUCTURES = {
    "oracle", "code_shell", "drone_whisperer", "eavesdropper", "extra_life",
    "phase_shifter", "grounding_rod", "echo_chamber", "sprite_caller",
    "logic_virus", "resonance_shield", "data_blade", "admonisher",
    "resonance_focus", "link_light", "master_key", "bandersnatch", "meat_cleaver"
}


def map_contact_type_enum(type_str: str) -> str:
    """Maps a free-text archetype or type string to a valid CommLink 6 ContactType enum."""
    if not type_str:
        return "STREET"

    clean = type_str.strip().upper()
    if clean in CONTACT_TYPE_ENUMS:
        return clean

    lower = type_str.lower()
    if any(k in lower for k in ["doc", "medical", "clinic", "hospital"]):
        return "MEDICAL"
    elif any(k in lower for k in ["magic", "talis", "shaman", "voodoo", "mage", "prof"]):
        return "MAGIC"
    elif any(k in lower for k in ["matrix", "deck", "sysop", "hacker", "programmer"]):
        return "MATRIX"
    elif any(k in lower for k in ["corp", "johnson", "executive", "manager", "suit"]):
        return "CORPORATE"
    elif any(k in lower for k in ["crime", "triad", "mafia", "vory", "gang", "hood"]):
        return "CRIMINAL"
    elif any(k in lower for k in ["media", "journal", "reporter", "model", "entertainer"]):
        return "MEDIA"
    elif any(k in lower for k in ["academic", "univ", "research"]):
        return "ACADEMIC"
    elif any(k in lower for k in ["gov", "agent", "police", "sec"]):
        return "GOVERNMENT"

    return "STREET"


def normalize_iso_date(date_str: str) -> str:
    """Converts dates like '2026-Apr-24' or '2026-04-24' to ISO-8601 for CommLink SimplePersist."""
    if not date_str or not date_str.strip():
        return "2026-01-01T00:00:00.000Z"

    clean = date_str.strip()
    if "T" in clean:
        return clean

    parts = clean.split("-")
    if len(parts) == 3:
        y, m, d = parts[0], parts[1], parts[2]
        if y.isdigit() and len(y) == 4:
            m_lower = m.lower()
            m_num = MONTH_MAP.get(m_lower, m.zfill(2) if m.isdigit() else "01")
            d_num = d.zfill(2) if d.isdigit() else "01"
            return f"{y}-{m_num}-{d_num}T00:00:00.000Z"

    return "2026-01-01T00:00:00.000Z"


def map_metatype_ref(raw_meta: str) -> str:
    """Maps character dossier metatype string to canonical CommLink 6 ref_metatypes ID."""
    if not raw_meta:
        return "human"
    m = raw_meta.strip().lower()
    if any(k in m for k in ["pilot", "pilot-ai", "ai-pilot"]):
        return "pilot-ai"
    elif "agent" in m and "ai" in m:
        return "agent-ai"
    elif "foundation" in m and "ai" in m:
        return "deep_foundation_ai"
    elif "dalakitnon" in m:
        return "elf"
    elif "koborokuru" in m:
        return "koborokuru"
    elif "dwarf" in m:
        return "dwarf"
    elif "elf" in m:
        return "elf"
    elif "oni" in m:
        return "oni"
    elif "ork" in m:
        return "ork"
    elif "troll" in m:
        return "troll"
    elif "human" in m:
        return "human"
    return m.replace(" ", "_").replace("-", "_")


def get_accessory_slot(acc_ref: str) -> str:
    """Determines canonical CommLink accessory slot name to prevent null-parent formula exceptions."""
    r = acc_ref.lower()
    if any(k in r for k in ["silencer", "suppressor", "gas_vent", "barrel"]):
        return "BARREL"
    if any(k in r for k in ["smartlink", "scope", "sight", "imaging"]):
        return "TOP"
    if any(k in r for k in ["bipod", "tripod", "laser", "flashlight"]):
        return "UNDER"
    if any(k in r for k in ["image_link", "flare_comp", "thermo", "low_light", "vision"]):
        return "OPTICAL"
    if any(k in r for k in ["audio", "sound", "ear", "spatial"]):
        return "AUDIO"
    if any(k in r for k in ["hood", "ballistic", "chem", "fire", "insul", "shock_frills", "holster"]):
        return "ARMOR"
    if any(k in r for k in ["fashion", "chic"]):
        return "FASHION"
    if any(k in r for k in ["soft", "p-ice", "assistant", "program", "app"]):
        return "SOFTWARE"
    if any(k in r for k in ["rack", "mount"]):
        return "VEHICLE_HARDPOINT"
    if any(k in r for k in ["propulsion", "rotor", "wheel", "boost", "powertrain", "engine"]):
        return "VEHICLE_POWERTRAIN"
    if any(k in r for k in ["features", "integrity", "chassis", "concealment", "coating"]):
        return "VEHICLE_CHASSIS"
    if any(k in r for k in ["cyberarm", "cyberleg", "cyberlimb", "implant"]):
        return "CYBERLIMB_IMPLANT"
    if any(k in r for k in ["satellite", "rigger", "autopilot", "sensor", "integrated_matrix"]):
        return "VEHICLE_ELECTRONICS"
    if any(k in r for k in ["upgrade", "dongle", "comhack", "securelink"]):
        return "ELECTRONIC_ACCESSORY"
    return "ARMOR"


def lookup_canonical_ref(item_name_or_ref: str, category: str, db_path: str = DEFAULT_DB_PATH) -> str:
    """Resolves an item name or ref against the CommLink 6 reference tables in rules_index.db."""
    if not item_name_or_ref:
        return "unknown"

    clean_str = item_name_or_ref.strip()
    norm_str = clean_str.lower().replace(" ", "_").replace("-", "_")
    if norm_str in CANONICAL_REF_ALIASES:
        clean_str = CANONICAL_REF_ALIASES[norm_str]
        norm_str = clean_str

    tbl_map = {
        "quality": "ref_qualities",
        "spell": "ref_spells",
        "complex_form": "ref_complex_forms",
        "gear": "ref_gear",
        "contact": "ref_contacts",
        "cyberware": "ref_cyberware",
        "bioware": "ref_cyberware",
        "augmentation": "ref_cyberware",
        "weapon": "ref_weapons",
        "vehicle": "ref_vehicles",
        "drone": "ref_vehicles",
    }
    tbl = tbl_map.get(category, "ref_gear")

    if not os.path.exists(db_path):
        return norm_str

    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        # Primary lookup in specified table
        row = cursor.execute(
            f"SELECT id FROM {tbl} WHERE id = ? OR lower(id) = ? OR lower(name) = ?",
            (clean_str, norm_str, clean_str.lower())
        ).fetchone()

        # If not found and category is gear, search across other equipment tables
        if not row and category == "gear":
            for alt_tbl in ["ref_vehicles", "ref_weapons", "ref_cyberware"]:
                row = cursor.execute(
                    f"SELECT id FROM {alt_tbl} WHERE id = ? OR lower(id) = ? OR lower(name) = ?",
                    (clean_str, norm_str, clean_str.lower())
                ).fetchone()
                if row:
                    break

        conn.close()
        if row:
            return row[0]
    except Exception:
        pass

    return norm_str


def is_valid_gear_template(ref_str: Optional[str], db_path: str = DEFAULT_DB_PATH) -> bool:
    """Verifies that an item reference exists in CommLink 6's gear/weapon/cyberware/vehicle catalog."""
    if not ref_str or ref_str in ["software_library", "qi_focus", "unknown"]:
        return False
    if not os.path.exists(db_path):
        return True
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        total_rows = 0
        for tbl in ["ref_gear", "ref_weapons", "ref_cyberware", "ref_vehicles"]:
            try:
                count_row = cursor.execute(f"SELECT COUNT(*) FROM {tbl}").fetchone()
                if count_row:
                    total_rows += count_row[0]
                row = cursor.execute(f"SELECT id FROM {tbl} WHERE id = ? OR lower(id) = ?", (ref_str, ref_str.lower())).fetchone()
                if row:
                    conn.close()
                    return True
            except Exception:
                pass
        conn.close()
        if total_rows < 10:
            return True
        return False
    except Exception:
        return True


def _safe_item_list(raw_section: Any) -> list:
    if not raw_section:
        return []
    if isinstance(raw_section, list):
        items = []
        for elem in raw_section:
            if isinstance(elem, list):
                items.extend(_safe_item_list(elem))
            else:
                items.append(elem)
        return items
    if isinstance(raw_section, dict):
        items = []
        for k, v in raw_section.items():
            if isinstance(v, list):
                items.extend(_safe_item_list(v))
            elif isinstance(v, dict):
                items.append(v)
            elif isinstance(v, str):
                items.append({"name": v, "id": v})
        return items
    return []


def extract_data_structures(char_data: Dict[str, Any], char_repo_path: Optional[str] = None) -> list:
    """Extracts technomancer resonance data structures from dossier, framework hosts, and modifiers."""
    ds_results = []
    seen = set()

    def add_ds(name_or_ref: str, rating: Any = 1):
        if not name_or_ref:
            return
        clean_name = str(name_or_ref).strip()
        ref = clean_name.lower().replace(" ", "_").replace("-", "_")
        ref = re.sub(r"^data_structure:?", "", ref).strip("_")
        ref = re.sub(r"_rating_\d+$", "", ref).strip("_")

        matched_ref = None
        for valid in COMMLINK_DATA_STRUCTURES:
            if valid == ref or valid in ref:
                matched_ref = valid
                break
        if not matched_ref:
            matched_ref = ref

        if matched_ref in COMMLINK_DATA_STRUCTURES and matched_ref not in seen:
            seen.add(matched_ref)
            try:
                r_val = int(rating)
            except Exception:
                r_val = 1
            ds_results.append({"ref": matched_ref, "name": clean_name, "rating": r_val})

    # 1. Top-level or technomancer section
    for ds in char_data.get("data_structures", []):
        if isinstance(ds, dict):
            add_ds(ds.get("ref") or ds.get("name"), ds.get("rating", 1))
        elif isinstance(ds, str):
            add_ds(ds)

    for ds in char_data.get("technomancer", {}).get("data_structures", []):
        if isinstance(ds, dict):
            add_ds(ds.get("ref") or ds.get("name"), ds.get("rating", 1))
        elif isinstance(ds, str):
            add_ds(ds)

    # 2. Check nested in drones or vehicles (e.g. host on Sky Commander)
    for v in char_data.get("drones", []) + char_data.get("vehicles", []):
        if isinstance(v, dict):
            host = v.get("framework_host", {})
            if isinstance(host, dict):
                for ds in host.get("data_structures", []):
                    if isinstance(ds, dict):
                        add_ds(ds.get("ref") or ds.get("name"), ds.get("rating", 1))
                    elif isinstance(ds, str):
                        add_ds(ds)

    # 3. Check modifiers
    for mod in char_data.get("modifiers", []):
        if isinstance(mod, dict):
            m_id = str(mod.get("id", "")).lower()
            m_name = str(mod.get("name", "")).lower()
            if "data_structure" in m_id or "data structure" in m_name:
                val = mod.get("value", 1)
                add_ds(m_id or m_name, val)

    # 4. Check items / foci
    for f in char_data.get("synergies", {}).get("foci", []) + char_data.get("items", []):
        if isinstance(f, dict):
            f_ref = str(f.get("ref", "")).lower()
            f_name = str(f.get("name", "")).lower()
            if "data_structure" in f_ref or "data structure" in f_name or "resonance structure" in f_name:
                add_ds(f_ref or f_name, f.get("rating", 1))

    return ds_results


def get_all_character_items(char_data: Dict[str, Any], char_repo_path: Optional[str] = None) -> list:
    """Gathers all items across weapons, armors, matrix_devices, gear, drones, vehicles, cyberware, and bioware."""
    all_raw = []
    for sec in ["weapons", "armors", "matrix_devices", "items", "gear", "drones", "vehicles"]:
        val = char_data.get(sec, [])
        all_raw.extend(_safe_item_list(val))

    res = []
    seen_refs = set()
    for item in all_raw:
        if isinstance(item, dict):
            d = dict(item)
            ref_k = str(d.get("ref") or d.get("id") or d.get("name", "")).lower()
            if ref_k:
                seen_refs.add(ref_k)
            res.append(d)
        elif isinstance(item, str):
            ref_k = item.lower()
            seen_refs.add(ref_k)
            res.append({"name": item, "ref": item, "mode": "CARRIED"})

    for aug_sec in ["cyberware", "bioware", "augmentations"]:
        for aug in _safe_item_list(char_data.get(aug_sec, [])):
            if isinstance(aug, dict):
                aug_dict = dict(aug)
                aug_dict.setdefault("mode", "IMPLANTED")
                res.append(aug_dict)
            elif isinstance(aug, str):
                res.append({"name": aug, "ref": aug, "mode": "IMPLANTED"})

    # Dynamic scanning of character_purchases.qmd and character_log.qmd for carried devices and retained loot
    if char_repo_path and os.path.exists(char_repo_path):
        # 1. Scan character_purchases.qmd
        for p_dir in ["core", "chapters", ""]:
            purch_path = os.path.join(char_repo_path, p_dir, "character_purchases.qmd") if p_dir else os.path.join(char_repo_path, "character_purchases.qmd")
            if os.path.exists(purch_path):
                try:
                    with open(purch_path, "r", encoding="utf-8") as pf:
                        for line in pf:
                            line_str = line.strip()
                            line_lower = line_str.lower()
                            if line_str.startswith("*") and any(k in line_lower for k in ["m-toc", "rcc", "cyberdeck", "commlink"]):
                                clean_name = re.sub(r"\{.*?\}", "", line_str).replace("*", "").strip()
                                clean_ref = clean_name.lower().replace(" ", "_").replace("-", "_")
                                clean_ref = CANONICAL_REF_ALIASES.get(clean_ref, clean_ref)
                                if clean_ref not in seen_refs:
                                    res.append({"name": clean_name, "ref": clean_ref, "mode": "CARRIED"})
                                    seen_refs.add(clean_ref)
                except Exception:
                    pass
                break

        # 2. Scan character_log.qmd for retained loot and acquired devices
        for l_dir in ["core", "chapters", ""]:
            log_path = os.path.join(char_repo_path, l_dir, "character_log.qmd") if l_dir else os.path.join(char_repo_path, "character_log.qmd")
            if os.path.exists(log_path):
                try:
                    with open(log_path, "r", encoding="utf-8") as lf:
                        in_loot_sec = False
                        for line in lf:
                            line_str = line.strip()
                            line_lower = line_str.lower()
                            if "loot" in line_lower and ("*" in line_str or "#" in line_str):
                                in_loot_sec = True
                                continue
                            elif in_loot_sec and line_str.startswith("#"):
                                in_loot_sec = False

                            if in_loot_sec or any(k in line_lower for k in ["rcc", "cyberdeck", "m-toc"]):
                                if "retained" in line_lower or "acquired" in line_lower or (in_loot_sec and line_str.startswith("*")):
                                    m_loot = re.search(r"[\*\-]\s*\*?([A-Za-z0-9\s\-]+(?:\s+(?:rcc|deck|commlink|focus|drone|terminal))?)\*?:?", line_str, re.IGNORECASE)
                                    if m_loot:
                                        item_name = m_loot.group(1).strip()
                                        item_ref = item_name.lower().replace(" ", "_").replace("-", "_")
                                        item_ref = CANONICAL_REF_ALIASES.get(item_ref, item_ref)
                                        if item_ref not in seen_refs and len(item_ref) > 2:
                                            canon = lookup_canonical_ref(item_ref, "gear")
                                            if canon != "unknown":
                                                res.append({"name": item_name, "ref": canon, "mode": "CARRIED"})
                                                seen_refs.add(item_ref)
                                                seen_refs.add(canon)
                except Exception:
                    pass
                break

    return res


def export_commlink_xml(
    char_data: Dict[str, Any],
    char_repo_path: Optional[str] = None,
    db_path: str = DEFAULT_DB_PATH
) -> str:
    """
    Generates a 100% CommLink 6 compliant XML document matching Java Unmarshaller3 / SimplePersist.
    Pulls live financial and karma totals from Quarto transaction ledgers when available.
    """
    log_totals = get_log_totals(char_repo_path) if char_repo_path and os.path.exists(char_repo_path) else {}

    root = ET.Element("sr6char")
    identity = char_data.get("identity", {})

    nuyen_val = int(log_totals.get("Nuyen", identity.get("nuyen", 5000)))
    karma_avail = int(log_totals.get("Karma", identity.get("karma", 0)))
    karma_life = int(log_totals.get("Lifetime_Karma", karma_avail))
    karma_spent = max(0, karma_life - karma_avail)

    raw_gender = str(identity.get("gender", "DIVERSE")).upper()
    gender_map = {"MALE": "MALE", "FEMALE": "FEMALE", "DIVERSE": "DIVERSE", "NON-BINARY": "DIVERSE"}
    root.set("gender", gender_map.get(raw_gender, "DIVERSE"))

    meta_str = map_metatype_ref(identity.get("metatype", "human"))
    root.set("meta", meta_str)
    root.set("karmaF", str(karma_avail))
    root.set("karmaI", str(karma_spent))
    root.set("nuyen", str(nuyen_val))
    root.set("career", "true")

    # ASDF Map stub
    ET.SubElement(root, "asdfMap")

    # Chargen Settings JSON
    cg_settings = ET.SubElement(root, "chargenSettings")
    cg_settings.text = '{"variant":"STANDARD","mysticAdeptPowerPoints":0,"toContacts":0,"negQualities":0,"initiation":0,"toNuyen":0}'

    # Real Name node
    if "real_name" in identity and identity["real_name"]:
        real_el = ET.SubElement(root, "realName")
        real_el.text = str(identity["real_name"])

    # Metahuman Type
    type_el = ET.SubElement(root, "type")
    type_el.text = "METAHUMAN"

    # Mortype & Tradition
    mortype_raw = identity.get("mortype", "").lower().replace(" ", "").replace("_", "")
    valid_mortypes = ["mysticadept", "magician", "adept", "technomancer", "aspectedmagician", "mundane"]
    matched_mortype = None
    for vm in valid_mortypes:
        if vm in mortype_raw:
            matched_mortype = vm
            break

    # If not explicitly specified, dynamically infer mortype from character mechanics
    if not matched_mortype:
        attrs = char_data.get("attributes", {})
        res_val = int(attrs.get("resonance", 0))
        mag_val = int(attrs.get("magic", 0))
        archetype = str(identity.get("archetype", "")).lower()
        role = str(identity.get("role", "")).lower()
        stream = identity.get("stream")
        complex_forms = char_data.get("complex_forms", [])
        spells = char_data.get("spells", [])
        adept_powers = char_data.get("adept_powers", [])

        if stream or complex_forms or res_val > 0 or "techno" in archetype or "techno" in role:
            matched_mortype = "technomancer"
        elif spells and adept_powers:
            matched_mortype = "mysticadept"
        elif spells:
            matched_mortype = "magician"
        elif adept_powers or mag_val > 0:
            matched_mortype = "adept"
        else:
            matched_mortype = "mundane"

    if matched_mortype:
        m_el = ET.SubElement(root, "mortype")
        m_el.text = matched_mortype

    tradition = identity.get("tradition", "").lower()
    if tradition:
        t_ref = "shinto" if "shinto" in tradition else tradition.split()[0].replace("/", "")
        t_el = ET.SubElement(root, "tradition")
        t_el.text = t_ref

    # Qualities
    pos_qualities = char_data.get("qualities", {}).get("positive", [])
    neg_qualities = char_data.get("qualities", {}).get("negative", [])

    qualities_el = ET.SubElement(root, "qualities")
    for q in pos_qualities + neg_qualities:
        q_el = ET.SubElement(qualities_el, "quality")
        q_el.set("lang", "en")
        q_ref = lookup_canonical_ref(q.get("ref") or q.get("name", ""), "quality", db_path=db_path)
        q_el.set("ref", q_ref)
        q_el.set("uuid", q.get("uuid") or str(uuid.uuid4()))
        if "rating" in q and int(q["rating"]) > 1:
            q_el.set("value", str(q["rating"]))
        if "choice" in q:
            choice_uuid = QUALITY_CHOICE_UUIDS.get(q_ref, str(uuid.uuid4()))
            dec_el = ET.SubElement(q_el, "decision")
            dec_el.set("choice", choice_uuid)
            raw_choice = str(q["choice"]).strip()
            if q_ref in ["exceptional_attribute", "metagenetic_attribute_improvement"]:
                raw_choice = raw_choice.upper()
            elif q_ref == "mentor_spirit":
                raw_choice = raw_choice.lower().replace(" ", "_")
            dec_el.set("value", raw_choice)

            # In CommLink 6, GetModificationsFromMentorSpirits evaluates adept modifications
            # for characters with usesPowers() (which is true for Adepts AND Mystic Adepts).
            # When the mentor spirit grants an adept power with choices (e.g. wise_warrior -> improved_ability_combat,
            # seducer/firebringer -> improved_ability), CommLink's upstream mentorspirits.xml omits the decision,
            # causing an unhandled modal error dialog on startup.
            # Adding the sub-decision directly to the mentor_spirit quality allows instantiateModification
            # to propagate the choice to the generated power seamlessly without UI errors.
            if q_ref == "mentor_spirit" and raw_choice in MENTOR_SPIRIT_ADEPT_CHOICES:
                adept_choice_uuid, adept_options = MENTOR_SPIRIT_ADEPT_CHOICES[raw_choice]
                char_skills = char_data.get("skills", [])
                char_skill_ids = [
                    str(s.get("id") or s.get("name", "")).lower().replace(" ", "_")
                    for s in char_skills
                ]
                selected_opt = None
                for opt in adept_options:
                    if opt in char_skill_ids:
                        selected_opt = opt
                        break
                if not selected_opt:
                    selected_opt = adept_options[0]
                extra_dec = ET.SubElement(q_el, "decision")
                extra_dec.set("choice", adept_choice_uuid)
                extra_dec.set("value", selected_opt)

    # Spells (Deduplicated)
    spells = char_data.get("spells", [])
    if spells:
        spells_el = ET.SubElement(root, "spells")
        exported_spells = set()
        for sp in spells:
            sp_ref = lookup_canonical_ref(sp.get("ref") or sp.get("name", ""), "spell", db_path=db_path)
            if sp_ref in exported_spells:
                continue
            sp_el = ET.SubElement(spells_el, "spell")
            sp_el.set("lang", "en")
            sp_el.set("ref", sp_ref)
            exported_spells.add(sp_ref)

    # Adept Powers (Validated against CommLink dataset and filtered for mentor/focus sources)
    powers = char_data.get("adept_powers", [])
    if powers:
        powers_el = None
        for p in powers:
            p_source = str(p.get("source", "")).lower()
            if any(skip_src in p_source for skip_src in ["focus", "qi", "mentor"]):
                continue
            p_ref = p.get("ref") or p.get("name", "").lower().replace(" ", "_")
            p_ref = COMMLINK_ADEPT_POWER_MAP.get(p_ref, p_ref)
            if p_ref not in COMMLINK_VALID_ADEPT_POWERS:
                continue

            if powers_el is None:
                powers_el = ET.SubElement(root, "adeptPowers")

            p_el = ET.SubElement(powers_el, "adeptpower")
            p_el.set("lang", "en")
            p_el.set("ref", p_ref)
            if "rating" in p and int(p["rating"]) > 0 and p_ref not in ["linguistics"]:
                p_el.set("value", str(p["rating"]))

            # Handle choices for adept powers requiring decisions
            if p_ref == "improved_ability_combat":
                p_choice = p.get("choice") or p.get("specification") or p.get("skill") or "close_combat"
                p_dec = ET.SubElement(p_el, "decision")
                p_dec.set("choice", "97fb1dcd-14e4-456c-aad7-17a7bf8cbbae")
                p_dec.set("value", str(p_choice).lower().replace(" ", "_"))
            elif p_ref == "improved_ability":
                p_choice = p.get("choice") or p.get("specification") or p.get("skill") or "athletics"
                p_dec = ET.SubElement(p_el, "decision")
                p_dec.set("choice", "05054102-0183-482a-9e2b-84bc8d5f153f")
                p_dec.set("value", str(p_choice).lower().replace(" ", "_"))
            elif p_ref in ["attribute_boost", "improved_physical_attribute"]:
                p_choice = str(p.get("choice") or p.get("specification") or p.get("attribute") or "AGILITY").upper()
                p_uuid = "1ec3bdd5-f9da-4ad2-8d44-9120529830e2" if p_ref == "attribute_boost" else "7282ba2c-fe33-4220-8fce-2ed77e0a3068"
                p_dec = ET.SubElement(p_el, "decision")
                p_dec.set("choice", p_uuid)
                p_dec.set("value", p_choice)
            elif p_ref in ["attribute_boost_mental", "improved_mental_attribute"]:
                p_choice = str(p.get("choice") or p.get("specification") or p.get("attribute") or "WILLPOWER").upper()
                p_uuid = "4fbc6994-a69c-4708-9d08-12ff9ffc087f" if p_ref == "attribute_boost_mental" else "4fbc6994-a69c-4708-9d08-12ff9ffc087e"
                p_dec = ET.SubElement(p_el, "decision")
                p_dec.set("choice", p_uuid)
                p_dec.set("value", p_choice)
            elif p_ref == "improved_sense":
                p_choice = str(p.get("choice") or p.get("specification") or "LOW_LIGHT").upper()
                p_dec = ET.SubElement(p_el, "decision")
                p_dec.set("choice", "220e6dfd-a76d-4c7e-97e1-dfdbdca464ef")
                p_dec.set("value", p_choice)

    # Complex Forms
    cforms = char_data.get("complex_forms", [])
    if cforms:
        cf_container = ET.SubElement(root, "complexforms")
        for cf in cforms:
            cf_ref = lookup_canonical_ref(cf.get("ref") or cf.get("name", ""), "complex_form", db_path=db_path)
            c_el = ET.SubElement(cf_container, "complexforms")
            c_el.set("lang", "en")
            c_el.set("ref", cf_ref)
            if "diffusion" in cf_ref:
                dec_cf = ET.SubElement(c_el, "decision")
                dec_cf.set("choice", "8b24b2be-c2fc-46f4-a353-7313f1f69d07")
                target_attr = cf.get("target_attribute", "FIREWALL").upper()
                dec_cf.set("value", target_attr)

    # Meta Echoes / Submersion Echoes / Metamagic
    meta_echoes = char_data.get("meta_echoes", [])
    if meta_echoes:
        echoes_el = ET.SubElement(root, "metaEchoes")
        for me in meta_echoes:
            me_el = ET.SubElement(echoes_el, "metaEcho")
            me_el.set("lang", "en")
            me_ref = me.get("ref") or me.get("name", "").lower().replace(" ", "_")
            if me_ref in ["power_point", "power_points", "powerpoint"]:
                me_ref = "power_points"
                val = me.get("rating") or me.get("value") or 1
                me_el.set("value", str(val))
            elif "rating" in me and int(me["rating"]) > 0:
                me_el.set("value", str(me["rating"]))
            elif "value" in me and int(me["value"]) > 0:
                me_el.set("value", str(me["value"]))
            me_el.set("ref", me_ref)

    # Data Structures (<datastructures>)
    datastructures = extract_data_structures(char_data, char_repo_path)
    if datastructures:
        ds_el = ET.SubElement(root, "datastructures")
        for ds in datastructures:
            d_node = ET.SubElement(ds_el, "datastructure")
            d_node.set("ref", ds["ref"])
            if "rating" in ds and int(ds["rating"]) > 0:
                d_node.set("value", str(ds["rating"]))

    # Name node
    name_el = ET.SubElement(root, "name")
    name_el.text = identity.get("handle") or identity.get("name", "Runner")

    # Datasets mode and Career rules
    ds_el = ET.SubElement(root, "datasets")
    ds_el.set("mode", "ALL")

    rules_el = ET.SubElement(root, "rules")
    r1 = ET.SubElement(rules_el, "set")
    r1.set("rule", "CAREER_UNDO_FROM_CAREER")
    r1.set("to", "true")
    r2 = ET.SubElement(rules_el, "set")
    r2.set("rule", "CAREER_PAY_GEAR")
    r2.set("to", "true")
    r3 = ET.SubElement(rules_el, "set")
    r3.set("rule", "CHARGEN_NEGATIVE_NUYEN")
    r3.set("to", "true")

    # Physical Bio Details
    if "hair_color" in identity:
        h_el = ET.SubElement(root, "hairColor")
        h_el.text = str(identity["hair_color"])
    if "eye_color" in identity:
        e_el = ET.SubElement(root, "eyeColor")
        e_el.text = str(identity["eye_color"])
    if "skin_color" in identity:
        sk_el = ET.SubElement(root, "skinColor")
        sk_el.text = str(identity["skin_color"])
    if "age" in identity:
        age_el = ET.SubElement(root, "age")
        age_el.text = str(identity["age"])
    if "size" in identity:
        size_el = ET.SubElement(root, "size")
        size_el.text = str(identity["size"]).replace("cm", "").strip()
    if "weight" in identity:
        w_el = ET.SubElement(root, "weight")
        w_el.text = str(identity["weight"]).replace("kg", "").strip()

    # Attributes
    attrs_el = ET.SubElement(root, "attributes")
    attrs = char_data.get("attributes", {})
    for attr, val in attrs.items():
        if attr.lower() in ["essence", "power_points"]:
            continue
        attr_el = ET.SubElement(attrs_el, "attributes")
        attr_el.set("id", attr.upper())
        attr_el.set("value", str(val))

    # Skills (Active, Knowledge, Language)
    skills_el = ET.SubElement(root, "skills")
    exported_langs = set()
    exported_knowledge = set()

    for s in char_data.get("skills", []):
        sk_ref = s.get("id", s.get("name", "").lower().replace(" ", "_"))
        if s.get("is_knowledge"):
            k_name = s.get("name", "Knowledge")
            if k_name.lower() in exported_knowledge:
                continue
            sk_el = ET.SubElement(skills_el, "skill")
            sk_el.set("lang", "en")
            sk_el.set("ref", "knowledge")
            sk_el.set("uuid", s.get("uuid") or str(uuid.uuid4()))
            sk_el.set("value", str(s.get("rating", 1)))
            dec_el = ET.SubElement(sk_el, "decision")
            dec_el.set("choice", "89ebc659-ba06-4732-b347-6b832842a55b")
            dec_el.set("value", k_name)
            exported_knowledge.add(k_name.lower())
        elif sk_ref == "language" or sk_ref.startswith("language_"):
            lang_name = s.get("name", "Native Language")
            m = re.search(r'\((.*?)\)', lang_name)
            if m:
                lang_name = m.group(1)
            elif sk_ref.startswith("language_"):
                lang_name = sk_ref.replace("language_", "").title()
            if lang_name.lower() in exported_langs:
                continue
            sk_el = ET.SubElement(skills_el, "skill")
            sk_el.set("lang", "en")
            sk_el.set("ref", "language")
            sk_el.set("uuid", s.get("uuid") or str(uuid.uuid4()))
            sk_el.set("value", str(s.get("rating", 1)))
            dec_el = ET.SubElement(sk_el, "decision")
            dec_el.set("choice", "a7103ee4-31fa-435d-ac42-08f7d4d1e80c")
            dec_el.set("value", lang_name)
            exported_langs.add(lang_name.lower())
        else:
            sk_el = ET.SubElement(skills_el, "skill")
            sk_el.set("lang", "en")
            sk_el.set("ref", sk_ref)
            sk_el.set("uuid", s.get("uuid") or str(uuid.uuid4()))
            sk_el.set("value", str(s.get("rating", 1)))
            if "specialization" in s and s["specialization"]:
                spec_el = ET.SubElement(sk_el, "skillspec")
                spec_el.set("lang", "en")
                spec_el.set("ref", s["specialization"].lower().replace(" ", "_"))

    for ks in char_data.get("knowledge_skills", []):
        k_name = ks.get("name", "Knowledge")
        is_lang = ks.get("is_native") or ks.get("is_linguasoft") or ks.get("level") in ["Native", "Basic", "Specialist", "Linguasoft"]
        if is_lang:
            if k_name.lower() in exported_langs:
                continue
            sk_el = ET.SubElement(skills_el, "skill")
            sk_el.set("lang", "en")
            sk_el.set("ref", "language")
            sk_el.set("uuid", ks.get("uuid") or str(uuid.uuid4()))
            r_val = ks.get("rating")
            sk_el.set("value", str(r_val if r_val is not None else 1))
            dec_el = ET.SubElement(sk_el, "decision")
            dec_el.set("choice", "a7103ee4-31fa-435d-ac42-08f7d4d1e80c")
            dec_el.set("value", k_name)
            exported_langs.add(k_name.lower())
        else:
            if k_name.lower() in exported_knowledge:
                continue
            sk_el = ET.SubElement(skills_el, "skill")
            sk_el.set("lang", "en")
            sk_el.set("ref", "knowledge")
            sk_el.set("uuid", ks.get("uuid") or str(uuid.uuid4()))
            r_val = ks.get("rating")
            sk_el.set("value", str(r_val if r_val is not None else 1))
            dec_el = ET.SubElement(sk_el, "decision")
            dec_el.set("choice", "89ebc659-ba06-4732-b347-6b832842a55b")
            dec_el.set("value", ks.get("name", "Knowledge"))
            exported_knowledge.add(k_name.lower())

    # Chargen Used and Strictness
    cg_el = ET.SubElement(root, "charGenUsed")
    cg_el.text = "free"

    strict_el = ET.SubElement(root, "strictness")
    strict_el.text = "srm"

    # Items / Gear / Weapons / Armor / Devices / Drones / Augmentations
    items_el = ET.SubElement(root, "items")
    all_items = get_all_character_items(char_data, char_repo_path)
    for g in all_items:
        g_ref = lookup_canonical_ref(g.get("ref") or g.get("name", ""), "gear", db_path=db_path)
        if not is_valid_gear_template(g_ref, db_path=db_path):
            continue

        g_el = ET.SubElement(items_el, "item")
        g_el.set("lang", "en")
        g_mode = g.get("mode", "CARRIED").upper()
        g_el.set("mode", g_mode)
        g_el.set("ref", g_ref)
        item_uuid = g.get("uuid") or str(uuid.uuid4())
        g_el.set("uuid", item_uuid)

        variant = resolve_cyberlimb_variant(g_ref, g)
        if variant:
            g_el.set("variant", variant)

        count_val = g.get("qty") or g.get("count", 1)
        if count_val and int(count_val) > 1:
            g_el.set("count", str(count_val))

        rating_val = g.get("rating")
        if rating_val and int(rating_val) > 0 and (g_mode == "IMPLANTED" or g_ref in ["contacts", "earbuds", "personal_assistant"]):
            dec_el = ET.SubElement(g_el, "decision")
            dec_el.set("choice", "c2d17c87-1cfe-4355-9877-a20fe09c170d")
            dec_el.set("value", str(rating_val))

        if g_mode == "IMPLANTED":
            grade_raw = str(g.get("grade", "STANDARD")).upper()
            grade_map = {
                "STANDARD": "STANDARD", "USED": "USED", "ALPHAWARE": "ALPHA",
                "ALPHA": "ALPHA", "BETAWARE": "BETA", "BETA": "BETA",
                "DELTAWARE": "DELTA", "DELTA": "DELTA", "OMEGA": "OMEGA"
            }
            dec_grade = ET.SubElement(g_el, "decision")
            dec_grade.set("choice", "c2d17c87-1cfe-4355-9877-a20fe09c170c")
            dec_grade.set("value", grade_map.get(grade_raw, "STANDARD"))

        if g_ref.startswith("ammo_") or "ammo" in g_ref:
            ammo_type = "REGULAR"
            name_check = (str(g.get("name", "")) + " " + g_ref).upper()
            if "APDS" in name_check:
                ammo_type = "APDS"
            elif "GEL" in name_check:
                ammo_type = "GEL"
            elif "FLECHETTE" in name_check:
                ammo_type = "FLECHETTE"
            elif "EX-EX" in name_check or "EXPLOSIVE" in name_check:
                ammo_type = "EXPLOSIVE"
            elif "STICK" in name_check:
                ammo_type = "STICK_N_SHOCK"
            elif "TRACER" in name_check:
                ammo_type = "TRACER"
            dec_ammo = ET.SubElement(g_el, "decision")
            dec_ammo.set("choice", "b015341d-24dc-42bb-a46b-781a5340e0b3")
            dec_ammo.set("value", ammo_type)

        accs = g.get("accessories", []) or g.get("modifications", [])
        if accs:
            acc_el = ET.SubElement(g_el, "accessories")
            for acc in accs:
                acc_name = acc if isinstance(acc, str) else (acc.get("name") or acc.get("ref", ""))
                acc_ref = lookup_canonical_ref(acc_name, "gear", db_path=db_path)
                if not is_valid_gear_template(acc_ref, db_path=db_path):
                    continue
                a_sub = ET.SubElement(acc_el, "item")
                a_sub.set("lang", "en")
                a_sub.set("mode", "EMBEDDED")
                a_sub.set("ref", acc_ref)
                a_sub.set("slot", get_accessory_slot(acc_ref))
                a_sub.set("uuid", str(uuid.uuid4()))

        # Drones with Satellite Link in master YAML modifications
        mods = [str(m).lower() for m in g.get("modifications", [])]
        if any("satellite" in m for m in mods):
            acc_el = g_el.find("accessories")
            if acc_el is None:
                acc_el = ET.SubElement(g_el, "accessories")
            sat_el = ET.SubElement(acc_el, "item")
            sat_el.set("lang", "en")
            sat_el.set("mode", "EMBEDDED")
            sat_el.set("ref", "satellite_link")
            sat_el.set("slot", "VEHICLE_ELECTRONICS")
            sat_el.set("uuid", str(uuid.uuid4()))

    # Essence Changes / Augmentation Tracking (<essenceChanges>)
    acclimation_rating = 0
    cyborg_rating = 0
    for q in pos_qualities:
        q_name = q.get("name", "").lower()
        if "acclimation" in q_name:
            acclimation_rating = int(q.get("rating", 1))
        elif "cyborg" in q_name:
            cyborg_rating = int(q.get("rating", 1))

    implanted_items = [it for it in all_items if it.get("mode") == "IMPLANTED"]
    if implanted_items or acclimation_rating > 0 or cyborg_rating > 0:
        ec_el = ET.SubElement(root, "essenceChanges")
        for aug in implanted_items:
            aug_ref = lookup_canonical_ref(aug.get("ref") or aug.get("name", ""), "cyberware", db_path=db_path)
            aug_uuid = aug.get("uuid") or str(uuid.uuid4())

            ess_val = None
            if "essence" in aug:
                try:
                    ess_val = float(aug["essence"])
                except Exception:
                    pass
            if ess_val is None and "notes" in aug:
                m = re.search(r'(\d+(?:\.\d+)?)\s*Ess', str(aug["notes"]), re.I)
                if m:
                    ess_val = float(m.group(1))
            if ess_val is None:
                r_val = float(aug.get("rating") or 1)
                ess_val = 0.1 * r_val

            val_millies = int(round(ess_val * 1000))
            val_el = ET.SubElement(ec_el, "valmod")
            val_el.set("id", aug_uuid)
            val_el.set("ref", aug_ref)
            val_el.set("set", "AUGMENTED")
            val_el.set("type", "CARRIED")
            val_el.set("value", str(val_millies))

        for _ in range(acclimation_rating):
            vm = ET.SubElement(ec_el, "valmod")
            vm.set("ref", "augmentation_acclimation")
            vm.set("type", "QUALITY")
            vm.set("value", "-100")

        for _ in range(cyborg_rating):
            vm = ET.SubElement(ec_el, "valmod")
            vm.set("ref", "cyborg")
            vm.set("type", "QUALITY")
            vm.set("value", "-100")

    # Contacts
    contacts_el = ET.SubElement(root, "contacts")
    merged_contacts = {}
    for c in normalize_contacts_list(char_data.get("contacts", [])):
        cname = c.get("name")
        if cname:
            merged_contacts[cname] = c

    if log_totals.get("Contacts"):
        for cname, cinfo in log_totals["Contacts"].items():
            if cname in merged_contacts:
                merged_contacts[cname].update(cinfo)
            else:
                merged_contacts[cname] = cinfo

    for cname, c in merged_contacts.items():
        c_el = ET.SubElement(contacts_el, "contact")
        c_el.set("name", cname)

        srm_info = get_official_srm_contact(cname, db_path=db_path)
        if srm_info:
            c_el.set("rat", str(srm_info["connection"]))
            c_el.set("type", map_contact_type_enum(srm_info["types"]))
            c_el.set("typename", str(srm_info["archetype"]))
        else:
            c_el.set("rat", str(c.get("connection", 1)))
            type_raw = c.get("type") or c.get("archetype") or ""
            c_el.set("type", map_contact_type_enum(type_raw))
            c_el.set("typename", str(type_raw))

        c_el.set("loy", str(c.get("loyalty", 1)))
        c_el.set("favors", str(c.get("favors", 0)))
        note_text = c.get("notes") or c.get("description")
        if note_text:
            desc_el = ET.SubElement(c_el, "description")
            desc_el.text = str(note_text)

    # Foci (Valid magic foci only; skip technomancer resonance structures / data structures)
    foci_list = list(char_data.get("synergies", {}).get("foci", []))
    if not foci_list:
        foci_list = [
            it for it in char_data.get("items", []) if isinstance(it, dict) and "focus" in it.get("ref", "").lower()
        ]
    existing_f_names = {str(f.get("name", "")).lower() for f in foci_list}
    for m in char_data.get("modifiers", []):
        if isinstance(m, dict) and m.get("type") == "focus":
            m_name = m.get("name", "Focus")
            if m_name.lower() not in existing_f_names:
                foci_list.append({
                    "name": m_name,
                    "ref": m.get("id", "power_focus"),
                    "rating": m.get("value", 3),
                    "bonded": True,
                    "applies_to": m.get("target", "magic").replace("attribute:", "")
                })

    foci_el = None
    exported_foci = set()
    for f in foci_list:
        f_name = str(f.get("name", "")).lower()
        f_ref = str(f.get("ref", "")).lower()

        # Skip technomancer resonance structures / non-magical foci
        if any(bad in f_ref or bad in f_name for bad in ["data_structure", "resonance", "data structure"]):
            continue

        canonical_ref = None
        if "qi" in f_ref or "qi" in f_name:
            canonical_ref = "qi_focus"
        elif "power" in f_ref or "power" in f_name:
            canonical_ref = "power_focus"
        elif "sustaining" in f_ref or "sustaining" in f_name:
            canonical_ref = "sustaining_focus"
        elif "weapon" in f_ref or "weapon" in f_name:
            canonical_ref = "weapon_focus"
        elif "counterspelling" in f_ref or "counterspelling" in f_name:
            canonical_ref = "counterspelling_focus"
        elif "spellcasting" in f_ref or "spellcasting" in f_name:
            canonical_ref = "spellcasting_focus"
        elif "summoning" in f_ref or "summoning" in f_name:
            canonical_ref = "summoning_focus"
        elif "banishing" in f_ref or "banishing" in f_name:
            canonical_ref = "banishing_focus"
        elif f_ref in COMMLINK_VALID_FOCI:
            canonical_ref = f_ref

        if not canonical_ref or canonical_ref not in COMMLINK_VALID_FOCI:
            continue

        f_rating = str(f.get("rating", 3))
        focus_key = (canonical_ref, f_rating)
        if focus_key in exported_foci:
            continue
        exported_foci.add(focus_key)

        if foci_el is None:
            foci_el = ET.SubElement(root, "foci")

        f_node = ET.SubElement(foci_el, "focus")
        f_node.set("lang", "en")
        f_node.set("ref", canonical_ref)
        f_node.set("value", f_rating)

        dec_rating = ET.SubElement(f_node, "decision")
        dec_rating.set("choice", "c2d17c87-1cfe-4355-9877-a20fe09c170d")
        dec_rating.set("value", f_rating)

        if canonical_ref == "qi_focus":
            power_choice = f.get("power")
            if not power_choice:
                for ap in char_data.get("adept_powers", []):
                    if "focus" in str(ap.get("source", "")).lower():
                        power_choice = ap.get("ref") or ap.get("name")
                        break
            if power_choice:
                p_choice_str = str(power_choice).lower().replace(" ", "_")
                p_choice_str = COMMLINK_ADEPT_POWER_MAP.get(p_choice_str, p_choice_str)
                dec_power = ET.SubElement(f_node, "decision")
                dec_power.set("choice", "37026c81-d5a0-44fe-8fa9-9263acb6059f")
                dec_power.set("value", p_choice_str)

    # Lifestyles
    lifestyles = char_data.get("lifestyles", [])
    if lifestyles:
        ls_container = ET.SubElement(root, "lifestyles")
        for ls in lifestyles:
            l_el = ET.SubElement(ls_container, "lifestyle")
            l_el.set("lang", "en")
            l_el.set("ref", ls.get("quality", "low").lower())
            l_el.set("comfort", ls.get("comfort", "low").lower())
            l_el.set("entert", ls.get("entertainment", "low").lower())
            l_el.set("necess", ls.get("necessities", "low").lower())
            l_el.set("neigh", ls.get("neighborhood", "low").lower())
            l_el.set("security", ls.get("security", "low").lower())
            l_el.set("space", ls.get("space", "low").lower())
            l_el.set("value", str(ls.get("months", 1)))
            if "sin" in ls:
                l_el.set("sin", str(ls["sin"]))

    # SINs & Licenses
    sins = char_data.get("sins", [])
    if sins:
        sins_el = ET.SubElement(root, "sins")
        sin_uuid_map = {}
        for s in sins:
            s_node = ET.SubElement(sins_el, "sin")
            s_node.set("name", s.get("name", "SIN"))
            raw_qual = s.get("quality", s.get("rating", "SECOND_LIFE"))
            mapped_qual = SIN_RATING_ENUM_MAP.get(str(raw_qual), str(raw_qual).upper())
            s_node.set("quality", mapped_qual)
            s_uuid = s.get("uuid") or str(uuid.uuid4())
            s_node.set("uniqueid", s_uuid)
            sin_uuid_map[s.get("name")] = s_uuid

        licenses = char_data.get("licenses", [])
        if licenses:
            lic_el = ET.SubElement(root, "licenses")
            for lic in licenses:
                l_node = ET.SubElement(lic_el, "licenses")
                l_node.set("name", str(lic.get("name", "License")))
                raw_rat = lic.get("rating", "SECOND_LIFE")
                mapped_rat = SIN_RATING_ENUM_MAP.get(str(raw_rat), str(raw_rat).upper())
                l_node.set("rating", mapped_rat)
                l_sin_name = lic.get("sin")
                l_node.set("sin", sin_uuid_map.get(l_sin_name, l_sin_name or str(uuid.uuid4())))
                l_node.set("uniqueid", lic.get("uuid") or str(uuid.uuid4()))

    # Rewards / Session History
    rewards_el = ET.SubElement(root, "rewards")
    for sess in log_totals.get("Session_Logs", []):
        r_el = ET.SubElement(rewards_el, "reward")
        raw_d = sess.get("date", "")
        r_el.set("date", normalize_iso_date(raw_d))
        r_el.set("exp", str(sess.get("karma", 0)))
        r_el.set("money", str(sess.get("nuyen", 0)))

        t_el = ET.SubElement(r_el, "title")
        t_el.text = sess.get("title", "Mission")

        if sess.get("gm"):
            gm_el = ET.SubElement(r_el, "gamemaster")
            gm_el.text = str(sess["gm"])

    try:
        ET.indent(root, space="   ", level=0)
    except Exception:
        pass

    xml_str = ET.tostring(root, encoding="utf-8").decode("utf-8")
    return '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n' + xml_str


def generate_commlink_metadata(
    char_data: Dict[str, Any],
    char_uuid: str,
    xml_filename: str,
    attachment_uuid: Optional[str] = None
) -> str:
    """Generates standard metadata.properties file required by CommLink 6 player save directories."""
    att_id = attachment_uuid or str(uuid.uuid4())
    identity = char_data.get("identity", {})
    name = identity.get("handle") or identity.get("name", "Runner")
    meta = identity.get("metatype", "Human")
    archetype = identity.get("archetype") or identity.get("role", "")
    mortype = identity.get("mortype", "")
    gender = str(identity.get("gender", "diverse")).lower()
    desc_parts = [p for p in [meta, mortype or archetype, gender] if p]
    desc = ", ".join(desc_parts) or "Shadowrun 6th Edition Character"

    return (
        "#Do not edit\n"
        f"attachment.{att_id}.type=CHARACTER\n"
        f"name={name}\n"
        f"attachment.{att_id}.format=RULESPECIFIC\n"
        f"attachment.{att_id}.file={xml_filename}\n"
        f"uuid={char_uuid}\n"
        "sync=true\n"
        f"desc={desc}\n"
    )


def scan_commlink_player_saves(player_dir: Optional[str] = None) -> Dict[str, Dict[str, str]]:
    """
    Scans CommLink 6 player directory for character folders and returns mapping of
    canonical character IDs (reiko, velvet, venn) to save folder & XML paths.
    """
    target_dir = player_dir or DEFAULT_COMMLINK_PLAYER_DIR
    if not os.path.exists(target_dir):
        return {}

    saves: Dict[str, Dict[str, str]] = {}
    subdirs = [os.path.join(target_dir, d) for d in os.listdir(target_dir) if os.path.isdir(os.path.join(target_dir, d))]

    configured_chars = get_character_configs()
    known_aliases = dict(KNOWN_CHAR_ALIASES)
    configured_uuids = {}

    for cid, cfg in configured_chars.items():
        known_aliases[cid.lower()] = cid
        cname = cfg.get("name", "").lower()
        if cname:
            known_aliases[cname] = cid
        for al in cfg.get("aliases", []):
            known_aliases[str(al).lower()] = cid
        if "commlink_uuid" in cfg:
            configured_uuids[cfg["commlink_uuid"].lower()] = cid

    for sdir in subdirs:
        folder_uuid = os.path.basename(sdir).lower()
        meta_path = os.path.join(sdir, "metadata.properties")
        meta_name = None
        meta_file = None
        att_uuid = None

        if os.path.exists(meta_path):
            try:
                with open(meta_path, "r", encoding="utf-8", errors="ignore") as mf:
                    for line in mf:
                        line = line.strip()
                        if line.startswith("name="):
                            meta_name = line.split("=", 1)[1].strip()
                        elif ".file=" in line:
                            meta_file = line.split("=", 1)[1].strip()
                            parts = line.split(".file=")[0].split(".")
                            if len(parts) >= 2:
                                att_uuid = parts[1]
            except Exception:
                pass

        xml_files = glob.glob(os.path.join(sdir, "*.xml"))
        if meta_file and os.path.exists(os.path.join(sdir, meta_file)):
            xml_files = [os.path.join(sdir, meta_file)]

        cid = configured_uuids.get(folder_uuid)
        if not cid and meta_name:
            mn_lower = meta_name.lower().strip()
            for alias, target_cid in known_aliases.items():
                if alias in mn_lower or mn_lower in alias:
                    cid = target_cid
                    break

        if not cid and xml_files:
            fn_base = os.path.basename(xml_files[0]).replace(".xml", "").lower().strip()
            for alias, target_cid in known_aliases.items():
                if alias in fn_base or fn_base in alias:
                    cid = target_cid
                    break

        if not cid:
            cid = folder_uuid

        xml_path = xml_files[0] if xml_files else os.path.join(sdir, f"character.xml")
        saves[cid] = {
            "char_id": cid,
            "char_uuid": folder_uuid,
            "attachment_uuid": att_uuid,
            "folder_path": sdir,
            "xml_filename": os.path.basename(xml_path),
            "xml_path": xml_path,
            "metadata_path": meta_path if os.path.exists(meta_path) else None,
            "character_name": meta_name
        }

    return saves


def export_to_commlink(
    char_id: str,
    player_dir: Optional[str] = None,
    explicit_uuid: Optional[str] = None,
    output_xml_path: Optional[str] = None
) -> Tuple[bool, str, Dict[str, Any]]:
    """
    Exports a character sheet de novo from SR6 Core master files into CommLink 6 player saves.
    Writes to player/myself/shadowrun6/<UUID>/ and updates metadata.properties.
    Also exports to character's local output/<char_id>_sheet.xml.
    """
    from sr6core.character.manager import CharacterManager

    target_dir = player_dir or DEFAULT_COMMLINK_PLAYER_DIR
    cm = CharacterManager()
    char = cm.get_character(char_id)
    if not char or not char.get("data"):
        return False, f"Character data for '{char_id}' not found in master workspace.", {}

    repo_path = char.get("config", {}).get("repo_path") or cm.get_character_repo_dir(char_id)
    identity = char["data"].get("identity", {})
    handle = identity.get("handle") or identity.get("name", char_id.title())

    # Generate validated de novo CommLink XML
    try:
        xml_content = export_commlink_xml(
            char_data=char["data"],
            char_repo_path=repo_path
        )
    except Exception as e:
        return False, f"Failed generating de novo XML for '{char_id}': {e}", {}

    # Always write to local repository output/<char_id>_sheet.xml if repo_path exists
    if repo_path and os.path.exists(repo_path):
        out_sheet_dir = os.path.join(repo_path, "output")
        os.makedirs(out_sheet_dir, exist_ok=True)
        local_xml_path = os.path.join(out_sheet_dir, f"{char_id}_sheet.xml")
        try:
            with open(local_xml_path, "w", encoding="utf-8") as f:
                f.write(xml_content)
        except Exception:
            pass

    # If explicit custom output path specified, write there and return
    if output_xml_path:
        os.makedirs(os.path.dirname(os.path.abspath(output_xml_path)), exist_ok=True)
        with open(output_xml_path, "w", encoding="utf-8") as f:
            f.write(xml_content)
        return True, f"Exported CommLink XML for '{char_id}' to '{output_xml_path}'.", {"path": output_xml_path}

    # Resolve CommLink player directory save target
    saves = scan_commlink_player_saves(target_dir)
    cfg = char.get("config", {})
    target_uuid = explicit_uuid or cfg.get("commlink_uuid")

    save_info = None
    if target_uuid:
        for s in saves.values():
            if s["char_uuid"].lower() == target_uuid.lower():
                save_info = s
                break

    if not save_info and char_id in saves:
        save_info = saves[char_id]

    if save_info:
        sdir = save_info["folder_path"]
        xml_path = save_info["xml_path"]
        meta_path = save_info.get("metadata_path")

        with open(xml_path, "w", encoding="utf-8") as f:
            f.write(xml_content)

        if meta_path and os.path.exists(meta_path):
            try:
                with open(meta_path, "r", encoding="utf-8", errors="ignore") as mf:
                    lines = mf.readlines()
                new_lines = []
                for line in lines:
                    if line.startswith("name="):
                        new_lines.append(f"name={handle}\n")
                    else:
                        new_lines.append(line)
                with open(meta_path, "w", encoding="utf-8") as mf:
                    mf.writelines(new_lines)
            except Exception:
                pass

        return True, f"Successfully exported '{char_id}' to CommLink 6 save at '{xml_path}'.", {
            "folder": sdir,
            "xml_path": xml_path,
            "char_uuid": save_info["char_uuid"]
        }

    elif target_uuid:
        # User defined a specific UUID in config, create folder
        sdir = os.path.join(target_dir, target_uuid)
        os.makedirs(sdir, exist_ok=True)
        xml_filename = f"{handle}.xml"
        xml_path = os.path.join(sdir, xml_filename)
        meta_path = os.path.join(sdir, "metadata.properties")

        meta_content = generate_commlink_metadata(
            char_data=char["data"],
            char_uuid=target_uuid,
            xml_filename=xml_filename
        )
        with open(meta_path, "w", encoding="utf-8") as mf:
            mf.write(meta_content)

        with open(xml_path, "w", encoding="utf-8") as f:
            f.write(xml_content)

        return True, f"Provisioned and exported '{char_id}' to CommLink 6 save at '{xml_path}'.", {
            "folder": sdir,
            "xml_path": xml_path,
            "char_uuid": target_uuid
        }

    else:
        # CommLink directory exists, but no matching folder found
        if os.path.exists(target_dir):
            msg = (
                f"Exported local sheet to '{repo_path}/output/{char_id}_sheet.xml'.\n"
                f"To link directly into CommLink 6, create a blank character in CommLink 6 and add its UUID to characters.yaml:\n"
                f"  {char_id}:\n"
                f"    commlink_uuid: \"<UUID>\""
            )
            return True, msg, {"local_sheet": f"{repo_path}/output/{char_id}_sheet.xml"}
        else:
            return True, f"Exported local sheet to '{repo_path}/output/{char_id}_sheet.xml'.", {
                "local_sheet": f"{repo_path}/output/{char_id}_sheet.xml"
            }

