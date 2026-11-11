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
     * *Zero Footprint Protocol:* **`Sterilize`** (*Street Wyrd*, p. 56).
     * *Deferred Flavor & Cosmetic Utility Backlog:* **`Charm`** (*CRB*, p. 138) and **`Fashion`** (*Street Wyrd*, p. 48) (deprioritized due to natural 19–24d social pools and *Cosmetic Control 2*).
  4. **Spirit Binding & Re-Binding (Minor Action):** Bind Fire or Air spirits up to the Magic $\times$ 3 Force cap (18 Force at Magic 6).

---

## 2. Master Unified Progression Queue

All upcoming upgrades are prioritized sequentially below. When logging post-mission downtime, advance the next available item in this table according to banked Karma, liquid Nuyen, and available action slots.

### A. Karma Progression Pipeline (Ontological & Metamagic Scaling)

*(Current Baseline: Initiation Grade 5 [Channeling, Centering, Masking, Stealth Effect, Power Point], Magic 6, Power Focus R3, Mentor Spirit Wise Warrior, 2 Karma banked after Session 9, Finesse negative quality active).*

<!-- TODO: Add Attribute Mastery: Charisma (DC 168) -->

| Step | Target Upgrade | Category | Cost | Downtime Action Required | Primary Tactical & Architectural Role |
| :---: | :--- | :--- | :---: | :---: | :--- |
| **01** | **Sorcery Specialization**<br>• *Spellcasting* | Active Skill | 5 Karma | None (Between runs) | *CRB* 69: Adds **+2 dice** to all Spellcasting tests (raises Spellcasting pool from **15d6 $\rightarrow$ 17d6**). Top priority to restore combat sorcery precision after accelerating Grade 5 initiation. |
| **02** | **Tactical Defense: Physical Barrier** | Manipulation (Area) | 5 Karma | 1 Minor Action (Study) | *CRB* 141: LOS(A), Sustained, Drain 6. Translucent barrier (Structure = Magic + net hits) providing mobile ballistic cover, barricading hallways, and stopping vehicle ramming. |
| **03** | **Initiation Grade 6**<br>• *The Magician's Way* | Metamagic | 12 Karma* | 1 Major Action<br>*(Mainline SRM)* | *Street Wyrd* 76: Cost $10+6-4=12\text{K}$ at **Loyalty 4 floor**. Apex capstone at Magic 6. Unlocks dual mentor spirit benefits for *Wise Warrior* (Adept combat sorcery bonus + **-1 Edge cost discount on Combat category spells/rituals**) and Adept drain resistance using $\text{Body} + \text{Charisma}$ (14+ dice). |
| **04** | **Spell: Stunball** | Direct Combat (Area) | 5 Karma | 1 Minor Action (Study) | *CRB* 134: LOS(A), DV 4, Stun. Non-lethal AoE that **completely bypasses armor** ($\text{Sorcery} + \text{Magic}$ vs $\text{Willpower} + \text{Intuition}$). Immediately activates *Wise Warrior*’s -1 Edge discount on Combat spells. |
| **05** | **Spell: Wingman** | Detection Spell | 5 Karma | 1 Minor Action (Study) | *Smooth Operations* 110: Specialized sustained Mindlink for social teamwork. Helper gets 1 temporary Edge on assistance; leader gains 1 temporary Edge for *each* die provided (19–24d). Solves the "two faces at the table" dilemma by turning Velvet into an unbeatable cooperative Edge battery. Sustained via *Focused Concentration*. |
| **06** | **Spell: Wreck (Drones)** | Direct Combat (LOS) | 5 Karma | 1 Minor Action (Study) | *Street Wyrd* 27: LOS, DV 4, Object destruction. Directly bypasses drone armor to destroy chassis/optics. Classified as a **Direct Combat** spell, so it reaps the *Wise Warrior* -1 Edge boost discount. |
| **07** | **Spell: Manaball** | Direct Combat (Area) | 5 Karma | 1 Minor Action (Study) | *CRB* 133: LOS(A), DV 5, Physical. Silent, lethal direct mana destruction that **completely bypasses armor**. Deployed against hardened combat teams, cybered hit squads, or hostile spirits when stun is insufficient. Reaps *Wise Warrior* -1 Edge discount. |
| **08** | **Quality: Charismatic Defense** | Positive Quality | 24 Karma<br>*(2x 12K)* | None (Between runs) | *Power Plays* 85: Bases Defense Rating off Charisma instead of Body! DR leaps from 2 $\rightarrow$ **10 (unarmored) / 14 (buffed) / 18–22 (armored)**. Generates defensive Edge against almost all incoming gunfire ("too damn pretty to shoot!"). Prioritized before attribute tax. |
| **09** | **Untrained Skill Repair**<br>• *Perception 1 (Intuition)*<br>• *Astral 1 (Intuition)* | Active Skills | 10 Karma tot<br>*(5K each)* | None (Between runs) | Removes -1 untrained penalty (+2 dice swing each; Perception 3d $\rightarrow$ 5d, Astral 3d $\rightarrow$ 5d). Essential for spotting physical ambushes and reading emotional auras. |
| **10** | **Tactical Sabotage: Sterilize** | Manipulation (Area) | 5 Karma | 1 Minor Action (Study) | *Street Wyrd* 56: Complete forensic DNA, biometric, and physical evidence cleansing. Eliminates material crime scene traces. |
| **11** | **Attribute: Magic 6 $\rightarrow$ 7** | Attribute | 35 Karma | None (Between runs) | Unlocks Initiate Grades 7+, expands Focus Bonding Cap from 30 $\rightarrow$ **35 Force**, and raises safe spirit summoning threshold to Force 6. |
| **12** | **Initiation Grade 7**<br>• *Extended Masking* | Metamagic | 13 Karma* | 1 Major Action<br>*(Mainline SRM)* | *Street Wyrd* 119 / *SRMG* 37–38: Cost $10+7-4=13\text{K}$ at **Loyalty 4 floor**. **Prerequisite: Masking**. Crucial stealth capstone. Extends aura masking to cover all sustained spells (*Increase Charisma*, *Increase Reflexes*, *Wingman*). Adversary mages and astral security assensing Velvet see only a completely mundane metahuman with zero active magic! |
| **13** | **Attribute: Magic 7 $\rightarrow$ 8** | Attribute | 40 Karma | None (Between runs) | Expands Individual Focus Force limit to **Force 8** and total cap to **40 Force** ($\text{Magic } 8 \times 5$). Unlocks upgrading 1 Sorcery focus (Force 4 $\rightarrow$ 8) and both Conjuring foci (Force 4 $\rightarrow$ 8 each), bringing **both Sorcery and Conjuring to the maximum +4 Augmented Skill Cap** (37 / 40 Force total across 6 foci, with Sustaining Focus R6). |
| **14** | **Initiation Grade 8**<br>• *Flexible Signature* | Metamagic | 14 Karma* | 1 Major Action<br>*(Mainline SRM)* | *CRB* 165: Cost $10+8-4=14\text{K}$ at **Loyalty 4 floor**. Enables altering or completely erasing astral signatures from instantaneous spellcasting within turns equal to Initiate Grade (8 turns). Completes the astral ghost footprint. |
| **15** | **Quality: Teamwork Makes Dream Work** | Positive Quality | 12 Karma<br>*(2x 6K)* | None (Between runs) | *Hack & Slash* 83: Extends social teamwork bonuses to all party members, multiplying Edge generation when paired with *Wingman*. |

*\*Initiation cost formula at Loyalty 6: $10 + \text{Grade} - 6$; at Loyalty 4 floor: $10 + \text{Grade} - 4$.*

#### Tactical Note on Debuff Spells vs. Direct Combat

* *Decrease Attribute (Willpower / Intuition):* While tempting to erode defender resistance against *Stunball* or *Manaball*, *Decrease Attribute* (*CRB*, p. 136) has severe mechanical constraints: **Range Touch**, **Sustained duration** (competing for one of Velvet's 3 Focused Concentration slots), and zero effect on Object Resistance. In contrast, Velvet's high Sorcery pool (17–19d6, reaching 21+ with Qi Focus) combined with *The Magician's Way* Edge discounts makes direct offensive casting faster, cleaner, and far more lethal from long range without burning sustaining overhead.

#### Deferred Backlog ("Nice-to-Have Flavor & Cosmetic Utility")

* **Spell: Charm** (*CRB*, p. 138; 5 Karma) — Manipulation spell granting +4 dice to social tests. Deprioritized because Velvet already operates with natural 19–24d social pools (buying 4–5 hits routinely); +4 extra dice is win-more overkill.
* **Spell: Fashion** (*Street Wyrd*, p. 48; 5 Karma) — Instant clothing transformation. Deprioritized because *Cosmetic Control 2* already handles biological shape/gender/height alteration, while physical nanopaste disguise kits and high-fashion modular wardrobes cover cosmetic apparel.

---

### B. Nuyen & Foci Progression Pipeline

*(Current Baseline: Power Focus Rating 3 bonded, ¥22,915 liquid nuyen after Session 9).*

| Step | Target Hardware / Focus Upgrade | Source / Book | Cost | Downtime Action Required | Capacity & Tactical Role |
| :---: | :--- | :--- | :--- | :---: | :--- |
| **H1** | **Qi Focus: Improved Conjuring (R1)** | *CRB* 146, 155<br>*GMP* 12 | ¥12,000 + 8 Karma | Minor Action (Bond Focus) | Force 4 Qi Focus ($4 \times 1.0\text{ PP}$; Conjuring is a Combat skill per SR6 FAQ). **#1 Hardware Priority:** Pushes Conjuring from 15 $\rightarrow$ **16 dice**, unlocking the **4 bought hits threshold** ($16 \div 4 = 4$ hits). Under *CRB* p. 146, spirits resist with $\text{Force} \times 2$; under *SRM GM Primer* p. 12, spirits with $\text{Force} > \text{Magic} - 2$ (Force 5+ at Magic 6) spend Edge to reroll the summoner's successes. Against standard **Force 4 spirits** (8 resistance dice, buying 2 hits), 4 bought hits guarantees **2 net tasks** (up from 1 task at 15d) with **zero drain risk** (4 Drain soaked by 16 Drain dice). **Avail 4L** (instant buy). Fits Magic 6 cap ($4 \le 6$). Ready as soon as 4 more Karma is banked (¥22,915 liquid nuyen on hand!). |
| **H2** | **Qi Focus: Improved Sorcery (R1)** | *CRB* 155, 294<br>*SSW FAQ* | ¥12,000 + 8 Karma | Minor Action (Bond Focus) | Force 4 Qi Focus ($4 \times 1.0\text{ PP}$; Sorcery is a Combat skill per SR6 FAQ). Adds **+1 die to Sorcery**, stacking with Wise Warrior (+1) for **+2 total bonus** (pushes Spellcasting baseline from 18 $\rightarrow$ **19 dice**). **Avail 4L** (instant downtime buy). Fits within Magic 6 individual Force cap ($4 \le 6$). |
| **H3** | **Sustaining Focus: Health (R6)** | *CRB* 137, 155, 294 | ¥24,000 + 12 Karma | Minor Action (Bond Focus) | Force 6 Focus (**Avail 6L**; $6 \times ¥4,000$, $6 \times 2\text{ Karma}$). Required to sustain *Increase Attribute* at the maximum **+4 bonus** (base DV 3 + 3 net hits = DV 6; sustained spell DV cannot exceed focus Force per *CRB* 155). Frees a *Focused Concentration* slot for *Wingman*. Fits within Magic 6 individual Force cap ($6 \le 6$). |
| **H4** | **Qi Focus: Improved Sorcery (R1) [#2]** | *CRB* 155<br>*SSWFAQ-0069* | ¥12,000 + 8 Karma | Minor Action (Bond Focus) | Force 4 Qi Focus. Per official FAQ, Qi Foci stack: adds a second +1 die to Sorcery (combined with Wise Warrior +1 and Qi Focus #1 for **+3 total bonus**, pushing Spellcasting to **20 dice = 5 bought hits**). |
| **H5** | **Qi Focus: Improved Conjuring (R1) [#2]** | *CRB* 155<br>*SSWFAQ-0069* | ¥12,000 + 8 Karma | Minor Action (Bond Focus) | Force 4 Qi Focus. Adds a second +1 die to Conjuring (pushes pool to **17 dice**). |
| **H6** | **M-TOC Tactical Network Node** | *Firing Squad* 110 | ¥15,000–¥30,000 | None (Market Purchase) | *Deferred Backlog:* Team Edge storage bank and encrypted squad tactical coordination network. Deprioritized to bottom of queue as team deckers and riggers consistently deploy one. |

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
* **Covert Social Support:** *Stealth Effect* allows Velvet to establish *Wingman* or cast covert assistance in plain sight across a high-security boardroom without manifesting light flares or astral ripples. Noticing magic requires a Perception + Intuition (Mage's Magic rank)(CRB 129).

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

1. **4th Spell Slot Expansion via Sustaining Focus: Health R6 (Step H3):** Acquiring the Force 6 Sustaining Focus (¥24,000 / 12 Karma) unlocks a permanent **4th simultaneous sustained spell**, allowing Velvet to maintain *Increase Charisma* (+4), *Increase Willpower* (+4), and *Increase Reflexes* (+3 Rea / +3d6 Init) simultaneously while keeping a dedicated dynamic slot for *Wingman* or *Physical Barrier*.
2. **Astral Invisibility via Extended Masking (Step 10, Grade 7):** Standard Masking only hides the caster's personal aura and bonded foci. *Extended Masking* (*Street Wyrd*, p. 119; *SRMG*, pp. 37–38) extends this concealment across all active sustained spells. Adversary mages and patrol spirits assensing Velvet perceive only a completely mundane metahuman with zero active spell signatures.

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
