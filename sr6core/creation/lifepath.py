"""
Life Path Module Compiler & Auditor for SR6 (Sixth World Companion).
"""

from typing import Dict, Any, List, Tuple

LIFEPATH_STAGES = ["Birth", "Youth", "Formative Years", "Higher Education / Real World", "Career"]


def audit_lifepath_build(creation_budget: Dict[str, Any]) -> Tuple[bool, List[str]]:
    warnings = []
    stages = creation_budget.get("lifepath_stages", [])
    
    if len(stages) < 5:
        warnings.append(f"Life Path build incomplete: {len(stages)} of 5 required stages configured.")
        
    for stage_idx, stage in enumerate(stages):
        if not stage.get("name"):
            warnings.append(f"Stage {stage_idx + 1} is missing a module name.")
            
    is_valid = len(warnings) == 0
    return is_valid, warnings
