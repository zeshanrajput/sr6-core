"""
Character Data Models and Unified Character Entity for Shadowrun 6th Edition.

This module provides:
1. Pydantic schema models for all SR6 subsystems (attributes, skills, qualities,
   spells, cyberware, vehicles, statblocks).
2. The high-level, unified `Character` class wrapping tabletop state with rich,
   documented properties (.name, .nuyen, .karma, .attributes, .skills, .pools,
   .gear, .weapons) and lifecycle methods (.sync(), .audit(), .export_quick_sheet()).
"""

from __future__ import annotations
import os
import re
import yaml
from typing import Dict, Any, List, Optional, Union
from pydantic import BaseModel, Field, field_validator


# =============================================================================
# 1. Pydantic Core Tabletop Data Models
# =============================================================================

class AttributeBlock(BaseModel):
    """Core physical and mental attributes for a character."""
    body: int = Field(ge=1, default=1)
    agility: int = Field(ge=1, default=1)
    reaction: int = Field(ge=1, default=1)
    strength: int = Field(ge=1, default=1)
    willpower: int = Field(ge=1, default=1)
    logic: int = Field(ge=1, default=1)
    intuition: int = Field(ge=1, default=1)
    charisma: int = Field(ge=1, default=1)
    edge: int = Field(ge=1, default=1)
    resonance: Optional[int] = Field(ge=0, default=0)
    magic: Optional[int] = Field(ge=0, default=0)
    essence: float = Field(gt=0.0, le=6.0, default=6.0)


class LivingPersonaASDF(BaseModel):
    """Living persona Attack, Sleaze, Data Processing, Firewall matrix attributes."""
    firewall: int = 0
    sleaze: int = 0
    data_processing: int = 0
    attack: int = 0


class LivingPersona(BaseModel):
    """Living Persona structure for Technomancers and AI Pilots."""
    asdf_bonuses: LivingPersonaASDF = Field(default_factory=LivingPersonaASDF)
    symbiosis_bonuses: LivingPersonaASDF = Field(default_factory=LivingPersonaASDF)
    programs: List[str] = Field(default_factory=list)


class Skill(BaseModel):
    """Active skill with attribute link, rating, and optional specialization."""
    name: str
    id: str
    attribute: str
    rating: int = 0
    specialization: Optional[str] = None


class Quality(BaseModel):
    """Positive or negative character quality."""
    name: str
    ref: str
    quality_type: str = "positive"  # positive or negative
    rating: Optional[int] = 1
    choice: Optional[str] = None


class ComplexForm(BaseModel):
    """Technomancer complex form."""
    name: str
    ref: str
    fading: int = 0
    target: Optional[str] = None
    duration: str = "Instant"


class MetaEcho(BaseModel):
    """Technomancer submersion echo or metamagic."""
    name: str
    ref: str


class Contact(BaseModel):
    """Tabletop social contact with Connection and Loyalty ratings."""
    name: str
    connection: int = 1
    loyalty: int = 1
    favors: int = 0
    type: Optional[str] = None
    notes: Optional[str] = ""


class Drone(BaseModel):
    """Drone or riggable vehicle."""
    name: str
    ref: str
    body: int = 1
    armor: int = 0
    pilot: int = 1
    sensor: int = 1
    speed: int = 0
    handling_on: int = 0
    handling_off: int = 0
    accel_on: int = 0
    accel_off: int = 0
    weapons: List[Dict[str, Any]] = Field(default_factory=list)
    modifications: List[Any] = Field(default_factory=list)
    accessories: List[Any] = Field(default_factory=list)
    shifted_slots: Optional[Dict[str, int]] = None


class CreationBudget(BaseModel):
    """Character generation budget tracking."""
    system: str = "Priority"  # Priority, SumToTen, PointBuy, LifePath
    priority_metatype: Optional[str] = "E"
    priority_attributes: Optional[str] = "A"
    priority_special: Optional[str] = "B"
    priority_skills: Optional[str] = "C"
    priority_resources: Optional[str] = "D"
    sum_to_ten_points: int = 10
    point_buy_karma: int = 100
    lifepath_stages: List[Dict[str, Any]] = Field(default_factory=list)


# =============================================================================
# 2. Structured Stat Block Models
# =============================================================================

class WeaponStatBlock(BaseModel):
    """Structured representation of a Shadowrun 6E Weapon."""
    name: str
    category: str = "General"
    damage: str
    attack_rating: List[int] = Field(default_factory=list)
    firing_modes: List[str] = Field(default_factory=list)
    ammo_capacity: Optional[int] = Field(default=None, ge=1)
    ammo_feed: Optional[str] = None
    availability: int = Field(ge=1, default=1)
    legal_restriction: Optional[str] = None
    cost: int = Field(ge=0, default=0)
    concealability: Optional[int] = None
    source_ref: Optional[str] = None

    @field_validator("damage")
    @classmethod
    def validate_damage(cls, v: str) -> str:
        v_clean = v.strip()
        if not v_clean or v_clean.startswith("-"):
            raise ValueError(f"Invalid damage notation: '{v}' cannot be empty or negative.")
        if not re.search(r"(?:\d+|\(STR(?:\+\d+)?\))[PSps]", v_clean):
            raise ValueError(f"Invalid SR6 damage notation: '{v}'. Must specify Physical (P) or Stun (S) damage.")
        return v_clean

    @field_validator("attack_rating", mode="before")
    @classmethod
    def parse_ar_array(cls, v: Any) -> List[int]:
        if isinstance(v, str):
            parts = [p.strip() for p in v.replace("–", "-").split("/")]
            result = []
            for p in parts:
                if p in ("-", "—", "", "N/A", "n/a"):
                    result.append(0)
                else:
                    try:
                        val = int(p)
                        if val < 0:
                            raise ValueError(f"Attack rating range cannot be negative: {val}")
                        result.append(val)
                    except ValueError:
                        result.append(0)
            return result
        elif isinstance(v, list):
            for x in v:
                if isinstance(x, int) and x < 0:
                    raise ValueError(f"Attack rating range cannot be negative: {x}")
            return v
        return v


class ArmorStatBlock(BaseModel):
    """Structured representation of Shadowrun 6E Armor."""
    name: str
    defense_rating: int = Field(ge=0, default=0)
    capacity: int = Field(ge=0, default=0)
    availability: int = Field(ge=1, default=1)
    legal_restriction: Optional[str] = None
    cost: int = Field(ge=0, default=0)
    features: List[str] = Field(default_factory=list)
    source_ref: Optional[str] = None


class VehicleStatBlock(BaseModel):
    """Structured representation of a Vehicle or Drone."""
    name: str
    category: str = "Groundcraft"
    handling: int = Field(ge=1, default=1)
    handling_offroad: Optional[int] = Field(default=None, ge=1)
    accel: int = Field(ge=1, default=1)
    speed_interval: int = Field(ge=1, default=10)
    top_speed: int = Field(gt=0, default=100)
    body: int = Field(ge=1, default=1)
    armor: int = Field(ge=0, default=0)
    pilot: int = Field(ge=0, default=1)
    sensor: int = Field(ge=0, default=1)
    seats: Optional[int] = Field(default=1, ge=0)
    availability: int = Field(ge=1, default=1)
    legal_restriction: Optional[str] = None
    cost: int = Field(ge=0, default=0)
    source_ref: Optional[str] = None


class SpellStatBlock(BaseModel):
    """Structured representation of a Spell."""
    name: str
    category: str = "Combat"
    spell_type: str = "Physical"
    range: str = "LOS"
    damage: Optional[str] = None
    duration: str = "Instant"
    drain: int = Field(ge=1, default=3)
    source_ref: Optional[str] = None


class AdeptPowerStatBlock(BaseModel):
    """Structured representation of an Adept Power."""
    name: str
    cost_per_level: float = Field(gt=0.0, default=0.5)
    max_levels: Optional[int] = Field(default=None, ge=1)
    activation: str = "Passive"
    prerequisites: Optional[str] = None
    description: Optional[str] = ""
    source_ref: Optional[str] = None


class QualityStatBlock(BaseModel):
    """Structured representation of a Character Quality."""
    name: str
    quality_type: str = "Positive"
    karma_cost: int = Field(ge=0, default=0)
    karma_bonus: int = Field(ge=0, default=0)
    prerequisites: Optional[str] = None
    summary: str = ""
    source_ref: Optional[str] = None


class CyberwareStatBlock(BaseModel):
    """Structured representation of Cyberware / Bioware."""
    name: str
    category: str = "Headware"
    essence_cost: float = Field(gt=0.0, le=6.0, default=0.1)
    capacity_cost: Optional[int] = Field(default=None, ge=0)
    availability: int = Field(ge=1, default=1)
    legal_restriction: Optional[str] = None
    cost: int = Field(ge=0, default=0)
    source_ref: Optional[str] = None


class NPCStatBlock(BaseModel):
    """Structured representation of an NPC, Grunt, or Contact Stat Block."""
    name: str
    archetype: Optional[str] = None
    professional_rating: int = Field(ge=0, le=6, default=1)
    attributes: AttributeBlock = Field(default_factory=AttributeBlock)
    initiative: str = "6 + 1D6"
    defense_rating: int = Field(ge=1, default=6)
    attack_rating: Optional[int] = Field(default=None, ge=0)
    condition_monitor: Dict[str, int] = Field(default_factory=lambda: {"physical": 10, "stun": 10})
    skills: Dict[str, int] = Field(default_factory=dict)
    qualities: List[str] = Field(default_factory=list)
    augmentations: List[str] = Field(default_factory=list)
    weapons: List[str] = Field(default_factory=list)
    armor: Optional[str] = None
    gear: List[str] = Field(default_factory=list)
    source_ref: Optional[str] = None


class ComplexFormStatBlock(BaseModel):
    """Structured representation of a Technomancer Complex Form."""
    name: str
    target: str = "Device"
    duration: str = "Instant"
    fading: int = Field(ge=1, default=2)
    description: Optional[str] = ""
    source_ref: Optional[str] = None


class SpriteStatBlock(BaseModel):
    """Structured representation of a Matrix Sprite."""
    name: str
    sprite_type: str = "Crack"
    level: Optional[int] = Field(default=None, ge=1)
    attack_formula: str = "L"
    sleaze_formula: str = "L"
    data_processing_formula: str = "L"
    firewall_formula: str = "L"
    initiative: str = "(DP * 2) + 4D6"
    skills: List[str] = Field(default_factory=list)
    powers: List[str] = Field(default_factory=list)
    optional_powers: List[str] = Field(default_factory=list)
    source_ref: Optional[str] = None


class SpiritStatBlock(BaseModel):
    """Structured representation of a Magical Spirit."""
    name: str
    spirit_type: str = "Air"
    force: Optional[int] = Field(default=None, ge=1)
    body_formula: str = "F"
    agility_formula: str = "F"
    reaction_formula: str = "F"
    strength_formula: str = "F"
    willpower_formula: str = "F"
    logic_formula: str = "F"
    intuition_formula: str = "F"
    charisma_formula: str = "F"
    essence_formula: str = "F"
    initiative: str = "(Reaction + Intuition) + 2D6"
    astral_initiative: str = "(Intuition * 2) + 3D6"
    skills: List[str] = Field(default_factory=list)
    powers: List[str] = Field(default_factory=list)
    optional_powers: List[str] = Field(default_factory=list)
    source_ref: Optional[str] = None


class AIStatBlock(BaseModel):
    """Structured representation of an Artificial Intelligence."""
    name: str
    ai_type: str = "Sapient"
    willpower: int = Field(ge=1, default=3)
    logic: int = Field(ge=1, default=4)
    intuition: int = Field(ge=1, default=4)
    charisma: int = Field(ge=1, default=3)
    edge: int = Field(ge=1, default=2)
    attack: int = Field(ge=0, default=2)
    sleaze: int = Field(ge=0, default=2)
    data_processing: int = Field(ge=0, default=4)
    firewall: int = Field(ge=0, default=4)
    matrix_condition_monitor: int = Field(ge=8, default=10)
    matrix_initiative: str = "8 + 4D6"
    home_node: Optional[str] = None
    skills: Dict[str, int] = Field(default_factory=dict)
    ai_qualities: List[str] = Field(default_factory=list)
    programs: List[str] = Field(default_factory=list)
    advanced_programs: List[str] = Field(default_factory=list)
    source_ref: Optional[str] = None


# Legacy Schema compatibility model
class CharacterSchema(BaseModel):
    """Legacy Pydantic schema model for validating raw character JSON/YAML."""
    handle: str
    real_name: Optional[str] = ""
    metatype: str = "Human"
    stream: Optional[str] = None
    gender: Optional[str] = "Unspecified"
    age: Optional[Any] = None
    attributes: AttributeBlock = Field(default_factory=AttributeBlock)
    living_persona: Optional[LivingPersona] = Field(default_factory=LivingPersona)
    qualities_positive: List[Quality] = Field(default_factory=list)
    qualities_negative: List[Quality] = Field(default_factory=list)
    skills: List[Skill] = Field(default_factory=list)
    complex_forms: List[ComplexForm] = Field(default_factory=list)
    meta_echoes: List[MetaEcho] = Field(default_factory=list)
    contacts: List[Contact] = Field(default_factory=list)
    drones: List[Drone] = Field(default_factory=list)
    creation_budget: CreationBudget = Field(default_factory=CreationBudget)


# =============================================================================
# 3. High-Level Character Entity (Authoritative Tabletop Wrapper)
# =============================================================================

class Character:
    """
    Unified, authoritative entity wrapping Shadowrun 6th Edition character state.

    This class serves as the central Python front door for the character portfolio.
    It wraps character data derived from the Markdown Trio (`character_build.qmd`,
    `character_purchases.qmd`, `character_log.qmd`) or loaded from master YAML.

    Attributes:
        id (str): Unique character identifier (e.g. 'reiko', 'velvet', 'venn').
        name (str): Full character name.
        handle (str): Street alias / handle.
        metatype (str): Character metatype (e.g. 'Human', 'Elf', 'AI-Pilot AI').
        nuyen (int): Current available nuyen balance.
        karma (int): Current unspent karma balance.
        lifetime_karma (int): Total lifetime karma earned.
        lifetime_nuyen (int): Total lifetime nuyen accumulated.
        attributes (Dict[str, int]): Physical, mental, and special attribute ratings.
        skills (List[Dict[str, Any]]): Active skills with ratings and specializations.
        pools (Dict[str, int]): Net modified dice pools calculated dynamically.
        gear (List[Dict[str, Any]]): Inventory and equipment items.
        weapons (List[Dict[str, Any]]): Tactical weapons with calculated AR/DV arrays.
        armor (List[Dict[str, Any]]): Armors and wearable protective gear.
        cyberware (List[Dict[str, Any]]): Cybernetic and bioware augmentations.
        qualities (Dict[str, List[Any]]): Categorized positive and negative qualities.
        contacts (List[Dict[str, Any]]): Social contacts with connection and loyalty.
        custom_mechanics (Dict[str, Any]): Data-driven derivations (living persona ASDF,
            Monad abilities, spirits, adept powers) derived without hardcoded hacks.

    Example:
        >>> import sr6core
        >>> char = sr6core.load_character("reiko")
        >>> print(f"{char.name} has {char.nuyen}¥ and {char.karma} Karma")
        >>> print(f"Firearms pool: {char.pools.get('Firearms', 0)}d6")
        >>> char.export_quick_sheet()  # Generates 2-page ASCII reference sheet
    """

    def __init__(self, raw_data: Dict[str, Any], repo_dir: Optional[str] = None):
        self._raw: Dict[str, Any] = raw_data or {}
        self._repo_dir: Optional[str] = repo_dir

        # Identity extraction
        identity = self._raw.get("identity", {})
        self.id: str = identity.get("id") or self._raw.get("handle") or "unknown"
        self.name: str = identity.get("name") or identity.get("real_name") or self._raw.get("name") or self.id.title()
        self.handle: str = identity.get("handle") or self._raw.get("handle") or self.name
        self.metatype: str = identity.get("metatype") or self._raw.get("metatype") or "Human"
        self.stream: Optional[str] = identity.get("stream") or self._raw.get("stream")
        self.tradition: Optional[str] = identity.get("tradition") or self._raw.get("tradition")

        # Finances & Balances
        self.nuyen: int = int(identity.get("nuyen", self._raw.get("nuyen", 0)))
        self.karma: int = int(identity.get("karma", self._raw.get("karma", 0)))
        self.lifetime_karma: int = int(identity.get("lifetime_karma", self.karma))
        self.lifetime_nuyen: int = int(identity.get("lifetime_nuyen", self.nuyen))
        self.heat: int = int(identity.get("heat", self._raw.get("heat", 0)))

        # Attributes
        self.attributes: Dict[str, int] = dict(self._raw.get("attributes", {}))

        # Skills
        raw_skills = self._raw.get("skills", [])
        self.skills: List[Dict[str, Any]] = raw_skills if isinstance(raw_skills, list) else []

        # Gear, Weapons, Armor, Cyberware
        self.gear: List[Dict[str, Any]] = list(self._raw.get("gear", []))
        self.weapons: List[Dict[str, Any]] = list(self._raw.get("weapons", []))
        self.armor: List[Dict[str, Any]] = list(self._raw.get("armors", self._raw.get("armor", [])))
        self.cyberware: List[Dict[str, Any]] = list(self._raw.get("cyberware", []))

        # Qualities
        raw_qualities = self._raw.get("qualities", {})
        if isinstance(raw_qualities, dict):
            self.qualities: Dict[str, List[Any]] = {
                "positive": list(raw_qualities.get("positive", [])),
                "negative": list(raw_qualities.get("negative", [])),
            }
        else:
            self.qualities = {
                "positive": list(self._raw.get("qualities_positive", [])),
                "negative": list(self._raw.get("qualities_negative", [])),
            }

        # Social Contacts
        self.contacts: List[Dict[str, Any]] = list(self._raw.get("contacts", []))

        # Awakened / Emerged / Special Subsystems
        self.spells: List[Dict[str, Any]] = list(self._raw.get("spells", []))
        self.complex_forms: List[Dict[str, Any]] = list(self._raw.get("complex_forms", []))
        self.adept_powers: List[Dict[str, Any]] = list(self._raw.get("adept_powers", []))
        self.drones: List[Dict[str, Any]] = list(self._raw.get("drones", []))

    @property
    def raw_data(self) -> Dict[str, Any]:
        """Returns the raw dictionary data."""
        return self._raw

    @property
    def pools(self) -> Dict[str, int]:
        """
        Dynamically calculates net tabletop dice pools for active skills, taking into
        account base attributes, skill ratings, specializations, and passive modifiers.
        """
        from sr6core.rules.modifiers import ModifierEngine

        calculated_pools: Dict[str, int] = {}
        for s in self.skills:
            if not isinstance(s, dict):
                continue
            skill_name = s.get("name", "")
            if not skill_name:
                continue

            # Calculate via ModifierEngine with full synergy/augmentation audits
            try:
                opt = ModifierEngine.calculate_skill_pool(
                    char_data=self._raw,
                    skill_name=skill_name,
                    specialization=s.get("specialization"),
                )
                calculated_pools[skill_name] = opt.total_pool()
                if s.get("specialization"):
                    calculated_pools[f"{skill_name} ({s['specialization']})"] = opt.total_pool()
            except Exception:
                # Fallback: base attribute + skill rating
                attr_name = s.get("attribute", "agility").lower()
                attr_val = self.attributes.get(attr_name, self.attributes.get(attr_name.upper(), 0))
                rating = s.get("rating", 0)
                calculated_pools[skill_name] = attr_val + rating

        return calculated_pools

    @property
    def custom_mechanics(self) -> Dict[str, Any]:
        """
        Derives uncommon and custom rule interactions dynamically from character
        qualities, augmentations, and data models without hardcoding character IDs.
        """
        from sr6core.rules.modifiers import ModifierEngine

        mechanics: Dict[str, Any] = {}

        # 1. Living Persona ASDF (Technomancers, AI Pilots)
        if self.stream or self.attributes.get("resonance", 0) > 0 or "living_persona" in self._raw:
            try:
                mechanics["living_persona"] = ModifierEngine.get_living_persona_asdf(self._raw)
                mechanics["full_matrix_defense"] = ModifierEngine.get_full_matrix_defense(self._raw)
                mechanics["matrix_initiative"] = ModifierEngine.get_matrix_initiative(self._raw)
            except Exception:
                pass

        # 2. Monad Co-Consciousness / Nanite Augmentations
        pos_names = [
            q.get("name", "").lower() if isinstance(q, dict) else str(q).lower()
            for q in self.qualities.get("positive", [])
        ]
        if any("monad" in qn for qn in pos_names) or "monad_abilities" in self._raw:
            mechanics["monad_abilities"] = self._raw.get("monad_abilities", [])

        # 3. Adept Powers & Astral Stats
        if self.attributes.get("magic", 0) > 0 or self.adept_powers:
            mechanics["adept_powers"] = self.adept_powers

        # 4. Rigging & Drones
        if self.drones:
            mechanics["drones"] = len(self.drones)

        return mechanics

    def sync(self) -> str:
        """
        Recompiles character master state from scratch from the Markdown Trio
        (`character_build.qmd`, `character_purchases.qmd`, `character_log.qmd`),
        updates `*_master.yaml`, and reloads active properties.

        Returns:
            str: Path to the updated master YAML file.
        """
        from sr6core.character.compiler import compile_character, rebuild_character_yaml

        target_path = rebuild_character_yaml(self.id)
        # Reload raw data
        with open(target_path, "r", encoding="utf-8") as f:
            new_data = yaml.safe_load(f)
        self.__init__(new_data, repo_dir=self._repo_dir)
        return target_path

    def audit(self) -> Dict[str, Any]:
        """
        Runs comprehensive character generation compliance checks against
        official SR6 priority tables, karma caps, and attribute limits.

        Returns:
            Dict[str, Any]: Structured audit report with 'valid' (bool),
            'positive_karma', 'negative_karma', and detailed section results.
        """
        from sr6core.creation.deep_audit import deep_audit_character

        return deep_audit_character(self.id)

    def export_quick_sheet(self, output_path: Optional[str] = None) -> str:
        """
        Generates the strictly budgeted 2-page ASCII reference sheet (<= 120 lines total,
        76-column fixed width) and writes it to disk.

        Args:
            output_path: Optional destination path. Defaults to
                `characters/{char_id}/output/text/{char_id}_sheet.txt`.

        Returns:
            str: Path to the generated sheet file.
        """
        from sr6core.publishing.quick_sheet import export_quick_sheet

        return export_quick_sheet(self._raw, char_repo_path=self._repo_dir, output_path=output_path)

    def generate_dossier(self) -> str:
        """
        Generates Quarto appendix dossier markdown containing dynamic tables,
        weapon arrays, and rules citations for book compilation.

        Returns:
            str: Rendered Quarto markdown string.
        """
        from sr6core.publishing.enricher import generate_quarto_appendix_dossier

        return generate_quarto_appendix_dossier(self._raw)

    def to_dict(self) -> Dict[str, Any]:
        """Returns the full character dataset as a serializable dictionary."""
        return dict(self._raw)

    def to_yaml(self) -> str:
        """Serializes the character dataset as YAML."""
        return yaml.dump(self._raw, default_flow_style=False, sort_keys=False, allow_unicode=True)

    @classmethod
    def load(cls, char_id: str, repo_dir: Optional[str] = None) -> "Character":
        """
        High-level factory function to load a Character by ID.

        Args:
            char_id (str): Character ID (e.g. 'reiko', 'velvet', 'venn').
            repo_dir (str, optional): Override character repo directory.

        Returns:
            Character: The loaded Character instance.
        """
        from sr6core.character.manager import CharacterManager

        cm = CharacterManager()
        char_record = cm.load_character(char_id)
        if not char_record:
            raise FileNotFoundError(f"Character portfolio not found for '{char_id}'.")

        data = char_record.get("data", {})
        resolved_dir = repo_dir or char_record.get("path")
        if resolved_dir and os.path.isfile(resolved_dir):
            resolved_dir = os.path.dirname(resolved_dir)

        return cls(raw_data=data, repo_dir=resolved_dir)

    def __repr__(self) -> str:
        return f"<Character id='{self.id}' name='{self.name}' metatype='{self.metatype}' karma={self.karma} nuyen={self.nuyen}>"


# =============================================================================
# 4. Top-Level Convenience Helpers
# =============================================================================

def load_character(char_id: str) -> Character:
    """Convenience helper to load a Character by ID."""
    return Character.load(char_id)


def list_characters() -> List[str]:
    """Lists all discovered character portfolio IDs."""
    from sr6core.character.manager import CharacterManager

    cm = CharacterManager()
    return list(cm.discover_characters().keys())
