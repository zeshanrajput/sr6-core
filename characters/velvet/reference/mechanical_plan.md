# Character Advancement & Mechanical Plan: Velvet

This document has one operational role: **directing the exact sequence of Karma and Nuyen expenditures, downtime activity allocations, and architectural upgrades during character log updates.**

* **Active State & Historical Records:** Current attributes, known spells, metamagics, acquired gear, bonded foci, and ledger balances are maintained in the Markdown Trio ([`character_log.qmd`](file:///c:/GitHub/sr6-core/characters/velvet/core/character_log.qmd), [`character_purchases.qmd`](file:///c:/GitHub/sr6-core/characters/velvet/core/character_purchases.qmd), [`character_build.qmd`](file:///c:/GitHub/sr6-core/characters/velvet/core/character_build.qmd)) and compiled into `velvet_master.yaml`. Full tabletop mechanics, spirit binding math, and stacking legality rules are codified in [`rules_and_downtime.qmd`](file:///c:/GitHub/sr6-core/characters/velvet/rules/rules_and_downtime.qmd).

---

## 1. Downtime Action Economy & Allocation Protocol

Under *SRM Guide v2.4* (pp. 17–20, 47, 59–60), downtime actions between missions are strictly budgeted:

* **Mainline SRM Missions:** Grant **1 Major + 1 Minor** Action (or **3 Minor Actions** if taking no Major).
* **Convention Mission Packs (CMPs):** Grant **2 Minor Actions only** (no Major Action; Initiation cannot be performed post-CMP).
* **The Coven Decay Protocol (Guild of Freelance Assets):**
  * Currently at **Loyalty 6** (decaying $6 \rightarrow 5 \rightarrow 4$ over upcoming months without maintenance).
  * **The Loyalty 4 Floor:** Once stabilized at Loyalty 4, maintenance costs only **1 Minor Downtime Action per month** and dues drop to **¥350/mo** ($50 \times \text{Connection 7}$). This permanently preserves a **-4 Karma initiation discount** while leaving every single SRM Major Downtime Action unencumbered.
* **Strict Priority Hierarchy (Execute in order upon run completion):**
  1. **Initiation (Major Action):** Consumes the Major Action on mainline SRMs when Karma threshold is reached. Initiate Grade is hard-capped by current Magic rating (**Grade 6 cap at Magic 6**).
  2. **Work for the People (Minor Action):** Non-negotiable conversion of **¥2,000 $\rightarrow$ +1 Karma** (funded directly by the ¥3,000 Hooder R3 monthly obligation).
  3. **Learn Spells (Minor Action):** Absorb queued spells (**5 Karma + 1 Minor Action study** each).
     * *Direct Combat & Teamwork Core:* **`Stunball`** (*CRB*, p. 134) $\rightarrow$ **`Wingman`** (*Smooth Operations*, p. 110) $\rightarrow$ **`Wreck (Drones)`** (*Street Wyrd*, p. 27) $\rightarrow$ **`Manaball`** (*CRB*, p. 133).
     * *Secondary Tactical Sabotage:* **`Sterilize`** (*Street Wyrd*, p. 56).
     * *Deferred Flavor & Cosmetic Utility Backlog:* **`Charm`** (*CRB*, p. 138) and **`Fashion`** (*Street Wyrd*, p. 48) (deprioritized due to natural 19–24d social pools and *Cosmetic Control 2*).
  4. **Spirit Binding & Re-Binding (Minor Action):** Bind Fire or Air spirits up to the Magic $\times$ 3 Force cap (18 Force at Magic 6).

---

## 2. Master Unified Progression Queue

All upcoming upgrades are prioritized sequentially below. When logging post-mission downtime, advance the next available item in this table according to banked Karma, liquid Nuyen, and available action slots.

### A. Karma Progression Pipeline (Ontological & Metamagic Scaling)

*(Current Baseline: Initiation Grade 5, Magic 6, 4 Karma banked after Session 9).*

| Step | Target Upgrade | Category | Cost | Downtime Action Required | Primary Tactical & Architectural Role |
| :---: | :--- | :--- | :---: | :---: | :--- |
| **01** | **Initiation Grade 6**<br>• *The Magician's Way* | Metamagic | 9 Karma* | 1 Major Action<br>*(Mainline SRM)* | *Street Wyrd* 76: Apex capstone at Magic 6. Unlocks dual mentor spirit benefits for *Wise Warrior* (Adept combat sorcery bonus + **-1 Edge cost discount on Combat category spells/rituals**). Allows Adept drain to be resisted with **Body + Charisma (14+ dice)**. |
| **02** | **Spell: Stunball** | Direct Combat (Area) | 5 Karma | 1 Minor Action (Study) | *CRB* 134: LOS(A), DV 4, Stun. Non-lethal AoE that **completely bypasses armor** ($\text{Sorcery} + \text{Magic}$ vs $\text{Willpower} + \text{Intuition}$). Cast silently via *Stealth Effect* (Grade 5). Immediately activates *Wise Warrior*’s -1 Edge discount on Combat spells. |
| **03** | **Spell: Wingman** | Detection Spell | 5 Karma | 1 Minor Action (Study) | *Smooth Operations* 110: Specialized sustained Mindlink for social teamwork. Helper gets 1 temporary Edge on assistance; leader gains 1 temporary Edge for *each* die provided (19–24d). Solves the "two faces at the table" dilemma by turning Velvet into an unbeatable cooperative Edge battery. Sustained via *Focused Concentration*. |
| **04** | **Spell: Wreck (Drones)** | Direct Combat (LOS) | 5 Karma | 1 Minor Action (Study) | *Street Wyrd* 27: LOS, DV 4, Object destruction. Directly bypasses drone armor to destroy chassis/optics. Classified as a **Direct Combat** spell, so it reaps the *Wise Warrior* -1 Edge boost discount. |
| **05** | **Spell: Manaball** | Direct Combat (Area) | 5 Karma | 1 Minor Action (Study) | *CRB* 133: LOS(A), DV 5, Physical. Silent, lethal direct mana destruction that **completely bypasses armor**. Deployed against hardened combat teams, cybered hit squads, or hostile spirits when stun is insufficient. Reaps *Wise Warrior* -1 Edge discount. |
| **06** | **Quality: Finesse** | Negative Quality | 0 Karma | None (SRMG Adoption) | *6WC* 137 / *SRMG* 37, 58, 137: Formalizes Velvet's ethos of surgical non-violence, zero collateral damage, and avoidance of unnecessary Heat. Free to adopt post-chargen (no bonus Karma granted). |
| **07** | **Untrained Skill Repair**<br>• *Perception 1 (Intuition)*<br>• *Astral 1 (Intuition)* | Active Skills | 10 Karma tot<br>*(5K each)* | None (Between runs) | Removes -1 untrained penalty (+2 dice swing each; Perception 3d $\rightarrow$ 5d, Astral 3d $\rightarrow$ 5d). Essential for spotting physical ambushes and reading emotional auras. |
| **08** | **Tactical Sabotage: Sterilize** | Manipulation (Area) | 5 Karma | 1 Minor Action (Study) | *Street Wyrd* 56: Complete forensic DNA, biometric, and physical evidence cleansing. Eliminates material crime scene traces. |
| **09** | **Attribute: Magic 6 $\rightarrow$ 7** | Attribute | 35 Karma | None (Between runs) | Unlocks Initiate Grades 7+, expands Focus Bonding Cap from 18 $\rightarrow$ **21 Force**, and raises safe spirit summoning threshold to Force 6. |
| **10** | **Initiation Grade 7**<br>• *Flexible Signature* | Metamagic | 12 Karma* | 1 Major Action<br>*(Mainline SRM)* | *CRB* 165: Enables altering or completely erasing astral signatures from spellcasting, rendering Velvet astrally untraceable. |
| **11** | **Attribute: Magic 7 $\rightarrow$ 8** | Attribute | 40 Karma | None (Between runs) | Expands Focus Bonding Cap to **24 Force**, allowing dual Rating 6 Qi Foci to bond simultaneously with Power Focus R3 and Sustaining Focus R3. |
| **12** | **Initiation Grade 8**<br>• *Adept Centering* | Metamagic | 13 Karma* | 1 Major Action<br>*(Mainline SRM)* | *CRB* 167: Adds Initiate Grade to physical and combat actions via centering gestures, insulating active tests against situational modifiers. |
| **13** | **Quality: Teamwork Makes Dream Work** | Positive Quality | 12 Karma<br>*(2x 6K)* | None (Between runs) | *Hack & Slash* 83: Extends social teamwork bonuses to all party members, multiplying Edge generation when paired with *Wingman*. |
| **14** | **Quality: Charismatic Defense** | Positive Quality | 24 Karma<br>*(2x 12K)* | None (Between runs) | *Power Plays* 85: Bases Defense Rating off Charisma instead of Body (DR jumps from 2 $\rightarrow$ **10–14**!). |

*\*Initiation cost formula at Loyalty 6: $10 + 5 - 6 = 9$ Karma; at Loyalty 4 floor: $10 + \text{Current Grade} - 4$.*

#### Deferred Backlog ("Nice-to-Have Flavor & Cosmetic Utility")
* **Spell: Charm** (*CRB*, p. 138; 5 Karma) — Manipulation spell granting +4 dice to social tests. Deprioritized because Velvet already operates with natural 19–24d social pools (buying 4–5 hits routinely); +4 extra dice is win-more overkill.
* **Spell: Fashion** (*Street Wyrd*, p. 48; 5 Karma) — Instant clothing transformation. Deprioritized because *Cosmetic Control 2* already handles biological shape/gender/height alteration, while physical nanopaste disguise kits and high-fashion modular wardrobes cover cosmetic apparel.

---

### B. Nuyen & Foci Progression Pipeline

*(Current Baseline: Power Focus Rating 3 bonded, ¥22,915 liquid nuyen after Session 9).*

| Step | Target Hardware / Focus Upgrade | Source / Book | Cost | Downtime Action Required | Capacity & Tactical Role |
| :---: | :--- | :--- | :--- | :---: | :--- |
| **H1** | **M-TOC Tactical Network Node** | *Firing Squad* 110 | ¥15,000–¥30,000 | None (Market Purchase) | Team Edge storage bank and encrypted squad tactical coordination network. |
| **H2** | **Qi Focus: Improved Sorcery (R3)** | *CRB* 155, 294 | ¥36,000 + 24 Karma | Minor Action (Bond Focus) | Rating 6 Qi Focus (Force 6 = $4 \times 1.5$ PP). Flat **+3 dice to all Spellcasting tests** (pushes Sorcery to **21+ dice**). Requires Magic 7 (21 Force cap). |
| **H3** | **Qi Focus: Improved Conjuring (R3)** | *CRB* 155, 294 | ¥36,000 + 24 Karma | Minor Action (Bond Focus) | Rating 6 Qi Focus (Force 6). Flat **+3 dice to Conjuring** (pushes pool to **20 dice = 5 bought hits vs Force 8 spirits**). Requires Magic 8 (24 Force cap). |
| **H4** | **Sustaining Focus: Health (R3)** | *CRB* 155, 294 | ¥27,000 + 6 Karma | Minor Action (Bond Focus) | Rating 3 Focus (Force 3). Sustains *Increase Attribute (Charisma)* or *Increase Reflexes* independently, freeing a Focused Concentration slot for *Wingman*. |

---

## 3. Forward Architectural Blueprints

### A. The Covert Social Infiltration & Wingman Cooperative Engine

```text
                               THE GHOST FACE OPERATIONAL ARRAY
                  [Covert Mana Manifestation + Social Edge Generation]

      STEALTH EFFECT (Grade 5)                    WINGMAN (Detection Spell)
    (Deadly Arts 173 / SRMG 75)                  (Smooth Operations 110)
  +--------------------------------+          +--------------------------------+
  |  Zero physical light/sound     |          |  Sustained specialized Mindlink|
  |  +5 to Perception threshold to |          |  Helper gains 1 temporary Edge |
  |   detect spellcasting in room  |          |  Leader gains 1 Edge per die   |
  +--------------------------------+          +--------------------------------+
                  |                                           |
                  +---------------------+---------------------+
                                        v
                        COSMETIC CONTROL 2 + COMMAND PRESENCE
                     (Street Wyrd 78 / Deadly Arts 28 — 3.0 PP)
  +----------------------------------------------------------------------------+
  |  • Instant Metatype Swapping: Pass as human, elf, ork, dwarf, or troll.   |
  |  • Command Presence: +2 dice & +1 Edge on Influence (Leadership) tests.   |
  |  • Edge Boost Discount: -1 Edge cost on Con (Disguise/Acting/Impersonate). |
  |  • Result: Velvet generates 2–3 team Edge every social exchange.          |
  +----------------------------------------------------------------------------+
```

* **Solving the "Two Faces at the Table" Problem:** Usually, having two social specialists at the table creates role friction and dilutes spotlight. *Wingman* completely inverts this: Velvet steps into the helper/co-pilot role, giving the lead Face an avalanche of temporary Edge (1 Edge per die contributed from Velvet’s 19–24d pool) while Velvet pockets a free Edge. The lead negotiator enters every high-stakes corporate sit-down saturated with maximum Edge.
* **Covert Social Support:** *Stealth Effect* allows Velvet to establish *Wingman* or cast covert assistance in plain sight across a high-security boardroom without manifesting light flares or astral ripples. Observers must beat **Threshold 5** on Perception to even suspect magic is occurring.

---

### B. The Direct Combat & Stealth Strike Arsenal

```text
                         THE DIRECT COMBAT & STEALTH STRIKE ARSENAL
                 [Armor-Bypassing Damage Triad + Zero-Footprint Casting]

       STUNBALL (CRB 134)           WRECK DRONES (SW 27)           MANABALL (CRB 133)
   (Direct Combat, Area, DV 4)   (Direct Combat, LOS, DV 4)   (Direct Combat, Area, DV 5)
  +---------------------------+ +---------------------------+ +---------------------------+
  | • Non-lethal crowd stun   | | • Destroys drone chassis, | | • Lethal physical AoE     |
  | • Rolls Sorcery + Magic   | |   propulsion & optics     | | • Deployed against        |
  |   vs Willpower + Intuition| | • Bypasses vehicle armor  | |   hardened kill squads    |
  | • COMPLETELY IGNORES ARMOR| | • Direct Combat category  | | • COMPLETELY IGNORES ARMOR|
  +---------------------------+ +---------------------------+ +---------------------------+
                |                             |                             |
                +-----------------------------+-----------------------------+
                                              v
                      THE MAGICIAN'S WAY + WISE WARRIOR MENTOR DISCOUNT
                                   (Street Wyrd 76 / CRB 166)
  +---------------------------------------------------------------------------------------+
  |  • -1 Edge Cost Discount: Applies across all three Combat spells.                     |
  |  • 1 Edge: Reroll 1 failed die or +1 to single die roll.                              |
  |  • 3 Edge: Add Magic (+6 dice) or reroll all failed dice on Stunball/Wreck/Manaball.  |
  |  • Stealth Effect (Grade 5): Silent casting (+5 Perception threshold to detect).      |
  |  • Finesse Quality Anchor: Surgical execution, zero collateral damage, zero Heat.     |
  +---------------------------------------------------------------------------------------+
```

* **The Direct Combat Triad:** By standardizing on **Direct Combat** spells, Velvet never rolls against physical Armor soak. Every attack tests $\text{Sorcery} + \text{Magic}$ directly against mental attributes or object thresholds, neutralizing heavily armored cyber-commandos and drones with equal ease.
* **Stealth Effect Lethality:** Combined with *Stealth Effect* (Grade 5), Velvet can drop an entire room cold in Stun (*Stunball*), disintegrate an aerial surveillance drone (*Wreck*), or dissolve a hostile kill squad (*Manaball*) without a single sound, light flash, or projectile trajectory.
* **Ethical & Operational Flexibility:** Velvet defaults to *Stunball* to uphold the *Finesse* doctrine (surgical, non-lethal, zero Heat), reserving *Manaball* for existential combat where non-lethal methods are tactically impossible.

---

### C. The Sovereign 3-Spell Sustaining Array

Under *Focused Concentration (Rating 3)* (*CRB*, p. 73), Velvet sustains three sovereign buffs 24/7 with **zero dice pool penalties**:

1. **Slot 1 (The Charisma Anchor):** *Increase Attribute (Charisma)* $\rightarrow$ Pushes Charisma from 10 $\rightarrow$ **14** (adds +4 dice to Influence, Con, Drain Resistance, and Defense Rating).
2. **Slot 2 (Combat & Action Economy):** *Increase Reflexes* $\rightarrow$ Pushes Reaction from 2 $\rightarrow$ **5** and Initiative to **4D6 (2 Major Actions)**.
3. **Slot 3 (Operational Support):** Dynamic slot alternated between **`Wingman`** (during social operations and team infiltrations), **`Physical Barrier`** (during combat extraction), or **`Increase Attribute (Willpower)`** (for high-drain ritual casting).

---

### D. The 24-Force Focus Bonding & Magic Ceiling Architecture

In SR6 (*CRB*, p. 154), maximum bonded focus Force is $\text{Magic} \times 3$. Velvet’s focus acquisitions scale in lockstep with Magic attribute milestones:

```text
    MAGIC 6 (18 FORCE CAP)         MAGIC 7 (21 FORCE CAP)         MAGIC 8 (24 FORCE CAP)
  +------------------------+     +------------------------+     +------------------------+
  | Power Focus R3  [3 F]  |     | Power Focus R3  [3 F]  |     | Power Focus R3  [3 F]  |
  | (Active in Play)       |     | Qi: Imp Sorc R3 [6 F]  |     | Qi: Imp Sorc R3 [6 F]  |
  | [15 Force Unused]      |     | [12 Force Unused]      |     | Qi: Imp Conj R3 [6 F]  |
  |                        |     |                        |     | Sust Focus R3   [3 F]  |
  |                        |     |                        |     | [6 Force Unused]       |
  +------------------------+     +------------------------+     +------------------------+
```

* **Magic 6 (Current State):** With only the **Power Focus Rating 3 (3 Force)** bonded, Velvet operates with **15 Force of headroom**, leaving ample room for temporary talismans.
* **Magic 7 (35 Karma):** Unlocks **Qi Focus: Improved Sorcery R3 (6 Force)**, pushing total bonded Force to **9 / 21 Force**.
* **Magic 8 (40 Karma):** Unlocks **Qi Focus: Improved Conjuring R3 (6 Force)** and **Sustaining Focus R3 (3 Force)**, reaching **18 / 24 Force** (safe within the 24 Force ceiling with 6 Force to spare).
