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
    },
    "metamagic": {
        "title": "SR6 Initiations & Metamagics Mechanics",
        "description": "Karma formulas, Drain resistance, Centering, and complete metamagic directory across CRB, Street Wyrd, Deadly Arts, and Smooth Operations.",
        "content": r"""# Shadowrun 6e Initiations & Metamagics Cheatsheet

## 1. Initiation Costs & Progression
* **Initiation Karma Formula**: $\text{Cost} = 10 + \text{Target Grade} - \text{Group/Coven Loyalty}$.
  * *Example*: Initiating from Grade 2 to Grade 3 with Coven Loyalty 8: $10 + 3 - 8 = \mathbf{5\text{ Karma}}$ (or 4 Karma with specific mission backing).
* **Maximum Group Discount**: Coven Loyalty cannot reduce cost below $(10 + \text{Target Grade}) / 2$ unless specified by special campaign waivers.
* **Initiation Grade Benefits**:
  * Raises Maximum Magic attribute by +1 per Grade.
  * Adds Initiate Grade to Counterspelling, Assensing masks, and metamagic dice pools.
  * Mystic Adepts can choose either a Metamagic OR 1.0 Adept Power Point (*Power Point* metamagic).

## 2. Drain Resistance & Centering (CRB p. 167)
* **Standard Drain Pool**: Willpower + Tradition Attribute (e.g., Charisma for Shinto/Shamanic; Logic for Hermetic).
* **Centering (Minor Action)**: Tradition-appropriate mundane action (chanting, mudras, instruments) adds **+Initiate Grade dice** to **ALL Drain Resistance tests**.
  * *At Grade 3*: +3 Drain dice.
  * *At Grade 4*: +4 Drain dice.
* **Adept Centering (Minor Action, CRB p. 167)**: Negates opponent Edge gains from environmental conditions (smoke, darkness, glare) or illusion spells.

## 3. Core Rulebook Metamagics (CRB pp. 167–168)
* **Masking**: Opposed test against Assensing using `Magic + Initiate Grade`. Disguises aura as mundane, alters apparent Magic rank by $\pm\text{Grade}$, and **masks up to Grade bonded foci**.
* **Power Point**: Adepts and Mystic Adepts only. Gain **1.0 Adept Power Point**. Can be selected multiple times.
* **Shielding**: Adds Initiate Grade dice directly to the **Spell Defense (Boosted Defense)** pool when defending against incoming hostile spells.
* **Spell Shaping**: Reshape area spells by taking -1 die per meter of radius added/subtracted or to create a 1-meter safe bubble. Incurs 0 drain surcharge.
* **Flexible Signature**: Alters or disguises your astral signature; reduces time signature lingers by Initiate Grade hours.
* **Fixation**: Enables permanent anchoring of alchemical preparations.
* **Quickening**: Spends Karma to sustain spells permanently. *(SRM Note: Quickened spells generate Heat and are permanently stripped by mana barriers).*

## 4. Street Wyrd Metamagics (Street Wyrd pp. 112–119)
* **Channeling (SW p. 113)**: Inhabits a summoned spirit in physical body. Physical attributes boosted by $\lfloor\text{Force}/2\rfloor$. Uses spirit powers via services (expends 0 spell drain). Spirit can assume full control for 1 combat turn to use its own mental skills.
* **Psychometry (SW p. 112)**: Active test (`Astral + Intuition + Grade` vs time-elapsed threshold). Imposes -4 penalty to other actions; duration 1d6 minutes. Reads emotional impressions, owner history, and trauma from touched objects.
* **Divination (SW p. 119)**:
  * *Passive*: Grants **+1 situational Edge before making Surprise tests**!
  * *Active*: Examines subject astrally $\rightarrow$ rolls `Astral + Magic + Grade` against $(10 - \text{minutes})$ threshold to view visions of future events. Resists drain equal to hits.
* **Extended Masking (SW p. 112)**: *Req: Masking*. Masks sustained spells, quickened spells, and complex forms under your disguise.
* **Invocation (SW p. 113)**: Summons Great Form spirits with high-impact Great Form powers.
* **Great Form Channeling (SW p. 113)**: *Req: Invocation + Channeling*. Houses Great Form spirits within physical form.
* **Absorption (SW p. 114)**: *Req: Shielding*. Successfully defended spell hits can be converted to negate drain or regain Edge.
* **Reflection (SW p. 114)**: *Req: Shielding*. Reflects hostile spells directly back at the attacking caster.
* **Severing (SW p. 114)**: *Req: Shielding*. Disrupts and severs sustained enemy spells and links.
* **Cleansing (SW p. 112)**: Purges astral pollution and background counts.
* **Paradigm Shift (SW p. 112)**: Permanently switches tradition drain attributes and spirit alignment.
* **Finding Your Way (SW p. 76)**: Adopts an Adept Way (e.g. *The Magician's Way*) through initiation without paying 40 Karma.

## 5. Deadly Arts Metamagics (Deadly Arts pp. 172–173; SRMG p. 75)
* **Stealth Effect (DA p. 173)**: Minor Action, +2 Drain Value. Camouflages physical spell manifestation (invisible on material plane until contact). Adds **+Initiate Grade** to the Perception threshold to notice casting.
* **Spell Blade (DA p. 172)**: Channels active combat spells directly through melee weapons on physical strikes.
* **Spell Grenade (DA p. 172)**: Pre-casts area combat spells into thrown projectiles for delayed detonation.

## 6. Smooth Operations Metamagics (Smooth Operations p. 105; SRM Legal)
* **Empathy (SO p. 105)**: Grants **+1 Edge on ALL Social tests**, and increases **Social Rating by Magic rating** (+6 Social Rating for Magic 6).
* **Charlatan (SO p. 105)**: Adds Con rank to Magic to determine Perception threshold to notice casting (e.g., $6 + 5 = \mathbf{11}$). Imposes a dice pool penalty equal to Con rank (-5 dice) to all enemy assensing tests against the performer, their spells, or their foci. Zero drain increase!
* **Astral Bluff (SO p. 105)**: Minor Action, Con + Magic (3) test to temporarily disguise emotional/health aura for net hit minutes; grants +1 Edge on accompanying Con tests.
* **Astral Scrutiny (SO p. 105)**: *Req: Astral 4 + Spec in Signatures*. Every 2 net hits on Assensing reveal positive/negative qualities, attributes, grades, or Edge.
* **Astral Camouflage (SO p. 105)**: *Req: Astral 5*. Denies opponents Edge when assensing/targeting aura; grants +1 Edge when avoiding astral detection or bypassing barriers.
"""
    }
}

CHEATSHEET_ALIASES: Dict[str, str] = {
    "metamagics": "metamagic",
    "magic": "metamagic",
    "initiation": "metamagic",
    "initiations": "metamagic",
}


def get_cheatsheet(topic: str) -> Optional[Dict[str, str]]:
    """Retrieves a cheatsheet by topic key."""
    clean = topic.strip().lower()
    canonical = CHEATSHEET_ALIASES.get(clean, clean)
    return CHEATSHEETS.get(canonical)


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
