"""
Test suite for SR6 Event-Sourced Campaign Ledger.
Validates immutable event appending, deterministic replay projections,
financial and karma tracking, and patch delta generation.
"""

import pytest
from sr6core.ledger.events import (
    KarmaAwardedEvent,
    KarmaSpentEvent,
    NuyenTransactionEvent,
    DamageAppliedEvent,
    AmmoExpendedEvent,
    ContactUpdatedEvent,
)
from sr6core.ledger.engine import CampaignEventLedger


def test_campaign_event_ledger_replay():
    ledger = CampaignEventLedger(char_id="yuriko")

    # Initial mission reward
    ledger.record(KarmaAwardedEvent(amount=10, mission="SRM 04-01", source="Mission Completion"))
    ledger.record(NuyenTransactionEvent(amount=15000, description="Mission Payout", msrp=15000))

    # Purchase Ares Predator VI with discount
    ledger.record(NuyenTransactionEvent(
        amount=-765,
        description="Purchased Ares Predator VI",
        msrp=850,
        actual_paid=765,
        discount_reason="Smile for the Camera"
    ))

    # Spend Karma to raise Agility
    ledger.record(KarmaSpentEvent(amount=10, category="Attributes", target="Agility", rating_from=4, rating_to=5))

    # Combat engagement
    ledger.record(AmmoExpendedEvent(weapon_id="ares_predator_vi", ammo_type="APDS", rounds=6, mode="BF"))
    ledger.record(DamageAppliedEvent(damage_type="Physical", boxes=2, source="Goon Shotgun"))
    ledger.record(ContactUpdatedEvent(contact_name="Doc Raven", favors_delta=2))

    # Replay
    state = ledger.replay(initial_karma=5, initial_nuyen=2000)

    # Initial 5 + 10 awarded - 10 spent = 5 available
    assert state.karma_available == 5
    # Initial 5 + 10 awarded = 15 lifetime
    assert state.lifetime_karma == 15
    assert state.karma_spent == 10

    # Initial 2000 + 15000 payout - 765 spent = 16235 available
    assert state.nuyen_available == 16235
    assert state.lifetime_nuyen == 17000
    assert state.nuyen_spent == 765

    # Combat & Contacts
    assert state.physical_damage == 2
    assert state.ammo_expended["ares_predator_vi_apds"] == 6
    assert state.contacts_favors["Doc Raven"] == 2


def test_yaml_patch_generation():
    ledger = CampaignEventLedger(char_id="velvet")
    ledger.record(KarmaAwardedEvent(amount=8, mission="SRM 04-02"))
    ledger.record(NuyenTransactionEvent(amount=10000, description="Payout"))

    current_master = {
        "identity": {
            "nuyen": 5000,
            "karma": 2,
            "total_karma": 2
        }
    }

    patch = ledger.export_yaml_patch(current_master)
    assert patch["nuyen"] == 10000
    assert patch["karma"] == 8
    assert patch["total_karma"] == 8
