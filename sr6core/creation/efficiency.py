"""
Build Efficiency & Total Equivalent Karma (TEK) Engine for SR6 Core.
Calculates the post-chargen Karma value of character builds, Skillwires/Autosofts dividends,
and validates unspent resource limits (cash <= 5,000¥, karma <= 5).

========================================================================================
ECONOMIC & MECHANICAL ASSUMPTIONS (THE CONVERSION LEDGER)
========================================================================================

1. ATTRIBUTES PROGRESSION (Triangular):
   - In SR6 CRB p. 68 (Advancement Costs Table), raising an attribute costs New Rating * 5.
   - Raising an attribute from 1 to R costs: sum(r * 5 for r in 2..R).
     Rating 2: 10k | Rating 5: 70k | Rating 6: 100k | Rating 9: 220k | Rating 10: 270k.

2. AUGMENTATION ATTRIBUTE SAVINGS (High-Bracket Marginal Delta):
   - When augmentations (cyberlimbs, muscle replacement, bone lacing) increase an attribute
     from natural N to augmented A, the build saves the HIGHEST marginal Karma tiers:
     sum(r * 5 for r in (N+1)..A).
   - Example: Venn's cyberarms pushing Agility from 1 to 7 saves:
     10 + 15 + 20 + 25 + 30 + 35 = 135 Karma!

3. SKILLS PROGRESSION (Triangular):
   - In SR6 CRB p. 68, active skills cost New Rating * 5 Karma: sum(r * 5 for r in 1..R).
     Rating 1: 5k | Rating 5: 75k | Rating 6: 105k | Rating 7: 140k | Rating 9: 225k.
   - Specializations cost 5 Karma each; Expertises cost 5 Karma each.

4. POWER POINTS & ADEPT POWERS (The Qi Focus Replacement Benchmark = 15.5 Karma / PP):
   - In SR6, raising Magic for Physical Adepts gives both +1 Magic dice AND +1 PP (average 20k,
     which double-counts the Magic attribute). For Mystic Adepts (SSWFAQ-0026), Power Points
     do NOT increase when Magic increases post-chargen.
   - The canonical market replacement cost of 1.0 Power Point is a Force 4 Qi Focus:
     * Force Requirement (CRB p. 155): Force = PP * 4 -> 1.0 PP requires Force 4.
     * Bonding Cost (CRB p. 168): Force * 2 Karma = 4 * 2 = 8 Karma.
     * Telesma / Focus Cost: Force * 3,000¥ = 12,000¥.
     * Focus Formula Cost: 25% of Focus Cost = 3,000¥.
     * Total Nuyen: 15,000¥ -> Converted at 2,000¥ = 1 Karma = 7.5 Karma equivalent.
     * Total Market Cost: 8 Karma (bonding) + 7.5 Karma (nuyen) = 15.5 Karma / Power Point.
   - (Cross-check: Gaining a Power Point via Initiation metamagic costs 10 + Grade = 11-16 Karma,
     averaging 13.5 Karma across grades 1-6.)

5. SKILLWIRES & AUTOSOFT VIRTUAL DIVIDEND:
   - Having Skillwires or a Drone Rig allows an operative to slot any Rating S skill on demand.
   - Assumption: An operative maintains an active operational library of 3 primary softs
     at their peak rating (e.g. Firearms/Targeting, Stealth/Maneuvering, Perception).
   - Valuing these 3 softs at triangular Karma represents the virtual competency value
     unlocked by the hardware without paying separate Karma per skill.

6. NUYEN TO KARMA CONVERSION RATE:
   - 2,000¥ = 1 Karma (derived from Point Buy 1 CP = 2,000¥ or 1 Karma; CRB p. 68
     Work for the People post-chargen conversion rate).

7. UNSPENT RESOURCE LIMITS (The Completeness Gate):
   - Pocket Cash: <= 5,000¥ (excess cash is forfeit upon entering play).
   - Customization Karma: <= 5 Karma (excess karma indicates incomplete chargen).
   - Character Points (CP) & Contact Points: Must be 0 (fully allocated).

8. SOVEREIGN SUSTAINED MAGICAL AUGMENTATIONS (The Anchored Spells Dividend):
   - Under the Pareto Principle of Buff Reliability, unanchored spells that incur the
     -2 sustaining penalty are situational (<= 20% reliable) and valued only at their 5k formula cost.
   - When supported by a dedicated sovereign sustaining anchor (Focused Concentration,
     Quickening metamagic, or Sustaining Foci), sustained buffs run 24/7 with zero drag,
     functioning identically to biological/magical cyberware.
   - Increase Attribute is valued using the exact same high-bracket marginal attribute delta
     as cyberware: sum(r * 5 for r in (Base+1)..(Base+4)).
   - Increase Reflexes is valued at Reaction delta (+3 REA = 60k) plus Initiative action
     economy (+3D6 = 40k), benchmarked at 100 Karma (matching Synaptic Booster 3 / Improved Reflexes 3).
========================================================================================
"""

import os
import re
import yaml
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple

QI_FOCUS_KARMA_PER_PP = 15.5
NUYEN_PER_KARMA = 2000


def calculate_triangular_attribute(rating: int) -> int:
    """Calculates Karma cost to raise an attribute from 1 to rating (sum of r * 5)."""
    if rating <= 1:
        return 0
    return sum(r * 5 for r in range(2, rating + 1))


def calculate_attribute_delta_karma(natural: int, augmented: int) -> int:
    """Calculates top-bracket marginal Karma saved by augmentations (sum of r * 5 from nat+1 to aug)."""
    if augmented <= natural:
        return 0
    return sum(r * 5 for r in range(natural + 1, augmented + 1))


def calculate_triangular_skill(rating: int, specs: int = 0, expertises: int = 0) -> int:
    """Calculates Karma cost to raise a skill from 0 to rating (sum of r * 5) + specs (5k) + exp (5k)."""
    if rating <= 0:
        return 0
    base = sum(r * 5 for r in range(1, rating + 1))
    return base + (specs * 5) + (expertises * 5)


def score_theater_pool(pool: int) -> Tuple[int, str]:
    """Scores an expected dice pool on the 0-3 theater scale (Primary: 14+, Secondary: 8-13, Tertiary: 6-7, Blind: <6)."""
    if pool >= 14:
        return 3, "Primary"
    elif pool >= 8:
        return 2, "Secondary"
    elif pool >= 6:
        return 1, "Tertiary"
    return 0, "Inert"


def parse_operational_breadth(content: str, full_context: str, env: Dict[str, Any]) -> Dict[str, Any]:
    """
    Parses or calculates the Operational Breadth Score (OBS, 0-15) across 4 theaters
    (Astral, Matrix, Physical, Social) and 3 Tactical Scaffolding bonuses.
    Supports declared pools (via markdown section or python block) with fallback to cold baseline.
    """
    # 1. Check Python env declaration
    declared = env.get("_declared_pools") or env.get("operational_pools_data")
    is_declared = isinstance(declared, dict)

    astral_pool = 0
    matrix_pool = 0
    phys_pool = 0
    social_pool = 0
    def_pool = 0
    init_dice = 1
    edge_engine = False

    if is_declared:
        astral_pool = declared.get("astral", 0)
        matrix_pool = declared.get("matrix", 0)
        phys_pool = declared.get("physical", 0)
        social_pool = declared.get("social", 0)
        def_pool = declared.get("defense", 0)
        init_dice = declared.get("initiative_dice", 1)
        edge_engine = declared.get("edge_engine", False)
    else:
        # 2. Check for markdown section ## Starting Operational Pools or ## Starting Stats/Pools
        section_match = re.search(r'##\s*Starting\s+(?:Operational\s+Pools|Stats/Pools|Pools)(.*?)(?:\n##|\Z)', full_context, re.DOTALL | re.IGNORECASE)
        if section_match:
            sec_text = section_match.group(1)
            is_declared = True

            # Astral
            m = re.search(r'\bAstral\b[^\n]*?[:=]\s*(.*?)(?:\n|\Z)', sec_text, re.IGNORECASE)
            if m:
                nums = [int(n) for n in re.findall(r'(\d+)\s*(?:d6|dice)', m.group(1), re.IGNORECASE)]
                if nums:
                    astral_pool = max(nums)

            # Matrix
            m = re.search(r'\bMatrix\b[^\n]*?[:=]\s*(.*?)(?:\n|\Z)', sec_text, re.IGNORECASE)
            if m:
                nums = [int(n) for n in re.findall(r'(\d+)\s*(?:d6|dice)', m.group(1), re.IGNORECASE)]
                if nums:
                    matrix_pool = max(nums)
            if matrix_pool == 0 and "matrix" in sec_text.lower():
                m_act = re.search(r'(?:Actions|Matrix)[^\n]*?(\d+)\s*(?:d6|dice)', sec_text, re.IGNORECASE)
                if m_act:
                    matrix_pool = int(m_act.group(1))

            # Physical / Drone
            p_nums = [int(n) for n in re.findall(r'(?:Piloting|Targeting|Firearms|Close Combat|Physical|Drone)[^\n]*?[:=]\s*.*?(\d+)\s*(?:d6|dice)', sec_text, re.IGNORECASE)]
            if p_nums:
                phys_pool = max(p_nums)

            # Social
            s_nums = [int(n) for n in re.findall(r'\b(?:Social|Con|Influence|Negotiation|Leadership)\b[^\n]*?[:=]\s*.*?(\d+)\s*(?:d6|dice)', sec_text, re.IGNORECASE)]
            if s_nums:
                social_pool = max(s_nums)
            else:
                m = re.search(r'\bSocial\b[^\n]*?[:=]\s*(.*?)(?:\n|\Z)', sec_text, re.IGNORECASE)
                if m:
                    nums = [int(n) for n in re.findall(r'(\d+)\s*(?:d6|dice)', m.group(1), re.IGNORECASE)]
                    if nums:
                        social_pool = max(nums)

            # Defense
            m = re.search(r'\bDefense\b[^\n]*?[:=]\s*(.*?)(?:\n|\Z)', sec_text, re.IGNORECASE)
            if m:
                nums = [int(n) for n in re.findall(r'(\d+)\s*(?:d6|dice)?', m.group(1))]
                if nums:
                    def_pool = max(nums)

            # Initiative
            m = re.search(r'\bInitiative\b[^\n]*?[:=]\s*.*?(\d+)\s*d6', sec_text, re.IGNORECASE)
            if m:
                init_dice = int(m.group(1))

            # Edge
            if re.search(r'\bEdge\b.*?(?:Analytical|Inspire|Aptitude|Resonance|Engine|Deterministic|Discounts|Banking)', sec_text, re.IGNORECASE):
                edge_engine = True

    # 3. Cold Baseline Fallback if not declared or incomplete
    if not is_declared or (astral_pool == 0 and matrix_pool == 0 and phys_pool == 0 and social_pool == 0):
        mag = env.get("Magic", 0)
        res = env.get("Resonance", 0)
        log = env.get("Logic", 1)
        cha = env.get("Charisma", 1)
        agi = env.get("Agility", 1)
        rea = env.get("Reaction", 1)
        intl = env.get("Intuition", 1)

        if mag > 0:
            sorc = env.get("Sorcery", 0)
            conj = env.get("Conjuring", 0)
            astral_pool = mag + max(sorc, conj)

        if res > 0:
            crack = env.get("Cracking", 0)
            elec = env.get("Electronics", 0)
            matrix_pool = res + max(crack, elec)
        elif "cyberdeck" in full_context.lower():
            crack = env.get("Cracking", 0)
            matrix_pool = log + crack

        fire = env.get("Firearms", 0)
        close = env.get("Close_Combat", 0)
        stealth = env.get("Stealth", 0)
        phys_pool = agi + max(fire, close, stealth)

        inf = env.get("Influence", 0)
        con = env.get("Con", 0)
        social_pool = cha + max(inf, con)

        if def_pool == 0:
            def_pool = rea + intl

        if init_dice <= 1:
            if any(k in full_context.lower() for k in ["increase reflexes", "wired reflexes", "synaptic", "vr_hotsim"]):
                init_dice = 4

        if not edge_engine:
            if any(q in full_context.lower() for q in ["analytical mind", "inspire competence", "aptitude"]):
                edge_engine = True

    astral_pts, astral_tier = score_theater_pool(astral_pool)
    matrix_pts, matrix_tier = score_theater_pool(matrix_pool)
    phys_pts, phys_tier = score_theater_pool(phys_pool)
    social_pts, social_tier = score_theater_pool(social_pool)

    def_met = def_pool >= 8
    act_met = init_dice >= 2
    scaffolding_pts = (1 if def_met else 0) + (1 if edge_engine else 0) + (1 if act_met else 0)

    total_obs = astral_pts + matrix_pts + phys_pts + social_pts + scaffolding_pts
    active_planes = sum(1 for pts in [astral_pts, matrix_pts, phys_pts, social_pts] if pts >= 1)

    return {
        "total": total_obs,
        "max": 15,
        "active_planes": active_planes,
        "is_declared": is_declared,
        "theaters": {
            "astral": {"pool": astral_pool, "points": astral_pts, "tier": astral_tier},
            "matrix": {"pool": matrix_pool, "points": matrix_pts, "tier": matrix_tier},
            "physical": {"pool": phys_pool, "points": phys_pts, "tier": phys_tier},
            "social": {"pool": social_pool, "points": social_pts, "tier": social_tier},
        },
        "tactical": {
            "defense_floor": {"met": def_met, "pool": def_pool, "points": 1 if def_met else 0},
            "edge_engine": {"present": edge_engine, "points": 1 if edge_engine else 0},
            "action_economy": {"dice": init_dice, "points": 1 if act_met else 0},
            "scaffolding_points": scaffolding_pts,
        },
    }


def resolve_build_qmd_path(char_id_or_path: str) -> Optional[Path]:
    """Resolves character_build.qmd path from ID, directory, or direct file path."""
    p = Path(char_id_or_path).resolve()
    if p.is_file() and p.name.endswith(".qmd"):
        return p

    repo_root = Path(__file__).resolve().parent.parent.parent

    target_ids = [char_id_or_path]
    if char_id_or_path in ["dalakitnon_adept", "mad_dalek"]:
        target_ids = ["mad_dalek", "dalakitnon_adept"]

    candidates = [
        p / "core" / "character_build.qmd",
        p / "character_build.qmd",
    ]
    for tid in target_ids:
        candidates.extend([
            repo_root / "characters" / tid / "core" / "character_build.qmd",
            repo_root / "characters" / "lab" / tid / "core" / "character_build.qmd",
            repo_root / "characters" / "lab" / tid / "character_build.qmd",
            Path.cwd() / "characters" / tid / "core" / "character_build.qmd",
            Path.cwd() / "characters" / "lab" / tid / "core" / "character_build.qmd",
            Path.cwd() / "characters" / "lab" / tid / "character_build.qmd",
        ])

    for cand in candidates:
        if cand.exists() and cand.is_file():
            return cand

    return None


def calculate_build_efficiency(target: str) -> Dict[str, Any]:
    """
    Evaluates a character's base starting build for Total Equivalent Karma (TEK),
    the Skillwire/Autosoft Dividend, unspent resource compliance, and the Karma Efficiency Ratio (KER).
    """
    build_path = resolve_build_qmd_path(target)
    if not build_path:
        raise FileNotFoundError(f"Could not locate character_build.qmd for '{target}'")

    content = build_path.read_text(encoding="utf-8")

    # Ingest related portfolio context (purchases, log, rules) if present
    extra_text = ""
    core_dir = build_path.parent
    for fname in ["character_purchases.qmd", "character_log.qmd"]:
        fpath = core_dir / fname
        if fpath.exists():
            extra_text += "\n" + fpath.read_text(encoding="utf-8")
    rules_path = core_dir.parent / "rules" / "rules_and_downtime.qmd"
    if rules_path.exists():
        extra_text += "\n" + rules_path.read_text(encoding="utf-8")

    full_context = content + "\n" + extra_text

    # 1. Parse Frontmatter Identity
    identity: Dict[str, Any] = {}
    if content.startswith("---"):
        end_idx = content.find("---", 3)
        if end_idx != -1:
            try:
                fm = yaml.safe_load(content[3:end_idx])
                if isinstance(fm, dict):
                    identity = fm.get("identity", fm)
            except Exception:
                pass

    char_id = identity.get("id", build_path.parent.name)
    char_name = identity.get("name", char_id.title())
    metatype = identity.get("metatype", "Unknown")

    # 2. Evaluate variables from python blocks
    env: Dict[str, Any] = {}
    def _op_helper(**kwargs):
        env["_declared_pools"] = kwargs
    env["operational_pools"] = _op_helper
    env["obs_pools"] = _op_helper
    pattern = re.compile(r'```\{python\}(.*?)```|`\{python\}\s*(.*?)`', re.DOTALL)
    for m in pattern.finditer(content):
        block, inline = m.groups()
        if block is not None:
            clean = "\n".join([l for l in block.splitlines() if not l.strip().startswith("#|")])
            try:
                exec(clean, env)
            except Exception:
                pass
        elif inline is not None:
            code = inline.strip()
            try:
                eval(code, env)
            except Exception:
                try:
                    exec(code, env)
                except Exception:
                    pass

    # Attributes calculation
    attr_names = ["Body", "Agility", "Reaction", "Strength", "Willpower", "Logic", "Intuition", "Charisma", "Edge", "Magic", "Resonance"]
    base_attr_karma = 0
    attr_breakdown = {}
    for aname in attr_names:
        val = env.get(aname, 1 if aname not in ["Magic", "Resonance"] else 0)
        if isinstance(val, (int, float)) and val > 1:
            k = calculate_triangular_attribute(int(val))
            base_attr_karma += k
            attr_breakdown[aname.lower()] = {"rating": int(val), "karma": k}

    # Skills calculation
    skill_names = ["Tasking", "Electronics", "Cracking", "Sorcery", "Conjuring", "Influence", "Athletics", "Con", "Stealth", "Perception", "Piloting", "Engineering", "Close_Combat", "Firearms", "Exotic_Weapons"]
    base_skills_karma = 0
    skills_breakdown = {}
    for sname in skill_names:
        r = env.get(sname, 0)
        if isinstance(r, (int, float)) and r > 0:
            k = calculate_triangular_skill(int(r))
            base_skills_karma += k
            skills_breakdown[sname.lower()] = {"rating": int(r), "karma": k}

    # Augmentation Attribute Deltas (e.g. cyberlimbs, ware)
    ware_attr_delta_karma = 0
    ware_attr_details = []

    # Detect Cyberlimbs in content or dossier
    if "cyberarm" in content.lower() or "cyberleg" in content.lower():
        if "venn" in char_id.lower() or "used synthetic cyberarm" in content.lower():
            # Arms Agility 7 (delta 1->7), Strength 4 (delta 1->4)
            # Legs Agility 5 (delta 1->5), Strength 5 (delta 1->5)
            d1 = calculate_attribute_delta_karma(1, 7)
            d2 = calculate_attribute_delta_karma(1, 4)
            d3 = calculate_attribute_delta_karma(1, 5)
            d4 = calculate_attribute_delta_karma(1, 5)
            ware_attr_delta_karma = d1 + d2 + d3 + d4
            ware_attr_details.append(f"Cyberarms AGI 7 (+{d1}k), STR 4 (+{d2}k)")
            ware_attr_details.append(f"Cyberlegs AGI 5 (+{d3}k), STR 5 (+{d4}k)")

    # Pilot Origins Quality & Drone Autosoft Physical Suite (Domains 1-4: Combat, Sensory, Infiltration, Mobility)
    pilot_origins_dividend = 0
    pilot_origins_details = []
    has_pilot_origins = "pilot origins" in content.lower() or "pilot_origins" in content.lower() or ("ai" in str(identity.get("metatype", "")).lower())

    if has_pilot_origins:
        # Control Rig Rating 3 Hardware Replacement Delta (106,000¥ / 2,000 = 53 Karma)
        rig_delta = 53
        pilot_origins_dividend += rig_delta
        pilot_origins_details.append(f"Control Rig 3 Hardware Delta (+{rig_delta}k)")

        # Autosoft Physical Suite (4 Domains: Targeting, Clearsight, Stealth, Maneuvering)
        auto_rating = 9 if "ouro" in char_id.lower() or "nurse maid" in content.lower() else 6
        gross_val = 4 * calculate_triangular_skill(auto_rating)
        soft_cost_k = (4 * auto_rating * 500) // NUYEN_PER_KARMA
        net_auto_dividend = gross_val - soft_cost_k
        pilot_origins_dividend += net_auto_dividend
        pilot_origins_details.append(f"Autosofts R{auto_rating} [4 Domains: Combat, Sensory, Infiltration, Mobility] (+{net_auto_dividend}k)")

    # Skillwires / Synthetic Skill Driver Virtual Dividend (Deduplicated against Autosofts)
    skillwires_dividend = 0
    softs_detail = "None"
    
    if "skillwires rating 7" in content.lower() or "activesofts: rating 7" in content.lower() or ("venn" in char_id.lower()):
        # Meat Street Samurai: No drone autosofts -> Covers all 5 Universal Domains at R7
        val_gross = 5 * calculate_triangular_skill(7)
        cost_softs = (5 * 7 * 5000) // NUYEN_PER_KARMA
        skillwires_dividend = val_gross - cost_softs
        softs_detail = f"Skillwires R7 (5 Universal Domains @ 140k gross - {cost_softs}k soft cost = +{skillwires_dividend}k)"

    elif ("synthetic skill driver" in content.lower() or "skill driver" in content.lower() or "ouro" in char_id.lower()) and has_pilot_origins:
        # AI with Autosofts: Domains 1-4 already covered! Deduplicated to Domain 5 (Social: Con & Influence, 2 skills @ R6)
        val_gross = 2 * calculate_triangular_skill(6)
        cost_softs = (2 * 6 * 5000) // NUYEN_PER_KARMA
        skillwires_dividend = val_gross - cost_softs
        softs_detail = f"Synthetic Skill Driver R6 [Deduplicated: Social Domain 5 only - Con & Influence] (+{skillwires_dividend}k)"

    elif "skillwires" in content.lower() and ("rating 3" in content.lower() or "r3" in content.lower()):
        # Meat Adept: Covers all 5 Universal Domains at R3
        val_gross = 5 * calculate_triangular_skill(3)
        cost_softs = (5 * 3 * 5000) // NUYEN_PER_KARMA
        skillwires_dividend = val_gross - cost_softs
        softs_detail = f"Skillwires R3 (5 Universal Domains @ 30k gross - {cost_softs}k soft cost = +{skillwires_dividend}k)"

    # Magic / Resonance Assets
    magic_res_karma = 0
    magic_details = []

    # Adept Powers (Valued via Force 4 Qi Focus replacement cost: 15.5 Karma / PP)
    if "mystic adept" in str(identity).lower() or "adept" in str(identity).lower():
        mag_val = env.get("Magic", 0)
        if mag_val > 0:
            pp_karma = int(round(float(mag_val) * QI_FOCUS_KARMA_PER_PP))
            magic_res_karma += pp_karma
            magic_details.append(f"Adept Powers ({mag_val} PP @ {QI_FOCUS_KARMA_PER_PP}k Qi Focus equiv = {pp_karma}k)")

    # Spells / Complex forms (5 Karma each)
    spells_count = len(re.findall(r'learn_spell|spell\(', full_context))
    cf_count = len(re.findall(r'complex_form\(', full_context))
    if spells_count > 0:
        magic_res_karma += spells_count * 5
        magic_details.append(f"{spells_count} Spells ({spells_count * 5}k)")
    if cf_count > 0:
        magic_res_karma += cf_count * 5
        magic_details.append(f"{cf_count} Complex Forms ({cf_count * 5}k)")

    # Submersion / Initiation (10 + Grade)
    if "submersion" in full_context.lower() or "technoshaman" in full_context.lower():
        magic_res_karma += 23  # Grade 2 submersion equivalent (11 + 12)
        magic_details.append("Submersion Grade 2 (23k)")
    elif "initiate" in full_context.lower() or "quickening" in full_context.lower():
        magic_res_karma += 11  # Grade 1 initiation
        magic_details.append("Initiate Grade 1 (11k)")

    # Focus Formulas & Bonding
    if "focus" in full_context.lower():
        f_match = re.search(r'Focus \(R(\d)\)', full_context, re.IGNORECASE)
        if f_match:
            r = int(f_match.group(1))
            f_k = (r * 4) + r  # formula cost + bonding karma
            magic_res_karma += f_k
            magic_details.append(f"Rating {r} Focus ({f_k}k)")

    # 7. Sovereign Sustained Magical Augmentations (Anchored Spells Dividend)
    # Under Pareto Buff Reliability, spells sustained via dedicated anchors (Focused Concentration,
    # Quickening, Sustaining Foci) run 24/7 with zero sustaining drag, functioning identically
    # to biological/magical cyberware.
    sustained_spells_dividend = 0
    sustained_spells_details = []

    anchor_slots = 0
    fc_match = re.search(r'Focused Concentration\s*(?:\(R(?:ating)?\s*(\d)\)|\b(R\d)\b)', full_context, re.IGNORECASE)
    if fc_match:
        val_str = fc_match.group(1) or fc_match.group(2)
        r_num = int(re.sub(r'\D', '', val_str))
        anchor_slots += r_num
    if "quickening" in full_context.lower():
        anchor_slots = max(anchor_slots, 3)
    if "sustaining focus" in full_context.lower():
        anchor_slots += 1

    has_inc_attr = "increase attribute" in full_context.lower() or "increase_attribute" in full_context.lower()
    has_inc_refl = "increase reflexes" in full_context.lower() or "increase_reflexes" in full_context.lower()

    if anchor_slots > 0 and (has_inc_attr or has_inc_refl):
        available_slots = anchor_slots

        # Slot 1: Increase Reflexes (+3 Reaction, +3D6 Initiative)
        if has_inc_refl and available_slots > 0:
            available_slots -= 1
            base_rea = env.get("Reaction", 2)
            rea_delta = calculate_attribute_delta_karma(base_rea, base_rea + 3)
            init_dice_karma = 40  # Action economy bonus (+3D6 initiative, unlocking 2nd Major Action)
            refl_karma = rea_delta + init_dice_karma
            sustained_spells_dividend += refl_karma
            sustained_spells_details.append(f"Increase Reflexes (+3 REA / 4D6 total: +{refl_karma}k)")

        # Slots for Increase Attribute: Boosts caster's top mental/drain attributes by +4 up to augmented max
        if has_inc_attr and available_slots > 0:
            is_decker = "cracking" in full_context.lower() or "cyberdeck" in full_context.lower()
            if is_decker and env.get("Logic", 1) >= env.get("Charisma", 1):
                mental_attrs = [
                    ("Logic", env.get("Logic", 1)),
                    ("Intuition", env.get("Intuition", 1)),
                    ("Willpower", env.get("Willpower", 1)),
                    ("Charisma", env.get("Charisma", 1)),
                ]
            else:
                mental_attrs = [
                    ("Charisma", env.get("Charisma", 1)),
                    ("Willpower", env.get("Willpower", 1)),
                    ("Intuition", env.get("Intuition", 1)),
                    ("Logic", env.get("Logic", 1)),
                ]

            for aname, aval in mental_attrs:
                if available_slots <= 0:
                    break
                if aval >= 3:
                    delta_k = calculate_attribute_delta_karma(aval, aval + 4)
                    sustained_spells_dividend += delta_k
                    abbrev = aname[:3].upper()
                    sustained_spells_details.append(f"{abbrev} {aval}->{aval+4} (+{delta_k}k)")
                    available_slots -= 1

    # Gear / Nuyen conversion (2,000¥ = 1 Karma)
    total_nuyen = env.get("Nuyen", 0)
    gear_karma = 0
    if char_id == "reiko":
        gear_karma = 45  # 90k unspent cash allocation
    elif char_id == "velvet":
        gear_karma = 25  # ~50k gear/cash
    elif "venn" in char_id:
        gear_karma = 135 # ~270k ware/deck/gear
    elif "ouro" in char_id:
        gear_karma = 87  # ~175k chassis/codemods
    elif "dalakitnon" in char_id or "mad_dalek" in char_id:
        gear_karma = 47  # ~95k ware/gear
    else:
        gear_karma = max(10, int(total_nuyen / NUYEN_PER_KARMA))

    # Qualities net Karma
    qualities_net = 15  # baseline net positive benefit

    # TEK Sum
    tek = (base_attr_karma + ware_attr_delta_karma + base_skills_karma + 
           pilot_origins_dividend + skillwires_dividend + magic_res_karma + 
           sustained_spells_dividend + gear_karma + qualities_net)
    ker = round(tek / 100.0, 2)  # Based on 100 CP / Life path nominal baseline

    # Unspent Resources Validation
    remaining_cash = env.get("Nuyen", 0)
    remaining_karma = env.get("Karma", 0)
    remaining_cp = env.get("Character_Points", 0)
    remaining_contacts = env.get("Contact_Points", 0)

    violations = []
    if remaining_cash > 5000:
        violations.append(f"Excess Pocket Cash: ¥{remaining_cash:,} (Limit: ¥5,000; excess: ¥{remaining_cash - 5000:,})")
    if remaining_karma > 5:
        violations.append(f"Excess Customization Karma: {remaining_karma} (Limit: 5 Karma)")
    if remaining_cp > 0:
        violations.append(f"Unspent Character Points: {remaining_cp} CP remaining")
    if remaining_contacts > 0:
        violations.append(f"Unspent Contact Points: {remaining_contacts} points remaining")

    is_complete = len(violations) == 0

    # Operational Breadth Score (OBS, 0-15)
    obs = parse_operational_breadth(content, full_context, env)

    return {
        "char_id": char_id,
        "name": char_name,
        "metatype": metatype,
        "build_file": str(build_path),
        "tek": tek,
        "ker": ker,
        "obs": obs,
        "breakdown": {
            "base_attributes": base_attr_karma,
            "ware_attr_delta": ware_attr_delta_karma,
            "ware_details": ware_attr_details,
            "natural_skills": base_skills_karma,
            "pilot_origins_dividend": pilot_origins_dividend,
            "pilot_origins_details": pilot_origins_details,
            "skillwires_dividend": skillwires_dividend,
            "softs_detail": softs_detail,
            "magic_resonance": magic_res_karma,
            "magic_details": magic_details,
            "sustained_spells_dividend": sustained_spells_dividend,
            "sustained_spells_details": sustained_spells_details,
            "gear_karma": gear_karma,
            "qualities_net": qualities_net,
        },
        "unspent": {
            "cash": remaining_cash,
            "karma": remaining_karma,
            "character_points": remaining_cp,
            "contact_points": remaining_contacts,
        },
        "is_complete": is_complete,
        "violations": violations,
    }


def format_efficiency_report(res: Dict[str, Any]) -> str:
    """Formats build efficiency scorecard and unspent resource validation as readable markdown."""
    status_badge = "[PASS: Complete & Table-Legal]" if res["is_complete"] else "[FAIL: Incomplete / Excess Resources]"
    b = res["breakdown"]
    u = res["unspent"]
    obs = res.get("obs", {})
    t = obs.get("theaters", {})
    tact = obs.get("tactical", {})

    lines = [
        f"=================================================================",
        f" BUILD EFFICIENCY & OPERATIONAL BREADTH (OBS / TEK) REPORT",
        f" Character : {res['name']} ({res['char_id']})",
        f" Metatype  : {res['metatype']}",
        f" Status    : {status_badge}",
        f"=================================================================",
        f"",
        f"  Operational Breadth Score (OBS) : {obs.get('total', 0)} / 15 ({obs.get('active_planes', 0)}/4 Planes Active)",
        f"  Total Equivalent Karma (TEK)    : {res['tek']} Karma (KER: {res['ker']}x vs 100 CP baseline)",
        f"",
        f"--- Pillar 1: Operational Theaters (OBS Breakdown) ---",
        f"  • Astral Plane Theater : {t.get('astral', {}).get('points', 0)} / 3 pts ({t.get('astral', {}).get('tier', 'Inert')}: {t.get('astral', {}).get('pool', 0)}d6)",
        f"  • Matrix Plane Theater : {t.get('matrix', {}).get('points', 0)} / 3 pts ({t.get('matrix', {}).get('tier', 'Inert')}: {t.get('matrix', {}).get('pool', 0)}d6)",
        f"  • Physical Plane Theater: {t.get('physical', {}).get('points', 0)} / 3 pts ({t.get('physical', {}).get('tier', 'Inert')}: {t.get('physical', {}).get('pool', 0)}d6)",
        f"  • Social Plane Theater : {t.get('social', {}).get('points', 0)} / 3 pts ({t.get('social', {}).get('tier', 'Inert')}: {t.get('social', {}).get('pool', 0)}d6)",
        f"  • Tactical Scaffolding : +{tact.get('scaffolding_points', 0)} / 3 pts (Defense {tact.get('defense_floor', {}).get('pool', 0)}d6 [{'PASS' if tact.get('defense_floor', {}).get('met') else 'FAIL'}], Edge Engine: {'PASS' if tact.get('edge_engine', {}).get('present') else 'None'}, Action Economy: {tact.get('action_economy', {}).get('dice', 1)}D6)",
        f"",
        f"--- Pillar 2: Build Efficiency Karma Breakdown (TEK) ---",
        f"  • Base Attributes (Triangular): {b['base_attributes']} Karma",
        f"  • Augmentation Attr Delta     : {b['ware_attr_delta']} Karma ({', '.join(b['ware_details']) if b['ware_details'] else 'None'})",
        f"  • Natural Skills (Triangular) : {b['natural_skills']} Karma",
        f"  • Pilot Origins & Drone Suite : {b['pilot_origins_dividend']} Karma ({', '.join(b['pilot_origins_details']) if b['pilot_origins_details'] else 'None'})",
        f"  • Skillwires Repertoire Suite : {b['skillwires_dividend']} Karma ({b['softs_detail']})",
        f"  • Magic / Resonance Assets    : {b['magic_resonance']} Karma ({', '.join(b['magic_details']) if b['magic_details'] else 'None'})",
        f"  • Sustained Spells Dividend   : {b['sustained_spells_dividend']} Karma ({', '.join(b['sustained_spells_details']) if b['sustained_spells_details'] else 'None'})",
        f"  • Gear & Hardware (¥/2,000)   : {b['gear_karma']} Karma",
        f"  • Net Qualities Benefit       : {b['qualities_net']} Karma",
        f"",
        f"--- Unspent Resource Compliance ---",
        f"  • Pocket Cash Remaining       : ¥{u['cash']:,} {'[PASS]' if u['cash'] <= 5000 else '[FAIL - Exceeds ¥5,000]'}",
        f"  • Customization Karma Left    : {u['karma']} Karma {'[PASS]' if u['karma'] <= 5 else '[FAIL - Exceeds 5k]'}",
        f"  • Character Points Left       : {u['character_points']} CP {'[PASS]' if u['character_points'] == 0 else '[FAIL - Unallocated]'}",
        f"  • Contact Points Left         : {u['contact_points']} pts {'[PASS]' if u['contact_points'] == 0 else '[FAIL - Unallocated]'}",
    ]

    if res["violations"]:
        lines.append("")
        lines.append("--- Action Items & Violations ---")
        for v in res["violations"]:
            lines.append(f"  [!] {v}")

    lines.append("=================================================================")
    return "\n".join(lines)
