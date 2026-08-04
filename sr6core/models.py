"""
Pydantic Data Models for Shadowrun 6th Edition Characters & Systems.
"""

from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field


class AttributeBlock(BaseModel):
    body: int = 1
    agility: int = 1
    reaction: int = 1
    strength: int = 1
    willpower: int = 1
    logic: int = 1
    intuition: int = 1
    charisma: int = 1
    edge: int = 1
    resonance: Optional[int] = 0
    magic: Optional[int] = 0
    essence: float = 6.0


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
