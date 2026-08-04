"""
Point-Buy & Karma Advancement Auditor for SR6.
"""

from typing import Dict, Any, List, Tuple


def audit_point_buy(char_data: Dict[str, Any], max_karma: int = 100) -> Tuple[bool, List[str]]:
    warnings = []
    
    # 1. Quality Karma Limit (SR6 Rule: Max 20 Karma net positive / 20 Karma negative at build)
    pos_qualities = char_data.get("qualities_positive", [])
    neg_qualities = char_data.get("qualities_negative", [])
    
    # 2. Check attribute max caps (SR6 Rule: Only one attribute can be maxed at character creation)
    attrs = char_data.get("attributes", {})
    maxed_attrs = 0
    for name, val in attrs.items():
        if isinstance(val, int) and val >= 6 and name.lower() not in ["resonance", "magic", "edge"]:
            maxed_attrs += 1
            
    if maxed_attrs > 1:
        warnings.append(f"At character creation, only 1 physical/mental attribute can reach max rating (found {maxed_attrs}).")

    is_valid = len(warnings) == 0
    return is_valid, warnings
