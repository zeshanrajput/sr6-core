"""
SRM Official Named Contacts Indexer & Verifier for SR6 Core.
Indexes and populates official named Shadowrun Missions Guide (SRMG) contacts with locked Connection ratings,
contact types, regions, and descriptions into SQLite ref_contacts table.
"""

import os
import sqlite3
from typing import Dict, Any, List, Optional

from sr6core.rules_db import DEFAULT_DB_PATH

# Official SRM Named Contacts from Shadowrun Missions Guide v2.4 (SRMG-0492 & SRMG-0493)
OFFICIAL_SRM_CONTACTS = [
    {
        "id": "brynne_taggart",
        "name": "Brynne Taggart",
        "connection": 4,
        "archetype": "Fixer",
        "region": "Seattle",
        "types": "Criminal, Street",
        "uses": "Getting jobs, fencing gear, gangs",
        "source": "SRMG v2.4 (SRM 2081-01)"
    },
    {
        "id": "donovan_pyke",
        "name": "Donovan Pyke",
        "connection": 8,
        "archetype": "Shadow Chapters Leader",
        "region": "Seattle",
        "types": "Corporate, Magic",
        "uses": "Getting jobs, politics, Shadow Chapters",
        "source": "SRMG v2.4 (SRM 2081-12)"
    },
    {
        "id": "eddie_wei",
        "name": "Eddie Wei",
        "connection": 4,
        "archetype": "Triad Johnson",
        "region": "Seattle",
        "types": "Criminal, Matrix",
        "uses": "Business and economics, getting jobs, triads",
        "source": "SRMG v2.4 (SRM 2081-02)"
    },
    {
        "id": "julian_muntefering",
        "name": "Julian Muntefering",
        "connection": 1,
        "archetype": "Corporate Kid",
        "region": "Seattle",
        "types": "Corporate, Engineering",
        "uses": "Corporate playground rumors, drones, rigging research",
        "source": "SRMG v2.4 (SRM 2081-08)"
    },
    {
        "id": "kingston",
        "name": "Kingston",
        "connection": 2,
        "archetype": "Shadowrunner / Street Samurai",
        "region": "Seattle",
        "types": "Criminal, Street",
        "uses": "Shadowrunners, street rumors",
        "source": "SRMG v2.4 (SRM 2081-02)"
    },
    {
        "id": "maccallister",
        "name": "MacCallister",
        "connection": 5,
        "archetype": "Fixer",
        "region": "Seattle",
        "types": "Matrix, Street",
        "uses": "Getting jobs, matrix, street scenes",
        "source": "SRMG v2.4 (SRM 2081-04)"
    },
    {
        "id": "ms_snow",
        "name": "Ms. Snow",
        "connection": 5,
        "archetype": "Shadow Chapters Johnson",
        "region": "Seattle",
        "types": "Corporate, Government",
        "uses": "Corporate rumors, getting jobs, military",
        "source": "SRMG v2.4 (SRM 2081-09)"
    },
    {
        "id": "ni_ni_xiaolu",
        "name": "Ni Ni Xiaolu",
        "connection": 3,
        "archetype": "Triad Johnson",
        "region": "Seattle",
        "types": "Criminal",
        "uses": "Getting jobs, drugs, street rumors, triads",
        "source": "SRMG v2.4 (SRM 2081-01)"
    },
    {
        "id": "piper",
        "name": "Piper",
        "connection": 2,
        "archetype": "Street Kid",
        "region": "Seattle",
        "types": "Street",
        "uses": "Seattle Underground guide, rumors, history",
        "source": "SRMG v2.4 (SRM 2081-04)"
    },
    {
        "id": "saint_james",
        "name": "Saint James",
        "connection": 8,
        "archetype": "Fixer",
        "region": "Seattle",
        "types": "Criminal, Street",
        "uses": "Corporations, getting jobs, fencing gear, gangs",
        "source": "SRMG v2.4 (SRM 2081-06)"
    },
    {
        "id": "toil",
        "name": "Toil",
        "connection": 4,
        "archetype": "Fixer",
        "region": "Seattle",
        "types": "Criminal, Street",
        "uses": "Drugs, exotic dancer clubs, getting jobs",
        "source": "SRMG v2.4 (SRM 2081-04)"
    },
    {
        "id": "trubble",
        "name": "Trubble",
        "connection": 1,
        "archetype": "Bodyguard",
        "region": "Seattle",
        "types": "Magic",
        "uses": "Bodyguards, insults, talismans",
        "source": "SRMG v2.4 (SRM 2081-04)"
    },
    {
        "id": "vincent_grisome",
        "name": "Vincent Grisome",
        "connection": 5,
        "archetype": "Seattle University Professor",
        "region": "Seattle",
        "types": "Academic, Magic",
        "uses": "Life Blood magic, thaumaturgy, university conclave",
        "source": "SRMG v2.4"
    },
    {
        "id": "whiskey",
        "name": "Whiskey",
        "connection": 2,
        "archetype": "Street Doc",
        "region": "Seattle",
        "types": "Medical",
        "uses": "Medicine, street docs",
        "source": "SRMG v2.4 (SRM 2081-02)"
    },
    {
        "id": "claudette_laurier",
        "name": "Claudette Laurier",
        "connection": 5,
        "archetype": "Golden Dawn Librarian",
        "region": "New Orleans",
        "types": "Criminal, Matrix",
        "uses": "Getting jobs, magical traditions",
        "source": "SRMG v2.4"
    },
    {
        "id": "debass",
        "name": "deBass",
        "connection": 3,
        "archetype": "Digital Killers Face",
        "region": "New Orleans",
        "types": "Criminal, Matrix",
        "uses": "Arson, data broker, Matrix",
        "source": "SRMG v2.4"
    },
    {
        "id": "fernand_amato",
        "name": "Fernand Amato",
        "connection": 4,
        "archetype": "Kozlowski Capo",
        "region": "New Orleans",
        "types": "Criminal, Street",
        "uses": "Getting jobs, fencing gear, organized crime",
        "source": "SRMG v2.4"
    },
    {
        "id": "indomitable_will",
        "name": "Indomitable Will",
        "connection": 3,
        "archetype": "River People Sysop",
        "region": "New Orleans",
        "types": "Corporate, Matrix",
        "uses": "Banking, HVAC systems, Matrix",
        "source": "SRMG v2.4"
    },
    {
        "id": "jolene_price",
        "name": "Jolene Price",
        "connection": 7,
        "archetype": "Riverboat Alliance Leader",
        "region": "New Orleans",
        "types": "Corporate, Street",
        "uses": "Getting jobs, dragons, mafia",
        "source": "SRMG v2.4"
    },
    {
        "id": "jp_chakraborty",
        "name": "J. P. Chakraborty",
        "connection": 4,
        "archetype": "Aurelian Design Model",
        "region": "New Orleans",
        "types": "Corporate, Matrix",
        "uses": "Business and economics, getting jobs, fashion",
        "source": "SRMG v2.4"
    },
    {
        "id": "lanyap",
        "name": "Lanyap",
        "connection": 4,
        "archetype": "Fixer",
        "region": "New Orleans",
        "types": "Criminal, Matrix",
        "uses": "Getting jobs, fencing gear, gambling, Matrix",
        "source": "SRMG v2.4"
    },
    {
        "id": "le_tigre",
        "name": "Le Tigre",
        "connection": 5,
        "archetype": "Epoch Model",
        "region": "New Orleans",
        "types": "Corporate, Magic",
        "uses": "Getting jobs, parties, modeling",
        "source": "SRMG v2.4"
    },
    {
        "id": "old_man",
        "name": "Old Man",
        "connection": 3,
        "archetype": "Zobop Lieutenant",
        "region": "New Orleans",
        "types": "Criminal, Magic",
        "uses": "Getting jobs, gun smuggling, voodoo",
        "source": "SRMG v2.4"
    },
    {
        "id": "renee_martin",
        "name": "Renée Martin",
        "connection": 4,
        "archetype": "League of Laveau Liaison",
        "region": "New Orleans",
        "types": "Corporate, Magic",
        "uses": "Getting jobs, magic, voodoo, zombies",
        "source": "SRMG v2.4"
    },
    {
        "id": "roanoke",
        "name": "Roanoke",
        "connection": 3,
        "archetype": "Ecological Activist",
        "region": "New Orleans",
        "types": "Criminal, Matrix",
        "uses": "Getting jobs, environmental science, shamanism",
        "source": "SRMG v2.4"
    },
    {
        "id": "doc_coughlin",
        "name": "Doc Coughlin",
        "connection": 3,
        "archetype": "Medical Doctor",
        "region": "Kentucky",
        "types": "Medical",
        "uses": "Medical care, Cyberware repairs",
        "source": "SRMG v2.4"
    },
    {
        "id": "garret_wade",
        "name": "Garret Wade",
        "connection": 3,
        "archetype": "Government Agent",
        "region": "Kentucky",
        "types": "Government",
        "uses": "Government clearances, licenses",
        "source": "SRMG v2.4"
    },
    {
        "id": "lady_siobhan",
        "name": "Lady Siobhan",
        "connection": 6,
        "archetype": "Magical Practitioner",
        "region": "Kentucky",
        "types": "Magic",
        "uses": "High magic, rituals, foci",
        "source": "SRMG v2.4"
    },
    {
        "id": "reilly_dragman",
        "name": "Reilly Dragman",
        "connection": 1,
        "archetype": "Novice Magician",
        "region": "Kentucky",
        "types": "Magic",
        "uses": "Street magic, minor talismans",
        "source": "SRMG v2.4"
    },
    {
        "id": "lady_brane_deigh",
        "name": "Lady Brane Deigh",
        "connection": 12,
        "archetype": "Arch-Mage / Seelie Court",
        "region": "Kentucky / Astral",
        "types": "Magic",
        "uses": "Forbidden magic (Cannot be called during missions)",
        "source": "SRMG v2.4"
    }
]


def populate_srm_contacts_table(db_path: str = DEFAULT_DB_PATH) -> int:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS ref_contacts (
            id TEXT PRIMARY KEY,
            name TEXT,
            connection INTEGER,
            archetype TEXT,
            region TEXT,
            types TEXT,
            uses TEXT,
            source TEXT
        )
    """)

    count = 0
    for c in OFFICIAL_SRM_CONTACTS:
        cursor.execute(
            "INSERT OR REPLACE INTO ref_contacts VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            (c["id"], c["name"], c["connection"], c["archetype"], c["region"], c["types"], c["uses"], c["source"])
        )
        count += 1

    conn.commit()
    conn.close()
    return count


def get_official_srm_contact(name_or_id: str, db_path: str = DEFAULT_DB_PATH) -> Optional[Dict[str, Any]]:
    if not os.path.exists(db_path):
        return None

    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    norm_target = name_or_id.strip().lower().replace(" ", "_")
    row = cursor.execute(
        "SELECT * FROM ref_contacts WHERE id = ? OR lower(id) = ? OR lower(name) = ?",
        (name_or_id.strip(), norm_target, name_or_id.strip().lower())
    ).fetchone()

    conn.close()
    if row:
        return dict(row)
    return None
