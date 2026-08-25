"""
Pydantic Data Models for Shadowrun 6th Edition Characters & Systems.
Includes character creation models and structured Stat Block models for weapons, armor,
vehicles, spells, cyberware, qualities, and NPC/Grunt profiles.
"""

from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field, field_validator


class AttributeBlock(BaseModel):
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
    firewall: int = 0
    sleaze: int = 0
    data_processing: int = 0
    attack: int = 0


class LivingPersona(BaseModel):
    asdf_bonuses: LivingPersonaASDF = Field(default_factory=LivingPersonaASDF)
    symbiosis_bonuses: LivingPersonaASDF = Field(default_factory=LivingPersonaASDF)
    programs: List[str] = Field(default_factory=list)


class Skill(BaseModel):
    name: str
    id: str
    attribute: str
    rating: int = 0
    specialization: Optional[str] = None


class Quality(BaseModel):
    name: str
    ref: str
    quality_type: str = "positive"  # positive or negative
    rating: Optional[int] = 1
    choice: Optional[str] = None


class ComplexForm(BaseModel):
    name: str
    ref: str
    fading: int = 0
    target: Optional[str] = None
    duration: str = "Instant"


class MetaEcho(BaseModel):
    name: str
    ref: str


class Contact(BaseModel):
    name: str
    connection: int = 1
    loyalty: int = 1
    favors: int = 0
    type: Optional[str] = None
    notes: Optional[str] = ""


class Drone(BaseModel):
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


class CreationBudget(BaseModel):
    system: str = "Priority"  # Priority, SumToTen, PointBuy, LifePath
    priority_metatype: Optional[str] = "E"
    priority_attributes: Optional[str] = "A"
    priority_special: Optional[str] = "B"
    priority_skills: Optional[str] = "C"
    priority_resources: Optional[str] = "D"
    sum_to_ten_points: int = 10
    point_buy_karma: int = 100
    lifepath_stages: List[Dict[str, Any]] = Field(default_factory=list)


class Character(BaseModel):
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


# =========================================================================
# Structured Stat Block Models (Weapons, Armor, Vehicles, Spells, NPCs)
import re

# =========================================================================
# Structured Stat Block Models (Weapons, Armor, Vehicles, Spells, NPCs)
# =========================================================================

class WeaponStatBlock(BaseModel):
    """Structured representation of a Shadowrun 6E Weapon."""
    name: str
    category: str = "General"                     # e.g., "Heavy Pistols", "Blades", "Assault Rifles"
    damage: str                                   # e.g., "3P", "4S", "5P/e", "(STR+2)P"
    attack_rating: List[int] = Field(default_factory=list)  # [Close, Near, Medium, Far, Extreme]
    firing_modes: List[str] = Field(default_factory=list)   # ["SS", "SA", "BF", "FA"]
    ammo_capacity: Optional[int] = Field(default=None, ge=1)
    ammo_feed: Optional[str] = None               # "c" (clip), "d" (drum), "m" (magazine), "b" (break)
    availability: int = Field(ge=1, default=1)
    legal_restriction: Optional[str] = None       # None (Legal), "L" (Licensed), "F" (Forbidden)
    cost: int = Field(ge=0, default=0)
    concealability: Optional[int] = None
    source_ref: Optional[str] = None              # Book / Rule Chunk reference (e.g. "SR6H p.248")

    @field_validator("damage")
    @classmethod
    def validate_damage(cls, v: str) -> str:
        v_clean = v.strip()
        if not v_clean or v_clean.startswith("-"):
            raise ValueError(f"Invalid damage notation: '{v}' cannot be empty or negative.")
        # Valid patterns: 3P, 4S, (STR+2)P, (STR)P, 5P/e, 4S(e), 12P(f), 4S(E)
        if not re.search(r"(?:\d+|\(STR(?:\+\d+)?\))[PSps]", v_clean):
            raise ValueError(f"Invalid SR6 damage notation: '{v}'. Must specify Physical (P) or Stun (S) damage.")
        return v_clean

    @field_validator("attack_rating", mode="before")
    @classmethod
    def parse_ar_array(cls, v: Any) -> List[int]:
        if isinstance(v, str):
            # Parse formats like "10/10/8/-/-" or "12/8/6/2/0"
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
    defense_rating: int = Field(ge=0, default=0)  # Bonus or base Defense Rating (e.g. +2, +3, +4)
    capacity: int = Field(ge=0, default=0)
    availability: int = Field(ge=1, default=1)
    legal_restriction: Optional[str] = None       # None, "L", "F"
    cost: int = Field(ge=0, default=0)
    features: List[str] = Field(default_factory=list)
    source_ref: Optional[str] = None


class VehicleStatBlock(BaseModel):
    """Structured representation of a Vehicle or Drone."""
    name: str
    category: str = "Groundcraft"                 # Groundcraft, Rotorcraft, Drone (Small), etc.
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
    category: str = "Combat"                      # Combat, Health, Illusion, Manipulation, Detection
    spell_type: str = "Physical"                  # Physical or Mana
    range: str = "LOS"                            # Touch, LOS, LOS (A)
    damage: Optional[str] = None                  # "P", "S", or None
    duration: str = "Instant"                     # Instant, Sustained, Permanent
    drain: int = Field(ge=1, default=3)
    source_ref: Optional[str] = None


class AdeptPowerStatBlock(BaseModel):
    """Structured representation of an Adept Power."""
    name: str
    cost_per_level: float = Field(gt=0.0, default=0.5)  # Power Point cost
    max_levels: Optional[int] = Field(default=None, ge=1)
    activation: str = "Passive"                   # Passive, Free Action, Minor Action
    prerequisites: Optional[str] = None
    description: Optional[str] = ""
    source_ref: Optional[str] = None


class QualityStatBlock(BaseModel):
    """Structured representation of a Character Quality."""
    name: str
    quality_type: str = "Positive"                # Positive or Negative
    karma_cost: int = Field(ge=0, default=0)
    karma_bonus: int = Field(ge=0, default=0)
    prerequisites: Optional[str] = None
    summary: str = ""
    source_ref: Optional[str] = None


class CyberwareStatBlock(BaseModel):
    """Structured representation of Cyberware / Bioware."""
    name: str
    category: str = "Headware"                    # Headware, Eyeware, Bodyware, Cyberlimbs, Bioware
    essence_cost: float = Field(gt=0.0, le=6.0, default=0.1)
    capacity_cost: Optional[int] = Field(default=None, ge=0)
    availability: int = Field(ge=1, default=1)
    legal_restriction: Optional[str] = None       # None, "L", "F"
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
    target: str = "Device"                        # Device, File, Host, Icon, Persona, Sprite
    duration: str = "Instant"                     # Instant, Sustained, Permanent
    fading: int = Field(ge=1, default=2)          # Fading Value (FV)
    description: Optional[str] = ""
    source_ref: Optional[str] = None


class SpriteStatBlock(BaseModel):
    """Structured representation of a Matrix Sprite."""
    name: str                                     # e.g. "Crack Sprite", "Fault Sprite", "Machine Sprite"
    sprite_type: str = "Crack"                    # Courier, Crack, Data, Fault, Machine, Tutor, Companion
    level: Optional[int] = Field(default=None, ge=1)
    attack_formula: str = "L"                     # Matrix Attack formula (e.g. L, L+1, L+2)
    sleaze_formula: str = "L"                     # Matrix Sleaze formula (e.g. L+3, L)
    data_processing_formula: str = "L"            # Matrix Data Processing formula (e.g. L+1, L+2)
    firewall_formula: str = "L"                   # Matrix Firewall formula (e.g. L+2, L)
    initiative: str = "(DP * 2) + 4D6"
    skills: List[str] = Field(default_factory=list)   # e.g. ["Cracking", "Electronics"]
    powers: List[str] = Field(default_factory=list)   # e.g. ["Cookie", "Decompile", "Suppression"]
    optional_powers: List[str] = Field(default_factory=list)
    source_ref: Optional[str] = None


class SpiritStatBlock(BaseModel):
    """Structured representation of a Magical Spirit."""
    name: str                                     # e.g. "Spirit of Air", "Fire Spirit"
    spirit_type: str = "Air"                      # Air, Beasts, Earth, Fire, Man, Water, Guardian, Plant, Guidance, Task
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
    skills: List[str] = Field(default_factory=list)   # e.g. ["Astral", "Athletics", "Close Combat", "Perception"]
    powers: List[str] = Field(default_factory=list)   # e.g. ["Materialization", "Movement", "Elemental Attack"]
    optional_powers: List[str] = Field(default_factory=list)
    source_ref: Optional[str] = None


class AIStatBlock(BaseModel):
    """
    Structured representation of an Artificial Intelligence (Proto-Sapient, Sapient, or E-Ghost) in SR6.
    - Matrix persona attributes (Attack, Sleaze, Data Processing, Firewall) replace physical attributes.
    - Single Matrix Condition Monitor calculated as ceil(Willpower / 2) + 8.
    - Matrix Initiative formula based on Data Processing + Intuition + 4D6 (Hot-Sim).
    """
    name: str
    ai_type: str = "Sapient"                      # Proto-Sapient, Sapient, E-Ghost
    
    # Mental Attributes
    willpower: int = Field(ge=1, default=3)
    logic: int = Field(ge=1, default=4)
    intuition: int = Field(ge=1, default=4)
    charisma: int = Field(ge=1, default=3)
    edge: int = Field(ge=1, default=2)

    # Matrix / Persona Attributes
    attack: int = Field(ge=0, default=2)
    sleaze: int = Field(ge=0, default=2)
    data_processing: int = Field(ge=0, default=4)
    firewall: int = Field(ge=0, default=4)

    # Single Matrix Condition Monitor (ceil(Willpower / 2) + 8)
    matrix_condition_monitor: int = Field(ge=8, default=10)

    # Initiative (hot-sim base)
    matrix_initiative: str = "8 + 4D6"
    
    # AI Specifics
    home_node: Optional[str] = None               # Device, Host, or Grid where AI resides
    skills: Dict[str, int] = Field(default_factory=dict)
    ai_qualities: List[str] = Field(default_factory=list)
    programs: List[str] = Field(default_factory=list)
    advanced_programs: List[str] = Field(default_factory=list)
    source_ref: Optional[str] = None
