"""
Canonical SRM Contacts Registry based on Shadowrun Missions Guide (SRM 2081) Appendix C.
Provides immutable connection ratings, canonical descriptions, types, and regions for all official SRM contacts.
"""

from typing import Dict, Any, Optional, List, Union

CANONICAL_CONTACTS: Dict[str, Dict[str, Any]] = {
    # --- SEATTLE CONTACTS (SRM 2081) ---
    "Brynne Taggart": {
        "job": "Fixer",
        "connection": 4,
        "region": "SEA",
        "missions": "SRM 2081-01, 03, 05, 06",
        "uses": "Getting jobs, fencing gear, gangs (Shadowrun Missions Seattle)",
        "types": "Criminal, Street",
        "description": "Uses: Getting jobs, fencing gear, gangs (Shadowrun Missions Seattle) | Types: Criminal, Street"
    },
    "Donovan Pyke": {
        "job": "Shadow Chapters Leader",
        "connection": 8,
        "region": "SEA",
        "missions": "SRM 2081-12, 16",
        "uses": "Getting jobs, politics, Shadow Chapters (Shadowrun Missions Seattle)",
        "types": "Corporate, Magic",
        "description": "Uses: Getting jobs, politics, Shadow Chapters (Shadowrun Missions Seattle) | Types: Corporate, Magic (Not available after 2081-24)"
    },
    "Eddie Wei": {
        "job": "Triad Johnson",
        "connection": 4,
        "region": "SEA",
        "missions": "SRM 2081-02, 08, 12",
        "uses": "Business and economics, getting jobs, triads (Shadowrun Missions Seattle)",
        "types": "Criminal, Matrix",
        "description": "Uses: Business and economics, getting jobs, triads (Shadowrun Missions Seattle) | Types: Criminal, Matrix (Not available after 2081-24)"
    },
    "Julian Müntefering": {
        "job": "Corporate Kid",
        "connection": 1,
        "region": "SEA",
        "missions": "SRM 2081-08",
        "uses": "Corporate playground rumors, drones, rigging research (Shadowrun Missions Seattle)",
        "types": "Corporate, Engineering",
        "description": "Uses: Corporate playground rumors, drones, rigging research (Shadowrun Missions Seattle) | Types: Corporate, Engineering"
    },
    "Julian Muntefering": {
        "job": "Corporate Kid",
        "connection": 1,
        "region": "SEA",
        "missions": "SRM 2081-08",
        "uses": "Corporate playground rumors, drones, rigging research (Shadowrun Missions Seattle)",
        "types": "Corporate, Engineering",
        "description": "Uses: Corporate playground rumors, drones, rigging research (Shadowrun Missions Seattle) | Types: Corporate, Engineering"
    },
    "Kingston": {
        "job": "Shadowrunner/Street Samurai",
        "connection": 2,
        "region": "SEA",
        "missions": "SRM 2081-02, 06",
        "uses": "Shadowrunners, street rumors (Shadowrun Missions Seattle)",
        "types": "Criminal, Street",
        "description": "Uses: Shadowrunners, street rumors (Shadowrun Missions Seattle) | Types: Criminal, Street"
    },
    "MacCallister": {
        "job": "Fixer",
        "connection": 5,
        "region": "SEA",
        "missions": "SRM 2081-04",
        "uses": "Getting jobs, matrix, street scenes (Shadowrun Missions Seattle)",
        "types": "Matrix, Street",
        "description": "Uses: Getting jobs, matrix, street scenes (Shadowrun Missions Seattle) | Types: Matrix, Street"
    },
    "Ms. Snow": {
        "job": "Shadow Chapters Johnson",
        "connection": 5,
        "region": "SEA",
        "missions": "SRM 2081-09, 12",
        "uses": "Corporate rumors, getting jobs, military (Shadowrun Missions Seattle)",
        "types": "Corporate, Government",
        "description": "Uses: Corporate rumors, getting jobs, military (Shadowrun Missions Seattle) | Types: Corporate, Government"
    },
    "Ni Ni Xiaolu": {
        "job": "Triad Johnson",
        "connection": 3,
        "region": "SEA",
        "missions": "SRM 2081-01, 07, 11",
        "uses": "Getting jobs, drugs, street rumors, triads (Shadowrun Missions Seattle)",
        "types": "Criminal",
        "description": "Uses: Getting jobs, drugs, street rumors, triads (Shadowrun Missions Seattle) | Types: Criminal"
    },
    "Piper": {
        "job": "Street Kid",
        "connection": 2,
        "region": "SEA",
        "missions": "SRM 2081-04, 12, 16",
        "uses": "Seattle Underground guide, rumors, history (Shadowrun Missions Seattle)",
        "types": "Street",
        "description": "Uses: Seattle Underground guide, rumors, history (Shadowrun Missions Seattle) | Types: Street"
    },
    "Saint James": {
        "job": "Fixer",
        "connection": 8,
        "region": "SEA",
        "missions": "SRM 2081-06, 18, 23, 24",
        "uses": "Corporations, getting jobs (Shadowrun Missions Seattle), fencing gear, gangs",
        "types": "Criminal, Street",
        "description": "Uses: Corporations, getting jobs (Shadowrun Missions Seattle), fencing gear, gangs | Types: Criminal, Street (Not available after 2081-24)"
    },
    "Toil": {
        "job": "Fixer",
        "connection": 4,
        "region": "SEA",
        "missions": "SRM 2081-04, 05, 10",
        "uses": "Drugs, exotic dancer clubs, getting jobs (Shadowrun Missions Seattle)",
        "types": "Criminal, Street",
        "description": "Uses: Drugs, exotic dancer clubs, getting jobs (Shadowrun Missions Seattle) | Types: Criminal, Street"
    },
    "Trubble": {
        "job": "Bodyguard",
        "connection": 1,
        "region": "SEA",
        "missions": "SRM 2081-04, 05",
        "uses": "Bodyguards, insults, talismans (Shadowrun Missions Seattle)",
        "types": "Magic",
        "description": "Uses: Bodyguards, insults, talismans (Shadowrun Missions Seattle) | Types: Magic"
    },
    "Vincent Grisome, Th.D., Ph.D.": {
        "job": "Seattle University Professor",
        "connection": 5,
        "region": "SEA",
        "missions": "",
        "uses": "Life Blood magic, thaumaturgy, Seattle University conclave (Shadowrun Missions Seattle)",
        "types": "Academic, Magic",
        "description": "Uses: Life Blood magic, thaumaturgy, Seattle University conclave (Shadowrun Missions Seattle) | Types: Academic, Magic"
    },
    "Whiskey": {
        "job": "Street Doc",
        "connection": 2,
        "region": "SEA",
        "missions": "SRM 2081-02, 08",
        "uses": "Medicine, street docs (Shadowrun Missions Seattle)",
        "types": "Medical",
        "description": "Uses: Medicine, street docs (Shadowrun Missions Seattle) | Types: Medical"
    },

    # --- NEW ORLEANS CONTACTS (SRM 2083) ---
    "Claudette Laurier": {
        "job": "Order of the Golden Dawn Librarian",
        "connection": 5,
        "region": "NOLA",
        "missions": "",
        "uses": "Getting jobs, magical traditions",
        "types": "Criminal, Matrix",
        "description": "Uses: Getting jobs, magical traditions | Types: Criminal, Matrix"
    },
    "deBass": {
        "job": "Guild of Digital Killers Face",
        "connection": 3,
        "region": "NOLA",
        "missions": "",
        "uses": "Arson, data broker, Matrix",
        "types": "Criminal, Matrix",
        "description": "Uses: Arson, data broker, Matrix | Types: Criminal, Matrix"
    },
    "Fernand Amato": {
        "job": "Kozlowski Capo",
        "connection": 4,
        "region": "NOLA",
        "missions": "",
        "uses": "Getting jobs, fencing gear, organized crime",
        "types": "Criminal, Street",
        "description": "Uses: Getting jobs, fencing gear, organized crime | Types: Criminal, Street"
    },
    "Fernand Anato": {  # Alias match
        "job": "Kozlowski Capo",
        "connection": 4,
        "region": "NOLA",
        "missions": "",
        "uses": "Getting jobs, fencing gear, organized crime",
        "types": "Criminal, Street",
        "description": "Uses: Getting jobs, fencing gear, organized crime | Types: Criminal, Street"
    },
    "Indomitable Will": {
        "job": "River People Sysop",
        "connection": 3,
        "region": "NOLA",
        "missions": "",
        "uses": "Banking, HVAC systems, Matrix",
        "types": "Corporate, Matrix",
        "description": "Uses: Banking, HVAC systems, Matrix | Types: Corporate, Matrix"
    },
    "Jolene Price": {
        "job": "Riverboat Alliance Leader",
        "connection": 7,
        "region": "NOLA",
        "missions": "",
        "uses": "Getting jobs, dragons, mafia",
        "types": "Corporate, Street",
        "description": "Uses: Getting jobs, dragons, mafia | Types: Corporate, Street"
    },
    "J. P. Chakraborty": {
        "job": "Aurelian Design Model",
        "connection": 4,
        "region": "NOLA",
        "missions": "",
        "uses": "Business and economics, getting jobs, fashion",
        "types": "Corporate, Matrix",
        "description": "Uses: Business and economics, getting jobs, fashion | Types: Corporate, Matrix"
    },
    "Lanyap": {
        "job": "Fixer",
        "connection": 4,
        "region": "NOLA",
        "missions": "",
        "uses": "Getting jobs, fencing gear, gambling, Matrix",
        "types": "Criminal, Matrix",
        "description": "Uses: Getting jobs, fencing gear, gambling, Matrix | Types: Criminal, Matrix"
    },
    "Le Tigre": {
        "job": "Epoch Model",
        "connection": 5,
        "region": "NOLA",
        "missions": "",
        "uses": "Getting jobs, parties, modeling",
        "types": "Corporate, Magic",
        "description": "Uses: Getting jobs, parties, modeling | Types: Corporate, Magic"
    },
    "Old Man": {
        "job": "Zobop Lieutenant",
        "connection": 3,
        "region": "NOLA",
        "missions": "",
        "uses": "Getting jobs, gun smuggling, voodoo",
        "types": "Criminal, Magic",
        "description": "Uses: Getting jobs, gun smuggling, voodoo | Types: Criminal, Magic"
    },
    "Renée Martin": {
        "job": "League of Laveau Liaison",
        "connection": 4,
        "region": "NOLA",
        "missions": "",
        "uses": "Getting jobs, magic, voodoo, zombies",
        "types": "Corporate, Magic",
        "description": "Uses: Getting jobs, magic, voodoo, zombies | Types: Corporate, Magic"
    },
    "Renee Martin": {
        "job": "League of Laveau Liaison",
        "connection": 4,
        "region": "NOLA",
        "missions": "",
        "uses": "Getting jobs, magic, voodoo, zombies",
        "types": "Corporate, Magic",
        "description": "Uses: Getting jobs, magic, voodoo, zombies | Types: Corporate, Magic"
    },
    "Roanoke": {
        "job": "Ecological Activist",
        "connection": 3,
        "region": "NOLA",
        "missions": "",
        "uses": "Getting jobs, environmental science, shamanism",
        "types": "Criminal, Matrix",
        "description": "Uses: Getting jobs, environmental science, shamanism | Types: Criminal, Matrix"
    },
    "Cedar": {
        "job": "Talismonger",
        "connection": 3,
        "region": "NOLA",
        "missions": "SRM 2083-20, SRM 2083-14",
        "uses": "Talismongering, magical supplies, Salish artifacts",
        "types": "Magic",
        "description": "Uses: Talismongering, magical supplies, Salish artifacts | Types: Magic"
    },
    "Alexander Sloane": {
        "job": "Etoile PI / Fixer",
        "connection": 4,
        "region": "NOLA",
        "missions": "SRM 2083-14",
        "uses": "Private investigation, bounty hunting, police contacts, job offers",
        "types": "Criminal, Law Enforcement",
        "description": "Uses: Private investigation, bounty hunting, police contacts, job offers | Types: Criminal, Law Enforcement"
    },
    "Alexander Sloan": {
        "job": "Etoile PI / Fixer",
        "connection": 4,
        "region": "NOLA",
        "missions": "SRM 2083-14",
        "uses": "Private investigation, bounty hunting, police contacts, job offers",
        "types": "Criminal, Law Enforcement",
        "description": "Uses: Private investigation, bounty hunting, police contacts, job offers | Types: Criminal, Law Enforcement"
    },

    # --- KENTUCKY FRIED SHADOWS 2 CONTACTS ---
    "Doc Coughlin": {
        "job": "Medical",
        "connection": 3,
        "region": "KY",
        "types": "Medical",
        "description": "Medical | Types: Medical"
    },
    "Garret Wade": {
        "job": "Government",
        "connection": 3,
        "region": "KY",
        "types": "Government",
        "description": "Government | Types: Government"
    },
    "Lady Siobhan": {
        "job": "Magic",
        "connection": 6,
        "region": "KY",
        "types": "Magic",
        "description": "Magic | Types: Magic"
    },
    "Reilly Dragman": {
        "job": "Magic",
        "connection": 1,
        "region": "KY",
        "types": "Magic",
        "description": "Magic | Types: Magic"
    },
    "Lady Brane Deigh": {
        "job": "Magic",
        "connection": 12,
        "region": "KY",
        "types": "Magic",
        "description": "Magic (Special Note: This contact cannot be called during a mission.) | Types: Magic"
    },
    "Queen Brane": {  # Alias for Lady Brane Deigh
        "job": "Magic",
        "connection": 12,
        "region": "KY",
        "types": "Magic",
        "description": "Magic (Special Note: This contact cannot be called during a mission.) | Types: Magic"
    }
}


import os
import re
from pathlib import Path
from typing import Dict, Any, Optional, List, Union
import yaml

_CONTACTS_REGISTRY: Optional[Dict[str, Dict[str, Any]]] = None

# SRM Official 2081 Contact Types / Archetypes (Appendix C)
STANDARD_CONTACT_TYPES: List[str] = [
    "Academic",
    "Corporate",
    "Criminal",
    "Engineering",
    "Government",
    "Law Enforcement",
    "Magic",
    "Matrix",
    "Medical",
    "Street",
]

# Standard Campaign Regions
REGION_MAP: Dict[str, str] = {
    "SEA": "Seattle",
    "NOLA": "New Orleans",
    "AMS": "Amsterdam",
    "HK": "Hong Kong",
    "KY": "Kentucky",
    "DW": "Desert Wars",
    "GEN": "General / Matrix / Other",
}


def parse_contact_types(val: Union[str, List[str], None]) -> List[str]:
    """
    Parses and normalizes contact types/categories into a clean list of strings.
    E.g. 'Criminal, Street' -> ['Criminal', 'Street']
         ['Criminal', 'Street'] -> ['Criminal', 'Street']
    """
    if not val:
        return []
    result: List[str] = []
    if isinstance(val, list):
        items = val
    elif isinstance(val, str):
        items = val.split(",")
    else:
        return []

    for item in items:
        if isinstance(item, str):
            p = item.strip().rstrip(".")
            # Strip prefixes like 'Types:' if embedded
            p = re.sub(r'^[Tt]ypes:\s*', '', p).strip()
            if p and p not in result:
                result.append(p)
    return result


def infer_contact_types(job: str = "", desc: str = "") -> List[str]:
    """Infers standard contact types from job title or description keywords."""
    combined = f"{job} {desc}".lower()
    inferred: List[str] = []
    
    keyword_map = [
        (["vory", "triad", "gang", "crime", "smuggler", "penose", "thief", "fencing", "fence", "borjevik", "bokor", "cutters"], "Criminal"),
        (["street", "samurai", "mercenary", "bartender", "ganger", "gladiator", "dive", "extra", "rapper", "courtesan", "informant"], "Street"),
        (["fixer"], ["Criminal", "Street"]),
        (["suit", "johnson", "corporate", "saeder-krupp", "knight errant", "wuxing", "conclave", "producer", "executive", "bureaucrat"], "Corporate"),
        (["spider", "decker", "technomancer", "matrix", "sysop", "emergent", "infobroker", "jackalope"], "Matrix"),
        (["talismonger", "spirit", "voodoo", "houngan", "mambo", "druid", "awakened", "dragon", "arcano", "naga"], "Magic"),
        (["doc", "street doc", "hospital", "clinic", "medical", "nurse", "paramedic"], "Medical"),
        (["mechanic", "modder", "cyber", "engineer", "rigging", "drones", "hardware"], "Engineering"),
        (["police", "detective", "knight errant", "nom", "officer", "patrol", "investigator"], "Law Enforcement"),
        (["academic", "archeologist", "professor", "researcher", "scholar", "journalist"], "Academic"),
        (["government", "royal", "house oranje", "official", "military", "corps"], "Government"),
    ]

    for keywords, cat in keyword_map:
        if any(kw in combined for kw in keywords):
            targets = [cat] if isinstance(cat, str) else cat
            for t in targets:
                if t not in inferred:
                    inferred.append(t)

    return inferred or ["Street"]


def _find_contacts_file() -> Optional[Path]:
    candidates = [
        Path(__file__).resolve().parents[2] / "reference" / "contacts.yaml",
        Path(__file__).resolve().parents[1] / "reference" / "contacts.yaml",
        Path.cwd() / "reference" / "contacts.yaml",
        Path.cwd().parent / "reference" / "contacts.yaml",
        Path.cwd().parents[1] / "reference" / "contacts.yaml",
    ]
    for c in candidates:
        if c.exists():
            return c
    return None


def get_contacts_registry() -> Dict[str, Dict[str, Any]]:
    global _CONTACTS_REGISTRY
    if _CONTACTS_REGISTRY is not None:
        return _CONTACTS_REGISTRY

    _CONTACTS_REGISTRY = {}
    fpath = _find_contacts_file()
    if fpath and fpath.exists():
        try:
            with open(fpath, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f)
                if isinstance(data, dict):
                    _CONTACTS_REGISTRY = data
        except Exception:
            pass

    for name, item in CANONICAL_CONTACTS.items():
        slug = name.lower().replace(" ", "_").replace("'", "").replace(".", "").replace(",", "").replace("-", "_")
        if slug not in _CONTACTS_REGISTRY:
            _CONTACTS_REGISTRY[slug] = {
                "id": slug,
                "name": name,
                "connection": item.get("connection", 1),
                "job": item.get("job", ""),
                "region": item.get("region", "SEA"),
                "canonical": True,
                "types": item.get("types", ""),
                "missions": item.get("missions", ""),
                "uses": item.get("uses", ""),
                "description": item.get("description", "")
            }

    # Normalize all entries in _CONTACTS_REGISTRY
    for slug, entry in _CONTACTS_REGISTRY.items():
        raw_types = entry.get("types")
        parsed = parse_contact_types(raw_types)
        if not parsed:
            parsed = infer_contact_types(entry.get("job", ""), entry.get("description", ""))
        entry["types"] = parsed
        entry["types_str"] = ", ".join(parsed) if parsed else "General"
        if not entry.get("region"):
            entry["region"] = "GEN"

    return _CONTACTS_REGISTRY


def get_contact(name_or_id: str) -> Optional[Dict[str, Any]]:
    """Resolves contact by id/slug or name (case-insensitive)."""
    reg = get_contacts_registry()
    key = name_or_id.strip()
    slug = key.lower().replace(" ", "_").replace("'", "").replace(".", "").replace(",", "").replace("-", "_")
    if slug in reg:
        return reg[slug]

    for c_slug, c_info in reg.items():
        if c_info.get("name", "").lower() == key.lower():
            return c_info

    return None


def get_canonical_contact(name: str) -> Optional[Dict[str, Any]]:
    """Returns canonical contact info if found, else None."""
    c = get_contact(name)
    if c and c.get("canonical", False):
        return c
    return CANONICAL_CONTACTS.get(name.strip())


def is_canonical_contact(name: str) -> bool:
    """Checks whether a contact name is an official SRM canonical contact."""
    c = get_contact(name)
    if c:
        return bool(c.get("canonical", False))
    return name.strip() in CANONICAL_CONTACTS


def normalize_contacts_list(contacts_data: Any) -> List[Dict[str, Any]]:
    """
    Normalizes contacts data whether structured as:
      - A dictionary: {name: contact_dict, ...}
      - A list of dictionaries: [contact_dict, ...]
      - A list of string names: [name, ...]
    Guarantees a list of dictionaries with 'name' populated.
    """
    if not contacts_data:
        return []

    result: List[Dict[str, Any]] = []

    if isinstance(contacts_data, dict):
        for k, v in contacts_data.items():
            if isinstance(v, dict):
                item = dict(v)
                if not item.get("name"):
                    item["name"] = str(k)
                result.append(item)
            elif isinstance(v, str):
                result.append({"name": str(k), "notes": v})
            else:
                result.append({"name": str(k)})
        return result

    if isinstance(contacts_data, list):
        for item in contacts_data:
            if isinstance(item, dict):
                result.append(dict(item))
            elif isinstance(item, str):
                result.append({"name": item})
        return result

    return result


def calculate_total_karma_invested(contacts_data: Any) -> int:
    """Calculates total karma invested in contacts (Connection + Loyalty)."""
    normalized = normalize_contacts_list(contacts_data)
    total = 0
    for c in normalized:
        conn = int(c.get("connection", 1))
        loy = int(c.get("loyalty", 1))
        total += (conn + loy)
    return total


def search_contacts(
    contacts_pool: Optional[Union[Dict[str, Any], List[Dict[str, Any]], str]] = None,
    *,
    contact_type: Optional[str] = None,
    region: Optional[str] = None,
    query: Optional[str] = None,
    min_connection: Optional[int] = None,
    min_loyalty: Optional[int] = None,
    char_id: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """
    Searches and filters contacts by type, region, query, and ratings.
    - If char_id is provided, searches that character's active contacts.
    - If contacts_pool is provided, searches that dictionary or list.
    - If neither is provided, searches the master contacts registry.
    """
    target_pool: List[Dict[str, Any]] = []

    # 1. Resolve source pool
    if char_id or (isinstance(contacts_pool, str) and contacts_pool.strip()):
        cid = char_id or str(contacts_pool).strip()
        from sr6core.character.model import load_character
        char = load_character(cid)
        target_pool = normalize_contacts_list(char.contacts)
    elif contacts_pool is not None:
        target_pool = normalize_contacts_list(contacts_pool)
    else:
        reg = get_contacts_registry()
        target_pool = [dict(v) for v in reg.values()]

    # 2. Enrich entries with master registry data where missing
    reg = get_contacts_registry()
    enriched_pool: List[Dict[str, Any]] = []
    for c in target_pool:
        item = dict(c)
        c_name = item.get("name", "")
        c_master = get_contact(c_name) if c_name else None
        if c_master:
            if not item.get("job") and c_master.get("job"):
                item["job"] = c_master.get("job")
            if not item.get("region") or item.get("region") == "GEN":
                item["region"] = c_master.get("region", "GEN")
            if not item.get("types"):
                item["types"] = list(c_master.get("types", []))
            if not item.get("uses") and c_master.get("uses"):
                item["uses"] = c_master.get("uses")
            if not item.get("description") and c_master.get("description"):
                item["description"] = c_master.get("description")
            if "canonical" not in item:
                item["canonical"] = c_master.get("canonical", False)

        # Ensure types are parsed
        parsed_types = parse_contact_types(item.get("types"))
        if not parsed_types:
            parsed_types = infer_contact_types(item.get("job", "") or item.get("type", ""), item.get("description", "") or item.get("notes", ""))
        item["types"] = parsed_types
        item["types_str"] = ", ".join(parsed_types) if parsed_types else "General"
        if not item.get("region"):
            item["region"] = "GEN"
        enriched_pool.append(item)

    # 3. Apply Filters
    results: List[Dict[str, Any]] = []

    req_type = contact_type.strip().lower() if contact_type else None
    req_reg = region.strip().lower() if region else None
    req_q = query.strip().lower() if query else None

    # Map region aliases if given (e.g. "seattle" -> "SEA")
    reg_code_matches = set()
    if req_reg:
        reg_code_matches.add(req_reg)
        for code, full_name in REGION_MAP.items():
            if req_reg == code.lower() or req_reg in full_name.lower() or full_name.lower() in req_reg:
                reg_code_matches.add(code.lower())
                reg_code_matches.add(full_name.lower())

    for c in enriched_pool:
        # Type filter
        if req_type:
            types_lower = [t.lower() for t in c.get("types", [])]
            job_lower = (c.get("job") or c.get("type") or "").lower()
            if not any(req_type in t for t in types_lower) and req_type not in job_lower:
                continue

        # Region filter
        if req_reg:
            c_reg_val = (c.get("region") or "").lower()
            c_reg_full = REGION_MAP.get(c.get("region", "").upper(), "").lower()
            if not any(m == c_reg_val or m == c_reg_full or m in c_reg_val for m in reg_code_matches):
                continue

        # Connection filter
        if min_connection is not None:
            if int(c.get("connection", 1)) < min_connection:
                continue

        # Loyalty filter
        if min_loyalty is not None:
            if int(c.get("loyalty", 1)) < min_loyalty:
                continue

        # Text query filter
        if req_q:
            searchable = " ".join([
                c.get("name", ""),
                c.get("job", "") or c.get("type", ""),
                c.get("region", ""),
                c.get("types_str", ""),
                c.get("notes", "") or "",
                c.get("uses", "") or "",
                c.get("description", "") or "",
                str(c.get("missions", "") or "")
            ]).lower()
            if req_q not in searchable:
                continue

        results.append(c)

    # 4. Sort results by Connection desc, Loyalty desc, Name asc
    def sort_key(item: Dict[str, Any]):
        conn = int(item.get("connection", 1))
        loy = int(item.get("loyalty", 0))
        name = item.get("name", "").lower()
        return (-conn, -loy, name)

    results.sort(key=sort_key)
    return results


def format_contacts_table(contacts: List[Dict[str, Any]], title: Optional[str] = None) -> str:
    """Formats a list of contacts into a clean markdown table."""
    if not contacts:
        msg = "No contacts found matching the specified criteria."
        return f"### {title}\n\n{msg}" if title else msg

    has_loyalty = any("loyalty" in c and c["loyalty"] is not None for c in contacts)
    has_favors = any(c.get("favors", 0) > 0 for c in contacts)

    headers = ["Contact Name", "Conn"]
    if has_loyalty:
        headers.append("Loy")
    if has_favors:
        headers.append("Favors")
    headers.extend(["Region", "Types", "Job / Archetype", "Notes / Uses"])

    sep = ["---", ":---:"]
    if has_loyalty:
        sep.append(":---:")
    if has_favors:
        sep.append(":---:")
    sep.extend(["---", "---", "---", "---"])

    lines = []
    if title:
        lines.append(f"### {title}\n")
    lines.append("| " + " | ".join(headers) + " |")
    lines.append("| " + " | ".join(sep) + " |")

    for c in contacts:
        row = [
            f"**{c.get('name', 'Unknown')}**",
            str(c.get("connection", 1))
        ]
        if has_loyalty:
            row.append(str(c.get("loyalty", 1)))
        if has_favors:
            row.append(str(c.get("favors", 0)))
        row.append(c.get("region", "GEN"))
        row.append(c.get("types_str", ", ".join(c.get("types", []))))
        job = c.get("job") or c.get("type") or ""
        row.append(job)
        notes = c.get("uses") or c.get("notes") or c.get("description") or ""
        if len(notes) > 80:
            notes = notes[:77] + "..."
        row.append(notes.replace("|", "/"))
        lines.append("| " + " | ".join(row) + " |")

    return "\n".join(lines)

