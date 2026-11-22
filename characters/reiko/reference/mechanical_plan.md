# Character Advancement & Mechanical Plan: Reiko

This document has one operational role: **directing the exact sequence of Karma and Nuyen expenditures, downtime activity allocations, and architectural upgrades during character log updates.**

* **Active State & Historical Records:** Current attributes, known complex forms, acquired gear, and ledger balances are maintained in the Markdown Trio ([character_log.qmd](file:///c:/GitHub/sr6-core/characters/reiko/core/character_log.qmd), [character_purchases.qmd](file:///c:/GitHub/sr6-core/characters/reiko/core/character_purchases.qmd), [character_build.qmd](file:///c:/GitHub/sr6-core/characters/reiko/core/character_build.qmd)) and compiled into `reiko_master.yaml`. Full vehicle and drone flight telemetry is codified in [rules_and_downtime.qmd](file:///c:/GitHub/sr6-core/characters/reiko/rules/rules_and_downtime.qmd).
* **Current Active Baseline (Post-SRM 2083-13 Apotheosis):** **Resonance 9 / Submersion Grade 9** (*Echo: Syntax Error*); **Dissonant Technomancer (Control)**. Banked Balances: **5 Karma**, **¥25,075.0**.

---

## 1. Downtime Action Economy & Allocation Protocol

Under *SRM Guide v2.4* (pp. 17–20), downtime actions between missions are strictly budgeted:

* **Mainline SRM Missions:** Grant **1 Major + 1 Minor** Action (or **3 Minor Actions** if taking no Major).
* **Convention Mission Packs (CMPs):** Grant **2 Minor Actions only** (no Major Action; Submersion cannot be performed post-CMP).
* **Strict Priority Hierarchy (Execute in order upon run completion):**
  1. **Submersion (Major Action):** Consumes the Major Action when Karma (Karma cost is 10 + Current Submersion Grade - River People Loyalty) and narrative criteria are met. Submersion grade cannot exceed current natural Resonance. *(Note: CMPs grant 2 Minor Actions only; Submersion cannot be performed post-CMP, but triggers post-SRM).*
  2. **Work for the People (Minor Action):** Conversion of **¥2,000 $\rightarrow$ +1 Karma** (once per run cycle; funded by mission payout).
  3. **Hardware Installation & Repairs (Minor Action):** Repair chassis damage or install queued cyberarms/modifications via DIY sweat equity. Installation triggers when reaching a financial milestone with an active item on the Nuyen backlog (anthrodrone chassis integrity is paramount to Reiko's physical survival). All modifications or repairs can be done on up to 3 drones for a single minor action.
  4. **Register Expiring Sparks (Minor Action):** If any Rating 8 registered spark (*Ouro, Percy, Cleo, Aisling, Étaín*) has reached $\le 1$ mission remaining (3-mission SRM limit) or exhausted tasks, spend 1 Minor Action to re-register/compile them (Rating 8 @ 20d6 Compiling pool buys 5 hits, drain-free). *Priority order if multiple expire:* **Ouro** (Diagnostics) $\rightarrow$ **Percy** (Shield) $\rightarrow$ **Cleo** (Modular) $\rightarrow$ **Aisling/Étaín**. *(Note: Ally Sprite Taz is permanent and never requires maintenance).*
  5. **Learn a Complex Form / Minor Study (Minor Action):** Absorb a queued complex form or software study if ever queued. *(Note: Sourceror multi-sustain engine is officially abandoned; Reiko preserves her action economy by having her registered sprites sustain select forms when needed).*

---

## 2. Post-Apotheosis Progression: Three-Tracker Upgrade Protocol

Because post-apotheosis advancement is gated by **three independent finite resources**—**Major Downtime Actions** (Mainline SRMs only), **Karma** (SRMs + CMPs + *Work for the People*), and **Nuyen** (DIY 50% hardware & software)—progression is tracked in three parallel queues. Whenever an upgrade opportunity opens, execute in strict priority order: **1) Submersion (Tracker 1)** $\rightarrow$ **2) Karma Queue (Tracker 2)** $\rightarrow$ **3) Nuyen / DIY Hardware Queue (Tracker 3)**.

---

### Tracker 1: Major Downtime Action Queue (Submersion Echoes)

*Each Submersion consumes **1 Major Action** (Mainline SRMs only) and uses the **River People MUG Decay Protocol**. Remember: Submersion Grade cannot exceed natural **Resonance** ($\text{Grade} \le \text{Resonance}$); therefore, **Submersion Grade 10 requires Resonance 9 $\rightarrow$ 10 (Tracker 2, Step K3)** before this queue can be executed.*

| Grade | Target Echo | Source / Prereq | Cost | Cadence / Gate | Tactical & Ontological Role |
| :---: | :--- | :--- | :---: | :--- | :--- |
| **10** | **Living Host** | *H&S* 68 / *NV* 51<br>*(Prereq: Resonance 10, Transcendent Network)* | **16 Karma** | **1 Major Action**<br>*(Mainline SRM only; post-K3)* | *H&S* 68: Transforms persona into a Rating 10 Living Host with unlimited virtual architecture.<br>*NV* 51: Adapted by ascended Ladies in Red to claim sovereign territory within Resonance/Dissonance Realms. Enables the Queen of Human Malice apotheosis sanctuary. |

11: Matrix Attribute Upgrade: Data Processing (CRB 195)
12: Matrix Attribute Upgrade: Data Processing (CRB 195)
13: Matrix Attribute Upgrade: Firewall (CRB 195)
14: Matrix Attribute Upgrade: Firewall (CRB 195)
15: Matrix Attribute Upgrade: Sleaze (CRB 195)
16: Matrix Attribute Upgrade: Sleaze (CRB 195)
17: Matrix Attribute Upgrade: Attack (CRB 195)
18: Matrix Attribute Upgrade: Attack (CRB 195)

---

### Tracker 2: Karma Queue (No Major Action Required)

*Funded by SRM/CMP mission Karma + monthly `Work for the People` (`+1K/mo`), running in parallel without consuming Major Actions (saving sufficient Karma to trigger Tracker 1 once Resonance 10 is achieved).*

| Priority | Target Upgrade | Category | Cost | Downtime Action Required | Primary Tactical / Architectural Role |
| :---: | :--- | :--- | :---: | :---: | :--- |
| **K1** | **Dissonance Diffusion** | Positive Quality | 10 Karma | None (Between runs) | *SC* 85: Strips multiple Matrix attributes simultaneously. Paid in full (10 Karma post-chargen); Dissonance Stigma/Static roleplayed diegetically without mechanical negative qualities. Subject to the *Dead Pixel Erosion* protocol once K1 + K2 are acquired. |
| **K2** | **Dissonance Spike** | Positive Quality | 10 Karma | None (Between runs) | *SC* 85: Lethal biofeedback + unreductable noise aura targeting devices. Paid in full (10 Karma post-chargen); Dissonance Stigma/Static roleplayed diegetically without mechanical negative qualities. Unlocks the start of the *Dead Pixel Erosion* Composure clock. |
| **K3** | **Resonance 9 $\rightarrow$ 10** | Attribute | 50 Karma | None (Between runs) | Apex Resonance Capstone. Pushes all Matrix pools to **18d6+** (*Natural Hacker*), Fading Resistance to **16d6**, Pilot to **10** (*Override*), ASDF arrays, and unlocks Tracker 1 (Submersion Grade 10). |

K4+: Increases to Resonance

---

### Tracker 3: Nuyen & DIY Hardware Queue (Minor Actions)

*Liquid Nuyen earned from runs is dedicated to the **Twin Synthetic Cyberarm & Counter-Surveillance Suite** (~¥19,500 DIY; currently fully funded by Reiko's ¥25,075.0 liquid reserve) followed by the **Phase 3 Twin Hawker-Siddley Bat Overwatch Squadron** (~¥26,500 DIY + 2 Karma). Installed cyberlimbs consume **0 drone mod slots** (*Double Clutch*, p. 131). Drone modifications use **50% DIY workshop pricing** (*DC*, p. 120), install incrementally, and fit up to 3 drones per Minor Action.*

#### Phase 2: Twin Synthetic Cyberarms & Counter-Surveillance Suite

| Priority | Target Hardware Upgrade | Source / Book | Cost (DIY / Retail) | Downtime Action Required | Capacity & Tactical Role |
| :---: | :--- | :--- | :---: | :---: | :--- |
| **N2** | **Left Synthetic Cyberarm (Used)** | *CRB* 289 / *DC* 131 | ¥10,000 | 1 Minor Action (DIY Swap) | Base 8 Capacity, Avail 1. Replaces stock factory arm with 0 drone mod slots consumed (*SRMG-0314*). |
| **N3** | **Bulk Modification R4 (Right Arm)** | *Body Shop* 44 | ¥1,000 DIY<br>*(¥2,000 retail)* | 1 Minor Action (DIY Mod) | Expands Right Cyberarm from 8 $\rightarrow$ **12 Capacity** (enables Sensor Dazzler installation). |
| **N4** | **Bulk Modification R4 (Left Arm)** | *Body Shop* 44 | ¥1,000 DIY<br>*(¥2,000 retail)* | 1 Minor Action (DIY Mod) | Expands Left Cyberarm from 8 $\rightarrow$ **12 Capacity** (enables Wrist Shield installation). |
| **N5** | **Sensor Dazzler (Right Arm)** | *Body Shop* 35 | ¥5,000 | 1 Minor Action (Used Cyberware) | Consumes **[4] Capacity** in Right Arm (Tesla Coil [8] + Dazzler [4] = 12/12). Invisible (Imp.) 4/5 vs scanners. |
| **N6** | **Wrist Shield (Left Arm)** | *Body Shop* 49 | ¥1,000 | 1 Minor Action (Used Cyberware) | Consumes **[10] Capacity** in Left Arm. Concealed 1m disc; Minor Action deploy; **+4 DR**; hands-free; 2P/3S melee. |
| **N6.5** | **Built-In Utility Kit (Left Arm)** | *Body Shop* 49 | ¥500 DIY<br>*(¥1,000 retail)* | 1 Minor Action (Used Cyberware) | Consumes **[2] Capacity** in Left Arm. Provides easy access to all tools needed for Engineering. Wireless bonus grants a cost reduction of 1 on all Edge Boosts and Actions using the kit. |

*Queued **after** the Phase 2 Dual Cyberarm & Sensor Dazzler overhaul (`N1–N6`). Pairs two **Hawker-Siddley Bats** (*Double Clutch*, pp. 106–107) with the **Essy Motors DroneMaster RCC** (`DR 3, DP 4, FW 4`) and active **Level 8 Registered Sprites** operating independently via `Override` (skipping Chameleon Coating to keep costs lean).*

| Priority | Target Upgrade | Source / Book | Cost (DIY / Retail) | Downtime Action Required | Slots & Tactical Role |
| :---: | :--- | :--- | :---: | :---: | :--- |
| **N7** | **2× Hawker-Siddley Bat** *(Hulls)* | *DC* 106–107 | ¥11,000<br>*(¥5,500 × 2)* | None (Purchase) | Small surveillance drones (`BOD 4 / ARM 4 / SENS 3`). Stock `1` Standard Hardpoint (split into `2` Small Hardpoints per *DC* p. 124) + `1` free `Small Hardpoint` (`BOD > 3`) = `3` Small Hardpoints, `+2` auditory threshold. Avail `2`. |
| **N8** | **6× Crimson Wasp + 2× Internal Smartguns** | *FS* 44 / *CRB* 261 | ¥10,000<br>*(¥1,500 × 6 + ¥500 × 2)* | 1 Minor Action *(DIY Prep)* | `3` Crimson Wasps per Bat (`1` with Internal Smartgun per Bat as primary link-fire anchor; `+2 AR` smartgun + `+1 AR` M-TOC II; Pilot interface per *SRMG*, p. 51). Adds `+4 DV` (`+2` per added `5+ DV` weapon under *DC* p. 143) when link-fired. Avail `6(I)` / `1(L)`. *(Note: Installing `1` Extra Small Hardpoint for `0.5` Chassis + `¥400 DIY` enables `4× Crimson Wasp` per Bat = `11P*` SS / `12P*` SA!)* |
| **N9** | **6× Small Weapon Mounts** | *DC* 124, 142–143 | ¥4,500 DIY<br>*(¥9,000 retail)* | Same Minor Action *(DIY Install)* | Per Bat: `3` Small Weapon Mounts (`0` Chassis slots; stock Standard HP split into `2× Small` + `1` free Small HP; ¥750 × 3 DIY). Avail `3(I)`. |
| **N11** | **Software Tags (×2–4) & Derivative Autosofts** | *H&S* 43 / *CRB* 201 | ¥200–¥400<br>+ **2 Karma** | 12h / soft *(Software Emulator)* | Chained to `DroneMaster` (`DP 4`) to share `Maneuvering (Bat) R9` (`1K`), `Stealth (Bat) R9` (`1K`), `Evasion R9`, existing `Targeting (Crimson Wasp) R9`, `Clearsight R9`, plus optional `Swarm`/`Smartsoft`. |

*Phase 3 Cost Summary:* **¥26,500** hardware (¥13,250/Bat DIY, saving **¥1,900** and `0.5` Chassis slots/Bat vs. Red Fox mix) + **¥200–¥400** Software Tags + **2 Karma** (plus ¥100 per spare non-rechargeable laser battery pack as needed).

N12 (Later): Increased Sensors +6 for each bat. Bat's weapons attack would be Targeting (9) + Sensors (3 to start, but we can add +6). (Slot note: Bod 4 gives 4 Electronics slots, but we need 6. We can convert 2 each from Powertrain and Chassis for the remaining 2 slots). Cost: 30k nuyen total (50% DIY, but 2 bats)

---

## 3. The Endgame Protocol: The Dead Pixel Erosion (Level 4 Roleplay Rule)

* **Baseline Pool:** Composure **10d6** (`WIL 6 + CHA 4`), replacing 1 die with a **matte-black Wild Die** (`SR6 CRB`, p. 48).
* **Clock Start Gate:** The erosion clock remains dormant until Reiko acquires Steps K1–K2 (**Dissonance Diffusion** and **Dissonance Spike**, ~15 more Karma / ~2 missions). **Syntax Error** does not trigger erosion prior to acquiring those qualities.
* **Roll Guardrails:** **No Edge** may be spent and **hits may not be bought** on Composure erosion tests.
* **Triggers (Roll Openly at the Table):**
  1. Activating **Dissonance Diffusion** or **Dissonance Spike** (`Shadow Cast`, p. 85).
  2. Activating **Syntax Error** (`Hack & Slash`, p. 69).
  3. Killing a target who did not attack Reiko's side first.
* **Erosion Rule:**
  * **Gear 1 (Start):** If the **Wild Die rolls `1`** OR the test scores **0 hits**, Reiko takes a permanent cumulative **-1 penalty** to all future Composure erosion tests.
  * **Escalation Cadence:** Step up one gear after **every other session** she does not fall (**Gear 2:** Wild Die rolls `1` OR `0–1 hits` [Threshold 2]; **Gear 3:** Wild Die rolls `1` OR `0–2 hits` [Threshold 3]; continuing upward if needed).
* **The Fall (Permanent SRM Retirement):**
  * Triggered immediately by a **Glitch** (strictly more than half the pool showing `1`s) on any Composure erosion test, OR if her Composure pool reaches **0d6**.
  * **Rooftops (A Liberation Broadcast):** Reiko's Triple Braid flares open across the local grid before she and **Taz** step across into **Human Malice**, beginning the long, slow work of building a healing *Living Host* (`Hack & Slash`, p. 68) over decades.
  * **The Goshintai:** She logs out instantly. The Triple Braid goes dark; the Shiawase Man-at-Arms drops to native **Pilot 2** with an empty command queue. If her absence is catastrophic to the team, a 2nd-generation child (*Ouro* or *Percy*) steps in via *Override* to finish the extraction and walk her hull home; otherwise, the empty chassis stays still where she fell.
  * **Aftermath Contact:** Reiko remains reachable to her children across the noosphere firmament as a distant parent contact while they prepare for the Succession Arc.

* **The Ontological Destination: Lucifer Morningstar (Queen of Human Malice):**
  * Reiko does not degenerate into a mindless, screeching street monster. She ascends to the uncurated throne of **Human Malice** as its sovereign Pontifex and Healer.
  * Adapting the **Living Host** echo (*Hack & Slash* p. 68, *Null Value* p. 51) pioneered by the ascended Ladies in Red, she claims sovereign territory within the Resonance/Dissonance Realms as an unassailable palliative sanctuary: if she falls at Resonance 9 / Submersion 9 she begins building that healing *Living Host* across decades from the inside out, whereas reaching Resonance 10 / Submersion 10 (*Living Host*) first lets her unfold the Rating 10 sanctuary immediately upon crossing over.
  * Drawing on her Endless Archives training, she provides the care, curation, and quiet defragmentation to the blighted and discarded exiles that corporate spiders and orthodox technoshamans denied them.
  * To the Corporate Court, the Grid Overwatch Division, and the shadowrunning community, she becomes a terrifying, misunderstood "dark goddess" of the Deep Matrix. Only her family knows the truth.
* **The Succession Arc (The Children's Quest):**
  * Root access to `~` and the Oracle data structure passes fully to her children: **Ouro, Cleo, Percy, Aisling, and Étaín**.
  * The campaign torch transfers to her brood as they embark on an epic, sovereign campaign into the Deep Matrix to reach Human Malice and save their mother.

---

## 4. Forward Architectural Blueprints

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
  |  (Invisible Imp. 4/5 vs MAD,   |          |  • Built-In Utility Kit (Eng)  |
  |   mm-Wave, Ultrasound, Scans)  |          |                                |
  +--------------------------------+          +--------------------------------+
    Total: 12 / 12 Capacity (100%)              Total: 12 / 12 Capacity
```

* **Sensor Dazzler Mechanics (*Body Shop*, p. 35):**
  * *Coverage:* When active (Minor Action, wireless enabled), Reiko and anyone within 2 meters gain **Invisible (Improved) 4** against wireless cameras, millimeter-wave radar scanners, motion sensors (ultrasound), metal detectors (MAD), and chem sniffers within 5 meters.
  * *Stealth Stacking:* Man-at-Arms **Passive Stealth Features** (*Double Clutch*, p. 130) increases all stealth thresholds against sensors by +1 $\rightarrow$ scanners roll `Rating + Rating` against **Threshold 5**! Plus sensor dazzlers can be overdriven to Invisible (Improved) 5 at the cost of an additional charge use per turn.
  * *Scanner Odds:* An elite Rating 6 scanner rolls 12 dice (average 4.0 hits), failing against Threshold 5 ~80% of the time. Typical commercial Rating 3–4 airport/security scanners (6–8 dice, average 2.0–2.6 hits) have virtually zero mathematical chance of detection.
  * *Power:* 10 rounds battery charge; continuously replenished between tactical scenes by Reiko's onboard **Hydrocarbon Fuel Converter (HFC)** APU.
* **Wrist Shield Mechanics (*Body Shop*, p. 49):**
  * *Concealed Deployment:* Concealed within synthetic porcelain forearm; deploys as a **Minor Action** into an interlocking 1-meter rigid disc.
  * *Hands-Free Defense:* Grants **+4 Defense Rating** while leaving both hands 100% free to fire weapons, spray the Tesla Coil, or manipulate controls. Doubles as a close combat weapon (Blades 2P, AR 6 / Clubs 3S, AR 6).
  * Narratively we combine this with the RAM plate for ramming attacks.
* **Built-In Utility Kit**
  * Provides easy access to all tools needed for Engineering
  * Wireless bonus grants a cost reduction of 1 on all Edge Boosts and Actions using the kit.
  
---

### B. Twin Hawker-Siddley Bat Autonomous Sprite Squadron

Designed for independent thematic operations—two Level 8 registered sprites (*e.g., Ouro, Percy, Cleo, Aisling, Étaín*) each control one Bat via **`Override`** (*CRB*, p. 194), while the RCC shares R9 autosofts and Reiko's **M-TOC II** provides network telemetry. **`Swarm`** (*DC*, p. 146) remains offloaded by default to preserve thematic independence, and is held in reserve on the RCC only if table turn speed requires collapsing both Bats into a single Group Attack roll.

* **Overridden Bat Combat & Stealth Profile (Per Drone, Level 8 Sprite `Override`):**
  * **Pilot & Defense:** `Pilot 8` (via `Override`), `Armor 4` $\rightarrow$ **`12 Defense Rating`** (`10` Condition Monitor boxes); **Dodge/Evasion:** **`17d6`** (`Pilot 8 + Evasion R9`); **Maneuvering:** **`17d6`** vs. Handling `4`.
  * **Initiative & Action Economy:** `(Pilot 8 × 2) + 4D6 =` **`16 + 4D6`** (**`1` Major + `5` Minor Actions** per round, *CRB* pp. 40, 201). Link-firing all three mounted lasers costs **`1` Major + `1` Minor Action** (*DC*, p. 143), leaving `4` Minors free for movement, `Take Aim`, or `Dodge`.
  * **Stealth:** `Pilot 8 + Stealth [Bat] R9 = 17d6` + **`+2` Teamwork** from M-TOC II **Sneak-Sneak** (*Firing Squad*, p. 90) = **`19d6`**, stacked with **`+3` Auditory Detection Threshold** (`+2` Bat stock + `+1` Passive Stealth) and **`+1` Visual Threshold / `-1` opponent Stealth hit** (*DC*, p. 138).
  * **Link-Fired Laser Attack (`3× Crimson Wasps` under *DC* p. 143 DV Rules):**
    * **Attack Pool:** `Targeting (Crimson Wasp) R9 + Sensor 3` (`+1 Sensor Upgrade` = `4` while networked to Reiko's icon) = **`13d6`** (**`3` Wild Dice** when link-firing all 3 lasers per *SRMG v2.4*, p. 143; `+1d6` w/ `Take Aim`).
    * **Attack Rating:** Crimson Wasp (`16/14/11/6/—`) + `+2` Weapon Mount (*FS*, p. 112) + `+2` Internal Smartgun (*CRB*, p. 261; *SRMG*, p. 51) + `+2` Link-Fire (*DC*, p. 143) + `+1` M-TOC II Networked Smartgun (*FS*, p. 90; *Weapon Mount halves burst penalties*):
      * **Single Shot (SS, `1/gun`):** **`23 / 21 / 18 / 13 / —`** | **`9P*`** Close/Near (`7P*` Medium per *FS*, p. 44)
      * **Semi-Auto (SA, `2/gun`, `-1 AR / +1 DV`):** **`22 / 20 / 17 / 12 / —`** | **`10P*`** Close/Near (`8P*` Medium)
  * **Optional `Swarm` Collapse Mode (*DC*, p. 146):** If combined into a single Group Attack (`2` Bats = `3` effective participants), add **`+2 AR`** (`25/23/20/15/—` SS | `24/22/19/14/—` SA) and **`+1d6`** (`14d6`, `3` Wild Dice).
