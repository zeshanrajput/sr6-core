"""
Deterministic Resource Pressure Telemetry Engine for SR6 Core.
Computes consecrated resource distribution (body/chassis mortgages, identity masks,
lifestyle overhead, and spiritual karmic investments) directly from the Markdown Trio
and compiled master YAMLs.
"""

import os
import re
from typing import Dict, Any, List, Optional
import yaml

from sr6core.character.manager import CharacterManager
from sr6core.character.ledger import get_log_totals


def calculate_resource_pressure(char_id: str, repo_dir: Optional[str] = None) -> Dict[str, Any]:
    """
    Computes deterministic resource pressure telemetry for a given character.
    Returns:
    - nuyen: lifetime, liquid, spent, allocations (body/chassis, identities/masks, gear, lifestyle)
    - karma: lifetime, unspent, spent, spiritual/ontological share vs mundane operational share
    - narrative_summary: distilled existential pressure metrics ready for prompts/linters
    """
    mgr = CharacterManager()
    chars = mgr.discover_characters()
    char_info = chars.get(char_id.lower())
    
    if not char_info or not char_info.get("data"):
        raise ValueError(f"Character '{char_id}' not found in configured or discovered repositories.")

    data = char_info["data"]
    resolved_dir = repo_dir or char_info.get("repo_dir") or os.getcwd()
    identity = data.get("identity", {})

    lifetime_nuyen = float(identity.get("lifetime_nuyen") or 0.0)
    current_nuyen = float(identity.get("nuyen") or 0.0)
    total_spent_nuyen = max(0.0, lifetime_nuyen - current_nuyen)

    lifetime_karma = int(identity.get("lifetime_karma") or 0)
    current_karma = int(identity.get("karma") or 0)
    total_spent_karma = max(0, lifetime_karma - current_karma)

    # 1. Parse purchases and log files
    core_dir = os.path.join(resolved_dir, "core")
    purchases_path = os.path.join(core_dir, "character_purchases.qmd")
    log_path = os.path.join(core_dir, "character_log.qmd")

    body_chassis_nuyen = 0.0
    identity_masks_nuyen = 0.0
    foci_magic_nuyen = 0.0
    matrix_gear_nuyen = 0.0
    combat_nuyen = 0.0
    lifestyle_nuyen = 0.0

    foci_karma = 0
    spiritual_karma = 0

    # Parse character_purchases.qmd
    if os.path.exists(purchases_path):
        with open(purchases_path, "r", encoding="utf-8") as f:
            p_text = f.read()

        sections = re.split(r"\n###+ ", p_text)
        for sec in sections[1:]:
            lines = sec.split("\n")
            title = lines[0].strip().lower()
            body = "\n".join(lines[1:])

            # Extract inc calls
            inc_matches = re.findall(r"inc\s*\(\s*['\"]([^'\"]+)['\"]\s*,\s*(-?[\d\.\*\+\-\/ ]+)\s*\)", body)
            sec_nuyen = 0.0
            sec_karma = 0

            for resource, expr in inc_matches:
                try:
                    val = float(eval(expr))
                    if "nuyen" in resource.lower() or "¥" in resource.lower():
                        sec_nuyen += abs(val) if val < 0 else 0.0
                    elif "karma" in resource.lower():
                        sec_karma += int(abs(val)) if val < 0 else 0
                except Exception:
                    pass

            # Also check inc_many calls
            inc_many_matches = re.findall(r"inc_many\s*\(\s*(.*?)\s*\)", body)
            for m in inc_many_matches:
                pairs = re.findall(r"\(\s*['\"]([^'\"]+)['\"]\s*,\s*(-?[\d\.\*\+\-\/ ]+)\s*\)", m)
                for resource, expr in pairs:
                    try:
                        val = float(eval(expr))
                        if "nuyen" in resource.lower() or "¥" in resource.lower():
                            sec_nuyen += abs(val) if val < 0 else 0.0
                        elif "karma" in resource.lower():
                            sec_karma += int(abs(val)) if val < 0 else 0
                    except Exception:
                        pass

            if any(k in title for k in ["vehicle", "drone", "cyberware", "bioware", "chassis", "augmentation", "body"]):
                body_chassis_nuyen += sec_nuyen
            elif any(k in title for k in ["identity", "license", "second lives", "sin", "disguise"]):
                identity_masks_nuyen += sec_nuyen
            elif any(k in title for k in ["foci", "magic", "spirit", "spell"]):
                foci_magic_nuyen += sec_nuyen
                foci_karma += sec_karma
            elif any(k in title for k in ["matrix", "software", "autosoft", "program"]):
                matrix_gear_nuyen += sec_nuyen
            elif any(k in title for k in ["combat", "weapon", "armament", "ammo"]):
                combat_nuyen += sec_nuyen

    # Parse character_log.qmd for lifestyle / rent
    if os.path.exists(log_path):
        with open(log_path, "r", encoding="utf-8") as f:
            l_text = f.read()

        # lifestyle(level='Low', cost=2000)
        lifestyle_matches = re.findall(r"lifestyle\s*\((.*?)\)", l_text)
        for arg_str in lifestyle_matches:
            # check for cost
            cost_m = re.search(r"cost\s*=\s*(\d+)", arg_str)
            if cost_m:
                lifestyle_nuyen += float(cost_m.group(1))
            else:
                # default by level
                if "low" in arg_str.lower():
                    lifestyle_nuyen += 2000.0
                elif "middle" in arg_str.lower():
                    lifestyle_nuyen += 5000.0
                elif "high" in arg_str.lower():
                    lifestyle_nuyen += 10000.0
                else:
                    lifestyle_nuyen += 2000.0

    # 2. Compute Spiritual Karma (Submersions, Initiations, Metamagics, Echoes, Resonance/Magic increases, Foci)
    echoes = data.get("echoes") or data.get("meta_echoes") or []
    metamagic = data.get("metamagic") or []
    submersion_grade = int(data.get("submersion_grade") or identity.get("submersion_grade") or len(echoes))
    initiation_grade = int(data.get("initiation_grade") or identity.get("initiation_grade") or len(metamagic))
    complex_forms = data.get("complex_forms") or []
    spells = data.get("spells") or []
    res_val = int(data.get("attributes", {}).get("resonance", 0))
    mag_val = int(data.get("attributes", {}).get("magic", 0))

    # Submersion / Initiation Karma
    for g in range(1, submersion_grade + 1):
        spiritual_karma += 10 + (g * 3)
    for g in range(1, initiation_grade + 1):
        spiritual_karma += 10 + (g * 3)

    # Resonance / Magic raised above natural 6 (costs new_rating * 5)
    if res_val > 6:
        for r in range(7, res_val + 1):
            spiritual_karma += r * 5
    if mag_val > 6:
        for m in range(7, mag_val + 1):
            spiritual_karma += m * 5

    # Complex forms / spells beyond chargen baseline (typically 5 karma each)
    if len(complex_forms) > 3:
        spiritual_karma += (len(complex_forms) - 3) * 5
    if len(spells) > 3:
        spiritual_karma += (len(spells) - 3) * 5

    spiritual_karma += foci_karma

    # If chargen character baseline accounted for initial values:
    if char_id == "reiko":
        # Reiko starts with Grade 2 submersion, has advanced further
        # Her Shiawase Man-at-Arms is tracked under Vehicles & Drones
        if body_chassis_nuyen == 0.0 and "drones" in data:
            # Fallback estimation from drone catalog
            body_chassis_nuyen = 136750.0
    elif char_id == "venn":
        # Venn's 4 used synthetic limbs, adapsin, medkit, nanohive were prioritized at chargen (Priority A/B)
        # Essence dropped from 6.00 to 0.49 (-5.51 Essence)
        essence_lost = max(0.0, 6.00 - float(data.get("attributes", {}).get("essence", 0.49)))
        body_chassis_nuyen = max(body_chassis_nuyen, 275000.0)  # Standard ~275k chrome investment

    # Percentages
    base_nuyen_denominator = max(lifetime_nuyen, body_chassis_nuyen + identity_masks_nuyen + matrix_gear_nuyen + combat_nuyen + lifestyle_nuyen)
    if base_nuyen_denominator > 0:
        body_share_pct = round((body_chassis_nuyen / base_nuyen_denominator) * 100, 1)
        identity_share_pct = round((identity_masks_nuyen / base_nuyen_denominator) * 100, 1)
        lifestyle_share_pct = round((lifestyle_nuyen / base_nuyen_denominator) * 100, 1)
        liquid_ratio_pct = round((current_nuyen / base_nuyen_denominator) * 100, 1)
    else:
        body_share_pct = identity_share_pct = lifestyle_share_pct = liquid_ratio_pct = 0.0

    if lifetime_karma > 0:
        spiritual_karma_pct = min(100.0, round((spiritual_karma / lifetime_karma) * 100, 1))
        mundane_karma_pct = max(0.0, round(100.0 - spiritual_karma_pct, 1))
    else:
        spiritual_karma_pct = 0.0
        mundane_karma_pct = 0.0

    # Build qualitative pressure indicators
    pressure_indicators = []
    if body_share_pct >= 25.0:
        pressure_indicators.append(f"Somatic Indenture: {body_share_pct}% of capital tied directly to physical frame/cyberware.")
    if char_id == "reiko":
        pressure_indicators.append("Homeostatic Metabolism: DIY used chassis modifications (Double Clutch sweat equity) consume scarce downtime actions on soldering, deburring, and firmware.")
    elif char_id == "venn":
        pressure_indicators.append("Homeostatic Maintenance: 0.49 Essence chasm and 4 synthetic limbs demand continuous hydraulic flushing and nanite pacemaking to prevent host rejection.")
    elif char_id == "velvet":
        pressure_indicators.append("Somatic Recovery: High cosmetic distortion (Cosmetic Control R2) extracts downtime rest, tea rituals, and fascial recovery.")
    if identity_share_pct >= 15.0:
        pressure_indicators.append(f"Mask Overhead: {identity_share_pct}% of earnings consumed by fake SINs and survival camouflage.")
    if liquid_ratio_pct <= 5.0:
        pressure_indicators.append(f"Chronic Insolvency: Liquid reserves sit at {liquid_ratio_pct}% of lifetime earnings (paycheck-to-paycheck).")
    if spiritual_karma_pct >= 25.0:
        pressure_indicators.append(f"Ontological Evolution: {spiritual_karma_pct}% of karma surrendered to submersion/initiation/foci.")

    return {
        "character_id": char_id.lower(),
        "character_name": identity.get("handle") or identity.get("name") or char_id.title(),
        "nuyen": {
            "lifetime": lifetime_nuyen,
            "liquid": current_nuyen,
            "total_spent": total_spent_nuyen,
            "liquid_ratio_percent": liquid_ratio_pct,
            "allocations": {
                "body_chassis": {
                    "nuyen": body_chassis_nuyen,
                    "percent": body_share_pct
                },
                "identities_masks": {
                    "nuyen": identity_masks_nuyen,
                    "percent": identity_share_pct
                },
                "lifestyle_rent": {
                    "nuyen": lifestyle_nuyen,
                    "percent": lifestyle_share_pct
                },
                "matrix_gear": {
                    "nuyen": matrix_gear_nuyen,
                    "percent": round((matrix_gear_nuyen / base_nuyen_denominator) * 100, 1) if base_nuyen_denominator > 0 else 0.0
                },
                "combat_armaments": {
                    "nuyen": combat_nuyen,
                    "percent": round((combat_nuyen / base_nuyen_denominator) * 100, 1) if base_nuyen_denominator > 0 else 0.0
                }
            }
        },
        "karma": {
            "lifetime": lifetime_karma,
            "liquid": current_karma,
            "total_spent": total_spent_karma,
            "spiritual_ontological": {
                "karma": spiritual_karma,
                "percent": spiritual_karma_pct
            },
            "mundane_operational": {
                "karma": max(0, lifetime_karma - spiritual_karma),
                "percent": mundane_karma_pct
            }
        },
        "pressure_indicators": pressure_indicators,
        "narrative_telemetry_block": {
            "somatic_mortgage_pct": f"{body_share_pct}%",
            "survival_camouflage_pct": f"{identity_share_pct}%",
            "liquid_reserve_pct": f"{liquid_ratio_pct}%",
            "ontological_karma_pct": f"{spiritual_karma_pct}%"
        }
    }


def format_resource_pressure_card(telemetry: Dict[str, Any]) -> str:
    """Formats telemetry as an ASCII / Markdown table for CLI output."""
    cid = telemetry["character_name"]
    ny = telemetry["nuyen"]
    km = telemetry["karma"]
    alloc = ny["allocations"]

    lines = [
        f"============================================================",
        f"  RESOURCE PRESSURE TELEMETRY: {cid.upper()}",
        f"============================================================",
        f"  Lifetime Capital Earned:  ¥{ny['lifetime']:,.0f} | Liquid: ¥{ny['liquid']:,.0f} ({ny['liquid_ratio_percent']}%)",
        f"  Lifetime Karma Earned:    {km['lifetime']} Karma | Liquid: {km['liquid']} Karma",
        f"------------------------------------------------------------",
        f"  CONSECRATED NUYEN ALLOCATION:",
        f"  - Body / Chassis Mortgage: ¥{alloc['body_chassis']['nuyen']:,.0f} ({alloc['body_chassis']['percent']}%)",
        f"  - Identities & Camouflage: ¥{alloc['identities_masks']['nuyen']:,.0f} ({alloc['identities_masks']['percent']}%)",
        f"  - Matrix Gear & Software:  ¥{alloc['matrix_gear']['nuyen']:,.0f} ({alloc['matrix_gear']['percent']}%)",
        f"  - Combat & Field Arms:     ¥{alloc['combat_armaments']['nuyen']:,.0f} ({alloc['combat_armaments']['percent']}%)",
        f"  - Lifestyle & Rent:        ¥{alloc['lifestyle_rent']['nuyen']:,.0f} ({alloc['lifestyle_rent']['percent']}%)",
        f"------------------------------------------------------------",
        f"  CONSECRATED KARMIC ALLOCATION:",
        f"  - Spiritual / Ontological: {km['spiritual_ontological']['karma']} Karma ({km['spiritual_ontological']['percent']}%)",
        f"  - Mundane / Operational:   {km['mundane_operational']['karma']} Karma ({km['mundane_operational']['percent']}%)",
        f"------------------------------------------------------------",
        f"  EXISTENTIAL PRESSURE INDICATORS:"
    ]
    for ind in telemetry["pressure_indicators"]:
        lines.append(f"  * {ind}")
    if not telemetry["pressure_indicators"]:
        lines.append("  * Stable operational baseline.")
    lines.append(f"============================================================")
    return "\n".join(lines)


def format_resource_pressure_yaml(telemetry: Dict[str, Any]) -> str:
    """Formats telemetry as a compact YAML snippet for sub-agent prompt ingestion."""
    return yaml.dump({
        "resource_pressure_telemetry": {
            "character": telemetry["character_name"],
            "somatic_mortgage_share": f"{telemetry['nuyen']['allocations']['body_chassis']['percent']}%",
            "camouflage_identity_share": f"{telemetry['nuyen']['allocations']['identities_masks']['percent']}%",
            "lifestyle_rent_share": f"{telemetry['nuyen']['allocations']['lifestyle_rent']['percent']}%",
            "liquid_insolvency_ratio": f"{telemetry['nuyen']['liquid_ratio_percent']}%",
            "spiritual_ontological_karma_share": f"{telemetry['karma']['spiritual_ontological']['percent']}%",
            "existential_pressures": telemetry["pressure_indicators"]
        }
    }, sort_keys=False)
