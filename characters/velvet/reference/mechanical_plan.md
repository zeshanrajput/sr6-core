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
  3. **Learn Spells (Minor Action):** Absorb the next queued spell (**5 Karma + 1 Minor Action study**). *Priority:* **`Wingman`** (*Smooth Operations*, p. 110) $\rightarrow$ **`Charm`** (*CRB*, p. 138) $\rightarrow$ **`Fashion`** (*Street Wyrd*, p. 48) $\rightarrow$ **`Sterilize`** (*Street Wyrd*, p. 56).
  4. **Spirit Binding & Re-Binding (Minor Action):** Bind Fire or Air spirits up to the Magic $\times$ 3 Force cap (18 Force at Magic 6).

---

## 2. Master Unified Progression Queue

All upcoming upgrades are prioritized sequentially below. When logging post-mission downtime, advance the next available item in this table according to banked Karma, liquid Nuyen, and available action slots.

### A. Karma Progression Pipeline (Ontological & Metamagic Scaling)

*(Current Baseline: Initiation Grade 5, Magic 6, 4 Karma banked after Session 9).*

| Step | Target Upgrade | Category | Cost | Downtime Action Required | Primary Tactical & Architectural Role |
| :---: | :--- | :--- | :---: | :---: | :--- |
| **01** | **Initiation Grade 6**<br>• *The Magician's Way* | Metamagic | 9 Karma* | 1 Major Action<br>*(Mainline SRM)* | *Street Wyrd* 76: Apex capstone at Magic 6. Unlocks dual mentor spirit benefits for *Wise Warrior* (combat sorcery bonus + combat spell Edge discounts) and allows Adept drain to be resisted with **Body + Charisma (14+ dice)**. |
| **02** | **Spell: Wingman** | Detection Spell | 5 Karma | 1 Minor Action (Study) | *Smooth Operations* 110: Specialized sustained Mindlink for social teamwork. Helper gets 1 temporary Edge on assistance; leader gains 1 temporary Edge for *each* die provided. Sustained via *Focused Concentration*. |
| **03** | **Spell: Charm** | Manipulation Spell | 5 Karma | 1 Minor Action (Study) | *CRB* 138: Adds +4 dice to all Influence and Con tests against targeted subjects. Pairs with *Stealth Effect* for covert social dominance. |
| **04** | **Spell: Fashion** | Manipulation Spell | 5 Karma | 1 Minor Action (Study) | *Street Wyrd* 48: Instant wardrobe and fabric restructuring. Combined with *Cosmetic Control 2*, enables seamless visual transformation in seconds. |
| **05** | **Untrained Skill Repair**<br>• *Perception 1 (Intuition)*<br>• *Astral 1 (Intuition)* | Active Skills | 10 Karma tot<br>*(5K each)* | None (Between runs) | Removes -1 untrained penalty (+2 dice swing each; Perception 3d $\rightarrow$ 5d, Astral 3d $\rightarrow$ 5d). Essential for spotting physical ambushes and reading emotional auras. |
| **06** | **Tactical Sabotage Spells**<br>• *Sterilize*<br>• *Wreck (Drones)* | Spells | 10 Karma tot<br>*(5K each)* | 2 Minor Actions (Study) | *Street Wyrd* 56, *CRB* 142: Complete forensic DNA/evidence cleansing (*Sterilize*); subtle physical disruption against hostile surveillance drones (*Wreck*). |
| **07** | **Attribute: Magic 6 $\rightarrow$ 7** | Attribute | 35 Karma | None (Between runs) | Unlocks Initiate Grades 7+, expands Focus Bonding Cap from 18 $\rightarrow$ **21 Force**, and raises safe spirit summoning threshold to Force 6. |
| **08** | **Initiation Grade 7**<br>• *Flexible Signature* | Metamagic | 12 Karma* | 1 Major Action<br>*(Mainline SRM)* | *CRB* 165: Enables altering or completely erasing astral signatures from spellcasting, rendering Velvet astrally untraceable. |
| **09** | **Attribute: Magic 7 $\rightarrow$ 8** | Attribute | 40 Karma | None (Between runs) | Expands Focus Bonding Cap to **24 Force**, allowing dual Rating 6 Qi Foci to bond simultaneously with Power Focus R3 and Sustaining Focus R3. |
| **10** | **Initiation Grade 8**<br>• *Adept Centering* | Metamagic | 13 Karma* | 1 Major Action<br>*(Mainline SRM)* | *CRB* 167: Adds Initiate Grade to physical and combat actions via centering gestures, insulating active tests against situational modifiers. |
| **11** | **Quality: Teamwork Makes Dream Work** | Positive Quality | 12 Karma<br>*(2x 6K)* | None (Between runs) | *Hack & Slash* 83: Extends social teamwork bonuses to all party members, multiplying Edge generation when paired with *Wingman*. |
| **12** | **Quality: Charismatic Defense** | Positive Quality | 24 Karma<br>*(2x 12K)* | None (Between runs) | *Power Plays* 85: Bases Defense Rating off Charisma instead of Body (DR jumps from 2 $\rightarrow$ **10–14**!). |

*\*Initiation cost formula at Loyalty 6: $10 + 5 - 6 = 9$ Karma; at Loyalty 4 floor: $10 + \text{Current Grade} - 4$.*

---

### B. Nuyen & Foci Progression Pipeline

*(Current Baseline: Power Focus Rating 3 bonded, ¥22,915 liquid nuyen after Session 9).*

| Step | Target Hardware / Focus Upgrade | Source / Book | Cost | Downtime Action Required | Capacity & Tactical Role |
| :---: | :--- | :--- | :---: | :---: | :--- |
| **H1** | **M-TOC Tactical Network Node** | *Firing Squad* 110 | ¥15,000–¥30,000 | None (Market Purchase) | Team Edge storage bank and encrypted squad tactical coordination network. |
| **H2** | **Qi Focus: Improved Sorcery (R3)** | *CRB* 155, 294 | ¥36,000 + 24 Karma | Minor Action (Bond Focus) | Rating 6 Qi Focus (Force 6 = $4 \times 1.5$ PP). Flat **+3 dice to all Spellcasting tests** (pushes Sorcery to **21+ dice**). Requires Magic 7 (21 Force cap). |
| **H3** | **Qi Focus: Improved Conjuring (R3)** | *CRB* 155, 294 | ¥36,000 + 24 Karma | Minor Action (Bond Focus) | Rating 6 Qi Focus (Force 6). Flat **+3 dice to Conjuring** (pushes pool to **20 dice = 5 bought hits vs Force 8 spirits**). Requires Magic 8 (24 Force cap). |
| **H4** | **Sustaining Focus: Health (R3)** | *CRB* 155, 294 | ¥27,000 + 6 Karma | Minor Action (Bond Focus) | Rating 3 Focus (Force 3). Sustains *Increase Attribute (Charisma)* or *Increase Reflexes* independently, freeing a Focused Concentration slot for *Wingman*. |

---

## 3. Forward Architectural Blueprints

### A. The Covert Social Infiltration & Edge Engine

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

* **Covert Social Casting:** *Stealth Effect* allows Velvet to cast *Charm* (+4 dice), *Fashion*, or *Mind Probe* in plain sight across a corporate gala or syndicate sit-down without manifesting light flares or astral ripples. Observers must beat **Threshold 5** on Perception to even suspect magic is occurring.
* **Teamwork Edge Multiplication:** When Velvet casts *Wingman* and acts as the helper on a social test, Velvet gains a free Edge, while the leader receives an additional temporary Edge for every assisting die Velvet provides. With Velvet rolling **19–24 dice** on Influence/Con, the team enters every critical negotiation with maximum Edge.

---

### B. The Sovereign 3-Spell Sustaining Array

Under *Focused Concentration (Rating 3)* (*CRB*, p. 73), Velvet sustains three sovereign buffs 24/7 with **zero dice pool penalties**:

1. **Slot 1 (The Charisma Anchor):** *Increase Attribute (Charisma)* $\rightarrow$ Pushes Charisma from 10 $\rightarrow$ **14** (adds +4 dice to Influence, Con, Drain Resistance, and Defense Rating).
2. **Slot 2 (Combat & Action Economy):** *Increase Reflexes* $\rightarrow$ Pushes Reaction from 2 $\rightarrow$ **5** and Initiative to **4D6 (2 Major Actions)**.
3. **Slot 3 (Operational Support):** Dynamic slot alternated between **`Wingman`** (during social operations and team infiltrations), **`Physical Barrier`** (during combat extraction), or **`Increase Attribute (Willpower)`** (for high-drain ritual casting).

---

### C. The 24-Force Focus Bonding & Magic Ceiling Architecture

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
