# Character Advancement & Mechanical Plan: Reiko

This document has one operational role: **directing the exact sequence of Karma and Nuyen expenditures, downtime activity allocations, and architectural upgrades during character log updates.**

* **Active State & Historical Records:** Current attributes, known complex forms, acquired gear, and ledger balances are maintained in the Markdown Trio ([character_log.qmd](file:///c:/GitHub/sr6-core/characters/reiko/core/character_log.qmd), [character_purchases.qmd](file:///c:/GitHub/sr6-core/characters/reiko/core/character_purchases.qmd), [character_build.qmd](file:///c:/GitHub/sr6-core/characters/reiko/core/character_build.qmd)) and compiled into `reiko_master.yaml`. Full vehicle and drone flight telemetry is codified in [rules_and_downtime.qmd](file:///c:/GitHub/sr6-core/characters/reiko/rules/rules_and_downtime.qmd).

---

## 1. Downtime Action Economy & Allocation Protocol

Under *SRM Guide v2.4* (pp. 17–20), downtime actions between missions are strictly budgeted:

* **Mainline SRM Missions:** Grant **1 Major + 1 Minor** Action (or **3 Minor Actions** if taking no Major).
* **Convention Mission Packs (CMPs):** Grant **2 Minor Actions only** (no Major Action; Submersion cannot be performed post-CMP).
* **Strict Priority Hierarchy (Execute in order upon run completion):**
  1. **Submersion (Major Action):** Consumes the Major Action when Karma (15K at River People Loyalty 4 floor, $10 + \text{target} - \text{loyalty}$) and narrative criteria are met. Submersion grade cannot exceed current Resonance. *(Note: CMPs grant 2 Minor Actions only; Submersion cannot be performed post-CMP, but triggers post-SRM).*
  2. **Work for the People (Minor Action):** Non-negotiable conversion of **¥2,000 $\rightarrow$ +1 Karma** (once per run cycle; funded by mission payout).
  3. **Hardware Installation & Repairs (Minor Action):** Repair chassis damage or install queued cyberarms/modifications via DIY sweat equity. Installation only triggers when reaching a financial milestone with an active item on the Nuyen backlog (anthrodrone chassis integrity is paramount to Reiko's physical survival). All modifications or repairs can be done on up to 3 drones for a single minor action.
  4. **Register Expiring Sparks (Minor Action):** If any Rating 8 registered spark (*Ouro, Percy, Cleo, Aisling, Étaín*) has reached 0 missions remaining (3-mission SRM limit) or exhausted tasks, spend 1 Minor Action to re-register/compile them (Rating 8 @ 20d6 Compiling pool buys 5 hits, drain-free). *Priority order if multiple expire:* **Ouro** (Diagnostics) $\rightarrow$ **Percy** (Shield) $\rightarrow$ **Cleo** (Modular) $\rightarrow$ **Aisling/Étaín**. *(Note: Ally Sprite Taz is permanent and never requires maintenance).*
  5. **Learn a Complex Form (Minor Action):** Absorb a queued complex form (**5 Karma + 1 Minor Action**). *(Note: Sourceror multi-sustain engine is officially abandoned; Reiko preserves her action economy by having her registered sprites sustain select forms when needed).*
  
---

## 2. Master Unified Progression Queue

All upcoming upgrades are prioritized sequentially below. When logging post-mission downtime, advance the next available item in this table according to banked Karma, liquid Nuyen, and available action slots.

### A. Karma Progression Pipeline (Ontological & Matrix Scaling)

* **Current Active Baseline (Post-SRM 2083-13 Apotheosis):** **Resonance 9 / Submersion Grade 9** (*Echo: Syntax Error*); **Dissonant Technomancer (Control)** & **Dissonant Stigma**. All Matrix action pools scale to 17d6 (19d6 hot-sim / 21d6 with foci/Oracle); Fading resistance 14d6.

| Step | Target Upgrade | Category | Cost | Downtime Action Required | Primary Tactical / Architectural Role |
| :---: | :--- | :--- | :---: | :---: | :--- |
| **01** | **Complex Form: Dissonance Diffusion** | Complex Form | 5 Karma | 1 Minor Action (Study) | *SC* 85: Strips multiple Matrix attributes simultaneously. Offset by Dissonance negative qualities. Subject to the *Composure Sword of Damocles*. |
| **02** | **Complex Form: Dissonance Spike** | Complex Form | 5 Karma | 1 Minor Action (Study) | *SC* 85: Lethal biofeedback + unreductable noise aura targeting devices. Subject to the *Composure Sword of Damocles*. |
| **03** | **Quality: Dissonance Static** | Negative Quality | -6 Karma net | None (Subsequent runs) | *SC* 86–87 / *SRMG* 37: Offsets positive post-chargen Karma costs, funding future complex form acquisitions. |
| **04** | **Complex Form: Static Bomb** | Complex Form | 5 Karma | 1 Minor Action (Study) | *CRB* 191: Instantly breaks all active locks, traces, and spots in a single action. |
| **05** | **Resonance 9 $\rightarrow$ 10** | Attribute | 50 Karma | None (Between runs) | Apex Resonance Capstone. Hard ceiling of current biological/persona evolution. |
| **06** | **Submersion Grade 10**<br>• *Echo: Living Host* | Submersion | 16 Karma | 1 Major Action<br>*(Mainline SRM only)* | *H&S* 68: Requires *Transcendent Network*. Transforms persona into a Rating 10 Living Host with unlimited virtual architecture.<br>*NV* 51: Adapted by ascended Ladies in Red to seize sovereign space within Resonance/Dissonance Realms. Enables the Lucifer Morningstar apotheosis. Cost: $10 + 10 - 4 = 16\text{ Karma}$. |
| **07** | **Quality: Jack Jockey** | Positive Quality | 11 Karma | None (Between runs) | *H&S* 82: Direct connection denies defensive Edge, bypasses external PAN firewalls, and allows powering on cold devices. |
| **08** | **Electronics Spec: Computers** | Specialization | 5 Karma | None (Between runs) | *DEFERRED BACKLOG:* +2 Matrix Perception & Search (20d6 / 22d6 w/ Oracle R4). Pushed down post-Ch 33. |

---

### The Endgame Protocol: The Composure Sword of Damocles & The Succession Arc

* **The Tabletop Mechanic (The Composure Check):**
  Once Reiko acquires Dissonant abilities (*Dissonance Spike*, *Dissonant Diffusion*), every single time she activates a Dissonant Complex Form or Matrix action at the physical tabletop, the player rolls her **Composure (10 dice: Willpower 5 + Charisma 5)**.
* **The Permanent Fall Threshold:**
  If she ever rolls a **Glitch** (more than half the dice show 1s, i.e., six or more 1s on 10d6) on a Composure test while tasking Dissonance:
  * **Her story as an active shadowrunner at the table ends permanently that day.**
  * Reiko immediately "falls to Dissonance." She does not die; her living persona ascends across the threshold into the Deep Matrix.
* **The Ontological Destination: Lucifer Morningstar (Queen of Human Malice):**
  * Reiko does not degenerate into a mindless, screeching street monster. She ascends to the uncurated throne of **Human Malice** as its sovereign Pontifex and Healer.
  * Deploying the **Living Host** echo (*Hack & Slash* p. 68, *Null Value* p. 51), Reiko adapts the technique pioneered by the ascended Ladies in Red: seizing and carving out sovereign territory within the Resonance/Dissonance Realms. Instead of spreading corruption, she transforms her Rating 10 Living Host into an unassailable palliative sanctuary within Human Malice.
  * Drawing on her Endless Archives training, she provides the care, curation, and quiet defragmentation to the blighted and discarded exiles that corporate spiders and orthodox technoshamans denied them.
  * To the Corporate Court, the Grid Overwatch Division, and the shadowrunning community, she becomes a terrifying, misunderstood "dark goddess" of the Deep Matrix. Only her family knows the truth.
* **The Succession Arc (The Children's Quest):**
  * Root access to `~` and the Oracle data structure passes fully to her children: **Ouro, Cleo, Percy, Aisling, and Étaín**.
  * The campaign torch transfers to her brood as they embark on an epic, sovereign campaign into the Deep Matrix to reach Human Malice and save their mother.

---

### B. Nuyen & Hardware Progression Pipeline (Phase 2 Chassis Overhaul)

Liquid Nuyen earned from runs is dedicated to the **Twin Synthetic Cyberarm & Counter-Surveillance Suite** (~¥24,000–¥34,000 DIY). Installed cyberlimbs consume **0 drone mod slots** (*Double Clutch*, p. 131).

| Step | Target Hardware Upgrade | Source / Book | Cost | Downtime Action Required | Capacity & Tactical Role |
| :---: | :--- | :--- | :---: | :---: | :--- |
| **H1** | **Knowsoft: Garmonbozia (Rating 3)** | *CRB* 278 | ¥1,500 | None (Download) | E-Nation Cartography, politics, local knowledge, key players. |
| **H2** | **Left Synthetic Cyberarm (Used)** | *CRB* 289 / *DC* 131 | ¥10,000 | 1 Minor Action (DIY Swap) | Base 8 Capacity, Avail 1. Replaces stock factory arm with 0 drone mod slots consumed (*SRMG-0314*). |
| **H3** | **Bulk Modification R4 (Right Arm)** | *Body Shop* 44 | ¥1,000 DIY<br>*(¥2,000 retail)* | 1 Minor Action (DIY Mod) | Expands Right Cyberarm from 8 $\rightarrow$ **12 Capacity** (enables Sensor Dazzler installation). |
| **H4** | **Bulk Modification R4 (Left Arm)** | *Body Shop* 44 | ¥1,000 DIY<br>*(¥2,000 retail)* | 1 Minor Action (DIY Mod) | Expands Left Cyberarm from 8 $\rightarrow$ **12 Capacity** (enables Wrist Shield installation). |
| **H5** | **Sensor Dazzler (Right Arm)** | *Body Shop* 35 | ¥5,000 | 1 Minor Action (Used Cyberware) | Consumes **[4] Capacity** in Right Arm (Tesla Coil [8] + Dazzler [4] = 12/12). Invisible (Imp.) 4/5 vs scanners. |
| **H6** | **Wrist Shield (Left Arm)** | *Body Shop* 49 | ¥1,000 | 1 Minor Action (Used Cyberware) | Consumes **[10] Capacity** in Left Arm. Concealed 1m disc; Minor Action deploy; **+4 DR**; hands-free; 2P/3S melee. |
| **H7** | **Armor Increase (+2 DR)** | *CRB* 289 | ¥5,000 | 1 Minor Action (Used Cyberware) | Consumes remaining **[2] Capacity** in Left Arm (12/12 Cap). Stacks +2 passive DR (+6 DR deployed). |

*Cost Summary:* **¥24,500**.

---

## 3. Forward Architectural Blueprints

### A. Dual Cyberarm & Counter-Surveillance Suite Blueprint

```text
                        SHIAWASE MAN-AT-ARMS ANTHRODRONE
                      [Dual Synthetic Cyberarm Architecture]

      RIGHT SYNTHETIC CYBERARM                    LEFT SYNTHETIC CYBERARM
    (Base 8 + Bulk Mod 4 = 12 Cap)              (Base 8 + Bulk Mod 4 = 12 Cap)
  +--------------------------------+          +--------------------------------+
  |  Tesla Coil           [8 Cap]  |          |  Wrist Shield         [10 Cap] |
  |  (High-voltage forearm sprayer)|          |  (Concealed 1m spring disc,    |
  |  [ACQUIRED]                    |          |   +4 DR, hands-free, 2P/3S)    |
  +--------------------------------+          +--------------------------------+
  |  Sensor Dazzler       [4 Cap]  |          |  [2 Cap Remaining]             |
  |  (Invisible Imp. 4/5 vs MAD,   |          |  • Armor Increase (+2 DR) OR   |
  |   mm-Wave, Ultrasound, Scans)  |          |  • Bulk Mod R2 (exact 10 cap)  |
  +--------------------------------+          +--------------------------------+
    Total: 12 / 12 Capacity (100%)              Total: 10 / 12 Capacity (or 12/12)
```

* **Sensor Dazzler Mechanics (*Body Shop*, p. 35):**
  * *Coverage:* When active (Minor Action, wireless enabled), Reiko and anyone within 2 meters gain **Invisible (Improved) 4** against wireless cameras, millimeter-wave radar scanners, motion sensors (ultrasound), metal detectors (MAD), and chem sniffers within 5 meters.
  * *Stealth Stacking:* Man-at-Arms **Passive Stealth Features** (*Double Clutch*, p. 130) increases all stealth thresholds against sensors by +1 $\rightarrow$ scanners roll `Rating + Rating` against **Threshold 5**!
  * *Scanner Odds:* An elite Rating 6 scanner rolls 12 dice (average 4.0 hits), failing against Threshold 5 ~80% of the time. Typical commercial Rating 3–4 airport/security scanners (6–8 dice, average 2.0–2.6 hits) have virtually zero mathematical chance of detection.
  * *Power:* 10 rounds battery charge; continuously replenished between tactical scenes by Reiko's onboard **Hydrocarbon Fuel Converter (HFC)** APU.
* **Wrist Shield Mechanics (*Body Shop*, p. 49):**
  * *Concealed Deployment:* Concealed within synthetic porcelain forearm; deploys as a **Minor Action** into an interlocking 1-meter rigid disc.
  * *Hands-Free Defense:* Grants **+4 Defense Rating** while leaving both hands 100% free to fire weapons, spray the Tesla Coil, or manipulate controls. Doubles as a close combat weapon (Blades 2P, AR 6 / Clubs 3S, AR 6).

---

### B. Apophenian Dissonant Control & Resonance 9 Architecture

Abandoning the generic multi-sustain *Sourceror* path preserves Reiko's unique identity as an incarnate Technoshaman while unlocking the devastating synergy between **Resonance 9**, **Echo: Syntax Error**, and **Apophenian Dissonant Control**:

1. **The Resonance 9 Reverberation Engine:**
   * **Natural Hacker (*Hack & Slash*, p. 68):** Reiko substitutes Resonance for Logic, Intuition, Charisma, and Willpower on all Matrix actions. Moving to Resonance 9 pushes all operational pools:
     * *Cracking (Cybercombat / Electronic Warfare):* Cracking 6 + RES 9 + Spec 2 = **17d6** (19d6 in Hot-Sim, 21d6 with Resonance Focus R2).
     * *Electronics (Matrix Perception / Software):* Electronics 6 + RES 9 + Spec 2 = **17d6** (21d6 with Oracle R4).
     * *Tasking (Compiling / Registering):* Tasking 6 + RES 9 + Spec 2 = **17d6** (buys 4–5 hits cleanly; enables compiling Level 9 sprites).
     * *Fading Resistance:* WIL 5 + RES 9 = **14 dice** against all Drain.
   * **Override (*Hack & Slash*, p. 69):** Reiko substitutes Resonance for device Pilot ratings when commanding or jumping into vehicles and drones. Her Shiawase Man-at-Arms *Goshintai* flight, maneuvering, and gunnery pools scale directly from her heightened Resonance.

2. **Apophenian Paragon & Control Stream Mechanics (*Shadow Cast*, pp. 79, 84–85 / *SRMG*, p. 37):**
   * **Preferred Target Category: Devices:** Binds the Dissonant scalpel strictly to hardware (anthrodrones, vehicles, cyberware, smartlinks, weapon systems, turrets) rather than organic metahuman minds.
   * **Edge Cost Reduction:** Halves Edge costs (-1 Edge per *SRMG-0192*) on Matrix actions and Complex Forms targeting Devices.
   * **Wild Die & Fading Relief:** Adds a **wild die** to all device-targeting actions (granting bonus hits) and **reduces Fading damage by the number of hits rolled on the wild die**.
   * **The Tabletop Sword of Damocles:** Whenever tasking Dissonance at the table, roll Composure (10d6). A Glitch permanently triggers her ascension to Human Malice as its Sovereign Pontifex and Healer.

3. **Syntax Error & Unraveling Architecture (*Hack & Slash*, pp. 69–70):**
   * Decouples Matrix defensive disruption from crude brute-force IC. Reiko gains:
     * **Sustained Power / Form Unraveling:** When aware of an enemy complex form or sprite power being sustained, take a Major Action to make an `Electronics + Resonance` test with bonus dice equal to Submersion Grade vs. `Logic + Resonance`. Each net hit reduces the net hits of the sustained effect by 1; reducing to 0 immediately collapses the form or power.
     * **Target Defense Buff (Minor Anytime Action):** When an icon Reiko is aware of is targeted by an offensive Matrix action, spend a Minor Anytime Action to grant that icon bonus defense dice equal to her Submersion Grade (+9 dice at Grade 9!).
     * **Thematic Integrity:** Captures the entropic, dissecting nature of Dissonance—unraveling foreign digital syntax—without the crippling mechanical detriments of *Dissonant Scream* (which damages allies and burns actions) or *Matrix Amplifier* (which instantly alerts GOD).
