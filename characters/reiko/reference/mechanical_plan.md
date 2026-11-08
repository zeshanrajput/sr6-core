# Character Advancement & Mechanical Plan: Reiko

This document has one operational role: **directing the exact sequence of Karma and Nuyen expenditures, downtime activity allocations, and architectural upgrades during character log updates.**

* **Active State & Historical Records:** Current attributes, known complex forms, acquired gear, and ledger balances are maintained in the Markdown Trio ([character_log.qmd](file:///c:/GitHub/sr6-core/characters/reiko/core/character_log.qmd), [character_purchases.qmd](file:///c:/GitHub/sr6-core/characters/reiko/core/character_purchases.qmd), [character_build.qmd](file:///c:/GitHub/sr6-core/characters/reiko/core/character_build.qmd)) and compiled into `reiko_master.yaml`. Full vehicle and drone flight telemetry is codified in [rules_and_downtime.qmd](file:///c:/GitHub/sr6-core/characters/reiko/rules/rules_and_downtime.qmd).

---

## 1. Downtime Action Economy & Allocation Protocol

Under *SRM Guide v2.4* (pp. 17–20), downtime actions between missions are strictly budgeted:

* **Mainline SRM Missions:** Grant **1 Major + 1 Minor** Action (or **3 Minor Actions** if taking no Major).
* **Convention Mission Packs (CMPs):** Grant **2 Minor Actions only** (no Major Action; Submersion cannot be performed post-CMP).
* **Strict Priority Hierarchy (Execute in order upon run completion):**
  1. **Submersion (Major Action):** Consumes the Major Action when Karma (19K) and narrative criteria are met. Submersion grade cannot exceed current Resonance.
  2. **Work for the People (Minor Action):** Non-negotiable conversion of **¥2,000 $\rightarrow$ +1 Karma** (once per run cycle; funded by mission payout).
  3. **Hardware Installation & Repairs (Minor Action):** Repair chassis damage or install queued cyberarms/modifications via DIY sweat equity. Installation only triggers when reaching a financial milestone with an active item on the Nuyen backlog (anthrodrone chassis integrity is paramount to Reiko's physical survival). All modifications or repairs can be done on up to 3 drones for a single minor action.
  4. **Register Expiring Sparks (Minor Action):** If any Rating 8 registered spark (*Ouro, Percy, Cleo, Aisling, Étaín*) has reached 0 missions remaining (3-mission SRM limit) or exhausted tasks, spend 1 Minor Action to re-register/compile them (Rating 8 @ 20d6 Compiling pool buys 5 hits, drain-free). *Priority order if multiple expire:* **Ouro** (Diagnostics) $\rightarrow$ **Percy** (Shield) $\rightarrow$ **Cleo** (Modular) $\rightarrow$ **Aisling/Étaín**. *(Note: Ally Sprite Taz is permanent and never requires maintenance).*
  5. **Learn a Complex Form (Minor Action):** Absorb the next queued complex form (**5 Karma + 1 Minor Action**).
  
---

## 2. Master Unified Progression Queue

All upcoming upgrades are prioritized sequentially below. When logging post-mission downtime, advance the next available item in this table according to banked Karma, liquid Nuyen, and available action slots.

### A. Karma Progression Pipeline (Ontological & Matrix Scaling)

| Step | Target Upgrade | Category | Cost | Downtime Action Required | Primary Tactical / Architectural Role |
| :---: | :--- | :--- | :---: | :---: | :--- |
| **01** | **Resonance 8 $\rightarrow$ 9** | Attribute | 45 Karma | None (Between runs) | Unlocks Prime Runner dice pools, +1 all Tasking/Matrix tests, +1 Fade resist. |
| **02** | **Submersion Grade 9**<br>• *Echo: Hybrid Sprites*<br>• *Dissonant Submersion* | Submersion | 19 Karma | 1 Major Action<br>*(Mainline SRM only)* | *H&S* 67: Decouples cross-sprite compiling (Machine/Courier sprites) from stream.<br>*SC* 84: Opens access to the Dissonance quality path. |
| **03** | **Stream Transition: Sourceror** | Stream Quality | 20 Karma | None (Between runs) | *H&S* 130–131: Replaces Technoshaman. Unlocks Aspect Peripheral (sustain $\lfloor\text{Submersion}/2\rfloor = \mathbf{4\text{–}5}$ forms with **zero penalties**). |
| **04** | **Complex Form: Hyperthreading** | Complex Form | 5 Karma | 1 Minor Action (Study) | *H&S* 131: Combine multiple complex forms into a single test/action. Core multi-sustain engine enabler. |
| **05** | **Quality: Dissonant Technomancer**<br>(Control / Apophenian)<br>• *Offset by Dissonant Stigma* | Positive Quality<br>*(Net -5K Offset)* | 10 Karma net<br>*(15K base - 5K)* | None (Submersion milestone) | *SC* 84, 86–87: Halves Edge costs (round up) on Matrix actions and complex forms targeting **Devices** (anthrodrones, cyberware, turrets). |
| **06a** | **Complex Form: Dissonance Spike** | Complex Form | 5 Karma | 1 Minor Action (Study) | *SC* 85: Lethal biofeedback + unreductable noise aura. Hyperthreads with *Resonance Spike* or *Cyber Spike*. |
| **06b** | **Complex Form: Dissonant Diffusion** | Complex Form | 5 Karma | 1 Minor Action (Study) | *SC* 85: Strips multiple Matrix attributes simultaneously. Hyperthreads with *Diffusion: Firewall*. |
| **07a** | **Complex Form: Enhance Autosofts** | Complex Form | 5 Karma | 1 Minor Action (Study) | *H&S* 64: [Slot 1] +3 dice pool bonus to all autosofts on Man-at-Arms chassis. |
| **07b** | **Complex Form: Infusion (DP)** | Complex Form | 5 Karma | 1 Minor Action (Study) | *CRB* 190: [Slot 3] Living Persona DP 7 $\rightarrow$ 9 (uncaps Rating 9 autosofts without Karma buys). |
| **07c** | **Complex Form: Infusion (Firewall)** | Complex Form | 5 Karma | 1 Minor Action (Study) | *CRB* 190: [Slot 3] Living Persona Firewall 9 $\rightarrow$ 11. |
| **07d** | **Complex Form: Attack Attribution** | Complex Form | 5 Karma | 1 Minor Action (Study) | *H&S* 62: [Slot 2] Replaces weak base Attack (3) with rolled hits (6–8). |
| **07e** | **Complex Form: Infusion (Sleaze)** | Complex Form | 5 Karma | 1 Minor Action (Study) | *CRB* 190: [Slot 2] Living Persona Sleaze 5 $\rightarrow$ 7–8. |
| **08** | **Complex Form: Static Bomb** | Complex Form | 5 Karma | 1 Minor Action (Study) | *CRB* 191: Instantly breaks all active locks, traces, and spots in a single action. |
| **09** | **Resonance 9 $\rightarrow$ 10** | Attribute | 50 Karma | None (Between runs) | Apex Resonance Capstone. Hard ceiling of current biological/persona evolution. |
| **10** | **Quality: Jack Jockey** | Positive Quality | 11 Karma | None (Between runs) | *H&S* 82: Direct connection denies defensive Edge, bypasses external PAN firewalls, and allows powering on cold devices. |
| **11** | **Electronics Spec: Computers** | Specialization | 5 Karma | None (Between runs) | *DEFERRED BACKLOG:* +2 Matrix Perception & Search (19d6 / 21d6 w/ Oracle R4). Pushed down post-Ch 33. |

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

### B. Sourceror 5-Sustain Matrix Engine Blueprint

As a Sourceror (*Hack & Slash*, pp. 130–131) at Submersion Grade 8–10, Reiko’s Aspect Peripheral sustains up to $\lfloor\text{Submersion}/2\rfloor$ (**4 to 5 complex forms simultaneously with ZERO dice pool penalties**), using **Hyperthreading** to execute stacked forms in a single action:

1. **Slot 1 (Chassis Combat & Drone Dominance):** *Enhance Autosofts* + *Enlighten Automaton* (Hyperthreaded on Shiawase Man-at-Arms). +2 Sensors, +1 Pilot, and **+3 dice to all autosofts** (Rating 9 autosofts roll at **12 dice**). Drain is shunted to registered sprites via *Sprite Link*.
2. **Slot 2 (Matrix Offense & Sleaze Infiltration):** *Attack Attribution* + *Infusion (Sleaze)*. Overcomes weak baseline ratings by replacing Attack with rolled hits (**Attack 6–8**) and pushing Sleaze from 5 $\rightarrow$ **7–8**.
3. **Slot 3 (Living Persona Hardening):** *Infusion (Data Processing)* + *Infusion (Firewall)*. Pushes DP from 7 $\rightarrow$ **9** (fully uncapping Rating 9 autosofts without Karma buys) and Firewall from 9 $\rightarrow$ **11**.
4. **Slot 4 (Operational Stealth Curtain):** *Sustain Phantom*. Conceals persona icon from matrix search; detection threshold equals rolled hits.
5. **Slot 5 (Free Combat / Utility Wildcard):** Reserved for dynamic tactical forms: *Puppeteer*, *Resonance Wires*, *Diffusion (Firewall)*, *Dissonance Spike*, or *Static Bomb*.
