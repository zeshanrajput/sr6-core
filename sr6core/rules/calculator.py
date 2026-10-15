"""
Cyberlimb & Augmentation Mathematics Engine for SR6 Core.
Automates capacity calculations, grade multipliers, Adapsin essence discounts, and enhancement tracking.
"""

from typing import Dict, Any, List, Optional, Tuple

GRADE_MULTIPLIERS = {
    "standard": {"cost": 1.0, "essence": 1.0, "avail_mod": 0},
    "used": {"cost": 0.5, "essence": 1.1, "avail_mod": -1},
    "alphaware": {"cost": 1.2, "essence": 0.8, "avail_mod": 1},
    "alpha": {"cost": 1.2, "essence": 0.8, "avail_mod": 1},
    "betaware": {"cost": 1.5, "essence": 0.7, "avail_mod": 2},
    "beta": {"cost": 1.5, "essence": 0.7, "avail_mod": 2},
    "deltaware": {"cost": 2.5, "essence": 0.5, "avail_mod": 3},
    "delta": {"cost": 2.5, "essence": 0.5, "avail_mod": 3},
}

BASE_LIMBS = {
    "arm": {"name": "Cyberarm", "base_essence": 1.0, "base_cost": 20000, "synthetic_cap": 8, "obvious_cap": 15},
    "cyberarm": {"name": "Cyberarm", "base_essence": 1.0, "base_cost": 20000, "synthetic_cap": 8, "obvious_cap": 15},
    "leg": {"name": "Cyberleg", "base_essence": 1.0, "base_cost": 20000, "synthetic_cap": 10, "obvious_cap": 15},
    "cyberleg": {"name": "Cyberleg", "base_essence": 1.0, "base_cost": 20000, "synthetic_cap": 10, "obvious_cap": 15},
    "torso": {"name": "Cybertorso", "base_essence": 1.5, "base_cost": 25000, "synthetic_cap": 10, "obvious_cap": 15},
    "cybertorso": {"name": "Cybertorso", "base_essence": 1.5, "base_cost": 25000, "synthetic_cap": 10, "obvious_cap": 15},
    "skull": {"name": "Cyberskull", "base_essence": 0.75, "base_cost": 15000, "synthetic_cap": 2, "obvious_cap": 4},
    "cyberskull": {"name": "Cyberskull", "base_essence": 0.75, "base_cost": 15000, "synthetic_cap": 2, "obvious_cap": 4},
}


def calculate_cyberlimb(
    limb: str = "cyberarm",
    synthetic: bool = True,
    grade: str = "standard",
    adapsin: bool = False,
    agi_enhancement: int = 0,
    str_enhancement: int = 0,
    armor_enhancement: int = 0,
    bulk_mod: int = 0,
    accessories: Optional[List[Dict[str, Any]]] = None,
) -> Dict[str, Any]:
    """
    Calculates exact costs, essence, capacities, and resulting attributes for a cyberlimb.
    """
    clean_limb = limb.strip().lower().replace(" ", "").replace("_", "").replace("-", "")
    base_info = BASE_LIMBS.get(clean_limb) or BASE_LIMBS["cyberarm"]

    clean_grade = grade.strip().lower()
    g_info = GRADE_MULTIPLIERS.get(clean_grade, GRADE_MULTIPLIERS["standard"])

    # Base essence & grade scaling
    limb_essence = base_info["base_essence"] * g_info["essence"]
    if adapsin:
        # Adapsin gives 10% Essence reduction post-grade on cyberware
        limb_essence = round(limb_essence * 0.90, 2)
    else:
        limb_essence = round(limb_essence, 2)

    # Base capacity
    base_capacity = base_info["synthetic_cap"] if synthetic else base_info["obvious_cap"]
    total_capacity = base_capacity + bulk_mod

    # Base cost
    limb_shell_cost = int(base_info["base_cost"] * g_info["cost"])

    # Bulk mod cost (1,000¥ per rating)
    bulk_cost = bulk_mod * 1000

    # Enhancements (2,500¥ and 1 Cap per rating)
    agi_cost = agi_enhancement * 2500
    str_cost = str_enhancement * 2500
    armor_cost = armor_enhancement * 2500

    enhancements_cost = agi_cost + str_cost + armor_cost
    enhancements_cap = agi_enhancement + str_enhancement + armor_enhancement

    # Accessories
    acc_list = accessories or []
    acc_cost = sum(a.get("cost", 0) for a in acc_list)
    acc_cap = sum(a.get("capacity", 0) for a in acc_list)

    total_cost = limb_shell_cost + bulk_cost + enhancements_cost + acc_cost
    used_capacity = enhancements_cap + acc_cap
    free_capacity = total_capacity - used_capacity

    return {
        "limb": base_info["name"],
        "appearance": "Synthetic" if synthetic else "Obvious",
        "grade": clean_grade.capitalize(),
        "adapsin_active": adapsin,
        "final_essence": limb_essence,
        "base_capacity": base_capacity,
        "bulk_mod_rating": bulk_mod,
        "total_capacity": total_capacity,
        "used_capacity": used_capacity,
        "free_capacity": free_capacity,
        "is_legal_capacity": free_capacity >= 0,
        "limb_shell_cost": limb_shell_cost,
        "bulk_mod_cost": bulk_cost,
        "enhancements": {
            "agility": {"rating": agi_enhancement, "cost": agi_cost, "cap": agi_enhancement},
            "strength": {"rating": str_enhancement, "cost": str_cost, "cap": str_enhancement},
            "armor": {"rating": armor_enhancement, "cost": armor_cost, "cap": armor_enhancement},
        },
        "enhancements_cost": enhancements_cost,
        "accessories": acc_list,
        "accessories_cost": acc_cost,
        "total_cost": total_cost,
        "resulting_attributes": {
            "agility": 2 + agi_enhancement,
            "strength": 2 + str_enhancement,
            "defense_rating_bonus": armor_enhancement
        }
    }


def calculate_ware(
    name: str,
    base_cost: int,
    base_essence: float,
    grade: str = "standard",
    is_bioware: bool = False,
    adapsin: bool = False,
) -> Dict[str, Any]:
    """
    Calculates grade adjustments and Adapsin interaction for general cyberware or bioware.
    """
    clean_grade = grade.strip().lower()
    g_info = GRADE_MULTIPLIERS.get(clean_grade, GRADE_MULTIPLIERS["standard"])

    cost = int(base_cost * g_info["cost"])
    ess = base_essence * g_info["essence"]

    adapsin_applied = False
    adapsin_warning = None
    if adapsin:
        if is_bioware:
            adapsin_warning = "Adapsin therapy only reduces cyberware Essence costs (bioware is exempt)."
        else:
            ess = ess * 0.90
            adapsin_applied = True

    final_essence = round(ess, 2)

    return {
        "name": name,
        "type": "Bioware" if is_bioware else "Cyberware",
        "grade": clean_grade.capitalize(),
        "base_cost": base_cost,
        "final_cost": cost,
        "base_essence": base_essence,
        "final_essence": final_essence,
        "adapsin_applied": adapsin_applied,
        "adapsin_warning": adapsin_warning,
    }


def format_limb_calculation(calc: Dict[str, Any]) -> str:
    """Renders a clean markdown report of the limb calculation."""
    lines = [
        f"### Cyberlimb Specification: {calc['appearance']} {calc['limb']} ({calc['grade']} Grade)",
        f"> **Final Essence**: `{calc['final_essence']}` | **Total Cost**: `{calc['total_cost']:,}¥` | **Capacity**: `{calc['used_capacity']} / {calc['total_capacity']}` ({calc['free_capacity']} Open)",
        ""
    ]

    if not calc["is_legal_capacity"]:
        lines.append(f"> [!CAUTION]\n> **OVER CAPACITY!** Exceeds maximum capacity by {abs(calc['free_capacity'])} slots!\n")

    lines.append("#### Financial & Essence Breakdown:")
    lines.append(f"- **Base Limb Shell**: {calc['limb_shell_cost']:,}¥ ({calc['appearance']}, {calc['grade']} Grade)")
    if calc["adapsin_active"]:
        lines.append(f"- **Adapsin Discount**: Applied (10% post-grade reduction on cyberware)")
    if calc["bulk_mod_rating"] > 0:
        lines.append(f"- **Bulk Modification R{calc['bulk_mod_rating']}**: +{calc['bulk_mod_rating']} Cap ({calc['bulk_mod_cost']:,}¥)")
    lines.append(f"- **Enhancements Total**: {calc['enhancements_cost']:,}¥")
    if calc["accessories_cost"] > 0:
        lines.append(f"- **Installed Accessories**: {calc['accessories_cost']:,}¥")
    lines.append(f"- **Total Capital Required**: **{calc['total_cost']:,}¥**")
    lines.append("")

    lines.append("#### Attributes & Capacity Allocation:")
    attrs = calc["resulting_attributes"]
    lines.append(f"- **Limb Physical Attributes**: **Agility {attrs['agility']}**, **Strength {attrs['strength']}**")
    if attrs["defense_rating_bonus"] > 0:
        lines.append(f"- **Defense Rating Bonus**: +{attrs['defense_rating_bonus']}")
    lines.append(f"- **Capacity Utilization**: {calc['used_capacity']} used of {calc['total_capacity']} maximum ({calc['free_capacity']} slots open).")
    lines.append("")

    return "\n".join(lines)


def format_ware_calculation(calc: Dict[str, Any]) -> str:
    """Renders a clean markdown report of general ware calculation."""
    lines = [
        f"### Augmentation Calculation: {calc['name']} ({calc['grade']} {calc['type']})",
        f"> **Final Essence**: `{calc['final_essence']}` | **Final Cost**: `{calc['final_cost']:,}¥`",
        ""
    ]
    if calc.get("adapsin_warning"):
        lines.append(f"> [!NOTE]\n> {calc['adapsin_warning']}\n")
    elif calc.get("adapsin_applied"):
        lines.append("> [!TIP]\n> Adapsin therapy applied 10% post-grade Essence reduction.\n")

    lines.append(f"- Base Cost: {calc['base_cost']:,}¥ $\\rightarrow$ Final Cost: **{calc['final_cost']:,}¥**")
    lines.append(f"- Base Essence: {calc['base_essence']} $\\rightarrow$ Final Essence: **{calc['final_essence']}**")
    return "\n".join(lines)
