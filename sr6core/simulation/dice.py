"""
SR6 Dice Pool Resolution Engine.
Handles standard d6 pools, Rule of Six exploding dice, bought hits,
Glitch / Critical Glitch boundary detection, and Edge maneuvers.
"""

import random
from typing import List, Optional, Tuple
from pydantic import BaseModel, Field


class DiceRollResult(BaseModel):
    """Structured result of an SR6 dice pool roll."""
    pool: int = Field(ge=0, description="Base dice pool size before roll")
    dice: List[int] = Field(default_factory=list, description="Array of rolled die values")
    hits: int = Field(default=0, ge=0, description="Total hits rolled (5s and 6s)")
    ones: int = Field(default=0, ge=0, description="Total ones rolled")
    is_glitch: bool = Field(default=False, description="True if ones > pool / 2")
    is_critical_glitch: bool = Field(default=False, description="True if is_glitch and hits == 0")
    is_exploding: bool = Field(default=False, description="True if Rule of Six was active")
    bought_hits: Optional[int] = Field(default=None, description="Hits if bought without rolling (pool // 4)")
    edge_spent: int = Field(default=0, ge=0, description="Edge points spent on this roll")
    description: str = Field(default="Dice Test", description="Name or label of the test")

    def format_terminal(self) -> str:
        """Renders colorized terminal summary."""
        dice_str = ", ".join(
            f"[bold green]{d}[/]" if d in (5, 6) else (f"[bold red]{d}[/]" if d == 1 else str(d))
            for d in self.dice
        )
        status = ""
        if self.is_critical_glitch:
            status = " [bold red]🚨 CRITICAL GLITCH![/]"
        elif self.is_glitch:
            status = " [bold yellow]⚠️ GLITCH![/]"
        elif self.hits >= 4:
            status = " [bold green]✨ SPECTACULAR SUCCESS[/]"

        return f"[bold cyan]{self.description}[/] ({self.pool}d6): [{dice_str}] -> [bold white]{self.hits} Hits[/]{status}"

    def format_markdown(self) -> str:
        """Renders Markdown callout representation."""
        dice_str = " ".join(f"**[{d}]**" if d >= 5 else (f"*({d})*" if d == 1 else str(d)) for d in self.dice)
        status = ""
        if self.is_critical_glitch:
            status = " 🚨 **CRITICAL GLITCH!**"
        elif self.is_glitch:
            status = " ⚠️ **GLITCH!**"

        return f"**{self.description}** ({self.pool}d6): `{dice_str}` → **{self.hits} Hits**{status}"


def roll_pool(
    pool: int,
    description: str = "Action Test",
    is_exploding: bool = False,
    buy_hits: bool = False,
    rng: Optional[random.Random] = None,
) -> DiceRollResult:
    """
    Rolls a pool of Shadowrun 6th Edition d6 dice.
    """
    if pool <= 0:
        return DiceRollResult(
            pool=0,
            dice=[],
            hits=0,
            ones=0,
            is_glitch=False,
            is_critical_glitch=False,
            is_exploding=is_exploding,
            bought_hits=0 if buy_hits else None,
            description=description,
        )

    if buy_hits:
        hits = pool // 4
        return DiceRollResult(
            pool=pool,
            dice=[],
            hits=hits,
            ones=0,
            is_glitch=False,
            is_critical_glitch=False,
            is_exploding=False,
            bought_hits=hits,
            description=f"{description} (Bought Hits)",
        )

    r = rng or random.Random()
    dice: List[int] = []
    hits = 0
    ones = 0

    def _roll_d6() -> int:
        return r.randint(1, 6)

    for _ in range(pool):
        val = _roll_d6()
        dice.append(val)
        if val >= 5:
            hits += 1
        elif val == 1:
            ones += 1

        if is_exploding and val == 6:
            explode_val = _roll_d6()
            while explode_val == 6:
                dice.append(explode_val)
                hits += 1
                explode_val = _roll_d6()
            dice.append(explode_val)
            if explode_val >= 5:
                hits += 1
            elif explode_val == 1:
                ones += 1

    is_glitch = ones > (pool / 2)
    is_critical_glitch = is_glitch and (hits == 0)

    return DiceRollResult(
        pool=pool,
        dice=dice,
        hits=hits,
        ones=ones,
        is_glitch=is_glitch,
        is_critical_glitch=is_critical_glitch,
        is_exploding=is_exploding,
        description=description,
    )


def apply_edge_reroll_failures(result: DiceRollResult, rng: Optional[random.Random] = None) -> DiceRollResult:
    """
    Applies 1 Edge maneuver: Rerolls all dice that did not score a hit (< 5).
    """
    r = rng or random.Random()
    kept_dice = [d for d in result.dice if d >= 5]
    failed_count = len(result.dice) - len(kept_dice)

    new_dice = list(kept_dice)
    new_hits = len(kept_dice)
    new_ones = 0

    for _ in range(failed_count):
        val = r.randint(1, 6)
        new_dice.append(val)
        if val >= 5:
            new_hits += 1
        elif val == 1:
            new_ones += 1

    is_glitch = new_ones > (result.pool / 2)
    is_critical_glitch = is_glitch and (new_hits == 0)

    return DiceRollResult(
        pool=result.pool,
        dice=new_dice,
        hits=new_hits,
        ones=new_ones,
        is_glitch=is_glitch,
        is_critical_glitch=is_critical_glitch,
        is_exploding=result.is_exploding,
        edge_spent=result.edge_spent + 1,
        description=f"{result.description} (Edge Rerolled)",
    )
