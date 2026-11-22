# Character Advancement & Mechanical Plan: Velvet

This document has one operational role: **directing the exact sequence of Karma and Nuyen expenditures, downtime activity allocations, and architectural upgrades during character log updates.**

* **Active State & Historical Records:** Current attributes, known spells, metamagics, acquired gear, bonded foci, and ledger balances are maintained in the Markdown Trio ([`character_log.qmd`](file:///c:/GitHub/sr6-core/characters/velvet/core/character_log.qmd), [`character_purchases.qmd`](file:///c:/GitHub/sr6-core/characters/velvet/core/character_purchases.qmd), [`character_build.qmd`](file:///c:/GitHub/sr6-core/characters/velvet/core/character_build.qmd)) and compiled into `velvet_master.yaml`. Full tabletop mechanics, spirit binding math, and stacking legality rules are codified in [`rules_and_downtime.qmd`](file:///c:/GitHub/sr6-core/characters/velvet/rules/rules_and_downtime.qmd).
* **Current Active Baseline (Post-SRM 2083-16 / Session 10):** **Initiation Grade 6** (*Channeling, Centering, Masking, Stealth Effect, Power Point, The Magician's Way*); **Magic 6**; **Power Focus R3**; **Mentor Spirit Wise Warrior**; **Finesse** negative quality active. Banked Balances: **1 Karma**, **¥28,265.0**.

---

## 1. Downtime Action Economy & Allocation Protocol

Under *SRM Guide v2.4* (pp. 17–20, 47, 59–60), downtime actions between missions are strictly budgeted:

* **Mainline SRM Missions:** Grant **1 Major + 1 Minor** Action (or **3 Minor Actions** if taking no Major).
* **Convention Mission Packs (CMPs):** Grant **2 Minor Actions only** (no Major Action; Initiation cannot be performed post-CMP).
* **The Coven Decay Protocol (Guild of Freelance Assets):**
  * Currently at **Loyalty 6** (decaying $6 \rightarrow 5 \rightarrow 4$ over upcoming months without maintenance).
  * *Initiation Cost Formula:* In SRM with an active coven possessing *Symmetrical Initiation* (*Street Wyrd*, p. 128), initiation Karma cost is:
    $$\text{Cost} = 10 + \text{Target Initiation Grade} - \text{Coven Loyalty}$$
    *(At Loyalty 6: $10 + \text{Grade} - 6$; at Loyalty 5: $10 + \text{Grade} - 5$; at Loyalty 4 floor: $10 + \text{Grade} - 4$).*
  * **The Loyalty 4 Floor:** Once stabilized at Loyalty 4, maintenance costs only **1 Minor Downtime Action per month** and dues drop to **¥350/mo** ($50 \times \text{Connection 7}$). This permanently preserves a **-4 Karma initiation discount** while leaving every single SRM Major Downtime Action unencumbered.
* **The Hooder R3 Synergy:**
  * Hooder (Rating 3) mandates **¥3,000/month** in charitable donations (*6WC*, p. 137).
  * Under *SRMG v2.4* p. 19, this monthly donation directly funds the **Work for the People** Minor Downtime Action (+1 Karma per month) at zero additional nuyen charge!
* **Strict Priority Hierarchy (Execute in order upon run completion):**
  1. **Initiation (Tracker 1 — Major Action):** Consumes the Major Action on mainline SRMs when Karma threshold is reached. Initiate Grade is hard-capped by current natural Magic rating ($\text{Grade} \le \text{Magic}$; Grade 6 cap at Magic 6).
  2. **Work for the People (Minor Action):** Non-negotiable conversion of **¥2,000 $\rightarrow$ +1 Karma** (funded directly by the ¥3,000 Hooder R3 monthly obligation).
  3. **Learn Spells (Tracker 2 — Minor Action):** Absorb queued spells (**5 Karma + 1 Minor Action study** each).
  4. **Focus Bonding (Tracker 3 — Minor Action):** Bond newly acquired Qi or Sustaining foci (**Bonding Karma + 1 Minor Action**).
  5. **Spirit Binding & Re-Binding (Minor Action):** Bind Fire or Air spirits up to the Magic $\times$ 3 Force cap (18 Force at Magic 6).

---

## 2. Post-Chargen Progression: Three-Tracker Upgrade Protocol

Because post-chargen advancement is gated by **three independent finite resources**—**Major Downtime Actions** (Mainline SRMs only), **Karma** (SRMs + CMPs + *Work for the People*), and **Nuyen** (Foci acquisitions, lifestyle, and gear)—progression is tracked in three parallel queues. Whenever an upgrade opportunity opens, execute in strict priority order: **1) Initiation (Tracker 1)** $\rightarrow$ **2) Karma Queue (Tracker 2)** $\rightarrow$ **3) Nuyen & Foci Queue (Tracker 3)**.

---

### Tracker 1: Major Downtime Action Queue (Initiations & Metamagics)

*Each Initiation consumes **1 Major Action** (Mainline SRMs only) and uses the **Guild of Freelance Assets Coven Decay Protocol** (decaying to Loyalty 4 floor). Remember: Initiate Grade cannot exceed natural **Magic** ($\text{Grade} \le \text{Magic}$); therefore, **Initiate Grade 6 is the current cap at Magic 6**, and Grades 7 and 8 require **Magic 6 $\rightarrow$ 7 (K11)** and **Magic 7 $\rightarrow$ 8 (K13)** from Tracker 2 first.*

| Grade | Target Metamagic | Source / Prereq | Cost | Cadence / Gate | Tactical & Ontological Role |
| :---: | :--- | :--- | :---: | :--- | :--- |
| **1–6** | *Channeling*, *Centering*, *Masking*, *Stealth Effect*, *Power Point*, *The Magician's Way* | *CRB* / *SW* / *DA* | Completed | **Session 1–10** | **Active Baseline:** Conscious spirit channeling, +6 Centering drain resistance, aura & foci masking, sensory stealth casting, +1.0 Adept PP, dual *Wise Warrior* benefits, and Body + Charisma drain resistance. |
| **7** | **Extended Masking** | *Street Wyrd* 119<br>*SRMG* 37–38 *(Prereq: Masking)* | **13 Karma*** | **1 Major Action**<br>*(Mainline SRM; post-K11)* | **Requires `Magic 6 -> 7` (K11) first.** Cost $10+7-4=13\text{K}$ at **Loyalty 4 floor**. Crucial stealth capstone. Extends aura masking to cover all sustained spells (*Increase Charisma*, *Increase Reflexes*, *Wingman*). Adversary mages and patrol spirits assensing Velvet perceive only a completely mundane metahuman with zero active magic! |
| **8** | **Flexible Signature** | *CRB* 165 | **14 Karma*** | **1 Major Action**<br>*(Mainline SRM; post-K13)* | **Requires `Magic 7 -> 8` (K13) first.** Cost $10+8-4=14\text{K}$ at **Loyalty 4 floor**. Enables altering or completely erasing astral signatures from instantaneous spellcasting within turns equal to Initiate Grade (8 turns). Completes the astral ghost footprint. |

*\*Initiation cost formula at Loyalty 6: $10 + \text{Grade} - 6$; at Loyalty 4 floor: $10 + \text{Grade} - 4$.*

---

### Tracker 2: Karma Queue (No Major Action Required)

*Funded by SRM/CMP mission Karma + monthly `Work for the People` (`+1K/mo` via Hooder R3), running in parallel without consuming Major Actions (reserving sufficient Karma to fund Tracker 1 initiations when mainline SRMs open).*

| Priority | Target Upgrade | Category | Cost | Time / Action Required | Primary Tactical & Architectural Role |
| :---: | :--- | :--- | :---: | :---: | :--- |
| **K1** | **Sorcery Specialization: Spellcasting** | Active Skill | 5 Karma | None (Between runs) | *CRB* 69: Adds **+2 dice** to all Spellcasting tests (raises Spellcasting pool from **15d6 $\rightarrow$ 17d6**). Top priority to restore combat sorcery precision after accelerating Grade 5 initiation. |
| **K2** | **Quality: Spirit Affinity (Water)** | Positive Quality | 28 Karma<br>*(2× 14K)* | None (Between runs) | *CRB* 73 / *Astral Ways* 46: Grants +1 bonus Edge on Conjuring tests for Water spirits and unlocks Water elementals. Unlocks Force 4 **Undine** (Channeled `Mist Form` for gaseous infiltration with foci) and Force 4 **Brume** (Channeled `Innate Spell: Fashion` & `Makeover` using Velvet's Sorcery pool), plus Force 10 **Jökulhlaup** (*Ice Dragon*) post-Magic scaling. |
| **K3** | **Tactical Defense: Physical Barrier** | Manipulation (Area) | 5 Karma | 1 Minor Action (Study) | *CRB* 141: LOS(A), Sustained, Drain 6. Translucent barrier (Structure = Magic + net hits) providing mobile ballistic cover, barricading hallways, and stopping vehicle ramming. |
| **K4** | **Quality: Attribute Mastery (Charisma)** | Positive Quality | 6 Karma<br>*(2× 3K)* | None (Between runs) | *Double Clutch* 168: Generates a **bonus Edge** on *any* test based on Charisma (all Drain resistance tests, social Influence/Con/Leadership tests, and Charismatic Defense DR) unless Edge is already gained from Attack Rating. Perfect synergy with CHA 10 (14 buffed!). |
| **K5** | **Spell: Stunball** | Direct Combat (Area) | 5 Karma | 1 Minor Action (Study) | *CRB* 134: LOS(A), DV 4, Stun. Non-lethal AoE that **completely bypasses armor** ($\text{Sorcery} + \text{Magic}$ vs $\text{Willpower} + \text{Intuition}$). Immediately reaps *Wise Warrior*’s -1 Edge discount on Combat spells post-Grade 6. |
| **K6** | **Spell: Wingman** | Detection Spell | 5 Karma | 1 Minor Action (Study) | *Smooth Operations* 110: Specialized sustained Mindlink for social teamwork. Helper gets 1 temporary Edge on assistance; leader gains 1 temporary Edge for *each* die provided (19–24d). Solves the "two faces at the table" dilemma by turning Velvet into an unbeatable cooperative Edge battery. |
| **K7** | **Spell: Wreck (Drones)** | Direct Combat (LOS) | 5 Karma | 1 Minor Action (Study) | *Street Wyrd* 27: LOS, DV 4, Object destruction. Spellcasting vs Object Resistance, does net hits unresisted damage. Classified as a **Direct Combat** spell, reaping *Wise Warrior* -1 Edge discount. |
| **K8** | **Spell: Manaball** | Direct Combat (Area) | 5 Karma | 1 Minor Action (Study) | *CRB* 133: LOS(A), DV 5, Physical. Silent, lethal direct mana destruction that **completely bypasses armor**. Deployed against hardened combat teams, cybered hit squads, or hostile spirits when stun is insufficient. |
| **K9** | **Quality: Charismatic Defense** | Positive Quality | 24 Karma<br>*(2× 12K)* | None (Between runs) | *Power Plays* 85: Bases Defense Rating off Charisma instead of Body! DR leaps from 2 $\rightarrow$ **10 (unarmored) / 14 (buffed) / 18–22 (armored)**. Generates defensive Edge against almost all incoming gunfire ("too damn pretty to shoot!"). |
| **K10** | **Spell: Sterilize** | Manipulation (Area) | 5 Karma | 1 Minor Action (Study) | *Street Wyrd* 56: Complete forensic DNA, biometric, and physical evidence cleansing. Eliminates material crime scene traces. |
| **K11** | **Attribute: Magic 6 $\rightarrow$ 7** | Attribute | 35 Karma | None (Between runs) | **Apex Scaling Milestone:** Unlocks Initiate Grade 7 (Tracker 1), expands Focus Bonding Cap from 30 $\rightarrow$ **35 Force**, and raises safe spirit summoning threshold to Force 6. |
| **K12** | **Untrained Skill Repair**<br>• *Perception 1 (Intuition)*<br>• *Astral 1 (Intuition)* | Active Skills | 10 Karma tot<br>*(5K each)* | None (Between runs) | Removes -1 untrained penalty (+2 dice swing each; Perception 3d $\rightarrow$ 5d, Astral 3d $\rightarrow$ 5d). Essential for spotting physical ambushes and reading emotional auras. |
| **K13** | **Attribute: Magic 7 $\rightarrow$ 8** | Attribute | 40 Karma | None (Between runs) | Expands Individual Focus Force limit to **Force 8** and total cap to **40 Force** ($\text{Magic } 8 \times 5$). Unlocks upgrading foci to cap both Sorcery and Conjuring at the **+4 Augmented Skill Maximum**. |
| **K14** | **Quality: Dreamwork** | Positive Quality | 10 Karma<br>*(2× 5K)* | None (Between runs) | *Smooth Operations* 162: When assisting another character in a Teamwork test, increases the amount of dice they can potentially gain by 1. |

Spell Priorities:

* Physical Barrier
* Stunball
* Wingman
* Wreck (Drones)
* Manaball
* Mind Probe
* Heal
* Shape Metal
* Decrease Attribute
* Silence
* Sterilize
* Trid Phantasm
* Fashion
* Charm

#### Maintenance & Ongoing Downtime Tasks (Tracker 2 Minor Actions)

* **Work for the People:** Spend 1 Minor Action (funded by Hooder R3 ¥3,000/mo donation) $\rightarrow$ **+1 Karma** per month.
* **Guild of Freelance Assets Maintenance:** At Loyalty 4 floor, spend 1 Minor Action + ¥350/mo dues once per month to stabilize the permanent -4 Karma initiation discount.

#### Deferred Flavor & Cosmetic Backlog

* **Spell: Charm** (*CRB*, p. 138; 5 Karma) — Manipulation spell granting +4 dice to social tests. Deprioritized because Velvet already operates with natural 19–24d social pools (buying 4–5 hits routinely).
* **Spell: Fashion** (*Street Wyrd*, p. 48; 5 Karma) — Instant clothing transformation. Deprioritized because *Cosmetic Control 2* already handles biological shape/gender/height alteration, while physical disguise kits and high-fashion wardrobes cover apparel.

---

### Tracker 3: Nuyen & Foci Progression Pipeline (Minor Actions)

*Current Baseline: Power Focus Rating 3 bonded; **¥28,265.0** liquid nuyen on hand. Foci acquisitions require Nuyen for purchase, **Bonding Karma** (drawn from Tracker 2 funds), and **1 Minor Downtime Action** to bond. In SR6 (*CRB*, pp. 154–155), total bonded Force cannot exceed $\text{Magic} \times 5$ (30 Force at Magic 6; 40 Force at Magic 8), and no single focus can exceed natural Magic ($6\text{ Force}$ at Magic 6).*

| Priority | Target Hardware / Focus Upgrade | Source / Book | Cost (Nuyen + Karma) | Downtime Action Required | Capacity & Tactical Role |
| :---: | :--- | :--- | :--- | :---: | :--- |
| **N1** | **Qi Focus: Improved Conjuring (R1, Force 4)** | *CRB* 146, 155<br>*GMP* 12 | **¥12,000**<br>+ 8 Karma | 1 Minor Action (Bond Focus) | Force 4 Qi Focus ($4 \times 1.0\text{ PP}$; Conjuring is a Combat skill per SR6 FAQ). **#1 Hardware Priority:** Pushes Conjuring from 15 $\rightarrow$ **16 dice**, unlocking the **4 bought hits threshold** ($16 \div 4 = 4$ hits). Against standard **Force 4 spirits** (8 resistance dice, buying 2 hits), guarantees **2 net tasks** (up from 1 task) with **zero drain risk**. Avail 4L. Fits Magic 6 cap ($4 \le 6$). **Funded right now by liquid reserves!** |
| **N2** | **Qi Focus: Improved Sorcery (R1, Force 4)** | *CRB* 155, 294<br>*SSW FAQ* | **¥12,000**<br>+ 8 Karma | 1 Minor Action (Bond Focus) | Force 4 Qi Focus ($4 \times 1.0\text{ PP}$; Sorcery is a Combat skill per SR6 FAQ). Adds **+1 die to Sorcery**, stacking with Wise Warrior (+1) for **+2 total bonus** (pushes Spellcasting baseline from 17 $\rightarrow$ **19 dice**). Avail 4L. Fits within Magic 6 cap ($4 \le 6$). |
| **N3** | **Sustaining Focus: Health (R6, Force 6)** | *CRB* 137, 155, 294 | **¥24,000**<br>+ 12 Karma | 1 Minor Action (Bond Focus) | Force 6 Focus (**Avail 6L**; $6 \times ¥4,000$, $6 \times 2\text{ Karma}$). Required to sustain *Increase Attribute* at the maximum **+4 bonus** (base DV 3 + 3 net hits = DV 6; sustained spell DV cannot exceed focus Force per *CRB* 155). Frees a *Focused Concentration* slot for *Wingman*. Fits within Magic 6 individual Force cap ($6 \le 6$). |
| **N4** | **Qi Focus: Improved Sorcery (R1) [#2, Force 4]** | *CRB* 155<br>*SSWFAQ-0069* | **¥12,000**<br>+ 8 Karma | 1 Minor Action (Bond Focus) | Force 4 Qi Focus. Per official FAQ, Qi Foci stack: adds a second +1 die to Sorcery (combined with Wise Warrior +1 and Qi Focus #1 for **+3 total bonus**, pushing Spellcasting to **20 dice = 5 bought hits**). |
| **N5** | **Qi Focus: Improved Conjuring (R1) [#2, Force 4]** | *CRB* 155<br>*SSWFAQ-0069* | **¥12,000**<br>+ 8 Karma | 1 Minor Action (Bond Focus) | Force 4 Qi Focus. Adds a second +1 die to Conjuring (pushes pool to **17 dice**). |
| **N6** | **M-TOC Tactical Network Node** | *Firing Squad* 110 | **¥15,000–¥30,000** | None (Market Purchase) | *Deferred Backlog:* Team Edge storage bank and encrypted squad tactical coordination network. Deprioritized to bottom of queue as team deckers and riggers consistently deploy one. |

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
* **Covert Social Support:** *Stealth Effect* allows Velvet to establish *Wingman* or cast covert assistance in plain sight across a high-security boardroom without manifesting light flares or astral ripples. Noticing magic requires a Perception + Intuition (Mage's Magic rank) (*CRB*, p. 129).

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
  |  • Finesse Quality Anchor: Surgical execution, zero collateral damage, zero Heat.     |
  +---------------------------------------------------------------------------------------+
```

* **The Direct Combat Triad:** By standardizing on **Direct Combat** spells, Velvet never rolls against physical Armor soak. Every attack tests $\text{Sorcery} + \text{Magic}$ directly against mental attributes or object thresholds, neutralizing heavily armored cyber-commandos and drones with equal ease.
* **Stealth Effect Lethality:** Combined with *Stealth Effect* (Grade 5), Velvet can drop an entire room cold in Stun (*Stunball*), disintegrate an aerial surveillance drone (*Wreck*), or dissolve a hostile kill squad (*Manaball*) without a single sound, light flash, or projectile trajectory.
* **Ethical & Operational Flexibility:** Velvet defaults to *Stunball* to uphold the *Finesse* doctrine (surgical, non-lethal, zero Heat), reserving *Manaball* for existential combat where non-lethal methods are tactically impossible.

---

### C. Sustaining Expansion & Extended Masking Architecture

Active operational mode allocations, spirit channeling stats, and deterministic casting pools are dynamically maintained in [`rules_and_downtime.qmd`](file:///c:/GitHub/sr6-core/characters/velvet/rules/rules_and_downtime.qmd#sustained-spells--spirit-channeling-strategy). Two forward milestones expand and protect this sustaining envelope:

```text
               THE SOVEREIGN SUSTAINING & EXTENDED MASKING SHIELD
           [4-Spell Sustaining Array + Complete Astral Invisibility]

     FOCUSED CONCENTRATION R3                     EXTENDED MASKING (Grade 7)
    (3 Spells Sustained Free)                    (Street Wyrd 119 / SRMG 37)
  +-----------------------------+               +-----------------------------+
  | Slot 1: Increase Charisma   |               | • Masks personal aura       |
  | Slot 2: Increase Willpower  | ------------> | • EXTENDS MASKING TO ALL    |
  | Slot 3: Increase Reflexes   |               |   ACTIVE SUSTAINED SPELLS!  |
  +-----------------------------+               | • Result: Velvet appears    |
                 +                              |   100% mundane to assensing |
  +-----------------------------+               +-----------------------------+
  | SUSTAINING FOCUS: HEALTH R6 |                             ^
  | Slot 4: Dynamic / Wingman   | ----------------------------+
  +-----------------------------+
```

1. **4th Spell Slot Expansion via Sustaining Focus: Health R6 (Step N3):** Acquiring the Force 6 Sustaining Focus (¥24,000 / 12 Karma) unlocks a permanent **4th simultaneous sustained spell**, allowing Velvet to maintain *Increase Charisma* (+4), *Increase Willpower* (+4), and *Increase Reflexes* (+3 Rea / +3d6 Init) simultaneously while keeping a dedicated dynamic slot for *Wingman* or *Physical Barrier*.
2. **Astral Invisibility via Extended Masking (Step 7, Grade 7):** Standard Masking only hides the caster's personal aura and bonded foci. *Extended Masking* (*Street Wyrd*, p. 119; *SRMG*, pp. 37–38) extends this concealment across all active sustained spells. Adversary mages and patrol spirits assensing Velvet perceive only a completely mundane metahuman with zero active spell signatures.

---

### D. The Focus Bonding & Magic Ceiling Architecture

In SR6 (*City Edition: Seattle*, p. 154–155), focus bonding is governed by three canonical constraints:

1. **Focus Count Limit:** You cannot bond more foci than your **Magic attribute** (max 6 foci at Magic 6; max 8 at Magic 8).
2. **Individual Force Hard Cap:** *"No focus Force may exceed your magic Attribute"* (at Magic 6, **no single focus can exceed Force 6**; Force 8 requires Magic 8).
3. **Total Bonded Force Cap:** Total Force of all bonded foci cannot exceed **$\text{Magic} \times 5$** (30 Force at Magic 6; 40 Force at Magic 8).

Because *Sorcery* and *Conjuring* are classified as **Combat skills** under the *Shadowrun 6th Edition FAQ*, *Improved Ability* costs **1.0 PP per rank** ($\text{Force} = 4 \times \text{PP}$). Therefore, Rating 1 is **Force 4**, while Rating 2 is **Force 8**.

Per official FAQ `SSWFAQ-0069`, **Qi Foci stack**. Velvet establishes dual Force 4 Qi Foci for both Sorcery and Conjuring at Magic 6, and upgrades to Force 8 Qi Foci at Magic 8 to cap both skills at the **+4 Augmented Maximum**:

```text
       MAGIC 6 (30 FORCE CAP, MAX 6 FOCI)             MAGIC 8 (40 FORCE CAP, MAX 8 FOCI)
  +-------------------------------------------+  +-------------------------------------------+
  | Power Focus R3                     [3 F]  |  | Power Focus R3                     [3 F]  |
  | Qi Focus: Imp Conjuring R1 (#1)    [4 F]  |  | Qi Focus: Imp Conjuring R2 (#1)    [8 F]  |
  | Qi Focus: Imp Conjuring R1 (#2)    [4 F]  |  | Qi Focus: Imp Conjuring R2 (#2)    [8 F]  |
  | Qi Focus: Imp Sorcery R1 (#1)      [4 F]  |  | Qi Focus: Imp Sorcery R2           [8 F]  |
  | Qi Focus: Imp Sorcery R1 (#2)      [4 F]  |  | Qi Focus: Imp Sorcery R1           [4 F]  |
  | Sustaining Focus: Health R6        [6 F]  |  | Sustaining Focus: Health R6        [6 F]  |
  +-------------------------------------------+  +-------------------------------------------+
  | • 6 Foci Bonded (Max Count: 6)            |  | • 6 Foci Bonded (Under Max Count: 8)      |
  | • Total Force: 25 / 30 (5 Force Headroom) |  | • Total Force: 37 / 40 (3 Force Headroom) |
  | • Sorcery Boost: +3 dice (w/ Wise Warrior)|  | • Sorcery Boost: +4 dice (AUGMENTED CAP)  |
  | • Conjuring Boost: +2 dice (17d pool)     |  | • Conjuring Boost: +4 dice (AUGMENTED CAP)|
  +-------------------------------------------+  +-------------------------------------------+
```

* **Magic 6 Architecture (Operational Suite):**
  * **Foci Breakdown:** Power Focus R3 (3F) + two Qi Focus: Imp Conjuring R1 (4F + 4F) + two Qi Focus: Imp Sorcery R1 (4F + 4F) + Sustaining Focus: Health R6 (6F).
  * **Focus Count:** Exactly 6 foci bonded $\le 6$ Magic limit.
  * **Total Force:** $3 + 4 + 4 + 4 + 4 + 6 = \mathbf{25\text{ Force}} \le 30$ Force cap (5 Force headroom!).
  * **Individual Force:** Every focus is Force 3, 4, or 6 $\le 6$ Magic limit (Sustaining Focus R6 fits the exact Magic 6 cap!).
  * **Availability:** All 6 foci are $\le 6\text{L}$ (**Availability 4L and 6L**), allowing **100% off-the-shelf downtime acquisitions with zero availability rolls!**
  * **Pool Impact:** Conjuring operates at **17 dice** (comfortably above the 16d / 4 bought hits cutoff); Spellcasting operates at **19–20 dice** (5 bought hits deterministically).
  * **Sustaining Capacity:** Force 6 Sustaining Focus can sustain *Increase Attribute* at the maximum **+4 bonus** (base DV 3 + 3 net hits = DV 6; sustained spell DV cannot exceed focus Force per *CRB* 155), completely freeing a *Focused Concentration* slot for *Wingman*.
* **Magic 8 Architecture (Apex +4 Capped Suite):**
  * **Foci Upgrades:**
    * Conjuring: Both Force 4 Qi Foci are upgraded to **Force 8** ($2\text{ PP} \times 4$), delivering $2 + 2 = \mathbf{+4\text{ dice}}$ (**Maximum Augmented Skill Cap**).
    * Sorcery: One Force 4 Qi Focus is upgraded to **Force 8** (+2 dice), while the second remains at **Force 4** (+1 die). Combined with *Wise Warrior* (+1 free), Sorcery delivers $1 + 2 + 1 = \mathbf{+4\text{ dice}}$ (**Maximum Augmented Skill Cap**).
  * **Focus Count:** 6 foci bonded $\le 8$ Magic limit (2 open slots remaining for talismans).
  * **Total Force:** $3 + 8 + 8 + 8 + 4 + 6 = \mathbf{37\text{ Force}} \le 40$ Force cap (3 Force headroom!).
  * **Individual Force:** Highest focus is Force 8 $\le 8$ Magic limit.
