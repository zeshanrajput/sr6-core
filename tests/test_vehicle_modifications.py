"""
Unit tests for Double Clutch (p. 120) Vehicle & Drone Modification Rules,
Automated Least-Used Resource 2:1 Slot Shifting, SRM Anthroform Cyberlimb Rules,
and Cyberlimb Internal Capacity Accounting.
"""

import pytest
from sr6core.vehicles import (
    calculate_vehicle_mod_slots,
    format_vehicle_mod_tables,
    parse_vehicle_modifications
)
from sr6core.rules_engine import get_drone_statblock_table
from sr6core.character_manager import CharacterManager


def test_base_mod_slots_unmodified_body():
    """Verifies that base Chassis, Powertrain, and Electronic slots equal unmodified Body."""
    test_drone = {
        "name": "Generic Rover",
        "body": 6,
        "pilot": 2,
        "sensor": 2,
        "modifications": []
    }
    slots = calculate_vehicle_mod_slots(test_drone)
    assert slots["unmodified_body"] == 6
    assert slots["base_slots"]["chassis"] == 6
    assert slots["base_slots"]["powertrain"] == 6
    assert slots["base_slots"]["electronic"] == 6
    assert slots["base_hardpoints"] == 2  # 6 // 3 = 2 Standard Hardpoints
    assert slots["is_legal"] is True


def test_matching_component_replacement_differential():
    """Verifies that higher rating matching components cost the difference in slots (DC p. 120)."""
    # Base Sensor is 3. Installing Increased Sensors 6 should cost 6 - 3 = 3 Electronic slots.
    drone = {
        "name": "Sensor Drone",
        "body": 5,
        "sensor": 3,
        "modifications": [
            "Increased Sensors 6"
        ]
    }
    slots = calculate_vehicle_mod_slots(drone)
    elec_mods = slots["categorized_mods"]["electronic"]
    assert len(elec_mods) == 1
    assert elec_mods[0]["rating"] == 6
    assert elec_mods[0]["slots_cost"] == 3  # 6 - 3 = 3
    assert slots["raw_used"]["electronic"] == 3
    assert slots["remaining"]["electronic"] == 2


def test_srm_anthroform_limb_replacement_rule():
    """
    Verifies SRM FAQ rule:
    Stock limbs on anthroform drones cost 0 Chassis slots and have 0 cyberware capacity.
    Replacing a stock limb with an actual cyberlimb costs 0 additional Chassis slots (1-for-1 exchange)
    and unlocks regular cyberware capacity (8 for Synthetic arm).
    """
    anthro_drone = {
        "name": "Shiawase Bi-Drone Butler",
        "category": "Anthroform Drone",
        "body": 4,
        "modifications": [
            "Used Synthetic Cyberarm (Right, 8 Capacity)"
        ]
    }
    slots = calculate_vehicle_mod_slots(anthro_drone)
    chassis_mods = slots["categorized_mods"]["chassis"]
    assert len(chassis_mods) == 1
    assert chassis_mods[0]["slots_cost"] == 0  # Exchanging stock limb costs 0 Chassis slots
    assert "0 Chassis slots per SRM guide" in chassis_mods[0]["notes"]
    assert len(slots["cyberlimbs"]) == 1
    assert slots["cyberlimbs"][0]["capacity"] == 8

    # Non-anthro drone mounting an integrated cyberarm costs 1 Chassis slot (DC p. 130)
    wheeled_drone = {
        "name": "MCT Doberman",
        "category": "Wheeled Drone",
        "body": 4,
        "modifications": [
            "Integrated Synthetic Cyberarm"
        ]
    }
    slots_wheeled = calculate_vehicle_mod_slots(wheeled_drone)
    assert slots_wheeled["categorized_mods"]["chassis"][0]["slots_cost"] == 1


def test_cyberlimb_internal_capacity_with_tesla_coil():
    """Verifies that weapons installed in a cyberlimb consume limb capacity points [c]."""
    anthro_drone = {
        "name": "Shiawase Man-at-Arms",
        "body": 10,
        "sensor": 3,
        "modifications": [
            "Used Synthetic Cyberarm (Right, 8 Capacity)",
            "Tesla Coil"
        ]
    }
    slots = calculate_vehicle_mod_slots(anthro_drone)
    assert len(slots["cyberlimbs"]) == 1
    cl = slots["cyberlimbs"][0]
    assert cl["capacity"] == 8
    assert cl["used_capacity"] == 8  # Tesla Coil takes [8] capacity (Body Shop p. 76)
    assert len(cl["items"]) == 1
    assert "Tesla Coil" in cl["items"][0]

    # Tesla coil should consume 0 vehicle mod slots
    tesla_mod = next(m for m in slots["categorized_mods"]["accessory"] if "tesla" in m["name"].lower())
    assert tesla_mod["slots_cost"] == 0


def test_automated_least_used_resource_conversion():
    """
    Verifies that when a category has a deficit, 2:1 slot conversion automatically
    pulls from the category with the most spare slots (least-used resource).
    """
    # Chassis needs 6 slots (base 4, deficit 2 -> needs 4 donor slots).
    # Powertrain has 0 used of 4 -> spare 4.
    # Electronic has 3 used of 4 -> spare 1.
    # Least-used resource is Powertrain (spare 4 > spare 1).
    # Engine should pull 4 slots from Powertrain @ 2:1 -> +2 Chassis.
    test_drone = {
        "name": "Overloaded Chassis Drone",
        "body": 4,
        "sensor": 1,
        "modifications": [
            "Increased Structural Integrity 2",  # 2 Chassis
            "Realistic Features 4",              # 4 Chassis -> Total 6 Chassis
            "ECM 1"                             # 1 Electronic
        ]
    }
    slots = calculate_vehicle_mod_slots(test_drone)
    assert slots["raw_used"]["chassis"] == 6
    assert slots["base_slots"]["chassis"] == 4
    # Auto shift: 4 from Powertrain -> +2 to Chassis
    assert len(slots["shifts"]) == 1
    shift = slots["shifts"][0]
    assert shift["from"] == "powertrain"
    assert shift["to"] == "chassis"
    assert shift["slots_spent"] == 4
    assert shift["slots_gained"] == 2
    assert shift["auto"] is True

    # Final effective capacities
    assert slots["effective_cap"]["chassis"] == 6
    assert slots["remaining"]["chassis"] == 0
    assert slots["effective_cap"]["powertrain"] == 0
    assert slots["remaining"]["powertrain"] == 0
    assert slots["remaining"]["electronic"] == 3  # 4 - 1 = 3
    assert slots["is_legal"] is True


def test_explicit_shift_override():
    """Verifies that explicit shifted_slots declarations override auto-conversion."""
    drone = {
        "name": "Custom Shift Drone",
        "body": 5,
        "sensor": 1,
        "shifted_slots": {
            "electronic_to_chassis": 2
        },
        "modifications": [
            "Increased Structural Integrity 2",  # 2
            "Realistic Features 4"               # 4 -> Total 6 Chassis (Base 5 + 1 = 6)
        ]
    }
    slots = calculate_vehicle_mod_slots(drone)
    assert len(slots["shifts"]) == 1
    shift = slots["shifts"][0]
    assert shift["from"] == "electronic"
    assert shift["to"] == "chassis"
    assert shift["slots_spent"] == 2
    assert shift["slots_gained"] == 1
    assert shift["explicit"] is True
    assert slots["effective_cap"]["chassis"] == 6
    assert slots["remaining"]["chassis"] == 0
    assert slots["effective_cap"]["electronic"] == 3  # 5 - 2 = 3
    assert slots["is_legal"] is True


def test_reiko_man_at_arms_complete_accounting():
    """
    Comprehensive verification of Reiko's Shiawase Man-at-Arms:
      - Unmodified Body: 10
      - Chassis (11 slots used): Structural Integrity 5 (5), Realistic Features 4 (4),
        Pop-Out Concealment x2 (2), Used Synthetic Cyberarm (0 per SRM).
      - Powertrain (6 or 8 slots used): Rotor (4), Wheeled (2), (Nitro Boost 2).
      - Electronic (5 slots used): Chameleon Coating (2), Increased Sensors 6 (3).
      - Hardpoints: 3/3 Standard used (2 Weapon Mounts + 1 Drone Rack).
      - Right Cyberarm: 8/8 Capacity used (Tesla Coil).
      - Least-used conversion: Pulls 2 slots from Electronic (spare 5 > spare 2/4) @ 2:1 -> +1 Chassis.
    """
    cm = CharacterManager()
    char = cm.load_character("reiko")
    assert char is not None
    data = char["data"]

    drones = data.get("drones", [])
    maa = next(d for d in drones if "man-at-arms" in d["name"].lower())
    assert maa is not None

    prof = parse_vehicle_modifications(maa, char_data=data)
    slots = prof["mod_slots"]

    assert slots["unmodified_body"] == 10
    assert slots["is_anthro"] is True

    # Check raw used slots
    assert slots["raw_used"]["chassis"] == 11
    assert slots["raw_used"]["powertrain"] in [6, 8]
    assert slots["raw_used"]["electronic"] == 5

    # Check auto 2:1 shift
    # Deficit of 1 in Chassis is filled by pulling 2 slots from Electronic (least-used resource)
    assert len(slots["shifts"]) >= 1
    s0 = slots["shifts"][0]
    assert s0["to"] == "chassis"
    assert s0["slots_gained"] == 1
    assert s0["slots_spent"] == 2

    # Check effective capacity and legality
    assert slots["effective_cap"]["chassis"] == 11
    assert slots["remaining"]["chassis"] == 0
    assert slots["remaining"]["powertrain"] >= 0
    assert slots["remaining"]["electronic"] >= 0
    assert slots["is_legal"] is True

    # Check Hardpoints
    assert slots["base_hardpoints"] == 3
    assert slots["hardpoints_used"] == 3
    assert slots["hardpoints_remaining"] == 0

    # Check Cyberlimbs & Tesla Coil
    assert len(slots["cyberlimbs"]) == 1
    cl = slots["cyberlimbs"][0]
    assert cl["capacity"] == 8
    assert cl["used_capacity"] == 8
    assert cl["capacity"] - cl["used_capacity"] == 0

    # Check Smart Tires and Wheeled Propulsion
    assert "Wheeled (Smart Tires): Han 3/4, Acc 15, SPD 25/120" in prof["mobility_str"]
    st_mod = next(m for m in slots["categorized_mods"]["accessory"] if "smart tires" in m["name"].lower())
    assert st_mod["slots_cost"] == 0
    assert "+5 Acceleration, +10 Speed Interval" in st_mod["notes"]


def test_drone_statblock_table_rendering():
    """Verifies that get_drone_statblock_table renders the full categorized tables."""
    table_md = get_drone_statblock_table("yuriko", "man-at-arms")
    assert "| SR6 Attribute | Rating / Value | Applied Modifiers Math & Notes |" in table_md
    assert "### Double Clutch Modification Slots & Capacity Summary" in table_md
    assert "### Installed Modifications by Category" in table_md
    assert "### Installed Cyberlimbs & Internal Capacity" in table_md

    # Check specific summary rows
    assert "| **Chassis** | 10 |" in table_md
    assert "| **Powertrain** | 10 |" in table_md
    assert "| **Electronic** | 10 |" in table_md
    assert "| **Hardpoints** | 3 (Standard) |" in table_md
    assert "Wheeled (Smart Tires): Han 3/4, Acc 15, SPD 25/120" in table_md

    # Check modifications rows
    assert "Increased Structural Integrity" in table_md
    assert "Realistic Features" in table_md
    assert "Pop-Out Concealment (Standard) x2" in table_md
    assert "Secondary Propulsion (Rotor)" in table_md
    assert "Secondary Propulsion (Wheeled)" in table_md
    assert "Smart Tires" in table_md
    assert "+5 Acceleration, +10 Speed Interval" in table_md
    assert "Chameleon Coating" in table_md
    assert "Increased Sensors" in table_md
    assert "Weapon Mount (Standard) x2" in table_md
    assert "Drone Rack (Small)" in table_md

    # Check cyberlimb row
    assert "**Used Synthetic Cyberarm (Right, 8 Capacity)**" in table_md
    assert "Tesla Coil (8 Capacity, 5S(e) Spray 20m)" in table_md


def test_smart_tires_mechanics():
    """
    Verifies Double Clutch Smart Tires mechanics:
      - Consumes 0 mod slots (Accessory).
      - Adds +5 Acceleration and +10 Speed Interval to wheeled propulsion.
      - Dynamic nanotech tread adapts to on-road/off-road surfaces with run-flat capability.
    """
    drone = {
        "name": "Test Rover",
        "body": 6,
        "modifications": [
            "Secondary Propulsion (Wheeled)",
            "Smart Tires"
        ]
    }
    slots = calculate_vehicle_mod_slots(drone)
    accs = slots["categorized_mods"]["accessory"]
    smart_tires = next((a for a in accs if "smart tires" in a["name"].lower()), None)
    assert smart_tires is not None
    assert smart_tires["slots_cost"] == 0
    assert "+5 Acceleration, +10 Speed Interval" in smart_tires["notes"]

    prof = parse_vehicle_modifications(drone)
    assert "Wheeled (Smart Tires): Han 3/4, Acc 15, SPD 25/120" in prof["mobility_str"]
    assert any("Smart Tires" in n for n in prof["notes"])
