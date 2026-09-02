"""
Domain Event Models for Event-Sourced Shadowrun 6E Campaign Tracking.
"""

from typing import Optional, Literal
from datetime import datetime
from pydantic import BaseModel, Field


class BaseCampaignEvent(BaseModel):
    """Base class for all immutable campaign ledger events."""
    event_id: str = Field(default_factory=lambda: f"evt_{datetime.now().strftime('%Y%m%d%H%M%S%f')}")
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())
    char_id: str = "general"
    mission: Optional[str] = None
    notes: Optional[str] = None


class KarmaAwardedEvent(BaseCampaignEvent):
    """Karma awarded to the runner (Mission reward, downtime study)."""
    event_type: Literal["karma_awarded"] = "karma_awarded"
    amount: int = Field(ge=1, description="Amount of Karma gained")
    source: str = "Mission Payout"


class KarmaSpentEvent(BaseCampaignEvent):
    """Karma spent on character advancement."""
    event_type: Literal["karma_spent"] = "karma_spent"
    amount: int = Field(ge=1, description="Amount of Karma spent")
    category: str = "Attributes"  # Attributes, Skills, Qualities, ComplexForms, Spells, Echoes
    target: str = ""              # e.g., "Agility", "Cracking", "Ambidextrous"
    rating_from: Optional[int] = None
    rating_to: Optional[int] = None


class NuyenTransactionEvent(BaseCampaignEvent):
    """Financial income or expenditure."""
    event_type: Literal["nuyen_transaction"] = "nuyen_transaction"
    amount: int = Field(description="Nuyen change (positive for income, negative for purchase)")
    description: str = ""
    msrp: Optional[int] = None
    actual_paid: Optional[int] = None
    discount_reason: Optional[str] = None  # e.g. "Smile for the Camera", "DIY Rigger 50%"


class DamageAppliedEvent(BaseCampaignEvent):
    """Damage suffered during combat or downtime."""
    event_type: Literal["damage_applied"] = "damage_applied"
    damage_type: Literal["Physical", "Stun", "Overflow"] = "Physical"
    boxes: int = Field(ge=1, description="Damage boxes taken")
    source: str = "Combat"


class AmmoExpendedEvent(BaseCampaignEvent):
    """Ammunition fired in combat."""
    event_type: Literal["ammo_expended"] = "ammo_expended"
    weapon_id: str
    ammo_type: str = "Regular"  # APDS, Gel, Regular, Flechette
    rounds: int = Field(ge=1, description="Rounds fired")
    mode: str = "SA"            # SS, SA, BF, FA


class ContactUpdatedEvent(BaseCampaignEvent):
    """Contact relationship adjustment (Favors or Loyalty changes)."""
    event_type: Literal["contact_updated"] = "contact_updated"
    contact_name: str
    connection_delta: int = 0
    loyalty_delta: int = 0
    favors_delta: int = 0


class QualityAcquiredEvent(BaseCampaignEvent):
    """New positive or negative quality acquired during campaign play."""
    event_type: Literal["quality_acquired"] = "quality_acquired"
    quality_name: str
    karma_cost: int = 0
    quality_type: Literal["positive", "negative"] = "positive"
