"""
Tabletop Subsystem Cheatsheets & Rules Reference for SR6 Core.
Provides instant, authoritative mechanical rulecards for Matrix, Action Economy, Monads, and Combat.
"""

from typing import Dict, Any, List, Optional

CHEATSHEETS: Dict[str, Dict[str, str]] = {
    "matrix": {
        "title": "SR6 Matrix & Persona Mechanics",
        "description": "ASDF derivations, defense pools by action, Full Matrix Defense, and Fading formulas.",
        "content": r"""# Shadowrun 6e Matrix & Persona Cheatsheet

## 1. Living Persona & Mental Attribute Equivalencies (Monads & Technomancers)
Monads and Technomancers project a Living Persona directly from their neural architecture:
* **Attack (A)** = Charisma
* **Sleaze (S)** = Intuition
* **Data Processing (D)** = Logic
* **Firewall (F)** = Willpower
* **Device Rating** = Resonance (Technomancers) or Logic (Monads/DIs)

*(Note: Deckers use the ASDF array assigned by their cyberdeck, with Data Processing and Firewall boosted by an implanted Cyberjack).*

## 2. Matrix Defense Pools by Incoming Action
When an enemy hacker or IC attacks your persona or PAN, defend using:
* **Data Spite (Spike)**: Data Processing + Firewall
* **Brute Force**: Willpower + Firewall
* **Hack on the Fly / Probe**: Intuition + Firewall
* **Crash Program**: Logic + Firewall
* **Control Device / Spoof**: Logic + Firewall

## 3. Full Matrix Defense (Interrupt Action)
* **Mechanics**: You may trade 1 Major Action or 4 Minor Actions to declare Full Matrix Defense.
* **Effect**: Adds your **Firewall** attribute rating as a bonus to **ALL** Matrix Defense tests until your next turn.
* **Example**: If standard defense is Willpower (8) + Firewall (12) = 20d6, Full Matrix Defense boosts the pool to **32d6** (8 + 12 + 12).

## 4. Fading & Resonance Drain
* **Fading Test Pool**: Willpower + Logic (or Willpower + Resonance).
* **Damage Nature**:
  * If Fading value $\le$ Technomancer's Resonance rating: Fading damage is **Stun**.
  * If Fading value $>$ Resonance rating: Fading damage is **Physical**.
"""
    },
    "actions": {
        "title": "SR6 Action Economy & Combat Turns",
        "description": "Base allotments, Initiative Dice bonus minors, round-start caps, and action trading.",
        "content": r"""# Shadowrun 6e Action Economy & Turn Structure Cheatsheet

## 1. Combat Round Allotment
* **Base Action Allotment**: Every character receives **1 Major Action** and **1 Minor Action** per combat round.
* **Initiative Dice Bonus**: Gain **+1 additional Minor Action** for every Initiative Die you roll:
  * 1D6 Initiative: 1 Major, 2 Minors
  * 2D6 Initiative: 1 Major, 3 Minors
  * 3D6 Initiative: 1 Major, 4 Minors
  * 4D6 Initiative: 1 Major, 5 Minors (Turn-Start Maximum!)
  * 5D6 Initiative: 1 Major, 5 Minors (The 6th Minor is lost to the turn-start cap)

## 2. The Turn-Start Minor Action Cap
* A player **cannot begin their turn with more than 5 Minor Actions**.
* Any additional Minor Actions granted by initiative dice beyond 5 are lost.

## 3. Action Trading (During Your Turn)
Trading actions can only occur **after your turn has begun**:
* **4 Minor Actions $\\rightarrow$ 1 Major Action**: You may exchange 4 Minors to take a second Major Action (e.g. making two separate attacks or casting two spells).
* **1 Major Action $\\rightarrow$ 1 Minor Action**: You may exchange a Major Action for an additional Minor Action (e.g. to move extra distance or reload).
* *Rule Note*: You cannot pre-convert 4 Minors into a Major before the round starts to bypass the 5 Minor cap.

## 4. Common Action Classifications
* **Major Actions**:
  * Attack (Firearms, Melee, Astral, Matrix)
  * Cast Spell / Thread Complex Form
  * Full Defense (Standard Meatspace)
  * Sprint (+15m Movement)
  * First Aid / Stabilize
* **Minor Actions**:
  * Move (Up to Movement Speed, typically 10m)
  * Take Aim (+1 die or +1 AR)
  * Quick Draw (Ready weapon with Athletics test)
  * Drop Prone / Stand Up
  * Shift DNI / Matrix Mode
  * Reload Weapon (Clips/Magazines)
"""
    },
    "monad": {
        "title": "SR6 Monad Abilities & Nanite Mechanics",
        "description": "Nanite Volume, Nanohive capacities, Overdrive, Resculpt, and Cellular Healing.",
        "content": r"""# Shadowrun 6e Monad & Nanite Mechanics Cheatsheet

## 1. Nanite Volume (NV) & Storage
* **Base NV Formula**: Derived from mental attributes: $\text{NV} = \text{Logic} + \text{Intuition}$.
* **Hardware Storage (Nanohives)**:
  * A biological host must store nanites in implanted **Nanohives** (installed in torso or limbs).
  * **Capacity Limit**: Combined Nanohive Rating $\times 3$ = Maximum physical NV capacity.
  * **Wireless Bonus**: Operating online increases capacity to Rating $\times 4$ and replenishes 1 NV per rating every hour.

## 2. Core Monad Abilities (Collapsing Now, pp. 154–161)
* **Attribute Overdrive (Minor Action)**:
  * Roll NV test (dice = current NV).
  * Each hit grants **+1 to a physical attribute** (Agility, Body, Reaction, Strength) for NV combat turns (max $+2$ or $+4$ augmented limit).
* **Resculpt**:
  * Monads can autonomously reshape cosmetic features, fingerprints, retinal patterns, dermal plating textures, and cyberlimb housings over downtime.
  * Allows alteration of physical appearance and concealment of augmentations without surgical downtime.
* **Rapid Cellular Healing (Minor or Major Action)**:
  * Roll NV test.
  * **Minor Action**: Clear Condition Monitor damage boxes equal to hits.
  * **Major Action**: Clear double hits in damage boxes and gain **+1 situational Edge**.
* **Adrenal Control (Minor Action)**:
  * Roll Willpower + NV to remain conscious and active even when Physical or Stun condition monitors are completely filled.
"""
    },
    "combat": {
        "title": "SR6 Combat Exchange & Edge Thresholds",
        "description": "AR vs DR 4-point differential, Edge generation ceiling, and damage resolution.",
        "content": r"""# Shadowrun 6e Tactical Combat Cheatsheet

## 1. The 4-Point Rule (Attack Rating vs Defense Rating)
Edge is generated dynamically by comparing the attacker's Attack Rating (AR) against the defender's Defense Rating (DR):
* If $\mathbf{AR \ge DR + 4}$: Attacker gains **1 Edge**.
* If $\mathbf{DR \ge AR + 4}$: Defender gains **1 Edge**.
* If the difference is $< 4$: **Neither party gains Edge** from the rating comparison.
* **Edge Round Ceiling**: A character can earn a **maximum of 2 Edge per combat round** from all sources combined (AR/DR comparison, qualities, maneuvers, and gear).

## 2. Opposed Test Resolution
1. **Attack Roll**:
   * Firearms: `Firearms + Agility`
   * Melee: `Close Combat + Agility`
2. **Defense Roll**:
   * `Reaction + Intuition`
   * Net Hits = Attacker Hits - Defender Hits. If Net Hits $\\le 0$, the attack misses completely.

## 3. Damage Resistance (Soak)
* **Modified Damage Value (DV)**: Base Weapon DV + Net Hits.
* **Soak Pool**: Roll `Body + Innate Armor/Bone Density`.
* **Final Damage Applied**: $\\text{Final DV} = \\text{Modified DV} - \\text{Soak Hits}$.
* Each point of remaining damage fills one box on the defender's Condition Monitor.

## 4. Common Tactical Status Effects
* **Blinded**: Cannot see; -4 dice pool penalty to physical tests; AR and DR set to 0.
* **Dazed**: Shocked or disoriented; loses all Minor Actions; can only take 1 Major Action on their turn.
* **Hobbled**: Movement speed halved; -2 penalty to Athletics tests.
* **Prone**: Lying flat; +2 DR against ranged attacks; -2 to melee defense; requires 1 Minor Action to stand.
"""
    }
}


def get_cheatsheet(topic: str) -> Optional[Dict[str, str]]:
    """Retrieves a cheatsheet by topic key."""
    clean = topic.strip().lower()
    return CHEATSHEETS.get(clean)


def list_cheatsheets() -> List[Dict[str, str]]:
    """Returns a list of all available cheatsheets with descriptions."""
    return [
        {"topic": k, "title": v["title"], "description": v["description"]}
        for k, v in CHEATSHEETS.items()
    ]


def format_cheatsheets_index() -> str:
    """Formats an index of available cheat sheets."""
    lines = ["### Available Shadowrun 6e Subsystem Cheatsheets:\n"]
    lines.append("| Topic | Subsystem Title | Description |")
    lines.append("| :--- | :--- | :--- |")
    for k, v in CHEATSHEETS.items():
        lines.append(f"| **`{k}`** | {v['title']} | {v['description']} |")
    lines.append("\n*Run `uv run sr6 cheat <topic>` to display any cheatsheet.*")
    return "\n".join(lines)
