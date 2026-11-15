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
        "Echo: Must have Living Network. When living persona functions as master device in a network, act as an advanced conduit for data, storing up to Submersion Grade in shared network Edge and broadcasting TacApps.",
        "Hack & Slash p.65",
    ),
    "overclocking": (
        "Echo: Accelerate living persona to act more quickly in the Matrix. Gain an additional Minor Action and +1D6 Initiative Dice while in hot-sim VR.",
        "CRB p.195",
    ),
    "software emulator": (
        "Echo: Must have Living Network. Capable of running commlink apps, cyberprograms, and autosofts directly on living persona. Program slots equal to Submersion Grade.",
        "Hack & Slash p.68",
    ),
    "sprite link": (
        "Echo: Mind is more closely linked to sprites. When spending a task and a Minor Action to command a sprite to assist with a Matrix action, gain +1 Edge for that action.",
        "Hack & Slash p.64",
    ),
    "syntax error": (
        "Echo: When aware of a Matrix action targeting an icon you are also aware of, spend a Minor Anytime Action to provide the target with bonus dice equal to your Submersion Grade on their defense test. You may also attempt to reduce or cancel a sustained complex form or sprite power you are aware of (Electronics + Resonance + Submersion Grade vs. Logic + Resonance).",
        "Hack & Slash p.69",
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
    src_str = str(source or "").strip()
    pg_str = str(page or "").strip()
    fb_str = str(fallback_page or "").strip()

    def _has_book_ref(s: str) -> bool:
        if not s:
            return False
        if "/" in s:
            return True
        return bool(re.search(r"[A-Za-z]{2,}", re.sub(r"^p\.\s*", "", s)))

    if pg_str:
        if _has_book_ref(pg_str):
            return pg_str
        clean_pg = re.sub(r"^p\.\s*", "", pg_str)
        return f"{src_str} p.{clean_pg}" if src_str else pg_str
    if fb_str:
        if _has_book_ref(fb_str) or "p." in fb_str or not src_str:
            return fb_str
        return f"{src_str} p.{fb_str}"
    return src_str


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
    current_artifact: Optional[Dict[str, Any]] = None

    def _extract_gear_entry(raw_clean: str, category: str) -> Dict[str, Any]:
        txt = raw_clean.strip()
        notes_parts: List[str] = []
        m_note = re.search(
            r"\s*\(([^)]*(?:Initial|Restock|SRM|CMP|SMH|Provided by|Mission|Loot|Asset|Data|Glade)[^)]*)\)\s*$",
            txt,
            re.IGNORECASE,
        )
        if m_note:
            notes_parts.append(m_note.group(1).strip())
            txt = txt[: m_note.start()].strip()

        qty = 1
        m_qty = re.search(r"\s+\bx(\d+)\b", txt, re.IGNORECASE)
        if m_qty:
            qty = int(m_qty.group(1))
            txt = (txt[: m_qty.start()] + txt[m_qty.end() :]).strip()

        rating: Any = ""
        m_rat = re.search(r"\s*\((?:Rating|R)\s*(\d+)\)\s*$", txt, re.IGNORECASE)
        if m_rat:
            rating = int(m_rat.group(1))
            txt = txt[: m_rat.start()].strip()
        else:
            m_rat_bare = re.search(r"\s+(?:Rating|R)\s*(\d+)\b", txt, re.IGNORECASE)
            if m_rat_bare:
                rating = int(m_rat_bare.group(1))
                txt = (txt[: m_rat_bare.start()] + txt[m_rat_bare.end() :]).strip()

        return {
            "name": txt.strip(),
            "rating": rating,
            "quantity": qty,
            "category": category,
            "notes": " ".join(notes_parts).strip(),
        }

    for raw_line in lines:
        stripped = raw_line.strip()
        if not stripped or stripped.startswith("---"):
            continue
        if stripped.startswith("### "):
            current_section = stripped[4:].strip().lower()
            current_sub_group = ""
            current_device = None
            current_artifact = None
            continue

        is_top_bullet = bool(re.match(r"^[\*\-]\s+", raw_line))
        is_sub_bullet = bool(re.match(r"^\s+[\*\-]\s+", raw_line))

        if "electronic" in current_section and not any(
            k in current_section for k in ("matrix", "commlink", "software")
        ):
            if is_top_bullet:
                clean_txt = _clean_qmd_line_text(stripped)
                if clean_txt:
                    result["extra_gear"].append(_extract_gear_entry(clean_txt, "Electronics"))

        elif any(k in current_section for k in ("matrix", "electronic", "commlink", "software")):
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
                if "data structure" in low_txt:
                    current_sub_group = "ignore"
                    continue
                if low_txt == "other" or low_txt.startswith("other "):
                    current_sub_group = "matrix_other"
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
                elif current_sub_group == "matrix_other":
                    if sub_txt.lower().startswith("linguasoft"):
                        continue
                    result["extra_gear"].append(
                        _extract_gear_entry(sub_txt, "Software / Matrix Asset")
                    )

        elif "other supplies" in current_section:
            if is_top_bullet:
                clean_txt = _clean_qmd_line_text(stripped)
                if clean_txt:
                    result["extra_gear"].append(
                        _extract_gear_entry(clean_txt, "Supplies / Medical & Toxins")
                    )

        elif "courtly regalia" in current_section or "mission artifact" in current_section:
            if is_top_bullet:
                clean_txt = _clean_qmd_line_text(stripped)
                if clean_txt:
                    current_artifact = _extract_gear_entry(clean_txt, "Mission Artifact / Regalia")
                    result["extra_gear"].append(current_artifact)
            elif is_sub_bullet and current_artifact is not None:
                sub_txt = _clean_qmd_line_text(stripped)
                if sub_txt:
                    prev_notes = current_artifact.get("notes") or ""
                    current_artifact["notes"] = (
                        f"{prev_notes} {sub_txt}".strip() if prev_notes else sub_txt
                    )
                    if current_artifact.get("rating", "") == "":
                        m_art_r = re.search(r"\bRating\s*(\d+)\b", sub_txt, re.IGNORECASE)
                        if m_art_r:
                            current_artifact["rating"] = int(m_art_r.group(1))

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
    `modifiers`, `synergies` (foci, mentor spirit), `adept_powers`, `augmentations`,
    and equipped matrix devices.
    """
    influences: Dict[str, List[str]] = {}
    skill_ratings: Dict[str, int] = {}
    for sk in char_data.get("skills") or []:
        if not isinstance(sk, dict):
            continue
        sk_rating = _parse_int(sk.get("rating"), 0)
        for key_field in ("id", "name"):
            k = str(sk.get(key_field) or "").strip().lower().replace(" ", "_")
            if k:
                skill_ratings[k] = sk_rating

    def add_inf(skill_id: str, text: str) -> None:
        bucket = influences.setdefault(skill_id, [])
        if not any(text.lower() == x.lower() for x in bucket):
            bucket.append(text)

    def _format_mod_label(
        mname: str, val: int, mnotes: str, target_sk: Optional[str] = None
    ) -> str:
        clean_name = mname
        clean_notes = mnotes
        if target_sk:
            sk_display = target_sk.replace("_", " ")
            sk_pat = re.compile(rf"\s*\(\s*{re.escape(sk_display)}\s*\)", re.IGNORECASE)
            clean_name = sk_pat.sub("", clean_name).strip()
            clean_notes = sk_pat.sub("", clean_notes).strip()

        redundant_note_pat = re.compile(
            r"^(?:[+-]?\d+\s*(?:d6|dice)?(?:\s+(?:to|for)\s+(?:res|resonance)(?:\s+attribute)?)?|(?:res|resonance)\s*[+-]\d+)\.?$",
            re.IGNORECASE,
        )
        if redundant_note_pat.match(clean_notes) or clean_notes.lower() == clean_name.lower():
            clean_notes = ""

        eff_val = val
        if target_sk and "clamped to" in clean_notes.lower():
            sk_rating = skill_ratings.get(target_sk)
            if sk_rating is not None:
                if eff_val <= 0:
                    m_bonus = re.search(r"\+(\d+)", clean_notes)
                    if m_bonus:
                        eff_val = int(m_bonus.group(1))
                if eff_val > 0:
                    eff_val = min(eff_val, sk_rating)
                    return f"{clean_name} ({eff_val:+d}d6, clamped to skill rating {sk_rating})"

        val_str = f"{eff_val:+d}d6" if eff_val else ""
        if val_str and clean_notes:
            return f"{clean_name} ({val_str}: {clean_notes})"
        if val_str:
            return f"{clean_name} ({val_str})"
        if clean_notes:
            return f"{clean_name} ({clean_notes})"
        return clean_name

    for mod in char_data.get("modifiers") or []:
        if not isinstance(mod, dict) or not mod.get("enabled", True):
            continue
        mname = str(mod.get("name") or "Modifier").strip()
        target = str(mod.get("target") or "").strip().lower()
        val = _parse_int(mod.get("value"), 0)
        mnotes = str(mod.get("notes") or "").strip()

        if target.startswith("skill:"):
            sk_key = target.split(":", 1)[1].strip().replace(" ", "_")
            if sk_key in ROLL20_ACTIVE_SKILLS:
                # No ally sprite or teamwork bonus applies to Tasking itself.
                if sk_key == "tasking" and ("teamwork" in mname.lower() or "symbiosis" in mname.lower()):
                    continue
                add_inf(sk_key, _format_mod_label(mname, val, mnotes, sk_key))
        elif target == "attribute:magic":
            for m_sk in ("sorcery", "conjuring", "enchanting", "astral"):
                add_inf(m_sk, _format_mod_label(mname, val, mnotes, m_sk))
        elif target == "attribute:resonance":
            for r_sk in ("tasking", "cracking", "electronics"):
                add_inf(r_sk, _format_mod_label(mname, val, mnotes, r_sk))
        elif target in ("matrix_actions", "all_matrix_actions"):
            for r_sk in ("cracking", "electronics", "tasking"):
                add_inf(r_sk, _format_mod_label(mname, val, mnotes, r_sk))

    synergies = char_data.get("synergies") or {}
    if isinstance(synergies, dict):
        for focus in synergies.get("foci") or []:
            if not isinstance(focus, dict):
                continue
            fname = str(focus.get("name") or "Focus").strip()
            if "oracle" in fname.lower():
                continue
            fname_base = re.sub(r"\s*\([^)]*\)", "", fname).strip().lower() or fname.lower()
            frating = _parse_int(focus.get("rating", focus.get("force", 0)), 0)
            fmods = focus.get("modifiers") or {}
            bonus = _parse_int(
                fmods.get("magic_dice") if isinstance(fmods, dict) else frating, frating
            )
            if bonus > 0:
                label = f"{fname} (+{bonus}d6)"
                if "resonance" in fname.lower():
                    for r_skill in ("tasking", "cracking", "electronics"):
                        if not any(fname_base in x.lower() for x in influences.get(r_skill, [])):
                            add_inf(r_skill, label)
                else:
                    for m_skill in ("sorcery", "conjuring", "enchanting", "astral"):
                        if not any(
                            fname_base in x.lower() or "power focus" in x.lower()
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

    # Attach ECM Warrior offensive Cracking bonus for M-TOC / ECM-equipped characters.
    if not any("ecm warrior" in x.lower() for x in influences.get("cracking", [])):
        ecm_chunks: List[str] = []
        for md in char_data.get("matrix_devices") or []:
            if isinstance(md, dict):
                ecm_chunks.append(
                    f"{md.get('name', '')} {md.get('notes', '')} {md.get('description', '')} "
                    + " ".join(str(a) for a in (md.get("accessories") or []))
                )
        for q_list in ((char_data.get("qualities") or {}).get("positive") or []):
            ecm_chunks.append(str(q_list))
        ecm_blob = " ".join(ecm_chunks)
        m_ecm = re.search(r"\bECM\s+Warrior\s*(III|II|I|\d+)\b", ecm_blob, re.IGNORECASE)
        if m_ecm:
            tier_raw = m_ecm.group(1).upper()
            tier_map = {"I": 1, "II": 2, "III": 3}
            bonus = tier_map.get(tier_raw) or _parse_int(tier_raw, 2)
            add_inf("cracking", f"ECM Warrior {tier_raw} (+{bonus}d6 Offensive Cracking)")
        elif "m-toc ii" in ecm_blob.lower() or "m-toc mark ii" in ecm_blob.lower():
            add_inf("cracking", "ECM Warrior II (+2d6 Offensive Cracking)")

    return influences


_PROGRAM_CATALOG: Dict[str, Tuple[str, str]] = {
    # Basic Matrix Programs (CRB p.184)
    "browse": ("CRB p.184", "Matrix Search tests take half the normal base time."),
    "baby monitor": (
        "CRB p.184",
        "Monitors your current Overwatch Score and alerts you before convergence.",
    ),
    "configurator": (
        "CRB p.184",
        "Reconfigure ASDF array and swap active Matrix programs with a single Minor Action.",
    ),
    "edit": (
        "CRB p.184",
        "Grants +2 Attack Rating to Edit File tests and automates routine file copying/tagging.",
    ),
    "encryption": (
        "CRB p.184",
        "Adds +1 Firewall (or +1 threshold against incoming Cracking tests on encrypted files).",
    ),
    "signal scrubber": ("CRB p.184", "Provides +2 Noise Reduction."),
    "toolbox": ("CRB p.184", "Increases Data Processing by +1."),
    "virtual machine": (
        "CRB p.184",
        "Adds +2 concurrent program slots; Matrix damage taken increases by +1 box.",
    ),
    # Hacking Programs (CRB p.185)
    "armor": ("CRB p.185", "Grants +2 dice to resist Matrix damage."),
    "biofeedback": (
        "CRB p.185",
        "Inflicts Biofeedback damage (Stun vs Cold-Sim, Physical vs Hot-Sim) alongside Matrix damage.",
    ),
    "biofeedback filter": ("CRB p.185", "Grants +2 dice to resist Biofeedback damage."),
    "blackout": (
        "CRB p.185",
        "Biofeedback damage dealt is always Stun regardless of VR mode.",
    ),
    "decryption": ("CRB p.185", "Increases Attack attribute by +1."),
    "defuse": ("CRB p.185", "Grants +4 dice to Disarm Data Bomb tests."),
    "exploit": ("CRB p.185", "Grants +2 Attack Rating on Hacking actions."),
    "fork": (
        "CRB p.185",
        "Execute a single Matrix action simultaneously against two valid targets.",
    ),
    "lockdown": (
        "CRB p.185",
        "Target persona becomes Link-Locked whenever you deal Matrix damage to it.",
    ),
    "mugger": ("CRB p.185", "Increases Matrix damage from Tar Pit / Crash Program by +1."),
    "overclock": ("CRB p.185", "Adds +2 Attack Rating (or +1 Attack/Sleaze bonus)."),
    "shell": ("CRB p.185", "Grants +1 die to resist both Matrix and Biofeedback damage."),
    "sneak": (
        "CRB p.185",
        "Adds +2 Attack Rating to defensive Matrix actions; blocks Trace Icon physical location.",
    ),
    "stealth": ("CRB p.185", "Increases Sleaze by +1."),
    "trace": ("CRB p.185", "Grants +2 Attack Rating on Trace Icon tests."),
    "track": ("CRB p.185", "Grants +2 dice on Trace Icon tests."),
    # Drone Autosofts (CRB p.269)
    "clearsight": ("CRB p.269", "Drone autosoft used in place of Perception."),
    "electronic warfare": (
        "CRB p.269",
        "Drone autosoft used in place of Electronics (Electronic Warfare).",
    ),
    "evasion": ("CRB p.269", "Drone autosoft used for defense and dodge tests."),
    "maneuvering": ("CRB p.269", "Drone autosoft used in place of Piloting."),
    "stealth (autosoft)": ("CRB p.269", "Drone autosoft used in place of Stealth."),
    "targeting": ("CRB p.269", "Weapon-linked drone autosoft used for autonomous Gunnery."),
    # Commlink Apps & M-TOC TacApps (Hack & Slash / 6WC / Firing Squad)
    "ticker": (
        "Hack & Slash p.58",
        "Automated AR feed pushing monitored alerts, OS warnings, and status telemetry.",
    ),
    "diagnostics": (
        "Hack & Slash p.58",
        "Tracks real-time PAN, drone, and chassis damage/condition monitors.",
    ),
    "mapper": (
        "Hack & Slash p.58",
        "Builds real-time physical and Matrix spatial overlays shared across the PAN.",
    ),
    "personal assistant": (
        "Hack & Slash p.58",
        "AI commlink agent (Bought Hits = Rating / 2) assisting Perception, Electronics, or Full Matrix Defense.",
    ),
    "social hud": (
        "Hack & Slash p.59",
        "AR social analysis overlay flagging micro-expressions, etiquette, and tactical social cues.",
    ),
    "p-ice spines": (
        "Hack & Slash p.59",
        "Retaliatory PAN defense app inflicting Matrix feedback damage against hostile intruders.",
    ),
    "facial scanner": (
        "Hack & Slash p.58",
        "Real-time facial recognition scanner querying SIN and public registries.",
    ),
    "thermal mood reading": (
        "Sixth World Companion p.131",
        "Micro-thermal facial imaging app reading stress, excitement, and deception cues.",
    ),
    "vocal tension detection": (
        "Sixth World Companion p.131",
        "Audio analyzer flagging stress and deception markers in spoken speech.",
    ),
    "nanomask": (
        "Sixth World Companion p.131",
        "Replaces outgoing AR/video commlink feeds with a synthetic persona mask.",
    ),
    "ecm warrior ii": (
        "Firing Squad p.68",
        "M-TOC TacApp granting +2d6 Offensive Cracking and -2 Noise to PAN deckers/technomancers.",
    ),
    "sneak-sneak": (
        "Firing Squad p.68",
        "M-TOC TacApp sharing +2d6 Stealth teamwork across networked PAN and drone assets.",
    ),
    "target artist": (
        "Firing Squad p.68",
        "M-TOC TacApp sharing LOS, reducing target cover by -1, and negating blind-fire penalties.",
    ),
    "artillery barrage": (
        "Firing Squad p.68",
        "M-TOC TacApp providing +1d6 indirect-fire and launcher coordination.",
    ),
    "mobile medic": (
        "Firing Squad p.68",
        "M-TOC TacApp providing +4d6 networked Biotech / First Aid triage support.",
    ),
}


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
    has_red_fox = any("red fox" in str(w.get("name", "")).lower() or "crimson wasp" in str(w.get("name", "")).lower() for w in _all_w if isinstance(w, dict))
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
                    f"• {5 + (submersion or 9)} Edge Storage (5 M-TOC Mark II, {submersion or 9} Transcendent Network)\n"
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
                "choice": "22d6 Standard / 25d6 Base Full Defense / 41d6 All-In",
                "positive": True,
                "rating": "",
                "page": "CRB p.181 / Hack & Slash p.33, 58, 69-70, 124",
                "description": (
                    "• Matrix Defense Rating (DR): 16 (Data Processing 7 + Firewall 9). Note: Designer Home Device (H&S p.124) treats Man-at-Arms physical Device Rating as +4 higher (Base 2 + 4 = 6) vs. Data Processing (7) for Edge comparison — it does NOT add +4 to Matrix DR.\n"
                    "• Encryption: +1 threshold to all incoming Cracking tests against any device on Reiko's PAN.\n"
                    "• Standard Matrix Defense (Free Action): 22d6 (5 Bought Hits) = Firewall (9) + Natural Hacker Resonance (9) + Resonance Focus (+4).\n"
                    "• Base Full Matrix Defense (PA R6 3 Bought Hits): 25d6 (6 Bought Hits) = 22d6 Standard + 3 Bought Hits from Personal Assistant R6.\n"
                    "• All-In Matrix Defense (Minor Anytime Actions when aware): 41d6 (10 Bought Hits) = 25d6 Base + Echo: Syntax Error (+9 Submersion) + Directional Shield Active Data Processing (+7).\n"
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
                sp_str = str(sp)
                is_exp = "expertise" in sp_str.lower()
                sp_clean = re.sub(r'\s*\(expertise\)', '', sp_str, flags=re.IGNORECASE).strip()
                _add_spec(sp_clean, is_exp)

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
                    "influencedBy": [
                        "Pilot Origins / Software Emulator (H&S p.120, R9 capped at DP 7)",
                        "Mobile Medic (+4d6)",
                    ],
                    "description": "Meatspace skill: uses Real Logic 4 (not Matrix Logic 13) + Rating 7 + Mobile Medic 4 = 15d6 Pool. Set Modifier to -5 (-9 Natural Hacker/Focus + 4 Mobile Medic; or -1 if Focus Effect is toggled off).",
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
                    "influencedBy": [
                        "Pilot Origins / Software Emulator (H&S p.120, R5 + Drones Spec 2 = 7 cap)",
                        "Taz Teamwork (+4d6)",
                    ],
                    "description": "Usable only for Drones. Meatspace skill: uses Real Logic 4 (not Matrix Logic 13) + Rating 5 + Drones Spec 2 + Taz Teamwork 4 = 15d6 Pool. Set Modifier to -5 (-9 Natural Hacker/Focus + 4 Taz Teamwork; or -1 if Focus Effect is toggled off).",
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
                    "influencedBy": [
                        "Pilot Origins / Software Emulator (H&S p.120, R5 + Navigation Spec 2 = 7 cap)",
                    ],
                    "description": "Usable only for Navigation. Meatspace skill: uses Real Intuition 2 (not Matrix Intuition 13) + Rating 5 + Navigation Spec 2 = 9d6 Pool. Set Modifier to -11 (-7 Natural Hacker - 4 Focus; or -7 if Focus Effect is toggled off).",
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

    commlink_app_names_lower = set()
    for _app in extra_purchases.get("commlink_apps", []):
        _an = str(_app.get("name") or "").strip().lower()
        if _an:
            commlink_app_names_lower.add(_an)
            commlink_app_names_lower.add(re.sub(r"\s*\([^)]*\)\s*$", "", _an).strip())

    extra_medkit_rating = next(
        (
            eg.get("rating")
            for eg in extra_purchases.get("extra_gear", [])
            if isinstance(eg, dict)
            and "medkit" in str(eg.get("name") or "").lower()
            and isinstance(eg.get("rating"), int)
        ),
        "",
    )

    fallback_gear_info: Dict[str, Tuple[str, str]] = {
        "peak-discharge laser battery clips": (
            "Spare peak-discharge laser battery clips for Crimson Wasp eye mounts.",
            "Firing Squad p.44",
        ),
        "glitter grenades": (
            "Aerosol dispersal grenades releasing reflective chaff.",
            "Firing Squad p.36-37",
        ),
        "built-in medkit": (
            "Drone-integrated diagnostic and trauma stabilization medkit on the Man-at-Arms chassis.",
            "CRB p.119",
        ),
        "medkit": (
            "Portable medical diagnostic and trauma stabilization kit.",
            "CRB p.119",
        ),
        "laser jack": (
            "Line-of-sight optical transceiver for direct optical Matrix links.",
            "Hack & Slash p.41",
        ),
        "satellite link": (
            "Satellite uplink transceiver for remote Matrix access outside grid coverage.",
            "CRB p.268",
        ),
        "narcoject": (
            "Fast-acting non-lethal knockout toxin.",
            "CRB p.122",
        ),
        "cyanide": (
            "Fast-acting lethal toxin.",
            "Body Shop p.113",
        ),
        "mapsoft": (
            "Geospatial and regional navigation database software.",
            "CRB p.271",
        ),
        "shopsoft": (
            "Technical diagnostic and repair schematic software.",
            "CRB p.271",
        ),
        "coding facility": (
            "Dedicated software engineering and compilation facility for custom programming work.",
            "Hack & Slash",
        ),
    }

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

        m_lead_qty = re.match(r"^(\d+)\s*x\s+(.+)$", gname, re.IGNORECASE)
        if m_lead_qty:
            parsed_qty = int(m_lead_qty.group(1))
            gname = m_lead_qty.group(2).strip()
            if gcount <= 1:
                gcount = parsed_qty

        gname_low = gname.lower()
        gname_base_low = re.sub(r"\s*\([^)]*\)\s*$", "", gname_low).strip()
        if gname_low in commlink_app_names_lower or gname_base_low in commlink_app_names_lower:
            continue

        if "built-in medkit" in gname_low and grating == "" and extra_medkit_rating != "":
            grating = extra_medkit_rating
        elif (
            "medkit" in gname_low
            and "savior" not in gname_low
            and any("medkit" in s and "savior" not in s for s in seen_items)
        ):
            continue

        gnotes = str(g.get("notes") or g.get("description") or "").strip()

        lookup_gname = gname
        if "glitter grenades" in gname_low:
            lookup_gname = "Glitter Grenade"
        elif "built-in medkit" in gname_low:
            lookup_gname = "Medkit"
        elif gname_low == "mapsoft":
            lookup_gname = "Mapsofts"
        elif gname_low == "shopsoft":
            lookup_gname = "Shopsofts"

        db_row = _lookup_db_row(conn, "ref_gear", g.get("ref"), lookup_gname)
        rule_desc, rule_page = _lookup_rule_text_and_page(conn, lookup_gname)
        fb_desc, fb_page = "", ""
        for fk, (fd, fp) in fallback_gear_info.items():
            if fk in gname_low:
                fb_desc, fb_page = fd, fp
                break

        page_str = _format_page(
            g.get("source") or (db_row or {}).get("source"),
            g.get("page") or _parse_xml_attr((db_row or {}).get("raw_xml", ""), "page"),
            fallback_page=rule_page or fb_page,
        )
        full_gdesc = _combine_descriptions(
            gnotes or _strip_xml_tags((db_row or {}).get("raw_xml", "")),
            rule_desc or fb_desc,
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

    # Route inhabited anthrodrone (Shiawase Man-at-Arms) chassis upgrades into Augmentations
    if is_ai:
        maa_drone = next(
            (
                d
                for d in (char_data.get("drones") or [])
                if isinstance(d, dict) and "man-at-arms" in str(d.get("name", "")).lower()
            ),
            None,
        )
        if maa_drone is not None:
            from sr6core.rules.vehicles import parse_vehicle_modifications

            maa_prof = parse_vehicle_modifications(maa_drone, char_data=char_data)
            maa_mods_blob = " | ".join(
                str(m) for m in (maa_drone.get("modifications") or [])
            ).lower()
            body_gain = max(0, maa_prof["augmented_body"] - maa_prof["base_body"]) or 5
            maa_chassis_entries: List[Tuple[str, Dict[str, Any]]] = [
                (
                    "structural integrity",
                    {
                        "name": "Increased Structural Integrity",
                        "level": body_gain,
                        "quality": "STANDARD",
                        "essence": 0.0,
                        "page": "Double Clutch p.125",
                        "description": (
                            f"Chassis reinforcement (+{body_gain} Body: Base {maa_prof['base_body']} -> Body {maa_prof['augmented_body']}; 5 Chassis slots). "
                            f"Physical Condition Monitor {8 + (maa_prof['augmented_body'] + 1) // 2} and Physical DR {maa_prof['augmented_body'] + maa_prof['base_armor']}."
                        ),
                        "accessories": [],
                    },
                ),
                (
                    "vector thrust",
                    {
                        "name": "Secondary Propulsion: Vector Thrust (LAV) & Thruster Tuning",
                        "level": "",
                        "quality": "STANDARD",
                        "essence": 0.0,
                        "page": "Double Clutch p.134, 136-138",
                        "description": (
                            "Forearm/calf vector thrusters with scapular wing spars (5 Powertrain slots; flight speed/handling), "
                            "Improved Acceleration (2 Ranks: +60% -> 41 m/rd), Top Speed Increase (3 Ranks: +60% -> 480 / 576 km/h), "
                            "plus thigh Nitro Boost capacitors (RP) and Hydrocarbon Fuel Converter (RP)."
                        ),
                        "accessories": [
                            {"name": "Improved Acceleration (2 Ranks)"},
                            {"name": "Top Speed Increase (3 Ranks)"},
                            {"name": "Nitro Boost (RP)"},
                            {"name": "Hydrocarbon Fuel Converter (RP)"},
                        ],
                    },
                ),
                (
                    "chameleon coating",
                    {
                        "name": "Chameleon Coating & Passive Stealth",
                        "level": 4,
                        "quality": "STANDARD",
                        "essence": 0.0,
                        "page": "Double Clutch p.138",
                        "description": (
                            "Chameleon Coating 4 (2 Electronics slots; grants Improved Invisibility 4 below second speed interval) "
                            "paired with Passive Stealth Features (1 Electronics slot)."
                        ),
                        "accessories": [{"name": "Passive Stealth Features"}],
                    },
                ),
                (
                    "realistic features",
                    {
                        "name": "Realistic Features",
                        "level": 4,
                        "quality": "STANDARD",
                        "essence": 0.0,
                        "page": "Double Clutch p.132",
                        "description": (
                            "Realistic anthropomorphic mimicry (4 Chassis slots, Rating 4)."
                        ),
                        "accessories": [],
                    },
                ),
                (
                    "cyberarm",
                    {
                        "name": "Synthetic Cyberarm (Right) — 8 Capacity",
                        "level": "",
                        "quality": "USED",
                        "essence": 0.0,
                        "page": "CRB p.282, 289 / DC p.131",
                        "description": (
                            "Used Synthetic Cyberarm replacing factory right anthroform cyberlimb (0 vehicle mod slots); "
                            "houses integrated Tesla Coil cyberweapon."
                        ),
                        "accessories": [{"name": "Tesla Coil (Cyberweapon)"}],
                    },
                ),
                (
                    "enhanced sensors",
                    {
                        "name": "Enhanced Sensors Array",
                        "level": maa_prof["hardware_sensor"],
                        "quality": "STANDARD",
                        "essence": 0.0,
                        "page": "Double Clutch p.142 / DA p.178",
                        "description": (
                            f"Base Sensor 2 upgraded to Hardware Sensor {maa_prof['hardware_sensor']} (7 Electronics slots; "
                            f"{maa_prof['augmented_sensor']} Passive w/ Sensor Upgrade & Home Device, "
                            f"{maa_prof['enlightened_sensor']} w/ Enlighten Automaton). Also houses Tactile Sensors (RP only)."
                        ),
                        "accessories": [
                            {"name": "Camera w/ Image Link"},
                            {"name": "Omni-Directional Mic w/ Sound Link"},
                            {"name": "Ultrasound"},
                            {"name": "Low-Light Vision"},
                            {"name": "Flare Compensation"},
                            {"name": "Olfactory Sensor"},
                            {"name": "Oral Chemical Analyzer"},
                            {"name": "Tactile Sensors (RP Only)"},
                        ],
                    },
                ),
                (
                    "weapon mount",
                    {
                        "name": "Weapon Mount (Small) x2 & Ocular Pop-Out Concealment",
                        "level": "",
                        "quality": "STANDARD",
                        "essence": 0.0,
                        "page": "Double Clutch p.124, 143-144",
                        "description": (
                            "1 Standard Hardpoint split into 2 Small Hardpoints (DC p.124) with ocular Pop-Out Concealment "
                            "(0.5 Chassis slots each, DC p.143-144) mounting 2x Crimson Wasp eye lasers."
                        ),
                        "accessories": [
                            {"name": "Pop-Out Concealment (Small) x2"},
                            {"name": "Crimson Wasp x2 (Eye Mounts)"},
                        ],
                    },
                ),
                (
                    "ram plate",
                    {
                        "name": "Ram Plate (Left Forearm Wrist-Shield)",
                        "level": "",
                        "quality": "STANDARD",
                        "essence": 0.0,
                        "page": "Double Clutch p.144",
                        "description": (
                            f"3rd Standard Hardpoint on left forearm wrist-shield mount; adds Body ({maa_prof['augmented_body']}) "
                            "to Ramming Attack Rating and halves return collision damage."
                        ),
                        "accessories": [],
                    },
                ),
                (
                    "drone rack",
                    {
                        "name": "Drone Rack (Small) & Integrated Hardline Comms",
                        "level": "",
                        "quality": "STANDARD",
                        "essence": 0.0,
                        "page": "Double Clutch p.143",
                        "description": (
                            "2nd Standard Hardpoint abdominal bay storing Federated-Boeing Sky Commander "
                            "(foldable swing-wing geometry). Includes integrated Satellite Link and Laser Jack hardpoints."
                        ),
                        "accessories": [
                            {"name": "Stores: Federated-Boeing Sky Commander"},
                            {"name": "Satellite Link"},
                            {"name": "Laser Jack"},
                        ],
                    },
                ),
            ]
            for mod_key, aug_entry in maa_chassis_entries:
                if (mod_key in maa_mods_blob or not maa_mods_blob) and aug_entry["name"].lower() not in seen_augs:
                    seen_augs.add(aug_entry["name"].lower())
                    augmentations_list.append(aug_entry)

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
        extra_autosofts: Dict[str, int] = {}

        if is_ai and is_drone:
            from sr6core.rules.vehicles import parse_vehicle_modifications, calculate_drone_action_pools

            v_prof = parse_vehicle_modifications(v, char_data=char_data)
            if "man-at-arms" in vname.lower():
                # Primary Inhabited Chassis via Override Sprite Power
                vtype = "DRONE_MEDIUM"
                body_val = v_prof["base_body"]
                armor_val = v_prof["base_armor"]
                pilot_val = v_prof["inhabited_pilot"]
                sensor_val = v_prof["hardware_sensor"]
                res_val = res_eff or 8
                des_val = 1 if any("designer" in q.get("name", "").lower() for q in char_data.get("qualities", {}).get("positive", [])) else 0
                aug_sen = v_prof["augmented_sensor"]
                enl_sen = v_prof["enlightened_sensor"]
                enl_delta = enl_sen - aug_sen
                pools = calculate_drone_action_pools(char_data, v, mode="inhabited_override")
                acc_out = [
                    {"name": "Chassis mods listed in Augmentations tab (9 systems)"},
                    {"name": "Crimson Wasp Array (2x Small Eye Mounts)"},
                    {"name": "Tesla Coil (Right Synthetic Cyberarm)"},
                    {"name": "Drone Rack: Federated-Boeing Sky Commander"},
                    {"name": f"Sensor Array (Hardware Rating {sensor_val} -> {aug_sen} Passive / {enl_sen} Enlightened)"},
                ]
                desc_str = (
                    f"{desc_str}\n"
                    f"Primary Inhabited Chassis (Override Sprite Power): Base Pilot {pilot_val} ({res_val} Resonance + {des_val} Designer) +4 Resonance Focus = {pilot_val + 4}; "
                    f"Body {body_val} +{v_prof['augmented_body'] - body_val} Structural Integrity = {v_prof['augmented_body']}; "
                    f"Sensor {sensor_val} (Hardware) +{aug_sen - sensor_val} (+1 Sensor Upgrade, +1 Home Device) = {aug_sen} Passive (+{enl_delta} Enlighten Automaton = {enl_sen} Sustained).\n"
                    f"Pilot Origins (Control Rig R1 Equiv.): +1d6 and -1 Threshold on all inhabited drone tests "
                    f"(Piloting {pools['piloting']['pool']}d6 [-1 Thresh], Gunnery {pools['gunnery']['pool']}d6 [{pools['gunnery']['pool'] + enl_delta}d6], "
                    f"Evasion {pools['evasion']['pool']}d6, Clearsight {pools['perception']['pool']}d6 [{pools['perception']['pool'] + enl_delta}d6], "
                    f"Stealth {pools['stealth']['pool']}d6)."
                ).strip()
            else:
                hw_sen = v_prof["hardware_sensor"]
                sensor_val = v_prof["augmented_sensor"]
                shared_auto = 9
                sneak_chunks = [
                    str(v.get("modifications") or ""),
                    str(v.get("accessories") or ""),
                ]
                for md in char_data.get("matrix_devices") or []:
                    if isinstance(md, dict):
                        sneak_chunks.append(
                            f"{md.get('name', '')} {md.get('notes', '')} {md.get('description', '')} {md.get('accessories', '')}"
                        )
                sneak_bonus = 2 if "sneak-sneak" in " ".join(sneak_chunks).lower() else 0
                stealth_auto = shared_auto + sneak_bonus
                sprite_pilot = 8
                sprite_mod = max(0, sprite_pilot - pilot_val)
                extra_autosofts = {
                    "clearsight": shared_auto,
                    "electronicWarfare": shared_auto,
                    "evasion": shared_auto,
                    "maneuvering": shared_auto,
                    "targeting": shared_auto,
                    "stealth": stealth_auto,
                }
                desc_str = (
                    f"{desc_str}\n"
                    f"Autonomous Secondary Drone (Own Pilot {pilot_val}, Sensor {hw_sen} +1 Sensor Upgrade = {sensor_val}; "
                    f"R{shared_auto} Shared Autosofts via RCC/Software Emulator, +{sneak_bonus} Stealth from Sneak-Sneak = {stealth_auto}): "
                    f"Piloting/Evasion {pilot_val + shared_auto}d6, Targeting/Clearsight {sensor_val + shared_auto}d6, Stealth {pilot_val + stealth_auto}d6. "
                    f"If Sprite-inhabited (set Pilot Mod +{sprite_mod} -> Pilot {sprite_pilot}): Piloting/Evasion {sprite_pilot + shared_auto}d6, Stealth {sprite_pilot + stealth_auto}d6."
                ).strip()

        out_veh = {
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
        out_veh.update(extra_autosofts)
        return out_veh

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
                "connection": connection,
                "favors": favors,
                "favor": favors,
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

    has_crimson_wasp = any("crimson wasp" in str(rw.get("name", "")).lower() for rw in ranged_items)
    has_red_fox = any("red fox" in str(rw.get("name", "")).lower() for rw in ranged_items)
    if is_ai and has_crimson_wasp:
        from sr6core.rules.vehicles import calculate_drone_action_pools

        maa_src = next(
            (d for d in (char_data.get("drones") or []) if isinstance(d, dict) and "man-at-arms" in str(d.get("name", "")).lower()),
            {"name": "Shiawase Man-at-Arms", "sensor": 2, "pilot": 2, "body": 10},
        )
        maa_pools = calculate_drone_action_pools(char_data, maa_src, mode="inhabited_override")
        wasp_pool = maa_pools["gunnery"]["pool"]
        # Tesla Coil is an internal cyberweapon without a Smartgun System (-1 vs smartlinked Targeting pool)
        has_smartlink_mod = any(
            isinstance(m, dict) and m.get("enabled", True) and m.get("id") == "smartlink_wireless"
            for m in (char_data.get("modifiers") or [])
        )
        tesla_pool = wasp_pool - (1 if has_smartlink_mod else 0)
        ranged_weapons_list.extend(
            [
                {
                    "name": "Crimson Wasp Array (2x Link-Fired)",
                    "skill": "exotic_weapons",
                    "pool": wasp_pool,
                    "damage": "7P*",
                    "attackRating": "22/20/17/12/-",
                    "mode": "SS",
                    "ammunition": "30",
                    "page": "FS 44",
                    "description": "Weapon: FS 44. Link Fire: DC 143 (+2 DV, +1 AR). Costs 1 major & 1 minor action to fire. 1 Wild Die. Decreases by 2P at Medium.",
                    "wifi": [],
                    "accessories": [{"name": "Smartgun System (Internal)"}, {"name": "Peak-Discharge Laser Battery Clips"}],
                },
                {
                    "name": "Tesla Coil (Straight)",
                    "skill": "exotic_weapons",
                    "pool": tesla_pool,
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
                    "name": "Crimson Wasp (single beam)",
                    "skill": "exotic_weapons",
                    "pool": wasp_pool,
                    "damage": "5P*",
                    "attackRating": "21/19/16/11/-",
                    "mode": "SS",
                    "ammunition": "30",
                    "page": "FS 44",
                    "description": "Weapon: FS 44. Independent eye mount. 1 Wild Die. Decreases to 3P at Medium.",
                    "wifi": [],
                    "accessories": [{"name": "Smartgun System (Internal)"}],
                },
                {
                    "name": "Tesla Coil (Wobbly)",
                    "skill": "exotic_weapons",
                    "pool": tesla_pool,
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
                    "pool": tesla_pool,
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
    elif is_ai and has_red_fox:
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
    elec_sk = next((s for s in skills_list if s["id"] == "electronics"), {})
    elec_rat = _parse_int(elec_sk.get("rating"), 5)
    has_cf_spec = any(
        "complex forms" in sp.get("name", "").lower() for sp in elec_sk.get("specializations", [])
    )
    cf_spec_b = 2 if has_cf_spec else 0
    crack_sk = next((s for s in skills_list if s["id"] == "cracking"), {})
    crack_rat = _parse_int(crack_sk.get("rating"), 5)
    has_cybercombat_spec = any(
        "cybercombat" in sp.get("name", "").lower() for sp in crack_sk.get("specializations", [])
    )
    cybercombat_spec_b = 2 if has_cybercombat_spec else 0
    res_focus_b = next(
        (
            _parse_int(i.get("rating"), 4)
            for i in items_list
            if "resonance focus" in i["name"].lower() and i.get("rating") not in ("", None)
        ),
        4 if is_ai else 0,
    )
    taz_b = (
        4
        if (
            char_data.get("sprite_powers")
            or any("sprite symbiosis" in e["name"].lower() for e in echoes_list)
        )
        else 0
    )
    ecm_b = (
        2
        if any(
            "ecm warrior" in str(a).lower()
            for md in (char_data.get("matrix_devices") or char_data.get("matrixItems") or [])
            if isinstance(md, dict)
            for a in (md.get("accessories") or [])
        )
        else (2 if is_ai else 0)
    )
    effective_res = res_eff or 9
    elec_cf_pool = elec_rat + cf_spec_b + effective_res + res_focus_b + taz_b
    crack_cf_pool = crack_rat + cybercombat_spec_b + effective_res + res_focus_b + taz_b + ecm_b

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
        char_cf_desc = re.sub(r"^Source:\s*[^|.\n]+[|.\n]*\s*", "", char_cf_desc, flags=re.IGNORECASE).strip()

        cf_infs = [str(x) for x in (cf.get("influences") or [])]
        if is_ai:
            if cf_name.lower() == "cyber spike":
                cf_infs.extend(
                    [
                        f"Electronics ({elec_rat}) + Complex Forms Spec (+{cf_spec_b}) + Resonance ({effective_res})",
                        f"Resonance Focus R{res_focus_b} (+{res_focus_b}d6)",
                        f"Taz Sprite Symbiosis (+{taz_b}d6)",
                        f"Total Pool: {elec_cf_pool}d6 vs Body + Essence (ECM Warrior II N/A; Electronics test)",
                    ]
                )
            elif cf_name.lower() == "resonance spike":
                cf_infs.extend(
                    [
                        f"Cracking ({crack_rat}) + Resonance ({effective_res})",
                        f"Resonance Focus R{res_focus_b} (+{res_focus_b}d6)",
                        f"Taz Sprite Symbiosis (+{taz_b}d6)",
                        f"ECM Warrior II TacApp (+{ecm_b}d6 Offensive Cracking)",
                        f"Total Pool: {crack_cf_pool}d6 vs Willpower + Firewall",
                    ]
                )
            else:
                cf_infs.extend(
                    [
                        f"Electronics ({elec_rat}) + Complex Forms Spec (+{cf_spec_b}) + Resonance ({effective_res})",
                        f"Resonance Focus R{res_focus_b} (+{res_focus_b}d6)",
                        f"Taz Sprite Symbiosis (+{taz_b}d6)",
                        f"Total Pool: {elec_cf_pool}d6",
                    ]
                )

        if rule_desc and len(char_cf_desc) < 90:
            cf_final_desc = rule_desc
        else:
            cf_final_desc = _combine_descriptions(char_cf_desc, rule_desc)

        complex_forms_list.append(
            {
                "name": cf_name,
                "duration": dur_out,
                "fading": fading_val,
                "page": page_str,
                "description": cf_final_desc,
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
        sp_infs = [f"Sprite Symbiosis (Taz — Companion Sprite R6, +{taz_b}d6)"]
        if is_ai and "death mark" in sp_name.lower():
            sp_infs = [
                f"Cracking ({crack_rat}) + Resonance ({effective_res})",
                f"Resonance Focus R{res_focus_b} (+{res_focus_b}d6)",
                f"Sprite Symbiosis (Taz — Companion Sprite R6, +{taz_b}d6)",
                f"ECM Warrior II TacApp (+{ecm_b}d6 Offensive Cracking)",
                f"Total Pool: {crack_cf_pool}d6 vs Intuition + Firewall",
            ]

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
        pname_base = re.sub(r"\s*\([^)]*\)", "", pname).strip().lower()
        cat_key = f"{pname_base} (autosoft)" if "autosoft" in pname.lower() else pname_base
        cat_page, cat_desc = _PROGRAM_CATALOG.get(
            cat_key,
            _PROGRAM_CATALOG.get(pname_base, ("", "")),
        )
        yaml_desc = str(
            prog.get("description") or prog.get("notes") or _strip_xml_tags(raw_xml) or ""
        ).strip()
        programs_out.append(
            {
                "name": pname,
                "page": _format_page(
                    prog.get("source") or (db_row or {}).get("source"),
                    prog.get("page") or _parse_xml_attr(raw_xml, "page"),
                    fallback_page=cat_page,
                ),
                "description": _combine_descriptions(yaml_desc, cat_desc),
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
                "page": "116, 124",
                "description": (
                    "Emergent Intelligence Living Persona: Base ASDF 3/5/3/5 increased by +4 augmented cap "
                    "(Resonance 9 [+1/+2/+2/+4] + Taz Sprite Symbiosis [+3/+2/+1/+0] + Toolbox [+1 DP]) to 7/9/7/9. "
                    "Matrix AR 16 (Attack 7 + Sleaze 9), Matrix DR 16 (DP 7 + FW 9; Designer Home Device raises Man-at-Arms Device Rating 2 -> 6 vs. DP 7 so opponents gain no Edge)."
                ),
                "accessories": [
                    {"name": "Resonance Focus (Bonded)", "rating": 4},
                    {"name": "Software Emulator Echo", "rating": submersion or res_eff or 9},
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
                "accessories": [],
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
                "accessories": [],
            },
        ]
        raw_matrix_devices = ai_matrix_devices + raw_matrix_devices

    for idx, dev in enumerate(raw_matrix_devices):
        if not isinstance(dev, dict):
            continue
        dname = str(dev.get("name") or "").strip()
        dname_norm = re.sub(r"\bmark\s+", "", dname.lower()).strip()
        if not dname or dname_norm in seen_matrix_devices:
            continue
        seen_matrix_devices.add(dname_norm)

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
        from sr6core.rules.vehicles import parse_vehicle_modifications, calculate_drone_action_pools

        sub_lvl = _parse_int(payload.get("submersion"), 9) or 9
        wil = attr_map.get("WILLPOWER", 6)
        log = attr_map.get("LOGIC", 4)
        intu = attr_map.get("INTUITION", 2)
        cha = attr_map.get("CHARISMA", 4)
        res_focus_r = next(
            (
                _parse_int(i.get("rating"), 4)
                for i in payload.get("items", [])
                if "resonance focus" in i["name"].lower() and i.get("rating") not in ("", None)
            ),
            4,
        )
        eff_res = resonance + res_focus_r
        nh_wil = max(0, resonance - wil)
        nh_log = max(0, resonance - log)
        nh_int = max(0, resonance - intu)
        nh_ji_mod = nh_int + nh_wil
        nh_log_init = nh_log + nh_int
        crack_sk = next((s["rating"] for s in payload.get("skills", []) if s["id"] == "cracking"), 5)
        elec_sk = next((s["rating"] for s in payload.get("skills", []) if s["id"] == "electronics"), 5)
        task_sk = next((s["rating"] for s in payload.get("skills", []) if s["id"] == "tasking"), 6)
        taz_b = 4
        ecm_b = 2
        overclock_b = 2
        hacking_p = crack_sk + 2 + eff_res + taz_b + ecm_b + overclock_b
        cybercombat_p = crack_sk + eff_res + taz_b + ecm_b + overclock_b
        hide_p = cybercombat_p
        software_p = elec_sk + 3 + eff_res + taz_b + overclock_b
        elec_base_p = elec_sk + eff_res + taz_b + overclock_b
        cf_p = elec_sk + 2 + eff_res + taz_b
        res_spike_p = crack_sk + eff_res + taz_b + ecm_b
        std_mdef_p = 9 + eff_res
        base_mdef_p = std_mdef_p + 3
        allin_mdef_p = base_mdef_p + sub_lvl + 7
        fade_compile_p = wil + cha + sub_lvl + res_focus_r
        fade_cf_p = wil + cha
        eng_mod_val = -(eff_res - log) + 4
        bio_mod_val = -(eff_res - log) + 4
        out_mod_val = -(eff_res - intu)

        maa_src = next(
            (d for d in (char_data.get("drones") or []) if isinstance(d, dict) and "man-at-arms" in str(d.get("name", "")).lower()),
            {"name": "Shiawase Man-at-Arms", "sensor": 2, "pilot": 2, "body": 10},
        )
        maa_prof = parse_vehicle_modifications(maa_src, char_data=char_data)
        maa_pools = calculate_drone_action_pools(char_data, maa_src, mode="inhabited_override")
        enl_delta = maa_prof["enlightened_sensor"] - maa_prof["augmented_sensor"]
        wasp_p = maa_pools["gunnery"]["pool"]
        wasp_p_enl = wasp_p + enl_delta
        tesla_p = wasp_p - 1
        tesla_p_enl = tesla_p + enl_delta
        clr_p = maa_pools["perception"]["pool"]
        clr_p_enl = clr_p + enl_delta
        plt_p = maa_pools["piloting"]["pool"]
        eva_p = maa_pools["evasion"]["pool"]
        stl_p = maa_pools["stealth"]["pool"]
        start_exotic = agi - 1
        wasp_mod = wasp_p - start_exotic
        wasp_mod_enl = wasp_p_enl - start_exotic
        tesla_mod = tesla_p - start_exotic
        tesla_mod_enl = tesla_p_enl - start_exotic
        lines.extend(
            [
                f"3. **Select Technomancer Stream (Matrix Tab)**: On the **Matrix** tab, select **`Technoshamans (Charisma)`** so Fade Resistance uses `Willpower + Charisma` (`{wil} + {cha} = {fade_cf_p}d6` base, `{fade_compile_p}d6` Compiling/Registering with Sprite Conduit +{sub_lvl} and Resonance Focus +{res_focus_r}).",
                "4. **Enable Overclock (Matrix Tab)**: Check the **`Overclock`** toggle on the **Matrix** tab so Roll20's native Matrix Action buttons automatically add **`+2d6`** (`@{matrix_overclock}*2`) and **`+1 Wild Die`**.",
                "",
                "---",
                "",
                "## 2. Post-Flight Adjustments (Native Roll20 Sheet Sync)",
                "",
                "Every time you re-import `reiko_roll20.json`, Roll20's `clean()` wipes repeating rows and restores default values. Apply these adjustments so native sheet buttons, GM opposition links, and custom Abilities all match:",
                "",
                "### 1) Skill Modifiers & Overclock (`Skills` & `Matrix` Tabs)",
                "Roll20's `repeating_effects` cannot directly modify active skill ranks (`Cracking`, `Electronics`, `Tasking`), **but setting each skill's `Mod` box (`x` settings on the Skills tab) DOES update every native Matrix Action button, Complex Form, and Sprite roll!**",
                "",
                f"Assuming **Effects 1–4** below are active (`RES {eff_res}`, `LOG {eff_res}`, `INT {eff_res}`, `WIL {wil + nh_wil + res_focus_r}`) and **`Overclock` is checked (`+2d6`, `1w`)** on the Matrix tab:",
                "",
                "- **Matrix Skills (`Skills` Tab -> Settings `x` -> `Mod`)**:",
                f"  - **`Cracking`**: Set **`Mod`** to **`+{taz_b + ecm_b}`** (`+4` Taz Symbiosis + `+2` ECM Warrior II = effective rating `{crack_sk + taz_b + ecm_b}`).",
                f"  - **`Electronics`**: Set **`Mod`** to **`+{taz_b}`** (`+4` Taz Symbiosis = effective rating `{elec_sk + taz_b}`).",
                "  - **`Tasking`**: Keep **`Mod`** at **`0`** (rating `6`; **no ally sprite can learn or assist with Tasking**).",
                "- **Native Matrix Action Dropdown (`Training Level?`) Lookup Table**:",
                f"  - **Hacking Actions** (`Backdoor Entry`, `Brute Force`, `Crack File`, `Probe`, `Spoof Command`): choose **`Specialized (+2)`** -> **`{hacking_p}d6 (1w)`**",
                f"  - **Cybercombat / EW Actions** (`Data Spike`, `Snoop`, `Tar Pit`, `Jam Signals`, `Disarm Data Bomb`, `Crash Program`, `Check OS`, `Hide`): choose **`Trained (0)`** -> **`{cybercombat_p}d6 (1w)`** *(note: `Hide` is defensive Cracking; subtract 2 -> `24d6 (1w)` if GM excludes `ECM Warrior II`)*",
                f"  - **Software Actions** (`Edit File`, `Encrypt File`, `Hash Check`, `Erase Matrix Signature`): choose **`Expertise (+3)`** -> **`{software_p}d6 (1w)`**",
                f"  - **Computer / Hardware / Search** (`Control Device`, `Matrix Perception`, `Matrix Search`, `Format Device`, `Trace Icon`, `Reboot Device`): choose **`Trained (0)`** -> **`{elec_base_p}d6 (1w)`**",
                f"- **Meatspace Emulated Skills (`Skills` Tab `Mod` to cancel Matrix `LOG {eff_res}` / `INT {eff_res}`)**:",
                f"  - **`Engineering (Drones)`**: Set **`Mod`** to **`{eng_mod_val}`** (`-{eff_res - log}` LOG offset + `4` Taz = **`15d6`** pool; use **`-1`** if `Resonance Focus` Effect is toggled off).",
                f"  - **`Biotech`**: Set **`Mod`** to **`{bio_mod_val}`** (`-{eff_res - log}` LOG offset + `4` Mobile Medic = **`15d6`** pool; use **`-1`** if `Resonance Focus` Effect is toggled off).",
                f"  - **`Outdoors (Navigation)`**: Set **`Mod`** to **`{out_mod_val}`** (`-{eff_res - intu}` INT offset = **`9d6`** pool; use **`-7`** if `Resonance Focus` Effect is toggled off).",
                "",
                "### 2) Complex Form Rolls (`Matrix` Tab)",
                "Open settings (`x`) on each Complex Form row:",
                f"- **Electronics Forms** (`Puppeteer`, `Cleaner`, `Diffusion of Firewall`, `Technoregeneration`, `Resonance Wires`, `Enlighten Automaton`, `Cyber Spike`): Skill = **`Electronics`** (effective `{elec_sk + taz_b}` w/ `Mod +4`), check **Specialization (`+2`)**, Modifier = **`0`** (or **`+{res_focus_r}`** if `Resonance Focus` Effect is toggled off) -> **`{cf_p}d6`** (`6` bought hits).",
                f"- **Resonance Spike** (`Cracking`): Skill = **`Cracking`** (effective `{crack_sk + taz_b + ecm_b}` w/ `Mod +6`), leave Specialization unchecked (`0`), Modifier = **`0`** (or **`+{res_focus_r}`** if `Resonance Focus` Effect is toggled off) -> **`{res_spike_p}d6`** (`6` bought hits).",
                "",
                "### 3) Drone Autosofts (`Vehicles` Tab)",
                "- **Inhabited Man-at-Arms Autosofts** (Emulated Rating 7 + 4 Sprite Symbiosis + **1 Pilot Origins** = **`12`** base effective autosoft/rig contribution; click power toggle ON):",
                "  - **Clearsight**: `12` (`7` Clearsight + `4` Taz + `1` Pilot Origins; click power toggle ON)",
                "  - **Evasion**: `12` (`7` Evasion + `4` Taz + `1` Pilot Origins; click power toggle ON)",
                "  - **Maneuvering**: `11` (`7` Maneuvering + `3` Taz Diagnosis + `1` Pilot Origins, **-1 Threshold**; click power toggle ON)",
                "  - **Stealth**: `14` (`7` Stealth + `4` Taz + `2` Sneak-Sneak + `1` Pilot Origins; click power toggle ON)",
                "  - **Targeting (Crimson Wasps)**: `13` (`7` Targeting + `4` Taz + `1` Smartlink + `1` Pilot Origins; click power toggle ON)",
                "  - **Targeting (Tesla Coil)**: `12` (`7` Targeting + `4` Taz + `1` Pilot Origins; un-smartlinked)",
                "- **Shiawase Man-at-Arms (Overridden Drone Body)**:",
                f"  - **Pilot Mod**: `+{res_focus_r}` (Resonance Focus R{res_focus_r} -> Effective Pilot {maa_prof['inhabited_pilot'] + res_focus_r})",
                f"  - **Body Mod**: `+{maa_prof['augmented_body'] - maa_prof['base_body']}` (Reinforced Frame -> Body {maa_prof['augmented_body']})",
                f"  - **Sensor Mod**: `+{maa_prof['augmented_sensor'] - maa_prof['hardware_sensor']}` Passive (Hardware {maa_prof['hardware_sensor']} + 1 Sensor Upgrade + 1 Home Device -> Sensor {maa_prof['augmented_sensor']}), or **`+{maa_prof['enlightened_sensor'] - maa_prof['hardware_sensor']}`** with **Enlighten Automaton** (`+{enl_delta}` -> Sensor {maa_prof['enlightened_sensor']})",
                "- **Secondary Drones** (`Sky Commander`, `MCT Hornet`, `MCT Gnat` — Autonomous Pilot, never inhabited by Reiko):",
                "  - **Pilot**: Own Pilot (`3` Sky Commander, `2` Hornet, `2` Gnat). If a Sprite inhabits the drone, set **Pilot Mod** to **`+5`** (`Sky Commander`) or **`+6`** (`Hornet`/`Gnat`) for **Pilot `8`** (`17d6` Piloting/Evasion, `19d6` Stealth).",
                "  - **Sensor**: Hardware + `1` (`Sensor Upgrade` quality -> Sky Commander `6`, Hornet `3`, Gnat `2`).",
                "  - **Autosofts**: `9` (`Clearsight 9`, `Electronic Warfare 9`, `Evasion 9`, `Maneuvering 9`, `Targeting 9` shared via RCC/Software tags) and **Stealth `11`** (`9` + `2` from `Sneak-Sneak`).",
                "",
                "### 4) Weapon Pools (`Arms` & `Core` Tabs)",
                f"The 5 Man-at-Arms weapons are exported using skill **`Exotic Weapons`** so your `Engineering (Drones)` skill doesn't inflate your weapon pools. Starting Roll20 pool = `Agility ({agi}) + Exotic Weapons (-1 unskilled) = {start_exotic}`:",
                f"- **Crimson Wasps (Smartlinked)**: `Targeting (7) + Sensor ({maa_prof['augmented_sensor']}) + Taz (4) + Pilot Origins (1) + Smartlink (1) = {wasp_p}d6` Passive (`{wasp_p_enl}d6` w/ Enlighten Automaton) -> Set Mod to **`+{wasp_mod}`** (`+{wasp_mod_enl}` sustained).",
                f"- **Tesla Coil (No Smartlink)**: `Targeting (7) + Sensor ({maa_prof['augmented_sensor']}) + Taz (4) + Pilot Origins (1) = {tesla_p}d6` Passive (`{tesla_p_enl}d6` w/ Enlighten Automaton) -> Set Mod to **`+{tesla_mod}`** (`+{tesla_mod_enl}` sustained).",
                "",
                "- Click the settings toggle (`x`) on each of the 5 weapons:",
                f"  1. **Crimson Wasp Array (2x Link-Fired)**: Set **Modifier** to **`+{wasp_mod}`** (Pool = **{wasp_p}d6** Passive / **{wasp_p_enl}d6** Sustained, 7P* DV [SS] / 8P* DV [SA], 1 Wild Die, AR 22/20/17/12/-).",
                f"  2. **Single Crimson Wasp (Eye Mount)**: Set **Modifier** to **`+{wasp_mod}`** (Pool = **{wasp_p}d6** Passive / **{wasp_p_enl}d6** Sustained, 5P* DV [SS] / 6P* DV [SA], 1 Wild Die, AR 21/19/16/11/-).",
                f"  3. **Tesla Coil (Straight Line)**: Set **Modifier** to **`+{tesla_mod}`** (Pool = **{tesla_p}d6** Passive / **{tesla_p_enl}d6** Sustained, 5S(e) DV, AR 10/12/-/-/-).",
                f"  4. **Tesla Coil (Wobbly Cone)**: Set **Modifier** to **`+{tesla_mod}`** (Pool = **{tesla_p}d6** Passive / **{tesla_p_enl}d6** Sustained, 4S(e) DV, Cone 20m x 3m base, Apex 8.58°).",
                f"  5. **Tesla Coil (Sweep Cone)**: Set **Modifier** to **`+{tesla_mod}`** (Pool = **{tesla_p}d6** Passive / **{tesla_p_enl}d6** Sustained, 2S(e) DV, Cone 20m x 10m base, Apex 28.07°).",
            ]
        )
    lines.extend(
        [
            "",
            "---",
            "",
            "## 3. One-Time Setup: Copy-Paste Effects (`Core Tab -> Attributes -> Effects`)",
            "",
            "> **Clean Modular Effects (`repeating_effects` survive JSON re-imports)**:",
            "> Separating modifiers into 4 dedicated Effects lets you inspect every single active source at a glance and toggle any piece (such as the bonded Resonance Focus) independently without breaking ASDF, Stun, derived mental tests, or Initiative.",
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
                "### Effect 1: `Living Persona ASDF & Overclocking`",
                "- **Duration**: `Permanent` | **Source**: `Living Persona (7/9/7/9) + Designer Home Device + Overclocking`",
                "- **What it does**: Sets Living Persona ASDF to **`7/9/7/9`** (`attack: 4+3=7`, `sleaze: 2+7=9`, `data_processing: 4+3=7`, `firewall: 6+3=9`), keeping **Matrix DR at `16`** (`DP 7 + FW 9`) while adding **`+1d6` Hot-Sim Initiative Dice** (`Overclocking`). *(Designer Home Device raises Man-at-Arms physical Device Rating `2 -> 6` vs. DP `7` for Edge comparison, rather than adding `+4` to Matrix DR.)*",
                "- **Modifications** *(copy-paste as a single line)*:",
                "```text",
                "attack_modifier: +3, sleaze_modifier: +7, data_processing_modifier: +3, firewall_modifier: +3, hot_sim_initiative_dice_mod: +1",
                "```",
                "",
                f"### Effect 2: `Natural Hacker (Subikari Stream — RES {resonance} Sub)`",
                "- **Duration**: `Permanent` | **Source**: `Natural Hacker (H&S p.83)`",
                f"- **What it does**: Replaces `Willpower` (`{wil} -> {resonance}`, `+{nh_wil}`), `Logic` (`{log} -> {resonance}`, `+{nh_log}`), and `Intuition` (`{intu} -> {resonance}`, `+{nh_int}`) with `Resonance {resonance}` for Matrix actions and defense tests (`WIL + FW`, `WIL + SLZ`, `Jack Out`). Cleanly offsets ASDF (`-{nh_wil} FW`, `-{nh_log} DP`, `-{nh_int} SLZ`), Stun boxes (`-2`), Composure (`-{nh_wil}`), Judge Intentions (`-{nh_ji_mod}`), Lift/Carry (`-{nh_wil}`), Compiling Fade (`-{nh_wil}`), Memory (`-{nh_log_init}`), and all 4 Initiative buttons (`-{nh_int}` / `-{nh_log_init}` Astral) so meatspace stats stay exact.",
                "- **Modifications** *(copy-paste as a single line)*:",
                "```text",
                f"willpower_modifier: +{nh_wil}, logic_modifier: +{nh_log}, intuition_modifier: +{nh_int}, firewall_modifier: -{nh_wil}, data_processing_modifier: -{nh_log}, sleaze_modifier: -{nh_int}, stun_modifier: -2, composure_modifier: -{nh_wil}, judge_intentions_modifier: -{nh_ji_mod}, lift_carry_modifier: -{nh_wil}, fade_compiling_modifier: -{nh_wil}, memory_modifier: -{nh_log_init}, initiative_mod: -{nh_int}, astral_initiative_mod: -{nh_log_init}, matrix_initiative_mod: -{nh_int}, cold_sim_initiative_mod: -{nh_int}, hot_sim_initiative_mod: -{nh_int}",
                "```",
                "",
                f"### Effect 3: `Resonance Focus (Rating {res_focus_r} — Bonded Data Structure)`",
                "- **Duration**: `Bonded (Toggleable)` | **Source**: `Resonance Focus R4 (Man-at-Arms)`",
                f"- **What it does**: Adds **`+{res_focus_r}` Resonance** (`{resonance} -> {eff_res}`), **`+{res_focus_r}` Willpower** (`{resonance} -> {eff_res}` for Matrix/Full Defense vs `WIL + FW`/`WIL + SLZ`), **`+{res_focus_r}` Logic**, and **`+{res_focus_r}` Intuition** (`{resonance} -> {eff_res}` for Natural Hacker), while offsetting ASDF (`-{res_focus_r}`), Stun (`-2`), `Composure` (`-{res_focus_r}`), `Judge Intentions` (`-{res_focus_r * 2}`), `Memory` (`-{res_focus_r * 2}`), `Lift/Carry` (`-{res_focus_r}`), Initiatives (`-{res_focus_r}` / `-{res_focus_r * 2}` Astral), and `fade_compiling_modifier` (`-{res_focus_r}`). Toggle OFF if unbonded — zero residual drift!",
                "- **Modifications** *(copy-paste as a single line)*:",
                "```text",
                f"resonance_modifier: +{res_focus_r}, willpower_modifier: +{res_focus_r}, logic_modifier: +{res_focus_r}, intuition_modifier: +{res_focus_r}, firewall_modifier: -{res_focus_r}, data_processing_modifier: -{res_focus_r}, sleaze_modifier: -{res_focus_r}, stun_modifier: -2, composure_modifier: -{res_focus_r}, judge_intentions_modifier: -{res_focus_r * 2}, memory_modifier: -{res_focus_r * 2}, lift_carry_modifier: -{res_focus_r}, initiative_mod: -{res_focus_r}, astral_initiative_mod: -{res_focus_r * 2}, matrix_initiative_mod: -{res_focus_r}, cold_sim_initiative_mod: -{res_focus_r}, hot_sim_initiative_mod: -{res_focus_r}, fade_compiling_modifier: -{res_focus_r}",
                "```",
                "",
                "### Effect 4: `Sprite Conduit, Taz Symbiosis & Technoshaman`",
                "- **Duration**: `Permanent / Symbiosis` | **Source**: `Sprite Conduit (Sub 9) + Resonance Focus R4 + Technoshamans`",
                f"- **What it does**: Adds **`+13` Compiling/Registering Fade Resistance** (`+9` Sprite Conduit + `+4` Resonance Focus, making `WIL 6 + CHA 4 + 13 = {fade_compile_p}d6` on `~fade_compiling` chat buttons) and **`+1` Sprite Resist DV** (`Technoshamans`). *(Note: Roll20's direct Submersion `Resist Fade` button omits `fade_compiling_modifier`, so use Section 4's `Fade-Resistance` Ability for direct one-click Fade rolls.)*",
                "- **Modifications** *(copy-paste as a single line)*:",
                "```text",
                f"fade_compiling_modifier: +{sub_lvl + res_focus_r}, sprite_resist_dv_modifier: +1",
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

    def _r20_ability(
        base: str,
        pool_expr: str,
        dice_count_expr: Optional[str] = None,
        wild_die: Any = False,
        overclock: Any = False,
        fade: Optional[int] = None,
        desc: str = "",
        tip: str = "",
        opp: str = "",
        include_wounds: bool = True,
        gm_whisper: bool = True,
    ) -> str:
        """Build a Roll20 `rolls-computed` Ability macro with explicit pool/wilddie rendering."""
        prefix = "@{gm_toggle} " if gm_whisper else ""
        wounds_part = "+@{wounds_toggle}" if include_wounds else ""
        full_pool = f"({pool_expr}{wounds_part}+@{{modifiers_toggle}}+@{{edge_toggle}})"
        if dice_count_expr is not None:
            roll_cnt = f"({dice_count_expr}{wounds_part}+@{{modifiers_toggle}}+@{{edge_toggle}})"
        elif wild_die is True:
            roll_cnt = f"(({pool_expr})-1{wounds_part}+@{{modifiers_toggle}}+@{{edge_toggle}})"
        else:
            roll_cnt = full_pool

        parts = [
            f"{prefix}&{{template:rolls-computed}}",
            "{{header=@{character_name}}}",
            f"{{{{base={base}}}}}",
            f"{{{{dicepool=[[{full_pool}]]}}}}",
            f"{{{{dice=[[{roll_cnt}d6>5@{{explode_toggle}}cs>5cf<[[(1+@{{bad_luck}})]]]]}}}}",
            "{{mod=[[@{modifiers_toggle}]]}}",
        ]
        if include_wounds:
            parts.append("{{wound=[[@{wounds_toggle}]]}}")
        parts.append("{{edge=[[@{edge_toggle}]]}}")
        if isinstance(wild_die, str):
            parts.append(f"{{{{wilddie=[[{wild_die}]]}}}}")
        elif wild_die:
            parts.append("{{wilddie=[[1+@{wild_die}]]}}")
        else:
            parts.append("{{wilddie=[[@{wild_die}]]}}")
        parts.append("{{wilddie_dice=[[1d6@{explode_toggle}cs>5cf<1]]}}")
        if isinstance(overclock, str):
            parts.append(f"{{{{overclock=[[{overclock}]]}}}}")
        elif overclock:
            parts.append("{{overclock=[[2]]}}")
        if fade is not None:
            parts.append(f"{{{{fade=[[{fade}]]}}}}")
        if desc:
            parts.append(f"{{{{desc={desc}}}}}")
        if tip:
            parts.append(f"{{{{tip={tip}}}}}")
        if opp:
            parts.append(f"{{{{opp={opp}}}}}")
        return "".join(parts)

    if magic > 0:
        lines.extend(
            [
                "",
                "### Leadership / Command Presence Roll (`Influence + Charisma + 2`)",
                "```text",
                f"@{{{c_ref}|gm_toggle}} &{{template:rolls-computed}}{{{{header=@{{{c_ref}|character_name}}}}}}{{{{base=Influence (Leadership + Command Presence)}}}}{{{{dicepool=[[(@{{{c_ref}|influence}}+@{{{c_ref}|charisma}}+2+@{{{c_ref}|wounds_toggle}}+@{{{c_ref}|modifiers_toggle}}+@{{{c_ref}|edge_toggle}})]]}}}}{{{{dice=[[(@{{{c_ref}|influence}}+@{{{c_ref}|charisma}}+2+@{{{c_ref}|wounds_toggle}}+@{{{c_ref}|modifiers_toggle}}+@{{{c_ref}|edge_toggle}})d6>5@{{{c_ref}|explode_toggle}}cs>5cf<[[(1+@{{{c_ref}|bad_luck}})]]]]}}}}{{{{mod=[[@{{{c_ref}|modifiers_toggle}}]]}}}}{{{{wound=[[@{{{c_ref}|wounds_toggle}}]]}}}}{{{{edge=[[@{{{c_ref}|edge_toggle}}]]}}}}{{{{desc=Wise Warrior (-1 Edge cost, min 1) + Command Presence (+2d6, +1 Edge) + Inspire Competence}}}}",
                "```",
                "",
                "### Con / Cosmetic Control Disguise Roll (`Con + Charisma`)",
                "```text",
                f"@{{{c_ref}|gm_toggle}} &{{template:rolls-computed}}{{{{header=@{{{c_ref}|character_name}}}}}}{{{{base=Con (Cosmetic Control R2)}}}}{{{{dicepool=[[(@{{{c_ref}|con}}+@{{{c_ref}|charisma}}+@{{{c_ref}|wounds_toggle}}+@{{{c_ref}|modifiers_toggle}}+@{{{c_ref}|edge_toggle}})]]}}}}{{{{dice=[[(@{{{c_ref}|con}}+@{{{c_ref}|charisma}}+@{{{c_ref}|wounds_toggle}}+@{{{c_ref}|modifiers_toggle}}+@{{{c_ref}|edge_toggle}})d6>5@{{{c_ref}|explode_toggle}}cs>5cf<[[(1+@{{{c_ref}|bad_luck}})]]]]}}}}{{{{mod=[[@{{{c_ref}|modifiers_toggle}}]]}}}}{{{{wound=[[@{{{c_ref}|wounds_toggle}}]]}}}}{{{{edge=[[@{{{c_ref}|edge_toggle}}]]}}}}{{{{desc=Cosmetic Control R2 (-1 Edge boost cost on Con tests) + Nanopaste/Nanocosmetics}}}}",
                "```",
                "",
                "### Spellcasting (`Sorcery + Magic + Specialization +2 + Wise Warrior +1`)",
                "```text",
                f"@{{{c_ref}|gm_toggle}} &{{template:rolls-computed}}{{{{header=@{{{c_ref}|character_name}}}}}}{{{{base=Spellcasting (Sorcery + Magic)}}}}{{{{dicepool=[[(@{{{c_ref}|sorcery}}+@{{{c_ref}|magic}}+3+@{{{c_ref}|wounds_toggle}}+@{{{c_ref}|modifiers_toggle}}+@{{{c_ref}|edge_toggle}})]]}}}}{{{{dice=[[(@{{{c_ref}|sorcery}}+@{{{c_ref}|magic}}+3+@{{{c_ref}|wounds_toggle}}+@{{{c_ref}|modifiers_toggle}}+@{{{c_ref}|edge_toggle}})d6>5@{{{c_ref}|explode_toggle}}cs>5cf<[[(1+@{{{c_ref}|bad_luck}})]]]]}}}}{{{{mod=[[@{{{c_ref}|modifiers_toggle}}]]}}}}{{{{wound=[[@{{{c_ref}|wounds_toggle}}]]}}}}{{{{edge=[[@{{{c_ref}|edge_toggle}}]]}}}}{{{{desc=Includes +2 Spellcasting Spec & +1 Improved Ability (Sorcery)}}}}",
                "```",
                "",
                "### Drain Resistance (`Willpower + Charisma`)",
                "```text",
                f"@{{{c_ref}|gm_toggle}} &{{template:rolls-computed}}{{{{header=@{{{c_ref}|character_name}}}}}}{{{{base=Drain Resistance (WIL + CHA)}}}}{{{{dicepool=[[(@{{{c_ref}|willpower}}+@{{{c_ref}|charisma}}+@{{{c_ref}|modifiers_toggle}}+@{{{c_ref}|edge_toggle}})]]}}}}{{{{dice=[[(@{{{c_ref}|willpower}}+@{{{c_ref}|charisma}}+@{{{c_ref}|modifiers_toggle}}+@{{{c_ref}|edge_toggle}})d6>5@{{{c_ref}|explode_toggle}}cs>5cf<[[(1+@{{{c_ref}|bad_luck}})]]]]}}}}{{{{mod=[[@{{{c_ref}|modifiers_toggle}}]]}}}}{{{{edge=[[@{{{c_ref}|edge_toggle}}]]}}}}{{{{desc=Shinto / Musok Tradition Drain Resistance}}}}",
                "```",
            ]
        )

    if resonance > 0:
        compile_p = task_sk + 2 + eff_res
        compile_link_p = compile_p + 2
        register_p = compile_p
        ew_q = (
            f"?{{EW Action?"
            f"|Snoop ({cybercombat_p}d6 + 1w),{cybercombat_p}"
            f"|Hide w/ ECM II ({cybercombat_p}d6 + 1w),{cybercombat_p}"
            f"|Hide Defensive ({cybercombat_p - 2}d6 + 1w),{cybercombat_p - 2}"
            f"}}"
        )
        atk_base_p = min(res_spike_p, cf_p)
        atk_delta = cybercombat_p - atk_base_p
        atk_q = (
            f"?{{Matrix Attack?"
            f"|Data Spike — Overclock & Fork ({cybercombat_p}d6 + 1w),1"
            f"|Resonance Spike — Complex Form ({res_spike_p}d6),0"
            f"|Cyber Spike — Complex Form ({cf_p}d6),0"
            f"}}"
        )
        task_q = (
            f"?{{Tasking Action?"
            f"|Compile Sprite ({compile_link_p}d6 w/ +2 Resonance Link),2"
            f"|Register Sprite ({register_p}d6),0"
            f"}}"
        )
        fade_q = (
            f"?{{Fade Type?"
            f"|Compiling / Registering ({fade_compile_p}d6 w/ Conduit +{sub_lvl} & Focus +{res_focus_r}),{fade_compile_p}"
            f"|Complex Form Threading ({fade_cf_p}d6 = WIL + CHA),{fade_cf_p}"
            f"}}"
        )
        mdef_q = (
            f"?{{Defense Mode?"
            f"|All-In Full Matrix Defense ({allin_mdef_p}d6 -> 10 Bought Hits),{allin_mdef_p}"
            f"|Base Full Matrix Defense w/ PA R6 ({base_mdef_p}d6 -> 6 Bought Hits),{base_mdef_p}"
            f"|Standard Matrix Defense ({std_mdef_p}d6 -> 5 Bought Hits),{std_mdef_p}"
            f"|Matrix Soak: FW + Armor (11d6 / 13d6 vs Biofeedback),11"
            f"}}"
        )
        meat_q = (
            f"?{{Meatspace Skill?"
            f"|Engineering: Drones (15d6),15"
            f"|Biotech: First Aid & Mobile Medic (15d6),15"
            f"|Outdoors: Navigation (9d6),9"
            f"}}"
        )

        lines.extend(
            [
                "",
                f"### `Matrix-Hacking` (`{hacking_p}d6 [1w]`: Backdoor Entry | Known Exploit Backdoor Entry | Probe | Spoof Command)",
                "```text",
                _r20_ability(
                    base="Matrix Hacking: ?{Hacking Action?|Backdoor Entry|Known Exploit Backdoor Entry|Probe|Spoof Command}",
                    pool_expr=f"{hacking_p}",
                    wild_die=True,
                    overclock=True,
                    desc="(Illegal), AR 16. Backdoor/Probe: Major/Extended, Admin access. Known Exploit Backdoor (H&S p.30): Major, no prior Probe needed; you cannot gain/spend Edge; target +1 Edge; failure raises OS without immediate alarm. Spoof: Major vs Pilot/FW.",
                    tip=f"Pool {hacking_p}d6 ({hacking_p - 1}d6 + 1w): Cracking ({crack_sk}) + Hacking Spec (+2) + RES ({resonance}) + Focus (+{res_focus_r}) + Taz (+{taz_b}) + ECM Warrior II (+{ecm_b}) + Overclock (+{overclock_b}, 1w).",
                    opp="Backdoor/Probe: [Willpower + Firewall](~selected|matrixresist_w_f) | [Firewall x2](~selected|matrixresist_f_f) / Spoof: [DP + Firewall](~selected|matrixresist_dp_f)",
                ),
                "```",
                "",
                f"### `Matrix-Electronic-Warfare` (`{cybercombat_p}d6 [1w]` / `{cybercombat_p - 2}d6 [1w]`: Hide | Snoop)",
                "```text",
                _r20_ability(
                    base=f"Matrix Electronic Warfare ({cybercombat_p}d6 Snoop/Hide | {cybercombat_p - 2}d6 Defensive Hide)",
                    pool_expr=ew_q,
                    dice_count_expr=f"({ew_q})-1",
                    wild_die=True,
                    overclock=True,
                    desc="(Illegal), CRB p.182, 184. Hide: Major/Minor evasive concealment. Snoop: Major, intercept comms (Net Hits min).",
                    tip=f"Cracking ({crack_sk}) + RES ({resonance}) + Focus (+{res_focus_r}) + Taz (+{taz_b}) + Overclock (+{overclock_b}, 1w) = {cybercombat_p - 2}d6 (+2 ECM Warrior II = {cybercombat_p}d6).",
                    opp="Hide: [Intuition + Data Processing](~selected|matrixresist_int_dp) | [DP + Sleaze](~selected|matrixresist_dp_s) / Snoop: [Willpower + Firewall](~selected|matrixresist_w_f)",
                ),
                "```",
                "",
                f"### `Matrix-Computer` (`{elec_base_p}d6 [1w]`: Matrix Perception | Threat Analysis)",
                "```text",
                _r20_ability(
                    base="Matrix Computer: ?{Computer Action?|Matrix Perception|Threat Analysis}",
                    pool_expr=f"{elec_base_p}",
                    wild_die=True,
                    overclock=True,
                    desc="(Legal). Matrix Perception (Minor/Major): spot hidden icons/files, CRB p.182. Threat Analysis (H&S p.31, Major): allies with AR access on PAN (up to DP 7 users) gain hits as Defense bonus dice until next turn.",
                    tip=f"Pool {elec_base_p}d6 ({elec_base_p - 1}d6 + 1w): Electronics ({elec_sk}) + RES ({resonance}) + Focus (+{res_focus_r}) + Taz (+{taz_b}) + Overclock (+{overclock_b}, 1w).",
                    opp="Perception (Silent): [Willpower + Sleaze](~selected|matrixresist_w_s) | Threat Analysis: Unopposed",
                ),
                "```",
                "",
                f"### `Matrix-Hardware` (`{elec_base_p}d6 [1w]`: Squelch | Subvert Infrastructure)",
                "```text",
                _r20_ability(
                    base="Matrix Hardware: ?{Hardware Action?|Squelch|Subvert Infrastructure}",
                    pool_expr=f"{elec_base_p}",
                    wild_die=True,
                    overclock=True,
                    desc="(Illegal, H&S p.31). Squelch (Minor, Outsider): prevents target device calls/transmissions for (Net Hits) min. Subvert Infrastructure (Major sustain, Admin): control 1 group of similar slaved simple devices per net hit (not an attack).",
                    tip=f"Pool {elec_base_p}d6 ({elec_base_p - 1}d6 + 1w): Electronics ({elec_sk}) + RES ({resonance}) + Focus (+{res_focus_r}) + Taz (+{taz_b}) + Overclock (+{overclock_b}, 1w).",
                    opp="Squelch: [Intuition + Sleaze](~selected|matrixresist_int_s) / [Sleaze x2](~selected|matrixresist_s_s) | Subvert: [Willpower + Firewall](~selected|matrixresist_w_f)",
                ),
                "```",
                "",
                f"### `Matrix-Attack` (`Data Spike {cybercombat_p}d6 [1w]` w/ Overclock & Fork | `Resonance Spike {res_spike_p}d6` | `Cyber Spike {cf_p}d6`)",
                "```text",
                _r20_ability(
                    base=f"Matrix Attack (Data Spike {cybercombat_p}d6+1w | Resonance/Cyber Spike {atk_base_p}d6)",
                    pool_expr=f"{atk_base_p}+{atk_delta}*{atk_q}",
                    dice_count_expr=f"{atk_base_p}+{atk_q}",
                    wild_die=f"{atk_q}+@{{wild_die}}",
                    overclock=f"{atk_delta}*{atk_q}",
                    desc="(Illegal), AR 16. Data Spike (CRB p.181, Fork up to 2 targets): Base DV 4 + net hits. | Resonance Spike (CF, Instant): Net hits = Matrix DV. | Cyber Spike (CF, Sustained, F2): Matrix damage vs target.",
                    tip=f"Data Spike ({cybercombat_p}d6+1w) includes Overclock +2 (+1w) & ECM Warrior II (+2). Resonance Spike uses Cracking ({crack_sk}); Cyber Spike uses Electronics ({elec_sk}) + CF Spec (+2); both have no Overclock.",
                    opp="Data Spike: [DP + Firewall](~selected|matrixresist_dp_f) | Resonance Spike: [Willpower + Firewall](~selected|matrixresist_w_f) | Cyber Spike: [Body + Essence](~selected|soak)",
                ),
                "```",
                "",
                f"### `Erase-Matrix-Signature` (`{software_p}d6 [1w]` Standalone Reminder)",
                "```text",
                _r20_ability(
                    base="Erase Matrix Signature (Software Expertise)",
                    pool_expr=f"{software_p}",
                    wild_die=True,
                    overclock=True,
                    desc="(Legal), Major Action, CRB p.181. Scrubs a Matrix signature (1 hit erases standard signature; complex forms/sprites require hits > Rating).",
                    tip=f"Pool {software_p}d6 ({software_p - 1}d6 + 1w): Electronics ({elec_sk}) + Software Expertise (+3) + RES ({resonance}) + Focus (+{res_focus_r}) + Taz (+{taz_b}) + Overclock (+{overclock_b}, 1w).",
                    opp="Threshold (Signature Rating)",
                ),
                "```",
                "",
                f"### `Cleaner` (`{cf_p}d6` Complex Form — Reduce OS & Autoroll Fade)",
                "```text",
                _r20_ability(
                    base="Cleaner (Complex Form — Reduce OS)",
                    pool_expr=f"{cf_p}",
                    wild_die=False,
                    overclock=False,
                    fade=2,
                    desc="(Complex Form), Permanent, Fade 2, CRB p.190. Each hit reduces your Overwatch Score by 1.",
                    tip=f"Pool {cf_p}d6: Electronics ({elec_sk}) + Complex Forms Spec (+2) + RES ({resonance}) + Focus (+{res_focus_r}) + Taz (+{taz_b}). Fade 2.",
                ),
                _r20_ability(
                    base="Resist Fade: Cleaner (Fade 2)",
                    pool_expr=f"{fade_cf_p}",
                    wild_die=False,
                    overclock=False,
                    include_wounds=False,
                    desc=f"Fade DV 2 (Drain: Stun damage if hits < 2). Technoshamans: WIL ({wil}) + CHA ({cha}) = {fade_cf_p}d6 (ignores wound penalties).",
                ),
                "```",
                "",
                f"### `Oracle-Search` (`{elec_base_p}d6 [1w]` -> `{elec_base_p - 1}d6 [1w]` 2-Major-Action / 1-Round Extended Search)",
                "```text",
                _r20_ability(
                    base="Oracle Search — Major Action 1/2 (1 Combat Round)",
                    pool_expr=f"{elec_base_p}",
                    wild_die=True,
                    overclock=True,
                    desc="(Legal), Extended Search Interval 1 (10 min base; 1 Major Action w/ Oracle R4), CRB p.183.",
                    tip=f"Pool {elec_base_p}d6 ({elec_base_p - 1}d6 + 1w): Electronics ({elec_sk}) + RES ({resonance}) + Focus (+{res_focus_r}) + Taz (+{taz_b}) + Overclock (+{overclock_b}, 1w) (28d6 if Oracle R4 swapped in for Focus).",
                    opp="Availability / Obscurity Threshold",
                ),
                _r20_ability(
                    base="Oracle Search — Major Action 2/2 (-1d6 Decay)",
                    pool_expr=f"{elec_base_p - 1}",
                    wild_die=True,
                    overclock=True,
                    desc="(Legal), Extended Search Interval 2 (completes 1 Combat Round / 2 Major Actions, -1d6 cumulative decay), CRB p.183.",
                    opp="Availability / Obscurity Threshold",
                ),
                "```",
                "",
                f"### `Compile-Register-Sprite` (`{compile_link_p}d6` Compiling w/ Resonance Link | `{register_p}d6` Registering)",
                "```text",
                _r20_ability(
                    base=f"Tasking (Compile {compile_link_p}d6 | Register {register_p}d6)",
                    pool_expr=f"{compile_p}+{task_q}",
                    wild_die=False,
                    overclock=False,
                    desc="Level ?{Level?|6} Sprite. Technoshamans: -2 Fade Value (+1 Service if Compiling >= 1 hit).",
                    tip=f"Tasking ({task_sk}) + Spec (+2) + RES ({resonance}) + Focus (+{res_focus_r}) = {compile_p}d6 (+2 Resonance Link when Compiling = {compile_link_p}d6). No ally sprite can learn or assist with Tasking.",
                    opp="Sprite Resistance (Level / Level x2)",
                ),
                "```",
                "",
                f"### `Fade-Resistance` (`{fade_compile_p}d6` Compiling/Registering | `{fade_cf_p}d6` Complex Form Threading)",
                "```text",
                _r20_ability(
                    base=f"Resist Fade (Compiling {fade_compile_p}d6 | Complex Form {fade_cf_p}d6)",
                    pool_expr=fade_q,
                    wild_die=False,
                    overclock=False,
                    include_wounds=False,
                    desc="Fade Resistance ignores Wound modifiers. Technoshamans: -2 Fade Value on Compiling/Decompiling.",
                    tip=f"Compiling/Registering = WIL ({wil}) + CHA ({cha}) + Sprite Conduit (+{sub_lvl}) + Focus (+{res_focus_r}) = {fade_compile_p}d6. Complex Form Threading = WIL ({wil}) + CHA ({cha}) = {fade_cf_p}d6.",
                ),
                "```",
                "",
                f"### `Matrix-Defense` (`{allin_mdef_p}d6` All-In | `{base_mdef_p}d6` Base Full | `{std_mdef_p}d6` Standard | `11d6` Soak)",
                "```text",
                _r20_ability(
                    base="Matrix Defense Umbrella",
                    pool_expr=mdef_q,
                    wild_die=False,
                    overclock=False,
                    desc=f"Standard ({std_mdef_p}d6 = 5 BH): FW 9 + RES {eff_res}. Base Full Defense ({base_mdef_p}d6 = 6 BH): +PA R6. All-In ({allin_mdef_p}d6 = 10 BH): +Syntax Error ({sub_lvl}) + Directional Shield DP (7). Soak: FW 9 + Armor 2 (+2 Biofeedback Filter).",
                ),
                "```",
                "",
                f"### `Death-Mark` (`{res_spike_p}d6` Sprite Power — Offensive Cracking vs Intuition + Firewall)",
                "```text",
                _r20_ability(
                    base="Sprite Power: Death Mark (Cracking + RES)",
                    pool_expr=f"{res_spike_p}",
                    wild_die=False,
                    overclock=False,
                    desc="Sustained Sprite Power (Offensive Cracking).",
                    tip=f"Pool {res_spike_p}d6: Cracking ({crack_sk}) + RES ({resonance}) + Focus (+{res_focus_r}) + Taz (+{taz_b}) + ECM Warrior II (+{ecm_b}).",
                    opp="[Intuition + Firewall](~selected|matrixresist_int_f)",
                ),
                "```",
                "",
                f"### Drone Perception / Clearsight (`{clr_p}d6` Passive / `{clr_p_enl}d6` Sustained — `-1` Threshold)",
                "```text",
                _r20_ability(
                    base="Drone Perception (Clearsight + Sensor)",
                    pool_expr=f"{clr_p}",
                    wild_die=False,
                    overclock=False,
                    gm_whisper=False,
                    desc=f"{clr_p}d6 Passive ({clr_p_enl}d6 w/ +{enl_delta} Enlighten Automaton), -1 Threshold via Pilot Origins.",
                    tip=f"Clearsight (7) + Sensor ({maa_prof['augmented_sensor']}/{maa_prof['enlightened_sensor']}) + Taz (+4) + Pilot Origins (+1).",
                ),
                "```",
                "",
                f"### Drone Piloting / Maneuvering & Wrist-Shield Ram (`{plt_p}d6` — `-1` Threshold, `33/39` AR, `8P*` DV)",
                "```text",
                _r20_ability(
                    base="Drone Piloting / Ramming (Maneuvering + Pilot/RES)",
                    pool_expr=f"{plt_p}",
                    wild_die=False,
                    overclock=False,
                    gm_whisper=False,
                    desc=f"-1 Threshold via Pilot Origins; Effective Handling 3. Ram Plate: AR 33 Passive / 39 Enlightened, DV 8P* (+1/Speed Interval), Halved Return Damage.",
                    tip=f"Maneuvering (7) + Pilot/RES ({maa_prof['inhabited_pilot']}) + Focus (+{res_focus_r}) + Taz Diagnosis (+3) + Pilot Origins (+1).",
                ),
                "```",
                "",
                f"### Drone Evasion (`{eva_p}d6` Defense Test)",
                "```text",
                _r20_ability(
                    base="Drone Evasion (Evasion + Pilot/RES)",
                    pool_expr=f"{eva_p}",
                    wild_die=False,
                    overclock=False,
                    gm_whisper=False,
                    desc="Add +4 Defense Dice for Full Defense or Dodge.",
                    tip=f"Evasion (7) + Pilot/RES ({maa_prof['inhabited_pilot']}) + Focus (+{res_focus_r}) + Taz Symbiosis (+4) + Pilot Origins (+1).",
                ),
                "```",
                "",
                f"### Drone Stealth (`{stl_p}d6` — `-1` Threshold)",
                "```text",
                _r20_ability(
                    base="Drone Stealth (Stealth + Pilot/RES)",
                    pool_expr=f"{stl_p}",
                    wild_die=False,
                    overclock=False,
                    gm_whisper=False,
                    desc="-1 Threshold via Pilot Origins.",
                    tip=f"Stealth (7) + Pilot/RES ({maa_prof['inhabited_pilot']}) + Focus (+{res_focus_r}) + Taz Symbiosis (+4) + Sneak-Sneak (+2) + Pilot Origins (+1).",
                ),
                "```",
                "",
                f"### Crimson Wasp Array (2x Link-Fired) Attack (`{wasp_p}d6` Passive / `{wasp_p_enl}d6` Sustained — 1 Wild Die, 7P* SS / 8P* SA)",
                "```text",
                _r20_ability(
                    base="Crimson Wasp Array (2x Link-Fired)",
                    pool_expr=f"{wasp_p}",
                    wild_die=True,
                    overclock=False,
                    gm_whisper=False,
                    desc="Mode: SS/SA (Link-Fired), Damage: 7P* (SS) / 8P* (SA), AR: 22/20/17/12/- (SS) or 21/19/16/11/- (SA), Ammo: 30(c). 1 Wild Die; -2P at Medium range.",
                    tip=f"FS 44 / DC 143 / SRMG 51. {wasp_p}d6 Passive ({wasp_p_enl}d6 w/ +{enl_delta} Enlighten Automaton): Targeting (7) + Sensor ({maa_prof['augmented_sensor']}/{maa_prof['enlightened_sensor']}) + Taz (+4) + Pilot Origins (+1) + Smartlink (+1).",
                ),
                "```",
                "",
                f"### Crimson Wasp Single Beam (`{wasp_p}d6` Passive / `{wasp_p_enl}d6` Sustained — 1 Wild Die, 5P* SS / 6P* SA)",
                "```text",
                _r20_ability(
                    base="Crimson Wasp (Single Beam)",
                    pool_expr=f"{wasp_p}",
                    wild_die=True,
                    overclock=False,
                    gm_whisper=False,
                    desc="Mode: SS/SA, Damage: 5P* (SS) / 6P* (SA), AR: 21/19/16/11/- (SS) or 20/18/15/10/- (SA), Ammo: 30(c). Independent Eye Mount; 1 Wild Die; -2P at Medium range.",
                    tip=f"FS 44 / SRMG 51. {wasp_p}d6 Passive ({wasp_p_enl}d6 w/ +{enl_delta} Enlighten Automaton): Targeting (7) + Sensor ({maa_prof['augmented_sensor']}/{maa_prof['enlightened_sensor']}) + Taz (+4) + Pilot Origins (+1) + Smartlink (+1).",
                ),
                "```",
                "",
                f"### Tesla Coil: Straight / Wobbly / Sweep (`{tesla_p}d6` Passive / `{tesla_p_enl}d6` Sustained)",
                "```text",
                _r20_ability(
                    base="Tesla Coil (?{Mode?|Straight Line (5S(e) AR 10/12)|Wobbly Cone (4S(e) AR 12/14)|Sweep Cone (2S(e) AR 14/16)})",
                    pool_expr=f"{tesla_p}",
                    wild_die=False,
                    overclock=False,
                    gm_whisper=False,
                    desc="BS 49 / SR6 117. Straight 20m line (REA+INT vs AR) or 20m cones (Wobbly 3m base 8.58° / Sweep 10m base 28.07°, may toggle Wild Die).",
                    tip=f"{tesla_p}d6 Passive ({tesla_p_enl}d6 w/ +{enl_delta} Enlighten Automaton): Targeting (7) + Sensor ({maa_prof['augmented_sensor']}/{maa_prof['enlightened_sensor']}) + Taz (+4) + Pilot Origins (+1).",
                ),
                "```",
                "",
                "### Engineering: Drones (`15d6`), Biotech (`15d6`) & Outdoors: Navigation (`9d6`) — Meatspace Emulated Skills",
                "```text",
                _r20_ability(
                    base="Meatspace Emulated Skill (Engineering 15d6 | Biotech 15d6 | Outdoors 9d6)",
                    pool_expr=meat_q,
                    wild_die=False,
                    overclock=False,
                    gm_whisper=False,
                    desc=f"Uses Real Logic ({log}) / Real Intuition ({intu}) instead of Natural Hacker. Engineering = LOG {log} + 5 + Spec 2 + Taz 4 = 15d6; Biotech = LOG {log} + 7 + Mobile Medic 4 = 15d6; Outdoors = INT {intu} + 5 + Spec 2 = 9d6.",
                ),
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
    Also writes `<char_id>_roll20.json` and the companion `<char_id>_roll20_macros.md`
    guide to the character's output directory when `char_repo_path` is provided.
    """
    payload = build_roll20_payload(char_data, char_repo_path=char_repo_path)
    json_str = json.dumps(payload, indent=indent, ensure_ascii=False)

    if char_repo_path and os.path.exists(char_repo_path):
        try:
            cid = str((char_data.get("identity") or {}).get("id") or "character").lower()
            out_dir = os.path.join(char_repo_path, "output")
            roll20_dir = os.path.join(out_dir, "roll20")
            os.makedirs(roll20_dir, exist_ok=True)

            # 1. Write Roll20 Macros & Effects markdown helper guide
            guide_path = os.path.join(roll20_dir, f"{cid}_roll20_macros.md")
            with open(guide_path, "w", encoding="utf-8") as f:
                f.write(generate_roll20_helper_guide(char_data, payload))

            # 2. Write Roll20 Genesis JSON payload
            json_path = os.path.join(roll20_dir, f"{cid}_roll20.json")
            with open(json_path, "w", encoding="utf-8") as f:
                f.write(json_str)

            # 3. Clean up any legacy loose files from the root of output/
            for legacy_name in [f"{cid}_roll20_macros.md", f"{cid}_roll20.json"]:
                legacy_file = os.path.join(out_dir, legacy_name)
                if os.path.isfile(legacy_file):
                    try:
                        os.remove(legacy_file)
                    except Exception:
                        pass
        except Exception:
            pass

    return json_str
