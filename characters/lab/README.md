# The Character Lab (Pre-Play Incubation & Holding Book)

The **Character Lab** (`characters/lab/`) is the dedicated incubation and theorycrafting workshop for Shadowrun 6th Edition character builds, archetypes, and concept prototypes within `sr6-core`.

---

## 1. The Core Philosophy: The Tabletop Canon Line & Holding Book

In the `sr6-core` ecosystem, there is a strict boundary between **Active Play** and **The Lab**:

```text
       +-------------------------------------------------------------+
       |                     THE CHARACTER LAB                       |
       |    (characters/lab/) - Pre-Play Incubation & Holding Book   |
       |                                                             |
       |  • Holding Book: Shared Quarto book for incubating builds   |
       |  • Ready Prototype Book: Standalone book once lore matures  |
       |  • Fluid mechanics, Session 4 Mulligan benchmarks, 0 drag   |
       +------------------------------+------------------------------+
                                      |
                     [GRADUATION GATE: ACTUAL TABLE PLAY]
                       - Scheduled in active campaign/convention
                       - Audit passes with 0 hard errors
                       - Complete Markdown Trio + Specs initialized
                                      |
                                      v
       +-------------------------------------------------------------+
       |                   ACTIVE CAMPAIGN ROSTER                    |
       |         (characters/<char_id>/) - Tabletop Canon            |
       |                                                             |
       |  • Immutable Chargen Snapshot (locked attributes & essence) |
       |  • Table-consecrated advancement (real GM dates, karma, ¥)  |
       |  • Published Quarto Book & Canonical Narrative Anthology    |
       +-------------------------------------------------------------+
```

* **The Holding Book (`characters/lab/_quarto.yml`)**: Incubating prototypes (`ouro`, `AshE`, `mad_dalek`) live inside this unified Character Lab Holding Book with shared navigation, companion PDF/Roll20 downloads, and standardized evaluation rubrics until they mature enough to warrant their own dedicated multi-chapter narrative book.
* **Ready Prototype Book (`characters/lab/venn/`)**: Once a Lab character accumulates background chapters, twenty questions, and deep mechanics appendices, they graduate into their own standalone Lab Quarto Book (marked `<LAB>`) while awaiting Session 1 at a live table.
* **Active Play (`characters/<char_id>/`)**: Reserved exclusively for characters that have stepped up to a physical or virtual table in an active campaign (e.g., `reiko`, `velvet`). Their chargen snapshot is locked and downtime expenditures are consecrated by table history.

---

## 2. Lab Taxonomy & Current Roster

| Codename / Slug | Archetype & Metatype | Chargen System | Taxonomy | Core Gimmick / Concept Notes | Build / Book |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Venn** (`venn`) | Monad (Human / AI Dual Entity)<br>Street Samurai / Decker | Point Buy 100 (*6WC*) | **Ready Prototype** | Used synthetic cyberlimbs (`AGI 8 / STR 4`, Redliner), Skillwires R6, Nanite Volume 6 (`Monad Matrix Attributes`, `Monad Physical Boost`). Pending SRM 2085 launch. | [Standalone `<LAB>` Book](../venn/index.html) |
| **Ouro** (`ouro`) | AI-Pilot AI (Emergent Intelligence)<br>Technomancer (Sourcerors) | Point Buy (*6WC* + *H&S*) | **Active Concept** | Utilitarian fork of [Sparks Template](sparks_template.md): `Nurse MAID Troll` (~2.0m), 3 Omega codemods (`Spark 5.01`), `Pilot Origins R3`, `Sprite Symbiosis` (Session-1 Machine Ally Sprite). | [Ouro Build](ouro/character_build.qmd) |
| **AshE** (`AshE`) | AI-Pilot AI (Emergent Intelligence)<br>Technomancer (Sourcerors) | Point Buy (*6WC* + *H&S*) | **Active Concept** | Combined handle of **Étaín & Aisling**: Spark Purist (`Spark 6.00`, 0 codemods, `RES 6`, `Edge 6`), twin `Shiawase Silverstar` chassis, Day-1 `Override` + `Overclocking` (**5D6**), Session-4 Music Ally Sprite bond. | [AshE Build](AshE/character_build.qmd) |
| **MAD Dalek** (`mad_dalek`) | Dalakitnon Elf<br>Mystic Adept Decker | Life Path (*6WC*) | **Mechanics Reference** | Double-crucible Life Path (`You were overwhelmed` $\times 2`), Alphaware Cyberjack R1 + Used Skill Rig PACK B (R5), Quickened 4D6 Reflexes & LOG 12 Drain, modular Force 4 Qi Foci. | [MAD Dalek Build](mad_dalek/character_build.qmd) |

> **Takahashi Second-Generation Family Blueprint:** See [Takahashi Second-Generation Sparks Template](sparks_template.md) for the shared Pilot-AI chassis and per-sibling diffs (`Ouro`, `AshE`, `Percy`, `Cleo`).

---

## 3. Graduation Requirements (Moving Out of the Lab)

To graduate a character from `characters/lab/<slug>/` into `characters/<char_id>/`, the build must satisfy all five gates:

1. **Table Commitment & Schedule (The True Trigger)**: Committed seat in a live campaign, convention slot, or SRM season kickoff.
2. **Deterministic Rules Audit Pass**: `uv run sr6 characters audit <id>` passes with **0 hard errors** and exact balance across Karma, Nuyen, CP, Contact Points, and Essence/Spark.
3. **Complete Markdown Trio Initialized**: `core/character_build.qmd`, `core/character_purchases.qmd`, and `core/character_log.qmd`.
4. **Living Specifications Initialized**: `reference/voice_spec.md`, `reference/storyboard.md`, and `reference/visual_anchors.md`.
5. **Ecosystem & Deployment Integration**: Updated in `characters.yaml` (`status: "active"`), compiled cleanly via `uv run sr6 sync-all`, and validated for CommLink 6 XML export.

---

## 4. Character Design Doctrine

### A. Magical Characters (Mystic Adepts & Life Path)

* **Mystic Adepts over Specialists:** Combining Sorcery, Conjuring, and Adept Powers (*Improved Ability* on Combat skills) unlocks unmatched multi-plane flexibility.
* **Life Path over Point Buy:** Life Path grants extra free attribute increments on metatypes with maximums $> 6$ and yields more free spells/PP. **Dalakitnon Elf** (4 boosted maximums: `AGI 7, LOG 8, INT 7, CHA 8`) is our #1 choice; **Pixie** is second (gains flight, higher lifestyle overhead). Use Point Buy only when SRM Life Path restrictions block required metagenic qualities (e.g. Velvet's `CHA 10`).
* **Skillwire Packages:** Almost always mount a Skill Rig (**PACK A Alpha** `318k¥ / 0.96 Ess / R6`, **PACK B Used** `125k¥ / 1.10 Ess / R5`, or **Used R4** `100k¥ / 0.88 Ess`) to cover all tertiary skills for a single point of Essence/Magic, upgradable post-chargen via the **Shadow Healthcare Community (SHC)**.
* **The Coven Decay Protocol:** Join an SRM Coven or MUG at **Connection 7 / Loyalty 8** (15 Contact Pts, 6 Karma). Initiation/Submersion costs `10 + Grade - Loyalty`. Allowing Loyalty to decay naturally ($8 \rightarrow 7 \rightarrow 6 \rightarrow 5 \rightarrow 4$) across Months 1–4 liberates **4 Major Downtime Actions** and saves **¥4,800** in dues before locking permanently at the **Loyalty 4 floor** (1 Minor Action/mo, ¥350/mo dues, permanent `-4` Karma discount). Never hoard 35 Karma prematurely just to save 2 Karma on decay!
* **Foci & Qi Stacking (*CRB* pp. 154–155; *City Edition* `[SR6H-0755]`; *SSW FAQ* `[SSWFAQ-0069]`):**
  * Individual focus Force may never exceed Magic (`Force <= Magic`). Never plan Force 8 Qi Foci at Magic $\le 6$.
  * Qi Foci stack (`[SSWFAQ-0069]`): bond modular **Force 4 Qi Foci** (`1.0 PP` Combat skills = `12,000¥`, `8 Karma`, `Avail 4L`) to reach `+4` max skill boosts cleanly. Total bonded Force cap is **Magic $\times 5$**.
  * **Power Focus R3 (`54k¥ / 18K / Avail 9L`)** yields `+3` across all Magic tests vs. `120 Karma` for natural `Magic 6 -> 9`.
* **Sustaining & Initiations:** **Quickening** (Initiate Grade 1) is the cheapest permanent sustaining engine (`Increase Reflexes` + `Increase Attribute`); **Focused Concentration** is flexible but Karma-expensive. Next initiation priorities: *Channeling*, *Centering*, *Masking*. Third tier to consider: Extended Masking, Flexible Signature, Invocation + Great Form Summoning

### B. Matrix & Emergent Characters (Pilot AI Technomancers)

* **Emergent Intelligences (EI) — Pilot AI Origin & The `DP 9` Mandate:** Access to Resonance + `Pilot Origins` + unlimited physical drone hull upgrades with **zero Resonance loss**. Because `Pilot Origins` caps autosofts at the AI's **Data Processing** attribute (*H&S* pp. 114–115), every Rating 9 autosoft build must maintain an explicit **Data Processing 9** strategy (`AshE`: `Base DP 7 + RES + Toolbox >= 9`; `Ouro`: `Base DP 5 + Toolbox 1 + Machine Ally Sprite Symbiosis 3 = 9`; or `Infusion [DP]`).
* **Anthroform Drone Chassis Selection:** See the **[Anthrodrone Chassis Guide](../../reference/anthrodrone_chassis_guide.md)** as the single source of truth for chassis stats, slot math, Heat modifiers, and starter-to-endgame recommendations.
* **Stream — Sourcerors:** `Hyperthreading` + `-2` Fade + free sustaining slots ($\lfloor \text{Grade}/2 \rfloor$). Functions economically as free scaling `Focused Concentration` (doubled per slot via `Hyperthreading`) plus a `Dissonant Technomancer` Fade discount without Composure erosion.
* **Compositional Day-1 Submersion Pairings:** Technomancers and EIs can submerge twice at chargen (`3K + 4K` under MUG Loyalty 8). Rather than prescribing a single template, the core rule is to pick **two Day-1 echoes that compound each other and your build's chassis/priorities**:
  * *Session-1 Symbiont (`Sprite Conduit` + `Sprite Symbiosis` — e.g., `Ouro`):* Pair with `4` banked Karma to compile & bond a **Level 1 Ally Sprite** in Session 1 (`2K` Reg + `2K` Bond) for instant ASDF boosts and fade-free *Override*.
  * *Active Resonance & Action Economy (`Resonance Power: Override` + `Overclocking` — e.g., `AshE`):* Unlocks Day-1 `20d6` Resonance piloting, `Targeting + Sensor`, and **5D6** VR Initiative (`2` Major Actions), clearing the runway to bond a **Level 3–6 Ally Sprite** by Session 4.
  * *Team PAN & TacApp Anchor (`Living Network` + `Transcendent Network` — e.g., `Percy`):* Establishes the living persona as PAN master from Day 1 while unlocking TacApps and shared team Edge pooling.
  * *Machinist / Fleet Rigger (`Living Network` + `Machine Mind` or `Software Emulator`):* Pairs PAN mastery with direct Control Rig neural interfacing (`Machine Mind` for meat technomancers) or program/autosoft emulation (`Software Emulator`) without spending Nuyen on an expensive RCC.
* **Ally Sprite Cost Formula (*Hack & Slash*, pp. 77–78):** Source Code = `(Level × 2) + Added Powers (+1 ea) + Added Skills (+1 Tech/Knowledge, +2 Social/Combat) + Added CFs/Echoes (+1 ea)`, paid **twice** (Step 3 Permanent Registration + Step 4 Ally Bond).
* **Key Complex Forms & Sustaining Prerequisite:** `Attack Attribution` & `Sleaze Attribution` allow dumping `ATK`/`SLZ` to `1` *only* when paired with a **zero-penalty sustaining strategy for 2 forms (or 1 hyperthreaded pair)**—e.g., `Sourceror` ($\text{Grade} \ge 2$, used by `Ouro` and `AshE`), handing sustaining off to registered/ally sprites, `Focused Concentration`, or another dedicated anchor. Other core forms: `Hyperthreading` (Sourceror only), `Resonance Wires` (pairs with `Jack Jockey`), `Diffusion (Firewall)`, `Machine Merge`, `Enlighten Automaton`, `Enhance Autosofts`, `Resonance Spike`, `Cleaner`, `Technoregeneration`.

### C. Magic vs. Technomancy Symmetry & Force Multiplication Doctrine

* **The Symbiont Parallel (`Channeling` $\leftrightarrow$ `Sprite Symbiosis`) & Session 4 Milestone:** Mage *Channeling* and Technomancer *Sprite Symbiosis* are direct structural mirrors: both grant attribute boosts, access to spirit/sprite powers, and an ablative shield where the symbiont absorbs incoming damage first. While spirits offer broader physical/astral versatility, ally sprites provide massive `+Level/2` Teamwork dice. **Every Mage or EI should unlock their symbiont (`Channeling` or `Sprite Symbiosis` / Ally Sprite) by the Session 4 Mulligan Milestone.**
* **Self-Buff Parity & The Mental Attribute Divide:** Mages rarely sustain buffs on other PCs long-term due to Quickening/sustaining Heat and action penalties. An EI buffing its drone body (*Enlighten Automaton*, *Machine Merge*, *Enhance Autosofts*) is roughly equivalent to a Mage self-buffing—except **Mages uniquely buff Mental Attributes (`+4 LOG/CHA/INT/WIL`)**, whereas EIs cannot without Spark-costly AI mental codemods (*Natural Hacker* substitutes RES on Matrix tests instead).
* **Skill Scaling Parity (`Qi Foci` $\leftrightarrow$ `Sprite Symbiosis Teamwork`):** Modular `Force 4 Qi Foci` (*Improved Ability*) and `Sprite Symbiosis` Teamwork (`+Level/2` dice across shared skills) yield equivalent skill-cap scaling. The key asymmetry is that an adept can boost `Conjuring` by `+4`, whereas a sprite can **never learn `Tasking`**—offset by the fact that technomancers do not need to summon as high-level sprites as mages summon spirits.
* **The Shadowrun Jan-Ken-Pon (Rock–Paper–Scissors):** Overall, Magic vs. Technomancy is a wash—each covers irreproducible tactical dimensions:
  * **Technomancers beat Riggers** (*Override*, *Puppeteer*, *Resonance Wires + Jack Jockey*).
  * **Riggers / EIs beat Mages** (sensor-locked kinetic/laser fire from drones and sprite-crewed platforms outside line-of-sight mana; a Machine Sprite using `Engineering [Gunnery]` fires drone weapons at `Level × 2` dice).
  * **Mages beat Technomancers** (Direct Mana spells vs. low physical/mental stats, Mind Magic, Astral overwatch).
  * *(Meat Street Samurai are collateral damage when caught outside their lane.)*
* **True Map Force Multiplication (Putting a 2nd Body on the Map):** Internal dual-consciousness (`Venn` without *Obsidian Cloud*, or `Ouro` with an internal symbiont in 1 body) does **not** count as map force multiplication. True Force Multiplication requires fielding an independent tactical actor on the physical map:
  * **Mages:** Summon materialized Spirits onto the map from Day 1 (`Conjuring >= 4`).
  * **Twin-Hull EIs (`AshE`):** Field a 2nd `Shiawase Silverstar` from Day 1 using a compiled **Level 6 Machine Sprite** (`Override` + `Engineering/Gunnery 12d6`), transitioning to permanent Ally Sprite `Aisling` at Session 4.
  * **Single-Hull EIs (`Ouro`):** Can add map force multiplication post-chargen for the cost of a **`Hawker-Siddley Bat`** (`~12.75k¥ DIY`, as pioneered by Reiko) piloted by a registered Machine Sprite (`Override` + `Engineering`).

### D. Universal Negative Quality Portfolio (Max 6 Qualities / $\le +20$ Net)

* **Hooder (R3, +15K):** ¥3,000/month tithing directly funds *Working for the People* (`+1` Karma/month).
* **Honorbound: Pirate's Code (+10K):** Zero mechanical drag; unlocks *Candle in the Dark*.
* **Sprite Bane (Primal) / Spirit Bane (Guardian) (+12K):** Virtually absent from SRM encounters and never summoned.
* **Finesse (+7K):** Reduces team Heat modifier by `-1` for subtle operatives.
* **Cyberpsychosis (R3, +24K):** Reserved for extreme low-Essence cyber-monads (`Edge 7` buffer).
* **Glitchy (+12K) / Injury Prone (+15K):** Situational fallback slots when `Sprite Bane` or other slots are swapped.

---

## 5. The Three-Horizon Evaluation Methodology

Builds in the Lab are evaluated deterministically via `uv run sr6 calc eff <char_id>` (`sr6core/creation/efficiency.py`) across **three complementary pillars**—with zero hardcoded character hacks:

### Pillar 1: 20-Point Operational Breadth Score (OBS, 0–20 Scale)

1. **Four Operational Planes (0–3 pts each = 12 pts max)** *(only Sovereign, ~100% uptime buffs counted; unanchored sustaining deducts `-2`)*:
   * **3 pts (Primary Mastery):** Sovereign pool $\ge 14\text{d6}$
   * **2 pts (Secondary Competence):** Sovereign pool `8–13d6`
   * **1 pt (Tertiary Floor):** Sovereign pool `6–7d6`
   * **0 pts (Inert / Blind):** $< 6\text{d6}$
2. **Eight Tactical & Capability Scaffolding Dimensions (+1 pt each = 8 pts max):**
   1. **Defense Floor (`+1`):** Active Defense $\ge 8\text{d6}$.
   2. **Action Economy (`+1`):** Initiative $\ge 2\text{D6}$ or deterministic 2 Major Actions/turn (*Hot-Sim VR*, *Increase Reflexes*, *Overclocking*, *Monad Physical Boost*).
   3. **Deterministic Edge Engine (`+1`):** Reliable Edge generation or cost reduction (*Brilliant Heuristics*, *Wise Warrior*, *Maximum Overdrive*, *Inspire Competence*, *Analytical Mind*, *Jack Jockey*).
   4. **Durability & Soak / Mitigation (`+1`):** High survivability ($\ge 14$ Soak/DR, *Damage Mitigation Protocols*, *Monad Toughness + Rapid Cellular Healing*, *Bone Density*, or heavy/twin drone hulls).
   5. **Sustain & Drain/Fade Economy (`+1`):** Dedicated sustaining & resistance architecture (*Sourceror Stream*, *Quickening*, *Focused Concentration*, or zero-drain augmentation).
   6. **Autonomous Force Multiplication (`+1`):** Independent tactical actor on the physical map (Materialized Spirit via `Conjuring >= 4`, 2nd Drone Chassis crewed by a Sprite/Ally Sprite, or Monad `Obsidian Cloud`).
   7. **Scene Permeability (`+1`):** Social & physical infiltration access (*Realistic Features*, *Chameleon Coating*, *Cosmetic Control*, *Resculpt*, *Gender Transmorphism*, *Masking*, *Phantom*, *Finesse*).
   8. **Burst Ceiling (`+1`):** Peak Sovereign Primary pool reaches **$\ge 18\text{d6}$** (Veteran/Elite readiness).

### Pillar 2: Data-Driven Total Equivalent Karma (TEK & KER)

Measures what the Day-1 build would cost if reverse-engineered into pure post-chargen Karma (`sr6core/creation/efficiency.py`):

* **Attributes & Augmentation Deltas:** Triangular `sum(r*5)` across physical or DI (`ASDF`) attributes + `Nanite_Volume`, plus non-duplicated whole-body marginal deltas for Cyberlimbs (`Redliner`), `Cyber Singularity Seeker`, `Bio-Response Override`, and `Neurochemical Regulator`.
* **Skillwires & Autosoft Dividends:** `Pilot Origins` Control Rig hardware delta (`R3 = +53K`, `R1 = +18K`) + 4 physical domains clamped by effective **Data Processing** (`min(Autosoft, Effective DP)`), deduplicated against `Synthetic Skill Driver` (Social Domain 5: `Con & Influence`) or meat `Skillwires` (5 universal domains at actual rating).
* **Magic / Resonance / Monad Assets:** `Adept Powers` (`15.5K/PP`), `Spells`/`Complex Forms`/`Monad Abilities` (`5K` ea), `Initiation`/`Submersion` (`11K/23K`), bonded `Foci`.
* **Anchored Buffs & Symbionts:** Sovereign `Increase Reflexes` / `Increase Attribute` (`Quickening` / `Focused Concentration`) + `Conjuring Spirit / Channeling` readiness for Mages, paired symmetrically against **Sourceror Hyperthreaded Attribution** (`ATK/SLZ` deltas + free hyperthreaded sustain slot + `-2 Fade`) for Technomancers/EIs.
* **Gear Capital & Quality Arbitrage:** Actual chargen Nuyen spent divided by `2,000¥`, plus `1×` Positive Quality cost saved vs. `2×` post-chargen purchase.

### Pillar 3: The Session 4 SRM Mulligan Checkpoint (+28 Karma / +30,000¥)

Because Shadowrun Missions permits free character rebuilds up through Session 4, every Lab build is benchmarked at **Session 4** assuming **+28 Karma**, **+30,000¥** (`60k¥` DIY / `7k¥:1K` *Shadow Healthcare* leverage), and **4 Major + 4 Minor Downtime Actions** (executing Months 1–2 of the Coven/MUG Decay Protocol at Loyalty 8 $\rightarrow$ 7). This prevents Day-0 static TEK from hiding high-velocity Purist builds (`AshE`, `MAD Dalek`) behind Day-1 codemod/ware spikes.

---

## 6. Unspent Resources & Completeness Gate

| Resource Type | Maximum Allowed Unspent | Failure Consequence |
| :--- | :---: | :--- |
| **Liquid Pocket Cash** | $\le \mathbf{5,000¥}$ | Excess cash is forfeit upon entering play. |
| **Customization Karma** | $\le \mathbf{5\text{ Karma}}$ | Excess karma is forfeit or indicates an unfinished build. |
| **Character Points (CP)** | **0 CP** | Incomplete chargen. |
| **Contact Points** | **0 Points** | Unassigned contacts. |

---

## 7. Benchmark Comparative Scorecard

The live comparative scorecard (Day-1 vs. Session 4 Mulligan Checkpoint, 20-point OBS capability matrix, and data-driven TEK breakdown across all Lab and Active characters) is auto-generated from [characters.yaml](../../characters.yaml) and `sr6core/creation/efficiency.py` during every `uv run sr6 sync-all` and `uv run sr6 build`.

* **Live Scorecard:** **[Benchmark Comparative Scorecard](scorecard.md)**
* **CLI Inspection:** Run `uv run sr6 calc eff <char_id>` for full per-character telemetry.
