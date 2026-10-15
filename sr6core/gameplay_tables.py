"""
Shim for backward compatibility with sr6core.gameplay_tables.
Re-exports from sr6core.rules.tables.
"""

from sr6core.rules.tables import (
    ACTIONS_DATA,
    STATUS_EFFECTS_DATA,
    EDGE_BOOSTS_DATA,
    init_gameplay_tables,
    populate_gameplay_tables,
)

__all__ = [
    "ACTIONS_DATA",
    "STATUS_EFFECTS_DATA",
    "EDGE_BOOSTS_DATA",
    "init_gameplay_tables",
    "populate_gameplay_tables",
]
