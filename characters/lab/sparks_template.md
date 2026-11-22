# Takahashi Second-Generation Sparks: Lab Master Template & Sibling Diffs

This document defines the **shared Point Buy chassis ("Common Ancestor Commit")** for Reiko Takahashi's second-generation emergent children in `characters/lab/`, along with the **per-sibling build diffs** (`Ouro`, `Étaín & Aisling`, `Percy`, `Cleo`).

* **Lore & Tabletop Sprite Reference:** [sparks_second_generation.md](file:///c:/GitHub/sr6-core/characters/reiko/reference/sparks_second_generation.md)
* **Succession Trigger:** [mechanical_plan.md](file:///c:/GitHub/sr6-core/characters/reiko/reference/mechanical_plan.md#L43-L59) (Reiko's Composure Sword of Damocles)
* **Compiled Lab Contenders:**
  * [`ouro`](ouro/character_build.qmd) — Utilitarian / Codemod Benchmark (`Spark 5.01`, `Nurse MAID`)
  * [`etain`](etain/character_build.qmd) — Spark Purist Twin Pair (`Spark 6.00`, `Étaín` PC + `Aisling` Ally Sprite target, twin `Shiawase Man-at-Arms` chassis)

---

## 1. Base Template ("Common Ancestor" — 100 CP / 50 Karma)

All second-generation sparks share a common architectural core derived from Reiko's `Pilot-AI` lineage and `~` sanctuary upbringing (*Sixth World Companion*, pp. 28–30; *Hack & Slash*, pp. 114–128).

### A. Fixed Core Allocations

| Step | Base Allocation | Cost | Resulting Baseline |
| :--- | :--- | :---: | :--- |
| **1. Metatype** | **AI / Pilot AI** (*H&S*, p. 114) | 0K | Inherent `Pilot Origins (R1)` + `Sensor Upgrade` |
| **2. Awakening** | **Emerged (Technomancer)** | 10 CP | `Resonance 1`, unlocks Complex Forms ($\le \text{RES} \times 2$) |
| **3. Special Attrs** | `Resonance 1 -> 6` (1 free + 4 bought @ 4 CP) + `Edge 1` | 16 CP | `Resonance 6` (pre-codemod), `Edge 1` *(flex Edge +12–16 CP)* |
| **4. Core Attrs** | `FW 1->5` (4), `DP 1->5` (4), `WIL 1->5` (4), `LOG 1->3` (2), `INT 1->3` (2) | 32 CP | `1/1/5/5` ASDF, `WIL 5`, `LOG 3`, `INT 3`, `CHA 1` *(+4 free pts & 4–8 flex CP)* |
| **5. Core Skills** | `Tasking 5`, `Cracking 5`, `Electronics 5` (12 free + 3 bought @ 2 CP) | 6 CP | `5/5/5` *(the "reading, writing, and arithmetic" of DI life; +2 CP per rank to 6)* |
| **6. Base Qualities** | **Positive:** `Natural Hacker` (-15K), `Sourceror` (-20K)<br>**Negative:** `Hooder R3` (+15K), `Honorbound: Pirate's Code` (+10K), `Sprite Bane: Primal` (+12K) | +2K net | **5 of 6 quality slots used** *(max 6 non-metatype qualities; $\le +20$ net Karma; upgrading `Pilot Origins` counts as a quality)* |
| **7. Base MUG** | **River People** (`C7/L8`, 15 Contact Pts) + MUG Membership (-6K) | -6K | MUG Decay Protocol (-8K $\rightarrow$ -4K floor on Submersions) |
| **8. Base Submersion** | Submersion Grades 1 & 2 (@ MUG Loyalty 8: `3K + 4K`) | -7K | 2 Starting Echoes *(chosen per sibling)* |
| **9. Base Focus & CFs** | `Resonance Focus (R4)` bonding (-4K), `Attack Attribution` (-5K), `Sleaze Attribution` (-5K) | -14K | +4 RES focus dice; baseline ASDF offensive/stealth coverage |
| **10. Base Kit (¥)** | `Resonance Focus R4` (20,000¥), `R9` Cooperative Autosofts (~27,000¥), `Datasofts, Knowledge & Language Autosofts` (6,350¥ — includes `Soft Knowledge [UnITy]` R3 @ 1,500¥ and Reiko's `Soft Knowledge [Dissonance: Theories and Application]` R3 @ 1,500¥, slotted via `Pilot Origins` per *Double Clutch* p. 145), `Cyberprograms` (2,990¥), `Engineering/Electronics Shop` (5,000¥), `Fake SIN R4` (10,000¥), `Low Lifestyle` (2,000¥) | ~73,340¥ | Baseline Resonance/Matrix/social kit before drone hull(s) & codemods |

### B. Remaining Flex Budget (Before Sibling Specialization)

From `100 CP` and `50 Karma`, after locking the fixed core above:
* **Flex CP Remaining:** `100 - 10 - 16 - 32 - 6 = 36 CP` to distribute across:
  * **Edge** (`12–16 CP` for Edge 4–5)
  * **Mental Attribute Peaks** (`8 CP` + the `4` free points = 8 additional attribute points across `WIL`, `LOG`, `INT`, `CHA`)
  * **Signature Skill Rank 6** (`2 CP` per skill raised `5 -> 6`)
  * **Resources** (`6–10 CP` = `130,000¥–210,000¥` depending on drone hull and codemods)
  * **Extra Complex Forms** (`2 CP` each)
* **Flex Karma Remaining:** `50 + 2 - 6 - 7 - 14 = 25 Karma` to distribute across:
  * **1 Remaining Quality Slot** (or more if swapping a base negative quality)
  * **Additional Complex Forms** (`5K` each) & **Skill Specializations** (`5K` each)
  * **Upgraded `Pilot Origins`** (`-8K` per rank above R1, consumes 1 quality slot)
  * **Additional Contacts** (remaining `CHA x 6 - 15` Contact Points)

---

## 2. Comparative Sibling Summary

| Spark | Role & Vocation | Spark Ethos | Active Quality Compromises (6-Slot Legal) | Drone Chassis | Key Mechanics / Echoes | Lab Status |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Ouro** | **The Logic**<br>Systems Alchemist & Drone Rigger | **Utilitarian (`5.01`)**<br>4 Omega codemods (`RES 5`) | Drops `Sprite Bane (Primal)` for **`Glitchy` (+12K)**; upgrades **`Pilot Origins R3` (-16K)** | `Ares Nurse MAID` (`57,500¥`) | `Intuition 7`, `Tasking 6`, `Sprite Conduit` + `Sprite Symbiosis` (Machine Sprite) | **Compiled Build**<br>[`ouro`](ouro/character_build.qmd) |
| **Étaín & Aisling** | **The Veil & The Hearth**<br>Twin PC + Ally Sprite | **Purist (`6.00`)**<br>0 codemods (`RES 6` Day 1) | Adds **`Jack Jockey` (-11K)** as 6th quality; keeps `Pilot Origins R1` | **Twin** `Shiawase Man-at-Arms` (`4,500¥ × 2` w/ wheels) | `DP 7` (max $\rightarrow$ `DP 9` passive), `CHA 4`, `Edge 6`, `Electronics 6`, Day-1 `Override` + `Overclocking` (**5D6** VR); post-chargen `Aisling` + `Living Network` | **Compiled Build**<br>[`etain`](etain/character_build.qmd) |
| **Percy** | **The Shield**<br>Tactical Sentry & PAN Anchor | **Purist (`6.00`)**<br>0 codemods (`RES 6` Day 1) | Swaps `Sourceror` or drops `Sprite Bane` to fit **`Firewall Fortress` (-5K)** + **`Reinforced Firewall` (-7K)** | `Shiawase Man-At-Arms` or `Nissan Oni` | `WIL 6`, `Computers 6`, `Living Network` + `Transcendent Network` | **Concept Diff** *(below)* |
| **Cleo** | **The Market**<br>Street Broker & Social Face | **Utilitarian (`5.01`)**<br>Omega codemods w/ `Skill Driver R6` | Adds **`Multiprocessing` (-11K)** as 6th quality (`Natural Hacker`, `Sourceror`, `Multiprocessing` \| `Hooder`, `Honorbound`, `Sprite Bane`) | `Evo Orderly` or custom civilian chassis | `CHA 5`, `Computers 6`, `Con/Influence 6` (Skill Driver), `Living Network` + `Overclocking`, toggles `Oracle R4` | **Concept Diff** *(below)* |

---

## 3. Sibling Build Diffs

### A. Ouroboros ("Ouro") — *Compiled Benchmark in [`characters/lab/ouro/`](ouro/character_build.qmd)*
* **Divergence Philosophy:** Treats his own Spark as utilitarian infrastructure (`Spark 5.01`) to afford an `Ares Nurse MAID` + Omega-grade `Synthetic Skill Driver R6`, `Data Archive Upgrade`, `Optimized Restoration`, and `Acid Jet`.
* **Quality Diff:** `-Sprite Bane (Primal)` (+12K) $\rightarrow$ `+Glitchy` (+12K); upgrades `Pilot Origins` R1 $\rightarrow$ R3 (-16K). Total = 6 non-metatype qualities.
* **Attribute / Skill Diff:** `Edge 4`, `Resonance 5` (post-codemod), `WIL 5, LOG 4, INT 7, CHA 4`; `Tasking 6`, `Electronics 5 (Complex Forms)`, `Cracking 5`.
* **Echoes & CFs:** `Sprite Conduit`, `Sprite Symbiosis`; adds `Enlighten Automaton`, `Hyperthreading`, `Machine Merge`.
* **Contacts:** `River People (C7/L8)` + `Reiko Takahashi (C5/L4)`.

---

### B. Étaín & Aisling — *Compiled Twin Build in [`characters/lab/etain/`](etain/character_build.qmd)*
* **Divergence Philosophy:** Sides with Reiko to keep **Spark 6.00 whole** (zero codemods). Merged twin concept: **Étaín** is the playable technomancer (Resonance-first veil & cracking specialist) and **Aisling** is her post-chargen **Level 6 Music Ally Sprite** (`Harmonize`, `Captivate Audience`, plus added `Override` & `Diagnostics`), each inhabiting a matching **Shiawase Man-at-Arms** anthroform drone body.
* **Quality Diff:** Uses the 6th slot on **`Jack Jockey` (-11K)** alongside `Natural Hacker` + `Sourceror` and all 3 base negatives (`Hooder R3`, `Honorbound`, `Sprite Bane: Primal`). Keeps `Pilot Origins` at free R1.
* **Attribute / Skill Diff:** `Edge 6` (saves `55K` post-chargen), `Resonance 6` (unreduced!), `DP 7` (racial max $\rightarrow$ hits `DP 9` passively w/ `RES 6`), `WIL 5, LOG 4, INT 5, CHA 4` (`24` Contact Pts: `River People C7/L8` + `Reiko C5/L4`); `Electronics 6` (only 1 chargen-max skill), `Cracking 5`, `Tasking 5`. (`0 CP`, `4 Karma`, `¥1,660` remaining; uses `Scratch-Built Junk` RCC until `Living Network`.)
* **Echoes & CFs:** Day-1 **`Resonance Power: Override`** + **`Overclocking`** (**20d6** Pilot, **5D6** VR Init, `Targeting + Sensor` from Session 1!); Day-1 `Attack Attribution`, `Sleaze Attribution`, `Hyperthreading`, `Resonance Wires`.
* **Post-Chargen Gate (3-Tracker Priority: Submersions $\rightarrow$ Karma $\rightarrow$ Nuyen):**
  * *Submersions (1 Major/SRM):* `1–2` (`Resonance Power: Override`, `Overclocking` @ chargen) $\rightarrow$ `3` (`New Sprite Type`, `5K`) $\rightarrow$ `4` (`Sprite Conduit`, `6K`) $\rightarrow$ `5` (`Living Network`, `8K`) $\rightarrow$ `6` (`Transcendent Network`, `9K`) $\rightarrow$ `7` (`Software Emulator`, `11K`, requires `RES 7`) $\rightarrow$ `8` (`Sprite Link`, `12K`, requires `RES 8`) $\rightarrow$ `9` (`Syntax Error`, `14K`, requires `RES 9`).
  * *Karma Queue:* Bond **Aisling Stage 1 (`Level 5` w/ `Override` + `Overclocking` = `24K`, `20K` net)** immediately as SRM #2 (`Sprite Conduit`) lands, then Stage 2a (`Phantom`/`Cracking`/`Diagnostics`/`Engineering`, `2K` each) $\rightarrow$ **`Diffusion (FW)`** (`Fade 2`) + **`Cleaner`** (`10K`, everyday matrix utilities; no `Infusion [FW]` needed) $\rightarrow$ Veteran/Elite combat & scaling CFs (`Enhance Autosofts`, `Enlighten Automaton`, `Resonance Spike`, `Technoregeneration` @ `5K` each; `Puppeteer` unnecessary w/ `Resonance Wires + Jack Jockey`; Étaín-only `Cyber Spike` deferred until `Sprite Link`—never shared w/ Aisling) $\rightarrow$ Stage 2b (`Level 5->6` + `Con`/`Influence`, `12K`, `44K` total w/ zero waste) $\rightarrow$ key specs & `Candle in the Dark` (`10K`) $\rightarrow$ bank straight to **`RES 7->10` (`35K/40K/45K/50K`)**, raising `Software` Spec/Exp (`Electronics 7+`) only to uncap **Aisling Level 7–10**.
  * *Nuyen Queue (50% DIY, "More Scenes First" $\rightarrow$ "Win More" Later, `Body >> Armor`):* Immediate street kit (`Stun Grenades` for `10S/8S/6S` blasts, `Electricity Resistance` on `Armor Jackets`, `Laser Jacks`, `Sat Links`, `~¥2–3.5k` using `¥2,160` starting cash; `Predator VIs + Silencers` & `Armor Jackets` bought at chargen!) $\rightarrow$ **scene-access priority (`Realistic Features R0->3/4` [`4k¥/rating DIY/hull`] + `Chameleon Coating 4` [`9k¥ DIY/hull`])** $\rightarrow$ **`Enhanced Sensors 2->6->9`** (`17.5k¥ DIY/hull` $\rightarrow$ `Sensor 10` = `20d6` w/ *Sensor Upgrade* & *Pilot Origins*) $\rightarrow$ **`Increased Structural Integrity R1–4`** (`Body 10 -> 14`, `10k¥ DIY/hull`; `Body 10` already ignores point-blank `10S` Stun Grenades Day 1; `15` CM boxes, `DV 14` Stun immunity) $\rightarrow$ `Oracle R4` (`20k¥`; skips hacking software library) $\rightarrow$ optional late limb cybernetics (`Used Cyberarm + Sensor Dazzler` / `Wrist Shields`, skippable) $\rightarrow$ **`Vector Thrust`** (`45k¥ DIY/hull`) & chassis `Standard Armor` strictly at the bottom (**never Full Body Armor**—negligible DR gain vs. high social penalty & flight interference).

---

### C. Percival ("Percy") — *Concept Diff (Not Yet Compiled)*
* **Divergence Philosophy:** Sides with Reiko to keep **Spark 6.00 whole** (`Resonance 6`). Heavy tactical anchor, defensive Matrix shield, and small-unit drone coordinator.
* **Quality Diff (6-Slot Resolution):** Wants both **`Firewall Fortress` (-5K)** and **`Reinforced Firewall` (-7K)**. Because the base already uses 5 slots (`Natural Hacker`, `Sourceror`, `Hooder R3`, `Honorbound`, `Sprite Bane`), Percy must either:
  * *Option 1 (Recommended):* Drop `Sourceror` (-20K) $\rightarrow$ take `Firewall Fortress` (-5K) + `Reinforced Firewall` (-7K), freeing `+8K` for Complex Forms/Specs while keeping all 3 base negatives (6 slots exact: `3 Pos / 3 Neg`), **or**
  * *Option 2:* Keep `Sourceror` + `Firewall Fortress` only (6 slots exact), deferring `Reinforced Firewall` (`7K` $\rightarrow$ `14K` post-chargen).
* **Attribute / Skill Diff:** `Edge 4–5`, `Resonance 6`, `WIL 6, LOG 4, INT 5, CHA 4` (or `INT 6 / LOG 3`); `Computers 6` (`Electronics 6` with Threat Analysis / Computers focus), `Cracking 5`, `Tasking 5`; Knowsoft: `Small Unit Tactics`.
* **Echoes & Chassis:** `Living Network`, `Transcendent Network`; heavy anthroform sentry hull (`Shiawase Man-At-Arms` or `Nissan Samurai`) foregoing `Realistic Features` for armor/body.

---

### D. Cleopatra ("Cleo") — *Concept Diff (Not Yet Compiled)*
* **Divergence Philosophy:** Utilitarian arbitrageur (`Spark 5.01`, Omega codemods including `Synthetic Skill Driver R6` + `Optimized Restoration` + `Data Archive Upgrade`) focused on social manipulation, supply-chain telemetry, and multi-channel action economy.
* **Quality Diff:** Uses the 6th quality slot on **`Multiprocessing` (-11K)** (*H&S*, p. 120) — 6 slots exact (`Natural Hacker`, `Sourceror`, `Multiprocessing` | `Hooder R3`, `Honorbound`, `Sprite Bane: Primal`).
* **Attribute / Skill Diff:** `Edge 4`, `Resonance 5` (post-codemod), `WIL 5, LOG 4, INT 5, CHA 5` (maxed Charisma for social presence & contacts); `Electronics 6` (Matrix Searches), `Cracking 5`, `Tasking 5`; `Con 6 / Influence 6` via `Synthetic Skill Driver R6`.
* **Echoes & Hardware:** `Living Network`, `Overclocking` (legal at Submersion Grade 1–2 per *City Edition* p. 195); civilian-passing chassis (`Evo Orderly` or `Nurse MAID`); `Resonance Focus R4` + `Oracle R4` *(toggled sequentially, as EIs may only keep one focus active at a time)*.
