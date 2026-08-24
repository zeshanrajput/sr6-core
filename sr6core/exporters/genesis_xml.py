"""
Genesis / CommLink6 XML Serializer for SR6.
Generates 100% CommLink6-compliant character XML files strictly matching CommLink6 Unmarshaller3 Java schema.
Fixes karmaF (karmaFree = available karma) and karmaI (karmaInvested = spent karma).
Dynamically synchronizes drone modifications (such as Satellite Link) from character YAML data without hardcoding.
"""

import os
import re
import uuid
import sqlite3
import xml.etree.ElementTree as ET
from typing import Dict, Any, Optional

from sr6core.rules_db import DEFAULT_DB_PATH
from sr6core.log_engine import get_log_totals
from sr6core.srm_contacts import get_official_srm_contact

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


def map_contact_type_enum(type_str: str) -> str:
    """Maps a free-text archetype or type string to a valid CommLink6 ContactType enum."""
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
    """Converts dates like '2026-Apr-24' or '2026-04-24' to full ISO-8601 '2026-04-24T00:00:00.000Z' for Java SimplePersist."""
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


def lookup_canonical_ref(item_name_or_ref: str, category: str, db_path: str = DEFAULT_DB_PATH) -> str:
    if not item_name_or_ref:
        return "unknown"

    clean_str = item_name_or_ref.strip()
    norm_str = clean_str.lower().replace(" ", "_")

    tbl_map = {
        "quality": "ref_qualities",
        "spell": "ref_spells",
        "complex_form": "ref_complex_forms",
        "gear": "ref_gear",
        "contact": "ref_contacts"
    }
    tbl = tbl_map.get(category, "ref_gear")

    if not os.path.exists(db_path):
        return norm_str

    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        row = cursor.execute(
            f"SELECT id FROM {tbl} WHERE id = ? OR lower(id) = ? OR lower(name) = ?",
            (clean_str, norm_str, clean_str.lower())
        ).fetchone()
        conn.close()
        if row:
            return row[0]
    except Exception:
        pass

    return norm_str


def is_software_ref(ref_str: str, slot_str: str = "") -> bool:
    if slot_str == "SOFTWARE":
        return True
    r = ref_str.lower()
    return any(p in r for p in [
        "soft_", "browse", "clearsight", "decryption", "edit", "evasion", "fork",
        "stealth", "targeting", "emulator", "sneak", "artillery", "ecm", "mapsoft",
        "baby_monitor", "social_hud", "hitchhiker", "maneuvering", "mannequin",
        "mefeed", "nexus_protocol", "overclock", "trace", "thermal_mood", "vocal_tension",
        "smart_rig", "shopsoft", "mobile_medic", "swarm_rig", "target_artist", "p-ice"
    ])


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


def get_all_character_items(char_data: Dict[str, Any]) -> list:
    """Gathers all items across weapons, armors, matrix_devices, software, items, gear, and drones."""
    all_raw = []
    for sec in ["weapons", "armors", "matrix_devices", "items", "gear", "drones"]:
        val = char_data.get(sec, [])
        all_raw.extend(_safe_item_list(val))

    res = []
    for item in all_raw:
        if isinstance(item, dict):
            res.append(item)
        elif isinstance(item, str):
            res.append({"name": item, "ref": item})
    return res


def is_valid_gear_template(ref_str: Optional[str], db_path: str = DEFAULT_DB_PATH) -> bool:
    if not ref_str or ref_str in ["software_library", "qi_focus", "unknown"]:
        return False
    if not os.path.exists(db_path):
        return True
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        row = cursor.execute("SELECT id FROM ref_gear WHERE id = ?", (ref_str,)).fetchone()
        conn.close()
        return row is not None
    except Exception:
        return True


def export_genesis_xml(char_data: Dict[str, Any], char_repo_path: Optional[str] = None, db_path: str = DEFAULT_DB_PATH) -> str:
    """
    Generates a 100% CommLink6 compliant XML document matching Java Unmarshaller3 schema.
    """
    log_totals = get_log_totals(char_repo_path) if char_repo_path and os.path.exists(char_repo_path) else {}

    root = ET.Element("sr6char")
    identity = char_data.get("identity", {})

    nuyen_val = int(log_totals.get("Nuyen", 5000))
    karma_avail = int(log_totals.get("Karma", 0))
    karma_life = int(log_totals.get("Lifetime_Karma", karma_avail))
    karma_spent = max(0, karma_life - karma_avail)

    root.set("gender", str(identity.get("gender", "MALE")).upper())
    root.set("meta", str(identity.get("metatype", "human")).lower())
    root.set("karmaF", str(karma_avail))
    root.set("karmaI", str(karma_spent))
    root.set("nuyen", str(nuyen_val))

    # Name node
    name_el = ET.SubElement(root, "name")
    name_el.text = identity.get("handle", "Unknown")

    # Real Name node
    if "real_name" in identity:
        real_el = ET.SubElement(root, "realName")
        real_el.text = identity["real_name"]

    # Attributes
    attrs_el = ET.SubElement(root, "attributes")
    attrs = char_data.get("attributes", {})
    for attr, val in attrs.items():
        if attr.lower() in ["essence", "power_points"]:
            continue
        attr_el = ET.SubElement(attrs_el, "attributes")
        attr_el.set("id", attr.upper())
        attr_el.set("value", str(val))

    # Qualities
    qualities_el = ET.SubElement(root, "qualities")
    pos_qualities = char_data.get("qualities", {}).get("positive", [])
    neg_qualities = char_data.get("qualities", {}).get("negative", [])

    for q in pos_qualities + neg_qualities:
        q_el = ET.SubElement(qualities_el, "quality")
        q_el.set("lang", "en")
        q_ref = lookup_canonical_ref(q.get("ref") or q.get("name", ""), "quality", db_path=db_path)
        q_el.set("ref", q_ref)
        q_el.set("uuid", str(uuid.uuid4()))
        if "rating" in q and q["rating"] > 1:
            q_el.set("value", str(q["rating"]))
        if "choice" in q:
            dec_el = ET.SubElement(q_el, "decision")
            dec_el.set("choice", str(uuid.uuid4()))
            dec_el.set("value", str(q["choice"]))

    # Skills
    skills_el = ET.SubElement(root, "skills")
    for s in char_data.get("skills", []):
        sk_el = ET.SubElement(skills_el, "skill")
        sk_el.set("lang", "en")
        sk_ref = s.get("id", s.get("name", "").lower().replace(" ", "_"))
        if s.get("is_knowledge"):
            sk_el.set("ref", "knowledge")
            sk_el.set("uuid", str(uuid.uuid4()))
            sk_el.set("value", str(s.get("rating", 1)))
            dec_el = ET.SubElement(sk_el, "decision")
            dec_el.set("choice", "89ebc659-ba06-4732-b347-6b832842a55b")
            dec_el.set("value", s.get("name", ""))
        elif sk_ref == "language":
            sk_el.set("ref", "language")
            sk_el.set("uuid", str(uuid.uuid4()))
            sk_el.set("value", str(s.get("rating", 1)))
            dec_el = ET.SubElement(sk_el, "decision")
            dec_el.set("choice", "a7103ee4-31fa-435d-ac42-08f7d4d1e80c")
            dec_el.set("value", s.get("name", "Native Language"))
        else:
            sk_el.set("ref", sk_ref)
            sk_el.set("uuid", str(uuid.uuid4()))
            sk_el.set("value", str(s.get("rating", 1)))
            if "specialization" in s and s["specialization"]:
                spec_el = ET.SubElement(sk_el, "skillspec")
                spec_el.set("lang", "en")
                spec_el.set("ref", s["specialization"].lower().replace(" ", "_"))

    # Spells
    spells = char_data.get("spells", [])
    if spells:
        spells_el = ET.SubElement(root, "spells")
        for sp in spells:
            sp_el = ET.SubElement(spells_el, "spell")
            sp_el.set("lang", "en")
            sp_ref = lookup_canonical_ref(sp.get("ref") or sp.get("name", ""), "spell", db_path=db_path)
            sp_el.set("ref", sp_ref)

    # Adept Powers
    powers = char_data.get("adept_powers", [])
    if powers:
        powers_el = ET.SubElement(root, "adeptPowers")
        for p in powers:
            if p.get("source"):
                continue
            p_el = ET.SubElement(powers_el, "adeptpower")
            p_el.set("lang", "en")
            p_ref = p.get("ref") or p.get("name", "").lower().replace(" ", "_")
            p_el.set("ref", p_ref)
            if "rating" in p and int(p["rating"]) > 0:
                p_el.set("value", str(p["rating"]))

    # Meta Echoes / Metamagics / Submersion Echoes
    meta_echoes = char_data.get("meta_echoes", [])
    if meta_echoes:
        echoes_el = ET.SubElement(root, "metaEchoes")
        for me in meta_echoes:
            me_el = ET.SubElement(echoes_el, "metaEcho")
            me_el.set("lang", "en")
            me_ref = me.get("ref") or me.get("name", "").lower().replace(" ", "_")
            me_el.set("ref", me_ref)

    # Complex Forms
    cforms = char_data.get("complex_forms", [])
    if cforms:
        cf_el = ET.SubElement(root, "complexforms")
        for cf in cforms:
            c_el = ET.SubElement(cf_el, "complexforms")
            c_el.set("lang", "en")
            c_ref = lookup_canonical_ref(cf.get("ref") or cf.get("name", ""), "complex_form", db_path=db_path)
            c_el.set("ref", c_ref)

    # Items / Gear / Weapons / Armor / Devices / Drones
    items_el = ET.SubElement(root, "items")
    gear_items = get_all_character_items(char_data)
    for g in gear_items:
        g_ref = lookup_canonical_ref(g.get("ref") or g.get("name", ""), "gear", db_path=db_path)
        if not is_valid_gear_template(g_ref, db_path=db_path):
            continue

        g_el = ET.SubElement(items_el, "item")
        g_el.set("lang", "en")
        g_mode = g.get("mode", "CARRIED").upper()
        g_el.set("mode", g_mode)
        g_el.set("ref", g_ref)
        g_el.set("uuid", str(uuid.uuid4()))

        count_val = g.get("qty") or g.get("count", 1)
        if count_val and int(count_val) > 1:
            g_el.set("count", str(count_val))

        rating_val = g.get("rating")
        if rating_val and int(rating_val) > 0 and g_ref in ["contacts", "earbuds", "personal_assistant"]:
            dec_el = ET.SubElement(g_el, "decision")
            dec_el.set("choice", "c2d17c87-1cfe-4355-9877-a20fe09c170d")
            dec_el.set("value", str(rating_val))

        # Check accessories
        accs = g.get("accessories", [])
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
                a_sub.set("uuid", str(uuid.uuid4()))

        # If drone lists Satellite Link in master YAML modifications, append accessory
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

    # Contacts
    contacts_el = ET.SubElement(root, "contacts")
    merged_contacts = {}

    for c in char_data.get("contacts", []):
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
        if "notes" in c and c["notes"]:
            desc_el = ET.SubElement(c_el, "description")
            desc_el.text = str(c["notes"])
        elif "description" in c and c["description"]:
            desc_el = ET.SubElement(c_el, "description")
            desc_el.text = str(c["description"])

    # Rewards / Session History (<title> and <gamemaster> child tags)
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

    # XML formatting
    try:
        ET.indent(root, space="   ", level=0)
    except Exception:
        pass

    xml_str = ET.tostring(root, encoding="utf-8").decode("utf-8")
    return '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n' + xml_str


def patch_genesis_xml(input_xml_path: str, char_data: Dict[str, Any], output_xml_path: str, char_repo_path: Optional[str] = None, db_path: str = DEFAULT_DB_PATH) -> bool:
    if not os.path.exists(input_xml_path):
        return False

    try:
        log_totals = get_log_totals(char_repo_path) if char_repo_path and os.path.exists(char_repo_path) else {}

        tree = ET.parse(input_xml_path)
        root = tree.getroot()

        # Remove root 'name' attribute if present
        if "name" in root.attrib:
            del root.attrib["name"]

        identity = char_data.get("identity", {})
        if "handle" in identity:
            name_el = root.find("name")
            if name_el is not None:
                name_el.text = identity["handle"]
        if "real_name" in identity:
            real_name_el = root.find("realName")
            if real_name_el is not None:
                real_name_el.text = identity["real_name"]

        # Update root Karma and Nuyen totals from log totals
        nuyen_val = int(log_totals.get("Nuyen", 5000))
        karma_avail = int(log_totals.get("Karma", 0))
        karma_life = int(log_totals.get("Lifetime_Karma", karma_avail))
        karma_spent = max(0, karma_life - karma_avail)

        root.set("nuyen", str(nuyen_val))
        root.set("karmaF", str(karma_avail))
        root.set("karmaI", str(karma_spent))

        # Remove invalid <sessionlogs> or <datastructures> tag if present
        old_logs = root.find("sessionlogs")
        if old_logs is not None:
            root.remove(old_logs)
        # DYNAMIC SKILLS SYNC FROM MASTER YAML
        skills_el = root.find("skills")
        if skills_el is None:
            skills_el = ET.SubElement(root, "skills")

        existing_skills_by_ref = {}
        for sk_node in skills_el.findall("skill"):
            r = sk_node.get("ref")
            if r:
                existing_skills_by_ref.setdefault(r, []).append(sk_node)

        for s in char_data.get("skills", []):
            sk_id = s.get("id", s.get("name", "").lower().replace(" ", "_"))
            rating_str = str(s.get("rating", 1))

            if s.get("is_knowledge"):
                k_name = s.get("name", "")
                k_match = None
                for kn in existing_skills_by_ref.get("knowledge", []):
                    dec = kn.find("decision")
                    if dec is not None and dec.get("value") == k_name:
                        k_match = kn
                        break
                if k_match is not None:
                    k_match.set("value", rating_str)
                else:
                    new_k = ET.SubElement(skills_el, "skill")
                    new_k.set("lang", "en")
                    new_k.set("ref", "knowledge")
                    new_k.set("uuid", str(uuid.uuid4()))
                    new_k.set("value", rating_str)
                    dec_el = ET.SubElement(new_k, "decision")
                    dec_el.set("choice", "89ebc659-ba06-4732-b347-6b832842a55b")
                    dec_el.set("value", k_name)
                    existing_skills_by_ref.setdefault("knowledge", []).append(new_k)
            elif sk_id == "language":
                lang_name = s.get("name", "Native Language")
                l_match = None
                for ln in existing_skills_by_ref.get("language", []):
                    l_match = ln
                    break
                if l_match is not None:
                    l_match.set("value", rating_str)
                else:
                    new_l = ET.SubElement(skills_el, "skill")
                    new_l.set("lang", "en")
                    new_l.set("ref", "language")
                    new_l.set("uuid", str(uuid.uuid4()))
                    new_l.set("value", rating_str)
                    dec_el = ET.SubElement(new_l, "decision")
                    dec_el.set("choice", "a7103ee4-31fa-435d-ac42-08f7d4d1e80c")
                    dec_el.set("value", lang_name)
                    existing_skills_by_ref.setdefault("language", []).append(new_l)
            else:
                sk_match = None
                if sk_id in existing_skills_by_ref and existing_skills_by_ref[sk_id]:
                    sk_match = existing_skills_by_ref[sk_id][0]

                if sk_match is not None:
                    sk_match.set("value", rating_str)
                else:
                    sk_match = ET.SubElement(skills_el, "skill")
                    sk_match.set("lang", "en")
                    sk_match.set("ref", sk_id)
                    sk_match.set("uuid", str(uuid.uuid4()))
                    sk_match.set("value", rating_str)
                    existing_skills_by_ref.setdefault(sk_id, []).append(sk_match)

                # Sync specialization (<skillspec>)
                spec_val = s.get("specialization")
                if spec_val:
                    spec_ref = spec_val.lower().replace(" ", "_")
                    spec_node = sk_match.find("skillspec")
                    if spec_node is None:
                        spec_node = ET.SubElement(sk_match, "skillspec")
                        spec_node.set("lang", "en")
                    spec_node.set("ref", spec_ref)
                else:
                    spec_node = sk_match.find("skillspec")
                    if spec_node is not None:
                        sk_match.remove(spec_node)

        # DYNAMIC ITEMS & GEAR SYNC FROM MASTER YAML
        items_container = root.find("items")
        if items_container is None:
            items_container = ET.SubElement(root, "items")

        # Clean out invalid or unresolvable items (e.g. software_library, qi_focus)
        for item_node in list(items_container.findall("item")):
            ref_val = item_node.get("ref")
            if not is_valid_gear_template(ref_val, db_path=db_path):
                items_container.remove(item_node)
            elif ref_val not in ["contacts", "earbuds", "personal_assistant"]:
                for dec in list(item_node.findall("decision")):
                    item_node.remove(dec)

        all_char_items = get_all_character_items(char_data)
        existing_item_map = {}
        for item_node in items_container.findall("item"):
            ref_val = item_node.get("ref")
            if ref_val:
                existing_item_map.setdefault(ref_val, []).append(item_node)

        for g in all_char_items:
            g_ref = lookup_canonical_ref(g.get("ref") or g.get("name", ""), "gear", db_path=db_path)
            if not is_valid_gear_template(g_ref, db_path=db_path):
                continue

            count_val = g.get("qty") or g.get("count", 1)

            rating_val = g.get("rating")
            if g_ref in existing_item_map:
                # Item exists, update count if specified
                node = existing_item_map[g_ref][0]
                if count_val and int(count_val) > 1:
                    node.set("count", str(count_val))
                if rating_val and int(rating_val) > 0 and g_ref in ["contacts", "earbuds", "personal_assistant"]:
                    dec = node.find("decision")
                    if dec is None:
                        dec = ET.SubElement(node, "decision")
                        dec.set("choice", "c2d17c87-1cfe-4355-9877-a20fe09c170d")
                    dec.set("value", str(rating_val))
            else:
                # Add newly acquired item
                new_item = ET.SubElement(items_container, "item")
                new_item.set("lang", "en")
                new_item.set("mode", g.get("mode", "CARRIED").upper())
                new_item.set("ref", g_ref)
                new_item.set("uuid", str(uuid.uuid4()))
                if count_val and int(count_val) > 1:
                    new_item.set("count", str(count_val))

                if rating_val and int(rating_val) > 0 and g_ref in ["contacts", "earbuds", "personal_assistant"]:
                    dec_el = ET.SubElement(new_item, "decision")
                    dec_el.set("choice", "c2d17c87-1cfe-4355-9877-a20fe09c170d")
                    dec_el.set("value", str(rating_val))

                existing_item_map.setdefault(g_ref, []).append(new_item)

        # DYNAMIC SATELLITE LINK SYNC BASED ON MASTER YAML MODIFICATIONS
        drone_refs_with_sat = set()
        for drone in char_data.get("drones", []):
            d_ref = lookup_canonical_ref(drone.get("ref") or drone.get("name", ""), "gear", db_path=db_path)
            mods = [str(m).lower() for m in drone.get("modifications", [])]
            if any("satellite" in m for m in mods):
                drone_refs_with_sat.add(d_ref)

        if items_container is not None and drone_refs_with_sat:
            for item in items_container.findall("item"):
                if item.get("ref") in drone_refs_with_sat:
                    acc_el = item.find("accessories")
                    if acc_el is None:
                        acc_el = ET.SubElement(item, "accessories")

                    existing_accs = [sub.get("ref") for sub in acc_el.findall("item")]
                    if "satellite_link" not in existing_accs:
                        sat_el = ET.SubElement(acc_el, "item")
                        sat_el.set("lang", "en")
                        sat_el.set("mode", "EMBEDDED")
                        sat_el.set("ref", "satellite_link")
                        sat_el.set("slot", "VEHICLE_ELECTRONICS")
                        sat_el.set("uuid", str(uuid.uuid4()))

        # DYNAMIC METAECHOES / METAMAGICS SYNC
        meta_echoes = char_data.get("meta_echoes", [])
        if meta_echoes:
            echoes_container = root.find("metaEchoes")
            if echoes_container is None:
                echoes_container = ET.SubElement(root, "metaEchoes")

            existing_echoes = {e.get("ref") for e in echoes_container.findall("metaEcho") if e.get("ref")}
            for me in meta_echoes:
                me_ref = me.get("ref") or me.get("name", "").lower().replace(" ", "_")
                if me_ref not in existing_echoes:
                    me_el = ET.SubElement(echoes_container, "metaEcho")
                    me_el.set("lang", "en")
                    me_el.set("ref", me_ref)
                    existing_echoes.add(me_ref)

        # DYNAMIC SPELLS SYNC
        spells = char_data.get("spells", [])
        if spells:
            spells_container = root.find("spells")
            if spells_container is None:
                spells_container = ET.SubElement(root, "spells")

            existing_spells = {s.get("ref") for s in spells_container.findall("spell") if s.get("ref")}
            for sp in spells:
                sp_ref = lookup_canonical_ref(sp.get("ref") or sp.get("name", ""), "spell", db_path=db_path)
                if sp_ref not in existing_spells:
                    sp_el = ET.SubElement(spells_container, "spell")
                    sp_el.set("lang", "en")
                    sp_el.set("ref", sp_ref)
                    existing_spells.add(sp_ref)

        # Remove bad complexForms tag if present
        bad_cf = root.find("complexForms")
        if bad_cf is not None:
            root.remove(bad_cf)

        # DYNAMIC COMPLEX FORMS SYNC
        cforms = char_data.get("complex_forms", [])
        if cforms:
            cf_container = root.find("complexforms")
            if cf_container is None:
                cf_container = ET.SubElement(root, "complexforms")

            # Remove any singular <complexform> elements which cause schema rejection in CommLink6
            for old_singular in list(cf_container.findall("complexform")):
                cf_container.remove(old_singular)

            existing_cfs = set()
            for c in list(cf_container.findall("complexforms")):
                r = c.get("ref")
                if r in existing_cfs:
                    cf_container.remove(c)
                elif r:
                    existing_cfs.add(r)

            for cf in cforms:
                cf_ref = lookup_canonical_ref(cf.get("ref") or cf.get("name", ""), "complex_form", db_path=db_path)
                if cf_ref not in existing_cfs:
                    c_el = ET.SubElement(cf_container, "complexforms")
                    c_el.set("lang", "en")
                    c_el.set("ref", cf_ref)
                    existing_cfs.add(cf_ref)

        # Update contacts while standardizing against SRM database and preserving <description> child tag
        contacts_el = root.find("contacts")
        if contacts_el is None:
            contacts_el = ET.SubElement(root, "contacts")

        merged_contacts = {c.get("name"): c for c in char_data.get("contacts", []) if c.get("name")}
        if log_totals.get("Contacts"):
            for cname, cinfo in log_totals["Contacts"].items():
                if cname in merged_contacts:
                    merged_contacts[cname].update(cinfo)
                else:
                    merged_contacts[cname] = cinfo

        existing_contacts = {c.get("name"): c for c in contacts_el.findall("contact") if c.get("name")}

        for cname, cinfo in merged_contacts.items():
            if cname in existing_contacts:
                c_el = existing_contacts[cname]
            else:
                c_el = ET.SubElement(contacts_el, "contact")
                c_el.set("name", cname)

            if "uuid" in c_el.attrib:
                del c_el.attrib["uuid"]

            # Check if this contact is an official SRM named contact
            srm_info = get_official_srm_contact(cname, db_path=db_path)
            if srm_info:
                c_el.set("rat", str(srm_info["connection"]))
                c_el.set("type", map_contact_type_enum(srm_info["types"]))
                c_el.set("typename", str(srm_info["archetype"]))
            else:
                if "connection" in cinfo:
                    c_el.set("rat", str(cinfo["connection"]))
                type_raw = cinfo.get("type") or cinfo.get("archetype") or c_el.get("typename") or ""
                c_el.set("type", map_contact_type_enum(type_raw))
                c_el.set("typename", str(type_raw))

            if "loyalty" in cinfo:
                c_el.set("loy", str(cinfo["loyalty"]))
            if "favors" in cinfo:
                c_el.set("favors", str(cinfo["favors"]))

            note_text = cinfo.get("notes") or cinfo.get("description")
            if note_text:
                desc_el = c_el.find("description")
                if desc_el is None:
                    desc_el = ET.SubElement(c_el, "description")
                desc_el.text = str(note_text)

        # Rewards / Session History (Sample XML Schema: date, exp, money as attributes; <title> & <gamemaster> as child tags)
        rewards_el = root.find("rewards")
        if rewards_el is None:
            rewards_el = ET.SubElement(root, "rewards")
        else:
            rewards_el.clear()

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

        os.makedirs(os.path.dirname(output_xml_path) or ".", exist_ok=True)
        tree.write(output_xml_path, encoding="utf-8", xml_declaration=True)
        return True
    except Exception as e:
        print(f"Error patching Genesis XML: {e}")
        return False
