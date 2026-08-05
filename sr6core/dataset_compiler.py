"""
CommLink6 Dataset Compiler for SR6.
Auto-detects and extracts official XML dataset files from CommLink6 JAR archives
into structured SQLite tables in rules_index.db.
"""

import os
import re
import glob
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
                raw_xml TEXT
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
                raw_xml TEXT
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
            CREATE TABLE IF NOT EXISTS ref_metatypes (
                id TEXT PRIMARY KEY,
                name TEXT,
                raw_xml TEXT
            )
        """)


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
        "metatypes": 0
    }

    try:
        with zipfile.ZipFile(jar_path, "r") as z:
            namelist = z.namelist()
            data_files = [f for f in namelist if f.startswith("de/rpgframework/shadowrun6/data/") and f.endswith(".xml")]

            for df in data_files:
                parts = df.split("/")
                source_set = parts[4] if len(parts) > 4 else "core"

                try:
                    raw_bytes = z.read(df)
                    root = ET.fromstring(raw_bytes)
                except Exception:
                    continue

                # 1. Qualities
                if "qualities" in df or root.tag == "qualities":
                    for q in root.findall(".//quality"):
                        qid = q.get("id")
                        if not qid:
                            continue
                        karma = int(q.get("karma", 0))
                        pos = q.get("pos", "true").lower() == "true"
                        qtype = "positive" if pos else "negative"
                        max_r = int(q.get("max", 1))
                        name = q.get("name", qid.replace("_", " ").title())
                        raw_xml = ET.tostring(q, encoding="utf-8").decode("utf-8")

                        cursor.execute(
                            "INSERT OR REPLACE INTO ref_qualities VALUES (?, ?, ?, ?, ?, ?, ?)",
                            (qid, name, karma, qtype, max_r, source_set, raw_xml)
                        )
                        stats["qualities"] += 1

                # 2. Spells
                elif "spells" in df or root.tag == "spells":
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

                        cursor.execute(
                            "INSERT OR REPLACE INTO ref_spells VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                            (sid, name, cat, drain, rng, dur, source_set, raw_xml)
                        )
                        stats["spells"] += 1

                # 3. Complex Forms
                elif "complex" in df or root.tag == "complexforms":
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

                # 4. Gear, Weapons, Armor, Vehicles, Augmentations
                elif "gear" in df or "augment" in df or root.tag in ["items", "gears"]:
                    for item in root.findall(".//*"):
                        iid = item.get("id")
                        if not iid or item.tag in ["requires", "modifications"]:
                            continue
                        name = item.get("name", iid.replace("_", " ").title())
                        cost = int(item.get("cost", 0)) if item.get("cost", "").isdigit() else 0
                        avail = item.get("avail", "1")
                        raw_xml = ET.tostring(item, encoding="utf-8").decode("utf-8")

                        cursor.execute(
                            "INSERT OR REPLACE INTO ref_gear VALUES (?, ?, ?, ?, ?, ?, ?)",
                            (iid, name, item.tag, cost, avail, source_set, raw_xml)
                        )
                        stats["gear"] += 1

                # 5. Metatypes
                elif "metatypes" in df or root.tag == "metatypes":
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
    for table in ["ref_contacts", "ref_qualities", "ref_spells", "ref_complex_forms", "ref_gear", "ref_metatypes"]:
        try:
            cnt = cursor.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
            counts[table] = cnt
        except Exception:
            counts[table] = 0

    info["counts"] = counts
    conn.close()
    return info
