"""
CommLink6 Dataset Compiler for SR6.
Auto-detects and extracts official XML dataset files from CommLink6 JAR archives
into structured SQLite tables in rules_index.db.
"""

import os
import re
import glob
import json
import sqlite3
import zipfile
import xml.etree.ElementTree as ET
from typing import Dict, Any, List, Optional, Tuple

from sr6core.rules_db import DEFAULT_DB_PATH

COMMLINK_DEFAULT_DIR = r"C:\Users\zesha\CommLink6\app\stable"


def find_latest_commlink_jar(search_dir: str = COMMLINK_DEFAULT_DIR) -> Optional[str]:
    if not os.path.exists(search_dir):
        return None

    jar_pattern = os.path.join(search_dir, "commlink6-*-complete.jar")
    jars = glob.glob(jar_pattern)
    if not jars:
        jar_pattern = os.path.join(search_dir, "*.jar")
        jars = glob.glob(jar_pattern)

    if not jars:
        return None

    def parse_version(path: str) -> Tuple[int, ...]:
        filename = os.path.basename(path)
        match = re.search(r'commlink6-(\d+)\.(\d+)\.(\d+)', filename)
        if match:
            return (int(match.group(1)), int(match.group(2)), int(match.group(3)))
        return (0, 0, 0)

    sorted_jars = sorted(jars, key=parse_version, reverse=True)
    return sorted_jars[0]


def extract_modifications_json(elem: Any) -> str:
    """Extracts structured passive modifiers from XML modification elements."""
    if isinstance(elem, str):
        try:
            elem = ET.fromstring(elem)
        except Exception:
            return "[]"
    mods = []
    search_nodes = elem.findall(".//modifications/*") + elem.findall(".//bonus/*")
    for mod in search_nodes:
        tag = mod.tag.lower()
        if tag in ["valmod", "checkmod", "attrmod", "attribute"]:
            m_type = mod.get("type", "").lower()
            ref = (mod.get("ref") or mod.get("name", "")).lower()
            val_str = mod.get("value", "")
            what = mod.get("what", "")
            apply_to = mod.get("apply", "")
            is_rating = "$RATING" in val_str
            val_num = None
            try:
                val_num = float(val_str) if "." in val_str else int(val_str)
            except Exception:
                pass
            mods.append({
                "tag": tag,
                "type": m_type,
                "ref": ref,
                "raw_value": val_str,
                "value": val_num if val_num is not None else 1,
                "is_rating_multiplier": is_rating,
                "what": what,
                "apply": apply_to
            })
    return json.dumps(mods) if mods else "[]"


def extract_weapon_features(elem: Any) -> Dict[str, Any]:
    """Extracts weapon slots/mounts, requirements, and embedded accessories."""
    if isinstance(elem, str):
        try:
            elem = ET.fromstring(elem)
        except Exception:
            return {
                "mounts": "",
                "mount_top": 0, "mount_barrel": 0, "mount_under": 0, "mount_internal": 0,
                "requirements_json": "[]", "embedded_accessories_json": "[]", "modifiers_json": "[]"
            }

    mounts = []
    search_mounts = elem.findall(".//modifications/itemmod") + elem.findall(".//accessory_mounts/mount")
    for itemmod in search_mounts:
        if itemmod.get("type") == "HOOK" or itemmod.tag == "mount":
            ref = (itemmod.get("ref") or itemmod.get("id", "")).upper()
            if ref and ref not in mounts:
                mounts.append(ref)

    embedded = []
    search_embed = elem.findall(".//modifications/embed") + elem.findall(".//embedded_accessories/item")
    for emb in search_embed:
        embedded.append({
            "type": emb.get("type", "GEAR"),
            "ref": emb.get("ref") or emb.get("id", ""),
            "mount": emb.get("intoRef", ""),
            "included": emb.get("included", "false").lower() == "true"
        })

    reqs = []
    for req in elem.findall(".//requires/*"):
        reqs.append({
            "tag": req.tag,
            "type": req.get("type", ""),
            "ref": req.get("ref", ""),
            "value": req.get("value", "")
        })

    return {
        "mounts": ",".join(mounts),
        "mount_top": 1 if "TOP" in mounts else 0,
        "mount_barrel": 1 if "BARREL" in mounts else 0,
        "mount_under": 1 if "UNDER" in mounts else 0,
        "mount_internal": 1 if "INTERNAL" in mounts else 0,
        "requirements_json": json.dumps(reqs) if reqs else "[]",
        "embedded_accessories_json": json.dumps(embedded) if embedded else "[]",
        "modifiers_json": extract_modifications_json(elem)
    }


def extract_cyberware_stats(elem: Any) -> Tuple[float, int]:
    """Extracts base essence cost and price accounting for dynamic formulas or tables."""
    if isinstance(elem, str):
        try:
            elem = ET.fromstring(elem)
        except Exception:
            return 0.0, 0

    ess_str = elem.get("ess") or elem.get("essence")
    if not ess_str:
        usage = elem.find(".//usage[@mode='IMPLANTED']")
        if usage is not None:
            ess_str = usage.get("value")
        if not ess_str:
            attr = elem.find(".//attrdef[@id='ESSENCECOST']")
            if attr is not None:
                ess_str = attr.get("value")

    essence = 0.0
    if ess_str:
        val = ess_str.replace("$RATING", "1").replace("*", " * ")
        try:
            essence = float(eval(val, {"__builtins__": None}, {}))
        except Exception:
            pass

    cost_str = elem.get("cost") or elem.get("price")
    if not cost_str or cost_str == "0":
        attr = elem.find(".//attrdef[@id='PRICE']")
        if attr is not None:
            tbl = attr.get("table")
            if tbl:
                cost_str = tbl.split(",")[0]
            else:
                cost_str = attr.get("value")

    cost = 0
    if cost_str:
        val = cost_str.replace("$RATING", "1").replace("*", " * ")
        try:
            cost = int(float(eval(val, {"__builtins__": None}, {})))
        except Exception:
            pass

    return essence, cost



def migrate_existing_dataset_tables(conn: sqlite3.Connection):
    """Adds missing columns, views, and backfills existing dataset tables from raw_xml."""
    cursor = conn.cursor()
    
    # 1. ref_weapons
    try:
        w_cols = [r[1] for r in cursor.execute("PRAGMA table_info(ref_weapons)").fetchall()]
        if w_cols:
            for col_name, col_type in [
                ("mounts", "TEXT"),
                ("mount_top", "INTEGER DEFAULT 0"),
                ("mount_barrel", "INTEGER DEFAULT 0"),
                ("mount_under", "INTEGER DEFAULT 0"),
                ("mount_internal", "INTEGER DEFAULT 0"),
                ("requirements_json", "TEXT"),
                ("embedded_accessories_json", "TEXT"),
                ("modifiers_json", "TEXT")
            ]:
                if col_name not in w_cols:
                    cursor.execute(f"ALTER TABLE ref_weapons ADD COLUMN {col_name} {col_type}")

            # Backfill weapons if mounts or modifiers_json is NULL
            weapons = cursor.execute("SELECT id, raw_xml FROM ref_weapons WHERE mounts IS NULL OR modifiers_json IS NULL").fetchall()
            for wid, raw_xml in weapons:
                if not raw_xml:
                    continue
                try:
                    elem = ET.fromstring(raw_xml)
                    feats = extract_weapon_features(elem)
                    cursor.execute("""
                        UPDATE ref_weapons
                        SET mounts = ?, mount_top = ?, mount_barrel = ?, mount_under = ?, mount_internal = ?,
                            requirements_json = ?, embedded_accessories_json = ?, modifiers_json = ?
                        WHERE id = ?
                    """, (
                        feats["mounts"], feats["mount_top"], feats["mount_barrel"], feats["mount_under"],
                        feats["mount_internal"], feats["requirements_json"], feats["embedded_accessories_json"],
                        feats["modifiers_json"], wid
                    ))
                except Exception:
                    pass
    except Exception:
        pass

    # 2. ref_cyberware, ref_qualities, ref_spells, ref_adept_powers
    for tbl in ["ref_cyberware", "ref_qualities", "ref_spells", "ref_adept_powers"]:
        try:
            cols = [r[1] for r in cursor.execute(f"PRAGMA table_info({tbl})").fetchall()]
            if cols and "modifiers_json" not in cols:
                cursor.execute(f"ALTER TABLE {tbl} ADD COLUMN modifiers_json TEXT")
            if tbl == "ref_cyberware":
                items = cursor.execute("SELECT id, raw_xml FROM ref_cyberware WHERE modifiers_json IS NULL OR cost = 0 OR essence = 0.0").fetchall()
            else:
                items = cursor.execute(f"SELECT id, raw_xml FROM {tbl} WHERE modifiers_json IS NULL").fetchall()
            for iid, raw_xml in items:
                if not raw_xml:
                    continue
                try:
                    elem = ET.fromstring(raw_xml)
                    m_json = extract_modifications_json(elem)
                    if tbl == "ref_cyberware":
                        ess_parsed, cost_parsed = extract_cyberware_stats(elem)
                        cursor.execute("""
                            UPDATE ref_cyberware
                            SET modifiers_json = ?,
                                essence = CASE WHEN (essence = 0.0 OR essence IS NULL) AND ? > 0 THEN ? ELSE essence END,
                                cost = CASE WHEN (cost = 0 OR cost IS NULL) AND ? > 0 THEN ? ELSE cost END
                            WHERE id = ?
                        """, (m_json, ess_parsed, ess_parsed, cost_parsed, cost_parsed, iid))
                    else:
                        cursor.execute(f"UPDATE {tbl} SET modifiers_json = ? WHERE id = ?", (m_json, iid))
                except Exception:
                    pass
        except Exception:
            pass

    # 3. v_cyberware_grades View
    try:
        cursor.execute("DROP VIEW IF EXISTS v_cyberware_grades")
        cursor.execute("""
            CREATE VIEW IF NOT EXISTS v_cyberware_grades AS
            SELECT 
                id,
                name,
                category,
                essence AS standard_essence,
                cost AS standard_cost,
                ROUND(essence * 0.8, 2) AS alpha_essence,
                CAST(ROUND(cost * 1.2) AS INTEGER) AS alpha_cost,
                ROUND(essence * 0.7, 2) AS beta_essence,
                CAST(ROUND(cost * 1.5) AS INTEGER) AS beta_cost,
                ROUND(essence * 0.5, 2) AS delta_essence,
                CAST(ROUND(cost * 2.5) AS INTEGER) AS delta_cost,
                ROUND(essence * 1.2, 2) AS used_essence,
                CAST(ROUND(cost * 0.8) AS INTEGER) AS used_cost,
                capacity,
                avail,
                source,
                modifiers_json
            FROM ref_cyberware;
        """)
    except Exception:
        pass

    conn.commit()


def init_dataset_tables(conn: sqlite3.Connection):
    with conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS dataset_meta (
                key TEXT PRIMARY KEY,
                value TEXT
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS ref_qualities (
                id TEXT PRIMARY KEY,
                name TEXT,
                karma INTEGER,
                quality_type TEXT,
                max_rating INTEGER,
                source TEXT,
                raw_xml TEXT,
                modifiers_json TEXT
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS ref_spells (
                id TEXT PRIMARY KEY,
                name TEXT,
                category TEXT,
                drain TEXT,
                range TEXT,
                duration TEXT,
                source TEXT,
                raw_xml TEXT,
                modifiers_json TEXT
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS ref_complex_forms (
                id TEXT PRIMARY KEY,
                name TEXT,
                fade TEXT,
                duration TEXT,
                target TEXT,
                source TEXT,
                raw_xml TEXT
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS ref_gear (
                id TEXT PRIMARY KEY,
                name TEXT,
                category TEXT,
                cost INTEGER,
                avail TEXT,
                source TEXT,
                raw_xml TEXT
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS ref_weapons (
                id TEXT PRIMARY KEY,
                name TEXT,
                category TEXT,
                damage TEXT,
                ap TEXT,
                attack_rating TEXT,
                modes TEXT,
                ammo TEXT,
                cost INTEGER,
                avail TEXT,
                source TEXT,
                raw_xml TEXT,
                mounts TEXT,
                mount_top INTEGER DEFAULT 0,
                mount_barrel INTEGER DEFAULT 0,
                mount_under INTEGER DEFAULT 0,
                mount_internal INTEGER DEFAULT 0,
                requirements_json TEXT,
                embedded_accessories_json TEXT,
                modifiers_json TEXT
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS ref_cyberware (
                id TEXT PRIMARY KEY,
                name TEXT,
                category TEXT,
                essence REAL,
                capacity TEXT,
                cost INTEGER,
                avail TEXT,
                source TEXT,
                raw_xml TEXT,
                modifiers_json TEXT
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS ref_adept_powers (
                id TEXT PRIMARY KEY,
                name TEXT,
                cost REAL,
                max_rating INTEGER,
                source TEXT,
                raw_xml TEXT,
                modifiers_json TEXT
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS ref_vehicles (
                id TEXT PRIMARY KEY,
                name TEXT,
                category TEXT,
                handling TEXT,
                speed TEXT,
                accel TEXT,
                body INTEGER,
                armor INTEGER,
                sensor INTEGER,
                seats INTEGER,
                cost INTEGER,
                avail TEXT,
                source TEXT,
                raw_xml TEXT
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS ref_programs (
                id TEXT PRIMARY KEY,
                name TEXT,
                category TEXT,
                cost INTEGER,
                source TEXT,
                raw_xml TEXT
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS ref_metatypes (
                id TEXT PRIMARY KEY,
                name TEXT,
                raw_xml TEXT
            )
        """)
        migrate_existing_dataset_tables(conn)


def compile_commlink_datasets(jar_path: Optional[str] = None, db_path: str = DEFAULT_DB_PATH) -> Tuple[bool, str]:
    if not jar_path:
        jar_path = find_latest_commlink_jar()

    if not jar_path or not os.path.exists(jar_path):
        return False, f"CommLink6 JAR file not found at: {jar_path or COMMLINK_DEFAULT_DIR}"

    dirname = os.path.dirname(db_path)
    if dirname:
        os.makedirs(dirname, exist_ok=True)
    conn = sqlite3.connect(db_path)
    init_dataset_tables(conn)
    cursor = conn.cursor()

    jar_name = os.path.basename(jar_path)

    stats = {
        "qualities": 0,
        "spells": 0,
        "complex_forms": 0,
        "gear": 0,
        "weapons": 0,
        "cyberware": 0,
        "adept_powers": 0,
        "vehicles": 0,
        "programs": 0,
        "metatypes": 0
    }

    try:
        with zipfile.ZipFile(jar_path, "r") as z:
            namelist = z.namelist()
            data_files = [f for f in namelist if f.startswith("de/rpgframework/shadowrun6/data/") and f.endswith(".xml")]

            for df in data_files:
                parts = df.split("/")
                fname = parts[-1].lower()
                source_set = parts[4] if len(parts) > 4 else "core"

                try:
                    raw_bytes = z.read(df)
                    root = ET.fromstring(raw_bytes)
                except Exception:
                    continue

                # 1. Qualities
                if "qualities" in fname or root.tag == "qualities":
                    for q in root.findall(".//quality"):
                        qid = q.get("id")
                        if not qid:
                            continue
                        karma = int(q.get("karma", 0)) if q.get("karma", "").isdigit() else 0
                        pos = q.get("pos", "true").lower() == "true"
                        qtype = "positive" if pos else "negative"
                        max_r = int(q.get("max", 1)) if q.get("max", "").isdigit() else 1
                        name = q.get("name", qid.replace("_", " ").title())
                        raw_xml = ET.tostring(q, encoding="utf-8").decode("utf-8")
                        mods_json = extract_modifications_json(q)

                        cursor.execute(
                            "INSERT OR REPLACE INTO ref_qualities (id, name, karma, quality_type, max_rating, source, raw_xml, modifiers_json) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                            (qid, name, karma, qtype, max_r, source_set, raw_xml, mods_json)
                        )
                        stats["qualities"] += 1

                # 2. Spells
                elif "spells" in fname or root.tag == "spells":
                    for s in root.findall(".//spell"):
                        sid = s.get("id")
                        if not sid:
                            continue
                        name = s.get("name", sid.replace("_", " ").title())
                        cat = s.get("category", "General")
                        drain = s.get("drain", "F-2")
                        rng = s.get("range", "LOS")
                        dur = s.get("duration", "Instant")
                        raw_xml = ET.tostring(s, encoding="utf-8").decode("utf-8")
                        mods_json = extract_modifications_json(s)

                        cursor.execute(
                            "INSERT OR REPLACE INTO ref_spells (id, name, category, drain, range, duration, source, raw_xml, modifiers_json) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                            (sid, name, cat, drain, rng, dur, source_set, raw_xml, mods_json)
                        )
                        stats["spells"] += 1

                # 3. Complex Forms
                elif "complex" in fname or root.tag == "complexforms":
                    for cf in root.findall(".//complexform"):
                        cid = cf.get("id")
                        if not cid:
                            continue
                        name = cf.get("name", cid.replace("_", " ").title())
                        fade = cf.get("fade", "2")
                        dur = cf.get("duration", "Instant")
                        target = cf.get("target", "Device")
                        raw_xml = ET.tostring(cf, encoding="utf-8").decode("utf-8")

                        cursor.execute(
                            "INSERT OR REPLACE INTO ref_complex_forms VALUES (?, ?, ?, ?, ?, ?, ?)",
                            (cid, name, fade, dur, target, source_set, raw_xml)
                        )
                        stats["complex_forms"] += 1

                # 4. Adept Powers
                elif "power" in fname or root.tag == "powers":
                    for pow_elem in root.findall(".//power"):
                        pid = pow_elem.get("id")
                        if not pid:
                            continue
                        name = pow_elem.get("name", pid.replace("_", " ").title())
                        cost = float(pow_elem.get("cost", 0.5)) if pow_elem.get("cost", "").replace(".", "").isdigit() else 0.5
                        max_r = int(pow_elem.get("max", 1)) if pow_elem.get("max", "").isdigit() else 1
                        raw_xml = ET.tostring(pow_elem, encoding="utf-8").decode("utf-8")
                        mods_json = extract_modifications_json(pow_elem)

                        cursor.execute(
                            "INSERT OR REPLACE INTO ref_adept_powers (id, name, cost, max_rating, source, raw_xml, modifiers_json) VALUES (?, ?, ?, ?, ?, ?, ?)",
                            (pid, name, cost, max_r, source_set, raw_xml, mods_json)
                        )
                        stats["adept_powers"] += 1

                # 5. Gear, Weapons, Vehicles, Augmentations, Programs
                elif "gear" in fname or "weapon" in fname or "augment" in fname or "vehicle" in fname or "pack" in fname or root.tag in ["items", "gears", "weapons", "vehicles"]:
                    for item in root.findall(".//*"):
                        iid = item.get("id")
                        if not iid or item.tag in ["requires", "modifications"]:
                            continue
                        name = item.get("name", iid.replace("_", " ").title())
                        cost = int(item.get("cost", 0)) if item.get("cost", "").isdigit() else 0
                        avail = item.get("avail", "1")
                        raw_xml = ET.tostring(item, encoding="utf-8").decode("utf-8")

                        is_weapon = any(w in fname for w in ["firearm", "weapon", "melee", "underbarrel"]) or item.get("damage") or item.get("attack")
                        is_cyber = any(c in fname for c in ["cyberware", "bioware", "headware", "bodyware", "eyeware", "earware", "cyberlimb", "geneware", "nanoware"])
                        is_vehicle = any(v in fname for v in ["vehicle", "drone"])
                        is_program = "software" in fname or "program" in fname

                        if is_weapon:
                            dmg = item.get("damage", "-")
                            ap = item.get("ap", "0")
                            ar = item.get("ar", item.get("attack", "-"))
                            modes = item.get("mode", item.get("modes", "-"))
                            ammo = item.get("ammo", "-")
                            cat = item.get("category", fname.replace("gear_", "").replace(".xml", "").title())
                            w_feats = extract_weapon_features(item)
                            cursor.execute(
                                """INSERT OR REPLACE INTO ref_weapons 
                                   (id, name, category, damage, ap, attack_rating, modes, ammo, cost, avail, source,
                                    mounts, mount_top, mount_barrel, mount_under, mount_internal, requirements_json, embedded_accessories_json, modifiers_json, raw_xml)
                                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                                (iid, name, cat, dmg, ap, ar, modes, ammo, cost, avail, source_set,
                                 w_feats["mounts"], w_feats["mount_top"], w_feats["mount_barrel"], w_feats["mount_under"],
                                 w_feats["mount_internal"], w_feats["requirements_json"], w_feats["embedded_accessories_json"],
                                 w_feats["modifiers_json"], raw_xml)
                            )
                            stats["weapons"] += 1

                        elif is_cyber:
                            ess_parsed, cost_parsed = extract_cyberware_stats(item)
                            ess = ess_parsed if ess_parsed > 0.0 else (float(item.get("ess", item.get("essence", 0.0))) if item.get("ess", "").replace(".", "").isdigit() else 0.0)
                            cap = item.get("capacity", item.get("cap", "-"))
                            cat = item.get("category", fname.replace("gear_", "").replace(".xml", "").title())
                            cost = cost_parsed if cost_parsed > 0 else (int(item.get("cost", 0)) if item.get("cost", "").isdigit() else 0)
                            mods_json = extract_modifications_json(item)
                            cursor.execute(
                                """INSERT OR REPLACE INTO ref_cyberware 
                                   (id, name, category, essence, capacity, cost, avail, source, modifiers_json, raw_xml)
                                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                                (iid, name, cat, ess, cap, cost, avail, source_set, mods_json, raw_xml)
                            )
                            stats["cyberware"] += 1

                        elif is_vehicle:
                            v_elem = item.find("vehicle")
                            if v_elem is not None:
                                hnd = v_elem.get("han", item.get("handling", "-"))
                                spd = v_elem.get("tspd", v_elem.get("spdi", item.get("speed", "-")))
                                acc = v_elem.get("acc", item.get("accel", "-"))
                                bod = int(v_elem.get("bod", 0)) if v_elem.get("bod", "").isdigit() else (int(item.get("body", 0)) if item.get("body", "").isdigit() else 0)
                                arm = int(v_elem.get("arm", 0)) if v_elem.get("arm", "").isdigit() else (int(item.get("armor", 0)) if item.get("armor", "").isdigit() else 0)
                                sens = int(v_elem.get("sen", 0)) if v_elem.get("sen", "").isdigit() else (int(item.get("sensor", 0)) if item.get("sensor", "").isdigit() else 0)
                                seats = int(v_elem.get("sea", 1)) if v_elem.get("sea", "").isdigit() else (int(item.get("seats", 1)) if item.get("seats", "").isdigit() else 1)
                            else:
                                hnd = item.get("handling", "-")
                                spd = item.get("speed", "-")
                                acc = item.get("accel", "-")
                                bod = int(item.get("body", 0)) if item.get("body", "").isdigit() else 0
                                arm = int(item.get("armor", 0)) if item.get("armor", "").isdigit() else 0
                                sens = int(item.get("sensor", 0)) if item.get("sensor", "").isdigit() else 0
                                seats = int(item.get("seats", 1)) if item.get("seats", "").isdigit() else 1
                            cat = item.get("category", fname.replace("gear_", "").replace(".xml", "").title())
                            cursor.execute(
                                "INSERT OR REPLACE INTO ref_vehicles VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                                (iid, name, cat, hnd, spd, acc, bod, arm, sens, seats, cost, avail, source_set, raw_xml)
                            )
                            stats["vehicles"] += 1

                        elif is_program:
                            cat = item.get("category", "Cyberdeck Program")
                            cursor.execute(
                                "INSERT OR REPLACE INTO ref_programs VALUES (?, ?, ?, ?, ?, ?)",
                                (iid, name, cat, cost, source_set, raw_xml)
                            )
                            stats["programs"] += 1

                        else:
                            cursor.execute(
                                "INSERT OR REPLACE INTO ref_gear VALUES (?, ?, ?, ?, ?, ?, ?)",
                                (iid, name, item.tag, cost, avail, source_set, raw_xml)
                            )
                            stats["gear"] += 1

                # 6. Metatypes
                elif "metatypes" in fname or root.tag == "metatypes":
                    for meta in root.findall(".//metatype"):
                        mid = meta.get("id")
                        if not mid:
                            continue
                        name = meta.get("name", mid.title())
                        raw_xml = ET.tostring(meta, encoding="utf-8").decode("utf-8")

                        cursor.execute(
                            "INSERT OR REPLACE INTO ref_metatypes VALUES (?, ?, ?)",
                            (mid, name, raw_xml)
                        )
                        stats["metatypes"] += 1

        import datetime
        now_str = datetime.datetime.now().isoformat()
        cursor.execute("INSERT OR REPLACE INTO dataset_meta VALUES ('commlink_jar', ?)", (jar_name,))
        cursor.execute("INSERT OR REPLACE INTO dataset_meta VALUES ('import_date', ?)", (now_str,))
        cursor.execute("INSERT OR REPLACE INTO dataset_meta VALUES ('stats', ?)", (str(stats),))

        conn.commit()
        conn.close()

        msg = (
            f"Successfully compiled CommLink6 datasets from '{jar_name}' into SQLite database:\n"
            f"  - Qualities: {stats['qualities']}\n"
            f"  - Spells: {stats['spells']}\n"
            f"  - Complex Forms: {stats['complex_forms']}\n"
            f"  - Weapons: {stats['weapons']}\n"
            f"  - Cyberware/Bioware: {stats['cyberware']}\n"
            f"  - Adept Powers: {stats['adept_powers']}\n"
            f"  - Vehicles/Drones: {stats['vehicles']}\n"
            f"  - Matrix Programs: {stats['programs']}\n"
            f"  - Gear & Items: {stats['gear']}\n"
            f"  - Metatypes: {stats['metatypes']}"
        )
        return True, msg

    except Exception as e:
        conn.close()
        return False, f"Error compiling CommLink6 datasets: {e}"


def get_dataset_info(db_path: str = DEFAULT_DB_PATH) -> Dict[str, Any]:
    if not os.path.exists(db_path):
        return {"exists": False}

    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    info = {"exists": True}

    try:
        rows = cursor.execute("SELECT * FROM dataset_meta").fetchall()
        for r in rows:
            info[r["key"]] = r["value"]
    except Exception:
        pass

    counts = {}
    for table in [
        "ref_contacts", "ref_qualities", "ref_spells", "ref_complex_forms",
        "ref_weapons", "ref_cyberware", "ref_adept_powers", "ref_vehicles",
        "ref_programs", "ref_gear", "ref_metatypes"
    ]:
        try:
            cnt = cursor.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
            counts[table] = cnt
        except Exception:
            counts[table] = 0

    info["counts"] = counts
    conn.close()
    return info
