"""
Priority & Sum-To-Ten Character Creation Auditor for SR6.
"""

from typing import Dict, Any, List, Tuple

PRIORITY_POINTS = {"A": 4, "B": 3, "C": 2, "D": 1, "E": 0}
ATTRIBUTE_BUDGET = {"A": 24, "B": 16, "C": 12, "D": 8, "E": 2}
SKILL_BUDGET = {"A": 32, "B": 24, "C": 20, "D": 16, "E": 10}
RESOURCE_BUDGET = {"A": 450000, "B": 300000, "C": 150000, "D": 50000, "E": 8000}


def audit_priority_build(creation_budget: Dict[str, Any], is_sum_to_ten: bool = False) -> Tuple[bool, List[str]]:
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
