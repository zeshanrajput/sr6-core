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
        sk_el.set("ref", sk_ref)
        sk_el.set("uuid", str(uuid.uuid4()))
        sk_el.set("value", str(s.get("rating", 1)))
        if "specialization" in s and s["specialization"]:
            dec_el = ET.SubElement(sk_el, "decision")
            dec_el.set("choice", str(uuid.uuid4()))
            dec_el.set("value", s["specialization"])

    # Items / Gear / Drones
    items_el = ET.SubElement(root, "items")
    gear_items = char_data.get("gear", []) + char_data.get("drones", [])
    for g in gear_items:
        g_el = ET.SubElement(items_el, "item")
        g_el.set("lang", "en")
        g_mode = g.get("mode", "CARRIED").upper()
        g_el.set("mode", g_mode)
        g_ref = lookup_canonical_ref(g.get("ref") or g.get("name", ""), "gear", db_path=db_path)
        g_el.set("ref", g_ref)
        g_el.set("uuid", str(uuid.uuid4()))

        # If drone lists Satellite Link in master YAML modifications, append accessory
        mods = [str(m).lower() for m in g.get("modifications", [])]
        if any("satellite" in m for m in mods):
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
        old_ds = root.find("datastructures")
        if old_ds is not None:
            root.remove(old_ds)

        # DYNAMIC SATELLITE LINK SYNC BASED ON MASTER YAML MODIFICATIONS
        drone_refs_with_sat = set()
        for drone in char_data.get("drones", []):
            d_ref = lookup_canonical_ref(drone.get("ref") or drone.get("name", ""), "gear", db_path=db_path)
            mods = [str(m).lower() for m in drone.get("modifications", [])]
            if any("satellite" in m for m in mods):
                drone_refs_with_sat.add(d_ref)

        items_container = root.find("items")
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
