"""
Priority & Sum-To-Ten Character Creation Auditor & Budget Subsystem for SR6.
"""

from typing import Dict, Any, List, Tuple

PRIORITY_POINTS = {"A": 4, "B": 3, "C": 2, "D": 1, "E": 0}
ATTRIBUTE_BUDGET = {"A": 24, "B": 16, "C": 12, "D": 8, "E": 2}
SKILL_BUDGET = {"A": 32, "B": 24, "C": 20, "D": 16, "E": 10}
RESOURCE_BUDGET = {"A": 450000, "B": 300000, "C": 150000, "D": 50000, "E": 8000}
METATYPE_ADJUSTMENT = {"A": 13, "B": 11, "C": 9, "D": 4, "E": 1}


def audit_priority_build(creation_budget: Dict[str, Any], is_sum_to_ten: bool = False) -> Tuple[bool, List[str]]:
    """
    Validates Priority Table row assignments (A-E) or Sum-to-Ten distribution.
    """
    warnings = []

    cats = {
        "Metatype": creation_budget.get("priority_metatype", "E").upper(),
        "Attributes": creation_budget.get("priority_attributes", "A").upper(),
        "Special": creation_budget.get("priority_special", "B").upper(),
        "Skills": creation_budget.get("priority_skills", "C").upper(),
        "Resources": creation_budget.get("priority_resources", "D").upper(),
    }

    # Check valid letters
    for k, v in cats.items():
        if v not in PRIORITY_POINTS:
            warnings.append(f"Invalid priority rank '{v}' for {k}. Must be A, B, C, D, or E.")

    if warnings:
        return False, warnings

    if is_sum_to_ten:
        total_pts = sum(PRIORITY_POINTS[v] for v in cats.values())
        if total_pts != 10:
            warnings.append(f"Sum-To-Ten total points sum to {total_pts}, but must equal exactly 10.")
    else:
        assigned = set(cats.values())
        if len(assigned) != 5:
            warnings.append("Standard Priority requires exactly one of each rank (A, B, C, D, E).")

    is_valid = len(warnings) == 0
    return is_valid, warnings


def calculate_priority_allocation(char_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Calculates points spent vs budget across Attributes, Skills, and Resources.
    """
    budget_spec = char_data.get("creation_budget", {})
    attr_rank = budget_spec.get("priority_attributes", "A").upper()
    skill_rank = budget_spec.get("priority_skills", "C").upper()
    res_rank = budget_spec.get("priority_resources", "D").upper()

    attr_budget = ATTRIBUTE_BUDGET.get(attr_rank, 16)
    skill_budget = SKILL_BUDGET.get(skill_rank, 20)
    res_budget = RESOURCE_BUDGET.get(res_rank, 50000)

    # Attributes spent: sum(attr - 1) for physical & mental
    attrs = char_data.get("attributes", {})
    phys_mental = ["body", "agility", "reaction", "strength", "willpower", "logic", "intuition", "charisma"]
    attr_spent = sum(max(0, int(attrs.get(k, 1)) - 1) for k in phys_mental)

    # Skills spent: sum of skill ratings
    skills = char_data.get("skills", [])
    skill_spent = sum(int(s.get("rating", 0)) for s in skills if isinstance(s, dict))

    return {
        "attributes": {
            "budget": attr_budget,
            "spent": attr_spent,
            "remaining": attr_budget - attr_spent,
            "valid": attr_spent <= attr_budget,
        },
        "skills": {
            "budget": skill_budget,
            "spent": skill_spent,
            "remaining": skill_budget - skill_spent,
            "valid": skill_spent <= skill_budget,
        },
        "resources": {
            "budget": res_budget,
        },
    }
