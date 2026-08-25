"""
Unit tests for Pydantic Stat Block Schemas & Markdown Extractors:
- WeaponStatBlock, ArmorStatBlock, VehicleStatBlock, SpellStatBlock, NPCStatBlock
- ComplexFormStatBlock, SpriteStatBlock, SpiritStatBlock
- Table extractors: parse_weapon_table, parse_armor_table, parse_vehicle_table, parse_spell_table
- Technomancer & Matrix extractors: parse_complex_form_table, parse_sprite_table, parse_spirit_table
- Stat block text extractor: parse_npc_statblock
"""

import pytest
from pydantic import ValidationError
from sr6core.models import (
    WeaponStatBlock,
    ArmorStatBlock,
    VehicleStatBlock,
    SpellStatBlock,
    ComplexFormStatBlock,
    SpriteStatBlock,
    SpiritStatBlock,
    AIStatBlock,
    NPCStatBlock,
    AttributeBlock,
)
from sr6core.vault.statblock_parser import (
    parse_markdown_table_rows,
    parse_weapon_table,
    parse_armor_table,
    parse_vehicle_table,
    parse_spell_table,
    parse_complex_form_table,
    parse_sprite_table,
    parse_spirit_table,
    parse_npc_statblock,
    parse_ai_statblock,
    calculate_modified_weapon,
    format_weapon_card,
    format_statblock_markdown,
    format_statblock_plaintext,
)


def test_weapon_statblock_pydantic_validation():
    w = WeaponStatBlock(
        name="Ares Predator VI",
        category="Heavy Pistols",
        damage="3P",
        attack_rating="10/10/8/-/-",
        firing_modes=["SA", "BF"],
        ammo_capacity=15,
        ammo_feed="c",
        availability=2,
        legal_restriction="L",
        cost=750,
    )
    assert w.name == "Ares Predator VI"
    assert w.damage == "3P"
    assert w.attack_rating == [10, 10, 8, 0, 0]
    assert w.firing_modes == ["SA", "BF"]
    assert w.ammo_capacity == 15
    assert w.ammo_feed == "c"
    assert w.legal_restriction == "L"
    assert w.cost == 750


def test_armor_statblock_pydantic_validation():
    a = ArmorStatBlock(
        name="Armored Jacket",
        defense_rating=4,
        capacity=6,
        availability=2,
        cost=1000,
        features=["Chemical Protection 2", "Insulation 1"],
    )
    assert a.defense_rating == 4
    assert a.capacity == 6
    assert len(a.features) == 2


def test_vehicle_statblock_pydantic_validation():
    v = VehicleStatBlock(
        name="Eurocar Westwind 3000",
        category="Groundcraft",
        handling=4,
        handling_offroad=2,
        accel=25,
        speed_interval=20,
        top_speed=240,
        body=10,
        armor=8,
        pilot=3,
        sensor=3,
        seats=2,
        cost=185000,
    )
    assert v.handling == 4
    assert v.handling_offroad == 2
    assert v.top_speed == 240
    assert v.body == 10


def test_spell_statblock_pydantic_validation():
    s = SpellStatBlock(
        name="Fireball",
        category="Combat",
        spell_type="Physical",
        range="LOS (A)",
        damage="P",
        duration="Instant",
        drain=5,
    )
    assert s.name == "Fireball"
    assert s.spell_type == "Physical"
    assert s.range == "LOS (A)"
    assert s.damage == "P"
    assert s.drain == 5


def test_complex_form_pydantic_validation():
    cf = ComplexFormStatBlock(
        name="Resonance Spike",
        target="Device",
        duration="Instant",
        fading=3,
        description="Inflicts Matrix damage directly to target device or persona."
    )
    assert cf.name == "Resonance Spike"
    assert cf.target == "Device"
    assert cf.duration == "Instant"
    assert cf.fading == 3


def test_sprite_pydantic_validation():
    sp = SpriteStatBlock(
        name="Crack Sprite",
        sprite_type="Crack",
        attack_formula="L",
        sleaze_formula="L+3",
        data_processing_formula="L+2",
        firewall_formula="L+1",
        initiative="(DP * 2) + 4D6",
        skills=["Cracking", "Electronics"],
        powers=["Cookie", "Decompile", "Suppression"],
    )
    assert sp.name == "Crack Sprite"
    assert sp.sleaze_formula == "L+3"
    assert "Cracking" in sp.skills
    assert "Cookie" in sp.powers


def test_spirit_pydantic_validation():
    spirit = SpiritStatBlock(
        name="Fire Spirit",
        spirit_type="Fire",
        body_formula="F+1",
        agility_formula="F+2",
        reaction_formula="F+3",
        strength_formula="F-2",
        willpower_formula="F",
        logic_formula="F",
        intuition_formula="F",
        charisma_formula="F",
        essence_formula="F",
        initiative="(Reaction + Intuition) + 2D6",
        skills=["Astral", "Athletics", "Close Combat", "Exotic Ranged Weapons", "Perception"],
        powers=["Accident", "Confusion", "Elemental Attack (Fire)", "Energy Aura (Fire)", "Engulf (Fire)", "Fear", "Materialization"],
    )
    assert spirit.name == "Fire Spirit"
    assert spirit.body_formula == "F+1"
    assert "Elemental Attack (Fire)" in spirit.powers


def test_npc_statblock_pydantic_validation():
    npc = NPCStatBlock(
        name="Kei 'Glitch' Takahashi",
        archetype="Decker",
        professional_rating=3,
        attributes=AttributeBlock(
            body=3, agility=4, reaction=4, strength=2,
            willpower=4, logic=6, intuition=5, charisma=3,
            edge=3, essence=5.2
        ),
        initiative="9 + 1D6",
        defense_rating=8,
        skills={"Electronics": 6, "Cracking": 6, "Firearms": 3, "Stealth": 4},
        weapons=["Fichetti Security 600 (2P, 12/9/6/-/-)"],
        armor="Armor Vest (+2)",
    )
    assert npc.professional_rating == 3
    assert npc.attributes.logic == 6
    assert npc.skills["Cracking"] == 6
    assert npc.defense_rating == 8


def test_parse_weapon_table():
    sample_table = """
| Weapon | Damage | Attack Rating | Modes | Ammo | Avail | Cost |
|---|---|---|---|---|---|---|
| Ares Predator VI | 3P | 10/10/8/-/- | SA/BF | 15(c) | 2(L) | 750¥ |
| Katana | (STR+3)P | 10/0/0/0/0 | - | - | 3 | 1,000¥ |
| Ingram Smartgun XIII | 3P | 12/10/7/-/- | SA/BF/FA | 32(c) | 3(F) | 800¥ |
"""
    weapons = parse_weapon_table(sample_table, default_category="Firearms")
    assert len(weapons) == 3

    # Check Ares Predator
    pred = weapons[0]
    assert pred.name == "Ares Predator VI"
    assert pred.damage == "3P"
    assert pred.attack_rating == [10, 10, 8, 0, 0]
    assert "SA" in pred.firing_modes
    assert "BF" in pred.firing_modes
    assert pred.ammo_capacity == 15
    assert pred.ammo_feed == "c"
    assert pred.availability == 2
    assert pred.legal_restriction == "L"
    assert pred.cost == 750

    # Check Katana
    katana = weapons[1]
    assert katana.name == "Katana"
    assert "(STR+3)P" in katana.damage
    assert katana.cost == 1000

    # Check Ingram Smartgun (Forbidden)
    ingram = weapons[2]
    assert ingram.name == "Ingram Smartgun XIII"
    assert ingram.legal_restriction == "F"
    assert ingram.ammo_capacity == 32


def test_parse_armor_table():
    sample_table = """
| Armor | Defense Rating | Capacity | Avail | Cost | Features |
|---|---|---|---|---|---|
| Armor Jacket | +4 | 6 | 2 | 1,000¥ | Standard lining |
| Full Body Armor | +5 | 8 | 4(L) | 2,500¥ | Helmet included |
"""
    armors = parse_armor_table(sample_table)
    assert len(armors) == 2
    assert armors[0].name == "Armor Jacket"
    assert armors[0].defense_rating == 4
    assert armors[0].cost == 1000
    assert armors[1].legal_restriction == "L"
    assert armors[1].defense_rating == 5


def test_parse_vehicle_table():
    sample_table = """
| Vehicle | Handling | Accel | Speed | Body | Armor | Pilot | Sensor | Seats | Avail | Cost |
|---|---|---|---|---|---|---|---|---|---|---|
| Ares Roadmaster | 3/3 | 12 | 15/140 | 16 | 12 | 2 | 2 | 6 | 3 | 55,000¥ |
| MCT-Nissan Roto-drone | 4 | 10 | 10/100 | 6 | 4 | 3 | 3 | 0 | 2 | 5,000¥ |
"""
    vehicles = parse_vehicle_table(sample_table)
    assert len(vehicles) == 2
    roadmaster = vehicles[0]
    assert roadmaster.name == "Ares Roadmaster"
    assert roadmaster.handling == 3
    assert roadmaster.body == 16
    assert roadmaster.armor == 12
    assert roadmaster.speed_interval == 15
    assert roadmaster.top_speed == 140
    assert roadmaster.cost == 55000

    rotodrone = vehicles[1]
    assert rotodrone.name == "MCT-Nissan Roto-drone"
    assert rotodrone.pilot == 3
    assert rotodrone.sensor == 3


def test_parse_spell_table():
    sample_table = """
| Spell | Type | Range | Damage | Duration | Drain |
|---|---|---|---|---|---|
| Manabolt | Mana | LOS | P | Instant | 4 |
| Heal | Physical | Touch | - | Permanent | 3 |
| Invisibility | Mana | LOS | - | Sustained | 3 |
"""
    spells = parse_spell_table(sample_table)
    assert len(spells) == 3
    assert spells[0].name == "Manabolt"
    assert spells[0].spell_type == "Mana"
    assert spells[0].damage == "P"
    assert spells[0].drain == 4

    assert spells[1].name == "Heal"
    assert spells[1].spell_type == "Physical"
    assert spells[1].duration == "Permanent"


def test_parse_complex_form_table():
    sample_table = """
| Complex Form | Target | Duration | Fading |
|---|---|---|---|
| Cleaner | Persona | Sustained | 2 |
| Diffusion of Firewall | Device | Sustained | 3 |
| Pulse Storm | Persona | Instant | 3 |
| Resonance Spike | Device | Instant | 3 |
"""
    forms = parse_complex_form_table(sample_table)
    assert len(forms) == 4
    assert forms[0].name == "Cleaner"
    assert forms[0].target == "Persona"
    assert forms[0].duration == "Sustained"
    assert forms[0].fading == 2

    assert forms[3].name == "Resonance Spike"
    assert forms[3].target == "Device"
    assert forms[3].fading == 3


def test_parse_sprite_table():
    sample_table = """
| Sprite | Attack | Sleaze | Data Processing | Firewall | Initiative | Skills | Powers |
|---|---|---|---|---|---|---|---|
| Courier Sprite | L | L+1 | L+2 | L+3 | (DP * 2) + 4D6 | Electronics | Cookie, Hash |
| Crack Sprite | L | L+3 | L+2 | L+1 | (DP * 2) + 4D6 | Cracking, Electronics | Cookie, Decompile, Suppression |
| Fault Sprite | L+3 | L | L+1 | L+2 | (DP * 2) + 4D6 | Cracking | Electron Storm, Gremlins |
"""
    sprites = parse_sprite_table(sample_table)
    assert len(sprites) == 3
    assert sprites[1].name == "Crack Sprite"
    assert sprites[1].sleaze_formula == "L+3"
    assert "Cracking" in sprites[1].skills
    assert "Suppression" in sprites[1].powers

    assert sprites[2].name == "Fault Sprite"
    assert sprites[2].attack_formula == "L+3"
    assert "Gremlins" in sprites[2].powers


def test_parse_spirit_table():
    sample_table = """
| Spirit | Body | Agility | Reaction | Strength | Willpower | Logic | Intuition | Charisma | Essence | Initiative | Skills | Powers |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Spirit of Air | F-2 | F+3 | F+4 | F-3 | F | F | F | F | F | (Reaction + Intuition) + 2D6 | Astral, Athletics, Perception | Accident, Concealment, Engulf (Air), Materialization, Movement |
| Fire Spirit | F+1 | F+2 | F+3 | F-2 | F | F | F | F | F | (Reaction + Intuition) + 2D6 | Astral, Athletics, Close Combat, Perception | Accident, Confusion, Elemental Attack (Fire), Materialization |
"""
    spirits = parse_spirit_table(sample_table)
    assert len(spirits) == 2
    assert spirits[0].name == "Spirit of Air"
    assert spirits[0].body_formula == "F-2"
    assert spirits[0].reaction_formula == "F+4"
    assert "Concealment" in spirits[0].powers

    assert spirits[1].name == "Fire Spirit"
    assert spirits[1].body_formula == "F+1"
    assert "Elemental Attack (Fire)" in spirits[1].powers


def test_parse_npc_statblock():
    sample_npc_text = """
Name: Renraku Red Samurai Lieutenant (PR 4)
Attributes: B 5, A 6, R 5(7), S 4, W 4, L 4, I 5, C 3, EDG 4, ESS 3.2
Initiative: 12 + 3D6
Defense Rating: 11
Attack Rating: 14
Skills: Firearms 6, Close Combat 6, Athletics 5, Perception 5, Stealth 4
Weapons: Ares Alpha (4P, 11/11/9/3/0, SA/BF/FA), Katana ((STR+3)P)
Armor: Red Samurai Custom Armor (+5)
Augmentations: Wired Reflexes 2, Smartlink, Cybereyes 2
Gear: Commlink (Rating 5), 4 spare clips, medkit (Rating 3)
Qualities: Toughness, Guts
"""
    npc = parse_npc_statblock(sample_npc_text)
    assert npc.name == "Renraku Red Samurai Lieutenant"
    assert npc.professional_rating == 4
    assert npc.attributes.body == 5
    assert npc.attributes.agility == 6
    assert npc.attributes.essence == 3.2
    assert npc.initiative == "12 + 3D6"
    assert npc.defense_rating == 11
    assert npc.attack_rating == 14
    assert npc.skills["Firearms"] == 6
    assert npc.skills["Close Combat"] == 6
    assert npc.skills["Perception"] == 5
    assert len(npc.weapons) == 2
    assert "Ares Alpha" in npc.weapons[0]
    assert "Red Samurai Custom Armor" in npc.armor
    assert len(npc.augmentations) == 3
    assert "Toughness" in npc.qualities


def test_ai_statblock_pydantic_validation():
    ai = AIStatBlock(
        name="Mirage",
        ai_type="E-Ghost",
        willpower=5,
        logic=7,
        intuition=6,
        charisma=4,
        edge=4,
        attack=6,
        sleaze=7,
        data_processing=8,
        firewall=6,
        matrix_condition_monitor=11,  # 8 + ceil(5/2) = 11
        matrix_initiative="14 + 4D6",
        home_node="Renraku Archology Archive Grid",
        skills={"Cracking": 7, "Electronics": 8, "Con": 4},
        ai_qualities=["Root Access", "Submerged: Paragon"],
        programs=["Armor", "Decryption", "Baby Monitor"],
    )
    assert ai.name == "Mirage"
    assert ai.ai_type == "E-Ghost"
    assert ai.willpower == 5
    assert ai.attack == 6
    assert ai.matrix_condition_monitor == 11
    assert "Decryption" in ai.programs


def test_parse_ai_statblock():
    sample_ai_text = """
Name: Null-Pointer
AI Type: Sapient
Willpower: 4, Logic: 5, Intuition: 5, Charisma: 3, Edge: 3
Attack: 4, Sleaze: 5, Data Processing: 6, Firewall: 5
Matrix Initiative: 11 + 4D6
Skills: Cracking 5, Electronics 6, Perception 4
AI Qualities: Home Ground (Grid), Emergent
Programs: Exploit, Stealth, Toolbox
Advanced Programs: Siphon, Crash
"""
    ai = parse_ai_statblock(sample_ai_text)
    assert ai.name == "Null-Pointer"
    assert ai.ai_type == "Sapient"
    assert ai.willpower == 4
    assert ai.logic == 5
    assert ai.attack == 4
    assert ai.sleaze == 5
    assert ai.data_processing == 6
    # 8 + ceil(4/2) = 8 + 2 = 10
    assert ai.matrix_condition_monitor == 10
    assert ai.skills["Cracking"] == 5
    assert len(ai.programs) == 3
    assert len(ai.advanced_programs) == 2


def test_calculate_modified_weapon_smartlink_and_apds():
    base_predator = WeaponStatBlock(
        name="Ares Predator VI",
        category="Heavy Pistols",
        damage="3P",
        attack_rating="10/10/8/-/-",
        firing_modes=["SA", "BF"],
        ammo_capacity=15,
        ammo_feed="c",
        availability=2,
        cost=750,
    )
    # Equip Internal Smartlink + Extended Clip + APDS ammo
    mod_pred = calculate_modified_weapon(
        base_predator,
        accessories=[
            {"name": "Smartlink", "mount": "internal"},
            {"name": "Extended Clip", "capacity_bonus": 15},
            {"name": "Silencer", "mount": "barrel"}
        ],
        ammo_type="APDS"
    )
    # Smartlink (+2 Close, +2 Near) + APDS (+2 all ranges)
    # Close: 10 + 2 + 2 = 14
    # Near: 10 + 2 + 2 = 14
    # Med: 8 + 2 = 10
    assert mod_pred.attack_rating == [14, 14, 10, 0, 0]
    assert mod_pred.ammo_capacity == 30
    assert mod_pred.damage == "3P"


def test_calculate_modified_weapon_explosive_and_sns():
    base_rifle = WeaponStatBlock(
        name="Ares Alpha",
        category="Assault Rifles",
        damage="4P",
        attack_rating="11/11/9/3/0",
        firing_modes=["SA", "BF", "FA"],
        ammo_capacity=42,
        ammo_feed="c",
    )
    # Explosive Ammo: +1 DV, -1 Close AR
    exp_rifle = calculate_modified_weapon(base_rifle, ammo_type="Explosive")
    assert exp_rifle.damage == "5P"
    assert exp_rifle.attack_rating[0] == 10  # 11 - 1 = 10

    # Stick-n-Shock Ammo: converts to S(e), -2 AR
    sns_rifle = calculate_modified_weapon(base_rifle, ammo_type="Stick-n-Shock")
    assert sns_rifle.damage == "4S(e)"
    assert sns_rifle.attack_rating == [9, 9, 7, 1, 0]


def test_format_weapon_card_for_yuriko():
    base_alpha = WeaponStatBlock(
        name="Ares Alpha Custom",
        category="Assault Rifles",
        damage="4P",
        attack_rating="11/11/9/3/0",
        firing_modes=["SA", "BF", "FA"],
        ammo_capacity=42,
        ammo_feed="c",
    )
    mod_alpha = calculate_modified_weapon(
        base_alpha,
        accessories=[{"name": "Internal Smartlink"}, {"name": "Gas-Vent 3"}],
        ammo_type="APDS"
    )
    card_md = format_weapon_card(
        mod_alpha,
        character_name="Yuriko",
        accessories=["Internal Smartlink", "Gas-Vent 3", "Underbarrel Grenade Launcher"],
        loaded_ammo="APDS (+2 AR)"
    )
    assert "### 🔫 Yuriko's Ares Alpha Custom (Assault Rifles)" in card_md
    assert "**Damage**: 4P" in card_md
    assert "**Attack Rating**: 15 / 15 / 11 / 5 / -" in card_md
    assert "**Accessories**: Internal Smartlink, Gas-Vent 3, Underbarrel Grenade Launcher" in card_md
    assert "**Loaded Ammunition**: APDS (+2 AR)" in card_md


def test_attribute_block_validation_errors():
    # Attribute cannot be zero or negative
    with pytest.raises(ValidationError):
        AttributeBlock(body=0)
    with pytest.raises(ValidationError):
        AttributeBlock(willpower=-2)
    # Essence must be > 0.0 and <= 6.0
    with pytest.raises(ValidationError):
        AttributeBlock(essence=0.0)
    with pytest.raises(ValidationError):
        AttributeBlock(essence=6.5)


def test_weapon_validation_errors():
    # Negative damage
    with pytest.raises(ValidationError):
        WeaponStatBlock(name="Bad Gun", damage="-3P")
    # Invalid damage format
    with pytest.raises(ValidationError):
        WeaponStatBlock(name="Bad Gun", damage="invalid")
    # Negative attack rating
    with pytest.raises(ValidationError):
        WeaponStatBlock(name="Bad Gun", damage="3P", attack_rating=[-1, 10, 8, 0, 0])
    # Negative cost
    with pytest.raises(ValidationError):
        WeaponStatBlock(name="Bad Gun", damage="3P", cost=-500)


def test_vehicle_validation_errors():
    # Zero handling
    with pytest.raises(ValidationError):
        VehicleStatBlock(name="Bad Drone", handling=0)
    # Zero top speed
    with pytest.raises(ValidationError):
        VehicleStatBlock(name="Bad Drone", top_speed=0)
    # Zero body
    with pytest.raises(ValidationError):
        VehicleStatBlock(name="Bad Drone", body=0)


def test_spell_and_complex_form_validation_errors():
    # Drain cannot be 0
    with pytest.raises(ValidationError):
        SpellStatBlock(name="Bad Spell", drain=0)
    # Fading cannot be 0
    with pytest.raises(ValidationError):
        ComplexFormStatBlock(name="Bad Form", fading=0)


def test_npc_validation_errors():
    # Professional Rating > 6
    with pytest.raises(ValidationError):
        NPCStatBlock(name="Bad NPC", professional_rating=7)
    # Defense Rating < 1
    with pytest.raises(ValidationError):
        NPCStatBlock(name="Bad NPC", defense_rating=0)


def test_format_statblock_markdown_all_types():
    w = WeaponStatBlock(name="Ares Predator VI", damage="3P", attack_rating=[10, 10, 8, 0, 0], firing_modes=["SA", "BF"], ammo_capacity=15, cost=750)
    w_md = format_statblock_markdown(w)
    assert "::: {.callout-note icon=false title=\"⚔️ WEAPON: Ares Predator VI" in w_md
    assert "| **3P** |" in w_md

    a = ArmorStatBlock(name="Armor Jacket", defense_rating=4, capacity=6, cost=1000)
    a_md = format_statblock_markdown(a)
    assert "::: {.callout-note icon=false title=\"🛡️ ARMOR: Armor Jacket\"}" in a_md
    assert "| **+4** |" in a_md

    v = VehicleStatBlock(name="Ares Roadmaster", handling=3, accel=12, speed_interval=15, top_speed=140, body=16, armor=12, pilot=2, sensor=2, seats=6, cost=55000)
    v_md = format_statblock_markdown(v)
    assert "::: {.callout-note icon=false title=\"🚗 VEHICLE / DRONE: Ares Roadmaster" in v_md
    assert "| 3 | 12 | 15/140 | 16 | 12 | 2 | 2 | 6 | 55,000¥ |" in v_md

    s = SpellStatBlock(name="Manabolt", spell_type="Mana", range="LOS", damage="P", duration="Instant", drain=4)
    s_md = format_statblock_markdown(s)
    assert "::: {.callout-note icon=false title=\"✨ SPELL: Manabolt" in s_md
    assert "| Mana | LOS | P | Instant | **4** |" in s_md

    cf = ComplexFormStatBlock(name="Cleaner", target="Persona", duration="Sustained", fading=2)
    cf_md = format_statblock_markdown(cf)
    assert "::: {.callout-note icon=false title=\"⚡ COMPLEX FORM: Cleaner\"}" in cf_md
    assert "| Persona | Sustained | **2** |" in cf_md

    sp = SpriteStatBlock(name="Crack Sprite", attack_formula="L", sleaze_formula="L+3", data_processing_formula="L+2", firewall_formula="L+1", skills=["Cracking"], powers=["Cookie"])
    sp_md = format_statblock_markdown(sp)
    assert "::: {.callout-note icon=false title=\"👾 SPRITE: Crack Sprite\"}" in sp_md

    spirit = SpiritStatBlock(name="Fire Spirit", body_formula="F+1", powers=["Elemental Attack (Fire)"])
    spirit_md = format_statblock_markdown(spirit)
    assert "::: {.callout-note icon=false title=\"🔥 SPIRIT: Fire Spirit\"}" in spirit_md

    ai = AIStatBlock(name="Mirage", attack=6, sleaze=7, data_processing=8, firewall=6, willpower=5, logic=7, intuition=6, charisma=4, edge=4)
    ai_md = format_statblock_markdown(ai)
    assert "::: {.callout-note icon=false title=\"🤖 AI ENTITY: Mirage" in ai_md

    npc = NPCStatBlock(name="Corp Guard", professional_rating=2, defense_rating=8)
    npc_md = format_statblock_markdown(npc)
    assert "::: {.callout-note icon=false title=\"👤 NPC: Corp Guard" in npc_md


def test_format_statblock_plaintext_all_types():
    w = WeaponStatBlock(name="Ares Predator VI", damage="3P", attack_rating=[10, 10, 8, 0, 0], firing_modes=["SA", "BF"], ammo_capacity=15, cost=750)
    w_txt = format_statblock_plaintext(w, width=76)
    for line in w_txt.strip().split("\n"):
        assert len(line) <= 76
    assert "WEAPON: ARES PREDATOR VI" in w_txt
    assert "3P" in w_txt

    v = VehicleStatBlock(name="Ares Roadmaster", handling=3, accel=12, speed_interval=15, top_speed=140, body=16, armor=12, pilot=2, sensor=2, seats=6, cost=55000)
    v_txt = format_statblock_plaintext(v, width=76)
    for line in v_txt.strip().split("\n"):
        assert len(line) <= 76
    assert "VEHICLE / DRONE: ARES ROADMASTER" in v_txt
