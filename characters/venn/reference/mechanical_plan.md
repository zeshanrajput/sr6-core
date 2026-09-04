# Mechanical Plan & Progression Roadmap

This document establishes Venn's post-chargen augmentation roadmap, tracking Essence holes, sell-back credits, cyberlimb capacity utilization, and Karma/Nuyen conversions via the **Working for the Streetdoc** Major Downtime Activity (*Shadowrun Missions Guide v2.4*, p. 20).

---

## 1. Core Downtime & Campaign Rules

* **Shadow Healthcare Community Membership**: Unlocks the *Working for the Streetdoc* Major Downtime Activity (*SRMG v2.4*, p. 20).
* **Augmentation Conversion Rate**: Convert unlimited Karma to Nuyen at **1 Karma = 7,000¥** (must be spent on augmentations for yourself).
* **Full Used/Standard Sell-Back**: Non-cultured cyberware and standard bioware can be sold back at their full purchased value (Used grade = 50% base retail credit; Standard grade = 100% base retail credit).
* **Cultured Bioware Alphaware Policy**: Because cultured bioware is genetically tailored to the host's DNA and **cannot be sold back or upgraded for trade-in nuyen credit** (0¥ resale), **all new cultured bioware is strictly purchased at Alphaware grade** on initial implantation. This permanently locks in the 20% Essence savings ($0.8\times$ multiplier) without risking stranded capital.
* **Used Grade Multipliers**: Used augmentations have an Essence multiplier of **1.1×** and a Nuyen cost multiplier of **0.5×** (50% retail).
* **Essence Hole Mechanics**: Removed augmentations create an Essence Hole equal to the Essence they consumed. New augmentations fill this hole first before touching remaining biological Essence (**0.66 Biological Essence baseline**).
* **Quality Compliance**: Biological Essence remains at $\le 1.00$ at all times, permanently maintaining legal compliance for **Cyberpsychosis (Rank 3)** (+24 Karma).

---

## 2. Starting Chargen Baseline & Augmentation State

Venn begins play with **0.66 Biological Essence** (6.00 Base + 1.00 Augmentation Acclimation R10 buffer $- 6.34$ Total Consumed):

| Augmentation | Grade | Base Ess | Grade Mult | Adapsin (-10%) | Final Ess | Purchase Cost | Key Function & Tabletop Synergy |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :--- |
| **Adapsin Therapy** | Gene | 0.10 | 1.0× | — | **0.10 Ess** | 30,000¥ | Therapeutic Geneware. Reduces Essence cost of all cyberware by 10% (round down) post-grade! |
| **Left Synthetic Cyberarm** | Used | 1.00 | 1.1× | 0.9× | **0.99 Ess** | 17,500¥ | Agility [+3] Mod; Built-in Utility Kit (2 Cap), Shock Hand (2 Cap). 1 Cap open. |
| **Right Synthetic Cyberarm** | Used | 1.00 | 1.1× | 0.9× | **0.99 Ess** | 17,500¥ | Agility [+3] Mod; Built-in Medkit (4 Cap) housing Savior Medkit R6. 1 Cap open. |
| **Left Synthetic Cyberleg** | Used | 1.00 | 1.1× | 0.9× | **0.99 Ess** | 17,500¥ | Agility [+3] Mod, Bulk Mod R2 (12 Cap). Houses Used Nanohive R3, Skates, Gecko Tips (12/12 Cap). |
| **Right Synthetic Cyberleg** | Used | 1.00 | 1.1× | 0.9× | **0.99 Ess** | 17,500¥ | Agility [+3] Mod, Bulk Mod R2 (12 Cap). Houses Used Nanohive R3, Skates, Gecko Tips (12/12 Cap). |
| **Left Leg Nanohive R3** | Used | 0.60 | In Limb | [6 Cap] | **0.00 Ess** | 22,500¥ | Consumes Capacity only (0.00 Ess). Controls 3 colonies, manages 9 NV, replenishes 3 NV/hr. |
| **Right Leg Nanohive R3** | Used | 0.60 | In Limb | [6 Cap] | **0.00 Ess** | 22,500¥ | Consumes Capacity only (0.00 Ess). Controls 3 colonies, manages 9 NV, replenishes 3 NV/hr. |
| **Bone Density Augmentation R4** | Beta | 1.20 | 0.7× | — | **0.84 Ess** | 30,000¥ | +4 Body for damage resistance soak (9 unarmored soak), 4P Unarmed DV, +3 AR. |
| **Skilljack R6** | Used | 0.60 | 1.1× | 0.9× | **0.59 Ess** | 60,000¥ | Runs Activesofts up to R6; Wireless limit = R6 × 4 = 24. |
| **Skillwires R6** | Used | 0.60 | 1.1× | 0.9× | **0.59 Ess** | 60,000¥ | Wireless-ON: +1 dice pool modifier to all skills routed through skillwires. |
| **Math SPU** | Used | 0.25 | 1.1× | 0.9× | **0.25 Ess** | 12,500¥ | -1 Edge cost on Logic tests (-2 when overdriven with +1 wild die); 0 Bad Luck. |
| **TOTAL CONSUMED** | | | | | **6.34 Ess** | **311,000¥** | **Remaining Biological Essence: 0.66 Ess** (Acclimation R10 buffer +1.00; leaves 0.66 Ess cushion) |

---

## 3. Cyberlimb Capacity Architecture (52 Total Capacity with Bulk R4)

```text
                    +------------------------------------------------+
                    |  CYBERLIMB MODULAR CAPACITY (52 CAP WITH BULK) |
                    +-----------------------+------------------------+
                                            |
                 +--------------------------+--------------------------+
                 |                                                     |
                 v                                                     v
    +------------------------------+             +------------------------------+
    |  CYBERARMS (24 CAP TOTAL)    |             |  CYBERLEGS (28 CAP TOTAL)    |
    |  Left Arm (12 Cap):          |             |  Left Leg (14 Cap):          |
    |  - Agility [+4] (4 Cap)      |             |  - Agility [+4] (4 Cap)      |
    |  - Tesla Coil (8 Cap)        |             |  - Retractable Skates (2 Cap)|
    |  Right Arm (12 Cap):         |             |  - Hydraulic Jacks R2 (2 Cap)|
    |  - Agility [+4] (4 Cap)      |             |  - Hidden Slide (3 Cap)      |
    |  - Built-in Medkit (4 Cap)   |             |  - Built-in Utility (2 Cap)  |
    |  - Monofilament Saw (4 Cap)  |             |  - Gecko Tips (1 Cap)        |
    |    [12/12 Exact per arm]     |             |  Right Leg (14 Cap):         |
    |                              |             |  - Agility [+4] (4 Cap)      |
    |                              |             |  - Retractable Skates (2 Cap)|
    |                              |             |  - Hydraulic Jacks R2 (2 Cap)|
    |                              |             |  - Smuggling Box (5 Cap)     |
    |                              |             |  - Gecko Tips (1 Cap)        |
    |                              |             |    [14/14 Exact per leg]     |
    +------------------------------+             +------------------------------+
```

### The Capacity vs. Essence Golden Rule (0 Essence Cost)

Source: Shadowrun 6e Core Rulebook (p. 288, 290) and Body Shop (p. 33–34, 44–49).

Under standard SR6 augmentation rules, cyberware modifications installed directly into organic flesh cost **Essence**, whereas modifications installed into existing cyberlimbs cost **[Capacity] ONLY (0.00 Essence cost)**. By adding **Bulk Modification Rating 4** (2,000¥ per limb | +4 Capacity per limb), Venn expands total cyberlimb capacity from 36 to **52 Total Capacity** with **0.00 Essence consumed**:

```text
                       PASSIVE & OVERDRIVEN ATTRIBUTE ARRAYS
+-----------------------------------------------------------------------------------+
|  CYBERLIMB AGILITY  | Base 2 + 4 Enhancement + 2 Redliner = 8 AGI (10 OVERDRIVEN)  |
|  NATURAL STRENGTH   | Base 2 + 0 Enhancement + 2 Redliner = 4 STR (6 OVERDRIVEN)   |
+-----------------------------------------------------------------------------------+
```

---

### Modular Capacity Breakdown (52 / 52 Capacity — 100% Utilized)

#### 1. Left Cyberarm (12 / 12 Capacity)

* **Agility Enhancement [+4]**: `[4 Cap | 20,000¥]` $\rightarrow$ Pushes limb Agility to **8 (10 Overdriven)**.
* **Tesla Coil (Spray Attack)**: `[8 Cap | 15,000¥ | Avail 7(I) | *Body Shop*, p. 49]` $\rightarrow$ Forearm-integrated directed lightning projector (**5S(e) Damage | Spray Attack Mode | AR 8/10\*/-/-/- | 5 Shots**). Arcs electrical stun damage across multiple clustered enemies without drawing a weapon!

#### 2. Right Cyberarm (12 / 12 Capacity)

* **Agility Enhancement [+4]**: `[4 Cap | 20,000¥]` $\rightarrow$ Pushes limb Agility to **8 (10 Overdriven)**.
* **Built-in Medkit (Mil-Spec Medkit R6)**: `[4 Cap | 1,000¥ + Medkit | *Body Shop*, p. 44]` $\rightarrow$ Automated paramedic trauma suite inside the right forearm. Allows instant field diagnosis, toxin stabilization, and emergency healing.
* **Implanted Monofilament Combat Chainsaw**: `[4 Cap | 3,000¥ | Avail 3 | *Body Shop*, p. 5 & *Firing Squad*, p. 14]` $\rightarrow$ Forearm-deployed motorized monofilament saw (**6P Base Physical Damage | AR 10/-/-/-/-**). Doubles its DV when employed against barriers, chewing through reinforced security doors, titanium bulkheads, and engine blocks in seconds!

#### 3. Left Cyberleg (14 / 14 Capacity)

* **Agility Enhancement [+4]**: `[4 Cap | 20,000¥]` $\rightarrow$ Operates at AGI 8 (10 Overdriven).
* **Retractable Inline Skates**: `[2 Cap | 250¥ | *Body Shop*, p. 48]` $\rightarrow$ Motorized inline wheels deployed on demand for high-speed **10-meter ground glide**.
* **Hydraulic Jacks (Rating 2)**: `[2 Cap | 5,000¥ | *SR6 Core*, p. 289]` $\rightarrow$ Reduces Flying Kick launch threshold from 3 down to **1 hit**, and absorbs up to 4 boxes of falling damage!
* **Hidden Slide**: `[3 Cap | 3,000¥ | *SR6 Core*, p. 289]` $\rightarrow$ Concealed pop-out slide mechanism for quick-deploying tools or secondary items.
* **Built-in Utility Kit**: `[2 Cap | 1,000¥ | *Body Shop*, p. 44]` $\rightarrow$ Integrated micro-soldering, lock diagnostics, and optical wire taps for 0-gear-penalty hardware decker bypass.
* **Gecko Tips**: `[1 Cap | 500¥ | *Body Shop*, p. 45]` $\rightarrow$ Microscopic setae on the sole of the foot.

#### 4. Right Cyberleg (14 / 14 Capacity)

* **Agility Enhancement [+4]**: `[4 Cap | 20,000¥]` $\rightarrow$ Operates at AGI 8 (10 Overdriven).
* **Retractable Inline Skates**: `[2 Cap | 250¥ | *Body Shop*, p. 48]` $\rightarrow$ Motorized inline wheels deployed on demand for high-speed **10-meter ground glide**.
* **Hydraulic Jacks (Rating 2)**: `[2 Cap | 5,000¥ | *SR6 Core*, p. 289]` $\rightarrow$ Reduces Flying Kick launch threshold from 3 down to **1 hit**.
* **Smuggling Compartment**: `[5 Cap | 6,000¥ | *SR6 Core*, p. 289]` $\rightarrow$ Heavy concealed internal cavity with $-4$ search modifier; fits illicit paydata drives, contraband, or compact hardware.
* **Gecko Tips**: `[1 Cap | 500¥ | *Body Shop*, p. 45]` $\rightarrow$ Microscopic setae on the sole of the foot.

---

### Non-Magical "Wall Running" & Kinetic Blitz Suite

1. **Non-Magical Wall Running**: Combining **Gecko Tips** in both cyberfeet with **Gecko Tape Gloves** (250¥) allows Venn to run, climb, or skate vertically up sheer walls and hang from ceilings like an Adept without magic!
2. **The 15+ Meter Kinetic Blitz**:
   * **Glide (Minor Action)**: Skates deploy $\rightarrow$ **10 meters** of high-speed gliding.
   * **Catapult (Minor Action)**: Hydraulic Jacks launch Venn **4–6+ meters** through the air (launch threshold = 1 hit).
   * **Strike (Major Action)**: Lands an **8P Base Physical Kick** or discharges the **5S(e) Tesla Coil Spray** across the entire enemy squad!

---

## 4. Downtime Progression Roadmap (12–14 Karma "Moves")

All augmentation progression is synchronized around the **Working for the Streetdoc** downtime move (*Body Shop*, p. 101: **7,000¥ per Karma spent**). To fit real-table pacing (accessing the streetdoc roughly every other mission), upgrades are organized into discrete **12–14 Karma "bites"**.

Because every augmentation upgrade utilizes an **Essence Hole** or cyberlimb capacity, **biological Essence remains strictly under the 1.00 Essence cap at all times**, keeping Venn **100% Cyberpsychosis legal across character lifetime**.

```text
               SYNCHRONIZED STREETDOC & KARMA PROGRESSION TIMELINE
+-----------------------------------------------------------------------------------+
|  CHARGEN BASELINE (Day 1)         -> Tae Kwon Do (7P Flying Kick) + Skates/Jacks  |
+-----------------------------------------------------------------------------------+
|  MOVE 1: STREETDOC (~14 Karma)   -> Essence Mine + Alphaware Cerebral R3 (LOG 10) |
|  INTERVAL 1: KARMA (12 Karma)    -> Sangre y Acero (8P Kick) + Mean Right Hook   |
|                                     (1-Edge Instant Blackout Subdual Engine!)     |
+-----------------------------------------------------------------------------------+
|  MOVE 2: STREETDOC (10.2 Karma)  -> 52-Cap Bulk + Tesla Coil + Saw + Smuggling    |
|  INTERVAL 2: KARMA (18 Karma)    -> Analytical Mind (6) + Extended Overdrive R1   |
+-----------------------------------------------------------------------------------+
|  MOVE 3: STREETDOC (~14 Karma)   -> Alphaware Cerebellum R3 (Intuition 8 / S:9)   |
|  INTERVAL 3: KARMA (17 Karma)    -> Extended Overdrive R2 (12) + Bending Reed [M] |
+-----------------------------------------------------------------------------------+
|  MOVE 4: STREETDOC (9.8 Karma)   -> Cerebellum Enhancer (INT 9/S:10) + Platelets  |
|  INTERVAL 4: KARMA (17 Karma)    -> Extended Overdrive R3 (12) + Bending Reed [R] |
+-----------------------------------------------------------------------------------+
|  INTERVAL 5: KARMA (5 Karma)     -> Sense the Breeze (5) (Damage Shunted to Stun) |
+-----------------------------------------------------------------------------------+
```

---

### Phase-by-Phase Step Accounting

#### Step 1: Streetdoc Move 1 — The "Essence Mine", Cerebral Boosters R3 & Enhancer

* **Prerequisite**: 14 Karma saved + chargen gear trade-in.
* **1. Upgrade 4x Cyberlimbs to Alphaware**:
  * *Sell-Back Credit*: 4 × 20,000¥ (base limb) = +80,000¥ trade-in credit.
  * *Alphaware Purchase*: 4 × 24,000¥ (20k × 1.2) = 96,000¥. Net cash required: **16,000¥** (2.3 Karma).
  * *Essence Freed*: $4 \times (1.00 - 0.80) = \mathbf{+0.80\text{ Ess Hole}}$.
* **2. Install Cerebral Boosters R3 (Alphaware Cultured Bioware)**:
  * *Essence Cost*: $0.60 \times 0.8 = \mathbf{0.48\text{ Ess}}$ (Seated inside the +0.80 Ess Hole).
  * *Nuyen Cost*: 113,400¥ ($94.5\text{k} \times 1.2$ | Funded via 11.7 Karma Streetdoc credit + trade-in/cash).
* **3. Install Cerebral Booster Enhancer (Alphaware Geneware)**:
  * *Essence Cost*: $0.20 \times 0.8 = \mathbf{0.16\text{ Ess}}$ (Seated inside the +0.80 Ess Hole).
  * *Nuyen Cost*: 48,000¥ (6.9 Karma).
  * *Essence Hole Balance*: $+0.80 - 0.48 - 0.16 = \mathbf{+0.16\text{ Ess Hole remaining}}$ (Biological Essence intact at **0.49**).
  * *Game Effect*: **Logic 10** (+3 Boosters + 1 Enhancer), Living Persona Data Processing **11**, Matrix Attack/Hacking pools **17d6–19d6**.

#### Step 2: Interleaved Karma & Nanite Spend 1 — 10P Flying Kick Engine & 1-Edge Instant Blackout

* **1. Martial Arts: Tae Kwon Do & Techniques (12 Karma)** (*Firing Squad*, p. 89, 102):
  * **Tae Kwon Do Style (7 Karma)**: Unlocks the formal unarmed striking style.
  * **Kick Attack (5 Karma)**: Adds **+1 DV** to all kicking attacks.
  * **Flying Kick (5 Karma)**: Adds **+2 DV** (stacks with Kick Attack for **+3 DV total**; extends Close range bracket by 0.5m/hit).
* **2. Sangre y Acero: Iron Limbs (7 Karma)** (*Body Shop*, p. 5 / *Firing Squad*, p. 103):
  * Unlocks **Iron Limbs** (Signature Technique: **+1 DV** base unarmed damage).
* **3. Mean Right Hook (5 Karma)** (*Firing Squad*, p. 104):
  * Reduces the Edge cost of the *Knockout Blow* Edge Action from 2 Edge $\rightarrow$ **1 Edge**.
* **4. Toughskin Colony Template Acquisition (12,000¥ / 1.7 Karma Streetdoc)** (*Body Shop*, p. 86):
  * Permanent template loaded into Nanohive forge software.
  * *Passive Armor*: Adds **+1 to Defense Rating** per 2 NV bound into the structure (up to +3 DR).
  * *Extruded Microspines (Minor Action)*: Microscopic carbon-nanotube spines extrude through skin/covering, adding **+1 DV to unarmed attacks** and inflicting 1P retaliatory damage on anyone grappling barehanded!
* **The 10P Kinetic Subdual Engine Calculation**:
  $$\text{4P (Bone Density 4)} + \text{1P (Iron Limbs)} + \text{1P (Neuromuscular Amp)} + \text{1P (Toughskin Spines)} + \text{3P (Flying Kick)} = \mathbf{10P\text{ Base Physical Damage!}}$$
  * *Net Hits Scaling*: With Agility 10 (Overdriven) + Athletics + Close Combat, 4 net hits yields **14P Physical Damage**!
  * *1-Edge Instant Blackout*: Spending **1 Edge on Knockout Blow** instantly drops any opponent unconscious whose Willpower or Body is $\le$ the damage inflicted!

#### Step 3: Streetdoc Move 2 — The 52-Capacity Bulk Expansion (10.2 Karma / 71,500¥)

* **Prerequisite**: 10–11 Karma saved with Streetdoc.
* **1. Bulk Modification Rating 4 (All 4 Limbs)**: 4 × 2,000¥ = **8,000¥** (1.1 Karma) $\rightarrow$ Expands capacity to **52 Total Cap** (0 Ess)!
* **2. Agility Enhancement [+4] (All 4 Limbs)**: 4 × 5,000¥ upgrade = **20,000¥** (2.8 Karma) $\rightarrow$ **Agility 8 (10 Overdriven)**!
* **3. Tesla Coil (Left Arm)**: **15,000¥** (2.1 Karma) $\rightarrow$ 5S(e) Directed Lightning Spray Attack.
* **4. Built-in Mil-Spec Medkit R6 (Right Arm)**: **4,000¥** (0.6 Karma) $\rightarrow$ Paramedic trauma suite.
* **5. Implanted Monofilament Combat Chainsaw (Right Arm)**: **3,000¥** (0.4 Karma) $\rightarrow$ 6P Structural Breacher (doubles DV vs barriers).
* **6. Smuggling Compartment (Right Leg)**: **6,000¥** (0.9 Karma) $\rightarrow$ Heavy concealed cavity ($-4$ search modifier).
* *Result*: The **Tesla Coil Spray**, **Monofilament Chainsaw**, and **52-Cap modular loadout** are 100% complete!

#### Step 4: Interleaved Karma Spend 2 — Analytical Mind & 1-Round Overdrive (18 Karma)

* **1. Analytical Mind (6 Karma)** (*Sixth World Companion*, p. 124 — Base 3 Karma × 2 post-chargen): +1 Edge on all Logic, pattern recognition, and matrix intrusion tests.
* **2. Extended Overdrive Rank 1 (12 Karma)** (*Sixth World Companion*, p. 133 — Base 6 Karma × 2 post-chargen): Overdrive lasts **1 full combat round** per activation.

#### Step 5: Streetdoc Move 3 — Intuition Transcendence (~14 Karma + Cash)

* **1. Upgrade Skilljack R6 & Skillwires R6 to Alphaware**:
  * *Sell-Back Credit*: +120,000¥ trade-in credit.
  * *Alphaware Purchase*: 288,000¥. Net cash required: **168,000¥**.
  * *Essence Freed*: $2 \times (0.66 - 0.48) = \mathbf{+0.36\text{ Ess Hole}}$ (Expands hole pool to $+0.16 + 0.36 = \mathbf{+0.52\text{ Ess Hole}}$).
* **2. Install Cerebellum Boosters R3 (Alphaware Cultured Bioware)**:
  * *Essence Cost*: $0.60 \times 0.8 = \mathbf{0.48\text{ Ess}}$ (Seated inside +0.52 Ess Hole).
  * *Nuyen Cost*: 180,000¥ (Funded via 14 Karma Streetdoc credit + mission cash earnings).
  * *Essence Hole Balance*: $+0.52 - 0.48 = \mathbf{+0.04\text{ Ess Hole remaining}}$ (Biological Essence intact at **0.49**).
  * *Game Effect*: **Intuition 8**, Living Persona Sleaze **9**, Matrix Perception/Defense **14d6**, Initiative **11 + 1D6**.

#### Step 6: Interleaved Karma Spend 3 — 2-Round Overdrive & Melee Dodge Mastery (17 Karma)

* **1. Extended Overdrive Rank 2 (12 Karma)**: Overdrive lasts **2 full combat rounds**.
* **2. Bending of the Reed (Melee) (5 Karma)** (*Firing Squad*, p. 103): Gain **+1 Bonus Edge** whenever taking the Dodge Minor Action against melee attacks.

#### Step 7: Streetdoc Move 4 — Max Sleaze & Damage Reduction (9.8 Karma / 68,400¥)

* **1. Install Cerebellum Booster Enhancer (Alphaware Geneware)**:
  * *Essence Cost*: $0.20 \times 0.8 = \mathbf{0.16\text{ Ess}}$ (Takes 0.04 from hole $+ 0.12$ from biological).
  * *Nuyen Cost*: 48,000¥ (6.9 Karma).
  * *Game Effect*: Pushes Intuition to **9** $\rightarrow$ Living Persona Sleaze = **10**!
* **2. Install Platelet Factories (Alphaware Bioware)**:
  * *Essence Cost*: $0.20 \times 0.8 = \mathbf{0.16\text{ Ess}}$ (Consumes 0.16 Biological Essence).
  * *Nuyen Cost*: 20,400¥ (2.9 Karma).
  * *Biological Essence*: Shifts from $0.49 \rightarrow \mathbf{0.21\text{ Ess}}$ (Safely under 1.00 cap; legal for Cyberpsychosis R3).
  * *Game Effect*: Whenever taking $\ge 2$ boxes of Physical damage from an attack, **reduce damage by 1 box**.

#### Step 8: Interleaved Karma Spend 4 — Full 3-Round Overdrive & Ranged Dodge (17 Karma)

* **1. Extended Overdrive Rank 3 (12 Karma)**: Overdrive lasts **3 full combat rounds** (Venn spends 1 Minor Action on Turn 1 and stays at Agility 10 / Wild Die / +1 Edge generation for the entire battle!).
* **2. Bending of the Reed (Ranged) (5 Karma)** (*Firing Squad*, p. 103): Gain **+1 Bonus Edge** whenever taking the Dodge Minor Action against ranged gunfire.

#### Step 9: Interleaved Karma Spend 5 — Damage Shunting to Stun (5 Karma)

* **1. Sense the Breeze (5 Karma)** (*Body Shop*, p. 5): After dodging via Bending of the Reed, shunt unsoaked Physical damage to **Stun damage** equal to augmented Reaction bonus.

---

## 5. Activesoft Acquisition Strategy: Pure Nuyen vs. Karma

Because *Working for the Streetdoc* yields **7,000¥ per Karma** on augmentations, while the *Programming* downtime move (*Hack and Slash*, p. 86) yields only **4,000¥ per Karma** on software:

> [!TIP]
> **Financial Rule**: Spend **100% of Karma** on Streetdoc augmentation moves and martial arts qualities. Purchase all Rating 6 Activesofts (30,000¥ each) with **Pure Nuyen from Mission Payouts**!

### Activesoft Priority Acquisition Order (via Mission Pay)

| Priority | Skillsoft (Rating 6) | Market Cost | Tabletop Attack / Test Pool |
| :---: | :--- | :---: | :--- |
| **1** | **Firearms (Heavy Pistols)** | ¥30,000 | **17d6 Pool** (19d6 Overdriven) w/ Smartlink + Wires-ON |
| **2** | **Close Combat (Unarmed)** | ¥30,000 | **15d6 Pool** (17d6 Overdriven) w/ Wires-ON |
| **3** | **Stealth (Sneaking)** | ¥30,000 | **15d6 Pool** (17d6 Overdriven) w/ Wires-ON |
| **4** | **Engineering (Lockpicking)** | ¥30,000 | **17d6 Pool** (18d6 Overdriven) w/ Logic 10 + Wires-ON |
| **5** | **Piloting (Ground Craft)** | ¥30,000 | **11d6 Pool** (13d6 Overdriven) w/ REA 2 + Wires-ON |

---

## 6. Chargen Skill Tuning: Free Athletics (Rating 1) Allocation

In Point Buy chargen, characters receive **12 Free Skill Points**. Venn spent 7 points on Electronics 6 + Specialization, and 5 points on Knowledge Skills.

By trading **1 Knowledge Skill** for **Athletics (Rating 1)** at chargen (0 CP, 0 Karma):

* **Eliminates Unskilled Penalty**: Removes the $-1$ dice pool penalty on all physical jumping, sprinting, climbing, and flying kicks.
* **Preserves Skillwire Capacity**: Does not tie up any skillwire slots.
* **Leap Distance Multiplier**: With Cyberleg Agility 8 (10 Overdriven) + Athletics 1 + Hydraulic Jacks R2, Venn rolls **9d6 (11d6 Overdriven)** against a threshold of **1**, guaranteeing **3–5 hits on every launch** and propelling Flying Kicks **1.5m to 2.5m+ across the room**!

---

## 7. Lifetime Essence Accounting Ledger

| Milestone / Upgrade Event | Ess Hole Freed | Ess Hole Consumed | Ess Hole Pool | Biological Essence | Cyberpsychosis Cap Status |
| :--- | :---: | :---: | :---: | :---: | :--- |
| **Chargen Baseline** | — | — | 0.00 | **0.66 Ess** | **LEGAL** ($\le 1.00$ Ess) |
| **Move 1: 4x Limbs $\rightarrow$ Alphaware** | +0.80 Ess | — | +0.80 Ess | 0.66 Ess | **LEGAL** ($\le 1.00$ Ess) |
| **Move 1: Alphaware Cerebral R3 & Enhancer** | — | 0.64 Ess | +0.16 Ess | 0.66 Ess | **LEGAL** ($\le 1.00$ Ess) |
| **Move 2: 52-Cap Bulk Modification** | — | — (0 Ess) | +0.16 Ess | 0.66 Ess | **LEGAL** ($\le 1.00$ Ess) |
| **Move 3: Skilljack/Wires $\rightarrow$ Alpha** | +0.36 Ess | — | +0.52 Ess | 0.66 Ess | **LEGAL** ($\le 1.00$ Ess) |
| **Move 3: Alphaware Cerebellum R3** | — | 0.48 Ess | +0.04 Ess | 0.66 Ess | **LEGAL** ($\le 1.00$ Ess) |
| **Move 4: Cerebellum Enhancer** | — | 0.16 Ess | 0.00 Ess | **0.54 Ess** | **LEGAL** ($\le 1.00$ Ess) |
| **Move 4: Platelet Factories** | — | 0.16 Ess | 0.00 Ess | **0.38 Ess** | **LEGAL** ($\le 1.00$ Ess) |

---

## 8. Strategic Multi-Axis Priority Analysis

```text
               DEVELOPMENT VALUE BY AXIS (POST-OPTIMIZATION)
+-----------------------------------------------------------------------------------+
| AXIS 1: COMPUTATIONAL SUPREMACY   | LOG 10 / INT 9 / Living Persona ASDF: 2/10/11/9 |
| AXIS 2: 10P KINETIC SUBDUAL ENGINE | 10P Base Kick + 1-Edge KO + 15m Skating Blitz |
| AXIS 3: STRUCTURAL BREACHING      | Monofilament Saw (6P / 2x vs Barriers) + Setae |
| AXIS 4: TRAUMA & FIRST AID SUITE  | Built-in Mil-Spec Medkit + Automated Treatment |
| AXIS 5: ESSENCE INTEGRITY         | Biological 0.66 -> 0.38 (100% Cyberpsychosis)  |
+-----------------------------------------------------------------------------------+
```
