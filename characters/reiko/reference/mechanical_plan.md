# Character Advancement & Mechanical Plan: Reiko

This document tracks character upgrades, mechanical evaluations, karma/nuyen targets, and downtime action logistics for **Reiko Takahashi (Yuriko Star)**.

*(Note: Internal reference document; not published in the Quarto narrative book).*

---

## 1. Executive Summary & Resource Balances

* **Current Available Karma:** 0 Karma (Banked towards *Tasking Spec: Compiling* [5 Karma target; 5 Karma deficit])
* **Lifetime Karma:** 238 Karma | **Submersion Grade:** 8
* **Current Nuyen Balance:** ¥2,550
* **Resonance:** 8 | **Essence / Spark:** 6.00 (Uncompromised)
* **Living Persona Baseline:** ASDF 7 / 9 / 7 / 9 | Full Defense: 34d6
* **Active Ally Sprite:** Taz (Level 7 Assassin Sprite; Symbiosis: Cracking +4, Electronics +4, Influence +4 [dynamically clamped to Reiko's underlying skill rating; currently +1])
* **Immediate Target:** Banking through the next mission to unlock **Tasking Spec: Compiling** (5 Karma; pushes compiling pool to 16d6 for safe Rating 8 sprite compiling).
* **Key Operating Constraint:** Preserve 6.00 Spark at all costs. Avoid codemods that cause Spark loss or risk AI Fragmentation.

---

## 2. Master Priority Upgrade Matrix

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│ STEP 0: ZERO-WAIT & HIGH-LEVERAGE (Immediate Pool / 0–5 Karma)               │
├────────────────────────────────┬──────────────┬──────────────┬──────────────┤
│ Upgrade Item                   │ Type         │ Cost         │ Primary Role │
├────────────────────────────────┼──────────────┼──────────────┼──────────────┤
│ Taz Symbiosis: Influence       │ Ally Sprite  │ 4 Karma      │ [ACQUIRED]   │
│                                │ Upgrade      │              │ Teamwork +4* │
│ Tasking Spec: Compiling        │ Specializ.   │ 5 Karma      │ [ACTIVE TGT] │
│                                │              │              │ Safe R8 Sprts│
├────────────────────────────────┴──────────────┴──────────────┴──────────────┤
│ STEP 1: CORE UTILITY & BREAD-AND-BUTTER ROLLS (5–10 Karma)                  │
├────────────────────────────────┬──────────────┬──────────────┬──────────────┤
│ Electronics Spec: Computers    │ Specializ.   │ 5 Karma      │ +2 Matrix    │
│                                │              │              │ Perception   │
│ Electronics Spec: Software     │ Specializ.   │ 5 Karma      │ +2 Coding &  │
│                                │              │              │ Sourcecraft  │
│ Influence Rank 1 -> 2          │ Active Skill │ 10 Karma     │ +2 Net Dice  │
│                                │              │              │ (Uncaps Taz) │
│ Influence Spec: Negotiation    │ Specializ.   │ 5 Karma      │ +2 Social    │
│                                │              │              │ Wheelhouse   │
├────────────────────────────────┴──────────────┴──────────────┴──────────────┤
│ STEP 2: TACTICAL EXPANSION & RIGGING SYNERGY (10–25 Karma)                   │
├────────────────────────────────┬──────────────┬──────────────┬──────────────┤
│ Complex Form: Enhance Autosoft │ Complex Form │ 5 Karma      │ Drone Buffing│
│ Complex Form: Enlighten Autom. │ Complex Form │ 5 Karma      │ Drone Auton. │
│ Influence Rank 2 -> 3          │ Active Skill │ 15 Karma     │ +2 Net Dice  │
│                                │              │              │ (Taz at +3)  │
│ Charisma 4 -> 5                │ Attribute    │ 25 Karma     │ Social & Comp│
├────────────────────────────────┴──────────────┴──────────────┴──────────────┤
│ STEP 3: HARDWARE BUILDS & CAPSTONES (Downtime Nuyen / 40+ Karma)             │
├────────────────────────────────┬──────────────┬──────────────┬──────────────┤
│ Second Cyberarm (Left, Used)   │ Anthrodrone  │ ¥10,000      │ Nanohive Cap │
│ Nanohive Rating 6 (Used)       │ Anthrodrone  │ ¥45,000      │ Hunter/Infest│
│ Hydrocarbon Fuel Converter     │ Anthrodrone  │ ¥7,500       │ Metabolic Eng│
│ Resonance 9                    │ Attribute    │ 45 Karma     │ Capstone     │
│ Resonance 10                   │ Attribute    │ 50 Karma     │ Capstone     │
└────────────────────────────────┴──────────────┴──────────────┴──────────────┘
*Logged as +4 in modifier ledger; ModifierEngine dynamically clamps teamwork bonus to Reiko's skill rating.
```

---

## 3. Deep Mechanical Evaluations & Rules Calibrations

### A. Taz Influence Symbiosis Mechanics

* **Doubled Karma Upgrade Rule (*HnS* p. 156):** Adding a non-matrix skill to an existing Ally Sprite costs $2 \times 2 = \mathbf{4\text{ Karma}}$. *(Acquired in SRM 2083-14 Post-Mission Advancement)*.
* **Automated Engine Teamwork Clamping (*Core*, p. 17):** Helpers cannot add more bonus dice than the leader’s base skill rank. Taz (Level 7) grants a declared modifier of $+4$ dice ($\lceil 7/2 \rceil$). The project's `ModifierEngine` automatically applies $\min(\text{Teamwork Bonus}, \text{Skill Rating})$ at test evaluation time:
  * *Rank 1 (Current):* 1 + 1 (Taz clamped) + 4 (CHA) = **6 dice** (Modifier logged as +4, clamped to +1 — **ACTIVE**)
  * *Rank 2:* 2 + 2 (Taz clamped) + 4 (CHA) = **8 dice** (Auto-evaluates to +2; Cost: 10 Karma)
  * *Rank 2 + Spec:* 2 + 2 (Taz clamped) + 2 (Spec) + 4 (CHA) = **10 dice** (Cost: 5 Karma)
  * *Rank 3:* 3 + 3 (Taz clamped) + 4 (CHA) = **10 dice general / 12 dice specialized** (Cost: 15 Karma)
  * *Rank 4:* 4 + 4 (Taz full) + 4 (CHA) = **12 dice general / 14 dice specialized** (Full +4 uncap achieved!)

### B. Natural Hacker & Intuition Defense

* With **Natural Hacker**, Matrix Perception is calculated as $\text{Electronics} + \text{Resonance}$, yielding **17–21 dice** regardless of Intuition. INT 2 remains a blindspot strictly for unassisted physical perception, which is offset via drone sensor suites and clearsight autosofts.

### C. Shiawase Man-at-Arms Anthrodrone Hardware Expansion

* **Second Cyberarm (Left, Used Synthetic Cyberarm — 8 Capacity):**
  * Cost: 10,000¥ (Base 20,000¥; 50% used).
  * Provides dedicated modular capacity to seat a heavy used nanohive without burdening the drone's primary torso capacity.
* **Nanohive Rating 6 (Used — 6 Capacity):**
  * Cost: 45,000¥ (Base 90,000¥; 50% used).
  * Capacity: `[6 Capacity]` housed inside the left cyberarm.
  * Function: Controls up to 6 nanite colonies simultaneously, manages 18 Nanite Volume (NV), and replenishes 6 NV per hour. Deploys specialized hunter/seeker or infestation nanites for physical sabotage and barrier disintegration.
* **Hydrocarbon Fuel Converter:**
  * Category: `[2 Powertrain Capacity]` (*Double Clutch*, p. 124).
  * Cost: 7,500¥ (Base Body 10 × 1,500¥ = 15,000¥; 50% self-install discount per *DC*, p. 120).
  * Placement & Function: Installed at the base of the anthrodrone's esophagus, linking oral chemoreceptors and digestive tract to the chassis auxiliary power cell. Allows the chassis to run indefinitely on organic matter (food, alcohol, sugars, plant matter, standard hydrocarbon fuels) away from electrical charging grids while physically consuming food and drink.

---

## 4. Purchasing & Progression Timeline

| Step | Target Upgrade | Cost | Downtime Actions Needed | Funding Mechanism & Status |
| :---: | :--- | :--- | :--- | :--- |
| **01** | **Taz Symbiosis: Influence** | **4 Karma** | None (Post-mission training) | **ACQUIRED** (SRM 2083-14 Post-Mission) |
| **02** | **Tasking Spec: Compiling** | 5 Karma | None (Between runs) | **ACTIVE TARGET** (0/5 Karma Banked) |
| **03** | **Electronics Spec: Computers** | 5 Karma | None (Between runs) | Banked Karma (+2 Matrix Perception) |
| **04** | **Electronics Spec: Software** | 5 Karma | None (Between runs) | Banked Karma (+2 Coding / Sourcecraft) |
| **05** | **Influence Rank 1 $\rightarrow$ 2** | 10 Karma | None (Between runs) | Banked Karma (Uncaps Taz to +2 teamwork) |
| **06** | **Influence Spec: Negotiation** | 5 Karma | None (Between runs) | Banked Karma (+2 Social Wheelhouse) |
| **07** | **Complex Form: Enhance Autosoft** | 5 Karma | 1 Minor Action (Study) | Banked Karma (Drone Buffing) |
| **08** | **Complex Form: Enlighten Automaton** | 5 Karma | 1 Minor Action (Study) | Banked Karma (Drone Autonomy) |
| **09** | **Second Cyberarm (Left, Used)** | ¥10,000 | 1 Minor Action (Install) | Mission Nuyen (8 Cap for Nanohive) |
| **10** | **Nanohive Rating 6 (Used)** | ¥45,000 | 1 Minor Action (Install) | Mission Nuyen (Hunter/Infest Nanites) |
| **11** | **Hydrocarbon Fuel Converter** | ¥7,500 | 1 Minor Action (Install) | Mission Nuyen (Metabolic Power) |
| **12** | **Influence Rank 2 $\rightarrow$ 3** | 15 Karma | None (Between runs) | Banked Karma (Uncaps Taz to +3 teamwork) |
| **13** | **Charisma 4 $\rightarrow$ 5** | 25 Karma | None (Between runs) | Banked Karma (Social & Compiling) |
| **14** | **Resonance 8 $\rightarrow$ 9** | 45 Karma | None (Between runs) | Banked Karma (Capstone Progression) |
| **15** | **Resonance 9 $\rightarrow$ 10** | 50 Karma | None (Between runs) | Banked Karma (Capstone Progression) |
