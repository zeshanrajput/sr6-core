"""
Canonical SRM Contacts Registry based on Shadowrun Missions Guide (SRM 2081) Appendix C.
Provides immutable connection ratings, canonical descriptions, types, and regions for all official SRM contacts.
"""

from typing import Dict, Any, Optional

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


def get_canonical_contact(name: str) -> Optional[Dict[str, Any]]:
    """Returns canonical contact info if found, else None."""
    return CANONICAL_CONTACTS.get(name.strip())


def is_canonical_contact(name: str) -> bool:
    """Checks whether a contact name is an official SRM canonical contact."""
    return name.strip() in CANONICAL_CONTACTS
