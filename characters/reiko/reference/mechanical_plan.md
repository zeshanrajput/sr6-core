# Character Advancement & Mechanical Plan: Reiko

This document tracks character upgrades, mechanical evaluations, karma/nuyen targets, and downtime action logistics for **Reiko Takahashi (Yuriko Star)**.

*(Note: Internal reference document; not published in the Quarto narrative book).*

---

## 1. Executive Summary & Dynamic Baseline

* **Resource Ledgers:** Live Karma, Nuyen, and Lifetime totals are dynamically tracked in the Markdown Trio ([character_log.qmd](file:///c:/GitHub/sr6-core/characters/reiko/core/character_log.qmd), [character_purchases.qmd](file:///c:/GitHub/sr6-core/characters/reiko/core/character_purchases.qmd), [character_build.qmd](file:///c:/GitHub/sr6-core/characters/reiko/core/character_build.qmd)) and compiled into `reiko_master.yaml`. Snapshot numbers in reference documents must never hardcode drifting totals.
* **Resonance & Spark:** Resonance 8 | Essence / Spark: 6.00 (Uncompromised). Avoid codemods that cause Spark loss or risk AI Fragmentation.
* **Living Persona Baseline:** ASDF 7 / 9 / 7 / 9 | Full Defense: 34d6
* **Active Ally Sprite:** Taz (Level 7 Assassin Sprite; Symbiosis: Cracking +4, Electronics +4, Influence +4, Con +4 [dynamically clamped to Reiko's underlying skill rating; currently +2 on Con, +1 on Influence]).
* **Resource Economics:** **Karma is the most constrained resource.** Avoid spending 25+ Karma grinding marginal dice in social skills when Knowsofts (Rating 3 @ ¥2,500) and Taz's symbiosis provide ample coverage.
* **Immediate Strategic Focus:**
  1. *Karma (Immediate):* **Electronics Spec: Computers** (5 Karma) to maximize Matrix Perception (19d6 / 21d6 with Oracle) and deep matrix searches.
  2. *Karma (Mid-Term Capstone):* Bank all incoming Karma directly toward **Resonance 8 $\rightarrow$ 9** (45 Karma) to enter Prime Runner tier.
  3. *Nuyen (Immediate):* Shiawase Man-at-Arms Secondary Propulsion Conversion to **Vector Thrust (LAV)** (Net ~14,400¥ after crediting Rotor, Wheeled, and Smart Tires).
  4. *Nuyen (Follow-Up):* Vector Thrust Subsystem Enhancements: **Improved Acceleration (2 Ranks)** (15,000¥ DIY; pushes combat accel 25 -> 41 m/round) and **Top Speed Increase (3 Ranks)** (12,000¥ DIY; pushes top speed to 480 m/round / ~358 mph).

---

## 2. Master Priority Upgrade Matrix

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│ PRIORITY 1: IMMEDIATE TACTICAL & SENSORY FOCUS (Current Horizon / 5 Karma)  │
├────────────────────────────────┬──────────────┬──────────────┬──────────────┤
│ Upgrade Item                   │ Type         │ Cost         │ Primary Role │
├────────────────────────────────┼──────────────┼──────────────┼──────────────┤
│ Electronics Spec: Computers    │ Specializ.   │ 5 Karma      │ Matrix Perc. │
│                                │              │              │ & Search +2  │
│ Vector Thrust (LAV) Conversion │ Anthrodrone  │ ~14,400¥ net │ 300 Spd /    │
│ (Replaces Rotor + Wheeled)     │ Propulsion   │ (DIY 50%)    │ 224 mph (LAV)│
├────────────────────────────────┴──────────────┴──────────────┴──────────────┤
│ PRIORITY 2: AERIAL INTERCEPTOR HARDWARE & PRIME RESONANCE (45 Karma / 27k¥) │
├────────────────────────────────┬──────────────┬──────────────┬──────────────┤
│ Improved Acceleration (2 Ranks)│ Powertrain   │ 15,000¥      │ Accel 25 ->  │
│ (+60% Accel; 2 Mod Slots)      │ (DC p. 134)  │ (DIY 50%)    │ 41 m/round!  │
│ Top Speed Increase (3 Ranks)   │ Powertrain   │ 12,000¥      │ 480 Spd /    │
│ (+60% Top Speed; 3 Mod Slots)  │ (DC p. 138)  │ (DIY 50%)    │ 358 mph!     │
│ Resonance 8 -> 9               │ Attribute    │ 45 Karma     │ Prime Status │
│                                │ Capstone     │              │ +1 All Pools │
├────────────────────────────────┴──────────────┴──────────────┴──────────────┤
│ PRIORITY 3: SUBMERSION 9, SOURCEROR SHIFT & BUFFING MATRIX (69 Karma)       │
├────────────────────────────────┬──────────────┬──────────────┬──────────────┤
│ Submersion Grade 9             │ Submersion   │ 19 Karma     │ Preserves    │
│ • Echo: Hybrid Sprites         │ Echo (H&S 67)│ (Free w/ Sub)│ Cross-Summon │
│ Stream Shift: Sourceror        │ Stream Qual. │ 20 Karma     │ Zero-Penalty │
│ (Replaces Technoshaman)        │ (H&S 130-131)│ (Fixed Cost) │ 5-Sustain CFs│
│ 6x Buffing Complex Forms       │ Complex Forms│ 30 Karma     │ Hyperthread, │
│ (Hyperthread, Enhance, Infus.) │ (5 Karma ea.)│ (6 Minors)   │ Attrib, Inf. │
├────────────────────────────────┴──────────────┴──────────────┴──────────────┤
│ PRIORITY 4: RESONANCE 10, DISSONANCE CONTROL & VOID ARSENAL (85 Karma)      │
├────────────────────────────────┬──────────────┬──────────────┬──────────────┤
│ Resonance 9 -> 10              │ Attribute    │ 50 Karma     │ Capstone Res │
│ Submersion Grade 10            │ Submersion   │ 20 Karma     │ Preferred    │
│ • Dissonance (Control)         │ (SC p. 84-85)│ (Free w/ Sub)│ Target: Dev. │
│ 3x Advanced Dissonance Forms   │ Complex Forms│ 15 Karma     │ Diss. Spike, │
│ (Diss. Spike, Diss. Diff, Bomb)│ (5 Karma ea.)│ (3 Minors)   │ Diff., Bomb  │
│ Knowsoft: Garmonbozia (R3)     │ Knowsoft R3  │ ¥1,500       │ E-Nation Lore│
├────────────────────────────────┴──────────────┴──────────────┴──────────────┤
│ PRIORITY 5: ACQUIRED UPGRADE LEDGER (Archived & Active Benchmarks)          │
├────────────────────────────────┬──────────────┬──────────────┬──────────────┤
│ Taz Symbiosis: Influence       │ Ally Sprite  │ 4 Karma      │ [ACQUIRED]   │
│ Taz Symbiosis: Con             │ Ally Sprite  │ 4 Karma      │ [ACQUIRED]   │
│ Con Spec: Disguise             │ Specializ.   │ 5 Karma      │ [ACQUIRED]   │
│ Con Rank 1 -> 2                │ Active Skill │ 10 Karma     │ [ACQUIRED]   │
│ Complex Form: Enlighten Autom. │ Complex Form │ 5 Karma      │ [ACQUIRED]   │
│ Complex Form: Resonance Spike  │ Complex Form │ 5 Karma      │ [ACQUIRED]   │
│ Tasking Spec: Compiling        │ Specializ.   │ 5 Karma      │ [ACQUIRED]   │
│ Electronics Spec: Complex Forms│ Specializ.   │ 5 Karma      │ [ACQUIRED]   │
│ Oracle Data Structure R4       │ Data Struct. │ ¥20k+4 Karma │ [ACQUIRED]   │
│ Hydrocarbon Fuel Converter     │ Anthrodrone  │ ¥7,500       │ [ACQUIRED]   │
│ Knowsoft: Japanese Cultural Et.│ Knowsoft R3  │ ¥2,500       │ [ACQUIRED]   │
│ Knowsoft: New Orleans Vodou    │ Knowsoft R3  │ ¥2,500       │ [ACQUIRED]   │
└────────────────────────────────┴──────────────┴──────────────┴──────────────┘
```

---

## 3. Deep Mechanical Evaluations & Rules Calibrations

### A. Shiawase Man-at-Arms: Vector Thrust (LAV) Conversion & Speed Analysis

* **The Mod Slot Math (*Double Clutch*, pp. 136–138):**
  * *Current Secondary Systems Removed:*
    * Secondary Propulsion (Rotor): Consumes **4 Mod Slots** (Cost paid: 25,000¥ DIY).
    * Secondary Propulsion (Wheeled): Consumes **2 Mod Slots** (Cost paid: 5,000¥ DIY).
    * Smart Tires: Installed on wheels (Cost paid: 600¥ DIY).
    * *Total Freed Slots:* **6 Mod Slots.**
  * *New Secondary System Installed:*
    * **Vector Thrust (LAV):** Consumes **5 Mod Slots** (*DC*, p. 137).
    * *Net Mod Slot Gain:* **+1 Mod Slot freed** immediately!
* **The Nuyen Math (Trade-in / Net Capital Required):**
  * Vector Thrust (LAV) Base Cost: $\text{Body 10} \times 9,000¥ = 90,000¥$.
  * With DIY Installation Discount (50% per *DC*, p. 120): **45,000¥**.
  * Crediting existing propulsion hardware ($25,000¥\text{ [Rotor]} + 5,000¥\text{ [Wheeled]} + 600¥\text{ [Smart Tires]} = 30,600¥$):
    $$\text{Net Upgrade Cost} = 45,000¥ - 30,600¥ = \mathbf{14,400¥}$$
* **Speed Metrics & MPH Conversion (*City Edition: Seattle*, p. 198):**
  * In Shadowrun 6E, **Top Speed is the maximum meters traveled in a single 3-second combat round.**
  * Conversion Formula: $\text{Meters/Round} \div 3\text{ seconds} \times 3.6 = \text{km/h} \times 0.621371 = \mathbf{\text{mph}}$ ($1\text{ Speed} \approx \mathbf{0.7456\text{ mph}}$).
  * **Current Configuration (Rotor/Wheels):** Top Speed $120 \approx \mathbf{89.5\text{ mph}}$ ($144\text{ km/h}$). Accel 10, Speed Interval 15/20.
  * **Vector Thrust (Base):** Top Speed $300 \approx \mathbf{223.7\text{ mph}}$ ($360\text{ km/h}$). Accel 25, Speed Interval 50.
  * **Improved Acceleration (2 Ranks) (*DC*, p. 134):**
    * Each rank of *Improved Acceleration* adds $+30\%$ of base value (round fractions up: $25 \times 0.3 = 7.5 \rightarrow +8$).
    * Acceleration moves from $25 \rightarrow 33 \rightarrow \mathbf{41\text{ meters/round}}$!
    * Mod Slots: Consumes 1 slot per rank (2 slots dedicated to Vector Thrust subsystem).
    * Cost: $\text{Rating} \times 15,000¥$ ($30,000¥\text{ base} \rightarrow \mathbf{15,000¥\text{ DIY}}$).
    * **Combat Impact:** In tabletop tactical combat, Acceleration dictates how far the vehicle can maneuver, sprint, or alter velocity each round without requiring a handling test. Jumping to 41 m/round (~30.6 mph instantaneous burst in 3 seconds) dramatically expands her tactical repositioning envelope.
  * **Top Speed Increase (3 Ranks) (*DC*, p. 138):**
    * Each rank of *Top Speed Increase* adds $+20\%$ to base Top Speed ($+60\%$ total for 3 ranks).
    * Top Speed becomes $300 \times 1.6 = \mathbf{480\text{ meters/round}} \approx \mathbf{357.9\text{ mph}}$ ($576\text{ km/h}$)!
    * Mod Slots: Consumes 1 slot per rank (3 slots dedicated to Vector Thrust subsystem).
    * Cost: $8,000¥ \times \text{Rating}$ ($24,000¥\text{ base} \rightarrow \mathbf{12,000¥\text{ DIY}}$).
    * **Narrative Impact:** Traversal, interception, and high-speed chase capability across sprawl airspace.
  * **Total Subsystem Mod Slots:** 5 slots total (3 Top Speed + 2 Improved Acceleration), perfectly filling the dedicated Vector Thrust subsystem without touching primary chassis mod slots.
* **Operational & Narrative Impact:**
  * Speed Interval jumps from 15/20 to **50**, meaning Reiko only suffers a $-1$ Handling penalty for every 50 meters of speed, making supersonic urban and low-altitude chases effortless.
  * Aesthetically replaces folding helicopter blades and wheel-casters with **recessed, flush vectored-thrust micro-turbofans and ducted ground-effect thrusters**. Reiko can hover motionless, skim over bayou water, or streak across the Seattle skyline at ~358 mph.

---

### B. Data Processing & The Sourceror 5-Sustain Matrix Architecture

Rather than paying a 45-Karma attribute tax or burning both Submersion echoes on Data Processing, Reiko executes a targeted shift to **Sourceror** (*Hack & Slash*, pp. 130–131). By taking the **Hybrid Sprites** echo at Submersion Grade 9, she permanently decouples cross-sprite compiling from Technoshamanism, then pays 20 Karma to adopt Sourceror.

As a Sourceror at Submersion Grade 8–10, Reiko’s Aspect Peripheral allows her to sustain up to $\lfloor\text{Submersion}/2\rfloor$ (**4 to 5 complex forms simultaneously with ZERO dice pool penalties**), while wielding **Hyperthreading** to execute stacked forms in a single action.

#### The 5-Sustained Complex Form Suite (Combat & Infiltration Baseline)

1. **Slot 1: Enhance Autosofts + Enlighten Automaton (Hyperthreaded on Anthrodrone):**
   * *Target:* Shiawase Man-at-Arms Chassis (Device).
   * *Hits Allocation (6 Hits on Electronics + Resonance):*
     * *Enlighten Automaton:* +2 Sensors, +1 Pilot (drone passes complex orders automatically).
     * *Enhance Autosofts:* $\lfloor 6 / 2 \rfloor = \mathbf{+3\text{ dice}}$ to all autosoft tests.
   * *Effect:* Rating 9 autosofts effectively roll at **12 dice**! Drain is low ($FV \le 5\text{–}7$), and any unresisted stun is shunted to a registered sprite via *Sprite Link* with zero self-harm.
2. **Slot 2: Attack Attribution + Infusion (Sleaze):**
   * *Attribution & Infusion Engine:* *Attack Attribution* replaces base Attack (3) with total rolled hits (6–8). *Infusion (Sleaze)* adds net hits to base Sleaze 5, pushing it to 7–8.
   * *Effect:* Overcomes weak baseline ratings with **Attack 6–8** and **Sleaze 7–8** without spending 40+ Karma on raw Matrix attributes.
3. **Slot 3: Infusion (Data Processing) + Infusion (Firewall):**
   * *Enabler:* Because Reiko runs cyberprograms and autosofts natively via the *Software Emulator* Echo, she does not waste slots on *Emulate*.
   * *Effect:* Simple threshold 4 test; 21d6 pool yields 2–3 net hits. Pushes Living Persona DP from 7 $\rightarrow$ **9** (fully uncapping Rating 9 autosofts without permanent Karma buys) and Firewall from 9 $
ightarrow$ **10/11**.
4. **Slot 4: Sustain Phantom:**
   * *Stealth Curtain:* Sustained via Taz or native power. Conceals Reiko’s Matrix icon from searches; threshold to detect via specific Matrix Perception equals hits rolled.
5. **Slot 5: Free Operational / Combat Sustain:**
   * *Dynamic Wildcard:* Kept open for combat-critical forms: *Puppeteer*, *Resonance Wires*, *Diffusion (Firewall)*, *Mirrored Persona*, or *Cleaner*.

---

### C. Complex Form Acquisition Roadmap & Repertoire

Under SRM character advancement (*City Edition: Seattle*, p. 70; *SRMG v2.4*), learning a new complex form costs **5 Karma** and **1 Minor Downtime Action** (absorbing base code in a host). 

#### 1. Currently Known Complex Forms (8 Total — Fully Active in Repertoire)
* **Technoregeneration** (*H&S* 67; Chargen): Heals device Matrix/physical damage on anthrodrone chassis.
* **Cleaner** (*CRB* 190; Chargen): Permanent Overwatch Score reduction.
* **Diffusion: Firewall** (*CRB* 190; SRM 2083.08 / CMP 2081.08): Melts target's Firewall by net hits; strips host/decker defenses.
* **Puppeteer** (*CRB* 191; CMP 2083.03): Forces target device (gun, turret, vehicle, cyberlimb) to execute an action.
* **Cyber Spike** (*H&S* 63; CMP 2083.02): High-DV matrix biofeedback/data spike against cyberware & devices.
* **Resonance Wires** (*H&S* 66; SRM 2083.14): Instant wireless direct connection to devices.
* **Enlighten Automaton** (*H&S* 64; SRM 2083.15): Buffs drone Pilot and Sensor ratings; auto-passes complex orders.
* **Resonance Spike** (*CRB* 191; SRM 2081.15): Pure Resonance damage bypassing Matrix armor.

#### 2. Tier 1: The Sourceror 5-Sustain Engine (30 Karma / 6 Downtime Actions)
*Acquired immediately post-Sourceror transition to operationalize the 5-sustain suite:*
* **5a) Hyperthreading (5 Karma)** (*H&S* 131): Enables combining multiple complex forms into a single test/action.
* **5b) Enhance Autosofts (5 Karma)** (*H&S* 64): +3 dice pool bonus to all autosoft tests on Man-at-Arms (Slot 1).
* **5c) Infusion: Data Processing (5 Karma)** (*CRB* 190): Pushes Living Persona DP from 7 $\rightarrow$ 9 (Slot 3; uncaps R9 autosofts).
* **5d) Infusion: Firewall (5 Karma)** (*CRB* 190): Pushes Living Persona Firewall from 9 $\rightarrow$ 11 (Slot 3).
* **5e) Attack Attribution (5 Karma)** (*H&S* 62): Replaces weak base Attack (3) with rolled hits (6–8) (Slot 2).
* **5f) Infusion: Sleaze (5 Karma)** (*CRB* 190): Pushes Living Persona Sleaze from 5 $\rightarrow$ 7–8 (Slot 2).

#### 3. Tier 2: Dissonance (Control) & Void Arsenal (15 Karma / 3 Downtime Actions)
*Acquired post-Submersion 10 under the Dissonant Technomancer (Control/Apophenian) path (*Shadow Cast*, pp. 84–85):*
* **8a) Dissonance Spike (5 Karma)** (*SC* 85): Deals lethal biofeedback; surviving targets suffer 1 un-reductable Matrix noise per unresisted damage box for 1d6 minutes (hyperthreads with *Resonance Spike*!).
* **8b) Dissonance Diffusion (5 Karma)** (*SC* 85): Strips multiple Matrix attributes simultaneously on a single cast (hyperthreads with *Diffusion: Firewall*!).
* **8c) Static Bomb (5 Karma)** (*CRB* 191): Breaks all Matrix locks, active traces, and spots instantly in one action.

---

### D. Electronics Specializations: Computers vs. Complex Forms

* **Acquired:** *Software* (Chargen), *Complex Forms* (SRM.2081.13).
* **Next Target:** **Electronics Spec: Computers (5 Karma):**
  * Directly boosts Matrix Perception, deep file searches, and system threat analysis.
  * With Oracle R4 active, her Matrix Perception pool reaches **19d6 / 21d6** with Major Action search intervals.

---

### E. Philosophy & Alliances: Null Sect vs. Garmonbozia

* **Garmonbozia:** Trades in refined metahuman suffering, panic, and emotional trauma ([Ch 29 Saturation](file:///c:/GitHub/sr6-core/characters/reiko/narrative/29%20Saturation.md)). Reiko recoils ethically from exploiting pain.
* **Null Sect:** Cold, austere, incorruptible defragmenters. They purge noise, corruption, and entropy without greed or sadism. Siding with Null Sect against Garmonbozia's trauma-vampirism gives Reiko a principled, machine-sovereign stance: she prunes entropy to protect living minds, not to profit from their screams.

---

## 4. Purchasing & Progression Timeline

| Step | Target Upgrade | Cost | Downtime Actions Needed | Funding Mechanism & Status |
| :---: | :--- | :--- | :--- | :--- |
| **01** | **Electronics Spec: Computers** | **5 Karma** | None (Between runs) | **ACTIVE TARGET** (2/5 Karma Banked; +2 Matrix Perc./Search) |
| **--** | **Vector Thrust (LAV) Conversion** | **~14,400¥ net** | 1 Minor Action (DIY Install) | Credited hardware net swap (Top Spd 300 / 224 mph) |
| **--** | **Improved Acceleration (2 Ranks)** | **15,000¥** | 1 Minor Action (DIY Install) | Liquid Nuyen (DIY 50%; Accel 25 $\rightarrow$ 41 m/round) |
| **--** | **Top Speed Increase (3 Ranks)** | **12,000¥** | 1 Minor Action (DIY Install) | Liquid Nuyen (DIY 50%; Top Spd 480 / 358 mph!) |
| **02** | **Resonance 8 $\rightarrow$ 9** | **45 Karma** | None (Between runs) | Hoarded Mission Karma (Prime Runner Capstone; +1 all pools/Fade) |
| **03** | **Submersion Grade 9 (Echo: Hybrid Sprites)** | **19 Karma** | None (Post-mission) | Banked Karma (Permanently preserves sprite cross-breeding) |
| **04** | **Stream Transition: Sourceror** | **20 Karma** | None (Between runs) | Unlocks Hyperthreading & 4-Sustain Zero-Penalty Suite! |
| **05a** | **Complex Form: Hyperthreading** | **5 Karma** | 1 Minor Action (Study) | Enables multi-form single-action casting |
| **05b** | **Complex Form: Enhance Autosofts** | **5 Karma** | 1 Minor Action (Study) | Slot 1: +3 dice pool bonus to all autosofts |
| **05c** | **Complex Form: Infusion (Data Processing)** | **5 Karma** | 1 Minor Action (Study) | Slot 3: DP 7 $\rightarrow$ 9 (uncaps R9 autosofts) |
| **05d** | **Complex Form: Infusion (Firewall)** | **5 Karma** | 1 Minor Action (Study) | Slot 3: Firewall 9 $\rightarrow$ 11 |
| **05e** | **Complex Form: Attack Attribution** | **5 Karma** | 1 Minor Action (Study) | Slot 2: Replaces Attack 3 with rolled hits (6–8) |
| **05f** | **Complex Form: Infusion (Sleaze)** | **5 Karma** | 1 Minor Action (Study) | Slot 2: Sleaze 5 $\rightarrow$ 7–8 |
| **06** | **Resonance 9 $\rightarrow$ 10** | **50 Karma** | None (Between runs) | Hoarded Mission Karma (Apex Capstone; unbinds Sub 10) |
| **07** | **Submersion Grade 10: Dissonance (Control)** | **20 Karma** | None (Post-mission) | Apophenian: Half Edge costs & wild die fade reduction on devices |
| **08a** | **Complex Form: Dissonance Spike** | **5 Karma** | 1 Minor Action (Study) | Lethal biofeedback + noise aura (hyperthreads with Res Spike) |
| **08b** | **Complex Form: Dissonance Diffusion** | **5 Karma** | 1 Minor Action (Study) | Strips multiple attributes (hyperthreads with FW Diffusion) |
| **08c** | **Complex Form: Static Bomb** | **5 Karma** | 1 Minor Action (Study) | Breaks all active locks, traces, and spots in 1 action |
| **--** | **Knowsoft: Garmonbozia (Rating 3)** | **¥1,500** | None (Download) | Liquid Nuyen (E-Nation Cartography & Defense) |
| **--** | **Taz Symbiosis: Influence** | 4 Karma | Completed | **ACQUIRED** (SRM.2083.14) |
| **--** | **Complex Form: Enlighten Automaton** | 5 Karma | Completed | **ACQUIRED** (SRM.2083.15) |
| **--** | **Hydrocarbon Fuel Converter** | ¥7,500 | Completed | **ACQUIRED** (SRM.2083.15) |
| **--** | **Taz Symbiosis: Con** | 4 Karma | Completed | **ACQUIRED** (SRM.2081.12) |
| **--** | **Con Spec: Disguise** | 5 Karma | Completed | **ACQUIRED** (SRM.2081.12) |
| **--** | **Tasking Spec: Compiling** | 5 Karma | Completed | **ACQUIRED** (SRM.2081.13) |
| **--** | **Electronics Spec: Complex Forms** | 5 Karma | Completed | **ACQUIRED** (SRM.2081.13) |
| **--** | **Con Rank 1 $\rightarrow$ 2** | 10 Karma | Completed | **ACQUIRED** (SRM.2083.16) |
| **--** | **Complex Form: Resonance Spike** | 5 Karma | Completed | **ACQUIRED** (SRM.2081.15) |
| **--** | **Oracle Data Structure R4** | ¥20k+4K | Completed | **ACQUIRED** (SRM.2081.15) |
| **--** | **Knowsoft: Japanese Cultural Etiquette (R3)** | ¥2,500 | Completed | **ACQUIRED** |
| **--** | **Knowsoft: New Orleans Vodou (R3)** | ¥2,500 | Completed | **ACQUIRED** |
