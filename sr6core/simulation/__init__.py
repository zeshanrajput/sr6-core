"""
SR6 Simulation Engine: Authoritative Tabletop Dice & Combat Resolution.
"""

from sr6core.simulation.dice import roll_pool, DiceRollResult
from sr6core.simulation.combat import CombatResolver, CombatResult
from sr6core.simulation.matrix_magic import resolve_drain_test, resolve_matrix_action, DrainResult

__all__ = [
    "roll_pool",
    "DiceRollResult",
    "CombatResolver",
    "CombatResult",
    "resolve_drain_test",
    "resolve_matrix_action",
    "DrainResult",
]
