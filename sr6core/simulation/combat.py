"""
SR6 Opposed Combat Simulation & Resolution Engine.
Resolves Attack Rating vs Defense Rating Edge advantage, opposed attack vs defense tests,
net hits calculation, and damage resistance soak.
"""

from typing import Optional, Tuple
from pydantic import BaseModel, Field

from sr6core.simulation.dice import roll_pool, DiceRollResult


class CombatResult(BaseModel):
    """Structured result of an opposed combat attack."""
    attacker_name: str = "Attacker"
    defender_name: str = "Defender"
    weapon_name: str = "Weapon"
    base_dv: int = Field(ge=0, description="Base Damage Value")
    damage_type: str = Field(default="P", description="Physical (P) or Stun (S)")

    attacker_ar: int = Field(ge=0, default=0)
    defender_dr: int = Field(ge=0, default=0)
    attacker_edge_gained: int = Field(ge=0, default=0)
    defender_edge_gained: int = Field(ge=0, default=0)

    attack_roll: DiceRollResult
    defense_roll: DiceRollResult
    net_hits: int = Field(description="Attacker hits minus Defender hits")
    is_hit: bool = Field(description="True if net_hits > 0")

    modified_dv: int = Field(ge=0, default=0, description="base_dv + net_hits if hit else 0")
    soak_roll: Optional[DiceRollResult] = None
    damage_inflicted: int = Field(ge=0, default=0, description="Final damage boxes applied to condition monitor")

    def format_terminal(self) -> str:
        """Colorized terminal summary of the combat exchange."""
        if not self.is_hit:
            return (
                f"[bold cyan]{self.attacker_name}[/] attacked [bold yellow]{self.defender_name}[/] with {self.weapon_name} -> "
                f"[bold red]MISSED[/] (Attacker: {self.attack_roll.hits} hits vs Defense: {self.defense_roll.hits} hits)"
            )

        soak_str = f" | Soak: {self.soak_roll.hits} hits" if self.soak_roll else ""
        return (
            f"[bold cyan]{self.attacker_name}[/] [bold green]HIT[/] [bold yellow]{self.defender_name}[/] with {self.weapon_name}!\n"
            f"  • Attack: {self.attack_roll.hits} hits vs Defense: {self.defense_roll.hits} hits -> [bold green]{self.net_hits} Net Hits[/]\n"
            f"  • DV: {self.base_dv} + {self.net_hits} = [bold yellow]{self.modified_dv}{self.damage_type}[/]{soak_str}\n"
            f"  • Final Damage Taken: [bold red]{self.damage_inflicted} {self.damage_type} Damage Boxes[/]"
        )

    def format_markdown(self) -> str:
        """Renders Quarto callout markdown representation."""
        if not self.is_hit:
            return (
                f"::: {{.callout-warning icon=false title=\"Combat Test: Attack Missed\"}}\n"
                f"**{self.attacker_name}** fired **{self.weapon_name}** at **{self.defender_name}**.\n\n"
                f"- **Attack Test**: {self.attack_roll.format_markdown()}\n"
                f"- **Defense Test**: {self.defense_roll.format_markdown()}\n"
                f"- **Outcome**: *Attack Missed* (0 Net Hits).\n"
                f":::"
            )

        soak_line = f"- **Damage Resistance Soak**: {self.soak_roll.format_markdown()}\n" if self.soak_roll else ""
        return (
            f"::: {{.callout-important icon=false title=\"Combat Test: {self.damage_inflicted} {self.damage_type} Damage Inflicted\"}}\n"
            f"**{self.attacker_name}** scored a direct hit on **{self.defender_name}** with **{self.weapon_name}**!\n\n"
            f"- **Attack Test**: {self.attack_roll.format_markdown()}\n"
            f"- **Defense Test**: {self.defense_roll.format_markdown()}\n"
            f"- **Net Hits**: **+{self.net_hits}** (Modified DV: **{self.modified_dv}{self.damage_type}**)\n"
            f"{soak_line}"
            f"- **Final Damage**: **{self.damage_inflicted} {self.damage_type} Boxes** applied to Condition Monitor.\n"
            f":::"
        )


class CombatResolver:
    """Core Shadowrun 6E opposed test resolution engine."""

    @staticmethod
    def compare_ar_dr(attacker_ar: int, defender_dr: int) -> Tuple[int, int]:
        """
        Compares Attack Rating (AR) to Defense Rating (DR).
        If one exceeds the other by 4 or more, that participant gains 1 Edge.
        """
        diff = attacker_ar - defender_dr
        attacker_edge = 1 if diff >= 4 else 0
        defender_edge = 1 if diff <= -4 else 0
        return attacker_edge, defender_edge

    @classmethod
    def resolve_attack(
        cls,
        attacker_pool: int,
        defender_pool: int,
        base_dv: int,
        soak_pool: int = 0,
        damage_type: str = "P",
        attacker_name: str = "Attacker",
        defender_name: str = "Defender",
        weapon_name: str = "Weapon",
        attacker_ar: int = 0,
        defender_dr: int = 0,
        is_exploding: bool = False,
    ) -> CombatResult:
        """
        Executes a full SR6 opposed attack test.
        """
        att_edge, def_edge = cls.compare_ar_dr(attacker_ar, defender_dr)

        attack_roll = roll_pool(attacker_pool, description=f"{attacker_name} Attack", is_exploding=is_exploding)
        defense_roll = roll_pool(defender_pool, description=f"{defender_name} Defense", is_exploding=False)

        net_hits = attack_roll.hits - defense_roll.hits
        is_hit = net_hits > 0

        if not is_hit:
            return CombatResult(
                attacker_name=attacker_name,
                defender_name=defender_name,
                weapon_name=weapon_name,
                base_dv=base_dv,
                damage_type=damage_type,
                attacker_ar=attacker_ar,
                defender_dr=defender_dr,
                attacker_edge_gained=att_edge,
                defender_edge_gained=def_edge,
                attack_roll=attack_roll,
                defense_roll=defense_roll,
                net_hits=net_hits,
                is_hit=False,
                modified_dv=0,
                soak_roll=None,
                damage_inflicted=0,
            )

        modified_dv = base_dv + net_hits
        soak_roll = None
        damage_inflicted = modified_dv

        if soak_pool > 0:
            soak_roll = roll_pool(soak_pool, description=f"{defender_name} Soak", is_exploding=False)
            damage_inflicted = max(0, modified_dv - soak_roll.hits)

        return CombatResult(
            attacker_name=attacker_name,
            defender_name=defender_name,
            weapon_name=weapon_name,
            base_dv=base_dv,
            damage_type=damage_type,
            attacker_ar=attacker_ar,
            defender_dr=defender_dr,
            attacker_edge_gained=att_edge,
            defender_edge_gained=def_edge,
            attack_roll=attack_roll,
            defense_roll=defense_roll,
            net_hits=net_hits,
            is_hit=True,
            modified_dv=modified_dv,
            soak_roll=soak_roll,
            damage_inflicted=damage_inflicted,
        )
