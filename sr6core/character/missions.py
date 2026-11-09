"""
Canonical SRM / CMP / SMH Missions Registry.
Delegates to sr6core.character.mission_registry for SQLite-backed mission metadata,
full-text search, and ebook linking while maintaining full backward compatibility.
"""

from typing import Dict, Any, Optional
from sr6core.character.mission_registry import (
    CANONICAL_MISSIONS,
    normalize_mission_code,
    get_mission_record,
    search_missions,
    ingest_all_missions,
)


def get_missions_registry() -> Dict[str, Dict[str, Any]]:
    """Returns canonical missions registry."""
    return CANONICAL_MISSIONS


def get_mission(code_or_title: str) -> Optional[Dict[str, Any]]:
    """Resolves mission by code (e.g. SRM.2081.01, 2081-01) or title."""
    return get_mission_record(code_or_title)
