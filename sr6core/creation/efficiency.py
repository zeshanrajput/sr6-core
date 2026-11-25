"""
Build Efficiency & Total Equivalent Karma (TEK) Engine for SR6 Core.
Calculates the post-chargen Karma value of character builds, Skillwires/Autosofts dividends,
20-point Operational Breadth Score (OBS), Session 4 SRM Mulligan Checkpoint (+28K / +30,000¥),
and validates unspent resource limits (cash <= 5,000¥, karma <= 5).

========================================================================================
ECONOMIC & MECHANICAL ASSUMPTIONS (THE CONVERSION LEDGER)
========================================================================================

1. ATTRIBUTES PROGRESSION (Triangular):
   - In SR6 CRB p. 68 (Advancement Costs Table), raising an attribute costs New Rating * 5.
   - Raising an attribute from 1 to R costs: sum(r * 5 for r in 2..R).
     Rating 2: 10k | Rating 5: 70k | Rating 6: 100k | Rating 9: 220k | Rating 10: 270k.

2. AUGMENTATION ATTRIBUTE SAVINGS (High-Bracket Marginal Delta):
   - When augmentations or cyber-qualities (cyberlimbs, Redliner, Cyber Singularity Seeker,
     Bio-Response Override, Neurochemical Regulator) increase an attribute from natural N
     to augmented A, the build saves the HIGHEST marginal Karma tiers:
     sum(r * 5 for r in (N+1)..A).

3. SKILLS PROGRESSION (Triangular):
   - In SR6 CRB p. 68, active skills cost New Rating * 5 Karma: sum(r * 5 for r in 1..R).
     Rating 1: 5k | Rating 5: 75k | Rating 6: 105k | Rating 7: 140k | Rating 9: 225k.
   - Specializations cost 5 Karma each; Expertises cost 5 Karma each.

4. POWER POINTS & ADEPT POWERS (The Qi Focus Replacement Benchmark = 15.5 Karma / PP):
   - The canonical market replacement cost of 1.0 Power Point is a Force 4 Qi Focus:
     8 Karma (bonding) + 15,000¥ (focus + formula @ 2,000¥/K = 7.5K) = 15.5 Karma / PP.

5. SKILLWIRES & AUTOSOFT VIRTUAL DIVIDEND:
   - Having Skillwires or a Drone Rig allows an operative to slot any Rating S skill on demand.
   - Autosofts (via Pilot Origins): 4 physical operational domains (Combat/Targeting,
     Sensory/Clearsight, Infiltration/Stealth, Mobility/Maneuvering) at actual autosoft rating.
   - Skillwires (Meat): 5 universal domains at actual skillwire rating.
   - Synthetic Skill Driver (AI w/ Pilot Origins): Deduplicated strictly to Social Domain 5
     (Con & Influence) so physical/combat domains are never double-counted.

6. NUYEN TO KARMA CONVERSION RATE:
   - 2,000¥ = 1 Karma (derived from Point Buy 1 CP = 2,000¥ or 1 Karma; CRB p. 68
     Work for the People post-chargen conversion rate).

7. UNSPENT RESOURCE LIMITS (The Completeness Gate):
   - Pocket Cash: <= 5,000¥ (excess cash is forfeit upon entering play).
   - Customization Karma: <= 5 Karma (excess karma indicates incomplete chargen).
   - Character Points (CP) & Contact Points: Must be 0 (fully allocated).

8. SOVEREIGN SUSTAINED MAGICAL AUGMENTATIONS (The Anchored Spells Dividend):
   - Sustained buffs backed by dedicated sovereign anchors (Focused Concentration,
     Quickening metamagic, Sustaining Foci) run 24/7 with zero drag, functioning identically
     to biological/magical cyberware.
   - Increase Attribute is valued at high-bracket marginal attribute delta: sum(r * 5 for r in (Base+1)..(Base+4)).
   - Increase Reflexes is valued at Reaction delta (+3 REA) + Initiative action economy (+3D6 = 40k).

9. OPERATIONAL BREADTH SCORE (OBS, 0-20 SCALE):
   - 4 Operational Planes (0-3 pts each = 12 pts max): Astral, Matrix, Physical, Social.
   - 8 Tactical & Capability Scaffolding Dimensions (+1 pt each = 8 pts max):
     1) Defense Floor (>= 8d6)
     2) Action Economy (>= 2D6 / 2 Major Actions)
     3) Deterministic Edge Engine
     4) Durability & Soak / Mitigation
     5) Sustain & Drain/Fade Economy
     6) Autonomous Force Multiplication (Ally Sprite / Twin Hull / Spirits / Monad Dual)
     7) Scene Permeability (Social/Stealth/Astral/Matrix Disguise & Infiltration)
     8) Burst Ceiling (>= 18d6 Sovereign Peak Pool)

10. SESSION 4 CHECKPOINT (SRM MULLIGAN GATE: +28 KARMA / +30,000¥):
   - Evaluates build trajectory at the SRM Session 4 rebuild cutoff (+28 Karma, +30,000¥ / 60k¥ DIY,
     and 4 Major / 4 Minor Downtime Actions).
========================================================================================
"""

import re
import yaml
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple

from sr6core.config import get_character_configs

QI_FOCUS_KARMA_PER_PP = 15.5
NUYEN_PER_KARMA = 2000

POSITIVE_QUALITY_COSTS = {
    "sourceror": 20,
    "technoshaman": 20,
    "natural hacker": 15,
    "jack jockey": 11,
    "multiprocessing": 11,
    "firewall fortress": 5,
    "reinforced firewall": 7,
    "augmentation acclimation": 20,
    "redliner": 10,
    "cyber singularity seeker": 10,
    "maximum overdrive": 7,
    "brilliant heuristics": 10,
    "mentor spirit": 10,
    "exceptional attribute": 12,
    "inspire competence": 11,
    "focused concentration (r3)": 36,
    "focused concentration r3": 36,
    "metagenetic attribute increase": 15,
    "designer": 6,
    "analytical mind": 6,
}


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


def _extract_section_text(full_context: str, heading_regex: str) -> str:
    """Extracts markdown text under a level-2 heading matching heading_regex until the next ## heading."""
    m = re.search(rf'##\s*{heading_regex}(.*?)(?:\n##\s|\Z)', full_context, re.DOTALL | re.IGNORECASE)
    return m.group(1) if m else ""


def _parse_pools_from_text(sec_text: str) -> Dict[str, Any]:
    """Parses Astral, Matrix, Physical, Social, Defense, Initiative, and Edge fields from a pools section."""
    astral_pool = 0
    matrix_pool = 0
    phys_pool = 0
    social_pool = 0
    def_pool = 0
    init_dice = 1
    edge_engine = False

    m = re.search(r'\bAstral[^\n]*?[:=]\s*(.*?)(?:\n|\Z)', sec_text, re.IGNORECASE)
    if m:
        nums = [int(n) for n in re.findall(r'(\d+)\s*(?:d6|dice)', m.group(1), re.IGNORECASE)]
        if nums:
            astral_pool = max(nums)

    m = re.search(r'\bMatrix\b[^\n]*?[:=]\s*(.*?)(?:\n|\Z)', sec_text, re.IGNORECASE)
    if m:
        nums = [int(n) for n in re.findall(r'(\d+)\s*(?:d6|dice)', m.group(1), re.IGNORECASE)]
        if nums:
            matrix_pool = max(nums)
    if matrix_pool == 0 and "matrix" in sec_text.lower():
        m_act = re.search(r'(?:Actions|Matrix|Threading)[^\n]*?(\d+)\s*(?:d6|dice)', sec_text, re.IGNORECASE)
        if m_act:
            matrix_pool = int(m_act.group(1))

    p_nums = [int(n) for n in re.findall(r'(?:Piloting|Targeting|Firearms|Close Combat|Physical|Drone)[^\n]*?[:=]\s*.*?(\d+)\s*(?:d6|dice)', sec_text, re.IGNORECASE)]
    if p_nums:
        phys_pool = max(p_nums)

    s_nums = [int(n) for n in re.findall(r'\b(?:Social|Con|Influence|Negotiation|Leadership)\b[^\n]*?[:=]\s*.*?(\d+)\s*(?:d6|dice)', sec_text, re.IGNORECASE)]
    if s_nums:
        social_pool = max(s_nums)
    else:
        m = re.search(r'\bSocial\b[^\n]*?[:=]\s*(.*?)(?:\n|\Z)', sec_text, re.IGNORECASE)
        if m:
            nums = [int(n) for n in re.findall(r'(\d+)\s*(?:d6|dice)', m.group(1), re.IGNORECASE)]
            if nums:
                social_pool = max(nums)

    m = re.search(r'\bDefense\b[^\n]*?[:=]\s*(.*?)(?:\n|\Z)', sec_text, re.IGNORECASE)
    if m:
        nums = [int(n) for n in re.findall(r'(\d+)\s*(?:d6|dice)?', m.group(1))]
        if nums:
            def_pool = max(nums)

    m = re.search(r'\bInitiative\b[^\n]*?[:=]\s*.*?(\d+)\s*d6', sec_text, re.IGNORECASE)
    if m:
        init_dice = int(m.group(1))

    if re.search(r'\bEdge\b.*?(?:Analytical|Inspire|Aptitude|Resonance|Engine|Deterministic|Discounts|Banking|Heuristics|Warrior|Overdrive|Jockey)', sec_text, re.IGNORECASE):
        edge_engine = True

    return {
        "astral": astral_pool,
        "matrix": matrix_pool,
        "physical": phys_pool,
        "social": social_pool,
        "defense": def_pool,
        "initiative_dice": init_dice,
        "edge_engine": edge_engine,
    }


def _evaluate_capability_scaffolding(
    full_context: str,
    env: Dict[str, Any],
    astral_pool: int,
    matrix_pool: int,
    phys_pool: int,
    social_pool: int,
    def_pool: int,
    init_dice: int,
    edge_engine: bool,
    declared: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """Evaluates the 8 Tactical & Capability Scaffolding Dimensions (+1 pt each, max 8)."""
    ctx = full_context.lower()
    dec = declared or {}

    def_met = bool(dec.get("defense_floor", def_pool >= 8))
    act_met = bool(dec.get("action_economy", init_dice >= 2 or "2 major actions" in ctx or "physical attribute boost" in ctx))
    edge_met = bool(dec.get("edge_engine", edge_engine))

    # 4. Durability & Soak / Damage Mitigation
    durability_met = bool(dec.get("durability_soak", False))
    if not durability_met:
        has_dmg_mit = "damage mitigation protocols" in ctx
        has_monad_durability = "monad toughness" in ctx and "rapid cellular healing" in ctx
        has_bone_density = "bone density" in ctx
        has_heavy_hull = "nurse maid troll" in ctx or "man-at-arms" in ctx or "shiawase silverstar" in ctx
        has_magic_armor = ("mystic armor" in ctx or "armor spell" in ctx or "combat sense" in ctx)
        durability_met = has_dmg_mit or has_monad_durability or has_bone_density or has_heavy_hull or has_magic_armor

    # 5. Sustain & Drain / Fade Economy
    sustain_drain_met = bool(dec.get("sustain_drain_economy", False))
    if not sustain_drain_met:
        has_sourceror = "sourceror" in ctx
        has_quickening = "quickening" in ctx
        has_fc = "focused concentration" in ctx
        has_zero_drain_ware = ("monad" in ctx or "cyberware" in ctx) and env.get("Magic", 0) == 0 and env.get("Resonance", 0) == 0
        sustain_drain_met = has_sourceror or has_quickening or has_fc or has_zero_drain_ware

    # 6. Autonomous Force Multiplication (Ally Sprite, Twin Hulls, High Conjuring, Dual Monad)
    force_mult_met = bool(dec.get("force_multiplication", False))
    if not force_mult_met:
        has_ally_sprite = "ally sprite" in ctx or "sprite symbiosis" in ctx or "sprite conduit" in ctx
        has_twin_hull = "twin" in ctx and ("silverstar" in ctx or "man-at-arms" in ctx or "drones" in ctx)
        has_conjuring = env.get("Conjuring", 0) >= 6
        has_monad_dual = "dual consciousness" in ctx or "monad" in ctx
        force_mult_met = has_ally_sprite or has_twin_hull or has_conjuring or has_monad_dual

    # 7. Scene Permeability (Infiltration, Social Disguise, Aura/Matrix Stealth)
    permeability_met = bool(dec.get("scene_permeability", False))
    if not permeability_met:
        permeability_markers = [
            "realistic features", "chameleon coating", "cosmetic control",
            "resculpt", "gender transmorphism", "masking", "stealth effect",
            "phantom", "finesse", "nanopaste disguise", "passive stealth"
        ]
        permeability_met = any(m in ctx for m in permeability_markers)

    # 8. Burst Ceiling (Peak Sovereign Pool >= 18d6)
    peak_pool = max(astral_pool, matrix_pool, phys_pool, social_pool)
    burst_met = bool(dec.get("burst_ceiling", peak_pool >= 18))

    scaffolding_pts = sum(
        1 for flag in [
            def_met, act_met, edge_met, durability_met,
            sustain_drain_met, force_mult_met, permeability_met, burst_met
        ] if flag
    )

    return {
        "defense_floor": {"met": def_met, "pool": def_pool, "points": 1 if def_met else 0},
        "action_economy": {"met": act_met, "dice": init_dice, "points": 1 if act_met else 0},
        "edge_engine": {"present": edge_met, "points": 1 if edge_met else 0},
        "durability_soak": {"met": durability_met, "points": 1 if durability_met else 0},
        "sustain_drain_economy": {"met": sustain_drain_met, "points": 1 if sustain_drain_met else 0},
        "force_multiplication": {"met": force_mult_met, "points": 1 if force_mult_met else 0},
        "scene_permeability": {"met": permeability_met, "points": 1 if permeability_met else 0},
        "burst_ceiling": {"met": burst_met, "peak_pool": peak_pool, "points": 1 if burst_met else 0},
        "scaffolding_points": scaffolding_pts,
    }


def parse_operational_breadth(content: str, full_context: str, env: Dict[str, Any]) -> Dict[str, Any]:
    """
    Parses or calculates the 20-Point Operational Breadth Score (OBS, 0-20) across 4 theaters
    (Astral, Matrix, Physical, Social: 0-3 pts each = 12) and 8 Tactical/Capability dimensions (+1 pt each = 8).
    """
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
        astral_pool = int(declared.get("astral", 0))
        matrix_pool = int(declared.get("matrix", 0))
        phys_pool = int(declared.get("physical", 0))
        social_pool = int(declared.get("social", 0))
        def_pool = int(declared.get("defense", 0))
        init_dice = int(declared.get("initiative_dice", 1))
        edge_engine = bool(declared.get("edge_engine", False))
    else:
        sec_text = _extract_section_text(full_context, r'Starting\s+(?:Operational\s+Pools|Stats/Pools|Pools)')
        if sec_text:
            is_declared = True
            parsed = _parse_pools_from_text(sec_text)
            astral_pool = parsed["astral"]
            matrix_pool = parsed["matrix"]
            phys_pool = parsed["physical"]
            social_pool = parsed["social"]
            def_pool = parsed["defense"]
            init_dice = parsed["initiative_dice"]
            edge_engine = parsed["edge_engine"]

    # Cold Baseline Fallback if not declared or incomplete
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
            if any(k in full_context.lower() for k in ["increase reflexes", "wired reflexes", "synaptic", "vr_hotsim", "hot-sim vr"]):
                init_dice = 4

        if not edge_engine:
            if any(q in full_context.lower() for q in ["analytical mind", "inspire competence", "aptitude", "brilliant heuristics", "wise warrior"]):
                edge_engine = True

    astral_pts, astral_tier = score_theater_pool(astral_pool)
    matrix_pts, matrix_tier = score_theater_pool(matrix_pool)
    phys_pts, phys_tier = score_theater_pool(phys_pool)
    social_pts, social_tier = score_theater_pool(social_pool)

    tactical = _evaluate_capability_scaffolding(
        full_context, env,
        astral_pool, matrix_pool, phys_pool, social_pool,
        def_pool, init_dice, edge_engine,
        declared=declared if is_declared else None,
    )

    total_obs = astral_pts + matrix_pts + phys_pts + social_pts + tactical["scaffolding_points"]
    active_planes = sum(1 for pts in [astral_pts, matrix_pts, phys_pts, social_pts] if pts >= 1)

    return {
        "total": total_obs,
        "max": 20,
        "active_planes": active_planes,
        "is_declared": is_declared,
        "theaters": {
            "astral": {"pool": astral_pool, "points": astral_pts, "tier": astral_tier},
            "matrix": {"pool": matrix_pool, "points": matrix_pts, "tier": matrix_tier},
            "physical": {"pool": phys_pool, "points": phys_pts, "tier": phys_tier},
            "social": {"pool": social_pool, "points": social_pts, "tier": social_tier},
        },
        "tactical": tactical,
    }


def _evaluate_session4_checkpoint(
    content: str,
    full_context: str,
    env: Dict[str, Any],
    day1_obs: Dict[str, Any],
    day1_tek: int,
    remaining_karma: int,
    remaining_cash: int,
) -> Dict[str, Any]:
    """
    Evaluates the Session 4 SRM Mulligan Checkpoint (+28 Karma / +30,000¥ / 4 Major & 4 Minor Actions).
    Reads declared `session4_pools(...)` or `## Session 4 Checkpoint` markdown when present,
    otherwise computes a deterministic projection from banked resources and active build hooks.
    """
    s4_dec = env.get("_session4_pools")
    s4_sec = _extract_section_text(full_context, r'Session\s*4\s*Checkpoint[^\n]*')
    ctx = full_context.lower()

    if isinstance(s4_dec, dict):
        astral = int(s4_dec.get("astral", day1_obs["theaters"]["astral"]["pool"]))
        matrix = int(s4_dec.get("matrix", day1_obs["theaters"]["matrix"]["pool"]))
        physical = int(s4_dec.get("physical", day1_obs["theaters"]["physical"]["pool"]))
        social = int(s4_dec.get("social", day1_obs["theaters"]["social"]["pool"]))
        defense = int(s4_dec.get("defense", day1_obs["tactical"]["defense_floor"]["pool"]))
        init_dice = int(s4_dec.get("initiative_dice", day1_obs["tactical"]["action_economy"]["dice"]))
        edge_eng = bool(s4_dec.get("edge_engine", day1_obs["tactical"]["edge_engine"]["present"]))
        bonus_tek = int(s4_dec.get("bonus_tek", 0))
        summary = str(s4_dec.get("summary", "Declared Session 4 Mulligan Checkpoint"))
        s4_tactical = _evaluate_capability_scaffolding(
            full_context + "\n" + s4_sec, env,
            astral, matrix, physical, social, defense, init_dice, edge_eng,
            declared=s4_dec,
        )
    elif s4_sec:
        parsed = _parse_pools_from_text(s4_sec)
        astral = parsed["astral"] or day1_obs["theaters"]["astral"]["pool"]
        matrix = parsed["matrix"] or day1_obs["theaters"]["matrix"]["pool"]
        physical = parsed["physical"] or day1_obs["theaters"]["physical"]["pool"]
        social = parsed["social"] or day1_obs["theaters"]["social"]["pool"]
        defense = parsed["defense"] or day1_obs["tactical"]["defense_floor"]["pool"]
        init_dice = parsed["initiative_dice"] if parsed["initiative_dice"] > 1 else day1_obs["tactical"]["action_economy"]["dice"]
        edge_eng = parsed["edge_engine"] or day1_obs["tactical"]["edge_engine"]["present"]
        s4_tactical = _evaluate_capability_scaffolding(
            full_context + "\n" + s4_sec, env,
            astral, matrix, physical, social, defense, init_dice, edge_eng,
        )
        m_tek = re.search(r'(?:Bonus\s+TEK|S4\s+Bonus\s+TEK|Trajectory\s+Dividend)\*{0,2}\s*[:=]\s*\*{0,2}\+?(\d+)', s4_sec, re.IGNORECASE)
        bonus_tek = int(m_tek.group(1)) if m_tek else 43
        m_sum = re.search(r'(?:Key\s+Unlocks|Summary|Highlights)\*{0,2}\s*[:=]\s*\*{0,2}(.*?)(?:\n|\Z)', s4_sec, re.IGNORECASE)
        summary = m_sum.group(1).strip() if m_sum else "Session 4 Mulligan Gate (+28K / +30,000¥)"
    else:
        # Generic deterministic projection for +28K / +30,000¥
        astral = day1_obs["theaters"]["astral"]["pool"]
        matrix = day1_obs["theaters"]["matrix"]["pool"]
        physical = day1_obs["theaters"]["physical"]["pool"]
        social = day1_obs["theaters"]["social"]["pool"]
        defense = day1_obs["tactical"]["defense_floor"]["pool"]
        init_dice = day1_obs["tactical"]["action_economy"]["dice"]
        edge_eng = day1_obs["tactical"]["edge_engine"]["present"]
        s4_tactical = _evaluate_capability_scaffolding(
            full_context, env,
            astral, matrix, physical, social, defense, init_dice, edge_eng,
        )
        # Base economic value of +28K + 30k¥ (15K base, 30K if DIY/Streetdoc)
        diy_mult = 2 if ("diy" in ctx or "working for the streetdoc" in ctx or "pilot origins" in ctx) else 1
        bonus_tek = 28 + remaining_karma + (15 * diy_mult) + (remaining_cash // NUYEN_PER_KARMA)
        summary = "Baseline +28 Karma / +30,000¥ advancement projection"

    a_pts, a_tier = score_theater_pool(astral)
    m_pts, m_tier = score_theater_pool(matrix)
    p_pts, p_tier = score_theater_pool(physical)
    s_pts, s_tier = score_theater_pool(social)

    s4_obs_total = a_pts + m_pts + p_pts + s_pts + s4_tactical["scaffolding_points"]
    s4_active_planes = sum(1 for pts in [a_pts, m_pts, p_pts, s_pts] if pts >= 1)
    s4_tek = day1_tek + bonus_tek

    return {
        "obs_total": s4_obs_total,
        "obs_max": 20,
        "obs_delta": s4_obs_total - day1_obs["total"],
        "active_planes": s4_active_planes,
        "tek": s4_tek,
        "ker": round(s4_tek / 100.0, 2),
        "bonus_tek": bonus_tek,
        "summary": summary,
        "theaters": {
            "astral": {"pool": astral, "points": a_pts, "tier": a_tier},
            "matrix": {"pool": matrix, "points": m_pts, "tier": m_tier},
            "physical": {"pool": physical, "points": p_pts, "tier": p_tier},
            "social": {"pool": social, "points": s_pts, "tier": s_tier},
        },
        "tactical": s4_tactical,
    }


def resolve_build_qmd_path(char_id_or_path: str) -> Optional[Path]:
    """Resolves character_build.qmd path from ID, directory, or direct file path."""
    p = Path(char_id_or_path).resolve()
    if p.is_file() and p.name.endswith(".qmd"):
        return p

    repo_root = Path(__file__).resolve().parent.parent.parent

    alias_map = {
        "dalakitnon_adept": ["mad_dalek", "dalakitnon_adept"],
        "etain": ["AshE", "etain"],
        "ashe": ["AshE", "ashe"],
        "yuriko": ["reiko", "yuriko"],
        "union": ["venn", "union"],
    }
    target_ids = alias_map.get(char_id_or_path.lower(), [char_id_or_path])

    candidates: List[Path] = [
        p / "core" / "character_build.qmd",
        p / "character_build.qmd",
    ]

    # Check characters.yaml repo mappings first
    try:
        configs = get_character_configs()
        for tid in target_ids:
            for cfg_key, cfg_val in configs.items():
                if cfg_key.lower() == tid.lower():
                    repo_rel = cfg_val.get("repo")
                    if repo_rel:
                        candidates.append(repo_root / repo_rel / "core" / "character_build.qmd")
                        candidates.append(repo_root / repo_rel / "character_build.qmd")
    except Exception:
        pass

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
    the Skillwire/Autosoft Dividend, 20-point OBS, Session 4 Checkpoint trajectory,
    and unspent resource compliance.
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
    # Isolate chargen-only portion (before Post-Chargen / In-Play Advancement / Session 4 sections)
    chargen_split = re.split(r'\n##\s*(?:Post-Chargen|In-Play Advancement|Session\s*4\s*Checkpoint)', content, maxsplit=1, flags=re.IGNORECASE)
    chargen_content = chargen_split[0]
    ctx_low = chargen_content.lower()
    full_low = full_context.lower()

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
    char_name = identity.get("name", str(char_id).title())
    metatype = identity.get("metatype", "Unknown")

    # 2. Evaluate variables & ledger trackers from python blocks in character_build.qmd
    env: Dict[str, Any] = {
        "_monad_abilities": [],
        "_adept_powers": [],
        "_spells": [],
        "_complex_forms": [],
        "_metamagics": [],
        "_echoes": [],
        "_nuyen_inflows": 0,
    }

    def _op_helper(**kwargs):
        env["_declared_pools"] = kwargs

    def _s4_helper(**kwargs):
        env["_session4_pools"] = kwargs

    env["operational_pools"] = _op_helper
    env["obs_pools"] = _op_helper
    env["session4_pools"] = _s4_helper

    pattern = re.compile(r'```\{python\}(.*?)```|`\{python\}\s*(.*?)`', re.DOTALL)
    for m in pattern.finditer(content):
        block, inline = m.groups()
        if block is not None:
            clean = "\n".join([l for l in block.splitlines() if not l.strip().startswith("#|")])
            try:
                exec(clean, env)
            except Exception:
                pass
            # Wrap inc/assign/inc_many and ledger helpers after definition block runs
            if "inc" in env and not getattr(env["inc"], "_wrapped", False):
                orig_inc = env["inc"]
                orig_assign = env.get("assign")
                orig_inc_many = env.get("inc_many")

                def tracked_inc(name, amount=1):
                    if name == "Nuyen" and amount > 0:
                        env["_nuyen_inflows"] += amount
                    return orig_inc(name, amount)

                def tracked_assign(name, value):
                    if name == "Nuyen" and value > 0:
                        env["_nuyen_inflows"] = max(env["_nuyen_inflows"], value)
                    return orig_assign(name, value)

                def tracked_inc_many(*pairs):
                    for name, amount in pairs:
                        if name == "Nuyen" and amount > 0:
                            env["_nuyen_inflows"] += amount
                    return orig_inc_many(*pairs)

                tracked_inc._wrapped = True  # type: ignore[attr-defined]
                env["inc"] = tracked_inc
                if orig_assign:
                    env["assign"] = tracked_assign
                if orig_inc_many:
                    env["inc_many"] = tracked_inc_many

                # Wrap ledger helpers if imported
                if "monad_ability" in env:
                    orig_ma = env["monad_ability"]
                    env["monad_ability"] = lambda *a, **kw: (env["_monad_abilities"].append(a[0] if a else ""), orig_ma(*a, **kw))[1]
                if "adept_power" in env:
                    orig_ap = env["adept_power"]
                    env["adept_power"] = lambda *a, **kw: (env["_adept_powers"].append({"name": a[0] if a else "", "cost_pp": kw.get("cost_pp", 0)}), orig_ap(*a, **kw))[1]
                if "complex_form" in env:
                    orig_cf = env["complex_form"]
                    env["complex_form"] = lambda *a, **kw: (env["_complex_forms"].append(a[0] if a else ""), orig_cf(*a, **kw))[1]
                if "spell" in env:
                    orig_sp = env["spell"]
                    env["spell"] = lambda *a, **kw: (env["_spells"].append(a[0] if a else ""), orig_sp(*a, **kw))[1]
                if "metamagic" in env:
                    orig_mm = env["metamagic"]
                    env["metamagic"] = lambda *a, **kw: (env["_metamagics"].append(a[0] if a else ""), orig_mm(*a, **kw))[1]
                if "echo" in env:
                    orig_ec = env["echo"]
                    env["echo"] = lambda *a, **kw: (env["_echoes"].append(a[0] if a else ""), orig_ec(*a, **kw))[1]

        elif inline is not None:
            code = inline.strip()
            try:
                eval(code, env)
            except Exception:
                try:
                    exec(code, env)
                except Exception:
                    pass

    # 3. Attributes Calculation (Data-Driven: Physical vs Digital Intelligence ASDF)
    is_di = env.get("Firewall", 0) > 0 or env.get("Data_Processing", 0) > 0
    if is_di:
        attr_names = ["Firewall", "Data_Processing", "Sleaze", "Attack", "Willpower", "Logic", "Intuition", "Charisma", "Edge", "Resonance"]
    else:
        attr_names = ["Body", "Agility", "Reaction", "Strength", "Willpower", "Logic", "Intuition", "Charisma", "Edge", "Magic", "Resonance", "Nanite_Volume"]

    base_attr_karma = 0
    attr_breakdown = {}
    for aname in attr_names:
        val = env.get(aname, 1 if aname not in ["Magic", "Resonance", "Nanite_Volume"] else 0)
        if isinstance(val, (int, float)) and val > 1:
            k = calculate_triangular_attribute(int(val))
            base_attr_karma += k
            attr_breakdown[aname.lower()] = {"rating": int(val), "karma": k}

    # 4. Skills Calculation
    skill_names = [
        "Tasking", "Electronics", "Cracking", "Sorcery", "Conjuring", "Influence",
        "Athletics", "Con", "Stealth", "Perception", "Piloting", "Engineering",
        "Close_Combat", "Firearms", "Exotic_Weapons"
    ]
    base_skills_karma = 0
    skills_breakdown = {}
    for sname in skill_names:
        r = env.get(sname, 0)
        if isinstance(r, (int, float)) and r > 0:
            k = calculate_triangular_skill(int(r))
            base_skills_karma += k
            skills_breakdown[sname.lower()] = {"rating": int(r), "karma": k}

    # 5. Augmentation & Quality Attribute Deltas (Data-Driven)
    ware_attr_delta_karma = 0
    ware_attr_details: List[str] = []

    if not is_di and ("synthetic cyberarm" in ctx_low or "synthetic cyberleg" in ctx_low):
        nat_agi = int(env.get("Agility", 1))
        nat_str = int(env.get("Strength", 1))
        redliner_bonus = 2 if "redliner" in ctx_low else 0
        if "two full synthetic cyberarms" in ctx_low:
            arm_agi_enh = 4 if "agility +4" in ctx_low or "agi+4" in ctx_low else 0
            arm_agi = max(nat_agi, 2 + arm_agi_enh + redliner_bonus)
            arm_str = max(nat_str, 2 + redliner_bonus)
            da = calculate_attribute_delta_karma(nat_agi, arm_agi)
            ds = calculate_attribute_delta_karma(nat_str, arm_str)
            if da + ds > 0:
                ware_attr_delta_karma += da + ds
                ware_attr_details.append(f"Cyberarms AGI {arm_agi} (+{da}k), STR {arm_str} (+{ds}k)")
        if "two full synthetic cyberlegs" in ctx_low:
            leg_agi_enh = 4 if "agility +4" in ctx_low or "agi+4" in ctx_low else 0
            leg_agi = max(nat_agi, 2 + leg_agi_enh + redliner_bonus)
            leg_str = max(nat_str, 2 + redliner_bonus)
            da = calculate_attribute_delta_karma(nat_agi, leg_agi)
            ds = calculate_attribute_delta_karma(nat_str, leg_str)
            if da + ds > 0:
                ware_attr_delta_karma += da + ds
                ware_attr_details.append(f"Cyberlegs AGI {leg_agi} (+{da}k), STR {leg_str} (+{ds}k)")

    nat_wil = int(env.get("Willpower", 1))
    aug_wil = nat_wil
    if "cyber singularity seeker" in ctx_low and ("4 full cyberlimbs" in ctx_low or "two full synthetic cyberlegs" in ctx_low):
        dw = calculate_attribute_delta_karma(aug_wil, aug_wil + 2)
        aug_wil += 2
        ware_attr_delta_karma += dw
        ware_attr_details.append(f"Cyber Singularity Seeker WIL {aug_wil-2}->{aug_wil} (+{dw}k)")
    if "bio-response override" in ctx_low:
        dw = calculate_attribute_delta_karma(aug_wil, aug_wil + 1)
        aug_wil += 1
        ware_attr_delta_karma += dw
        ware_attr_details.append(f"Bio-Response Override WIL {aug_wil-1}->{aug_wil} (+{dw}k)")
    if "neurochemical regulator" in ctx_low:
        nat_cha = int(env.get("Charisma", 1))
        dc = calculate_attribute_delta_karma(nat_cha, nat_cha + 1)
        ware_attr_delta_karma += dc
        ware_attr_details.append(f"Neurochemical Regulator CHA {nat_cha}->{nat_cha+1} (+{dc}k)")

    # 6. Pilot Origins & Drone Autosoft Physical Suite (4 Physical Domains)
    pilot_origins_dividend = 0
    pilot_origins_details: List[str] = []
    has_pilot_origins = "pilot origins" in ctx_low or "pilot_origins" in ctx_low or ("ai" in str(metatype).lower())

    if has_pilot_origins:
        # Control Rig replacement hardware delta (R3 = 106k¥ = 53K; R1 = 36k¥ = 18K)
        rig_r = 3 if re.search(r'pilot origins\s*(?:\(rating\s*3\)|r3)', ctx_low) else 1
        rig_delta = 53 if rig_r == 3 else 18
        pilot_origins_dividend += rig_delta
        pilot_origins_details.append(f"Pilot Origins R{rig_r} / Control Rig {rig_r} Delta (+{rig_delta}k)")

        # Parse peak Autosoft Rating (R9 vs R6) across build
        auto_ratings = [
            int(r) for r in re.findall(r'(?:autosofts?|clearsight|maneuvering|targeting)[^.\n]{0,60}(?:rating\s*|@?\s*r)(9|8|7|6|5|4)', ctx_low)
        ] + [
            int(r) for r in re.findall(r'(?:rating\s*|r)(9|8|7|6|5|4)\s+autosofts?', ctx_low)
        ]
        auto_rating = max(auto_ratings) if auto_ratings else 6

        gross_val = 4 * calculate_triangular_skill(auto_rating)
        soft_cost_k = (4 * auto_rating * 500) // NUYEN_PER_KARMA
        net_auto_dividend = gross_val - soft_cost_k
        pilot_origins_dividend += net_auto_dividend
        pilot_origins_details.append(f"Autosofts R{auto_rating} [4 Domains: Combat, Sensory, Infiltration, Mobility] (+{net_auto_dividend}k)")

    # 7. Skillwires / Synthetic Skill Driver Virtual Dividend (Deduplicated against Autosofts)
    skillwires_dividend = 0
    softs_detail = "None"

    if "synthetic skill driver" in ctx_low and has_pilot_origins:
        m_ssd = re.search(r'synthetic skill driver[^\n]{0,40}(?:rating\s*|r)(\d)', ctx_low)
        ssd_r = int(m_ssd.group(1)) if m_ssd else 6
        val_gross = 2 * calculate_triangular_skill(ssd_r)
        cost_softs = (2 * ssd_r * 5000) // NUYEN_PER_KARMA
        skillwires_dividend = val_gross - cost_softs
        softs_detail = f"Synthetic Skill Driver R{ssd_r} [Deduplicated: Social Domain 5 - Con & Influence] (+{skillwires_dividend}k)"
    else:
        sw_rating = 0
        if "skill rig pack a" in ctx_low:
            sw_rating = 6
        elif "skill rig pack b" in ctx_low:
            sw_rating = 5
        else:
            m_sw = re.search(r'skillwires\s*(?:\(rating\s*|rating\s*|r)(\d)', ctx_low)
            if m_sw:
                sw_rating = int(m_sw.group(1))
        if sw_rating > 0:
            val_gross = 5 * calculate_triangular_skill(sw_rating)
            cost_softs = (5 * sw_rating * 5000) // NUYEN_PER_KARMA
            skillwires_dividend = val_gross - cost_softs
            softs_detail = f"Skillwires R{sw_rating} (5 Universal Domains @ {calculate_triangular_skill(sw_rating)}k - {cost_softs}k soft cost = +{skillwires_dividend}k)"

    # 8. Magic / Resonance / Monad Assets
    magic_res_karma = 0
    magic_details: List[str] = []

    # Monad Abilities (5 Karma each)
    monad_count = len(env["_monad_abilities"]) or len(re.findall(r'monad_ability\(', content))
    if monad_count > 0:
        mk = monad_count * 5
        magic_res_karma += mk
        magic_details.append(f"{monad_count} Monad Abilities ({mk}k)")

    # Adept Powers (Valued via Force 4 Qi Focus replacement cost: 15.5 Karma / PP)
    if env["_adept_powers"]:
        total_pp = sum(float(ap.get("cost_pp", 0)) for ap in env["_adept_powers"])
        if "mentor spirit (wise warrior)" in ctx_low and not any("wise warrior" in str(ap).lower() for ap in env["_adept_powers"]):
            total_pp += 1.0
        if total_pp > 0:
            pp_karma = int(round(total_pp * QI_FOCUS_KARMA_PER_PP))
            magic_res_karma += pp_karma
            magic_details.append(f"Adept Powers ({total_pp:g} PP @ {QI_FOCUS_KARMA_PER_PP}k Qi Focus equiv = {pp_karma}k)")
    elif "mystic adept" in str(identity).lower() or "adept" in str(identity).lower():
        mag_val = env.get("Magic", 0)
        if mag_val > 0:
            pp_karma = int(round(float(mag_val) * QI_FOCUS_KARMA_PER_PP))
            magic_res_karma += pp_karma
            magic_details.append(f"Adept Powers ({mag_val} PP @ {QI_FOCUS_KARMA_PER_PP}k Qi Focus equiv = {pp_karma}k)")

    # Spells & Complex Forms (5 Karma each)
    spells_count = len(env["_spells"]) or len(re.findall(r'learn_spell|spell\(', full_context))
    if spells_count == 0 and env.get("Magic", 0) > 0:
        # Count explicitly declared free/starting spells in build doc
        free_spells = sum(1 for sp in ["increase reflexes", "increase attribute"] if sp in ctx_low)
        spells_count = free_spells
    cf_count = len(env["_complex_forms"]) or len(re.findall(r'complex_form\(', content))
    if spells_count > 0:
        magic_res_karma += spells_count * 5
        magic_details.append(f"{spells_count} Spells ({spells_count * 5}k)")
    if cf_count > 0:
        magic_res_karma += cf_count * 5
        magic_details.append(f"{cf_count} Complex Forms ({cf_count * 5}k)")

    # Submersion / Initiation (10 + Grade)
    echo_count = len(env["_echoes"]) or len(re.findall(r'echo\(', content))
    if echo_count >= 2 or "submersion grade 2" in ctx_low or "grades 1 & 2" in ctx_low or "technoshaman" in ctx_low:
        magic_res_karma += 23
        magic_details.append("Submersion Grade 2 (23k)")
    elif echo_count == 1 or "submersion" in ctx_low:
        magic_res_karma += 11
        magic_details.append("Submersion Grade 1 (11k)")
    elif len(env["_metamagics"]) >= 1 or "initiate grade: **1**" in ctx_low or "initiation grade 1" in ctx_low or "quickening" in ctx_low:
        magic_res_karma += 11
        magic_details.append("Initiate Grade 1 (11k)")

    # Focus Formulas & Bonding (chargen only; handles both `(R4)` and `(Rating 4)`)
    f_matches = re.findall(r'Focus\s*\((?:R|Rating\s*)(\d+)\)', chargen_content, re.IGNORECASE)
    if f_matches:
        for r_str in set(f_matches):
            r = int(r_str)
            f_k = (r * 4) + r  # formula cost + bonding karma
            magic_res_karma += f_k
            magic_details.append(f"Rating {r} Focus ({f_k}k)")

    # 9. Sovereign Sustained Magical Augmentations (Anchored Spells Dividend)
    sustained_spells_dividend = 0
    sustained_spells_details: List[str] = []

    anchor_slots = 0
    fc_match = re.search(r'Focused Concentration\s*(?:\(R(?:ating)?\s*(\d)\)|\b(R\d)\b)', full_context, re.IGNORECASE)
    if fc_match:
        val_str = fc_match.group(1) or fc_match.group(2)
        anchor_slots += int(re.sub(r'\D', '', val_str))
    if "quickening" in full_low:
        anchor_slots = max(anchor_slots, 3)
    if "sustaining focus" in full_low:
        anchor_slots += 1

    has_inc_attr = "increase attribute" in full_low or "increase_attribute" in full_low
    has_inc_refl = "increase reflexes" in full_low or "increase_reflexes" in full_low

    if anchor_slots > 0 and (has_inc_attr or has_inc_refl):
        available_slots = anchor_slots
        if has_inc_refl and available_slots > 0:
            available_slots -= 1
            base_rea = env.get("Reaction", 2)
            rea_delta = calculate_attribute_delta_karma(base_rea, base_rea + 3)
            init_dice_karma = 40
            refl_karma = rea_delta + init_dice_karma
            sustained_spells_dividend += refl_karma
            sustained_spells_details.append(f"Increase Reflexes (+3 REA / 4D6 total: +{refl_karma}k)")

        if has_inc_attr and available_slots > 0:
            is_decker = "cracking" in full_low or "cyberdeck" in full_low
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

    # 10. Gear / Nuyen Capital Spent (Data-Driven: Total Chargen Nuyen - Remaining Cash) / 2,000¥
    remaining_cash = int(env.get("Nuyen", 0))
    total_nuyen_in = int(env.get("_nuyen_inflows", 0))
    if "unable to rebuild gear" in ctx_low and total_nuyen_in > 0:
        gear_karma = total_nuyen_in // NUYEN_PER_KARMA
    elif total_nuyen_in > remaining_cash:
        gear_karma = round((total_nuyen_in - remaining_cash) / NUYEN_PER_KARMA)
    else:
        gear_karma = max(10, total_nuyen_in // NUYEN_PER_KARMA)

    # 11. Qualities Chargen Arbitrage (Positive Qualities cost 1x at chargen vs 2x post-chargen)
    qualities_net = 0
    for qname, qcost in POSITIVE_QUALITY_COSTS.items():
        # Match quality lines/bullets rather than incidental prose like "technoshaman mentor"
        if re.search(rf'(?:\*\*|^\s*[\*\-]\s*|\b){re.escape(qname)}(?:\s+stream)?(?:\*\*|\s*\(|\s*:)', ctx_low, re.MULTILINE):
            if qname == "technoshaman" and "sourceror" in ctx_low:
                continue
            qualities_net += qcost
    if re.search(r'pilot origins\s*\(rating\s*3\)', ctx_low):
        qualities_net += 16
    if qualities_net == 0:
        qualities_net = 15

    # TEK Sum
    tek = (
        base_attr_karma + ware_attr_delta_karma + base_skills_karma
        + pilot_origins_dividend + skillwires_dividend + magic_res_karma
        + sustained_spells_dividend + gear_karma + qualities_net
    )
    ker = round(tek / 100.0, 2)

    # 12. Unspent Resources Validation
    remaining_karma = int(env.get("Karma", 0))
    remaining_cp = int(env.get("Character_Points", 0))
    remaining_contacts = int(env.get("Contact_Points", 0))

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

    # 13. 20-Point Operational Breadth Score (OBS) & Session 4 Checkpoint
    obs = parse_operational_breadth(content, full_context, env)
    session4 = _evaluate_session4_checkpoint(
        content, full_context, env, obs, tek, remaining_karma, remaining_cash
    )

    return {
        "char_id": char_id,
        "name": char_name,
        "metatype": metatype,
        "build_file": str(build_path),
        "tek": tek,
        "ker": ker,
        "obs": obs,
        "session4": session4,
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
    """Formats 20-pt OBS, data-driven TEK, Session 4 Checkpoint, and resource validation."""
    status_badge = "[PASS: Complete & Table-Legal]" if res["is_complete"] else "[FAIL: Incomplete / Excess Resources]"
    b = res["breakdown"]
    u = res["unspent"]
    obs = res.get("obs", {})
    t = obs.get("theaters", {})
    tact = obs.get("tactical", {})
    s4 = res.get("session4", {})

    lines = [
        "=================================================================",
        " BUILD EFFICIENCY & OPERATIONAL BREADTH (OBS / TEK / S4) REPORT",
        f" Character : {res['name']} ({res['char_id']})",
        f" Metatype  : {res['metatype']}",
        f" Status    : {status_badge}",
        "=================================================================",
        "",
        f"  Operational Breadth Score (OBS) : {obs.get('total', 0)} / {obs.get('max', 20)} ({obs.get('active_planes', 0)}/4 Planes Active)",
        f"  Total Equivalent Karma (TEK)    : {res['tek']} Karma (KER: {res['ker']}x vs 100 CP baseline)",
    ]
    if s4:
        lines.append(
            f"  Session 4 Mulligan Checkpoint   : OBS {s4['obs_total']} / {s4['obs_max']} ({s4['obs_delta']:+d}) | "
            f"TEK {s4['tek']} (+{s4['bonus_tek']}k, KER {s4['ker']}x)"
        )

    lines.extend([
        "",
        "--- Pillar 1: Operational Theaters & 8 Capability Dimensions (OBS / 20) ---",
        f"  • Astral Plane Theater : {t.get('astral', {}).get('points', 0)} / 3 pts ({t.get('astral', {}).get('tier', 'Inert')}: {t.get('astral', {}).get('pool', 0)}d6)",
        f"  • Matrix Plane Theater : {t.get('matrix', {}).get('points', 0)} / 3 pts ({t.get('matrix', {}).get('tier', 'Inert')}: {t.get('matrix', {}).get('pool', 0)}d6)",
        f"  • Physical Plane Theater: {t.get('physical', {}).get('points', 0)} / 3 pts ({t.get('physical', {}).get('tier', 'Inert')}: {t.get('physical', {}).get('pool', 0)}d6)",
        f"  • Social Plane Theater : {t.get('social', {}).get('points', 0)} / 3 pts ({t.get('social', {}).get('tier', 'Inert')}: {t.get('social', {}).get('pool', 0)}d6)",
        f"  • Capability Scaffolding: +{tact.get('scaffolding_points', 0)} / 8 pts",
        f"      - Defense Floor (>=8d6)   : {'PASS' if tact.get('defense_floor', {}).get('met') else 'FAIL'} ({tact.get('defense_floor', {}).get('pool', 0)}d6)",
        f"      - Action Economy (>=2D6)  : {'PASS' if tact.get('action_economy', {}).get('met') else 'FAIL'} ({tact.get('action_economy', {}).get('dice', 1)}D6)",
        f"      - Edge Engine             : {'PASS' if tact.get('edge_engine', {}).get('present') else 'None'}",
        f"      - Durability / Soak       : {'PASS' if tact.get('durability_soak', {}).get('met') else 'None'}",
        f"      - Sustain / Drain Economy : {'PASS' if tact.get('sustain_drain_economy', {}).get('met') else 'None'}",
        f"      - Force Multiplication    : {'PASS' if tact.get('force_multiplication', {}).get('met') else 'None'}",
        f"      - Scene Permeability      : {'PASS' if tact.get('scene_permeability', {}).get('met') else 'None'}",
        f"      - Burst Ceiling (>=18d6)  : {'PASS' if tact.get('burst_ceiling', {}).get('met') else 'None'} (Peak {tact.get('burst_ceiling', {}).get('peak_pool', 0)}d6)",
        "",
        "--- Pillar 2: Build Efficiency Karma Breakdown (TEK) ---",
        f"  • Base Attributes (Triangular): {b['base_attributes']} Karma",
        f"  • Augmentation Attr Delta     : {b['ware_attr_delta']} Karma ({', '.join(b['ware_details']) if b['ware_details'] else 'None'})",
        f"  • Natural Skills (Triangular) : {b['natural_skills']} Karma",
        f"  • Pilot Origins & Drone Suite : {b['pilot_origins_dividend']} Karma ({', '.join(b['pilot_origins_details']) if b['pilot_origins_details'] else 'None'})",
        f"  • Skillwires Repertoire Suite : {b['skillwires_dividend']} Karma ({b['softs_detail']})",
        f"  • Magic / Resonance / Monad   : {b['magic_resonance']} Karma ({', '.join(b['magic_details']) if b['magic_details'] else 'None'})",
        f"  • Sustained Spells Dividend   : {b['sustained_spells_dividend']} Karma ({', '.join(b['sustained_spells_details']) if b['sustained_spells_details'] else 'None'})",
        f"  • Gear Capital Spent (¥/2000) : {b['gear_karma']} Karma",
        f"  • Positive Quality Arbitrage  : {b['qualities_net']} Karma",
    ])

    if s4:
        lines.extend([
            "",
            "--- Pillar 3: Session 4 SRM Mulligan Checkpoint (+28K / +30,000¥) ---",
            f"  • Projected OBS : {s4['obs_total']} / {s4['obs_max']} ({s4['active_planes']}/4 Planes Active)",
            f"  • Projected TEK : {s4['tek']} Karma (+{s4['bonus_tek']}k trajectory dividend, KER {s4['ker']}x)",
            f"  • Key Unlocks   : {s4['summary']}",
        ])

    lines.extend([
        "",
        "--- Unspent Resource Compliance ---",
        f"  • Pocket Cash Remaining       : ¥{u['cash']:,} {'[PASS]' if u['cash'] <= 5000 else '[FAIL - Exceeds ¥5,000]'}",
        f"  • Customization Karma Left    : {u['karma']} Karma {'[PASS]' if u['karma'] <= 5 else '[FAIL - Exceeds 5k]'}",
        f"  • Character Points Left       : {u['character_points']} CP {'[PASS]' if u['character_points'] == 0 else '[FAIL - Unallocated]'}",
        f"  • Contact Points Left         : {u['contact_points']} pts {'[PASS]' if u['contact_points'] == 0 else '[FAIL - Unallocated]'}",
    ])

    if res["violations"]:
        lines.append("")
        lines.append("--- Action Items & Violations ---")
        for v in res["violations"]:
            lines.append(f"  [!] {v}")

    lines.append("=================================================================")
    return "\n".join(lines)


def _format_check(flag: bool) -> str:
    return "✅" if flag else "—"


def generate_lab_scorecard_markdown(output_path: Optional[Path] = None) -> str:
    """
    Dynamically evaluates every character in `characters.yaml` via `calculate_build_efficiency()`
    and writes an auto-generated Markdown scorecard (`characters/lab/scorecard.md`).
    """
    repo_root = Path(__file__).resolve().parent.parent.parent
    target_path = Path(output_path) if output_path else (repo_root / "characters" / "lab" / "scorecard.md")

    configs = get_character_configs()
    rows: List[Dict[str, Any]] = []
    for cid, cfg in configs.items():
        try:
            res = calculate_build_efficiency(cid)
            res["_cfg"] = cfg
            res["_cid"] = cid
            rows.append(res)
        except Exception:
            continue

    # Sort Lab prototypes first (by Session-4 TEK desc), then Active references (by Session-4 TEK desc)
    rows.sort(
        key=lambda r: (
            0 if r["_cfg"].get("status", "prototype") != "active" else 1,
            -r.get("session4", {}).get("tek", r["tek"]),
        )
    )

    lines: List[str] = [
        "# Benchmark Comparative Scorecard",
        "",
        "> **Auto-Generated Telemetry:** This scorecard is compiled automatically from `characters.yaml` and each character's `character_build.qmd` during `uv run sr6 sync-all` and `uv run sr6 build`. Do not edit this file manually—update the source build files or `sr6core/creation/efficiency.py` instead.",
        "",
        "See [Lab Overview & Evaluation Rubrics](index.qmd) for the full 20-point OBS, Data-Driven TEK, and Session 4 SRM Mulligan Checkpoint definitions.",
        "",
        "---",
        "",
        "## 1. Day-1 vs. Session 4 Mulligan Scorecard",
        "",
        "| Character | Status & Archetype | Planes<br>(D1 → S4) | OBS (0–20)<br>(D1 → S4) | Day-1 TEK (KER) | Session-4 TEK (KER) | Session-4 Mulligan Gate Highlights (+28K / +30,000¥) | Resource Audit |",
        "| :--- | :--- | :---: | :---: | :---: | :---: | :--- | :---: |",
    ]

    for r in rows:
        cid = r["_cid"]
        cfg = r["_cfg"]
        status_raw = cfg.get("status", "prototype")
        badge = "`<LAB>`" if status_raw != "active" else "`ACTIVE`"
        role = cfg.get("role", r["metatype"])
        obs = r["obs"]
        s4 = r["session4"]
        u = r["unspent"]
        audit_str = (
            f"**PASS** (`{u['karma']}K`, `¥{u['cash']:,}`)"
            if r["is_complete"]
            else f"**FAIL** (`{u['karma']}K`, `¥{u['cash']:,}`)"
        )
        summary = s4["summary"].replace("|", "/")
        lines.append(
            f"| **{r['name']}** (`{cid}`) | {badge} {role} | "
            f"**{obs['active_planes']}/4 → {s4['active_planes']}/4** | "
            f"**{obs['total']} → {s4['obs_total']}** | "
            f"**{r['tek']:,}** ({r['ker']}x) | "
            f"**{s4['tek']:,}** ({s4['ker']}x, +{s4['bonus_tek']}k) | "
            f"{summary} | {audit_str} |"
        )

    lines.extend([
        "",
        "---",
        "",
        "## 2. Day-1 Operational Planes & 8-Dimension Capability Matrix",
        "",
        "| Character | Astral | Matrix | Physical | Social | Def | Act | Edge | Soak | Sustain | Force | Perm | Burst | **OBS** |",
        "| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |",
    ])

    for r in rows:
        t = r["obs"]["theaters"]
        sc = r["obs"]["tactical"]
        lines.append(
            f"| **{r['name']}** | "
            f"{t['astral']['pool']}d6 ({t['astral']['points']}) | "
            f"{t['matrix']['pool']}d6 ({t['matrix']['points']}) | "
            f"{t['physical']['pool']}d6 ({t['physical']['points']}) | "
            f"{t['social']['pool']}d6 ({t['social']['points']}) | "
            f"{_format_check(sc['defense_floor']['met'])} | "
            f"{_format_check(sc['action_economy']['met'])} | "
            f"{_format_check(sc['edge_engine']['present'])} | "
            f"{_format_check(sc['durability_soak']['met'])} | "
            f"{_format_check(sc['sustain_drain_economy']['met'])} | "
            f"{_format_check(sc['force_multiplication']['met'])} | "
            f"{_format_check(sc['scene_permeability']['met'])} | "
            f"{_format_check(sc['burst_ceiling']['met'])} | "
            f"**{r['obs']['total']} / 20** |"
        )

    lines.extend([
        "",
        "---",
        "",
        "## 3. Data-Driven TEK Karma Breakdown Ledger",
        "",
        "| Character | Base Attrs | Ware Delta | Natural Skills | Pilot & Drones | Skillwires | Magic / Res / Monad | Anchored Spells | Gear Capital | Quality Arbitrage | **Day-1 TEK** |",
        "| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |",
    ])

    for r in rows:
        b = r["breakdown"]
        lines.append(
            f"| **{r['name']}** | "
            f"{b['base_attributes']} | "
            f"{b['ware_attr_delta']} | "
            f"{b['natural_skills']} | "
            f"{b['pilot_origins_dividend']} | "
            f"{b['skillwires_dividend']} | "
            f"{b['magic_resonance']} | "
            f"{b['sustained_spells_dividend']} | "
            f"{b['gear_karma']} | "
            f"{b['qualities_net']} | "
            f"**{r['tek']:,}** |"
        )

    md = "\n".join(lines) + "\n"
    target_path.parent.mkdir(parents=True, exist_ok=True)
    target_path.write_text(md, encoding="utf-8")
    return md
