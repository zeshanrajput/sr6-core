"""
SR6 Matrix & Magic Simulation Engine.
Resolves Spell Drain resistance tests, Technomancer Fading tests, and Matrix opposed tests.
"""

from typing import Optional
from pydantic import BaseModel, Field

from sr6core.simulation.dice import roll_pool, DiceRollResult


class DrainResult(BaseModel):
    """Structured result of a spell drain or fading test."""
    test_type: str = "Drain"  # "Drain" or "Fading"
    drain_value: int = Field(ge=0, description="Target drain/fading value")
    resistance_roll: DiceRollResult
    drain_taken: int = Field(ge=0, description="Unresisted drain/fading damage boxes")
    damage_type: str = Field(default="S", description="Stun (S) or Physical (P)")

    def format_terminal(self) -> str:
        if self.drain_taken == 0:
            return (
                f"[bold green]✓ Fully Resisted {self.test_type}![/] "
                f"(Resisted {self.resistance_roll.hits} hits vs DV {self.drain_value})"
            )
        return (
            f"[bold red]⚠ Suffered {self.drain_taken} {self.damage_type} {self.test_type} Damage![/] "
            f"(Target: {self.drain_value}, Resisted: {self.resistance_roll.hits} hits)"
        )


def resolve_drain_test(
    drain_value: int,
    resistance_pool: int,
    test_type: str = "Drain",
    damage_type: str = "S",
    is_exploding: bool = False,
) -> DrainResult:
    """
    Executes a Spell Drain or Technomancer Fading resistance roll.
    """
    roll = roll_pool(resistance_pool, description=f"{test_type} Resistance", is_exploding=is_exploding)
    drain_taken = max(0, drain_value - roll.hits)

    return DrainResult(
        test_type=test_type,
        drain_value=drain_value,
        resistance_roll=roll,
        drain_taken=drain_taken,
        damage_type=damage_type,
    )


def resolve_matrix_action(
    attacker_pool: int,
    defender_pool: int,
    action_name: str = "Brute Force",
    attacker_name: str = "Hacker",
    defender_name: str = "Host / Device",
) -> DiceRollResult:
    """
    Resolves an opposed Matrix action test.
    """
    att_roll = roll_pool(attacker_pool, description=f"{attacker_name} {action_name}")
    def_roll = roll_pool(defender_pool, description=f"{defender_name} Defense")

    net_hits = att_roll.hits - def_roll.hits
    att_roll.description = f"{action_name}: Net Hits {net_hits:+d} (Att: {att_roll.hits} vs Def: {def_roll.hits})"
    return att_roll
