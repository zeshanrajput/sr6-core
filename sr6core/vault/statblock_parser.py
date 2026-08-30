"""
Stat Block & Table Parser for Shadowrun 6th Edition.
Parses Markdown tables and unstructured stat block text into typed Pydantic models:
- WeaponStatBlock
- ArmorStatBlock
- VehicleStatBlock
- SpellStatBlock
- NPCStatBlock
"""

import re
from typing import List, Dict, Any, Optional, Tuple
from sr6core.models import (
    WeaponStatBlock,
    ArmorStatBlock,
    VehicleStatBlock,
    SpellStatBlock,
    NPCStatBlock,
    AttributeBlock,
    ComplexFormStatBlock,
    SpriteStatBlock,
    SpiritStatBlock,
    AIStatBlock,
)


def parse_markdown_table_rows(table_text: str) -> List[Dict[str, str]]:
    """
    Parses a Markdown table string into a list of dictionaries mapping lowercase header -> cell text.
    """
    lines = [l.strip() for l in table_text.strip().split("\n") if l.strip()]
    table_lines = [l for l in lines if l.startswith("|") and l.endswith("|")]
    if len(table_lines) < 2:
        return []

    # Extract headers
    raw_headers = [h.strip() for h in table_lines[0].strip("|").split("|")]
    clean_headers = [re.sub(r"[^\w\s\(\)]", "", h).strip().lower() for h in raw_headers]

    # Find row start (skip separator line like |---|---|)
    start_idx = 1
    if len(table_lines) > 1 and re.match(r"^\|[\s\-:|]+\|$", table_lines[1]):
        start_idx = 2

    rows = []
    for line in table_lines[start_idx:]:
        cells = [c.strip() for c in line.strip("|").split("|")]
        if len(cells) < len(clean_headers):
            # Pad if needed
            cells.extend([""] * (len(clean_headers) - len(cells)))
        
        row_dict = {}
        for h, c in zip(clean_headers, cells):
            row_dict[h] = c
        rows.append(row_dict)

    return rows


def _parse_cost(val: str) -> int:
    """Parses cost string like '750¥', '1,200', '500 nuyen' into int."""
    cleaned = re.sub(r"[^\d]", "", val)
    return int(cleaned) if cleaned else 0


def _parse_avail_and_restriction(val: str) -> Tuple[int, Optional[str]]:
    """Parses availability and restriction like '2(L)', '4(F)', '3', '6L' -> (avail, restriction)."""
    val = val.strip()
    match = re.search(r"(\d+)\s*(?:\(?([LF])\)?)?", val, re.IGNORECASE)
    if match:
        avail = int(match.group(1))
        restr = match.group(2).upper() if match.group(2) else None
        return avail, restr
    return 1, None


def _parse_ammo(val: str) -> Tuple[Optional[int], Optional[str]]:
    """Parses ammo strings like '15(c)', '6(b)', '30(d)', '100(belt)' -> (capacity, feed)."""
    val = val.strip()
    match = re.search(r"(\d+)\s*(?:\(?([a-zA-Z]+)\)?)?", val)
    if match:
        cap = int(match.group(1))
        feed = match.group(2).lower() if match.group(2) else "c"
        return cap, feed
    return None, None


def parse_weapon_table(table_text: str, default_category: str = "General") -> List[WeaponStatBlock]:
    """
    Parses a weapon markdown table into a list of validated WeaponStatBlock instances.
    """
    rows = parse_markdown_table_rows(table_text)
    weapons = []

    for r in rows:
        # Match header variants
        name = r.get("weapon") or r.get("name") or r.get("item") or ""
        if not name or name.lower() in ("weapon", "name", "item"):
            continue

        damage = r.get("dv") or r.get("damage") or "3P"
        # Clean damage notation
        damage = damage.replace(" ", "").upper()
        if not re.search(r"[PS]", damage):
            damage = damage + "P"

        ar_val = r.get("attack rating") or r.get("ar") or r.get("attack rating ar") or ""
        # Check individual range columns if AR is not unified
        if not ar_val and any(k in r for k in ("close", "near", "medium", "far", "extreme")):
            close_v = r.get("close", "0")
            near_v = r.get("near", "0")
            med_v = r.get("medium", "0")
            far_v = r.get("far", "0")
            ext_v = r.get("extreme", "0")
            ar_val = f"{close_v}/{near_v}/{med_v}/{far_v}/{ext_v}"

        modes_raw = r.get("mode") or r.get("modes") or r.get("firing mode") or ""
        modes = [m.strip().upper() for m in re.split(r"[/,\s]+", modes_raw) if m.strip()]

        ammo_raw = r.get("ammo") or r.get("capacity") or ""
        ammo_cap, ammo_feed = _parse_ammo(ammo_raw)

        avail_raw = r.get("avail") or r.get("availability") or "1"
        avail, legal_restr = _parse_avail_and_restriction(avail_raw)

        cost_raw = r.get("cost") or r.get("price") or "0"
        cost = _parse_cost(cost_raw)

        category = r.get("category") or default_category

        weapon = WeaponStatBlock(
            name=name,
            category=category,
            damage=damage,
            attack_rating=ar_val,
            firing_modes=modes,
            ammo_capacity=ammo_cap,
            ammo_feed=ammo_feed,
            availability=avail,
            legal_restriction=legal_restr,
            cost=cost,
        )
        weapons.append(weapon)

    return weapons


def parse_armor_table(table_text: str) -> List[ArmorStatBlock]:
    """
    Parses an armor markdown table into a list of validated ArmorStatBlock instances.
    """
    rows = parse_markdown_table_rows(table_text)
    armors = []

    for r in rows:
        name = r.get("armor") or r.get("name") or r.get("item") or ""
        if not name or name.lower() in ("armor", "name", "item"):
            continue

        dr_raw = r.get("defense rating") or r.get("dr") or r.get("armor rating") or r.get("rating") or "0"
        dr_match = re.search(r"\+?(\d+)", dr_raw)
        dr = int(dr_match.group(1)) if dr_match else 0

        cap_raw = r.get("capacity") or "0"
        cap_match = re.search(r"(\d+)", cap_raw)
        cap = int(cap_match.group(1)) if cap_match else 0

        avail_raw = r.get("avail") or r.get("availability") or "1"
        avail, legal_restr = _parse_avail_and_restriction(avail_raw)

        cost_raw = r.get("cost") or r.get("price") or "0"
        cost = _parse_cost(cost_raw)

        features_raw = r.get("features") or r.get("notes") or ""
        features = [f.strip() for f in features_raw.split(",") if f.strip()]

        armor = ArmorStatBlock(
            name=name,
            defense_rating=dr,
            capacity=cap,
            availability=avail,
            legal_restriction=legal_restr,
            cost=cost,
            features=features,
        )
        armors.append(armor)

    return armors


def parse_vehicle_table(table_text: str, default_category: str = "Groundcraft") -> List[VehicleStatBlock]:
    """
    Parses a vehicle or drone markdown table into a list of validated VehicleStatBlock instances.
    """
    rows = parse_markdown_table_rows(table_text)
    vehicles = []

    for r in rows:
        name = r.get("vehicle") or r.get("drone") or r.get("name") or r.get("model") or ""
        if not name or name.lower() in ("vehicle", "drone", "name", "model"):
            continue

        handling_raw = r.get("handling") or "1"
        h_match = re.search(r"(\d+)(?:/(\d+))?", handling_raw)
        handling = int(h_match.group(1)) if h_match else 1
        handling_off = int(h_match.group(2)) if h_match and h_match.group(2) else None

        accel_raw = r.get("accel") or r.get("acceleration") or "1"
        accel_match = re.search(r"(\d+)", accel_raw)
        accel = int(accel_match.group(1)) if accel_match else 1

        speed_raw = r.get("speed") or r.get("speed interval / top speed") or r.get("top speed") or "10/100"
        s_match = re.search(r"(\d+)(?:/(\d+))?", speed_raw)
        speed_int = int(s_match.group(1)) if s_match else 10
        top_speed = int(s_match.group(2)) if s_match and s_match.group(2) else (speed_int * 10)

        body_raw = r.get("body") or r.get("bod") or "1"
        b_match = re.search(r"(\d+)", body_raw)
        body = int(b_match.group(1)) if b_match else 1

        armor_raw = r.get("armor") or r.get("arm") or "0"
        a_match = re.search(r"(\d+)", armor_raw)
        armor = int(a_match.group(1)) if a_match else 0

        pilot_raw = r.get("pilot") or r.get("plt") or "1"
        p_match = re.search(r"(\d+)", pilot_raw)
        pilot = int(p_match.group(1)) if p_match else 1

        sensor_raw = r.get("sensor") or r.get("sen") or "1"
        sen_match = re.search(r"(\d+)", sensor_raw)
        sensor = int(sen_match.group(1)) if sen_match else 1

        seats_raw = r.get("seats") or r.get("seating") or "1"
        seat_match = re.search(r"(\d+)", seats_raw)
        seats = int(seat_match.group(1)) if seat_match else 1

        avail_raw = r.get("avail") or r.get("availability") or "1"
        avail, legal_restr = _parse_avail_and_restriction(avail_raw)

        cost_raw = r.get("cost") or r.get("price") or "0"
        cost = _parse_cost(cost_raw)

        vehicle = VehicleStatBlock(
            name=name,
            category=r.get("category") or default_category,
            handling=handling,
            handling_offroad=handling_off,
            accel=accel,
            speed_interval=speed_int,
            top_speed=top_speed,
            body=body,
            armor=armor,
            pilot=pilot,
            sensor=sensor,
            seats=seats,
            availability=avail,
            legal_restriction=legal_restr,
            cost=cost,
        )
        vehicles.append(vehicle)

    return vehicles


def parse_spell_table(table_text: str, default_category: str = "Combat") -> List[SpellStatBlock]:
    """
    Parses a spell markdown table into a list of validated SpellStatBlock instances.
    """
    rows = parse_markdown_table_rows(table_text)
    spells = []

    for r in rows:
        name = r.get("spell") or r.get("name") or ""
        if not name or name.lower() in ("spell", "name"):
            continue

        type_raw = r.get("type") or "Physical"
        spell_type = "Mana" if type_raw.strip().upper().startswith("M") else "Physical"

        range_val = r.get("range") or "LOS"
        dmg_raw = r.get("damage") or r.get("dmg") or None
        damage = dmg_raw.strip().upper() if dmg_raw and dmg_raw.strip() not in ("-", "—", "") else None

        duration = r.get("duration") or "Instant"

        drain_raw = r.get("drain") or r.get("dv") or "3"
        drain_match = re.search(r"(\d+)", drain_raw)
        drain = int(drain_match.group(1)) if drain_match else 3

        spell = SpellStatBlock(
            name=name,
            category=r.get("category") or default_category,
            spell_type=spell_type,
            range=range_val,
            damage=damage,
            duration=duration,
            drain=drain,
        )
        spells.append(spell)

    return spells


def _split_outside_parens(text: str, delimiter: str = ",") -> List[str]:
    """Splits a string by delimiter only when not nested inside parentheses."""
    parts = []
    current = []
    paren_depth = 0
    for char in text:
        if char == "(":
            paren_depth += 1
        elif char == ")":
            paren_depth = max(0, paren_depth - 1)
        
        if char == delimiter and paren_depth == 0:
            part = "".join(current).strip()
            if part:
                parts.append(part)
            current = []
        else:
            current.append(char)
    if current:
        part = "".join(current).strip()
        if part:
            parts.append(part)
    return parts


def parse_npc_statblock(text: str) -> NPCStatBlock:
    """
    Parses raw text or Markdown describing an NPC or Grunt into a validated NPCStatBlock.
    Handles formats like:
      Name: Corp Sec Guard (PR 2)
      Attributes: B 4, A 4, R 3(4), S 3, W 3, L 2, I 3, C 2, EDG 2, ESS 5.4
      DR: 8, Init: 7 + 2D6
      Skills: Firearms 4, Close Combat 3, Perception 3
      Weapons: Ares Predator VI (3P, 10/10/8/-/-)
      Armor: Armor Vest (+2)
    """
    lines = [l.strip() for l in text.strip().split("\n") if l.strip()]

    name = "NPC"
    archetype = None
    pr = 1
    attrs = AttributeBlock()
    init = "6 + 1D6"
    dr = 6
    ar = None
    skills: Dict[str, int] = {}
    weapons: List[str] = []
    armor = None
    gear: List[str] = []
    qualities: List[str] = []
    augmentations: List[str] = []

    for line in lines:
        # 1. Name & Professional Rating
        if re.match(r"^(?:name|npc|character):\s*(.+)$", line, re.IGNORECASE):
            raw_name = re.sub(r"^(?:name|npc|character):\s*", "", line, flags=re.IGNORECASE).strip()
            pr_match = re.search(r"\(?\b(?:PR|Professional Rating)\s*[:=]?\s*(\d+)\)?", raw_name, re.IGNORECASE)
            if pr_match:
                pr = int(pr_match.group(1))
                name = re.sub(r"\(?\b(?:PR|Professional Rating)\s*[:=]?\s*\d+\)?", "", raw_name, flags=re.IGNORECASE).strip(" -:,()")
            else:
                name = raw_name

        elif re.match(r"^professional rating\s*[:=]?\s*(\d+)$", line, re.IGNORECASE):
            pr_match = re.search(r"(\d+)", line)
            if pr_match:
                pr = int(pr_match.group(1))

        # 2. Attributes Line (e.g. B 4, A 4, R 3(5), S 3, W 3, L 2, I 3, C 2, EDG 2, ESS 5.4)
        if re.search(r"\bB(?:OD)?\s*[:=]?\s*\d+", line, re.IGNORECASE) and re.search(r"\bA(?:GI)?\s*[:=]?\s*\d+", line, re.IGNORECASE):
            body_m = re.search(r"\bB(?:OD)?\s*[:=]?\s*(\d+)", line, re.IGNORECASE)
            agi_m = re.search(r"\bA(?:GI)?\s*[:=]?\s*(\d+)", line, re.IGNORECASE)
            rea_m = re.search(r"\bR(?:EA)?\s*[:=]?\s*(\d+)", line, re.IGNORECASE)
            str_m = re.search(r"\bS(?:TR)?\s*[:=]?\s*(\d+)", line, re.IGNORECASE)
            wil_m = re.search(r"\bW(?:IL)?\s*[:=]?\s*(\d+)", line, re.IGNORECASE)
            log_m = re.search(r"\bL(?:OG)?\s*[:=]?\s*(\d+)", line, re.IGNORECASE)
            int_m = re.search(r"\bI(?:NT)?\s*[:=]?\s*(\d+)", line, re.IGNORECASE)
            cha_m = re.search(r"\bC(?:HA)?\s*[:=]?\s*(\d+)", line, re.IGNORECASE)
            edg_m = re.search(r"\bEDG\s*[:=]?\s*(\d+)", line, re.IGNORECASE)
            ess_m = re.search(r"\bESS\s*[:=]?\s*([\d\.]+)", line, re.IGNORECASE)
            mag_m = re.search(r"\bMAG\s*[:=]?\s*(\d+)", line, re.IGNORECASE)
            res_m = re.search(r"\bRES\s*[:=]?\s*(\d+)", line, re.IGNORECASE)

            attrs = AttributeBlock(
                body=int(body_m.group(1)) if body_m else 1,
                agility=int(agi_m.group(1)) if agi_m else 1,
                reaction=int(rea_m.group(1)) if rea_m else 1,
                strength=int(str_m.group(1)) if str_m else 1,
                willpower=int(wil_m.group(1)) if wil_m else 1,
                logic=int(log_m.group(1)) if log_m else 1,
                intuition=int(int_m.group(1)) if int_m else 1,
                charisma=int(cha_m.group(1)) if cha_m else 1,
                edge=int(edg_m.group(1)) if edg_m else 1,
                essence=float(ess_m.group(1)) if ess_m else 6.0,
                magic=int(mag_m.group(1)) if mag_m else 0,
                resonance=int(res_m.group(1)) if res_m else 0,
            )

        # 3. Initiative
        if re.search(r"\b(?:Init|Initiative)\s*[:=]?\s*(\d+\s*\+\s*\d+D6|\d+)", line, re.IGNORECASE):
            init_m = re.search(r"\b(?:Init|Initiative)\s*[:=]?\s*([0-9\s\+Dd]+)", line, re.IGNORECASE)
            if init_m:
                init = init_m.group(1).strip()

        # 4. Defense Rating (DR)
        if re.search(r"\b(?:DR|Defense Rating)\s*[:=]?\s*(\d+)", line, re.IGNORECASE):
            dr_m = re.search(r"\b(?:DR|Defense Rating)\s*[:=]?\s*(\d+)", line, re.IGNORECASE)
            if dr_m:
                dr = int(dr_m.group(1))

        # 5. Attack Rating (AR)
        if re.search(r"\b(?:AR|Attack Rating)\s*[:=]?\s*(\d+)", line, re.IGNORECASE):
            ar_m = re.search(r"\b(?:AR|Attack Rating)\s*[:=]?\s*(\d+)", line, re.IGNORECASE)
            if ar_m:
                ar = int(ar_m.group(1))

        # 6. Skills
        if re.match(r"^skills\s*[:=]?\s*(.+)$", line, re.IGNORECASE):
            skills_text = re.sub(r"^skills\s*[:=]?\s*", "", line, flags=re.IGNORECASE)
            for item in _split_outside_parens(skills_text, ","):
                item = item.strip()
                s_match = re.match(r"^([A-Za-z\s\(\)]+?)\s+(\d+)$", item)
                if s_match:
                    s_name = s_match.group(1).strip()
                    s_val = int(s_match.group(2))
                    skills[s_name] = s_val

        # 7. Weapons
        if re.match(r"^weapons?\s*[:=]?\s*(.+)$", line, re.IGNORECASE):
            w_text = re.sub(r"^weapons?\s*[:=]?\s*", "", line, flags=re.IGNORECASE)
            for w in _split_outside_parens(w_text, ","):
                if w.strip():
                    weapons.append(w.strip())

        # 8. Armor
        if re.match(r"^armor\s*[:=]?\s*(.+)$", line, re.IGNORECASE):
            armor = re.sub(r"^armor\s*[:=]?\s*", "", line, flags=re.IGNORECASE).strip()

        # 9. Augmentations / Cyberware
        if re.match(r"^(?:augmentations?|cyberware|bioware)\s*[:=]?\s*(.+)$", line, re.IGNORECASE):
            aug_text = re.sub(r"^(?:augmentations?|cyberware|bioware)\s*[:=]?\s*", "", line, flags=re.IGNORECASE)
            for a in _split_outside_parens(aug_text, ","):
                if a.strip():
                    augmentations.append(a.strip())

        # 10. Gear
        if re.match(r"^gear\s*[:=]?\s*(.+)$", line, re.IGNORECASE):
            g_text = re.sub(r"^gear\s*[:=]?\s*", "", line, flags=re.IGNORECASE)
            for g in _split_outside_parens(g_text, ","):
                if g.strip():
                    gear.append(g.strip())

        # 11. Qualities
        if re.match(r"^qualities\s*[:=]?\s*(.+)$", line, re.IGNORECASE):
            q_text = re.sub(r"^qualities\s*[:=]?\s*", "", line, flags=re.IGNORECASE)
            for q in _split_outside_parens(q_text, ","):
                if q.strip():
                    qualities.append(q.strip())

    return NPCStatBlock(
        name=name,
        archetype=archetype,
        professional_rating=pr,
        attributes=attrs,
        initiative=init,
        defense_rating=dr,
        attack_rating=ar,
        skills=skills,
        qualities=qualities,
        augmentations=augmentations,
        weapons=weapons,
        armor=armor,
        gear=gear,
    )


def parse_complex_form_table(table_text: str) -> List[ComplexFormStatBlock]:
    """
    Parses a Technomancer Complex Form markdown table into validated ComplexFormStatBlock instances.
    """
    rows = parse_markdown_table_rows(table_text)
    forms = []

    for r in rows:
        name = r.get("complex form") or r.get("form") or r.get("name") or ""
        if not name or name.lower() in ("complex form", "form", "name"):
            continue

        target = r.get("target") or "Device"
        duration = r.get("duration") or "Instant"

        fading_raw = r.get("fading") or r.get("fv") or r.get("drain") or "2"
        f_match = re.search(r"(\d+)", fading_raw)
        fading = int(f_match.group(1)) if f_match else 2

        desc = r.get("description") or r.get("effect") or ""

        form = ComplexFormStatBlock(
            name=name,
            target=target,
            duration=duration,
            fading=fading,
            description=desc,
        )
        forms.append(form)

    return forms


def parse_sprite_table(table_text: str) -> List[SpriteStatBlock]:
    """
    Parses a Matrix Sprite summary table into validated SpriteStatBlock instances.
    """
    rows = parse_markdown_table_rows(table_text)
    sprites = []

    for r in rows:
        name = r.get("sprite") or r.get("type") or r.get("name") or ""
        if not name or name.lower() in ("sprite", "type", "name"):
            continue

        atk = r.get("attack") or r.get("att") or r.get("a") or "L"
        slz = r.get("sleaze") or r.get("slz") or r.get("s") or "L"
        dp = r.get("data processing") or r.get("dp") or r.get("d") or "L"
        fw = r.get("firewall") or r.get("fw") or r.get("f") or "L"
        init = r.get("initiative") or "(DP * 2) + 4D6"

        skills_raw = r.get("skills") or ""
        skills = [s.strip() for s in _split_outside_parens(skills_raw, ",") if s.strip()]

        powers_raw = r.get("powers") or r.get("sprite powers") or ""
        powers = [p.strip() for p in _split_outside_parens(powers_raw, ",") if p.strip()]

        opt_raw = r.get("optional powers") or ""
        opt_powers = [o.strip() for o in _split_outside_parens(opt_raw, ",") if o.strip()]

        sprite = SpriteStatBlock(
            name=name,
            sprite_type=name.replace("Sprite", "").strip() or "Crack",
            attack_formula=atk,
            sleaze_formula=slz,
            data_processing_formula=dp,
            firewall_formula=fw,
            initiative=init,
            skills=skills,
            powers=powers,
            optional_powers=opt_powers,
        )
        sprites.append(sprite)

    return sprites


def parse_spirit_table(table_text: str) -> List[SpiritStatBlock]:
    """
    Parses a Magical Spirit summary table into validated SpiritStatBlock instances.
    """
    rows = parse_markdown_table_rows(table_text)
    spirits = []

    for r in rows:
        name = r.get("spirit") or r.get("type") or r.get("name") or ""
        if not name or name.lower() in ("spirit", "type", "name"):
            continue

        bod = r.get("body") or r.get("bod") or r.get("b") or "F"
        agi = r.get("agility") or r.get("agi") or r.get("a") or "F"
        rea = r.get("reaction") or r.get("rea") or r.get("r") or "F"
        st = r.get("strength") or r.get("str") or r.get("s") or "F"
        wil = r.get("willpower") or r.get("wil") or r.get("w") or "F"
        log = r.get("logic") or r.get("log") or r.get("l") or "F"
        intu = r.get("intuition") or r.get("int") or r.get("i") or "F"
        cha = r.get("charisma") or r.get("cha") or r.get("c") or "F"
        ess = r.get("essence") or r.get("ess") or "F"
        init = r.get("initiative") or "(Reaction + Intuition) + 2D6"

        skills_raw = r.get("skills") or ""
        skills = [s.strip() for s in _split_outside_parens(skills_raw, ",") if s.strip()]

        powers_raw = r.get("powers") or r.get("spirit powers") or ""
        powers = [p.strip() for p in _split_outside_parens(powers_raw, ",") if p.strip()]

        opt_raw = r.get("optional powers") or ""
        opt_powers = [o.strip() for o in _split_outside_parens(opt_raw, ",") if o.strip()]

        spirit = SpiritStatBlock(
            name=name,
            spirit_type=name.replace("Spirit", "").replace("of", "").strip() or "Air",
            body_formula=bod,
            agility_formula=agi,
            reaction_formula=rea,
            strength_formula=st,
            willpower_formula=wil,
            logic_formula=log,
            intuition_formula=intu,
            charisma_formula=cha,
            essence_formula=ess,
            initiative=init,
            skills=skills,
            powers=powers,
            optional_powers=opt_powers,
        )
        spirits.append(spirit)

    return spirits


def parse_ai_statblock(text: str) -> AIStatBlock:
    """
    Parses an Artificial Intelligence / E-Ghost / Proto-Sapient stat block for SR6.
    - Extracts mental attributes (W, L, I, C, EDG) and Matrix persona attributes (A, S, D, F).
    - Calculates single Matrix Condition Monitor: ceil(Willpower / 2) + 8.
    - Extracts Matrix Initiative, AI Qualities, and loaded Programs.
    """
    lines = [l.strip() for l in text.strip().split("\n") if l.strip()]

    name = "AI Entity"
    ai_type = "Sapient"
    wil = 3
    log = 4
    intu = 4
    cha = 3
    edg = 2

    atk = 2
    slz = 2
    dp = 4
    fw = 4
    init = "8 + 4D6"
    home = None
    skills: Dict[str, int] = {}
    ai_qualities: List[str] = []
    programs: List[str] = []
    adv_programs: List[str] = []

    for line in lines:
        if re.match(r"^(?:name|ai|entity):\s*(.+)$", line, re.IGNORECASE):
            name = re.sub(r"^(?:name|ai|entity):\s*", "", line, flags=re.IGNORECASE).strip()

        elif re.match(r"^(?:type|ai type):\s*(.+)$", line, re.IGNORECASE):
            ai_type = re.sub(r"^(?:type|ai type):\s*", "", line, flags=re.IGNORECASE).strip()

        # Mental Attributes (W, L, I, C, EDG)
        if re.search(r"\b(?:W|WIL|Willpower)\s*[:=]?\s*\d+", line, re.IGNORECASE):
            w_m = re.search(r"\b(?:W|WIL|Willpower)\s*[:=]?\s*(\d+)", line, re.IGNORECASE)
            l_m = re.search(r"\b(?:L|LOG|Logic)\s*[:=]?\s*(\d+)", line, re.IGNORECASE)
            i_m = re.search(r"\b(?:I|INT|Intuition)\s*[:=]?\s*(\d+)", line, re.IGNORECASE)
            c_m = re.search(r"\b(?:C|CHA|Charisma)\s*[:=]?\s*(\d+)", line, re.IGNORECASE)
            e_m = re.search(r"\b(?:E|EDG|Edge)\s*[:=]?\s*(\d+)", line, re.IGNORECASE)
            if w_m: wil = int(w_m.group(1))
            if l_m: log = int(l_m.group(1))
            if i_m: intu = int(i_m.group(1))
            if c_m: cha = int(c_m.group(1))
            if e_m: edg = int(e_m.group(1))

        # Matrix / Persona Attributes (A, S, D, F)
        if re.search(r"\b(?:A|ATK|Attack)\s*[:=]?\s*\d+", line, re.IGNORECASE) and re.search(r"\b(?:S|SLZ|Sleaze)\s*[:=]?\s*\d+", line, re.IGNORECASE):
            a_m = re.search(r"\b(?:A|ATK|Attack)\s*[:=]?\s*(\d+)", line, re.IGNORECASE)
            s_m = re.search(r"\b(?:S|SLZ|Sleaze)\s*[:=]?\s*(\d+)", line, re.IGNORECASE)
            d_m = re.search(r"\b(?:D|DP|Data Processing)\s*[:=]?\s*(\d+)", line, re.IGNORECASE)
            f_m = re.search(r"\b(?:F|FW|Firewall)\s*[:=]?\s*(\d+)", line, re.IGNORECASE)
            if a_m: atk = int(a_m.group(1))
            if s_m: slz = int(s_m.group(1))
            if d_m: dp = int(d_m.group(1))
            if f_m: fw = int(f_m.group(1))

        # Initiative
        if re.search(r"\b(?:Init|Initiative|Matrix Initiative)\s*[:=]?\s*(.+)$", line, re.IGNORECASE):
            init_m = re.search(r"\b(?:Init|Initiative|Matrix Initiative)\s*[:=]?\s*([0-9\s\+Dd]+)", line, re.IGNORECASE)
            if init_m:
                init = init_m.group(1).strip()

        # Skills
        if re.match(r"^skills\s*[:=]?\s*(.+)$", line, re.IGNORECASE):
            skills_text = re.sub(r"^skills\s*[:=]?\s*", "", line, flags=re.IGNORECASE)
            for item in _split_outside_parens(skills_text, ","):
                item = item.strip()
                s_match = re.match(r"^([A-Za-z\s\(\)]+?)\s+(\d+)$", item)
                if s_match:
                    skills[s_match.group(1).strip()] = int(s_match.group(2))

        # AI Qualities
        if re.match(r"^(?:ai qualities|qualities)\s*[:=]?\s*(.+)$", line, re.IGNORECASE):
            q_text = re.sub(r"^(?:ai qualities|qualities)\s*[:=]?\s*", "", line, flags=re.IGNORECASE)
            ai_qualities = [q.strip() for q in _split_outside_parens(q_text, ",") if q.strip()]

        # Programs
        if re.match(r"^(?:programs|loaded programs)\s*[:=]?\s*(.+)$", line, re.IGNORECASE):
            p_text = re.sub(r"^(?:programs|loaded programs)\s*[:=]?\s*", "", line, flags=re.IGNORECASE)
            programs = [p.strip() for p in _split_outside_parens(p_text, ",") if p.strip()]

        # Advanced Programs
        if re.match(r"^(?:advanced programs)\s*[:=]?\s*(.+)$", line, re.IGNORECASE):
            ap_text = re.sub(r"^(?:advanced programs)\s*[:=]?\s*", "", line, flags=re.IGNORECASE)
            adv_programs = [ap.strip() for ap in _split_outside_parens(ap_text, ",") if ap.strip()]

    # Condition Monitor calculation (ceil(Willpower / 2) + 8)
    cond_monitor = 8 + ((wil + 1) // 2)

    return AIStatBlock(
        name=name,
        ai_type=ai_type,
        willpower=wil,
        logic=log,
        intuition=intu,
        charisma=cha,
        edge=edg,
        attack=atk,
        sleaze=slz,
        data_processing=dp,
        firewall=fw,
        matrix_condition_monitor=cond_monitor,
        matrix_initiative=init,
        home_node=home,
        skills=skills,
        ai_qualities=ai_qualities,
        programs=programs,
        advanced_programs=adv_programs,
    )


def calculate_modified_weapon(
    base_weapon: WeaponStatBlock,
    accessories: Optional[List[Dict[str, Any]]] = None,
    ammo_type: Optional[str] = None
) -> WeaponStatBlock:
    """
    Computes effective post-modification stats for a weapon:
    - Smartlink / Smartgun: +2 Attack Rating at Close/Near ranges.
    - Extended Barrel: +1 AR at Medium/Far/Extreme, -1 AR at Close.
    - Extended Magazine / Drum: Multiplies/increases ammo capacity.
    - APDS: +2 AR across all non-zero ranges.
    - Explosive Ammunition: +1 Damage Value, -1 AR at Close.
    - Stick-n-Shock: Converts damage to Stun (Electricity), -2 AR.
    - Gel Rounds: Converts damage to Stun, grants +2 Defense Rating to target.
    """
    w_dict = base_weapon.model_dump()
    ar = list(base_weapon.attack_rating)
    while len(ar) < 5:
        ar.append(0)

    damage = base_weapon.damage
    ammo_cap = base_weapon.ammo_capacity
    modes = list(base_weapon.firing_modes)

    acc_list = accessories or []
    acc_names = [a.get("name", "").lower() if isinstance(a, dict) else str(a).lower() for a in acc_list]

    # 1. Smartlink / Smartgun modifications
    if any("smartlink" in a or "smartgun" in a for a in acc_names):
        if len(ar) > 0 and ar[0] > 0: ar[0] += 2
        if len(ar) > 1 and ar[1] > 0: ar[1] += 2

    # 2. Extended Barrel
    if any("extended barrel" in a for a in acc_names):
        if len(ar) > 0 and ar[0] > 0: ar[0] = max(0, ar[0] - 1)
        for i in range(2, len(ar)):
            if ar[i] > 0: ar[i] += 1

    # 3. Extended Magazine / Drum
    for a in acc_list:
        if isinstance(a, dict):
            bonus = a.get("capacity_bonus")
            if bonus:
                ammo_cap = (ammo_cap or 0) + int(bonus)
            elif "extended clip" in a.get("name", "").lower() or "extended magazine" in a.get("name", "").lower():
                if ammo_cap: ammo_cap = int(ammo_cap * 1.5)
            elif "drum" in a.get("name", "").lower():
                if ammo_cap: ammo_cap = ammo_cap * 2

    # 4. Ammunition Modifiers
    if ammo_type:
        a_type = ammo_type.lower()
        if "apds" in a_type:
            # +2 AR across all active ranges
            ar = [x + 2 if x > 0 else 0 for x in ar]
        elif "explosive" in a_type:
            # +1 DV, -1 AR Close
            m = re.match(r"^(\d+)([PS])(.*)$", damage)
            if m:
                val = int(m.group(1)) + 1
                damage = f"{val}{m.group(2)}{m.group(3)}"
            if len(ar) > 0 and ar[0] > 0: ar[0] = max(0, ar[0] - 1)
        elif "stick-n-shock" in a_type or "sns" in a_type:
            # Convert to Stun/Electricity, -2 AR
            m = re.match(r"^(\d+)[PS](.*)$", damage)
            if m:
                damage = f"{m.group(1)}S(e){m.group(2)}"
            ar = [max(0, x - 2) if x > 0 else 0 for x in ar]
        elif "gel" in a_type:
            # Convert to Stun
            m = re.match(r"^(\d+)[PS](.*)$", damage)
            if m:
                damage = f"{m.group(1)}S{m.group(2)}"

    w_dict["damage"] = damage
    w_dict["attack_rating"] = ar
    w_dict["ammo_capacity"] = ammo_cap
    w_dict["firing_modes"] = modes

    return WeaponStatBlock(**w_dict)


def format_weapon_card(
    weapon: WeaponStatBlock,
    character_name: Optional[str] = None,
    accessories: Optional[List[str]] = None,
    loaded_ammo: Optional[str] = None
) -> str:
    """
    Renders a clean, formatted Markdown card block for character dossiers, Quarto appendices, and card stacks.
    """
    header_title = f"{character_name}'s {weapon.name}" if character_name else weapon.name
    modes_str = "/".join(weapon.firing_modes) if weapon.firing_modes else "SS"
    ammo_str = f"{weapon.ammo_capacity or '-'}({weapon.ammo_feed or 'c'})"
    ar_str = " / ".join(str(x) if x > 0 else "-" for x in weapon.attack_rating)

    lines = [
        f"### 🔫 {header_title} ({weapon.category})",
        f"> **Damage**: {weapon.damage} | **Modes**: {modes_str} | **Ammo**: {ammo_str}",
        f"> **Attack Rating**: {ar_str} *(Close / Near / Med / Far / Ext)*",
    ]

    if accessories:
        lines.append(f"> **Accessories**: {', '.join(accessories)}")
    if loaded_ammo:
        lines.append(f"> **Loaded Ammunition**: {loaded_ammo}")

    return "\n".join(lines) + "\n"


def format_statblock_markdown(model: Any, title: Optional[str] = None) -> str:
    """
    Renders an authentic Shadowrun 6E book-style Markdown callout block for Quarto books & HTML appendices.
    """
    if isinstance(model, WeaponStatBlock):
        callout_title = title or f"⚔️ WEAPON: {model.name} ({model.category})"
        is_melee = model.category.lower() in ["melee", "unarmed", "exotic_melee", "close_combat"] or any(
            x in model.name.lower() for x in ["cesta", "cestas", "whip", "dagger", "sword", "knife", "blade", "unarmed", "fist", "club", "staff"]
        )
        if is_melee:
            modes_str = "—"
            ammo_str = "—"
        else:
            modes_str = " / ".join(model.firing_modes) if model.firing_modes else "SS"
            ammo_str = f"{model.ammo_capacity or '—'}({model.ammo_feed or 'c'})"
        ar_str = " / ".join(str(x) if x > 0 else "—" for x in model.attack_rating)
        restr = f"({model.legal_restriction})" if model.legal_restriction else ""
        cost_str = f"{model.cost:,}¥" if model.cost else "—"

        return (
            f"::: {{.callout-note icon=false title=\"{callout_title}\"}}\n"
            f"| Damage | Attack Rating (C/N/M/F/E) | Modes | Ammo | Avail | Cost |\n"
            f"| :--- | :--- | :--- | :--- | :--- | :--- |\n"
            f"| **{model.damage}** | {ar_str} | {modes_str} | {ammo_str} | {model.availability}{restr} | {cost_str} |\n"
            f":::\n"
        )

    elif isinstance(model, ArmorStatBlock):
        callout_title = title or f"🛡️ ARMOR: {model.name}"
        restr = f"({model.legal_restriction})" if model.legal_restriction else ""
        cost_str = f"{model.cost:,}¥" if model.cost else "—"
        feat_str = ", ".join(model.features) if model.features else "Standard"

        return (
            f"::: {{.callout-note icon=false title=\"{callout_title}\"}}\n"
            f"| Defense Rating | Capacity | Avail | Cost | Features |\n"
            f"| :--- | :--- | :--- | :--- | :--- |\n"
            f"| **+{model.defense_rating}** | {model.capacity} | {model.availability}{restr} | {cost_str} | {feat_str} |\n"
            f":::\n"
        )

    elif isinstance(model, VehicleStatBlock):
        callout_title = title or f"🚗 VEHICLE / DRONE: {model.name} ({model.category})"
        h_str = f"{model.handling}/{model.handling_offroad}" if model.handling_offroad else str(model.handling)
        spd_str = f"{model.speed_interval}/{model.top_speed}"
        cost_str = f"{model.cost:,}¥" if model.cost else "—"

        return (
            f"::: {{.callout-note icon=false title=\"{callout_title}\"}}\n"
            f"| Handling | Accel | Speed | Body | Armor | Pilot | Sensor | Seats | Cost |\n"
            f"| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |\n"
            f"| {h_str} | {model.accel} | {spd_str} | {model.body} | {model.armor} | {model.pilot} | {model.sensor} | {model.seats or 0} | {cost_str} |\n"
            f":::\n"
        )

    elif isinstance(model, SpellStatBlock):
        callout_title = title or f"✨ SPELL: {model.name} ({model.category})"
        dmg_str = model.damage or "—"

        return (
            f"::: {{.callout-note icon=false title=\"{callout_title}\"}}\n"
            f"| Type | Range | Damage | Duration | Drain Value |\n"
            f"| :--- | :--- | :--- | :--- | :--- |\n"
            f"| {model.spell_type} | {model.range} | {dmg_str} | {model.duration} | **{model.drain}** |\n"
            f":::\n"
        )

    elif isinstance(model, ComplexFormStatBlock):
        callout_title = title or f"⚡ COMPLEX FORM: {model.name}"

        return (
            f"::: {{.callout-note icon=false title=\"{callout_title}\"}}\n"
            f"| Target | Duration | Fading Value |\n"
            f"| :--- | :--- | :--- |\n"
            f"| {model.target} | {model.duration} | **{model.fading}** |\n\n"
            f"{model.description or ''}\n"
            f":::\n"
        )

    elif isinstance(model, SpriteStatBlock):
        callout_title = title or f"👾 SPRITE: {model.name}"
        skills_str = ", ".join(model.skills) if model.skills else "—"
        powers_str = ", ".join(model.powers) if model.powers else "—"

        return (
            f"::: {{.callout-note icon=false title=\"{callout_title}\"}}\n"
            f"| Attack | Sleaze | Data Processing | Firewall | Initiative |\n"
            f"| :--- | :--- | :--- | :--- | :--- |\n"
            f"| {model.attack_formula} | {model.sleaze_formula} | {model.data_processing_formula} | {model.firewall_formula} | {model.initiative} |\n\n"
            f"* **Skills**: {skills_str}  \n"
            f"* **Powers**: {powers_str}\n"
            f":::\n"
        )

    elif isinstance(model, SpiritStatBlock):
        callout_title = title or f"🔥 SPIRIT: {model.name}"
        skills_str = ", ".join(model.skills) if model.skills else "—"
        powers_str = ", ".join(model.powers) if model.powers else "—"

        return (
            f"::: {{.callout-note icon=false title=\"{callout_title}\"}}\n"
            f"| BOD | AGI | REA | STR | WIL | LOG | INT | CHA | ESS | Initiative |\n"
            f"| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |\n"
            f"| {model.body_formula} | {model.agility_formula} | {model.reaction_formula} | {model.strength_formula} | {model.willpower_formula} | {model.logic_formula} | {model.intuition_formula} | {model.charisma_formula} | {model.essence_formula} | {model.initiative} |\n\n"
            f"* **Skills**: {skills_str}  \n"
            f"* **Powers**: {powers_str}\n"
            f":::\n"
        )

    elif isinstance(model, AIStatBlock):
        callout_title = title or f"🤖 AI ENTITY: {model.name} ({model.ai_type})"
        skills_str = ", ".join(f"{k} {v}" for k, v in model.skills.items()) if model.skills else "—"
        progs_str = ", ".join(model.programs) if model.programs else "—"

        return (
            f"::: {{.callout-note icon=false title=\"{callout_title}\"}}\n"
            f"| Attack | Sleaze | Data Processing | Firewall | WIL | LOG | INT | CHA | EDG |\n"
            f"| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |\n"
            f"| {model.attack} | {model.sleaze} | {model.data_processing} | {model.firewall} | {model.willpower} | {model.logic} | {model.intuition} | {model.charisma} | {model.edge} |\n\n"
            f"* **Matrix Condition Monitor**: {model.matrix_condition_monitor} boxes  \n"
            f"* **Matrix Initiative**: {model.matrix_initiative}  \n"
            f"* **Skills**: {skills_str}  \n"
            f"* **Programs**: {progs_str}\n"
            f":::\n"
        )

    elif isinstance(model, NPCStatBlock):
        callout_title = title or f"👤 NPC: {model.name} (PR {model.professional_rating})"
        a = model.attributes
        skills_str = ", ".join(f"{k} {v}" for k, v in model.skills.items()) if model.skills else "—"
        weapons_str = ", ".join(model.weapons) if model.weapons else "—"
        armor_str = model.armor or "Street Clothes"
        aug_str = ", ".join(model.augmentations) if model.augmentations else "None"

        return (
            f"::: {{.callout-note icon=false title=\"{callout_title}\"}}\n"
            f"| BOD | AGI | REA | STR | WIL | LOG | INT | CHA | EDG | ESS |\n"
            f"| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |\n"
            f"| {a.body} | {a.agility} | {a.reaction} | {a.strength} | {a.willpower} | {a.logic} | {a.intuition} | {a.charisma} | {a.edge} | {a.essence:.1f} |\n\n"
            f"* **Initiative**: {model.initiative} | **Defense Rating**: {model.defense_rating}" + (f" | **Attack Rating**: {model.attack_rating}" if model.attack_rating else "") + "  \n"
            f"* **Skills**: {skills_str}  \n"
            f"* **Weapons**: {weapons_str}  \n"
            f"* **Armor**: {armor_str}  \n"
            f"* **Augmentations**: {aug_str}\n"
            f":::\n"
        )

    return f"```yaml\n{model}\n```\n"


def format_statblock_plaintext(model: Any, title: Optional[str] = None, width: int = 76) -> str:
    """
    Renders an authentic, cleanly bordered ASCII stat block strictly within terminal/print width.
    """
    border = "=" * width
    divider = "-" * width

    if isinstance(model, WeaponStatBlock):
        header = title or f"WEAPON: {model.name.upper()} ({model.category})"
        modes_str = "/".join(model.firing_modes) if model.firing_modes else "SS"
        ammo_str = f"{model.ammo_capacity or '-'}({model.ammo_feed or 'c'})"
        ar_str = " / ".join(str(x) if x > 0 else "-" for x in model.attack_rating)
        restr = f" ({model.legal_restriction})" if model.legal_restriction else ""
        cost_str = f"{model.cost:,}¥" if model.cost else "-"

        lines = [
            border,
            f" {header}",
            divider,
            f"  Damage: {model.damage:<6} | Modes: {modes_str:<8} | Ammo: {ammo_str:<8} | Avail: {model.availability}{restr}",
            f"  Attack Rating: {ar_str} (C/N/M/F/E) | Cost: {cost_str}",
            border,
        ]
        return "\n".join(lines) + "\n"

    elif isinstance(model, ArmorStatBlock):
        header = title or f"ARMOR: {model.name.upper()}"
        restr = f" ({model.legal_restriction})" if model.legal_restriction else ""
        cost_str = f"{model.cost:,}¥" if model.cost else "-"
        feat_str = ", ".join(model.features) if model.features else "Standard"

        lines = [
            border,
            f" {header}",
            divider,
            f"  Defense Rating: +{model.defense_rating:<4} | Capacity: {model.capacity:<4} | Avail: {model.availability}{restr} | Cost: {cost_str}",
            f"  Features      : {feat_str}",
            border,
        ]
        return "\n".join(lines) + "\n"

    elif isinstance(model, VehicleStatBlock):
        header = title or f"VEHICLE / DRONE: {model.name.upper()} ({model.category})"
        h_str = f"{model.handling}/{model.handling_offroad}" if model.handling_offroad else str(model.handling)
        spd_str = f"{model.speed_interval}/{model.top_speed}"
        cost_str = f"{model.cost:,}¥" if model.cost else "-"

        lines = [
            border,
            f" {header}",
            divider,
            f"  Handling: {h_str:<5} | Accel: {model.accel:<4} | Speed: {spd_str:<8} | Body: {model.body:<3} | Armor: {model.armor}",
            f"  Pilot   : {model.pilot:<5} | Sensor: {model.sensor:<3} | Seats: {model.seats or 0:<8} | Cost: {cost_str}",
            border,
        ]
        return "\n".join(lines) + "\n"

    elif isinstance(model, SpellStatBlock):
        header = title or f"SPELL: {model.name.upper()} ({model.category})"
        lines = [
            border,
            f" {header}",
            divider,
            f"  Type: {model.spell_type:<8} | Range: {model.range:<8} | Damage: {model.damage or '-':<4} | Duration: {model.duration}",
            f"  Drain Value : {model.drain} DV",
            border,
        ]
        return "\n".join(lines) + "\n"

    elif isinstance(model, ComplexFormStatBlock):
        header = title or f"COMPLEX FORM: {model.name.upper()}"
        lines = [
            border,
            f" {header}",
            divider,
            f"  Target: {model.target:<10} | Duration: {model.duration:<10} | Fading Value: {model.fading} FV",
        ]
        if model.description:
            lines.append(f"  Effect: {model.description}")
        lines.append(border)
        return "\n".join(lines) + "\n"

    elif isinstance(model, SpriteStatBlock):
        header = title or f"SPRITE: {model.name.upper()}"
        skills_str = ", ".join(model.skills) if model.skills else "-"
        powers_str = ", ".join(model.powers) if model.powers else "-"

        lines = [
            border,
            f" {header}",
            divider,
            f"  ATK: {model.attack_formula:<4} | SLZ: {model.sleaze_formula:<4} | DP: {model.data_processing_formula:<4} | FW: {model.firewall_formula:<4} | Init: {model.initiative}",
            f"  Skills: {skills_str}",
            f"  Powers: {powers_str}",
            border,
        ]
        return "\n".join(lines) + "\n"

    elif isinstance(model, SpiritStatBlock):
        header = title or f"SPIRIT: {model.name.upper()}"
        skills_str = ", ".join(model.skills) if model.skills else "-"
        powers_str = ", ".join(model.powers) if model.powers else "-"

        lines = [
            border,
            f" {header}",
            divider,
            f"  BOD: {model.body_formula:<3} AGI: {model.agility_formula:<3} REA: {model.reaction_formula:<3} STR: {model.strength_formula:<3} WIL: {model.willpower_formula:<3} LOG: {model.logic_formula:<3} INT: {model.intuition_formula:<3} CHA: {model.charisma_formula:<3}",
            f"  Initiative : {model.initiative}",
            f"  Skills     : {skills_str}",
            f"  Powers     : {powers_str}",
            border,
        ]
        return "\n".join(lines) + "\n"

    elif isinstance(model, AIStatBlock):
        header = title or f"AI ENTITY: {model.name.upper()} ({model.ai_type})"
        skills_str = ", ".join(f"{k} {v}" for k, v in model.skills.items()) if model.skills else "-"
        progs_str = ", ".join(model.programs) if model.programs else "-"

        lines = [
            border,
            f" {header}",
            divider,
            f"  ATK: {model.attack:<2} | SLZ: {model.sleaze:<2} | DP: {model.data_processing:<2} | FW: {model.firewall:<2} | WIL: {model.willpower:<2} | LOG: {model.logic:<2} | INT: {model.intuition:<2} | CHA: {model.charisma:<2} | EDG: {model.edge}",
            f"  Matrix Condition Monitor : {model.matrix_condition_monitor} boxes",
            f"  Matrix Initiative        : {model.matrix_initiative}",
            f"  Skills   : {skills_str}",
            f"  Programs : {progs_str}",
            border,
        ]
        return "\n".join(lines) + "\n"

    elif isinstance(model, NPCStatBlock):
        header = title or f"NPC: {model.name.upper()} (PR {model.professional_rating})"
        a = model.attributes
        skills_str = ", ".join(f"{k} {v}" for k, v in model.skills.items()) if model.skills else "-"
        weaps_str = ", ".join(model.weapons) if model.weapons else "-"

        lines = [
            border,
            f" {header}",
            divider,
            f"  BOD: {a.body:<2} | AGI: {a.agility:<2} | REA: {a.reaction:<2} | STR: {a.strength:<2} | WIL: {a.willpower:<2} | LOG: {a.logic:<2} | INT: {a.intuition:<2} | CHA: {a.charisma:<2} | EDG: {a.edge}",
            f"  Initiative: {model.initiative:<14} | DR: {model.defense_rating:<4} | AR: {model.attack_rating or '-'}",
            f"  Skills  : {skills_str}",
            f"  Weapons : {weaps_str}",
            f"  Armor   : {model.armor or 'Street Clothes'}",
            border,
        ]
        return "\n".join(lines) + "\n"

    return f"{model}\n"


def extract_statblocks_from_rule(content: str) -> List[Any]:
    """
    Extracts all typed Pydantic stat blocks from a rule chunk content.
    Attempts parsing Markdown tables or prose stat blocks.
    """
    if not content:
        return []

    statblocks = []

    # 1. Try table parsers
    for parser in [
        parse_weapon_table,
        parse_armor_table,
        parse_spell_table,
        parse_complex_form_table,
        parse_vehicle_table,
        parse_sprite_table,
        parse_spirit_table,
        parse_ai_table,
    ]:
        try:
            res = parser(content)
            if res:
                statblocks.extend(res)
        except Exception:
            pass

    # 2. If no table matches, try NPC stat block
    if not statblocks:
        try:
            npc = parse_npc_statblock(content)
            if npc:
                statblocks.append(npc)
        except Exception:
            pass

    return statblocks
