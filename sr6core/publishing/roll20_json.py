"""
Roll20 Shadowrun Sixth World (Genesis JSON) Exporter for SR6 Core.

Generates a Genesis-compatible JSON payload specifically engineered to match
the `doImport(json)` sheet worker in the official Roll20 Shadowrun Sixth World
character sheet (`Shadowrun6thEdition.html`), plus a companion Roll20 Macros &
Effects copy-paste helper guide.
"""

import json
import math
import os
import re
import sqlite3
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


# Official Roll20 active skill IDs and canonical display names
ROLL20_ACTIVE_SKILLS: Dict[str, Tuple[str, str, str]] = {
    "astral": ("astral", "Astral", "intuition"),
    "athletics": ("athletics", "Athletics", "agility"),
    "biotech": ("biotech", "Biotech", "logic"),
    "close_combat": ("close_combat", "Close Combat", "agility"),
    "close combat": ("close_combat", "Close Combat", "agility"),
    "con": ("con", "Con", "charisma"),
    "conjuring": ("conjuring", "Conjuring", "magic"),
    "cracking": ("cracking", "Cracking", "logic"),
    "electronics": ("electronics", "Electronics", "logic"),
    "enchanting": ("enchanting", "Enchanting", "magic"),
    "engineering": ("engineering", "Engineering", "logic"),
    "exotic_weapons": ("exotic_weapons", "Exotic Weapons", "agility"),
    "exotic weapons": ("exotic_weapons", "Exotic Weapons", "agility"),
    "firearms": ("firearms", "Firearms", "agility"),
    "influence": ("influence", "Influence", "charisma"),
    "outdoors": ("outdoors", "Outdoors", "intuition"),
    "patterncraft": ("patterncraft", "Patterncraft", "magic"),
    "perception": ("perception", "Perception", "intuition"),
    "piloting": ("piloting", "Piloting", "reaction"),
    "sorcery": ("sorcery", "Sorcery", "magic"),
    "stealth": ("stealth", "Stealth", "agility"),
    "tasking": ("tasking", "Tasking", "resonance"),
}

# Valid Roll20 weapon skill IDs (for weapon_skills dictionary in doImport)
VALID_WEAPON_SKILLS = {
    "firearms",
    "exotic_weapons",
    "athletics",
    "close_combat",
    "engineering",
}

# Cumulative armor keywords (pieces that stack with primary body armor in SR6)
CUMULATIVE_ARMOR_KEYWORDS = (
    "helmet",
    "shield",
    "ballistic shield",
    "riot shield",
    "tactical shield",
    "forearm guard",
    "gel pack",
    "ballistic hood",
    "rapid adjustment clothing system",
    "racs",
)

# Gear items routed to the Augmentations section on Roll20 (with 0 Essence cost)
AUGMENTATION_GEAR_KEYWORDS = (
    "nanopaste",
    "nanocosmetics",
    "savior medkit",
)


def _get_db_connection() -> Optional[sqlite3.Connection]:
    """Connect to the centralized SQLite rules database if available."""
    env_path = os.environ.get("SR6_RULES_DB_PATH")
    db_path = Path(env_path) if env_path else Path.home() / ".sr6" / "rules_index.db"
    if not db_path.exists():
        return None
    try:
        conn = sqlite3.connect(str(db_path))
        conn.row_factory = sqlite3.Row
        return conn
    except Exception:
        return None


def _strip_xml_tags(xml_str: str) -> str:
    """Extract human-readable text or description from raw XML if present."""
    if not xml_str:
        return ""
    m = re.search(r"<description>(.*?)</description>", xml_str, re.DOTALL | re.IGNORECASE)
    if m:
        return re.sub(r"\s+", " ", m.group(1)).strip()
    return ""


def _parse_xml_attr(xml_str: str, attr_name: str) -> str:
    """Extract an XML attribute value (e.g. page='132', type='MANA') from raw_xml."""
    if not xml_str:
        return ""
    m = re.search(rf'\b{re.escape(attr_name)}="([^"]*)"', xml_str, re.IGNORECASE)
    return m.group(1).strip() if m else ""


def _lookup_db_row(
    conn: Optional[sqlite3.Connection],
    table: str,
    ref_id: Optional[str],
    name: Optional[str],
) -> Optional[Dict[str, Any]]:
    """Look up a reference row by id or name (case-insensitive)."""
    if conn is None:
        return None
    try:
        cur = conn.cursor()
        if ref_id:
            cur.execute(f"SELECT * FROM {table} WHERE LOWER(id) = LOWER(?)", (str(ref_id),))
            row = cur.fetchone()
            if row:
                return dict(row)
        if name:
            clean_name = re.sub(r"\s*\(.*?\)", "", str(name)).strip()
            for candidate in (str(name).strip(), clean_name):
                if not candidate:
                    continue
                cur.execute(
                    f"SELECT * FROM {table} WHERE LOWER(name) = LOWER(?)",
                    (candidate,),
                )
                row = cur.fetchone()
                if row:
                    return dict(row)
    except Exception:
        return None
    return None


# Canonical rulebook descriptions for items whose two-column PDF extraction in `rules`
# interleaved adjacent entries (e.g., 6WC p.133/137, SW p.78/81, CRB p.223) or whose
# topic header is grouped under a broader section (e.g., Biotech / Optical & Audio Devices).
CANONICAL_RULE_DESCRIPTIONS: Dict[str, Tuple[str, str]] = {
    "metagenetic attribute improvement": (
        "You possess the metagenetic capability to raise one attribute beyond normal metahuman limits.\n"
        "• Cost: 15 Karma\n"
        "• Game Effect: Increase the natural and augmented maximum of the chosen attribute by 1.",
        "Sixth World Companion p.25",
    ),
    "exceptional attribute": (
        "You push one of your natural attributes beyond standard metatype limits.\n"
        "• Cost: 12 Karma\n"
        "• Game Effect: Increase the natural maximum of one Physical or Mental attribute by 1 (allowing you to raise it to the new maximum).",
        "CRB p.71",
    ),
    "inspire competence": (
        "You know how to motivate people to get the most out of their capabilities.\n"
        "• Cost: 11 Karma\n"
        "• Game Effect: For a Major Action, you may make an Influence (Leadership) + Charisma test to assist another character on a Teamwork test with any skill. Either you or the character that you assist (player choice) gains a point of Edge.",
        "Sixth World Companion p.133",
    ),
    "focused concentration": (
        "You know how to compartmentalize your mind and keep hold of arcane and emergent manipulations without straining yourself.\n"
        "• Cost: 12 Karma per level (max 3)\n"
        "• Game Effect: For each level of this quality, you may sustain one spell, ritual, or complex form without suffering the normal -2 sustaining penalty.",
        "CRB p.71",
    ),
    "injury prone": (
        "Whenever you get hurt, you get hurt bad.\n"
        "• Bonus: 15 Karma\n"
        "• Game Effect: Whenever you suffer damage from any source, take one extra box of the same type of damage (Physical or Stun).",
        "Sixth World Companion p.137",
    ),
    "hooder": (
        "You're driven to do what you can to help others.\n"
        "• Bonus: 5 Karma per level (max level 3)\n"
        "• Game Effect: You must donate at least 1,000 nuyen per level of this quality every month. The donation cannot go to other members of your team, and you take a -2 dice pool modifier on Negotiation tests to increase pay for runs that help the needy.",
        "Sixth World Companion p.137",
    ),
    "elemental attack": (
        "Type: P | Action: Major | Range: LOS | Duration: Instant\n"
        "Make a ranged combat attack using the spirit's Magic + Agility (or Spellcasting while Channeling). "
        "The attack has a DV of (Force)P Elemental and Attack Ratings of Near (Force x 2), Close (Force x 2) - 2, "
        "Medium (Force x 2) - 8, Far (Force x 2) - 10. Targets also suffer the elemental Status Effect: "
        "Zapped (Electricity), Burning (Fire), Corroded (Chemical), or Chilled (Cold).",
        "CRB p.223 / Street Wyrd p.113",
    ),
    "cosmetic control": (
        "Cost: 1.0 PP per level (max 2 levels) | Activation: Major Action\n"
        "Alter your body to change physical appearance (hair, gender markers, skin tone, facial features, height, weight). "
        "Level 1 allows changes within your metatype's normal range; Level 2 reaches beyond metaspecies limitations "
        "(ear shape, horns/tusks, height/size across human/elf/ork/dwarf/troll, and exotic skin/eye/hair patterns). "
        "Each level lowers the cost of Edge Boosts by 1 for Con tests (Acting, Disguise, Impersonation).",
        "Street Wyrd p.78-79",
    ),
    "linguistics": (
        "Cost: 0.25 PP | Activation: Passive\n"
        "Focus superhuman perception, memorization, mimicry, and empathy to learn languages after a minimum of 1 hour of exposure "
        "without spending Karma, gaining the Language skill at the Basic level. Also provides +1 bonus die to Perception tests "
        "to understand any language in which you are trained.",
        "Street Wyrd p.81",
    ),
    "contacts": (
        "Optical lenses worn directly on the eyes (Capacity 1–3). "
        "Equipped with Image Link (AR display), Flare Compensation (ignores glare/flash modifiers), and Thermographic Vision (heat-signature spectrum).",
        "CRB p.274",
    ),
    "earbuds": (
        "In-ear audio enhancement unit (Capacity 1–3) for wireless commlink audio routing and acoustic filtering.",
        "CRB p.275",
    ),
    "nanopaste disguise kit": (
        "Biotech cream filled with programmable nanites that adhere to skin and reshape facial contours, texture, and pigmentation for physical disguise.",
        "CRB p.280 / Body Shop",
    ),
    "nanocosmetics kit": (
        "Programmable cosmetic nanites that dynamically shift hair color, makeup, and skin tone on command to support social infiltration and identity masking.",
        "Smooth Operations / Body Shop",
    ),
    "savior medkit": (
        "Rating 6 advanced nanotech trauma medkit capable of stabilizing critical injuries and assisting Biotech/First Aid tests.",
        "Body Shop p.123",
    ),
    "virtual machine": (
        "Commlink/deck utility that expands concurrent program slots by +2 while increasing Matrix damage taken by +1 box.",
        "CRB p.185",
    ),
    "nanomask": (
        "Commlink app that coordinates programmable facial/cosmetic nanites to defeat biometric and facial recognition scanners.",
        "Smooth Operations p.118",
    ),
    "mefeed": (
        "Social media and persona-curation commlink application that continuously broadcasts and manages public SIN lifestyle feeds.",
        "Hack & Slash p.47",
    ),
    "natural hacker": (
        "You use your innate connection to the Resonance to get things done in the Matrix. It's all you need.\n"
        "• Cost: 15 Karma\n"
        "• Game Effect: Whenever you take a Matrix action or a defense test against a Matrix action, complex form, or sprite power, you may choose to use your Resonance attribute in place of any other non-Matrix attribute used on that test. You may not replace Attack, Sleaze, Data Processing, or Firewall with Resonance using this quality.",
        "Hack & Slash p.83",
    ),
    "stream: technoshamans": (
        "Technoshamans integrate the spiritual with their abilities. They are experts on sprites, phenomenal at interacting with Resonance creatures.\n"
        "• Drain/Fade Attribute: Willpower + Charisma\n"
        "• Complex Form: Loto (Fade 4, Duration Instant)\n"
        "• Game Effect: All Compiling and Decompiling acts reduce Fade Value by 2. Gain the ability to compile hybrid sprites; +1 additional service when earning at least 1 hit on the Compiling test.",
        "Hack & Slash p.131 / CRB p.191",
    ),
    "designer": (
        "Some AIs are experts at restructuring firmware to achieve maximum hardware efficiency.\n"
        "• Cost: 6 Karma\n"
        "• Game Effect: Your self-designed home device grants an additional +1 modifier to the Data Processing or Pilot attribute and 2 points of noise reduction.",
        "Hack & Slash p.119",
    ),
    "sensor upgrade": (
        "The AI is an expert at tweaking the sensor settings of devices linked to it.\n"
        "• Cost: 5 Karma\n"
        "• Game Effect: Adds +1 to the Sensor rating of any vehicle, drone, or device that is linked to its icon. All functions of a single sensor array gain this bonus, if applicable. Also applies to any device the AI is currently running on.",
        "Hack & Slash p.120",
    ),
    "pilot origins": (
        "An AI with this quality likely evolved from a drone pilot program and retained its abilities.\n"
        "• Cost: 8 Karma per Level (max 3)\n"
        "• Game Effect: The AI may jump into drones and vehicles, controlling them like a rigger. Each level of this quality grants the bonus of a control rig of an equal rating. The AI is also capable of loading, converting, and using drone autosofts equal to its Data Processing (AI-driven drones use the attributes, skills, and Matrix Initiative of the AI). Piloting is by pure calculation and data processing.",
        "Hack & Slash p.120",
    ),
    "buddy system": (
        "You don't feel safe enough to concentrate clearly without someone to watch your back.\n"
        "• Bonus: 7 Karma\n"
        "• Game Effect: Whenever you are alone, you may only gain a maximum of one Edge per combat round. If you are in VR mode, having an agent program or sprite nearby (or a SimShare hitchhiker) is enough to prevent the penalty.",
        "Hack & Slash p.84",
    ),
    "sprite bane": (
        "A certain type of spirit/sprite has an inherent dislike for you.\n"
        "• Bonus: 12 Karma\n"
        "• Game Effect: Choose a type of spirit or sprite (Primal Sprite). Spirits/sprites from that category gain a bonus point of Edge when you attempt a Tasking test against them. In combat, Primal Sprites will attack you first and relentlessly. Character suffers a -2 dice pool penalty when interacting with or compiling/registering them.",
        "CRB p.79 / Berlin p.79",
    ),
    "hooder": (
        "You're driven to do what you can to help others.\n"
        "• Bonus: 5 Karma per level (max level 3). Rating 2 (10 Karma).\n"
        "• Game Effect: You must donate at least 1,000 nuyen per level of this quality every month. The donation cannot go to other members of your team, and you take a -2 dice pool modifier on Negotiation tests to increase pay for runs that help the needy.",
        "Sixth World Companion p.137",
    ),
    "new sprite type": (
        "Echo: Gain the ability to compile and register Assassin, Defender, Modular, and Primal sprites (see New Sprite Types, p. 72).",
        "Hack & Slash p.64",
    ),
    "sprite conduit": (
        "Echo: Able to form deep bonds with sprites, and through these bonds help register them into a more permanent form with expenditure of time and Karma.",
        "Hack & Slash p.65",
    ),
    "sprite symbiosis": (
        "Echo: Must have Sprite Conduit. Form a permanent symbiotic bond with registered ally sprite (Taz, Rating 6 Companion Sprite), sharing attributes (+4 augmented cap to ASDF), sprite powers, and continuous teamwork (+4d6). Ally sprite is undetectable except to entities with Resonance.",
        "Hack & Slash p.65 / p.79",
    ),
    "living network": (
        "Echo: Living Persona functions as a master PAN/WAN router capable of slaving devices and sharing network defense.",
        "Hack & Slash p.64",
    ),
    "transcendent network": (
        "Echo: Must have Living Network. When living persona functions as master device in a network, act as an advanced conduit for data, storing up to Submersion Grade (8) in shared network Edge and broadcasting TacApps.",
        "Hack & Slash p.65",
    ),
    "overclocking": (
        "Echo: Accelerate living persona to act more quickly in the Matrix. Gain an additional Minor Action and +1D6 Initiative Dice while in hot-sim VR.",
        "CRB p.195",
    ),
    "software emulator": (
        "Echo: Must have Living Network. Capable of running commlink apps, cyberprograms, and autosofts directly on living persona. Program slots equal to Submersion Grade (8).",
        "Hack & Slash p.68",
    ),
    "sprite link": (
        "Echo: Mind is more closely linked to sprites. When spending a task and a Minor Action to command a sprite to assist with a Matrix action, gain +1 Edge for that action.",
        "Hack & Slash p.64",
    ),
    "technoregeneration": (
        "Fade: Hits | Duration: Permanent | Target: Electronic Device\n"
        "The equivalent of a Heal spell for electronic devices. Make an Electronics (Hardware) + Resonance test; "
        "each hit restores 1 box of Matrix damage on a device (replaces 1 die with a Wild Die until 1 hour of toolkit maintenance is performed).",
        "Hack & Slash p.67",
    ),
    "cleaner": (
        "Fade: 2 | Duration: Permanent\n"
        "Make an Electronics + Resonance test. Each hit reduces your Overwatch Score (OS) by 1.",
        "CRB p.190",
    ),
    "diffusion": (
        "Fade: 4 | Duration: Sustained\n"
        "Make an Electronics + Resonance vs. Willpower + Firewall opposed test. Each net hit reduces the target's Matrix attribute (Firewall) by 1 (to a minimum of 1).",
        "CRB p.190",
    ),
    "puppeteer": (
        "Fade: 5 | Duration: Sustained\n"
        "Make an Electronics + Resonance vs. Willpower + Firewall test. If successful, you may take the Control Device action on a target device even without the required access level.",
        "CRB p.190",
    ),
    "cyber spike": (
        "Fade: Hits | Duration: Sustained\n"
        "Target a character with wireless-enabled cyberware (or via direct connection / Resonance Wires). "
        "Make an Electronics + Resonance test vs. Body + Essence (rounded down). Each net hit inflicts 1 box of Physical damage (resisted with Body) and stresses all cyberware for 1 combat round.",
        "Hack & Slash p.63",
    ),
    "resonance wires": (
        "Fade: 2 | Duration: Sustained\n"
        "Target a visible device or character and make an Electronics + Resonance (2 + Noise) test. "
        "Establishes a remote direct connection to the target's devices even if wireless mode is disabled.",
        "Hack & Slash p.66",
    ),
    "enlighten automaton": (
        "Fade: Hits | Duration: Sustained\n"
        "Target a drone/vehicle not currently jumped into and make an Electronics + Resonance test. "
        "Increase the target's Pilot and/or Sensor rating by your hits (up to double its base rating).",
        "Hack & Slash p.64",
    ),
    "resonance spike": (
        "Fade: 4 | Duration: Immediate\n"
        "Make a Cracking + Resonance vs. Willpower + Firewall test; each net hit causes 1 box of unresisted Matrix damage.",
        "CRB p.190",
    ),
}
CANONICAL_COMPLEX_FORMS: Dict[str, Dict[str, Any]] = {
    "puppeteer": {"fading": 5, "duration": "Sustained", "target": "Device", "page": "CRB p.190"},
    "diffusion": {"fading": 4, "duration": "Sustained", "target": "Device", "page": "CRB p.190"},
    "cleaner": {"fading": 2, "duration": "Permanent", "target": "Device", "page": "CRB p.190"},
    "cyber spike": {"fading": -1, "duration": "Immediate", "target": "Device", "page": "Hack & Slash p.63"},
    "resonance spike": {"fading": 4, "duration": "Immediate", "target": "Device", "page": "CRB p.190"},
    "technoregeneration": {"fading": -1, "duration": "Permanent", "target": "Electronic Device", "page": "Hack & Slash p.67"},
    "resonance wires": {"fading": 2, "duration": "Sustained", "target": "Device", "page": "Hack & Slash p.66"},
    "enlighten automaton": {"fading": -1, "duration": "Sustained", "target": "Device", "page": "Hack & Slash p.64"},
}



def _clean_rule_markdown(content: str) -> str:
    """Strip YAML frontmatter, neighboring spell bleed, and markdown headers from a `rules` chunk."""
    if not content:
        return ""
    # Remove YAML frontmatter
    text = re.sub(r"^---\s*\n.*?\n---\s*\n?", "", content, flags=re.DOTALL)
    # If this is a spell chunk containing "RANGE TYPE DURATION DV", trim any preceding
    # paragraph bleed from the previous spell on the same two-column page.
    m_spell_hdr = re.search(r"(RANGE\s+TYPE\s+DURATION\s+DV\b.*)", text, flags=re.DOTALL)
    if m_spell_hdr:
        text = m_spell_hdr.group(1)
    # Remove leading markdown headers (# / ## / ###)
    lines = []
    for line in text.splitlines():
        s = line.strip()
        if s.startswith("#"):
            continue
        lines.append(s)
    cleaned = "\n".join(lines).strip()
    # Collapse 3+ newlines into 2
    cleaned = re.sub(r"\n{3,}", "\n\n", cleaned)
    return cleaned


def _lookup_rule_text_and_page(
    conn: Optional[sqlite3.Connection],
    name: str,
    chapter_hint: Optional[str] = None,
) -> Tuple[str, str]:
    """
    Search `CANONICAL_RULE_DESCRIPTIONS` first (to avoid two-column PDF shifts),
    then query the `rules` vault table for the official rulebook description and
    page reference for a spell, adept power, quality, metamagic, or gear item.
    Returns (cleaned_description, source_and_page).
    """
    if not name:
        return "", ""
    clean_name = re.sub(r"\s*\(.*?\)", "", str(name)).strip()
    clean_name = re.sub(r"\s+(?:Rating|R)?\s*\d+$", "", clean_name, flags=re.I).strip()
    if not clean_name:
        return "", ""

    canon = CANONICAL_RULE_DESCRIPTIONS.get(clean_name.lower())
    if canon:
        return canon

    if conn is None:
        return "", ""

    try:
        cur = conn.cursor()
        # Try exact or prefix topic match first, prioritizing Hong Kong / Seattle / Core
        cur.execute(
            """
            SELECT source, page, chapter, topic, content
            FROM rules
            WHERE LOWER(topic) = LOWER(?)
               OR LOWER(topic) LIKE LOWER(?)
            ORDER BY
                CASE
                    WHEN LOWER(topic) = LOWER(?) THEN 0
                    ELSE 1
                END,
                CASE
                    WHEN source LIKE '%Hong Kong%' THEN 0
                    WHEN source LIKE '%Seattle%' THEN 1
                    WHEN source LIKE '%Berlin%' THEN 2
                    ELSE 3
                END
            LIMIT 8
            """,
            (clean_name, f"{clean_name}%", clean_name),
        )
        rows = [dict(r) for r in cur.fetchall()]
        if not rows:
            return "", ""

        chosen = rows[0]
        if chapter_hint:
            for r in rows:
                if chapter_hint.lower() in str(r.get("chapter") or "").lower():
                    chosen = r
                    break

        desc = _clean_rule_markdown(str(chosen.get("content") or ""))
        src = str(chosen.get("source") or "").strip()
        pg = str(chosen.get("page") or "").strip()
        page_label = f"{src} p.{pg}" if (src and pg and pg != "None") else src
        return desc, page_label
    except Exception:
        return "", ""


def _format_page(source: Any, page: Any = "", fallback_page: str = "") -> str:
    """Format book source and page string cleanly for Roll20 notes."""
    if fallback_page and ("p." in fallback_page or not source):
        return fallback_page
    src_str = str(source or "").strip()
    pg_str = str(page or "").strip()
    if src_str and pg_str and pg_str not in src_str:
        return f"{src_str} p.{pg_str}"
    return src_str or pg_str or fallback_page


def _combine_descriptions(char_notes: str, rule_desc: str) -> str:
    """Combine character-specific notes with official rulebook description cleanly."""
    c_clean = (char_notes or "").strip()
    r_clean = (rule_desc or "").strip()
    if c_clean and r_clean:
        if c_clean.lower() in r_clean.lower():
            return r_clean
        return f"{c_clean}\n\n{r_clean}"
    return c_clean or r_clean


def _parse_float(val: Any, default: float = 0.0) -> float:
    """Safely extract a float from int/float or strings like '2.0 PP' or '0.24'."""
    if isinstance(val, (int, float)):
        return float(val)
    if not val:
        return default
    m = re.search(r"[-+]?\d+(?:\.\d+)?", str(val))
    return float(m.group(0)) if m else default


def _parse_int(val: Any, default: int = 0) -> int:
    """Safely extract an integer from int/float or strings like 'Rating 4' or '3'."""
    if isinstance(val, (int, float)):
        return int(val)
    if not val:
        return default
    m = re.search(r"[-+]?\d+", str(val))
    return int(m.group(0)) if m else default


def _stringify_accessory_item(item: Any) -> str:
    """Convert an accessory/modification entry (str or dict) into a clean display string."""
    if isinstance(item, str):
        return item.strip()
    if isinstance(item, dict):
        if "name" in item:
            r = item.get("rating")
            return f"{item['name']} (R{r})" if r else str(item["name"]).strip()
        parts = [f"{k}: {v}" for k, v in item.items()]
        return ", ".join(parts).strip()
    return str(item).strip()


def _resolve_attribute_from_block(
    attrs_block: Dict[str, Any],
    sub_block_name: str,
    attr_key: str,
    default_val: int = 1,
) -> Tuple[int, int]:
    """
    Resolve (base, effective) integer values for an attribute, supporting both:
    - Flat schema: `attributes: {body: 2, charisma: 10, ...}`
    - Nested schema: `attributes: {physical: {body: {base: 2, effective: 4}}, ...}`
    """
    raw_val = attrs_block.get(attr_key)
    if raw_val is None:
        sub = attrs_block.get(sub_block_name)
        if isinstance(sub, dict):
            raw_val = sub.get(attr_key)

    if isinstance(raw_val, dict):
        base = _parse_int(raw_val.get("base", raw_val.get("value", default_val)), default_val)
        eff = _parse_int(
            raw_val.get("effective", raw_val.get("augmented", raw_val.get("total", base))),
            base,
        )
        return base, eff
    if isinstance(raw_val, (int, float)):
        val = int(raw_val)
        return val, val
    return default_val, default_val


def _normalize_aug_quality(grade: Any) -> str:
    """
    Map cyberware/bioware grade strings to Roll20's `aug_grades` lookup keys:
    'STANDARD', 'ALPHA', 'BETA', 'DELTA', 'USED'.
    """
    g = str(grade or "Standard").strip().upper()
    if "DELTA" in g:
        return "DELTA"
    if "BETA" in g:
        return "BETA"
    if "ALPHA" in g:
        return "ALPHA"
    if "USED" in g or "OMEGA" in g or "EXO" in g:
        return "USED"
    return "STANDARD"


def _normalize_spell_category(cat: Any) -> str:
    """
    Map spell category to Roll20's `spell_categories` lookup keys:
    'Combat spells', 'Detection spells', 'Heal spells', 'Illusion spells', 'Manipulation spells'.
    """
    c = str(cat or "").strip().lower()
    if "combat" in c:
        return "Combat spells"
    if "detect" in c:
        return "Detection spells"
    if "heal" in c or "health" in c:
        return "Heal spells"
    if "illusion" in c:
        return "Illusion spells"
    if "manipulat" in c:
        return "Manipulation spells"
    return "Manipulation spells"


def _normalize_spell_duration(dur: Any) -> str:
    """
    Map spell duration to Roll20's `spell_duration` lookup keys:
    'Instantaneous', 'Sustained', 'Limited', 'Permanent'.
    """
    d = str(dur or "").strip().lower()
    if "sustain" in d:
        return "Sustained"
    if "perm" in d:
        return "Permanent"
    if "limit" in d or "spec" in d:
        return "Limited"
    return "Instantaneous"


def _normalize_spell_range(rng: Any, is_area: bool = False) -> str:
    """
    Map spell range to Roll20's `spell_range` lookup keys:
    'Line of sight', 'Line of sight (Area)', 'Special', 'Touch'.
    """
    r = str(rng or "").strip().lower()
    if "touch" in r or r == "t":
        return "Touch"
    if "spec" in r:
        return "Special"
    if "(a)" in r or "area" in r or is_area:
        return "Line of sight (Area)"
    return "Line of sight"


def _normalize_spell_type(stype: Any) -> str:
    """
    Map spell type to Roll20's `spell_types` lookup keys: 'Physical', 'Mana'.
    """
    t = str(stype or "").strip().lower()
    if "phys" in t or t == "p":
        return "Physical"
    return "Mana"


def _extract_spell_features(
    spell: Dict[str, Any], db_row: Optional[Dict[str, Any]]
) -> List[str]:
    """
    Extract Roll20 spell feature keys:
    'direct', 'indirect', 'sense_single', 'sense_multi', 'area'.
    """
    features: List[str] = []
    raw_feats = spell.get("features") or []
    if isinstance(raw_feats, list):
        for f in raw_feats:
            fl = str(f).strip().lower()
            if fl in ("direct", "indirect", "sense_single", "sense_multi", "area"):
                features.append(fl)

    text_blob = " ".join(
        str(x or "")
        for x in (
            spell.get("name"),
            spell.get("range"),
            spell.get("effect"),
            spell.get("notes"),
            spell.get("description"),
            (db_row or {}).get("raw_xml"),
        )
    ).lower()

    if "indirect" in text_blob and "indirect" not in features:
        features.append("indirect")
    elif "direct" in text_blob and "direct" not in features:
        features.append("direct")

    if (
        "(a)" in str(spell.get("range", "")).lower()
        or "area" in str(spell.get("range", "")).lower()
        or "area" in str((db_row or {}).get("range", "")).lower()
    ) and "area" not in features:
        features.append("area")

    return features


def _normalize_adept_activation(act: Any, raw_xml: str = "") -> str:
    """
    Map adept power activation to Roll20's `power_activations` lookup keys:
    'MAJOR_ACTION', 'MINOR_ACTION', 'PASSIVE'.
    """
    text = f"{act or ''} {_parse_xml_attr(raw_xml, 'activation')}".strip().lower()
    if "major" in text:
        return "MAJOR_ACTION"
    if "minor" in text:
        return "MINOR_ACTION"
    return "PASSIVE"


def _normalize_cf_duration(dur: Any) -> str:
    """
    Map complex form duration to Roll20's `cf_durations` lookup keys:
    'Sustained', 'Immediate', 'Permanent'.
    """
    d = str(dur or "").strip().lower()
    if "sustain" in d:
        return "Sustained"
    if "perm" in d:
        return "Permanent"
    return "Immediate"


def _normalize_weapon_skill(skill: Any, category: Any = "", is_melee: bool = False) -> str:
    """
    Map weapon skill/category to one of Roll20's valid `weapon_skills` keys:
    'firearms', 'exotic_weapons', 'athletics', 'close_combat', 'engineering'.
    """
    s = str(skill or "").strip().lower().replace(" ", "_")
    if s in VALID_WEAPON_SKILLS:
        return s
    cat = str(category or "").strip().lower()
    if "exotic" in s or "exotic" in cat:
        return "exotic_weapons"
    if "throw" in s or "throw" in cat or "archery" in cat or "athletics" in s:
        return "athletics"
    if "gunnery" in s or "engineer" in s:
        return "engineering"
    if is_melee or any(k in cat for k in ("blade", "club", "unarmed", "melee", "close")):
        return "close_combat"
    return "firearms"


def _normalize_attack_rating(ar: Any, is_melee: bool = False) -> str:
    """
    Ensure weapon attackRating is always a 5-element slash-separated string
    'C/N/M/F/E' (e.g., '9/8/6/-/-' or '8/-/-/-/-').
    """
    if isinstance(ar, (list, tuple)):
        parts = [str(x).strip() if str(x).strip() not in ("", "0", "None") else "-" for x in ar]
    else:
        raw = str(ar or "").strip()
        if "/" in raw:
            parts = [p.strip() or "-" for p in raw.split("/")]
        elif raw and raw != "0":
            parts = [raw, "-", "-", "-", "-"]
        else:
            parts = ["-", "-", "-", "-", "-"]

    while len(parts) < 5:
        parts.append("-")
    return "/".join(parts[:5])


def _clean_qmd_line_text(line: str) -> str:
    """Strip inline Quarto `{python} ...` code, backticks, and markdown formatting."""
    cleaned = re.sub(r"`\s*\{?python[^`]*\}?\s*`", "", line)
    cleaned = re.sub(r"\{python[^}]*\}", "", cleaned)
    cleaned = re.sub(r"`[^`]*`", "", cleaned)
    cleaned = re.sub(r"\*+", "", cleaned)
    cleaned = re.sub(r"^[\s\-•*]+", "", cleaned)
    return cleaned.strip().rstrip(":").strip()


def _parse_chargen_contacts_from_build_qmd(char_repo_path: Optional[str]) -> List[Dict[str, Any]]:
    """
    Parse chargen contacts from `core/character_build.qmd` (e.g. `* Vincent Grisome (C5 L3)`)
    so starting contacts are included alongside mission contacts on the Roll20 Social tab.
    """
    contacts: List[Dict[str, Any]] = []
    if not char_repo_path or not os.path.exists(char_repo_path):
        return contacts

    build_path = os.path.join(char_repo_path, "core", "character_build.qmd")
    if not os.path.exists(build_path):
        return contacts

    try:
        with open(build_path, "r", encoding="utf-8") as f:
            lines = f.readlines()
    except Exception:
        return contacts

    in_contacts = False
    current_region = ""
    region_code_map = {
        "seattle": "SEA",
        "new orleans": "NOLA",
        "hong kong": "HK",
        "amsterdam": "AMS",
        "other": "ORG",
    }

    for raw_line in lines:
        stripped = raw_line.strip()
        if not stripped:
            continue
        if stripped.startswith("### "):
            header = stripped[4:].strip().lower()
            if header == "contacts":
                in_contacts = True
                continue
            elif in_contacts and header == "other":
                current_region = "ORG"
                continue
            elif header.endswith("contacts"):
                in_contacts = True
                reg_prefix = header.replace("contacts", "").strip()
                current_region = region_code_map.get(reg_prefix, reg_prefix.upper())
                continue
            elif in_contacts:
                in_contacts = False
                continue

        if not in_contacts:
            continue

        if stripped.startswith("#### "):
            reg_title = stripped[5:].strip().lower().replace("contacts", "").strip()
            current_region = region_code_map.get(reg_title, reg_title.upper())
            continue

        if raw_line.startswith("* ") or raw_line.startswith("- "):
            clean_txt = _clean_qmd_line_text(stripped)
            m = re.match(
                r"^(.+?)\s*\((?:([^,()]+),\s*)?C\s*(\d+)\s+L\s*(\d+)\)(?:\s*:\s*(.*))?$",
                clean_txt,
                re.IGNORECASE,
            )
            if m:
                cname = m.group(1).strip()
                paren_role = (m.group(2) or "").strip()
                conn_val = int(m.group(3))
                loy_val = int(m.group(4))
                role_desc = (m.group(5) or paren_role or "").strip()
                contacts.append(
                    {
                        "name": cname,
                        "connection": conn_val,
                        "loyalty": loy_val,
                        "favors": 0,
                        "type": role_desc or "Chargen Contact",
                        "region": current_region,
                        "description": f"Character Creation Contact ({current_region})"
                        + (f" — {role_desc}" if role_desc else ""),
                    }
                )

    return contacts


def _parse_extra_purchases_matrix_and_gear(char_repo_path: Optional[str]) -> Dict[str, Any]:
    """
    Parse `character_purchases.qmd` (if available) to pick up commlinks, cyberdecks,
    software library programs (basic, hacking, rigger, autosofts, knowsofts, commlink apps),
    sensor sub-items, and special contracts/subscriptions.
    """
    result: Dict[str, Any] = {
        "matrix_devices": [],
        "commlink_apps": [],
        "programs": [],
        "extra_gear": [],
    }
    if not char_repo_path or not os.path.exists(char_repo_path):
        return result

    qmd_path = os.path.join(char_repo_path, "core", "character_purchases.qmd")
    if not os.path.exists(qmd_path):
        qmd_path = os.path.join(char_repo_path, "chapters", "character_purchases.qmd")
    if not os.path.exists(qmd_path):
        return result

    try:
        with open(qmd_path, "r", encoding="utf-8") as f:
            lines = f.readlines()
    except Exception:
        return result

    current_section = ""
    current_sub_group = ""
    current_device: Optional[Dict[str, Any]] = None

    for raw_line in lines:
        stripped = raw_line.strip()
        if not stripped or stripped.startswith("---"):
            continue
        if stripped.startswith("### "):
            current_section = stripped[4:].strip().lower()
            current_sub_group = ""
            current_device = None
            continue

        is_top_bullet = bool(re.match(r"^[\*\-]\s+", raw_line))
        is_sub_bullet = bool(re.match(r"^\s+[\*\-]\s+", raw_line))

        if any(k in current_section for k in ("matrix", "electronic", "commlink", "software")):
            if is_top_bullet:
                current_device = None
                current_sub_group = ""
                clean_txt = _clean_qmd_line_text(stripped)
                low_txt = clean_txt.lower()
                if "software library" in low_txt:
                    current_sub_group = "programs"
                    continue
                if "autosoft" in low_txt:
                    current_sub_group = "autosofts"
                    continue
                if "knowsoft" in low_txt:
                    current_sub_group = "knowsofts"
                    continue
                if "commlink app" in low_txt or "utilities" in low_txt:
                    current_sub_group = "apps"
                    continue
                if "sensor" in low_txt or "audio / visual" in low_txt:
                    current_sub_group = "sensors"
                    continue
                if any(k in low_txt for k in ("data structure", "other")):
                    current_sub_group = "ignore"
                    continue

                m_dr = re.search(r"Device Rating\s*(\d+)", clean_txt, re.IGNORECASE)
                if m_dr:
                    dr = int(m_dr.group(1))
                    m_qty = re.search(r"\bx(\d+)\b", clean_txt, re.IGNORECASE)
                    qty = int(m_qty.group(1)) if m_qty else 1
                    dev_name = clean_txt.split("(")[0].strip()
                    if qty > 1:
                        dev_name = f"{dev_name} (x{qty})"
                    current_device = {
                        "name": dev_name,
                        "deviceRating": dr,
                        "subType": "CYBERDECK" if "deck" in low_txt else "COMMLINK",
                        "description": clean_txt,
                        "accessories": [],
                    }
                    result["matrix_devices"].append(current_device)
                    current_sub_group = "device_mods"
                    continue

                if current_section == "commlink apps":
                    app_name = re.sub(r"\s*\([^)]+\)\s*$", "", clean_txt).strip()
                    result["commlink_apps"].append(
                        {"name": app_name, "page": "CRB/HS", "description": ""}
                    )
            elif is_sub_bullet:
                sub_txt = _clean_qmd_line_text(stripped)
                if not sub_txt:
                    continue
                if sub_txt.lower() in (
                    "basic programs",
                    "hacking programs",
                    "rigger programs",
                    "knowledge",
                ):
                    continue
                if current_sub_group == "device_mods" and current_device is not None:
                    m_r = re.search(r"\((?:Rating|R)\s*(\d+)\)", sub_txt, re.I)
                    r_val = int(m_r.group(1)) if m_r else 0
                    mod_clean = re.sub(
                        r"\s*\((?:Rating|R)\s*\d+\)", "", sub_txt, flags=re.I
                    ).strip()
                    current_device["accessories"].append({"name": mod_clean, "rating": r_val})
                elif current_sub_group in ("programs", "autosofts", "knowsofts", "apps"):
                    result["programs"].append(
                        {
                            "name": sub_txt,
                            "page": "CRB / Hack & Slash",
                            "description": f"Matrix Program ({current_sub_group.title()})",
                        }
                    )
                    if current_sub_group == "apps":
                        result["commlink_apps"].append(
                            {"name": sub_txt, "page": "CRB/HS", "description": "Commlink App"}
                        )
                elif current_sub_group == "sensors":
                    m_r = re.search(r"\((?:Rating|R)\s*(\d+)", sub_txt, re.I)
                    r_val = int(m_r.group(1)) if m_r else ""
                    result["extra_gear"].append(
                        {
                            "name": sub_txt,
                            "rating": r_val,
                            "quantity": 1,
                            "category": "Sensor / Audio-Visual",
                        }
                    )

        elif (
            "special asset" in current_section
            or "subscription" in current_section
            or "contract" in current_section
        ):
            if is_top_bullet:
                clean_txt = _clean_qmd_line_text(stripped)
                if clean_txt:
                    name_part = clean_txt.split(":")[0].strip()
                    notes_part = clean_txt.split(":", 1)[1].strip() if ":" in clean_txt else ""
                    result["extra_gear"].append(
                        {
                            "name": name_part,
                            "rating": "",
                            "quantity": 1,
                            "category": "Contract / Service",
                            "notes": notes_part,
                        }
                    )

    return result


def _collect_skill_influences(char_data: Dict[str, Any]) -> Dict[str, List[str]]:
    """
    Build a mapping of active skill_id -> list of modifier descriptions from
    `modifiers`, `synergies` (foci, mentor spirit), `adept_powers`, and `augmentations`.
    """
    influences: Dict[str, List[str]] = {}

    def add_inf(skill_id: str, text: str) -> None:
        bucket = influences.setdefault(skill_id, [])
        if text not in bucket:
            bucket.append(text)

    for mod in char_data.get("modifiers") or []:
        if not isinstance(mod, dict) or not mod.get("enabled", True):
            continue
        mname = str(mod.get("name") or "Modifier").strip()
        target = str(mod.get("target") or "").strip().lower()
        val = _parse_int(mod.get("value"), 0)
        mnotes = str(mod.get("notes") or "").strip()
        val_str = f"{val:+d}d6" if val else ""
        label = (
            f"{mname} ({val_str}: {mnotes})"
            if (val_str and mnotes)
            else (f"{mname} ({val_str})" if val_str else f"{mname} ({mnotes})")
        )

        if target.startswith("skill:"):
            sk_key = target.split(":", 1)[1].strip().replace(" ", "_")
            if sk_key in ROLL20_ACTIVE_SKILLS:
                add_inf(sk_key, label)
        elif target == "attribute:magic":
            for m_sk in ("sorcery", "conjuring", "enchanting", "astral"):
                add_inf(m_sk, label)
        elif target == "attribute:resonance":
            add_inf("tasking", label)
            add_inf("cracking", label)
            add_inf("electronics", label)
        elif target in ("matrix_actions", "all_matrix_actions"):
            for r_sk in ("cracking", "electronics", "tasking"):
                add_inf(r_sk, label)

    synergies = char_data.get("synergies") or {}
    if isinstance(synergies, dict):
        for focus in synergies.get("foci") or []:
            if not isinstance(focus, dict):
                continue
            fname = str(focus.get("name") or "Focus").strip()
            if "oracle" in fname.lower():
                continue
            frating = _parse_int(focus.get("rating", focus.get("force", 0)), 0)
            fmods = focus.get("modifiers") or {}
            bonus = _parse_int(
                fmods.get("magic_dice") if isinstance(fmods, dict) else frating, frating
            )
            if bonus > 0:
                label = f"{fname} (+{bonus}d6)"
                if "resonance" in fname.lower():
                    for r_skill in ("tasking", "cracking", "electronics"):
                        if not any(fname.lower() in x.lower() for x in influences.get(r_skill, [])):
                            add_inf(r_skill, label)
                else:
                    for m_skill in ("sorcery", "conjuring", "enchanting", "astral"):
                        if not any(
                            fname.lower() in x.lower() or "power focus" in x.lower()
                            for x in influences.get(m_skill, [])
                        ):
                            add_inf(m_skill, label)

        ms = synergies.get("mentor_spirit") or {}
        if isinstance(ms, dict) and ms.get("name"):
            ms_name = ms["name"]
            ms_mods = ms.get("modifiers") or {}
            if isinstance(ms_mods, dict):
                for sk_key, bonus in ms_mods.items():
                    norm_sk = sk_key.strip().lower().replace(" ", "_")
                    if norm_sk in ROLL20_ACTIVE_SKILLS:
                        add_inf(norm_sk, f"Mentor Spirit: {ms_name} (+{bonus}d6)")

    for ap in char_data.get("adept_powers") or []:
        if not isinstance(ap, dict):
            continue
        ap_name = str(ap.get("name") or "").strip()
        ap_low = ap_name.lower()
        if "command presence" in ap_low:
            add_inf("influence", f"{ap_name} (+2d6 & +1 Edge on Leadership)")
        elif "cosmetic control" in ap_low:
            add_inf("con", f"{ap_name} (-1 Edge cost on Con / Disguise)")
        elif "vocal control" in ap_low:
            add_inf("con", f"{ap_name} (+1d6)")
            add_inf("influence", f"{ap_name} (+1d6)")
        elif "traceless walk" in ap_low:
            add_inf("stealth", f"{ap_name} (Ignore sound/surface modifiers)")

    for aug in (char_data.get("augmentations") or []) + (char_data.get("cyberware") or []):
        if not isinstance(aug, dict):
            continue
        aug_name = str(aug.get("name") or "").strip()
        aug_rating = _parse_int(aug.get("rating"), 1)
        if "tailored pheromones" in aug_name.lower():
            add_inf("con", f"{aug_name} (+{aug_rating}d6 in aroma range)")
            add_inf("influence", f"{aug_name} (+{aug_rating}d6 in aroma range)")
        elif "smartlink" in aug_name.lower():
            add_inf("firearms", f"{aug_name} (+1d6 wireless Dice Pool, +2 AR)")

    return influences


def build_roll20_payload(
    char_data: Dict[str, Any],
    char_repo_path: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Construct the complete Roll20 Shadowrun Sixth World Genesis JSON dictionary
    from a compiled character dossier (`*_master.yaml`).
    """
    conn = _get_db_connection()
    identity = char_data.get("identity") or {}
    attrs_block = char_data.get("attributes") or {}
    resources = char_data.get("resources") or {}
    reputation_block = char_data.get("reputation") or {}

    ledger_totals: Dict[str, Any] = {}
    if char_repo_path and os.path.exists(char_repo_path):
        try:
            from sr6core.character.ledger import CharacterLedger

            ledger = CharacterLedger(char_repo_path)
            ledger_totals = ledger.get_totals() or {}
        except Exception:
            ledger_totals = {}

    extra_purchases = _parse_extra_purchases_matrix_and_gear(char_repo_path)
    chargen_contacts = _parse_chargen_contacts_from_build_qmd(char_repo_path)

    # 1. Identity & Top-Level Fields
    street_name = str(
        identity.get("name")
        or identity.get("handle")
        or identity.get("street_name")
        or "Runner"
    )
    birth_name = str(
        identity.get("real_name")
        or identity.get("legal_name")
        or identity.get("birth_name")
        or street_name
    )
    metatype = str(identity.get("metatype") or "Human")
    age = str(identity.get("age") or "")
    gender = str(identity.get("gender") or identity.get("sex") or "")
    size = str(identity.get("size") or identity.get("height") or "")
    weight = str(identity.get("weight") or "")

    karma_block = resources.get("karma")
    if isinstance(karma_block, dict):
        free_karma = _parse_int(karma_block.get("available"), 0)
        total_karma = _parse_int(
            karma_block.get("career_total")
            or karma_block.get("total")
            or identity.get("lifetime_karma")
            or ledger_totals.get("Career_Karma")
            or free_karma,
            free_karma,
        )
    else:
        free_karma = _parse_int(
            identity.get("karma")
            if identity.get("karma") is not None
            else (ledger_totals.get("Karma") or identity.get("karma_available") or 0),
            0,
        )
        total_karma = _parse_int(
            identity.get("lifetime_karma")
            or ledger_totals.get("Lifetime_Karma")
            or ledger_totals.get("Career_Karma")
            or identity.get("karma_total")
            or free_karma,
            free_karma,
        )

    nuyen_block = resources.get("nuyen")
    if isinstance(nuyen_block, dict):
        nuyen = _parse_int(nuyen_block.get("available"), 0)
    elif isinstance(nuyen_block, (int, float)):
        nuyen = int(nuyen_block)
    else:
        nuyen = _parse_int(
            identity.get("nuyen")
            if identity.get("nuyen") is not None
            else (ledger_totals.get("Nuyen") or identity.get("nuyen_available") or 0),
            0,
        )

    metamagic_raw = char_data.get("metamagic") or []
    echoes_raw = char_data.get("echoes") or []
    initiation = _parse_int(
        identity.get("initiation")
        or identity.get("initiate_grade")
        or ledger_totals.get("Initiation_Grade")
        or len(metamagic_raw),
        0,
    )
    submersion = _parse_int(
        identity.get("submersion")
        or identity.get("submersion_grade")
        or ledger_totals.get("Submersion_Grade")
        or len(echoes_raw),
        0,
    )

    heat = _parse_int(
        identity.get("heat")
        if identity.get("heat") is not None
        else (
            reputation_block.get("heat")
            if isinstance(reputation_block, dict)
            else ledger_totals.get("Heat")
        ),
        0,
    )

    if char_data.get("total_reputation") is not None:
        reputation = _parse_int(char_data.get("total_reputation"), 0)
    elif isinstance(reputation_block, dict):
        if "total_reputation" in reputation_block or "reputation" in reputation_block:
            reputation = _parse_int(
                reputation_block.get("total_reputation", reputation_block.get("reputation")), 0
            )
        else:
            reputation = sum(
                int(v)
                for k, v in reputation_block.items()
                if isinstance(v, (int, float)) and k != "heat"
            )
    else:
        reputation = _parse_int(ledger_totals.get("Reputation"), 0)

    notes_lines: List[str] = []
    for label, key in (
        ("Concept", "concept"),
        ("Archetype", "mortype"),
        ("Role", "role"),
        ("Archetype", "archetype"),
        ("Tradition", "tradition"),
        ("Stream", "stream"),
        ("Heritage", "heritage"),
    ):
        if identity.get(key):
            line = f"{label}: {identity[key]}"
            if line not in notes_lines:
                notes_lines.append(line)

    if isinstance(reputation_block, dict) and any(
        k in reputation_block for k in ("SEA", "AMS", "HK")
    ):
        reg_str = ", ".join(
            f"{k}: {v}" for k, v in reputation_block.items() if isinstance(v, (int, float))
        )
        notes_lines.append(f"Regional Reputation: {reg_str} (Total: {reputation})")

    aug_attr_notes: List[str] = []
    for label, sub_name, key in (
        ("BOD", "physical", "body"),
        ("AGI", "physical", "agility"),
        ("REA", "physical", "reaction"),
        ("STR", "physical", "strength"),
        ("WIL", "mental", "willpower"),
        ("LOG", "mental", "logic"),
        ("INT", "mental", "intuition"),
        ("CHA", "mental", "charisma"),
    ):
        b_val, e_val = _resolve_attribute_from_block(attrs_block, sub_name, key, 1)
        if b_val != e_val:
            aug_attr_notes.append(f"{label}: {b_val} ({e_val})")
    if aug_attr_notes:
        notes_lines.append(
            "Augmented Attributes (Natural -> Effective): " + ", ".join(aug_attr_notes)
        )

    player_notes = "\n".join(notes_lines) if notes_lines else f"{street_name} ({metatype})"

    # 2. Attributes (`json.attributes`)
    is_ai = "ai" in metatype.lower()
    _raw_w = char_data.get("weapons") or []
    _all_w = (_raw_w.get("ranged", []) + _raw_w.get("melee", [])) if isinstance(_raw_w, dict) else (_raw_w if isinstance(_raw_w, list) else [])
    has_red_fox = any("red fox" in str(w.get("name", "")).lower() for w in _all_w if isinstance(w, dict))
    attributes_list: List[Dict[str, Any]] = []
    core_attr_map = [
        ("BODY", "physical", "body", 1),
        ("AGILITY", "physical", "agility", 1),
        ("REACTION", "physical", "reaction", 1),
        ("STRENGTH", "physical", "strength", 1),
        ("WILLPOWER", "mental", "willpower", 1),
        ("LOGIC", "mental", "logic", 1),
        ("INTUITION", "mental", "intuition", 1),
        ("CHARISMA", "mental", "charisma", 1),
        ("EDGE", "special", "edge", 1),
    ]
    for r20_id, sub_name, attr_key, default_v in core_attr_map:
        _base, eff = _resolve_attribute_from_block(attrs_block, sub_name, attr_key, default_v)
        if is_ai:
            # Per Hack & Slash Matrix-to-Physical Equivalence table (AGI = DP 7, REA = Sleaze 9,
            # STR = Attack 7) and Reiko's inhabited Shiawase Man-at-Arms (Body 10 + 5 = 15)
            if r20_id == "BODY":
                eff = 15
            elif r20_id == "AGILITY":
                eff = 7
            elif r20_id == "REACTION":
                eff = 9
            elif r20_id == "STRENGTH":
                eff = 7
        attributes_list.append(
            {
                "id": r20_id,
                "points": eff,
                "modifiedValue": eff,
            }
        )

    _, magic_eff = _resolve_attribute_from_block(attrs_block, "special", "magic", 0)
    _, res_eff = _resolve_attribute_from_block(attrs_block, "special", "resonance", 0)
    _, pp_eff = _resolve_attribute_from_block(attrs_block, "special", "power_points", 0)

    adept_powers_raw = char_data.get("adept_powers") or []
    if pp_eff <= 0 and adept_powers_raw:
        total_pp = sum(
            _parse_float(ap.get("cost_pp", ap.get("cost")), 0.0)
            for ap in adept_powers_raw
            if isinstance(ap, dict)
        )
        pp_eff = int(math.ceil(total_pp)) if total_pp > 0 else 0

    if magic_eff > 0:
        attributes_list.append(
            {
                "id": "MAGIC",
                "points": magic_eff,
                "modifiedValue": magic_eff,
            }
        )
    if res_eff > 0:
        attributes_list.append(
            {
                "id": "RESONANCE",
                "points": res_eff,
                "modifiedValue": res_eff,
            }
        )
    if pp_eff > 0:
        attributes_list.append(
            {
                "id": "POWER_POINTS",
                "points": pp_eff,
                "modifiedValue": pp_eff,
            }
        )

    # 3. Qualities (`json.qualities`) with full rulebook descriptions from `rules` vault
    qualities_list: List[Dict[str, Any]] = []
    seen_qualities = set()
    qualities_block = char_data.get("qualities") or {}

    def _process_quality_entry(q: Any, is_positive: bool) -> None:
        if isinstance(q, str):
            q = {"name": q}
        if not isinstance(q, dict):
            return
        raw_name = str(q.get("name") or "").strip()
        if not raw_name:
            return
        choice = str(q.get("choice") or "").strip()
        base_name = raw_name

        m_paren = re.search(r"^(.*?)\s*\(([^)]+)\)\s*$", raw_name)
        if m_paren and not re.match(r"^(?:Rating|R|Level)\s*\d+$", m_paren.group(2), re.I):
            base_name = m_paren.group(1).strip()
            paren_choice = m_paren.group(2).strip()
            if not choice or choice.lower() in paren_choice.lower():
                choice = paren_choice
        elif choice and f"({choice.lower()})" in raw_name.lower():
            base_name = re.sub(
                rf"\s*\({re.escape(choice)}\)", "", raw_name, flags=re.IGNORECASE
            ).strip()

        dedup_key = (base_name.lower(), choice.lower(), is_positive)
        if dedup_key in seen_qualities:
            return
        seen_qualities.add(dedup_key)

        db_row = _lookup_db_row(conn, "ref_qualities", q.get("ref"), base_name)
        rule_desc, rule_page = _lookup_rule_text_and_page(conn, base_name, chapter_hint="Qualit")
        if base_name.lower() == "mentor spirit" and choice:
            ms_desc, ms_page = _lookup_rule_text_and_page(conn, choice, chapter_hint="Mentor")
            if ms_desc:
                rule_desc = ms_desc
                rule_page = ms_page or rule_page

        rating_val = q.get("rating", q.get("level", ""))
        rating_out: Any = (
            int(rating_val) if isinstance(rating_val, (int, float)) and rating_val > 0 else ""
        )

        page_str = _format_page(
            q.get("source") or (db_row or {}).get("source"),
            q.get("page") or _parse_xml_attr((db_row or {}).get("raw_xml", ""), "page"),
            fallback_page=rule_page,
        )
        char_q_notes = " | ".join(
            str(x).strip()
            for x in (
                q.get("effect"),
                q.get("notes"),
                q.get("description"),
                _strip_xml_tags((db_row or {}).get("raw_xml", "")),
            )
            if x and str(x).strip()
        )
        full_desc = _combine_descriptions(char_q_notes, rule_desc)

        qualities_list.append(
            {
                "name": base_name,
                "choice": choice,
                "positive": is_positive,
                "rating": rating_out,
                "page": page_str,
                "description": full_desc,
            }
        )

    if isinstance(qualities_block, dict):
        for q in qualities_block.get("positive") or []:
            _process_quality_entry(q, True)
        for q in qualities_block.get("negative") or []:
            _process_quality_entry(q, False)
    elif isinstance(qualities_block, list):
        for q in qualities_block:
            is_pos = bool(q.get("positive", True)) if isinstance(q, dict) else True
            _process_quality_entry(q, is_pos)

    if is_ai:
        qualities_list.append(
            {
                "name": "Network Benefits",
                "choice": "Transcendent Network + M-TOC Mark II",
                "positive": True,
                "rating": "",
                "page": "Firing Squad p.68 / Hack & Slash p.65",
                "description": (
                    "• 13 Edge Storage (5 M-TOC Mark II, 8 Transcendent Network)\n"
                    "• -6 Noise Reduction (-2 Signal Scrubber program, -2 Home Device / Designer quality, -2 ECM Warrior II TacApp)\n"
                    "• +1 Sensor Rating to any connected drone/vehicle (Sensor Upgrade quality)\n"
                    "• Detect Ambush: -2 threshold (M-TOC Mark II)\n"
                    "• Smartguns: Extra +1 Attack Rating via Smartsoft array (drone target locks shared across PAN)\n"
                    "• Encryption: +1 threshold to incoming Cracking tests against any PAN device\n"
                    "• TacApps (4 Active on M-TOC Mark II):\n"
                    "  - ECM Warrior II (+2 Dice Pool to offensive Cracking tests, -2 Noise)\n"
                    "  - Sneak-Sneak (+2 Teamwork Dice to Stealth tests)\n"
                    "  - Target Artist (Shared LOS; reduce cover bonus by 1; ignore blind fire penalty)\n"
                    "  - Artillery Barrage (+1 Dice Pool to launcher/indirect fire tests)\n"
                    "  - [In Library: Mobile Medic (+1 First Aid / Medkit teamwork)]\n"
                    "• Coordination: Connected characters using Send Message (Minor Action) immediately gain 1 bonus Minor Action (1/round)."
                ),
            }
        )
        qualities_list.append(
            {
                "name": "Matrix Defense Umbrella",
                "choice": "21d6 Standard / 34d6 Full Matrix Defense",
                "positive": True,
                "rating": "",
                "page": "CRB p.181 / Hack & Slash p.33, 65, 119",
                "description": (
                    "• Matrix Defense Rating (DR): 16 (Data Processing 7 + Firewall 9) — treated as +4 higher (20 DR) for Edge comparison via Designer Home Device (H&S p.119).\n"
                    "• Encryption: +1 threshold to all incoming Cracking tests against any device on Reiko's PAN.\n"
                    "• Standard Matrix Defense vs. Attack Actions (e.g., Data Spike, Crack File): 21d6 (5 Bought Hits) = Firewall (9) + Natural Hacker Resonance (8) + Resonance Focus (+4).\n"
                    "• Standard Matrix Defense vs. Sleaze Actions (e.g., Spoof Command, Backdoor Entry, Probe): 21d6 (5 Bought Hits) = Firewall (9) + Natural Hacker Resonance (8) + Resonance Focus (+4).\n"
                    "• Full Matrix Defense (Major Action — All Matrix Attacks for Round): 34d6 (8 Bought Hits) = Resonance (8) + Resonance Focus (+4) + Firewall (9) + Personal Assistant App R6 (+6) + Directional Shield Active Data Processing (+7).\n"
                    "• Biofeedback / Matrix Soak: Firewall (9) + Armor Program (+2) + Biofeedback Filter (+2 vs Biofeedback)."
                ),
            }
        )

    # 4. Skills, Knowledges & Languages (`json.skills`)
    skills_list: List[Dict[str, Any]] = []
    seen_active_skills = set()
    seen_knowledge_skills = set()
    skill_influences = _collect_skill_influences(char_data)

    raw_skills = char_data.get("skills") or []
    raw_knowledges = char_data.get("knowledge_skills") or []
    has_dedicated_knowledges = len(raw_knowledges) > 0

    for sk in raw_skills:
        if not isinstance(sk, dict):
            continue
        sk_id_raw = str(sk.get("id") or "").strip().lower()
        sk_name_raw = str(sk.get("name") or "").strip()
        is_know = (
            bool(sk.get("is_knowledge"))
            or sk_id_raw in ("knowledge", "language")
            or sk_id_raw.startswith("language_")
            or "language" in sk_name_raw.lower()
        )

        if is_know:
            if has_dedicated_knowledges:
                continue
            k_id = (
                "language"
                if ("lang" in sk_id_raw or "language" in sk_name_raw.lower())
                else "knowledge"
            )
            if (k_id, sk_name_raw.lower()) not in seen_knowledge_skills:
                seen_knowledge_skills.add((k_id, sk_name_raw.lower()))
                skills_list.append(
                    {
                        "id": k_id,
                        "name": sk_name_raw,
                        "rating": 0,
                        "attribute": "@{intuition}" if k_id == "language" else "@{logic}",
                        "specializations": [],
                        "influencedBy": [],
                        "description": str(sk.get("notes") or ""),
                    }
                )
            continue

        lookup_key = sk_id_raw if sk_id_raw in ROLL20_ACTIVE_SKILLS else sk_name_raw.lower()
        if lookup_key not in ROLL20_ACTIVE_SKILLS:
            lookup_key = lookup_key.replace("_", " ")
        if lookup_key not in ROLL20_ACTIVE_SKILLS:
            continue

        r20_skill_id, r20_display_name, default_attr = ROLL20_ACTIVE_SKILLS[lookup_key]
        if r20_skill_id in seen_active_skills:
            continue
        seen_active_skills.add(r20_skill_id)

        rating = _parse_int(sk.get("rating"), 0)
        attr_name = str(sk.get("attribute") or default_attr).strip().lower()
        if not attr_name.startswith("@{"):
            attr_name = f"@{{{attr_name}}}"

        specs_out: List[Dict[str, Any]] = []
        seen_specs = set()

        def _add_spec(s_name: str, is_exp: bool = False) -> None:
            s_clean = s_name.strip()
            if not s_clean or s_clean.lower() in seen_specs:
                return
            seen_specs.add(s_clean.lower())
            specs_out.append({"name": s_clean, "expertise": is_exp})

        if sk.get("expertise"):
            exp_val = sk["expertise"]
            if isinstance(exp_val, list):
                for e in exp_val:
                    _add_spec(str(e), True)
            else:
                _add_spec(str(exp_val), True)

        if sk.get("specialization"):
            _add_spec(str(sk["specialization"]), False)

        for sp in sk.get("specializations") or []:
            if isinstance(sp, dict):
                _add_spec(str(sp.get("name", "")), bool(sp.get("expertise", False)))
            else:
                _add_spec(str(sp), False)

        inf_list = list(skill_influences.get(r20_skill_id, []))
        skills_list.append(
            {
                "id": r20_skill_id,
                "name": r20_display_name,
                "rating": rating,
                "attribute": attr_name,
                "specializations": specs_out,
                "influencedBy": inf_list,
                "description": str(sk.get("notes") or ""),
            }
        )

    if is_ai and has_red_fox:
        # Add emulated autosoft skills (Pilot Origins / Software Emulator)
        if "biotech" not in seen_active_skills:
            seen_active_skills.add("biotech")
            skills_list.append(
                {
                    "id": "biotech",
                    "name": "Biotech",
                    "rating": 7,
                    "attribute": "@{logic}",
                    "specializations": [],
                    "influencedBy": ["Emulated Autosoft (Rating 9, capped by Data Processing 7)"],
                    "description": "Emulated Autosoft via Pilot Origins (H&S p. 120) & Software Emulator echo. Rating 9 software capped by DP 7. Meatspace skill: uses Real Logic 4 (not Natural Hacker 12) + Rating 7 + Mobile Medic 4 = 15d6 Pool. Set Modifier to -4 (-8 Natural Hacker + 4 Mobile Medic).",
                }
            )
        if "engineering" not in seen_active_skills:
            seen_active_skills.add("engineering")
            skills_list.append(
                {
                    "id": "engineering",
                    "name": "Engineering",
                    "rating": 5,
                    "attribute": "@{logic}",
                    "specializations": [{"name": "Drones", "expertise": False}],
                    "influencedBy": ["Emulated Autosoft (Rating 9, capped by DP 7 -> Rating 5 + Drones Spec 2)"],
                    "description": "Emulated Autosoft via Pilot Origins (H&S p. 120) & Software Emulator echo. Rating 5 + Drones Spec 2 (effective autosoft ceiling 7). Usable only for Drones. Meatspace skill: uses Real Logic 4 (not Natural Hacker 12) + Rating 5 + Drones Spec 2 + Taz Teamwork 4 = 15d6 Pool. Set Modifier to -4 (-8 Natural Hacker + 4 Taz Teamwork).",
                }
            )
        if "outdoors" not in seen_active_skills:
            seen_active_skills.add("outdoors")
            skills_list.append(
                {
                    "id": "outdoors",
                    "name": "Outdoors",
                    "rating": 5,
                    "attribute": "@{intuition}",
                    "specializations": [{"name": "Navigation", "expertise": False}],
                    "influencedBy": ["Emulated Autosoft (Rating 9, capped by DP 7 -> Rating 5 + Navigation Spec 2)"],
                    "description": "Emulated Autosoft via Pilot Origins (H&S p. 120) & Software Emulator echo. Rating 5 + Navigation Spec 2 (effective autosoft ceiling 7). Usable only for Navigation. Meatspace skill: uses Real Intuition 2 (not Natural Hacker 12) + Rating 5 + Navigation Spec 2 = 9d6 Pool. Set Modifier to -10 (-10 Natural Hacker).",
                }
            )

    if is_ai and has_red_fox:
        extra_emulated_knowledges = [
            {"name": "Performance (R9 Autosoft)", "category": "knowledge", "notes": "Emulated Autosoft (Rating 9, capped by DP 7) via Pilot Origins. Emulates Con: Performance."},
        ]
        raw_knowledges = list(raw_knowledges) + [
            k for k in extra_emulated_knowledges if not any(k["name"].lower() in str(rk.get("name", "")).lower() for rk in raw_knowledges)
        ]

    for ksk in raw_knowledges:
        if not isinstance(ksk, dict):
            continue
        k_name = str(ksk.get("name") or "").strip()
        if not k_name:
            continue
        k_cat = str(ksk.get("category") or "").strip().lower()
        k_notes = str(ksk.get("notes") or "").strip()
        k_level = str(ksk.get("level") or "").strip()

        is_lang = (
            "lang" in k_cat
            or bool(ksk.get("is_native"))
            or bool(ksk.get("is_linguasoft"))
            or bool(k_level)
            or "language" in k_notes.lower()
        )
        k_id = "language" if is_lang else "knowledge"

        display_k_name = k_name
        if k_id == "language":
            tier_label = k_level
            if not tier_label and k_notes:
                for tier in ("Native", "Expert", "Specialist", "Basic", "Competent"):
                    if tier.lower() in k_notes.lower():
                        tier_label = tier
                        break
            if tier_label and tier_label.lower() not in k_name.lower():
                display_k_name = f"{k_name} ({tier_label})"

        dedup_k = (k_id, display_k_name.lower())
        if dedup_k in seen_knowledge_skills:
            continue
        seen_knowledge_skills.add(dedup_k)

        skills_list.append(
            {
                "id": k_id,
                "name": display_k_name,
                "rating": 0,
                "attribute": "@{intuition}" if k_id == "language" else "@{logic}",
                "specializations": [],
                "influencedBy": [],
                "description": k_notes,
            }
        )

    # 5. Armor (`json.armors`) - Split out cumulative sub-pieces (Ballistic Hood, RACS)
    # so Roll20 automatically checks Primary on SkinShield (+2) and Cumulative on
    # Ballistic Hood (+1) and RACS (+2)!
    armors_list: List[Dict[str, Any]] = []
    extra_wardrobe_items: List[Dict[str, Any]] = []
    raw_armors = char_data.get("armors") or char_data.get("armor") or []

    primary_idx = 0
    best_rating = -1
    for idx, arm in enumerate(raw_armors):
        if not isinstance(arm, dict):
            continue
        aname = str(arm.get("name") or "").lower()
        if any(k in aname for k in CUMULATIVE_ARMOR_KEYWORDS):
            continue
        r_val = _parse_int(arm.get("defense_rating", arm.get("rating", 0)), 0)
        if r_val > best_rating:
            best_rating = r_val
            primary_idx = idx

    extracted_cumulative_armors: List[Dict[str, Any]] = []

    for idx, arm in enumerate(raw_armors):
        if not isinstance(arm, dict):
            continue
        aname = str(arm.get("name") or "").strip()
        if not aname:
            continue
        arating = _parse_int(arm.get("defense_rating", arm.get("rating", 0)), 0)
        notes = str(arm.get("notes") or arm.get("description") or "").strip()

        accessories_out: List[Dict[str, Any]] = []
        for mod in arm.get("modifications") or arm.get("accessories") or []:
            mod_str = _stringify_accessory_item(mod)
            if not mod_str:
                continue
            mod_low = mod_str.lower()
            # Check if this accessory is a cumulative DR piece (Ballistic Hood or RACS)
            if "ballistic hood" in mod_low:
                extracted_cumulative_armors.append(
                    {
                        "name": "Ballistic Hood",
                        "rating": 1,
                        "socialrating": 0,
                        "isIgnored": False,
                        "primary": False,
                        "page": "Firing Squad p.55",
                        "description": "Cumulative +1 Defense Rating hood attachment.",
                        "accessories": [],
                    }
                )
                continue
            elif (
                "ruthenium armor" in mod_low
                or "rapid adjustment clothing system" in mod_low
                or "racs" in mod_low
            ):
                m_racs = re.search(r"(\d+)", mod_str)
                racs_r = int(m_racs.group(1)) if m_racs else 2
                extracted_cumulative_armors.append(
                    {
                        "name": f"Ruthenium Armor Concealment System (RACS {racs_r})",
                        "rating": 2,
                        "socialrating": 0,
                        "isIgnored": False,
                        "primary": False,
                        "page": "Firing Squad p.54",
                        "description": (
                            f"Ruthenium Armor Concealment System (Rating {racs_r}): Chameleon suit modification included with SecureTech SkinShield. "
                            f"Grants +2 Defense Rating during combat due to shifting patterns (Cumulative), +1 bonus Edge on Stealth tests, "
                            f"and a Perception threshold of {racs_r} to detect the wearer (drops by 1 per meter moved past 3m/round)."
                        ),
                        "accessories": [],
                    }
                )
                continue

            m_r = re.search(r"(?:x|R|Rating\s*)(\d+)\s*$", mod_str, re.I)
            r_val = (
                int(m_r.group(1))
                if m_r
                else (int(mod.get("rating", 0)) if isinstance(mod, dict) and "rating" in mod else 0)
            )
            accessories_out.append({"name": mod_str, "rating": r_val})

        social_rating = _parse_int(arm.get("social_rating", arm.get("socialrating", 0)), 0)
        if social_rating == 0:
            combined_armor_text = f"{notes} " + " ".join(a["name"] for a in accessories_out)
            m_soc = re.search(r"([+-]\d+)\s*Social", combined_armor_text, re.IGNORECASE)
            if m_soc:
                social_rating = int(m_soc.group(1))
            elif "très chic" in combined_armor_text.lower():
                m_tc = re.search(r"Très Chic\s*x?(\d+)?", combined_armor_text, re.IGNORECASE)
                social_rating = int(m_tc.group(1)) if (m_tc and m_tc.group(1)) else 1

        is_primary = idx == primary_idx
        is_cumulative = any(k in aname.lower() for k in CUMULATIVE_ARMOR_KEYWORDS)
        is_ignored = not (is_primary or is_cumulative)

        db_row = _lookup_db_row(conn, "ref_gear", arm.get("ref"), aname)
        rule_desc, rule_page = _lookup_rule_text_and_page(conn, aname, chapter_hint="Armor")
        page_str = _format_page(
            arm.get("source") or (db_row or {}).get("source"),
            arm.get("page") or _parse_xml_attr((db_row or {}).get("raw_xml", ""), "page"),
            fallback_page=rule_page,
        )

        armors_list.append(
            {
                "name": aname,
                "rating": arating,
                "socialrating": social_rating,
                "isIgnored": is_ignored,
                "primary": is_primary,
                "page": page_str,
                "description": _combine_descriptions(notes, rule_desc),
                "accessories": accessories_out,
            }
        )

        if is_ignored:
            soc_str = f", Social {social_rating:+d}" if social_rating else ""
            extra_wardrobe_items.append(
                {
                    "name": f"{aname} (Wardrobe - DR +{arating}{soc_str})",
                    "rating": arating,
                    "count": 1,
                    "type": "ARMOR",
                    "subType": "WARDROBE",
                    "page": page_str,
                    "description": notes
                    or f"Alternate outfit (Defense Rating +{arating}{soc_str})",
                    "accessories": [{"name": a["name"]} for a in accessories_out],
                }
            )

    # Append extracted cumulative armor pieces (Ballistic Hood, RACS)
    for c_arm in extracted_cumulative_armors:
        if not any(a["name"].lower() == c_arm["name"].lower() for a in armors_list):
            armors_list.append(c_arm)

    # For Emergent Intelligence characters inhabiting the Shiawase Man-at-Arms, export
    # the Man-At-Arms Base Armor (8) as Primary armor so Core DR calculates 15 + 8 = 23!
    if is_ai and not armors_list:
        armors_list.append(
            {
                "name": "Man-At-Arms Base Armor",
                "rating": 8,
                "socialrating": 0,
                "isIgnored": False,
                "primary": True,
                "page": "Double Clutch p.140",
                "description": (
                    "Shiawase Man-at-Arms Anthropomorphic Drone Chassis Base Armor (Armor 8). "
                    "Combines with Man-at-Arms Body 15 (Base 10 + 5 Increased Structural Integrity) for 23 Physical Defense Rating."
                ),
                "accessories": [],
            }
        )

    # 6 & 7. Items (`json.items`) & Augmentations (`json.augmentations`)
    # Disguise/biotech/medical kits (Nanopaste, Nanocosmetics, Savior Medkit) are routed to
    # `json.augmentations` with `essence: 0.0`, while foci, sensors (Contacts, Earbuds,
    # Subvocal Mic), contracts, and Software Library go to `json.items`.
    items_list: List[Dict[str, Any]] = []
    seen_items = set()
    augmentations_list: List[Dict[str, Any]] = []
    seen_augs = set()

    synergies = char_data.get("synergies") or {}
    if isinstance(synergies, dict):
        for focus in synergies.get("foci") or []:
            if not isinstance(focus, dict):
                continue
            fname = str(focus.get("name") or "").strip()
            if not fname or "oracle" in fname.lower():
                continue
            frating = _parse_int(focus.get("rating", focus.get("force", 1)), 1)
            fnotes = str(
                focus.get("notes") or focus.get("effect") or "Bonded Focus"
            ).strip()
            rule_desc, rule_page = _lookup_rule_text_and_page(
                conn,
                "Resonance Focus" if "resonance" in fname.lower() else "Power Focus",
                chapter_hint="Foci",
            )
            seen_items.add(fname.lower())
            items_list.append(
                {
                    "name": fname,
                    "rating": frating,
                    "count": 1,
                    "type": "RESONANCE" if "resonance" in fname.lower() else "MAGICAL",
                    "subType": "FOCUS",
                    "page": rule_page or ("Hack & Slash p.70" if "resonance" in fname.lower() else "CRB p.147"),
                    "description": _combine_descriptions(fnotes, rule_desc),
                    "accessories": [],
                }
            )

    all_gear_sources = list(char_data.get("gear") or []) + extra_purchases.get("extra_gear", [])
    for g in all_gear_sources:
        if isinstance(g, str):
            g = {"name": g}
        if not isinstance(g, dict):
            continue
        gname = str(g.get("name") or "").strip()
        if not gname:
            continue

        grating_raw = g.get("rating", g.get("capacity", ""))
        grating: Any = (
            int(grating_raw)
            if isinstance(grating_raw, (int, float)) and grating_raw > 0
            else ""
        )
        gcount = _parse_int(g.get("qty", g.get("quantity", g.get("count", 1))), 1)
        gnotes = str(g.get("notes") or g.get("description") or "").strip()

        db_row = _lookup_db_row(conn, "ref_gear", g.get("ref"), gname)
        rule_desc, rule_page = _lookup_rule_text_and_page(conn, gname)
        page_str = _format_page(
            g.get("source") or (db_row or {}).get("source"),
            g.get("page") or _parse_xml_attr((db_row or {}).get("raw_xml", ""), "page"),
            fallback_page=rule_page,
        )
        full_gdesc = _combine_descriptions(
            gnotes or _strip_xml_tags((db_row or {}).get("raw_xml", "")),
            rule_desc,
        )

        # Check if this gear item belongs in Augmentations (Nanopaste, Nanocosmetics, Savior Medkit)
        if any(k in gname.lower() for k in AUGMENTATION_GEAR_KEYWORDS):
            clean_aug_gname = re.sub(r"\s*\((?:Rating|R)\s*\d+\)", "", gname, flags=re.I).strip()
            if clean_aug_gname.lower() not in seen_augs:
                seen_augs.add(clean_aug_gname.lower())
                augmentations_list.append(
                    {
                        "name": clean_aug_gname,
                        "level": grating,
                        "quality": "STANDARD",
                        "essence": 0.0,
                        "page": page_str or "Body Shop",
                        "description": full_gdesc,
                        "accessories": [],
                    }
                )
            continue

        base_gname = gname.split("(")[0].strip().lower()
        if gname.lower() in seen_items or (
            base_gname and any(base_gname == s.split("(")[0].strip().lower() for s in seen_items)
        ):
            continue
        seen_items.add(gname.lower())

        acc_out: List[Dict[str, str]] = []
        for mod in g.get("modifications") or g.get("accessories") or []:
            acc_out.append({"name": _stringify_accessory_item(mod)})

        items_list.append(
            {
                "name": gname,
                "rating": grating,
                "count": gcount,
                "type": str(g.get("category") or (db_row or {}).get("category") or "GEAR"),
                "subType": "",
                "page": page_str,
                "description": full_gdesc,
                "accessories": acc_out,
            }
        )

    # Add consolidated Software Library item to Gear if commlink apps exist
    if extra_purchases.get("commlink_apps"):
        app_names = [a["name"] for a in extra_purchases["commlink_apps"] if a.get("name")]
        if app_names and "software library" not in seen_items:
            seen_items.add("software library")
            items_list.append(
                {
                    "name": "Commlink Software Library",
                    "rating": "",
                    "count": len(app_names),
                    "type": "SOFTWARE",
                    "subType": "APPS",
                    "page": "CRB / Hack & Slash / Smooth Operations",
                    "description": "Installed Commlink Apps & Utilities: " + ", ".join(app_names),
                    "accessories": [{"name": an} for an in app_names],
                }
            )

    for w_item in extra_wardrobe_items:
        if w_item["name"].lower() not in seen_items:
            seen_items.add(w_item["name"].lower())
            items_list.append(w_item)

    # Process standard Cyberware / Bioware Augmentations
    for aug in (char_data.get("augmentations") or []) + (char_data.get("cyberware") or []):
        if not isinstance(aug, dict):
            continue
        aug_name = str(aug.get("name") or "").strip()
        if not aug_name or aug_name.lower() in seen_augs:
            continue
        seen_augs.add(aug_name.lower())
        clean_aug_name = re.sub(r"\s*\((?:Rating|R)\s*\d+\)", "", aug_name, flags=re.I).strip()
        level_raw = aug.get("rating", aug.get("level", ""))
        if not level_raw:
            m_lvl = re.search(r"\((?:Rating|R)\s*(\d+)\)", aug_name, re.I)
            if m_lvl:
                level_raw = int(m_lvl.group(1))
        level_out: Any = (
            int(level_raw) if isinstance(level_raw, (int, float)) and level_raw > 0 else ""
        )

        quality_key = _normalize_aug_quality(aug.get("grade") or aug.get("quality"))
        essence_val = _parse_float(aug.get("essence", aug.get("essence_cost")), 0.0)

        db_row = _lookup_db_row(conn, "ref_cyberware", aug.get("ref"), clean_aug_name)
        rule_desc, rule_page = _lookup_rule_text_and_page(conn, clean_aug_name)
        page_str = _format_page(
            aug.get("source") or (db_row or {}).get("source"),
            aug.get("page") or _parse_xml_attr((db_row or {}).get("raw_xml", ""), "page"),
            fallback_page=rule_page,
        )
        char_aug_desc = str(
            aug.get("notes")
            or aug.get("effect")
            or aug.get("description")
            or _strip_xml_tags((db_row or {}).get("raw_xml", ""))
            or ""
        ).strip()

        acc_out = [
            {"name": _stringify_accessory_item(m)}
            for m in (aug.get("modifications") or aug.get("accessories") or [])
        ]

        augmentations_list.append(
            {
                "name": clean_aug_name,
                "level": level_out,
                "quality": quality_key,
                "essence": essence_val,
                "page": page_str,
                "description": _combine_descriptions(char_aug_desc, rule_desc),
                "accessories": acc_out,
            }
        )

    # 8. Vehicles & Drones (`json.vehicles`, `json.drones`)
    vehicles_list: List[Dict[str, Any]] = []
    drones_list: List[Dict[str, Any]] = []

    def _format_vehicle_or_drone(v: Dict[str, Any], is_drone: bool) -> Dict[str, Any]:
        vname = str(v.get("name") or "Vehicle").strip()
        db_row = _lookup_db_row(conn, "ref_vehicles", v.get("ref"), vname)
        handling_raw = str(v.get("handling") or (db_row or {}).get("handling") or "4/4")
        h_parts = handling_raw.split("/")
        handl_on = int(re.sub(r"\D", "", h_parts[0]) or 4)
        handl_off = int(re.sub(r"\D", "", h_parts[1]) or handl_on) if len(h_parts) > 1 else handl_on

        vtype = "VEHICLES"
        if is_drone:
            sz = str(
                v.get("size") or v.get("category") or (db_row or {}).get("category") or ""
            ).upper()
            if "MICRO" in sz:
                vtype = "DRONE_MICRO"
            elif "MINI" in sz:
                vtype = "DRONE_MINI"
            elif "LARGE" in sz:
                vtype = "DRONE_LARGE"
            elif "MED" in sz:
                vtype = "DRONE_MEDIUM"
            else:
                vtype = "DRONE_SMALL"

        acc_out = [
            {"name": _stringify_accessory_item(m)}
            for m in (v.get("modifications") or v.get("accessories") or [])
        ]
        page_str = _format_page(
            v.get("source") or (db_row or {}).get("source"),
            v.get("page") or "",
        )

        body_val = _parse_int(v.get("body") or (db_row or {}).get("body"), 4)
        armor_val = _parse_int(v.get("armor") or (db_row or {}).get("armor"), 4)
        pilot_val = _parse_int(v.get("pilot"), 2)
        sensor_val = _parse_int(v.get("sensor") or (db_row or {}).get("sensor"), 2)
        desc_str = str(v.get("notes") or v.get("description") or "").strip()

        if is_ai and is_drone:
            if "man-at-arms" in vname.lower():
                # Primary Inhabited Chassis via Override Sprite Power
                vtype = "DRONE_MEDIUM"
                body_val = 10
                armor_val = 8
                pilot_val = 9
                sensor_val = 2
                desc_str = (
                    f"{desc_str}\n"
                    "Primary Inhabited Chassis (Override Sprite Power): Base Pilot 9 (8 Resonance + 1 Designer) +4 Resonance Focus = 13; "
                    "Body 10 +5 Structural Integrity = 15; Sensor 2 +6 (+2 Inc. Sensors, +1 Sensor Upgrade, +2 Enlightened Automaton, +1 Home Device) = 8.\n"
                    "Post-Import: Use JSON={...} string in Notes to set all Autosoft pools and attribute modifiers in a single click."
                ).strip()
            else:
                if "sky commander" in vname.lower() and sensor_val < 4:
                    sensor_val = 4
                desc_str = (
                    f"{desc_str}\n"
                    "Networked Secondary Drone (+1 Sensor from Sensor Upgrade quality). "
                    "Modified Autosoft Pools: Clearsight 11, Evasion 11, Maneuvering 11, Stealth 13 (+2 Sneak-Sneak), Targeting 12 (+1 Smartlink)."
                ).strip()

        return {
            "name": vname,
            "type": vtype,
            "subtype": str(
                v.get("subtype") or v.get("category") or (db_row or {}).get("category") or ""
            ),
            "handlOn": handl_on,
            "handlOff": handl_off,
            "accelOn": _parse_int(
                v.get("accel") or v.get("acceleration") or (db_row or {}).get("accel"), 10
            ),
            "speedIntOn": _parse_int(v.get("speed_interval"), 20),
            "speed": _parse_int(v.get("speed") or (db_row or {}).get("speed"), 100),
            "body": body_val,
            "armor": armor_val,
            "pilot": pilot_val,
            "sensor": sensor_val,
            "seats": _parse_int(v.get("seats") or (db_row or {}).get("seats"), 0),
            "page": page_str,
            "description": desc_str,
            "accessories": acc_out,
        }

    for veh in char_data.get("vehicles") or []:
        if isinstance(veh, dict):
            vehicles_list.append(_format_vehicle_or_drone(veh, False))
    for drn in char_data.get("drones") or []:
        if isinstance(drn, dict):
            dname = str(drn.get("name") or "").lower()
            if is_ai and "man-at-arms" in dname:
                # Place primary inhabited chassis at index 0 of drones_list for top visibility
                formatted_drone = _format_vehicle_or_drone(drn, True)
                formatted_drone["type"] = "DRONE_MEDIUM"
                formatted_drone["subtype"] = "Anthropomorphic Drone"
                drones_list.insert(0, formatted_drone)
            else:
                drones_list.append(_format_vehicle_or_drone(drn, True))

    # 9. SINs, Lifestyles & Licenses (`json.sins`, `json.lifestyles`, `json.licenses`)
    sins_list: List[Dict[str, Any]] = []
    sin_names_set = set()
    raw_to_clean_sin: Dict[str, str] = {}

    for s in char_data.get("sins") or []:
        if isinstance(s, str):
            s = {"name": s, "rating": 1}
        if not isinstance(s, dict):
            continue
        raw_sname = str(s.get("name") or "").strip()
        if not raw_sname:
            continue
        clean_sname = re.sub(r":\s+\(", " (", raw_sname)
        clean_sname = re.sub(r"\s{2,}", " ", clean_sname).strip()
        raw_to_clean_sin[raw_sname] = clean_sname
        if clean_sname in sin_names_set:
            continue
        sin_names_set.add(clean_sname)
        srating = _parse_int(s.get("rating", s.get("quality", 4)), 4)
        sins_list.append(
            {
                "name": clean_sname,
                "quality": srating,
                "description": str(
                    s.get("notes") or s.get("description") or f"Rating {srating} Identity"
                ),
            }
        )

    if not sins_list:
        default_sin_name = f"{street_name} (Primary Identity)"
        sins_list.append(
            {
                "name": default_sin_name,
                "quality": 4,
                "description": "Primary Runner Identity",
            }
        )
        sin_names_set.add(default_sin_name)

    primary_sin_name = sins_list[0]["name"]

    lifestyles_list: List[Dict[str, Any]] = []
    raw_lifestyles = list(char_data.get("lifestyles") or [])
    if not raw_lifestyles and resources.get("lifestyle"):
        raw_lifestyles = [resources["lifestyle"]]
    if not raw_lifestyles:
        raw_lifestyles = [
            {
                "type": "Low",
                "custom_name": "Primary Safehouse / Lifestyle",
                "months_paid": 1,
                "sin": primary_sin_name,
            }
        ]

    for lf in raw_lifestyles:
        if isinstance(lf, str):
            lf = {"type": lf, "months_paid": 1}
        if not isinstance(lf, dict):
            continue
        lf_type = str(lf.get("type") or lf.get("name") or "Middle").strip()
        lf_custom = str(
            lf.get("custom_name") or lf.get("location") or lf.get("notes") or lf_type
        ).strip()
        lf_months = _parse_int(lf.get("months_paid", lf.get("paidMonths", 1)), 1)
        raw_lf_sin = str(lf.get("sin") or primary_sin_name).strip()
        lf_sin = raw_to_clean_sin.get(raw_lf_sin, re.sub(r":\s+\(", " (", raw_lf_sin).strip())
        if lf_sin not in sin_names_set:
            lf_sin = primary_sin_name

        lifestyles_list.append(
            {
                "name": lf_type,
                "customName": lf_custom,
                "paidMonths": lf_months,
                "sin": lf_sin,
            }
        )

    licenses_list: List[Dict[str, Any]] = []
    for lic in char_data.get("licenses") or []:
        if isinstance(lic, str):
            lic = {"name": lic}
        if not isinstance(lic, dict):
            continue
        lic_name = str(lic.get("name") or "").strip()
        if not lic_name:
            continue
        lic_rating = lic.get("rating")
        if (
            lic_rating
            and f"r{lic_rating}" not in lic_name.lower()
            and f"rating {lic_rating}" not in lic_name.lower()
        ):
            lic_display = f"{lic_name} (R{lic_rating})"
        else:
            lic_display = lic_name

        raw_lic_sin = str(lic.get("sin") or primary_sin_name).strip()
        lic_sin = raw_to_clean_sin.get(raw_lic_sin, re.sub(r":\s+\(", " (", raw_lic_sin).strip())
        if lic_sin not in sin_names_set:
            lic_sin = primary_sin_name

        licenses_list.append(
            {
                "name": lic_display,
                "sin": lic_sin,
            }
        )

    # 10. Contacts (`json.contacts`) - Merge chargen contacts + mission contacts
    contacts_list: List[Dict[str, Any]] = []
    raw_contacts = char_data.get("contacts") or []
    if isinstance(raw_contacts, dict):
        contact_iter = list(raw_contacts.values())
    elif isinstance(raw_contacts, list):
        contact_iter = list(raw_contacts)
    else:
        contact_iter = []

    seen_contacts: Dict[str, Dict[str, Any]] = {}
    for c in contact_iter:
        if not isinstance(c, dict):
            continue
        cname = str(c.get("name") or c.get("canonical_name") or "").strip()
        if not cname:
            continue
        seen_contacts[cname.lower()] = dict(c)

    # Merge chargen contacts from `character_build.qmd`, preserving higher C/L ratings
    for cc in chargen_contacts:
        cc_name = str(cc.get("name") or "").strip()
        if not cc_name:
            continue
        key = cc_name.lower()
        if key not in seen_contacts:
            seen_contacts[key] = cc
        else:
            existing = seen_contacts[key]
            existing["connection"] = max(
                _parse_int(existing.get("connection", existing.get("influence", 1)), 1),
                _parse_int(cc.get("connection", 1), 1),
            )
            existing["loyalty"] = max(
                _parse_int(existing.get("loyalty", 1), 1),
                _parse_int(cc.get("loyalty", 1), 1),
            )

    for c in seen_contacts.values():
        cname = str(c.get("name") or c.get("canonical_name") or "").strip()
        favors = _parse_int(c.get("favors"), 0)
        if favors > 0 and "fp)" not in cname.lower():
            cname = f"{cname} ({favors} FP)"

        ctype = str(c.get("archetype") or c.get("type") or c.get("role") or "Contact").strip()
        if c.get("region") and f"({c['region']})" not in ctype:
            ctype = f"{ctype} ({c['region']})"
        loyalty = _parse_int(c.get("loyalty"), 1)
        connection = _parse_int(c.get("connection", c.get("influence", 1)), 1)
        cdesc = str(c.get("notes") or c.get("description") or "").strip()

        contacts_list.append(
            {
                "name": cname,
                "type": ctype,
                "loyalty": loyalty,
                "influence": connection,
                "description": cdesc,
            }
        )

    contacts_list.sort(key=lambda c: str(c.get("name") or "").lower())

    # 11. Weapons (`json.longRangeWeapons` & `json.closeCombatWeapons`)
    ranged_weapons_list: List[Dict[str, Any]] = []
    melee_weapons_list: List[Dict[str, Any]] = []

    raw_weapons = char_data.get("weapons") or []
    ranged_items: List[Dict[str, Any]] = []
    melee_items: List[Dict[str, Any]] = []

    if isinstance(raw_weapons, dict):
        ranged_items.extend(raw_weapons.get("ranged") or [])
        melee_items.extend(raw_weapons.get("melee") or [])
    elif isinstance(raw_weapons, list):
        for w in raw_weapons:
            if not isinstance(w, dict):
                continue
            wcat = str(w.get("category") or w.get("type") or "").lower()
            wskill = str(w.get("skill") or "").lower()
            if any(
                k in wcat or k in wskill
                for k in ("melee", "blade", "club", "unarmed", "close")
            ):
                melee_items.append(w)
            else:
                ranged_items.append(w)

    has_red_fox = any("red fox" in str(rw.get("name", "")).lower() for rw in ranged_items)
    if is_ai and has_red_fox:
        ranged_weapons_list.extend(
            [
                {
                    "name": "Red Fox Array (2x Link-Fired)",
                    "skill": "exotic_weapons",
                    "pool": 20,
                    "damage": "8P",
                    "attackRating": "21/23/21/14/-",
                    "mode": "SS",
                    "ammunition": "30",
                    "page": "FS 44",
                    "description": "Weapon: FS 44. Link Fire: DC 143. Costs 1 major & 1 minor action to fire. 2 Wild Dice.",
                    "wifi": [],
                    "accessories": [{"name": "Smartgun System (Internal)"}, {"name": "Peak-Discharge Laser Battery Clips"}],
                },
                {
                    "name": "Tesla Coil (Straight)",
                    "skill": "exotic_weapons",
                    "pool": 20,
                    "damage": "5S(e)",
                    "attackRating": "10/12*/-/-/-",
                    "mode": "SS",
                    "ammunition": "20",
                    "page": "BS 49",
                    "description": "Weapon: BS 49. Flamethrower rules: SR6 117.",
                    "wifi": [],
                    "accessories": [],
                },
                {
                    "name": "Red Fox (single beam)",
                    "skill": "exotic_weapons",
                    "pool": 20,
                    "damage": "6P",
                    "attackRating": "20/22/20/13/-",
                    "mode": "SS",
                    "ammunition": "30",
                    "page": "FS 44",
                    "description": "Weapon: FS 44. 1 Wild Die.",
                    "wifi": [],
                    "accessories": [{"name": "Smartgun System (Internal)"}],
                },
                {
                    "name": "Tesla Coil (Wobbly)",
                    "skill": "exotic_weapons",
                    "pool": 20,
                    "damage": "4S(e)",
                    "attackRating": "12/14*/-/-/-",
                    "mode": "SS",
                    "ammunition": "20",
                    "page": "BS 49",
                    "description": "Weapon: BS 49. Flamethrower rules: SR6 117. Fires in a cone 20m long, 3m at base (apex angle 8.58). May use wild die.",
                    "wifi": [],
                    "accessories": [],
                },
                {
                    "name": "Tesla Coil (Sweep)",
                    "skill": "exotic_weapons",
                    "pool": 20,
                    "damage": "2S(e)",
                    "attackRating": "14/16*/-/-/-",
                    "mode": "SS",
                    "ammunition": "20",
                    "page": "BS 49",
                    "description": "Weapon: BS 49. Flamethrower rules: SR6 117. Fires in a cone 20m long, 10m at base (apex angle 28.07). May use wild die.",
                    "wifi": [],
                    "accessories": [],
                },
            ]
        )
    else:
        for rw in ranged_items:
            wname = str(rw.get("name") or "Ranged Weapon").strip()
            db_row = _lookup_db_row(conn, "ref_weapons", rw.get("ref"), wname)
            wcat = str(rw.get("category") or (db_row or {}).get("category") or "")
            wskill = _normalize_weapon_skill(rw.get("skill"), wcat, is_melee=False)
            wdmg = str(rw.get("damage") or rw.get("dv") or (db_row or {}).get("damage") or "3P").strip()
            war = _normalize_attack_rating(
                rw.get("attack_rating") or rw.get("ar") or (db_row or {}).get("attack_rating"),
                is_melee=False,
            )
            wmode = str(
                rw.get("modes") or rw.get("mode") or (db_row or {}).get("modes") or "SA"
            ).strip()
            wammo = str(
                rw.get("ammo") or rw.get("ammunition") or (db_row or {}).get("ammo") or "10(c)"
            ).strip()
            page_str = _format_page(
                rw.get("source") or (db_row or {}).get("source"),
                rw.get("page") or "",
            )
            acc_out = [
                {"name": _stringify_accessory_item(m)}
                for m in (rw.get("modifications") or rw.get("accessories") or [])
            ]
            ranged_weapons_list.append(
                {
                    "name": wname,
                    "skill": wskill,
                    "damage": wdmg,
                    "attackRating": war,
                    "mode": wmode,
                    "ammunition": wammo,
                    "page": page_str,
                    "description": str(rw.get("notes") or rw.get("description") or ""),
                    "wifi": [],
                    "accessories": acc_out,
                }
            )

    # If the character has the Channeling metamagic, include `Elemental Attack` as a
    # ranged weapon macro card so the GM gets the full range-band AR & DV display in chat!
    # (Per Street Wyrd p.113, channeling mages do not gain access to Engulf.)
    has_channeling = any(
        "channeling" in str(m.get("name", m) if isinstance(m, dict) else m).lower()
        for m in metamagic_raw
    )
    if has_channeling and not any(
        "elemental attack" in rw["name"].lower() for rw in ranged_weapons_list
    ):
        _, cha_eff = _resolve_attribute_from_block(attrs_block, "mental", "charisma", 6)
        _, agi_eff = _resolve_attribute_from_block(attrs_block, "physical", "agility", 3)
        sorcery_rating = next(
            (s["rating"] for s in skills_list if s["id"] == "sorcery"), 5
        )
        # Base Sorcery + Magic (+ Power Focus + Wise Warrior if present)
        focus_bonus = 3 if any("power focus" in i["name"].lower() for i in items_list) else 0
        ww_bonus = 1 if any("improved ability (sorcery)" in str(ap.get("name", "")).lower() for ap in adept_powers_raw) else 0
        spellcasting_pool = sorcery_rating + magic_eff + focus_bonus + ww_bonus
        # Roll20 computes Ranged Weapon Pool as Agility + Skill (-1 if unskilled) + Mod
        recommended_mod = spellcasting_pool - (agi_eff - 1)
        ar_val = magic_eff + cha_eff
        elem_desc, elem_page = _lookup_rule_text_and_page(conn, "Elemental Attack", chapter_hint="Critter")
        ranged_weapons_list.append(
            {
                "name": "Elemental Attack",
                "skill": "exotic_weapons",
                "damage": f"{magic_eff}P",
                "attackRating": f"{ar_val}/{ar_val}/{ar_val}/-/-",
                "mode": "SS",
                "ammunition": "0",
                "page": elem_page or "CRB p.224 / Street Wyrd p.113",
                "description": _combine_descriptions(
                    f"Channeled Spirit Ranged Attack (DV = Force P Elemental, AP/AR = 2x Force). "
                    f"Post-Import Setup: Set Weapon 'Mod' to +{recommended_mod} so total pool equals {spellcasting_pool}d6.",
                    elem_desc,
                ),
                "wifi": [],
                "accessories": [],
            }
        )

    for mw in melee_items:
        wname = str(mw.get("name") or "Melee Weapon").strip()
        db_row = _lookup_db_row(conn, "ref_weapons", mw.get("ref"), wname)
        wcat = str(mw.get("category") or (db_row or {}).get("category") or "Melee")
        wskill = _normalize_weapon_skill(mw.get("skill"), wcat, is_melee=True)
        wdmg = str(mw.get("damage") or mw.get("dv") or (db_row or {}).get("damage") or "2P").strip()
        war = _normalize_attack_rating(
            mw.get("attack_rating") or mw.get("ar") or (db_row or {}).get("attack_rating"),
            is_melee=True,
        )
        page_str = _format_page(
            mw.get("source") or (db_row or {}).get("source"),
            mw.get("page") or "",
        )
        acc_out = [
            {"name": _stringify_accessory_item(m)}
            for m in (mw.get("modifications") or mw.get("accessories") or [])
        ]
        melee_weapons_list.append(
            {
                "name": wname,
                "skill": wskill,
                "damage": wdmg,
                "attackRating": war,
                "page": page_str,
                "description": str(mw.get("notes") or mw.get("description") or ""),
                "wifi": [],
                "accessories": acc_out,
            }
        )

    if not melee_weapons_list:
        _, str_eff = _resolve_attribute_from_block(attrs_block, "physical", "strength", 2)
        _, rea_eff = _resolve_attribute_from_block(attrs_block, "physical", "reaction", 2)
        melee_weapons_list.append(
            {
                "name": "Unarmed",
                "skill": "close_combat",
                "damage": "2S",
                "attackRating": f"{str_eff + rea_eff}/-/-/-/-",
                "page": "CRB p.109",
                "description": "Unarmed melee attack",
                "wifi": [],
                "accessories": [],
            }
        )

    # 12. Spells (`json.spells`) - Deduplicated + Enriched with full rulebook descriptions
    spells_by_key: Dict[str, Dict[str, Any]] = {}
    for sp in char_data.get("spells") or []:
        if not isinstance(sp, dict):
            continue
        sname = str(sp.get("name") or "").strip()
        if not sname:
            continue
        key = str(sp.get("ref") or sname).strip().lower()
        existing = spells_by_key.get(key)
        if existing is None:
            spells_by_key[key] = sp
        else:
            old_cat = str(existing.get("category") or "General")
            new_cat = str(sp.get("category") or "General")
            if (old_cat == "General" and new_cat != "General") or (
                len(str(sp.get("effect") or sp.get("notes") or ""))
                > len(str(existing.get("effect") or existing.get("notes") or ""))
            ):
                merged = dict(existing)
                merged.update({k: v for k, v in sp.items() if v not in (None, "", "General")})
                spells_by_key[key] = merged

    spells_list: List[Dict[str, Any]] = []
    spell_influences = list(skill_influences.get("sorcery", []))

    for sp in spells_by_key.values():
        sname = str(sp.get("name") or "").strip()
        db_row = _lookup_db_row(conn, "ref_spells", sp.get("ref"), sname)
        raw_xml = (db_row or {}).get("raw_xml", "")
        rule_desc, rule_page = _lookup_rule_text_and_page(conn, sname, chapter_hint="Spell")

        raw_cat = sp.get("category")
        if not raw_cat or str(raw_cat).lower() == "general":
            raw_cat = (db_row or {}).get("category") or "Manipulation"
        cat_out = _normalize_spell_category(raw_cat)

        raw_dur = sp.get("duration") or (db_row or {}).get("duration") or "Sustained"
        dur_out = _normalize_spell_duration(raw_dur)

        feats_out = _extract_spell_features(sp, db_row)
        raw_rng = sp.get("range") or (db_row or {}).get("range") or "LOS"
        rng_out = _normalize_spell_range(raw_rng, is_area=("area" in feats_out))

        raw_type = sp.get("type") or _parse_xml_attr(raw_xml, "type") or "Mana"
        type_out = _normalize_spell_type(raw_type)

        drain_val = _parse_int(sp.get("drain", (db_row or {}).get("drain", 2)), 2)
        page_str = _format_page(
            sp.get("source") or (db_row or {}).get("source"),
            sp.get("page") or _parse_xml_attr(raw_xml, "page"),
            fallback_page=rule_page,
        )
        char_sp_desc = str(
            sp.get("effect")
            or sp.get("notes")
            or sp.get("description")
            or _strip_xml_tags(raw_xml)
            or ""
        ).strip()

        spells_list.append(
            {
                "name": sname,
                "category": cat_out,
                "type": type_out,
                "range": rng_out,
                "duration": dur_out,
                "drain": drain_val,
                "isAlchemistic": bool(sp.get("isAlchemistic", False)),
                "features": feats_out,
                "influencedBy": spell_influences,
                "page": page_str,
                "description": _combine_descriptions(char_sp_desc, rule_desc),
            }
        )

    # 13. Rituals (`json.rituals`)
    rituals_list: List[Dict[str, Any]] = []
    for rit in char_data.get("rituals") or []:
        if not isinstance(rit, dict):
            continue
        rname = str(rit.get("name") or "").strip()
        if not rname:
            continue
        rule_desc, rule_page = _lookup_rule_text_and_page(conn, rname, chapter_hint="Ritual")
        rituals_list.append(
            {
                "name": rname,
                "threshold": _parse_int(rit.get("threshold"), 4),
                "page": _format_page(rit.get("source"), rit.get("page"), fallback_page=rule_page),
                "description": _combine_descriptions(
                    str(rit.get("notes") or rit.get("effect") or rit.get("description") or ""),
                    rule_desc,
                ),
                "features": [str(f) for f in (rit.get("features") or [])],
            }
        )

    # 14. Adept Powers (`json.adeptPowers`) - Enriched with full rulebook descriptions
    adept_powers_list: List[Dict[str, Any]] = []
    for ap in adept_powers_raw:
        if not isinstance(ap, dict):
            continue
        ap_name = str(ap.get("name") or "").strip()
        if not ap_name:
            continue
        clean_ap_name = re.sub(r"\s+\d+$", "", ap_name).strip()
        db_row = _lookup_db_row(conn, "ref_adept_powers", ap.get("ref"), clean_ap_name)
        raw_xml = (db_row or {}).get("raw_xml", "")
        rule_desc, rule_page = _lookup_rule_text_and_page(conn, clean_ap_name, chapter_hint="Adept")

        lvl_raw = ap.get("rating", ap.get("level", ""))
        if not lvl_raw:
            m_end = re.search(r"\s+(\d+)$", ap_name)
            if m_end:
                lvl_raw = int(m_end.group(1))
        lvl_out: Any = int(lvl_raw) if isinstance(lvl_raw, (int, float)) and lvl_raw > 0 else ""

        cost_val = _parse_float(
            ap.get("cost_pp", ap.get("cost", (db_row or {}).get("cost", 0.5))), 0.0
        )
        act_key = _normalize_adept_activation(ap.get("action") or ap.get("activation"), raw_xml)
        page_str = _format_page(
            ap.get("source") or (db_row or {}).get("source"),
            ap.get("page") or _parse_xml_attr(raw_xml, "page"),
            fallback_page=rule_page,
        )
        char_ap_desc = str(
            ap.get("effect")
            or ap.get("notes")
            or ap.get("description")
            or _strip_xml_tags(raw_xml)
            or ""
        ).strip()

        adept_powers_list.append(
            {
                "name": clean_ap_name,
                "level": lvl_out,
                "cost": cost_val,
                "activation": act_key,
                "page": page_str,
                "description": _combine_descriptions(char_ap_desc, rule_desc),
            }
        )

    # 15. Metamagic & Echoes (`json.metamagic`, `json.echoes`) - Enriched with rulebook text
    metamagic_list: List[Dict[str, Any]] = []
    seen_mm = set()
    for mm in metamagic_raw:
        if isinstance(mm, str):
            mm = {"name": mm}
        if not isinstance(mm, dict):
            continue
        mm_name = str(mm.get("name") or "").strip()
        if not mm_name or mm_name.lower() in seen_mm:
            continue
        seen_mm.add(mm_name.lower())
        rule_desc, rule_page = _lookup_rule_text_and_page(conn, mm_name)
        metamagic_list.append(
            {
                "name": mm_name,
                "page": _format_page(
                    mm.get("source"), mm.get("page"), fallback_page=rule_page or "CRB / Street Wyrd"
                ),
                "description": _combine_descriptions(
                    str(mm.get("effect") or mm.get("notes") or mm.get("description") or ""),
                    rule_desc,
                ),
            }
        )

    echoes_list: List[Dict[str, Any]] = []
    seen_echoes = set()
    for ec in echoes_raw:
        if isinstance(ec, str):
            ec = {"name": ec}
        if not isinstance(ec, dict):
            continue
        ec_name = str(ec.get("name") or "").strip()
        if not ec_name or ec_name.lower() in seen_echoes:
            continue
        seen_echoes.add(ec_name.lower())
        rule_desc, rule_page = _lookup_rule_text_and_page(conn, ec_name)
        echoes_list.append(
            {
                "name": ec_name,
                "page": _format_page(ec.get("source"), ec.get("page"), fallback_page=rule_page or "CRB"),
                "description": _combine_descriptions(
                    str(ec.get("effect") or ec.get("notes") or ec.get("description") or ""),
                    rule_desc,
                ),
            }
        )

    # 16. Complex Forms (`json.complexForms`) - Includes Complex Forms & Symbiosed Sprite Powers
    complex_forms_list: List[Dict[str, Any]] = []
    seen_cfs = set()
    for cf in char_data.get("complex_forms") or []:
        if not isinstance(cf, dict):
            continue
        cf_name = str(cf.get("name") or "").strip()
        if not cf_name or cf_name.lower() in seen_cfs:
            continue
        seen_cfs.add(cf_name.lower())
        db_row = _lookup_db_row(conn, "ref_complex_forms", cf.get("ref"), cf_name)
        raw_xml = (db_row or {}).get("raw_xml", "")
        rule_desc, rule_page = _lookup_rule_text_and_page(conn, cf_name)
        canon_cf = CANONICAL_COMPLEX_FORMS.get(cf_name.lower()) or {}
        dur_out = _normalize_cf_duration(canon_cf.get("duration") or cf.get("duration") or (db_row or {}).get("duration"))
        fading_val = canon_cf.get("fading") if "fading" in canon_cf else _parse_int(cf.get("fading", cf.get("fade", (db_row or {}).get("fade", 2))), 2)
        page_str = canon_cf.get("page") or _format_page(
            cf.get("source") or (db_row or {}).get("source"),
            cf.get("page") or _parse_xml_attr(raw_xml, "page"),
            fallback_page=rule_page,
        )
        char_cf_desc = str(
            cf.get("effect")
            or cf.get("notes")
            or cf.get("description")
            or _strip_xml_tags(raw_xml)
            or ""
        ).strip()

        cf_infs = [str(x) for x in (cf.get("influences") or [])]
        if is_ai:
            if cf_name.lower() == "cyber spike":
                cf_infs.extend(
                    [
                        "Resonance Focus R4 (+4d6)",
                        "Electronics: Complex Forms Spec (+2d6)",
                        "Taz Sprite Symbiosis (+4d6)",
                    ]
                )
                char_cf_desc = (
                    f"{char_cf_desc}\n"
                    "[Electronics test vs Body + Essence. Total Pool: 23d6 = Electronics 5 + Complex Forms Spec 2 + Resonance 8 + Focus 4 + Taz 4. ECM Warrior II does not apply (Electronics test, not Cracking); Cybercombat spec not possessed.]"
                ).strip()
            elif cf_name.lower() == "resonance spike":
                cf_infs.extend(
                    [
                        "Resonance Focus R4 (+4d6)",
                        "Taz Sprite Symbiosis (+4d6)",
                        "ECM Warrior II TacApp (+2d6 Offensive Cracking)",
                    ]
                )
                char_cf_desc = (
                    f"{char_cf_desc}\n"
                    "[Cracking test vs Willpower + Firewall. Total Pool: 23d6 = Cracking 5 + Resonance 8 + Focus 4 + Taz 4 + ECM Warrior II 2. Cybercombat spec not possessed.]"
                ).strip()
            else:
                cf_infs.extend(
                    [
                        "Resonance Focus R4 (+4d6)",
                        "Electronics: Complex Forms Spec (+2d6)",
                        "Taz Sprite Symbiosis (+4d6)",
                    ]
                )

        complex_forms_list.append(
            {
                "name": cf_name,
                "duration": dur_out,
                "fading": fading_val,
                "page": page_str,
                "description": _combine_descriptions(char_cf_desc, rule_desc),
                "influences": cf_infs,
            }
        )

    # Also export Symbiosed Sprite Powers into `json.complexForms` for AI / Sprite Symbiosis characters
    for sp_pow in char_data.get("sprite_powers") or []:
        if not isinstance(sp_pow, dict):
            continue
        sp_name = str(sp_pow.get("name") or "").strip()
        if not sp_name:
            continue
        display_sp_name = sp_name if "sprite power" in sp_name.lower() else f"Sprite Power: {sp_name}"
        if display_sp_name.lower() in seen_cfs:
            continue
        seen_cfs.add(display_sp_name.lower())
        sp_dur = _normalize_cf_duration(sp_pow.get("duration") or "Sustained")
        sp_desc = " | ".join(
            str(x).strip()
            for x in (
                sp_pow.get("category"),
                sp_pow.get("action") and f"Action: {sp_pow.get('action')}",
                sp_pow.get("test") and f"Test: {sp_pow.get('test')}",
                sp_pow.get("effect"),
                sp_pow.get("notes"),
            )
            if x and str(x).strip()
        )
        sp_infs = ["Sprite Symbiosis (Taz — Companion Sprite R6)"]
        if is_ai and "death mark" in sp_name.lower():
            sp_infs.extend(
                [
                    "Resonance Focus R4 (+4d6)",
                    "ECM Warrior II TacApp (+2d6 Offensive Cracking)",
                ]
            )
            sp_desc = (
                f"{sp_desc} | "
                "[Offensive Cracking test vs Intuition + Firewall. Total Pool: 23d6 = Cracking 5 + Resonance 8 + Focus 4 + Taz 4 + ECM Warrior II 2.]"
            ).strip()

        complex_forms_list.append(
            {
                "name": display_sp_name,
                "duration": sp_dur,
                "fading": 0,
                "page": _format_page(sp_pow.get("source") or "Hack & Slash", sp_pow.get("page") or "65"),
                "description": sp_desc,
                "influences": sp_infs,
            }
        )

    # 17. Martial Arts (`json.martialArts`)
    martial_arts_list: List[Dict[str, Any]] = []
    for ma in char_data.get("martial_arts") or []:
        if not isinstance(ma, dict):
            continue
        ma_name = str(ma.get("name") or "").strip()
        if not ma_name:
            continue
        martial_arts_list.append(
            {
                "name": ma_name,
                "page": _format_page(ma.get("source"), ma.get("page")),
                "description": str(ma.get("notes") or ma.get("description") or ""),
                "techniques": [str(t) for t in (ma.get("techniques") or [])],
            }
        )

    # 18. Matrix Devices & Programs (`json.matrixItems`)
    matrix_items_list: List[Dict[str, Any]] = []
    seen_matrix_devices = set()

    programs_out: List[Dict[str, str]] = []
    seen_programs = set()

    for prog in (
        (char_data.get("programs") or [])
        + (char_data.get("commlink_apps") or [])
        + extra_purchases.get("programs", [])
        + extra_purchases.get("commlink_apps", [])
    ):
        if isinstance(prog, str):
            prog = {"name": prog}
        if not isinstance(prog, dict):
            continue
        pname = str(prog.get("name") or "").strip()
        if not pname or pname.lower() in seen_programs:
            continue
        seen_programs.add(pname.lower())
        db_row = _lookup_db_row(conn, "ref_programs", prog.get("ref"), pname)
        raw_xml = (db_row or {}).get("raw_xml", "")
        rule_desc, rule_page = _lookup_rule_text_and_page(conn, pname)
        programs_out.append(
            {
                "name": pname,
                "page": _format_page(
                    prog.get("source") or (db_row or {}).get("source"),
                    prog.get("page") or _parse_xml_attr(raw_xml, "page"),
                    fallback_page=rule_page,
                ),
                "description": _combine_descriptions(
                    str(
                        prog.get("description")
                        or prog.get("notes")
                        or _strip_xml_tags(raw_xml)
                        or ""
                    ).strip(),
                    rule_desc,
                ),
            }
        )

    raw_matrix_devices = list(char_data.get("matrix_devices") or char_data.get("matrixItems") or [])
    raw_matrix_devices.extend(extra_purchases.get("matrix_devices", []))

    if is_ai:
        ai_matrix_devices = [
            {
                "name": "Living Persona (r31-K0 / Pilot AI)",
                "deviceRating": res_eff or 8,
                "subType": "CYBERDECK",
                "concurrentPrograms": res_eff or 8,
                "attack": 7,
                "sleaze": 9,
                "dataProcessing": 7,
                "firewall": 9,
                "source": "CRB / Hack & Slash",
                "page": "116",
                "description": (
                    "Emergent Intelligence Living Persona: Base ASDF 3/5/3/5 increased by +4 augmented cap "
                    "(Taz Sprite Symbiosis +6, Toolbox +1, Encryption +1) to 7/9/7/9. "
                    "Matrix AR 16 (Attack 7 + Sleaze 9), Matrix DR 16 (DP 7 + FW 9, treated as 20 DR via Designer Home Device)."
                ),
                "accessories": [
                    {"name": "Resonance Focus (Bonded)", "rating": 4},
                    {"name": "Software Emulator Echo", "rating": 8},
                ],
            },
            {
                "name": "M-TOC Mark II",
                "deviceRating": 6,
                "subType": "TAC_NET",
                "concurrentPrograms": 4,
                "attack": 0,
                "sleaze": 0,
                "dataProcessing": 6,
                "firewall": 6,
                "source": "Firing Squad",
                "page": "68",
                "description": (
                    "Mobile Tactical Operations Center Mark II (slaved in Sky Commander Integrated Matrix Dock). "
                    "Stores 5 Edge, -2 Ambush threshold, runs 4 active TacApps: ECM Warrior II (+2 offensive Cracking, -2 Noise), "
                    "Sneak-Sneak (+2 Stealth TW), Target Artist (shared LOS; -1 cover; ignore blind fire), Artillery Barrage (+1 Launcher). "
                    "[In Library: Mobile Medic]."
                ),
                "accessories": [
                    {"name": "ECM Warrior II (Active TacApp)", "rating": 0},
                    {"name": "Sneak-Sneak (Active TacApp)", "rating": 0},
                    {"name": "Target Artist (Active TacApp)", "rating": 0},
                    {"name": "Artillery Barrage (Active TacApp)", "rating": 0},
                    {"name": "Mobile Medic (Library TacApp)", "rating": 0},
                ],
            },
            {
                "name": "Essy Motors DroneMaster",
                "deviceRating": 3,
                "subType": "RIGGER_CONSOLE",
                "concurrentPrograms": 3,
                "attack": 0,
                "sleaze": 0,
                "dataProcessing": 4,
                "firewall": 4,
                "source": "CRB",
                "page": "269",
                "description": "Rigger Command Console (Noise Reduction 3, Sharing 3) used for secondary drone autosoft slaving and Swarm operations.",
                "accessories": [],
            },
            {
                "name": "The Holy Wild Sanctuary Host (~)",
                "deviceRating": 2,
                "subType": "CYBERDECK",
                "concurrentPrograms": 2,
                "attack": 2,
                "sleaze": 3,
                "dataProcessing": 4,
                "firewall": 5,
                "source": "Hack & Slash",
                "page": "125",
                "description": (
                    "Rating 2 Mobile Sanctuary Host integrated into the Federated-Boeing Sky Commander. "
                    "Houses dormant Data Structure: Oracle (Rating 4) in its optical cluster substrate "
                    "(inactive on character sheet while Resonance Focus R4 is active, per SRM single Data Structure rule for EIs)."
                ),
                "accessories": [
                    {"name": "Data Structure: Oracle (Dormant / Inactive)", "rating": 4},
                ],
            },
        ]
        raw_matrix_devices = ai_matrix_devices + raw_matrix_devices

    for idx, dev in enumerate(raw_matrix_devices):
        if not isinstance(dev, dict):
            continue
        dname = str(dev.get("name") or "").strip()
        if not dname or dname.lower() in seen_matrix_devices:
            continue
        seen_matrix_devices.add(dname.lower())

        dr = _parse_int(dev.get("deviceRating", dev.get("device_rating", dev.get("rating", 3))), 3)
        subtype = str(dev.get("subType") or dev.get("type") or "COMMLINK").upper()
        if subtype not in (
            "COMMLINK",
            "CYBERDECK",
            "CYBER_HEADWARE",
            "RIGGER_CONSOLE",
            "CONTROL_RIG",
            "TAC_NET",
        ):
            subtype = "COMMLINK"

        default_dp = max(1, dr // 2)
        default_fw = max(1, dr // 2)
        if "erika elite" in dname.lower():
            default_dp, default_fw = 2, 1
        elif "renraku sensei" in dname.lower():
            default_dp, default_fw = 2, 0
        elif "hermes ikon" in dname.lower():
            default_dp, default_fw = 3, 0
        elif "transys avalon" in dname.lower():
            default_dp, default_fw = 3, 1
        elif "fairlight excalibur" in dname.lower():
            default_dp, default_fw = 3, 2

        atk = _parse_int(dev.get("attack"), 0)
        slz = _parse_int(dev.get("sleaze"), 0)
        dp = _parse_int(dev.get("dataProcessing", dev.get("data_processing")), default_dp)
        fw = _parse_int(dev.get("firewall"), default_fw)
        prog_slots = _parse_int(dev.get("concurrentPrograms", dev.get("programs_max")), dr)

        matrix_items_list.append(
            {
                "name": dname,
                "deviceRating": dr,
                "subType": subtype,
                "concurrentPrograms": prog_slots,
                "attack": atk,
                "sleaze": slz,
                "dataProcessing": dp,
                "firewall": fw,
                "page": _format_page(dev.get("source") or "CRB", dev.get("page")),
                "description": str(dev.get("description") or dev.get("notes") or ""),
                "accessories": [
                    {
                        "name": str(a.get("name", a) if isinstance(a, dict) else a),
                        "rating": _parse_int(a.get("rating", 0) if isinstance(a, dict) else 0, 0),
                    }
                    for a in (dev.get("accessories") or [])
                ],
                "programs": programs_out if idx == 0 else [],
            }
        )

    if conn is not None:
        conn.close()

    return {
        "name": birth_name,
        "streetName": street_name,
        "metaType": metatype,
        "age": age,
        "gender": gender,
        "size": size,
        "weight": weight,
        "karma": total_karma,
        "freeKarma": free_karma,
        "nuyen": nuyen,
        "initiation": initiation,
        "submersion": submersion,
        "heat": heat,
        "reputation": reputation,
        "notes": player_notes,
        "attributes": attributes_list,
        "qualities": qualities_list,
        "skills": skills_list,
        "armors": armors_list,
        "items": items_list,
        "augmentations": augmentations_list,
        "vehicles": vehicles_list,
        "drones": drones_list,
        "sins": sins_list,
        "lifestyles": lifestyles_list,
        "licenses": licenses_list,
        "contacts": contacts_list,
        "longRangeWeapons": ranged_weapons_list,
        "closeCombatWeapons": melee_weapons_list,
        "spells": spells_list,
        "rituals": rituals_list,
        "adeptPowers": adept_powers_list,
        "metamagic": rituals_list if False else metamagic_list,
        "echoes": echoes_list,
        "complexForms": complex_forms_list,
        "martialArts": martial_arts_list,
        "matrixItems": matrix_items_list,
    }


def generate_roll20_helper_guide(
    char_data: Dict[str, Any],
    payload: Dict[str, Any],
) -> str:
    """
    Generate a companion Markdown cheat sheet with ready-to-paste Roll20 Effects
    (`repeating_effects` Modifications strings), post-import setup steps, and
    custom Roll20 chat macros for the character.
    """
    street_name = payload.get("streetName", "Runner")
    attr_map = {a["id"]: a["modifiedValue"] for a in payload.get("attributes", [])}
    agi = attr_map.get("AGILITY", 3)
    magic = attr_map.get("MAGIC", 0)
    resonance = attr_map.get("RESONANCE", 0)

    lines = [
        f"# Roll20 Setup, Effects & Macros Guide — {street_name}",
        "",
        "## 1. Pre-Import & Post-Import Quick Checklist",
        "1. **Automatic Clean on Re-Import (`clean()`)**: Roll20's importer (`doImport`) automatically calls `clean()` (`lines 14690–14698`), wiping and replacing all 20 repeating sections (`quality`, `skills`, `knowledges`, `armor`, `items`, `augmentations`, `vehicle`, `lifestyle`, `contacts`, `range`, `melee`, `spell`, `ritual`, `powers`, `metamagic`, `echoes`, `forms`, `martial`, `devices`, `programs`) while **preserving `repeating_effects`**! That means your custom Effects in `Attributes -> Effects` survive re-imports.",
        "2. **Enable Modifiers (Options Tab)**: On the **Options** tab (gear icon), check **`Enable Modifiers`** so toggleable items in the `Attributes -> Effects` sub-tab automatically update your attributes and derived pools. *(Note: if you manually typed `+3` into an attribute's `Mod` box before creating an Effect for it, zero out the manual `Mod` box first so the Effect doesn't stack `+3 + +3 = +6`.)*",
    ]

    if magic > 0:
        lines.extend(
            [
                "3. **Select Tradition (Magic Tab)**: On the **Magic** tab, select **`Shamanism (Charisma)`** from the Tradition dropdown so Roll20 computes Magic Attack Rating (`Charisma + Magic`) and Drain Resistance (`Willpower + Charisma`).",
                "4. **Elemental Attack (Core / Arms Tab)**:",
            ]
        )
        sorcery_sk = next((s["rating"] for s in payload.get("skills", []) if s["id"] == "sorcery"), 5)
        focus_b = 3 if any("power focus" in i["name"].lower() for i in payload.get("items", [])) else 0
        ww_b = 1 if any("improved ability (sorcery)" in ap["name"].lower() for ap in payload.get("adeptPowers", [])) else 0
        base_sc_pool = sorcery_sk + magic + focus_b + ww_b
        # Unskilled exotic_weapons = Agility - 1
        unbuffed_mod = base_sc_pool - (agi - 1)
        lines.extend(
            [
                f"   - Check **Primary** next to **`Elemental Attack`** on the Arms tab so it appears on your Core tab.",
                f"   - Because Roll20's weapon macro rolls `Agility + Exotic Weapons (-1 unskilled) + Mod`, set the weapon's **`Mod`** field to **`+{unbuffed_mod}`** (or **`+{unbuffed_mod - 2}`** while Channeled `Agility +2` is active) so the macro rolls your exact **{base_sc_pool}d6** Spellcasting pool.",
            ]
        )

    if resonance > 0:
        lines.extend(
            [
                "3. **Select Technomancer Stream (Matrix Tab)**: On the **Matrix** tab, select **`Technoshamans (Charisma)`** so Fade Resistance rolls `Willpower + Charisma` (`6 + 4 = 10d6`).",
                "",
                "---",
                "",
                "## 2. Post-Flight Adjustments (The 4 Post-Import Steps)",
                "",
                "Every time you re-import `reiko_roll20.json`, Roll20's `clean()` wipes repeating rows and restores default values. Follow these 4 quick adjustments to finalize the sheet for tabletop play:",
                "",
                "### 1) Drone Autosofts (`Vehicles` Tab)",
                "- **Base Autosofts**: Set each autosoft rating to **`11`** (Rating 7 + 4 Sprite Symbiosis teamwork):",
                "  - **Clearsight**: `11` (click power toggle ON)",
                "  - **Evasion**: `11` (click power toggle ON)",
                "  - **Maneuvering**: `11` (click power toggle ON)",
                "  - **Electronic Warfare**: `11` (click power toggle ON, if present)",
                "- **Stealth**: Set to **`13`** (`11` base + `2` from Sneak-Sneak TacApp on M-TOC Mark II; click power toggle ON).",
                "- **Targeting**: Set to **`12`** (`11` base + `1` Smartlinked weapons; click power toggle ON).",
                "- **Shiawase Man-at-Arms (Overridden Drone Body)**:",
                "  - **Pilot Mod**: `+4` (Resonance Focus R4 -> Pilot 13)",
                "  - **Body Mod**: `+5` (Reinforced Frame -> Body 15)",
                "  - **Sensor Mod**: `+6` (Base 2 + 2 Improved Sensors + 1 Sensor Upgrade + 1 Designer Home Device -> Sensor 8)",
                "- **Secondary Drones** (`Sky Commander`, `MCT Gnat`, `MCT Hornet`, `Dream Genie`, `Utility-One`):",
                "  - **Sensor Mod**: `+1` (Sensor Upgrade quality)",
                "  - Autosofts: `11` base, `13` stealth, `12` targeting (all powered ON)",
                "",
                "### 2) Weapon Pools to Reflect Targeting Pool (`Arms` & `Core` Tabs)",
                "The 5 Man-at-Arms weapons are exported using skill **`Exotic Weapons`** so your new `Engineering (Drones)` skill doesn't inflate your weapon pools. Here is the math for the **20d6** target pool:",
                "- **Starting Pool**: `Agility (7) + Exotic Weapons (-1 unskilled) = 6`.",
                "- **Drone Targeting Pool**: `Targeting Autosoft (12) + Man-at-Arms Sensor (8) = 20`.",
                "- **Modifier to Add**: `20 - 6 = +14`.",
                "*(Note: If you ever revert weapons to `Engineering`, the starting pool is `Logic 12 - 1 = 11`, which needed `+9` to reach 20. With `Exotic Weapons`, you add `+14`.)*",
                "",
                "- Click the settings toggle (`x`) on each of the 5 weapons:",
                "  1. **Red Fox Array (2x Link-Fired)**: Set **Modifier** to **`+14`** (Pool = **20d6**, 8P DV, 2 Wild Dice, AR 21/23/21/14/-).",
                "  2. **Single Red Fox (Eye Mount)**: Set **Modifier** to **`+14`** (Pool = **20d6**, 6P DV, 1 Wild Die, AR 20/22/20/13/-).",
                "  3. **Tesla Coil (Straight Line)**: Set **Modifier** to **`+14`** (Pool = **20d6**, 5S(e) DV, AR 10/12/-/-/-).",
                "  4. **Tesla Coil (Wobbly Cone)**: Set **Modifier** to **`+14`** (Pool = **20d6**, 4S(e) DV, Cone 20m x 3m base, Apex 8.58°).",
                "  5. **Tesla Coil (Sweep Cone)**: Set **Modifier** to **`+14`** (Pool = **20d6**, 2S(e) DV, Cone 20m x 10m base, Apex 28.07°).",
                "  *(Note: If rolling unassisted drone targeting without sensor pairing, set Pool to `12`.)*",
                "",
                "",
                "### 3) Complex Form Rolls (`Matrix` Tab)",
                "Roll20's importer omits setting skill attributes on Complex Forms, leaving them at 'No Roll'. Open settings (`x`) on each form:",
                "- **Electronics Forms** (`Puppeteer`, `Cleaner`, `Diffusion of Firewall`, `Technoregeneration`, `Resonance Wires`, `Enlighten Automaton`, `Cyber Spike`):",
                "  - **Skill**: Select **`Electronics`**",
                "  - **Specialization**: Check box (**`+2`**)",
                "  - **Modifier**: Set to **`+7`** (Focus +4 + Taz Symbiosis +3) to roll full **`23d6`** pool (or leave blank to roll base 16d6).",
                "- **Resonance Spike** (`Cracking`):",
                "  - **Skill**: Select **`Cracking`**",
                "  - **Specialization**: Check box (**`+2`**)",
                "  - **Modifier**: Set to **`+7`** (Focus +4 + Taz Symbiosis + ECM Warrior II) to roll full **`23d6`** pool.",
                "",
                "### 4) Add Sprite Symbiosis & TacApp Modifiers to Skills (`Core` & `Skills` Tabs)",
                "Because Natural Hacker (*Hack & Slash* p. 83) strictly replaces Logic and Intuition on *Matrix actions*, meatspace skills (Engineering, Biotech, Navigation) cannot use your inflated Matrix attributes (Logic 12, Intuition 12). Instead, they roll with your real meatspace attributes (Logic 4, Intuition 2).",
                "",
                "To counteract the +8 Logic and +10 Intuition bonuses provided by the Natural Hacker Effect in Roll20, apply the following compensating modifiers on the **Skills** tab (click settings `x` on each skill):",
                "",
                "- **Matrix Skills** (Natural Hacker Resonance 12 applies):",
                "  - **Cracking**: Set Modifier to **`+4`** (Taz Teamwork -> Pool **21d6**, or **23d6** with Hacking Spec).",
                "  - **Electronics**: Set Modifier to **`+4`** (Taz Teamwork -> Pool **21d6**, or **23d6** with Software/Complex Forms Spec).",
                "  - **Tasking**: Set Modifier to **`+4`** (Taz Teamwork -> Pool **22d6**, or **24d6** with Registering/Compiling Spec).",
                "- **Meatspace Emulated Skills** (Compensate for Natural Hacker +8 LOG / +10 INT):",
                "  - **Engineering (Drones)**: Set Modifier to **`-4`** (Real Logic 4 + Rating 5 + Drones Spec 2 + Taz Teamwork 4 = **15d6** Pool. Roll20 calculates 12 + 5 + 2 = 19; `19 - 4 = 15d6`).",
                "  - **Biotech**: Set Modifier to **`-4`** (Real Logic 4 + Rating 7 + Mobile Medic 4 = **15d6** Pool. Roll20 calculates 12 + 7 = 19; `19 - 4 = 15d6`).",
                "  - **Outdoors (Navigation)**: Set Modifier to **`-10`** (Real Intuition 2 + Rating 5 + Navigation Spec 2 = **9d6** Pool. Roll20 calculates 12 + 5 + 2 = 19; `19 - 10 = 9d6`).",
            ]
        )
    lines.extend(
        [
            "",
            "---",
            "",
            "## 3. One-Time Setup: Copy-Paste Effects (`Core Tab -> Attributes -> Effects`)",
            "",
            "> **Why Skill Modifiers (`cracking`, `electronics`) Are Handled Via Macros Rather Than Effects**:",
            "> Roll20's `repeating_effects` sheet worker only supports attributes and derived pools in `allowed_modifiers` (`logic_modifier`, `attack_modifier`, `fade_compiling_modifier`, etc.). Active skill ratings (`attr_cracking`, `attr_electronics`) are managed by a separate worker (`update_skill_ratings`) that overwrites hidden skill attributes upon any change. To ensure your +4d6 Taz teamwork and +2d6 ECM Warrior II bonuses always roll reliably without desyncing, they are pre-calculated into the dedicated chat macros in Section 3 below.",
            "",
        ]
    )

    if magic > 0:
        lines.extend(
            [
                "### Effect 1: Channeled Spirit (Force 4+)",
                "- **Name**: `Channeled Spirit (F4+)`",
                "- **Duration**: `Sustained / Services`",
                "- **Source**: `Channeling Metamagic`",
                "- **Modifications** *(copy-paste as a single line)*:",
                "```text",
                "body_modifier: +2, agility_modifier: +2, reaction_modifier: +2, strength_modifier: +2",
                "```",
                "",
                "### Effect 2: Sustained Increase Attribute (Willpower & Charisma +4)",
                "- **Name**: `Increase Attribute (WIL +4, CHA +4)`",
                "- **Duration**: `Sustained (Focused Concentration R3)`",
                "- **Source**: `Spellcasting`",
                "- **Modifications** *(copy-paste as a single line)*:",
                "```text",
                "willpower_modifier: +4, charisma_modifier: +4",
                "```",
                "",
                "### Effect 3: Power Focus (Rating 3)",
                "- **Name**: `Power Focus (Rating 3)`",
                "- **Duration**: `Active (Bonded)`",
                "- **Source**: `Focus`",
                "- **Modifications** *(copy-paste as a single line)*:",
                "```text",
                "magic_modifier: +3",
                "```",
                "",
                "### Effect 4: Increase Reflexes (+2 REA, +2d6 Initiative)",
                "- **Name**: `Increase Reflexes`",
                "- **Duration**: `Sustained`",
                "- **Source**: `Spellcasting`",
                "- **Modifications** *(copy-paste as a single line)*:",
                "```text",
                "reaction_modifier: +2, initiative_dice_mod: +2",
                "```",
            ]
        )

    if resonance > 0:
        lines.extend(
            [
                "### Effect 1: Natural Hacker + Resonance Focus (R4) + Living Persona (`7/9/7/9`) — *With Initiative Fix!*",
                "- **Name**: `Natural Hacker + Resonance Focus R4 + Living Persona 7/9/7/9`",
                "- **Duration**: `Permanent / Bonded`",
                "- **Source**: `Natural Hacker + Resonance Focus R4 + Taz Symbiosis`",
                "- **Why this solves the Initiative & ASDF headaches**:",
                "  1. Raises `Resonance` (`8 + 4 = 12`), `Logic` (`4 + 8 = 12`), and `Intuition` (`2 + 10 = 12`) so all `Cracking`, `Electronics`, and `Tasking` rolls use `12`.",
                "  2. Cancels out the `+10` Intuition inflation on **all 4 Initiative buttons** (`initiative_mod: -10`, `matrix_initiative_mod: -10`, `cold_sim_initiative_mod: -10`, `hot_sim_initiative_mod: -10`, plus `hot_sim_initiative_dice_mod: +1` for Overclocking) so you **never have to disable this Effect before rolling Initiative** (`Physical = 11 + 1d6`, `Matrix AR = 9 + 2d6`, `Cold-Sim = 9 + 3d6`, `Hot-Sim = 9 + 5d6`)!",
                "  3. Compensates for `techno_update()` so your Living Persona ASDF stays locked at **`Attack 7, Sleaze 9, Data Processing 7, Firewall 9`** (`Matrix AR 16`, `Matrix DR 16`).",
                "  4. Adds `fade_compiling_modifier: +8` (`+4` Resonance Focus + `+4` Taz Symbiosis on Compiling/Registering) and `sprite_resist_dv_modifier: +1` (`Technoshamans` stream).",
                "- **Modifications** *(copy-paste as a single line)*:",
                "```text",
                "resonance_modifier: +4, logic_modifier: +8, intuition_modifier: +10, attack_modifier: +3, sleaze_modifier: -3, data_processing_modifier: -5, firewall_modifier: +3, initiative_mod: -10, matrix_initiative_mod: -10, cold_sim_initiative_mod: -10, hot_sim_initiative_mod: -10, hot_sim_initiative_dice_mod: +1, judge_intentions_modifier: -10, memory_modifier: -8, fade_compiling_modifier: +8, sprite_resist_dv_modifier: +1",
                "```",
            ]
        )

    c_ref = street_name
    lines.extend(
        [
            "",
            "---",
            "",
            f"## 4. Permanent Alternative: Character Sheet Abilities (`Attributes & Abilities` Tab)",
            "",
            f"> **Why did \"No character was found for any of the attributes\" happen?**",
            f"> When you paste a macro into Roll20's global **Collections -> Macros** tab and click \"Test Macro\", Roll20 checks the attribute against the exact character name in your Journal (`@{{{c_ref}|...}}`). If your character sheet in Roll20 is named `Reiko` rather than `{c_ref}`, Roll20 cannot find the character!",
            f">",
            f"> **The Best Solution: Character Sheet Abilities (`Attributes & Abilities` Tab)**:",
            f"> Open your character sheet in Roll20 -> go to the **Attributes & Abilities** tab -> click **+ Add** under Abilities -> paste any macro below and check **\"Show in Macro Bar\"** or **\"Show as Token Action\"**! Because it is an Ability on the sheet, it NEVER requires a character name, works 100% reliably, and survives JSON re-imports!",
        ]
    )

    if magic > 0:
        lines.extend(
            [
                "",
                "### Leadership / Command Presence Roll (`Influence + Charisma + 2`)",
                "```text",
                f"@{{{c_ref}|gm_toggle}} &{{template:rolls-computed}}{{{{header=@{{{c_ref}|character_name}}}}}}{{{{base=Influence (Leadership + Command Presence)}}}}{{{{dice=[[(@{{{c_ref}|influence}}+@{{{c_ref}|charisma}}+2+@{{{c_ref}|wounds_toggle}}+@{{{c_ref}|modifiers_toggle}}+@{{{c_ref}|edge_toggle}})d6>5@{{{c_ref}|explode_toggle}}]]}}}}{{{{mod=[[@{{{c_ref}|modifiers_toggle}}]]}}}}{{{{wound=[[@{{{c_ref}|wounds_toggle}}]]}}}}{{{{edge=[[@{{{c_ref}|edge_toggle}}]]}}}}{{{{notes=Wise Warrior (-1 Edge cost, min 1) + Command Presence (+2d6, +1 Edge) + Inspire Competence}}}}",
                "```",
                "",
                "### Con / Cosmetic Control Disguise Roll (`Con + Charisma`)",
                "```text",
                f"@{{{c_ref}|gm_toggle}} &{{template:rolls-computed}}{{{{header=@{{{c_ref}|character_name}}}}}}{{{{base=Con (Cosmetic Control R2)}}}}{{{{dice=[[(@{{{c_ref}|con}}+@{{{c_ref}|charisma}}+@{{{c_ref}|wounds_toggle}}+@{{{c_ref}|modifiers_toggle}}+@{{{c_ref}|edge_toggle}})d6>5@{{{c_ref}|explode_toggle}}]]}}}}{{{{mod=[[@{{{c_ref}|modifiers_toggle}}]]}}}}{{{{wound=[[@{{{c_ref}|wounds_toggle}}]]}}}}{{{{edge=[[@{{{c_ref}|edge_toggle}}]]}}}}{{{{notes=Cosmetic Control R2 (-1 Edge boost cost on Con tests) + Nanopaste/Nanocosmetics}}}}",
                "```",
                "",
                "### Spellcasting (`Sorcery + Magic + Specialization +2 + Wise Warrior +1`)",
                "```text",
                f"@{{{c_ref}|gm_toggle}} &{{template:rolls-computed}}{{{{header=@{{{c_ref}|character_name}}}}}}{{{{base=Spellcasting (Sorcery + Magic)}}}}{{{{dice=[[(@{{{c_ref}|sorcery}}+@{{{c_ref}|magic}}+3+@{{{c_ref}|wounds_toggle}}+@{{{c_ref}|modifiers_toggle}}+@{{{c_ref}|edge_toggle}})d6>5@{{{c_ref}|explode_toggle}}]]}}}}{{{{mod=[[@{{{c_ref}|modifiers_toggle}}]]}}}}{{{{wound=[[@{{{c_ref}|wounds_toggle}}]]}}}}{{{{edge=[[@{{{c_ref}|edge_toggle}}]]}}}}{{{{notes=Includes +2 Spellcasting Spec & +1 Improved Ability (Sorcery)}}}}",
                "```",
                "",
                "### Drain Resistance (`Willpower + Charisma`)",
                "```text",
                f"@{{{c_ref}|gm_toggle}} &{{template:rolls-computed}}{{{{header=@{{{c_ref}|character_name}}}}}}{{{{base=Drain Resistance (WIL + CHA)}}}}{{{{dice=[[(@{{{c_ref}|willpower}}+@{{{c_ref}|charisma}}+@{{{c_ref}|modifiers_toggle}}+@{{{c_ref}|edge_toggle}})d6>5@{{{c_ref}|explode_toggle}}]]}}}}{{{{mod=[[@{{{c_ref}|modifiers_toggle}}]]}}}}{{{{edge=[[@{{{c_ref}|edge_toggle}}]]}}}}{{{{notes=Shinto / Musok Tradition Drain Resistance}}}}",
                "```",
            ]
        )

    if resonance > 0:
        lines.extend(
            [
                "",
                "### Red Fox Array (2x Link-Fired) Attack (`20d6` Pool — 2 Wild Dice, 8P DV)",
                "```text",
                f"&{{template:rolls-computed}}{{{{header=@{{character_name}}}}}}{{{{base=Red Fox Array (2x Link-Fired)}}}}{{{{dice=[[(20+@{{wounds_toggle}}+@{{modifiers_toggle}}+@{{edge_toggle}})d6>5@{{explode_toggle}}]]}}}}{{{{wilddie=[[@{{wild_die}}]]}}}}{{{{wilddie_dice=[[2]]}}}}{{{{desc=Mode: SS (Link-Fired), Damage: 8P, AR: 21/23/21/14/-, Ammo: 30(c)}}}}{{{{notes=FS 44 / DC 143. Link-Fired 2x Red Foxes in Eye Mounts. Costs 1 Major & 1 Minor Action. 2 Wild Dice. -3P at Medium range. Smartgun (+1 AR).}}}}{{{{mod=[[@{{modifiers_toggle}}]]}}}}{{{{wound=[[@{{wounds_toggle}}]]}}}}{{{{edge=[[@{{edge_toggle}}]]}}}}",
                "```",
                "",
                "### Red Fox Single Beam (`20d6` Pool — 1 Wild Die, 6P DV)",
                "```text",
                f"&{{template:rolls-computed}}{{{{header=@{{character_name}}}}}}{{{{base=Red Fox (Single Beam)}}}}{{{{dice=[[(20+@{{wounds_toggle}}+@{{modifiers_toggle}}+@{{edge_toggle}})d6>5@{{explode_toggle}}]]}}}}{{{{wilddie=[[@{{wild_die}}]]}}}}{{{{wilddie_dice=[[1]]}}}}{{{{desc=Mode: SS, Damage: 6P, AR: 20/22/20/13/-, Ammo: 30(c)}}}}{{{{notes=FS 44. Independent Single Eye Mount (No extra minor action). 1 Wild Die. -3P at Medium range. Smartgun (+1 AR).}}}}{{{{mod=[[@{{modifiers_toggle}}]]}}}}{{{{wound=[[@{{wounds_toggle}}]]}}}}{{{{edge=[[@{{edge_toggle}}]]}}}}",
                "```",
                "",
                "### Tesla Coil: Straight Line (`20d6` Pool — 5S(e) DV)",
                "```text",
                f"&{{template:rolls-computed}}{{{{header=@{{character_name}}}}}}{{{{base=Tesla Coil (Straight Line)}}}}{{{{dice=[[(20+@{{wounds_toggle}}+@{{modifiers_toggle}}+@{{edge_toggle}})d6>5@{{explode_toggle}}]]}}}}{{{{desc=Mode: SS, Damage: 5S(e), AR: 10/12/-/-/-}}}}{{{{notes=BS 49 / SR6 117 Flamethrower rules. Fires in a straight line 20m long. Target defends with REA + INT vs AR. 5S(e) Electrical damage. 20 charges.}}}}{{{{mod=[[@{{modifiers_toggle}}]]}}}}{{{{wound=[[@{{wounds_toggle}}]]}}}}{{{{edge=[[@{{edge_toggle}}]]}}}}",
                "```",
                "",
                "### Tesla Coil: Wobbly Cone (`20d6` Pool — 4S(e) DV, Apex 8.58°)",
                "```text",
                f"&{{template:rolls-computed}}{{{{header=@{{character_name}}}}}}{{{{base=Tesla Coil (Wobbly Cone)}}}}{{{{dice=[[(20+@{{wounds_toggle}}+@{{modifiers_toggle}}+@{{edge_toggle}})d6>5@{{explode_toggle}}]]}}}}{{{{desc=Mode: SS, Damage: 4S(e), AR: 12/14/-/-/-}}}}{{{{notes=BS 49 / SR6 117. Fires in a cone 20m long, 3m wide at base (apex angle 8.58°). May use wild die. 4S(e) Electrical damage. 20 charges.}}}}{{{{mod=[[@{{modifiers_toggle}}]]}}}}{{{{wound=[[@{{wounds_toggle}}]]}}}}{{{{edge=[[@{{edge_toggle}}]]}}}}",
                "```",
                "",
                "### Engineering: Drones (`15d6` Pool — Drone Maintenance & Repairs)",
                "```text",
                f"&{{template:rolls-computed}}{{{{header=@{{character_name}}}}}}{{{{base=Engineering (Drones)}}}}{{{{dice=[[(15+@{{wounds_toggle}}+@{{modifiers_toggle}}+@{{edge_toggle}})d6>5@{{explode_toggle}}]]}}}}{{{{mod=[[@{{modifiers_toggle}}]]}}}}{{{{wound=[[@{{wounds_toggle}}]]}}}}{{{{edge=[[@{{edge_toggle}}]]}}}}{{{{notes=15d6 Pool: Real Logic (4) + Engineering (5) + Drones Spec (+2) + Taz Teamwork (+4). Meatspace action (Natural Hacker does not apply). Autosoft only applies to Drones.}}}}",
                "```",
                "",
                "### Biotech: First Aid & Medicine (`15d6` Pool — Mobile Medic TacApp)",
                "```text",
                f"&{{template:rolls-computed}}{{{{header=@{{character_name}}}}}}{{{{base=Biotech (First Aid / Medicine)}}}}{{{{dice=[[(15+@{{wounds_toggle}}+@{{modifiers_toggle}}+@{{edge_toggle}})d6>5@{{explode_toggle}}]]}}}}{{{{mod=[[@{{modifiers_toggle}}]]}}}}{{{{wound=[[@{{wounds_toggle}}]]}}}}{{{{edge=[[@{{edge_toggle}}]]}}}}{{{{notes=15d6 Pool: Real Logic (4) + Biotech (7) + Mobile Medic TacApp (+4, half Resonance). Meatspace action (Natural Hacker does not apply). Heals damage, stabilizes patients, and treats trauma.}}}}",
                "```",
                "",
                "### Outdoors: Navigation (`9d6` Pool — Land & Route Navigation)",
                "```text",
                f"&{{template:rolls-computed}}{{{{header=@{{character_name}}}}}}{{{{base=Outdoors (Navigation)}}}}{{{{dice=[[(9+@{{wounds_toggle}}+@{{modifiers_toggle}}+@{{edge_toggle}})d6>5@{{explode_toggle}}]]}}}}{{{{mod=[[@{{modifiers_toggle}}]]}}}}{{{{wound=[[@{{wounds_toggle}}]]}}}}{{{{edge=[[@{{edge_toggle}}]]}}}}{{{{notes=9d6 Pool: Real Intuition (2) + Outdoors (5) + Navigation Spec (+2). Meatspace action (Natural Hacker does not apply). Autosoft only applies to Navigation.}}}}",
                "```",
                "",
                "### Tesla Coil: Sweep Cone (`20d6` Pool — 2S(e) DV, Apex 28.07°)",
                "```text",
                f"&{{template:rolls-computed}}{{{{header=@{{character_name}}}}}}{{{{base=Tesla Coil (Sweep Cone)}}}}{{{{dice=[[(20+@{{wounds_toggle}}+@{{modifiers_toggle}}+@{{edge_toggle}})d6>5@{{explode_toggle}}]]}}}}{{{{desc=Mode: SS, Damage: 2S(e), AR: 14/16/-/-/-}}}}{{{{notes=BS 49 / SR6 117. Fires in a cone 20m long, 10m wide at base (apex angle 28.07°). May use wild die. 2S(e) Electrical damage. 20 charges.}}}}{{{{mod=[[@{{modifiers_toggle}}]]}}}}{{{{wound=[[@{{wounds_toggle}}]]}}}}{{{{edge=[[@{{edge_toggle}}]]}}}}",
                "```",
                "",
                "### Standard Matrix Defense Umbrella (`21d6` — 5 Bought Hits vs Attack & Sleaze Actions)",
                "```text",
                f"@{{{c_ref}|gm_toggle}} &{{template:rolls-computed}}{{{{header=@{{{c_ref}|character_name}}}}}}{{{{base=Matrix Defense Umbrella (FW 9 + RES 12)}}}}{{{{dice=[[(21+@{{{c_ref}|wounds_toggle}}+@{{{c_ref}|modifiers_toggle}}+@{{{c_ref}|edge_toggle}})d6>5@{{{c_ref}|explode_toggle}}]]}}}}{{{{mod=[[@{{{c_ref}|modifiers_toggle}}]]}}}}{{{{wound=[[@{{{c_ref}|wounds_toggle}}]]}}}}{{{{edge=[[@{{{c_ref}|edge_toggle}}]]}}}}{{{{notes=Standard Matrix Defense (21d6 = 5 Bought Hits): Firewall (9) + Natural Hacker Resonance (8) + Resonance Focus (+4). Matrix DR 16 (treated as 20 DR for Edge via Designer Home Device). Encryption: +1 threshold to incoming Cracking tests.}}}}",
                "```",
                "",
                "### Full Matrix Defense Umbrella (`34d6` — 8 Bought Hits, Major Action)",
                "```text",
                f"@{{{c_ref}|gm_toggle}} &{{template:rolls-computed}}{{{{header=@{{{c_ref}|character_name}}}}}}{{{{base=Full Matrix Defense (34d6 -> 8 Bought Hits)}}}}{{{{dice=[[(34+@{{{c_ref}|wounds_toggle}}+@{{{c_ref}|modifiers_toggle}}+@{{{c_ref}|edge_toggle}})d6>5@{{{c_ref}|explode_toggle}}]]}}}}{{{{mod=[[@{{{c_ref}|modifiers_toggle}}]]}}}}{{{{wound=[[@{{{c_ref}|wounds_toggle}}]]}}}}{{{{edge=[[@{{{c_ref}|edge_toggle}}]]}}}}{{{{notes=Full Matrix Defense (34d6 = 8 Bought Hits): RES (8) + RES Focus (+4) + FW (9) + Personal Assistant R6 (+6) + Directional Shield Active DP (+7).}}}}",
                "```",
                "",
                "### Cyber Spike (`23d6` — Electronics Test vs Body + Essence)",
                "```text",
                f"@{{{c_ref}|gm_toggle}} &{{template:rolls-computed}}{{{{header=@{{{c_ref}|character_name}}}}}}{{{{base=Cyber Spike (Electronics + RES)}}}}{{{{dice=[[(23+@{{{c_ref}|wounds_toggle}}+@{{{c_ref}|modifiers_toggle}}+@{{{c_ref}|edge_toggle}})d6>5@{{{c_ref}|explode_toggle}}]]}}}}{{{{mod=[[@{{{c_ref}|modifiers_toggle}}]]}}}}{{{{wound=[[@{{{c_ref}|wounds_toggle}}]]}}}}{{{{edge=[[@{{{c_ref}|edge_toggle}}]]}}}}{{{{notes=23d6 Pool: Electronics (5) + Complex Forms Spec (+2) + Resonance (8) + Resonance Focus (+4) + Taz Symbiosis (+4) vs Body + Essence. Note: ECM Warrior II does not apply (Electronics test); Cybercombat spec not possessed. Net hits = Physical damage + cyberware stress. Sustained.}}}}",
                "```",
                "",
                "### Resonance Spike (`23d6` — Cracking Test vs Willpower + Firewall)",
                "```text",
                f"@{{{c_ref}|gm_toggle}} &{{template:rolls-computed}}{{{{header=@{{{c_ref}|character_name}}}}}}{{{{base=Resonance Spike (Cracking + RES)}}}}{{{{dice=[[(23+@{{{c_ref}|wounds_toggle}}+@{{{c_ref}|modifiers_toggle}}+@{{{c_ref}|edge_toggle}})d6>5@{{{c_ref}|explode_toggle}}]]}}}}{{{{mod=[[@{{{c_ref}|modifiers_toggle}}]]}}}}{{{{wound=[[@{{{c_ref}|wounds_toggle}}]]}}}}{{{{edge=[[@{{{c_ref}|edge_toggle}}]]}}}}{{{{notes=23d6 Pool: Cracking (5) + Resonance (8) + Resonance Focus (+4) + Taz Symbiosis (+4) + ECM Warrior II (+2) vs Willpower + Firewall. Note: Cybercombat spec not possessed. Net hits = unresisted Matrix damage. Instant.}}}}",
                "```",
                "",
                "### Sprite Power: Death Mark (`23d6` — Offensive Cracking Test vs Intuition + Firewall)",
                "```text",
                f"@{{{c_ref}|gm_toggle}} &{{template:rolls-computed}}{{{{header=@{{{c_ref}|character_name}}}}}}{{{{base=Sprite Power: Death Mark (Cracking + RES)}}}}{{{{dice=[[(23+@{{{c_ref}|wounds_toggle}}+@{{{c_ref}|modifiers_toggle}}+@{{{c_ref}|edge_toggle}})d6>5@{{{c_ref}|explode_toggle}}]]}}}}{{{{mod=[[@{{{c_ref}|modifiers_toggle}}]]}}}}{{{{wound=[[@{{{c_ref}|wounds_toggle}}]]}}}}{{{{edge=[[@{{{c_ref}|edge_toggle}}]]}}}}{{{{notes=23d6 Pool: Cracking (5) + Resonance (8) + Resonance Focus (+4) + Taz Symbiosis (+4) + ECM Warrior II (+2) vs Intuition + Firewall. Target takes net hits as extra Matrix DV on all attacks. Sustained.}}}}",
                "```",
                "",
                "### Data Spike (`23d6` — Matrix Cybercombat Action)",
                "```text",
                f"@{{{c_ref}|gm_toggle}} &{{template:rolls-computed}}{{{{header=@{{{c_ref}|character_name}}}}}}{{{{base=Data Spike (Cracking + RES/LOG)}}}}{{{{dice=[[(23+@{{{c_ref}|wounds_toggle}}+@{{{c_ref}|modifiers_toggle}}+@{{{c_ref}|edge_toggle}})d6>5@{{{c_ref}|explode_toggle}}]]}}}}{{{{mod=[[@{{{c_ref}|modifiers_toggle}}]]}}}}{{{{wound=[[@{{{c_ref}|wounds_toggle}}]]}}}}{{{{edge=[[@{{{c_ref}|edge_toggle}}]]}}}}{{{{notes=23d6 Pool: Cracking (5) + Natural Hacker RES (12) + Taz (+4) + ECM Warrior II (+2) vs Intuition + Firewall. Base DV = Attack/2 (4P) + net hits. AR 16 (Attack 7 + Sleaze 9).}}}}",
                "```",
                "",
                "### Brute Force (`23d6` — Matrix Cracking Action)",
                "```text",
                f"@{{{c_ref}|gm_toggle}} &{{template:rolls-computed}}{{{{header=@{{{c_ref}|character_name}}}}}}{{{{base=Brute Force (Cracking + RES/LOG)}}}}{{{{dice=[[(23+@{{{c_ref}|wounds_toggle}}+@{{{c_ref}|modifiers_toggle}}+@{{{c_ref}|edge_toggle}})d6>5@{{{c_ref}|explode_toggle}}]]}}}}{{{{mod=[[@{{{c_ref}|modifiers_toggle}}]]}}}}{{{{wound=[[@{{{c_ref}|wounds_toggle}}]]}}}}{{{{edge=[[@{{{c_ref}|edge_toggle}}]]}}}}{{{{notes=23d6 Pool: Cracking (5) + Natural Hacker RES (12) + Taz (+4) + ECM Warrior II (+2) vs Willpower + Firewall. Grants User Access (+1 Edge if 2+ net hits).}}}}",
                "```",
                "",
                "### Hack on the Fly (`21d6` — Matrix Sleaze Action)",
                "```text",
                f"@{{{c_ref}|gm_toggle}} &{{template:rolls-computed}}{{{{header=@{{{c_ref}|character_name}}}}}}{{{{base=Hack on the Fly (Cracking + RES/LOG)}}}}{{{{dice=[[(21+@{{{c_ref}|wounds_toggle}}+@{{{c_ref}|modifiers_toggle}}+@{{{c_ref}|edge_toggle}})d6>5@{{{c_ref}|explode_toggle}}]]}}}}{{{{mod=[[@{{{c_ref}|modifiers_toggle}}]]}}}}{{{{wound=[[@{{{c_ref}|wounds_toggle}}]]}}}}{{{{edge=[[@{{{c_ref}|edge_toggle}}]]}}}}{{{{notes=21d6 Pool: Cracking (5) + Natural Hacker RES (12) + Taz (+4) vs Intuition + Firewall. Stealthy access without raising alarm. AR 16.}}}}",
                "```",
                "",
                "### Matrix Perception (`23d6` — Electronics + RES/LOG + Software Spec)",
                "```text",
                f"@{{{c_ref}|gm_toggle}} &{{template:rolls-computed}}{{{{header=@{{{c_ref}|character_name}}}}}}{{{{base=Matrix Perception (Electronics + RES/LOG)}}}}{{{{dice=[[(23+@{{{c_ref}|wounds_toggle}}+@{{{c_ref}|modifiers_toggle}}+@{{{c_ref}|edge_toggle}})d6>5@{{{c_ref}|explode_toggle}}]]}}}}{{{{mod=[[@{{{c_ref}|modifiers_toggle}}]]}}}}{{{{wound=[[@{{{c_ref}|wounds_toggle}}]]}}}}{{{{edge=[[@{{{c_ref}|edge_toggle}}]]}}}}{{{{notes=23d6 Pool: Electronics (5) + Software Spec (+2) + Natural Hacker RES (12) + Taz (+4) vs Sleaze + Willpower. Inspects Matrix icons, running programs, and hidden nodes.}}}}",
                "```",
                "",
                "### Control Device (`21d6` — Electronics + RES/LOG)",
                "```text",
                f"@{{{c_ref}|gm_toggle}} &{{template:rolls-computed}}{{{{header=@{{{c_ref}|character_name}}}}}}{{{{base=Control Device (Electronics + RES/LOG)}}}}{{{{dice=[[(21+@{{{c_ref}|wounds_toggle}}+@{{{c_ref}|modifiers_toggle}}+@{{{c_ref}|edge_toggle}})d6>5@{{{c_ref}|explode_toggle}}]]}}}}{{{{mod=[[@{{{c_ref}|modifiers_toggle}}]]}}}}{{{{wound=[[@{{{c_ref}|wounds_toggle}}]]}}}}{{{{edge=[[@{{{c_ref}|edge_toggle}}]]}}}}{{{{notes=21d6 Pool: Electronics (5) + Natural Hacker RES (12) + Taz (+4) vs Willpower + Firewall. Remotely commands or triggers target electronics.}}}}",
                "```",
                "",
                "### Compile Sprite (`22d6` — Tasking + RES + Compiling Spec + Resonance Link)",
                "```text",
                f"@{{{c_ref}|gm_toggle}} &{{template:rolls-computed}}{{{{header=@{{{c_ref}|character_name}}}}}}{{{{base=Compile Sprite (Tasking + RES)}}}}{{{{dice=[[(22+@{{{c_ref}|wounds_toggle}}+@{{{c_ref}|modifiers_toggle}}+@{{{c_ref}|edge_toggle}})d6>5@{{{c_ref}|explode_toggle}}]]}}}}{{{{mod=[[@{{{c_ref}|modifiers_toggle}}]]}}}}{{{{wound=[[@{{{c_ref}|wounds_toggle}}]]}}}}{{{{edge=[[@{{{c_ref}|edge_toggle}}]]}}}}{{{{notes=22d6 Pool: Tasking (6) + Compiling Spec (+2) + Resonance (12) + Resonance Link (+2) vs Sprite Level. Technoshamans: -2 Fade Value, +1 Service on >= 1 hit.}}}}",
                "```",
                "",
                "### Register Sprite (`20d6` — Tasking + RES + Registering Spec)",
                "```text",
                f"@{{{c_ref}|gm_toggle}} &{{template:rolls-computed}}{{{{header=@{{{c_ref}|character_name}}}}}}{{{{base=Register Sprite (Tasking + RES)}}}}{{{{dice=[[(20+@{{{c_ref}|wounds_toggle}}+@{{{c_ref}|modifiers_toggle}}+@{{{c_ref}|edge_toggle}})d6>5@{{{c_ref}|explode_toggle}}]]}}}}{{{{mod=[[@{{{c_ref}|modifiers_toggle}}]]}}}}{{{{wound=[[@{{{c_ref}|wounds_toggle}}]]}}}}{{{{edge=[[@{{{c_ref}|edge_toggle}}]]}}}}{{{{notes=20d6 Pool: Tasking (6) + Registering Spec (+2) + Resonance (12) vs Sprite Level x 2. Technoshamans: -2 Fade Value.}}}}",
                "```",
                "",
                "### Fade Resistance (`10d6` — Willpower + Charisma)",
                "```text",
                f"@{{{c_ref}|gm_toggle}} &{{template:rolls-computed}}{{{{header=@{{{c_ref}|character_name}}}}}}{{{{base=Fade Resistance (WIL + CHA)}}}}{{{{dice=[[(10+@{{{c_ref}|modifiers_toggle}}+@{{{c_ref}|edge_toggle}})d6>5@{{{c_ref}|explode_toggle}}]]}}}}{{{{mod=[[@{{{c_ref}|modifiers_toggle}}]]}}}}{{{{edge=[[@{{{c_ref}|edge_toggle}}]]}}}}{{{{notes=Technoshamans Stream Fade Resistance: Willpower (6) + Charisma (4) = 10d6. Compiling/Decompiling actions reduce Fade Value by 2.}}}}",
                "```",
            ]
        )
    return "\n".join(lines) + "\n"


def export_roll20_json(
    char_data: Dict[str, Any],
    char_repo_path: Optional[str] = None,
    indent: int = 2,
) -> str:
    """
    Serialize the compiled character dossier into a formatted Roll20 Genesis JSON string.
    Also writes the companion `<char_id>_roll20_macros.md` guide to the character's output
    directory when `char_repo_path` is provided.
    """
    payload = build_roll20_payload(char_data, char_repo_path=char_repo_path)
    if char_repo_path and os.path.exists(char_repo_path):
        try:
            cid = str((char_data.get("identity") or {}).get("id") or "character").lower()
            out_dir = os.path.join(char_repo_path, "output")
            os.makedirs(out_dir, exist_ok=True)
            guide_path = os.path.join(out_dir, f"{cid}_roll20_macros.md")
            with open(guide_path, "w", encoding="utf-8") as f:
                f.write(generate_roll20_helper_guide(char_data, payload))
        except Exception:
            pass
    return json.dumps(payload, indent=indent, ensure_ascii=False)
