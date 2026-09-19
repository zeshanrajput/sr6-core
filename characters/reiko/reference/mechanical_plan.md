# Character Advancement & Mechanical Plan: Reiko

This document tracks character upgrades, mechanical evaluations, karma/nuyen targets, and downtime action logistics for **Reiko Takahashi (Yuriko Star)**.

*(Note: Internal reference document; not published in the Quarto narrative book).*

---

## 1. Executive Summary & Dynamic Baseline

* **Resource Ledgers:** Live Karma, Nuyen, and Lifetime totals are dynamically tracked in the Markdown Trio ([character_log.qmd](file:///c:/GitHub/sr6-core/characters/reiko/core/character_log.qmd), [character_purchases.qmd](file:///c:/GitHub/sr6-core/characters/reiko/core/character_purchases.qmd), [character_build.qmd](file:///c:/GitHub/sr6-core/characters/reiko/core/character_build.qmd)) and compiled into `reiko_master.yaml`. Snapshot numbers in reference documents must never hardcode drifting totals.
* **Resonance & Spark:** Resonance 8 | Essence / Spark: 6.00 (Uncompromised). Avoid codemods that cause Spark loss or risk AI Fragmentation.
* **Living Persona Baseline:** ASDF 7 / 9 / 7 / 9 | Full Defense: 34d6
* **Active Ally Sprite:** Taz (Level 7 Assassin Sprite; Symbiosis: Cracking +4, Electronics +4, Influence +4 [dynamically clamped to Reiko's underlying skill rating; currently +1; Con +4 planned]).
* **Resource Economics:** **Karma is the most constrained resource.** Where possible, knowledge skills and utility functions should be acquired via Nuyen (Rating 3 Knowsofts @ ¥2,500 each or programmed autosofts) rather than burning raw Karma.
* **Immediate Strategic Focus:**
  1. *Karma:* Bank through the next mission to unlock **Tasking Spec: Compiling** (5 Karma; pushes compiling pool to 16d6 unassisted / 19d6 with foci/symbiosis for safe Rating 7–8 sprite compiling).
  2. *Nuyen:* Prioritize the **Hydrocarbon Fuel Converter** (¥7,500) over the empty cyberarm chassis for off-grid survival power and social masquerade.

---

## 2. Master Priority Upgrade Matrix

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│ STEP 0: ZERO-WAIT & HIGH-LEVERAGE (Immediate Pool / 0–5 Karma / Low Nuyen)  │
├────────────────────────────────┬──────────────┬──────────────┬──────────────┤
│ Upgrade Item                   │ Type         │ Cost         │ Primary Role │
├────────────────────────────────┼──────────────┼──────────────┼──────────────┤
│ Taz Symbiosis: Influence       │ Ally Sprite  │ 4 Karma      │ [ACQUIRED]   │
│                                │ Upgrade      │              │ Teamwork +4* │
│ Complex Form: Enlighten Autom. │ Complex Form │ 5 Karma      │ [ACQUIRED]   │
│                                │              │              │ Drone/Hull +2│
│ Hydrocarbon Fuel Converter     │ Anthrodrone  │ ¥7,500       │ [ACQUIRED]   │
│                                │ Powertrain   │              │ Off-Grid Pwr │
│ Knowsoft: Japanese Cultural Et.│ Knowsoft R3  │ ¥2,500       │ [ACQUIRED]   │
│                                │              │              │ Corp/Salon   │
│ Knowsoft: New Orleans Vodou    │ Knowsoft R3  │ ¥2,500       │ [ACQUIRED]   │
│                                │              │              │ Loa/Veve/Nous│
│ Tasking Spec: Compiling        │ Specializ.   │ 5 Karma      │ [ACTIVE TGT] │
│                                │              │              │ Safe R7-8 Spr│
│ Knowsoft: Garmonbozia          │ Knowsoft R3  │ ¥2,500       │ [NEXT KNOWSFT│
│                                │              │              │ E-Nation Lore│
├────────────────────────────────┴──────────────┴──────────────┴──────────────┤
│ STEP 1: CORE MATRIX & SOCIAL SPECIALIZATIONS (5–10 Karma)                   │
├────────────────────────────────┬──────────────┬──────────────┬──────────────┤
│ Electronics Spec: Complex Forms│ Specializ.   │ 5 Karma      │ Threading &  │
│                                │              │              │ Sustaining   │
│ Electronics Spec: Computers    │ Specializ.   │ 5 Karma      │ Matrix Perc. │
│                                │              │              │ & Search     │
│ Influence Spec: Etiquette      │ Specializ.   │ 5 Karma      │ Corp & Salon │
│                                │              │              │ Wheelhouse   │
│ Influence Spec: Negotiation    │ Specializ.   │ 5 Karma      │ Johnson Fees │
│                                │              │              │ & Contracts  │
│ Con Spec: Disguise             │ Specializ.   │ 5 Karma      │ Sprawl Mask  │
│                                │              │              │ "Not a Weapon│
├────────────────────────────────┴──────────────┴──────────────┴──────────────┤
│ STEP 2: TACTICAL EXPANSION & RIGGING SYNERGY (10–25 Karma)                   │
├────────────────────────────────┬──────────────┬──────────────┬──────────────┤
│ Influence Rank 1 -> 2          │ Active Skill │ 10 Karma     │ +2 Net Dice  │
│                                │              │              │ (Uncaps Taz) │
│ Complex Form: Enhance Autosoft │ Complex Form │ 5 Karma      │ Drone Fleet  │
│ Focused Concentration (Rat. 1) │ Quality      │ 24 Karma     │ Sustain CFs  │
│ Taz Symbiosis: Con             │ Ally Sprite  │ 4 Karma      │ Teamwork +4* │
│                                │ Upgrade      │              │ (Clamped +1) │
│ Con Rank 1 -> 2                │ Active Skill │ 10 Karma     │ +2 Net Dice  │
│                                │              │              │ (Uncaps Taz) │
│ Influence Rank 2 -> 3          │ Active Skill │ 15 Karma     │ 12d6 Spec.   │
│ Con Rank 2 -> 3                │ Active Skill │ 15 Karma     │ 12d6 Disguise│
│ Charisma 4 -> 5                │ Attribute    │ 25 Karma     │ Social & Comp│
├────────────────────────────────┴──────────────┴──────────────┴──────────────┤
│ STEP 3: IMMUNE SYSTEM HARDWARE & CAPSTONES (Downtime Nuyen / 40+ Karma)      │
├────────────────────────────────┬──────────────┬──────────────┬──────────────┤
│ Second Cyberarm (Left, Used)   │ Anthrodrone  │ ¥10,000      │ Preps Hive   │
│ Nanohive Rating 6 (Used)       │ Anthrodrone  │ ¥45,000      │ "Leukocyte"  │
│                                │              │              │ Immune System│
│ Resonance 8 -> 9               │ Attribute    │ 45 Karma     │ Capstone     │
│ Resonance 9 -> 10              │ Attribute    │ 50 Karma     │ Capstone     │
└────────────────────────────────┴──────────────┴──────────────┴──────────────┘
*Logged as +4 in modifier ledger; ModifierEngine dynamically clamps teamwork bonus to Reiko's skill rating.
```

---

## 3. Deep Mechanical Evaluations & Rules Calibrations

### A. Taz Influence & Con Symbiosis Mechanics

* **Doubled Karma Upgrade Rule (*HnS* p. 156):** Adding a non-matrix skill to an existing Ally Sprite costs $2 \times 2 = \mathbf{4\text{ Karma}}$.
* **Automated Engine Teamwork Clamping (*Core*, p. 17):** Helpers cannot add more bonus dice than the leader’s base skill rank. Taz (Level 7) grants a declared modifier of $+4$ dice ($\lceil 7/2 \rceil$). The project's `ModifierEngine` automatically applies $\min(\text{Teamwork Bonus}, \text{Skill Rating})$ at test evaluation time:
  * **Influence Progression:**
    * *Rank 1 (Current):* 1 + 1 (Taz clamped) + 4 (CHA) = **6 dice general / 8 dice specialized** (Modifier logged as +4, clamped to +1 — **ACTIVE**)
    * *Rank 2:* 2 + 2 (Taz clamped) + 4 (CHA) = **8 dice general / 10 dice specialized** (Auto-evaluates to +2; Cost: 10 Karma)
    * *Rank 3:* 3 + 3 (Taz clamped) + 4 (CHA) = **10 dice general / 12 dice specialized** (Cost: 15 Karma)
    * *Rank 4:* 4 + 4 (Taz full) + 4 (CHA) = **12 dice general / 14 dice specialized** (Full +4 uncap achieved!)
  * **Con Progression (Post-Taz Con Upgrade):**
    * *Rank 1 Baseline:* 1 + 4 (CHA) = **5 dice general / 7 dice specialized (Disguise)**.
    * *Rank 1 + Taz Con (4 Karma):* 1 + 1 (Taz clamped) + 4 (CHA) = **6 dice general / 8 dice specialized (Disguise)**.
    * *Rank 2 (10 Karma):* 2 + 2 (Taz clamped) + 4 (CHA) = **8 dice general / 10 dice specialized (Disguise)** (Uncaps Taz to +2).
    * *Rank 3 (15 Karma):* 3 + 3 (Taz clamped) + 4 (CHA) = **10 dice general / 12 dice specialized (Disguise)** (Uncaps Taz to +3).
    * *Rank 4 (20 Karma):* 4 + 4 (Taz full) + 4 (CHA) = **12 dice general / 14 dice specialized (Disguise)** (Full +4 uncap!).
    * *(Note: At Charisma 5, all pools advance by +1 die: 9 / 11 / 13 dice specialized).*

### B. Natural Hacker & Intuition Defense

* With **Natural Hacker**, Matrix Perception is calculated as $\text{Electronics} + \text{Resonance}$, yielding **17–21 dice** regardless of Intuition. INT 2 remains a blindspot strictly for unassisted physical perception, which is offset via drone sensor suites and clearsight autosofts.

### C. Shiawase Man-at-Arms Anthrodrone Hardware Expansion & Staging

* **Hydrocarbon Fuel Converter [ACQUIRED]:**
  * Category: `[2 Powertrain Capacity]` (*Double Clutch*, p. 124).
  * Cost: 7,500¥ (Base Body 10 × 1,500¥ = 15,000¥; 50% self-install discount per *DC*, p. 120).
  * Placement & Function: Installed at the base of the anthrodrone's esophagus, linking oral chemoreceptors and digestive tract to the chassis auxiliary power cell.
  * Operational Value: 
    1. *Survival Power Generation:* Allows the chassis to run indefinitely on organic matter (food, alcohol, sugars, plant matter, standard hydrocarbon fuels) away from electrical charging grids. Reiko has repeatedly faced situations without grid power (submerged in Malta, lost in the bayous); this prevents operational stranding.
    2. *Masquerade Reinforcement:* Functionally converts social consumption (drinking with Johnsons or sipping tea with clients) into direct fuel rather than dumping inert fluid into a dead reservoir.
* **Second Cyberarm (Left, Used Synthetic Cyberarm — 8 Capacity):**
  * Cost: 10,000¥ (Base 20,000¥; 50% used).
  * Staging Rationale: An empty cyberarm provides minimal standalone value. Its primary role is to house the Nanohive Rating 6 without consuming primary torso capacity. Deferred until Reiko is ready to fund and seat the hive.
* **Nanohive Rating 6 (Used — 6 Capacity — The "Leukocyte" Immune System):**
  * Cost: 45,000¥ (Base 90,000¥; 50% used).
  * Narrative Alignment (*25 DelTree*): Following her acute nanite contamination in the bayou and Nagai’s gift of the boxwood token, the nanohive functions as Reiko's physical immune system—cultivating autonomous hunter nanites ("white blood cells") that isolate, dissolve, and delete foreign microscopic machines and biological/chemical rot before they breach her titanium core.

### D. Social & Disguise Calibrations (Con & Influence)

* **Con (Disguise Specialization & The Masquerade of Trust):**
  * In *26 SIGTSTP*, Reiko decided to stop faking *for her friends*—shutting down the autonomic breathing daemon and cervical micro-tremors in their presence. However, the Sixth World remains viciously prejudiced against autonomous machines, AI entities, and combat constructs (e.g. Humanis Policlub, paranoid security guards, trigger-happy police).
  * Walking the streets as an obvious 100-pound military-grade weapon platform invites panic and lethal corporate attention. Con (Disguise) and synthetic emulation remain **vital operational tools** to masquerade as "not a war machine" in public spaces, hotel lobbies, and social meets.
  * *Narrative Resonance:* Ceasing the masquerade becomes a profound, intimate sign of trust reserved exclusively for true allies and loved ones.
* **Influence (Etiquette & Negotiation Specializations):**
  * Shadowrun Missions embraces the **Expanded Specializations** rule (*6WC*, p. 145), allowing multiple specializations per skill.
  * **Etiquette Specialization (5 Karma):** Inherent to Reiko's core identity—governing formal Japanese corporate registers (*ojigi*, keigo honorifics) and Coffin Girls salon hospitality (*Chanoyu*).
  * **Negotiation Specialization (5 Karma):** Secures shadowrunner fee leverage, contract payouts, and Johnson bargaining without being shortchanged.

### E. Electronics Specializations (Complex Forms & Computers)

* Reiko already possesses **Electronics Spec: Software** from character creation.
* Under *6WC* Expanded Specializations, she can add further specializations directly:
  1. **Complex Forms (5 Karma):** Critical for her evolving technoshamanic loadout (Enlighten Automaton, Puppeteer, Cyber Spike, Resonance Wires, Diffusion). Boosts threading and sustaining tests.
  2. **Computers (5 Karma):** Maximizes Matrix Perception, deep Matrix Searches, and real-time Threat Analysis.

### F. Knowledge Skills & The Knowsoft Economy

* **Chargen Baseline (*CRB*, p. 66; *6WC*, p. 29):**
  Characters receive free Knowledge skills equal to their starting **Logic attribute (Logic 4)** plus one free Native Language. These represent Reiko’s foundational origin:
  1. **Resonance Realms:** Origin deep-matrix cartography, Nous currents, and fractal flora.
  2. **Kernel Panic:** The wild haven, un-allocated address space, and liberated sparks.
  3. **The Endless Archives:** Ancestral and corporate deep storage.
  4. **UNified Information TheorY (UnITy):** Emergence theology, mathematical dogma, and spiritual doctrine.
* **Active Slotted Knowsofts [ACQUIRED]:**
  Because Reiko natively runs autosofts, acquiring new knowledge as **Rating 3 Knowsofts for ¥2,500 each** preserves scarce Karma for active skills and Resonance:
  1. **Japanese Cultural Etiquette (Rating 3 Knowsoft):** [ACQUIRED] Neo-Tokyo corporate hierarchy, bowing registers (*ojigi*), keigo, and traditional tea hospitality (*Chanoyu*).
  2. **New Orleans Vodou & Loa Syncretism (Rating 3 Knowsoft):** [ACQUIRED] Deep literacy in Baron Samedi, the Loa of the Wires, League of Laveau, Zobop, and the theological intersection where Mana meets Nous.
* **Future Knowledge Targets:**
  1. **Garmonbozia (Rating 3 Knowsoft — ¥2,500):** Sovereign DI e-nation cartography and liberation networks.
  2. **Shiawase Drone Engineering & Casemodding:** Custom chassis repairs and rigging integrations.

---

## 4. Purchasing & Progression Timeline

| Step | Target Upgrade | Cost | Downtime Actions Needed | Funding Mechanism & Status |
| :---: | :--- | :--- | :--- | :--- |
| **01** | **Taz Symbiosis: Influence** | **4 Karma** | None (Post-mission training) | **ACQUIRED** (SRM 2083-14 Post-Mission) |
| **02** | **Complex Form: Enlighten Automaton** | **5 Karma** | 1 Major Action (Study) | **ACQUIRED** (SRM 2083-15 Post-Mission) |
| **03** | **Hydrocarbon Fuel Converter** | **¥7,500** | 1 Minor Action (Install) | **ACQUIRED** (Off-Grid Power & Ingestion Masquerade) |
| **04** | **Knowsoft: Japanese Cultural Etiquette (R3)** | **¥2,500** | None (Download) | **ACQUIRED** (Preserves Karma; Corp/Salon Etiquette) |
| **05** | **Knowsoft: New Orleans Vodou (R3)** | **¥2,500** | None (Download) | **ACQUIRED** (Preserves Karma; Loa/Veves/Nous) |
| **06** | **Tasking Spec: Compiling** | 5 Karma | None (Between runs) | **ACTIVE TARGET** (3/5 Karma Banked) |
| **07** | **Knowsoft: Garmonbozia (R3)** | ¥2,500 | None (Download) | Liquid Nuyen (Next Knowsoft Target; E-Nation Lore) |
| **08** | **Electronics Spec: Complex Forms** | 5 Karma | None (Between runs) | Banked Karma (Threading / Sustaining Form Buffs) |
| **09** | **Electronics Spec: Computers** | 5 Karma | None (Between runs) | Banked Karma (+2 Matrix Perception & Searches) |
| **10** | **Influence Spec: Etiquette** | 5 Karma | None (Between runs) | Banked Karma (Corporate Protocol & Salon Hospitality) |
| **11** | **Influence Spec: Negotiation** | 5 Karma | None (Between runs) | Banked Karma (Johnson Bargaining & Fee Leverage) |
| **12** | **Con Spec: Disguise** | 5 Karma | None (Between runs) | Banked Karma (Public Sprawl Masquerade "Not a Weapon") |
| **13** | **Influence Rank 1 $\rightarrow$ 2** | 10 Karma | None (Between runs) | Banked Karma (Uncaps Taz to +2 teamwork) |
| **14** | **Complex Form: Enhance Autosoft** | 5 Karma | 1 Minor Action (Study) | Banked Karma (Drone Fleet Buffing) |
| **15** | **Focused Concentration (Rating 1)** | 24 Karma | None (Between runs) | Banked Karma (Sustain Enlighten Automaton penalty-free) |
| **16** | **Taz Symbiosis: Con** | 4 Karma | None (Post-mission training) | Banked Karma (Taz assists with public posture/masquerade) |
| **17** | **Con Rank 1 $\rightarrow$ 2** | 10 Karma | None (Between runs) | Banked Karma (Uncaps Taz Con to +2; 10 dice Disguise) |
| **18** | **Second Cyberarm (Left, Used)** | ¥10,000 | 1 Minor Action (Install) | Liquid Nuyen (8 Cap dedicated for Nanohive) |
| **19** | **Nanohive Rating 6 (Used)** | ¥45,000 | 1 Minor Action (Install) | Mission Nuyen ("Leukocyte" Immune System) |
| **20** | **Influence Rank 2 $\rightarrow$ 3** | 15 Karma | None (Between runs) | Banked Karma (Uncaps Taz to +3 teamwork; 12d6 Spec) |
| **21** | **Con Rank 2 $\rightarrow$ 3** | 15 Karma | None (Between runs) | Banked Karma (Uncaps Taz to +3 teamwork; 12d6 Disguise) |
| **22** | **Charisma 4 $\rightarrow$ 5** | 25 Karma | None (Between runs) | Banked Karma (Social, Disguise, & Compiling Pools) |
| **23** | **Resonance 8 $\rightarrow$ 9** | 45 Karma | None (Between runs) | Banked Karma (Capstone Progression) |
| **24** | **Resonance 9 $\rightarrow$ 10** | 50 Karma | None (Between runs) | Banked Karma (Capstone Progression) |
