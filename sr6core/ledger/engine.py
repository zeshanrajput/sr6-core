"""
Campaign Event Ledger Engine: Deterministic State Projection & Multi-Ledger Reconciliation.
Replays typed domain events to project exact tabletop resource states without regex parsing vulnerabilities.
"""

import os
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

from sr6core.ledger.events import (
    BaseCampaignEvent,
    KarmaAwardedEvent,
    KarmaSpentEvent,
    NuyenTransactionEvent,
    DamageAppliedEvent,
    AmmoExpendedEvent,
    ContactUpdatedEvent,
    QualityAcquiredEvent,
)


class ProjectedState(BaseModel):
    """Calculated runner state derived from chronologically replaying all ledger events."""
    char_id: str = "general"
    karma_available: int = 0
    lifetime_karma: int = 0
    karma_spent: int = 0
    nuyen_available: int = 0
    lifetime_nuyen: int = 0
    nuyen_spent: int = 0
    physical_damage: int = 0
    stun_damage: int = 0
    ammo_expended: Dict[str, int] = Field(default_factory=dict)
    contacts_favors: Dict[str, int] = Field(default_factory=dict)
    advancements: List[Dict[str, Any]] = Field(default_factory=list)


class CampaignEventLedger:
    """Manages an append-only stream of campaign domain events."""

    def __init__(self, char_id: str = "general"):
        self.char_id = char_id
        self.events: List[BaseCampaignEvent] = []

    def record(self, event: BaseCampaignEvent) -> None:
        """Appends an event to the ledger."""
        self.events.append(event)

    def replay(self, initial_karma: int = 0, initial_nuyen: int = 0) -> ProjectedState:
        """
        Deterministically replays the event stream to project current totals.
        """
        state = ProjectedState(
            char_id=self.char_id,
            karma_available=initial_karma,
            lifetime_karma=initial_karma,
            nuyen_available=initial_nuyen,
            lifetime_nuyen=initial_nuyen,
        )

        for event in self.events:
            if isinstance(event, KarmaAwardedEvent):
                state.karma_available += event.amount
                state.lifetime_karma += event.amount

            elif isinstance(event, KarmaSpentEvent):
                state.karma_available -= event.amount
                state.karma_spent += event.amount
                state.advancements.append({
                    "category": event.category,
                    "target": event.target,
                    "amount": event.amount,
                    "from": event.rating_from,
                    "to": event.rating_to,
                })

            elif isinstance(event, NuyenTransactionEvent):
                state.nuyen_available += event.amount
                if event.amount > 0:
                    state.lifetime_nuyen += event.amount
                else:
                    state.nuyen_spent += abs(event.amount)

            elif isinstance(event, DamageAppliedEvent):
                if event.damage_type == "Physical":
                    state.physical_damage += event.boxes
                elif event.damage_type == "Stun":
                    state.stun_damage += event.boxes

            elif isinstance(event, AmmoExpendedEvent):
                key = f"{event.weapon_id}_{event.ammo_type}".lower()
                state.ammo_expended[key] = state.ammo_expended.get(key, 0) + event.rounds

            elif isinstance(event, ContactUpdatedEvent):
                c_name = event.contact_name.strip()
                state.contacts_favors[c_name] = state.contacts_favors.get(c_name, 0) + event.favors_delta

            elif isinstance(event, QualityAcquiredEvent):
                if event.karma_cost > 0:
                    state.karma_available -= event.karma_cost
                    state.karma_spent += event.karma_cost

        return state

    def export_yaml_patch(self, current_master: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generates a delta patch against character_master.yaml.
        """
        projected = self.replay()
        current_identity = current_master.get("identity", {})
        current_nuyen = current_identity.get("nuyen", 0)
        current_karma = current_identity.get("karma", 0)

        patch = {}
        if projected.nuyen_available != current_nuyen:
            patch["nuyen"] = projected.nuyen_available
        if projected.karma_available != current_karma:
            patch["karma"] = projected.karma_available
            patch["total_karma"] = projected.lifetime_karma

        return patch
