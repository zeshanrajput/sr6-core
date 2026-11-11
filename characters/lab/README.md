# The Character Lab (Pre-Play Incubation & Theorycrafting)

The **Character Lab** (`characters/lab/`) is the dedicated incubation and theorycrafting workshop for Shadowrun 6th Edition character builds, archetypes, and concept prototypes within `sr6-core`.

---

## 1. The Core Philosophy: The Tabletop Canon Line

In the `sr6-core` ecosystem, there is a strict boundary between **Active Play** and **The Lab**:

```text
       +-------------------------------------------------------------+
       |                     THE CHARACTER LAB                       |
       |      (characters/lab/<slug>/) - Pre-Play Incubation         |
       |                                                             |
       |  • Fluid mechanics: change attributes, swap ware, rebuild   |
       |  • No table consequences: scratch karma/nuyen balances      |
       |  • Prototypes, rule benchmarks, and living concepts         |
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

* **Active Play (`characters/<char_id>/`)**: Reserved exclusively for characters that have stepped up to a physical or virtual table in an active campaign (e.g. `reiko`, `velvet`). Their chargen snapshot is locked, downtime expenditures are consequential, and their narrative is directly consecrated by table events.
* **The Lab (`characters/lab/<slug>/`)**: For everything else. Until a character plays Session 1 at a live table, they remain in the Lab. You are free to radically overhaul attributes, tune cyberware grades, swap spells/complex forms, or rewrite backstories without guilt or fear of corrupting campaign history.

---

## 2. Lab Taxonomy

Every entry in the Lab belongs to one of three developmental stages:

| Taxonomy | Definition | Typical Structure | Example |
| :--- | :--- | :--- | :--- |
| **Active Concept** | In-progress build exploring specific mechanics, archetypes, or rules subsystems. Highly fluid. | Single `character_build.qmd` + optional `notes.md` | `ouro` (Point Buy AI-Pilot Technomancer) |
| **Mechanics Reference** | Preserved build study benchmarked to test specific rules edge-cases, life paths, or priority arrays. | Single `character_build.qmd` | `mad_dalek` (6WC Life Path double-crucible) |
| **Ready Prototype** | Mechanically complete portfolio with lore, reference specs, and narrative, awaiting table launch. | Full portfolio (`core/`, `narrative/`, `reference/`, `_quarto.yml`) | `venn` (Monad Street Samurai / Operative) |

---

## 3. Current Lab Roster

| Codename / Slug | Archetype & Metatype | Chargen System | Taxonomy | Core Gimmick / Concept Notes | Status |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **[`venn`](venn/)** | Monad (Human / AI Dual Entity)<br>Street Samurai / Operative | Point Buy 100 (*6WC*) | **Ready Prototype** | Used synthetic cyberlimbs (0.1 Essence), nanite swarm volume, hot-sim VR skillwires array. Pending SRM 2085 table kickoff. | Fully built; chapters 01–07; mutable |
| **[`ouro`](ouro/)** | AI-Pilot AI (Emergent Intelligence)<br>Technomancer (Sourcerors) | Point Buy (*6WC* + *H&S*) | **Active Concept** | Anthro Nurse Maid drone rigger frame, Crack sprite symbiosis, ASDF attribution, living persona. kin to Reiko. | Chargen complete; post-chargen mapped |
| **[`mad_dalek`](mad_dalek/)** | Dalakitnon Elf<br>Mystic Adept | Life Path (*6WC*) | **Mechanics Reference** | Implanted cyberjack + skillwires (Option B), exercising the double-event crucible rule. Full astral + Matrix flexibility. | Complete reference build |

---

## 4. Graduation Requirements (Moving Out of the Lab)

To graduate a character from `characters/lab/<slug>/` into `characters/<char_id>/`, the build must satisfy all five gates:

1. **Table Commitment & Schedule (The True Trigger)**:
   * The character must have a committed seat in an actual live game: an upcoming convention slot, an SRM season kickoff, a home campaign session 1, or formal GM sanctioning.
   * *If a character is finished but has no active game scheduled, they remain in the Lab as a Ready Prototype.*
2. **Deterministic Rules Audit Pass**:
   * Must pass `uv run sr6 characters audit <id>` with **0 hard errors**.
   * Exact balance across Karma, Nuyen, Skill points, Quality balance, and Essence legality.
3. **The Complete Markdown Trio Initialized**:
   * `core/character_build.qmd`: Complete starting build.
   * `core/character_purchases.qmd`: Starting gear, lifestyle, weapons, armor, vehicles, and bonded foci with exact costs.
   * `core/character_log.qmd`: Initialized with Session 0 / Chargen credit and initial contact roster.
4. **Living Specifications Initialized**:
   * `reference/voice_spec.md`: Sensory matrix, POV integrity, and character-specific anti-slop rules.
   * `reference/storyboard.md`: 6 thematic verticals (internal & external) and initial bespoke foils mapped.
   * `reference/visual_anchors.md`: Physical appearance and sensory cues defined.
5. **Ecosystem & Deployment Integration**:
   * Updated in [`characters.yaml`](file:///c:/GitHub/sr6-core/characters.yaml) with `repo: "characters/<char_id>"` and `status: "active"`.
   * Master YAML compiled cleanly via `uv run sr6 sync-all`.
   * CommLink 6 XML export validated for physical table play (`uv run sr6 export <id> --format=xml`).

---

## 5. Starting a New Build in the Lab

To spin up a new idea:

1. Create a new directory: `characters/lab/<slug>/`.
2. Add a `character_build.qmd` containing the reactive Python math blocks:

   ```markdown
   ---
   title: "Character Creation (<Method>)"
   identity:
     id: <slug>
     name: "<Full Name>"
     handle: "<Handle>"
     metatype: "<Metatype>"
     system: shadowrun6e
   ---
   ```

3. Register the new concept in the Roster table in this README.

---

## 6. The Two-Pillar Character Evaluation Rubric

Every build in the Lab is evaluated across two distinct, complementary axes: **Operational Strength** (how effectively the build performs at the table) and **Build Efficiency** (how effectively the build maximizes post-chargen Karma value).

---

## Character Design Strategies

### Magical Characters

* We favor **Mystic Adepts** over Traditional Mages, Aspected Mages, or Adepts due to their versatility of having both spells and adept powers
* We favor **Life Path** chargen system over Point Buy
  * Mystic Adepts gain more spells and adept powers "for free" versus other chargen methods.
    * Note: do not buy adept powers for karma in chargen. Qi Foci cost 1 less karma and 6000 nuyen post-chargen.
  * Any character gains additional attribute points for any attribute that starts with a maximum greater than 6
  * We favor **Dalakitnon** as they have the most (4) attributes that gain these additional points
  * **Pixies** are a close second; versus Dalakitnon they gain flight but have increased lifestyle costs
  * In SRM under Life Path a character cannot start with metagenetic qualities. If these are necessary to the build, we must then use another chargen method (Velvet is an example of this, where we needed metagenetic charisma to achieve the character design goal of Charisma 10 at creation)
* We will almost always start with one of the following **Skillwire packages**, depending on resource availability:
  * Skill Rig Pack A, alpha quality (318,000 nuyen, 0.96 Essence, rating 6)
  * Skill Rig Pack B, alpha quality (265,000 nuyen, 0.8 Essence, rating 5)
  * Skill Rig, used quality (100,000 nuyen, 0.88 Essence, rating 4)
  * All of these are chosen to provide cost effective access to all skills with only a single point loss of Essence/Magic
  * Choosing a higher rating rig at chargen is not imperative, as these can be upgraded post-chargen cost effectively by joining the Shadow Healthcare Community (SHC) (6 karma, see SRM Guide, can be done post-chargen)
* Covens & The Coven Decay Protocol
  * We will generally have mage characters join one of the covens in the SRM Guide.
  * We will join either at Loyalty 4 or 8. This reduces the karma cost of all initiations by the loyalty rating:
    $$\text{Cost} = 10 + \text{Initiate Grade} - \text{Coven Loyalty}$$
    * **Loyalty 4:** Requires 1 minor downtime action per month and modest dues to maintain.
    * **Loyalty 8 Decay Protocol:** We enter at Loyalty 8 and deliberately allow loyalty to decay by 1 per month ($8 \rightarrow 7 \rightarrow 6 \rightarrow 5 \rightarrow 4$). This liberates 4 Major Downtime Actions across Months 1–4 for initiations and saves ¥4,800 in dues.
    * **The Loyalty 4 Floor:** Decay halts permanently at the Loyalty 4 floor (1 Minor action/mo, ¥350/mo dues for Connection 7), locking in a permanent **-4 Karma discount** on all subsequent initiations forever.
    * **The "Hoard Magic" Fallacy vs. The 2-Karma Difference:** Delaying an initiation (like Grade 7) from Loyalty 6 to the Loyalty 4 floor costs only **2 Karma** ($10 + 7 - 4 = 13\text{K}$ vs $10 + 7 - 6 = 11\text{K}$). Freezing 35 Karma to raise Magic $6 \rightarrow 7$ prematurely purely to preserve coven discounts is a false economy: it starves the character of table performance for 4–5 missions to save a trivial 2 Karma!
* Foci Architecture & The Power Focus Arbitrage
  * **The Power Focus vs. Natural Magic Arbitrage:**
    * A Power Focus Rating 3 costs **54,000¥ and 18 Karma** (Availability 9L).
    * It grants **+3 to effective Magic across ALL tests involving Magic** (Spellcasting, Counterspelling, Rituals, Conjuring, Banishing, Astral tests, and Drain Resistance).
    * Achieving a +3 bonus through natural Magic advancement ($6 \rightarrow 7 \rightarrow 8 \rightarrow 9$) costs an astronomical **120 Karma**!
    * Convention Mission Packs (CMPs) grant nuyen (~15,000¥–25,000¥) and 2 Minor Downtime Actions (no Major action), making them ideal for funding and bonding foci without burning initiation opportunities.
  * **The Legal Qi Foci Stacking Architecture (*CRB* p. 154–155; *City Edition* p. 154–155 `[SR6H-0755]`; *SSW FAQ* `[SSWFAQ-0069]`):**
    * *Individual Force Cap:* *"No focus Force may exceed your Magic attribute."* At Magic $\le 6$, Force 8 Qi Foci are **ILLEGAL** ($8 > \text{Magic}$). Never plan Force 8 foci for characters with Magic 5 or 6.
    * *Modular Stacking:* Per `[SSWFAQ-0069]`, Qi Foci explicitly stack!
      * For Combat skills (1.0 PP/rank per FAQ: Sorcery, Conjuring), use modular **Force 4 Qi Foci** (Rating 1 each, 1.0 PP, Avail 4L, 12,000¥, 8 Karma).
      * To reach +2 on Conjuring at Magic $\le 6$, bond **two Force 4 Qi Foci** instead of one illegal Force 8 focus.
      * Availability 4L is readily available through mid-tier fixers (Connection 4–5) without high-availability rolls or black clinic time.
  * **Total Bonded Force Cap (*City Edition: Seattle* p. 154–155 `[SR6H-0755]`):**
    * The total bonded Force limit is **Magic x 5** (NOT the pre-errata Magic x 3). At Magic 5, this allows up to **25 Force** across up to 5 foci; at Magic 6, **30 Force** across up to 6 foci.
  * **Sustaining Focus Force Requirement:**
    * A sustaining focus must equal or exceed the modified Drain Value of the spell (*CRB* p. 155).
    * *Increase Attribute* at the max +4 bonus has a modified DV of 6 (Base 3 + 3 net hits), requiring a **Force 6 Sustaining Focus** (24,000¥, 12 Karma, Avail 6L).
* Sustaining Strategy
  * Quickening: Cheapest option by far. Spells cost karma to reapply if they are dropped
  * Focused Concentration: Allows us to drop and change spells at will, far more expensive and limited slots
  * Sustaining Foci: Relatively expensive, limited to one school, and same cost post-chargen
* Initiations
  * We can take one initiation at chargen
  * Quickening is the highest priority if that is our sustaining strategy
  * Channeling is the next highest priority for attribute bonuses, dual nature, and access to spirit powers
* Spells
  * Increase Attributes and Increase Reflexes are the highest priority
* Adept Powers
  * One of the few ways to gain bonuses to Sorcery
  * Qi Foci are cost effective and are the same cost post-chargen (stacking Force 4 foci for Combat skills)

### Matrix Characters

* We favor **Emergent Intelligences (EI)**
  * Emergent Intelligences have access to Resonance abilities versus other Artificial Intelligences
  * Emergent Intelligences have access to 'Pilot Origins', a highly effective vehicle for most required skills (see skillwires/autosofts section below). We take this on every character, almost always through the Pilot AI origin.
  * Emergent Intelligences can perform a nearly unlimited amount of modification to their drone physical bodies without diminishing their Resonance
  * We will purchase an anthroform drone with realistic features in chargen to allow the character to function in normal society
    * The Ares Nurse MAID (DA 176, 57500 nuyen; BOD 8, ARM 6, realistic features 4 without using mod slots)
    * The Shiawase Butler (DC 117, 3000 nuyen, realistic features 1 but BOD 4, ARM 0)
    * Shiawase Man-At-Arms (DC 118, 4500 nuyen, BOD 10, ARM 8, but no realistic features)
    * Shiawase Silverstar (Tarnished Star 158, 9000 nuyen, BOD 8, ARM 4, realistic features 1)
    * Nissan Samurai (CRB 300, 4500 nuyen, BOD 6, ARM 6. Strictly worse than the Man-At-Arms)
    * Large Drones (Nurse MAID Troll, Nissan Oni): higher sensor max rating but less discreet
* **Technomancers** are a close second.
  * They cannot modify their bodies as much, but they can benefit from magical buffs
  * We would take one of the **skillwire packages** discussed above for the same reasons
* We favor the **Point Buy** system for Matrix Characters
  * EIs cannot use the life path creation system
  * Point Buy allows for more efficient access to nuyen versus the Priority or Sum-to-Ten systems
  * A technomancer could consider Life Path as a Dalakitnon for the reasons in the magic section. Pixies do not get logic bonuses.
* Matrix User Groups (MUGs) function like a coven for technomancers and EIs. We follow the same logic as we do for covens.
* Stream: We favor **Sourcerors** for:
  * Action Economy (hyperthreading allows us to thread two complex forms at once)
  * Sustaining Economy (sustaining a hyperthreaded form allows us to sustain 2 or 4 complex forms as a single sustained form)
  * Sustaining Slots (Free "Focused Concentration" for complex forms at Submersion grade / 2, rounded down)
  * This can be taken post-chargen as the karma cost is the same.
* Foci
  * EIs can only use one at a time. We highly favor the Resonance Focus.
  * Technomancers can add an Oracle and other foci as interested.
  * Foci cost the same post-chargen, so they can be deferred.
* Submersions
  * TMs and EIs can submerge twice in chargen. Sourcerors want to do both to unlock their 1st sustaining slot.
  * Options:
    * Sprite Conduit and Sprite Symbiosis: Unlocks ally sprite symbiosis on day 1 for +6 matrix attributes and either Phantom (most likely) or Override
    * Living Network and Transcendent Network: Unlocks TacApps and Edge Storage for the team
    * Living Network and Software Emulator: There are other ways for EIs to run programs, but TMs might value more
    * Overclocking: Eventually necessary for action economy
* Complex Forms
  * Cost the same post-chargen, so only prioritize attack and sleaze attribution in chargen if these stats are dumped
  * Attack and Sleaze Attribution
    * Replace these stats, allowing us to dump them in chargen
    * For Sourcerors, this is a single sustaining slot for scenes where we are primary technical
  * Diffusion (Firewall): Essential for tackling high firewall hosts, either alone or in a team
  * Machine Merge, Enhance Autosoft, and Enlighten Automaton
    * All three add different bonuses to operating our drones under pilot origins
  * Resonance Wires
    * Establishes a direct connection to any visible device
    * Strong synergy with the 'Jack Jockey' quality (as a quality, this should be taken in chargen if desired)
  * Resonance Spike: Not susceptible to P-ICE Spines
  * Cyber Spike: devastating to enemy deckers and riggers
  * Puppeteer: nice for taking a quick shortcut to control devices sometimes
  * Editor: same for editing files, but less useful as you usually have to hack a network anyway to see the files
  * Technoregeneration: Heal spell for drones. Damage can generally be avoided, but when you need it you need it
  
#### Negative Qualities

Recall the max of 6 qualities and a 20 bonus karma net cap from qualities. We will generally take 2-4 negative qualities per character, and our positive qualities will generally be high cost/value (10+ karma).

Favored for all characters:

* Hooder (R3)
  * 15 bonus karma
  * costs 3000 nuyen per month, which counts towards 'working for the people'
* Honorbound: Pirate's Code
  * 10 bonus karma
  * Enables access to 'Candle in the Darkness'
  * No real tabletop impact
* Spirit Bane (Guidance Spirits) or Sprite Bane (Primal Sprites)
  * 12 bonus karma
  * These spirits/sprites do not appear in missions and are rarely useful to summon
* Cyberpsychosis: only for very low essence characters (such as Venn)

Negative Qualities "with benefits":

* Finesse (6WC 137)
  * 7 bonus karma
  * Lowers team heat modifier by -1

If absolutely necessary:

* Injury Prone (6WC 137): 15 bonus karma, taking damage can generally be avoided (caution in characters vulnerable to fading)
* Glitchy (6WC 137): 12 bonus karma, glitches are very rare

---

### Pillar 1: Operational Strength Rubric (Table Performance)

#### 1. The Pareto Principle of Buff Reliability

When calculating expected dice pools, only **Sovereign, High-Uptime Buffs ($\approx 100\%$ availability)** are included:

* **Included**: Bonded foci, ally sprite symbiosis, installed augmentations, active autosofts, sustained spells with dedicated sustaining anchors (*Focused Concentration*, Quickening, Sustaining Foci, or Spirits).
* **Excluded**: Teamwork tests ($\le 20\%$ reliable), situational environmental Edge, or temporary tactical buffs.
* **The Sustaining Penalty Rule**: If a build sustains a spell *without* dedicated sustaining mitigation, a **$-2$ penalty** must be deducted from all active operational pools.

#### 2. Pool Benchmarks & Competence Floors

| Pool Tier | Standard Difficulty | Veteran Difficulty | Elite / Prime Difficulty | Role in Play |
| :--- | :---: | :---: | :---: | :--- |
| **Primary** | **14+ Dice** | **20+ Dice** | **26+ Dice** | Core archetype specialty (Hacking, Sorcery, Face negotiation, Firearms) |
| **Secondary** | **8+ Dice** | **14+ Dice** | **20+ Dice** | Secondary operational role (Rigging, Close combat, Astral defense) |
| **Competence Floor** | **6+ Dice** | **12+ Dice** | **18+ Dice** | Universal survival baseline (Perception, Stealth, Con, Athletics) |

#### 3. The "Skillwires / Autosofts Mandate"

Buying broad tertiary skills (Perception, Stealth, Athletics, Con, Piloting, Engineering) with raw Karma at chargen or in play is a massive Karma trap.

* **The Mandate**: Every Lab prototype should default to having **Skillwires (for meat)** or an **Autosoft array (for riggers/AIs)** to cover the Competence Floor at Rating 4–7 on demand. Omitting skillwires requires an explicit thematic justification.

#### 4. The Three Tactical Bonuses

* **Bonus A — Defensive Secondary**: Meeting the Secondary threshold on Defense (REA + INT). Tactical positioning, cover, and drone meat shields can protect a glass face or remote hacker, but having defense reach secondary status provides crucial insurance.
* **Bonus B — Dedicated Edge Engine**: A deterministic mechanism for generating 1–2 Edge per turn without relying on fiddly AR/DR differentials (e.g. *Inspiring Confidence*, *Analytical Mind*, *Aptitude*, or stream/tradition mechanics).
* **Bonus C — Action Economy**: Access to $\ge 2\text{D}6\text{–}3\text{D}6$ Initiative (allowing 4 Minor Actions to be traded for a 2nd Major Action). Can be deferred to post-chargen advancement.

#### 5. The Operational Breadth Score (OBS, 0–15 Scale)

To measure how effectively a character engages the game when scenes shift across Shadowrun's four operational planes (Astral, Matrix, Physical, Social), builds are evaluated on the **Operational Breadth Score (OBS)**:

* **The Four Operational Theaters (0–3 pts each, max 12 pts)**:
  * **3 pts (Primary Mastery)**: Sovereign pool $\ge 14\text{+ dice}$. Archetype lead.
  * **2 pts (Secondary Competence)**: Sovereign pool $\ge 8\text{–}13\text{ dice}$. Backup / reliable operative.
  * **1 pt (Tertiary Floor)**: Sovereign pool $\ge 6\text{–}7\text{ dice}$. Basic self-sufficiency floor.
  * **0 pts (Inert / Blind)**: $< 6\text{ dice}$ or cannot interact (mundane in Astral; commlink-only in Matrix).
* **The Three Tactical Scaffolding Bonuses (+1 pt each, max 3 pts)**:
  * **Defense Floor (+1 pt)**: Defense pool $\ge 8\text{+ dice}$.
  * **Dedicated Edge Engine (+1 pt)**: Deterministic generation (*Inspiring Confidence*, *Analytical Mind*, *Aptitude*).
  * **Action Economy (+1 pt)**: Initiative $\ge 2\text{D}6\text{–}4\text{D}6$ (unlocking 2 Major Actions).

##### The Declared Operational Pools Standard

Rather than guessing complex multi-source stackings, every build declares its peak expected pools at the end of `character_build.qmd`:

```markdown
## Starting Operational Pools

* **Astral**: Sorcery (3) + LOG (12) = 15d6 | Conjuring (6) + MAG (5) = 11d6
* **Matrix**: Cracking/Electronics (5) + LOG (12) + Brilliant Heuristics (3) = 20d6
* **Physical**: Firearms/Stealth: Skillwires (3) + AGI (3) = 8d6
* **Social**: Influence (2) + CHA (2) + Command Voice (2) = 8d6
* **Defense**: REA (2) + INT (7) = 9d6
* **Initiative**: 4d6 (Increase Reflexes, 2 Major Actions)
* **Edge Engine**: Analytical Mind (+1 free Edge on Logic tests)
```

*(Can alternatively be declared via python helper: `{python} operational_pools(astral=15, matrix=20, physical=8, social=8, defense=9, initiative_dice=4, edge_engine=True)`).*

---

### Pillar 2: Build Efficiency & Total Equivalent Karma (TEK)

In addition to table performance, builds are evaluated on **economic efficiency**: what the completed character would cost if reverse-engineered into pure post-chargen Karma.

* **Top-Bracket Augmentation Deltas**: Augmentations that boost attributes save the most expensive high-bracket marginal Karma tiers (e.g., pushing an attribute to 7–9 saves 35–45 Karma per point).
* **The Skillwires / Autosoft Dividend**: Installing Skillwires or Drone Autosofts grants immediate access to multiple high-rating skills without paying separate triangular Karma for each, dramatically multiplying effective build value.
* **Qi Focus Power Point Benchmark**: Adept Power Points are valued at their canonical in-game replacement cost via Force 4 Qi Foci (**15.5 Karma per PP**; 8 bonding Karma + 15,000¥ focus/formula).
* **Sovereign Sustained Magical Augmentations (Anchored Spells Dividend)**: Sustained spells backed by dedicated sovereign sustaining anchors (*Focused Concentration*, *Quickening*, or *Sustaining Foci*) run 24/7 with zero drag, functioning identically to biological/magical cyberware. *Increase Attribute* is credited using the high-bracket marginal attribute delta (+250k for CHA 10 $\rightarrow$ 14, +150k for WIL 5 $\rightarrow$ 9, +210k for LOG 8 $\rightarrow$ 12); *Increase Reflexes* is credited at Reaction delta + Initiative action economy (+100k for +3 REA / 4D6).
* **Deterministic Telemetry**: Evaluated automatically via the CLI:

  ```powershell
  uv run sr6 calc eff <char_id>
  ```

  *(See `sr6core/creation/efficiency.py` for the complete mathematical conversion ledger and derivations).*

---

## 7. Unspent Resources & Completeness Gate

A build is **only considered complete and rules-legal for play** when all chargen pools have been fully allocated under strict tabletop limits:

| Resource Type | Maximum Allowed Unspent | Failure Consequence |
| :--- | :---: | :--- |
| **Liquid Pocket Cash** | $\le \mathbf{5,000¥}$ | Excess cash is lost upon entering play (must be spent on gear/lifestyle). |
| **Customization Karma** | $\le \mathbf{5\text{ Karma}}$ | Excess karma is forfeit or indicates an unfinished build. |
| **Character Points (CP)** | **0 CP** | Incomplete chargen (must be converted to attributes, skills, or nuyen). |
| **Contact Points** | **0 Points** | Unassigned contacts; must be allocated to fixers, docs, or informants. |

---

## 8. Benchmark Comparative Scorecard (Active Canon vs. Lab Builds)

Evaluating the base starting builds of active campaign characters (`reiko`, `velvet`) against current Lab prototypes (`venn`, `ouro`, `dalakitnon_adept`):

| Character | Method / Metatype | Active Planes | OBS (0–15) | Base Attrs | Ware Delta | Natural Skills | Softs Dividend | Magic / Res | Sustained Spells | Gear | Net Quals | **TEK** | **KER** | Unspent Resource Audit |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :--- |
| **Dalakitnon** | Life Path (6WC)<br>Elf Mystic Adept | **4 / 4** | **13 / 15** | 415 | — | 210 | **113** | 89 | **420** | 47 | 15 | **1,309** | **$13.09\times$** | <span style="color:green">**PASS**</span>: 0 CP, 0 Contacts, 3k Karma, 3,575¥ cash ($\le 5,000¥$). |
| **Ouro** | Point Buy 100<br>AI-Pilot Technomancer | **3 / 4** | **11 / 15** | 435 | — | 255 | **1,124** | 43 | — | 87 | 15 | **1,959** | **$19.59\times$** | <span style="color:green">**PASS**</span>: 0 CP, 0 Contacts, 3k Karma, 2,160¥ cash ($\le 5,000¥$). |
| **Velvet** *(Base)* | Point Buy 100<br>Elf Mystic Adept | **2 / 4** | **9 / 15** | 555 | — | 305 | — | 139 | **500** | 25 | 15 | **1,539** | **$15.39\times$** | <span style="color:green">**PASS**</span>: 0 CP, 0 Contacts, 0k Karma, 4,025¥ cash ($\le 5,000¥$). |
| **Reiko** *(Base)* | Point Buy 100<br>AI-Pilot Technomancer | **2 / 4** | **8 / 15** | 345 | — | 265 | **467** | 83 | — | 45 | 15 | **1,220** | **$12.20\times$** | <span style="color:red">**FAIL: ¥90,000 unspent cash**</span> (exceeds 5k limit; unitemized gear). |
| **Venn** | Point Buy 100<br>Monad Street Sam | **2 / 4** | **7 / 15** | 465 | 320 | 320 | **613** | — | — | 135 | 15 | **1,868** | **$18.68\times$** | <span style="color:green">**PASS**</span>: 0 CP, 0 Contacts (Parnell C4/L2, Dr. Ortiz C3/L3), 3k Karma, 570¥ cash ($\le 5,000¥$). |

### Key Takeaways & The Two-Pillar Synergy

1. **The Sovereign Magical Augmentation Breakthrough**: Crediting anchored sustained spells (*Focused Concentration*, *Quickening*) equally alongside cyberware elevates Velvet to **1,539 TEK** ($15.39\times$) and Dalakitnon to **1,309 TEK** ($13.09\times$). Velvet's combination of natural Charisma 10 $\rightarrow$ 14 (+250k), Willpower 5 $\rightarrow$ 9 (+150k), and 4D6 Initiative (+100k) matches the astronomical power of heavy cyberware while preserving full magical aura integrity.
2. **The 3-Tier Power Scale**:
   * **Tier 1 — Synthetic Singularity (1,800–2,000 TEK)**: Ouro (**1,959 TEK**) and Venn (**1,868 TEK**) sit at the absolute apex, combining top-bracket hardware deltas (Control Rig 3 / Cyberlimbs) with universal operational software (R9 autosofts / R7 skillwires across all 5 operational domains).
   * **Tier 2 — Metahuman Arch-Mage (1,300–1,600 TEK)**: Velvet (**1,539 TEK**) and Dalakitnon (**1,309 TEK**) harness sovereign sustained metamagic and Qi foci to shatter natural attribute caps and match cybernetic initiative without Essence loss.
   * **Tier 3 — Emergent Specialist (1,100–1,300 TEK)**: Reiko (**1,220 TEK**) leverages Pilot Origins and R6 autosofts for exceptional operational competence, but lacks high-bracket physical augmentations or anchored attribute spells.
3. **The 5-Domain Deduplication Principle**: Ouro's valuation avoids double counting: physical/combat domains are handled by cheap autosofts, while the Synthetic Skill Driver receives dividend credit strictly for Domain 5 (Social Utility: Con & Influence).
4. **Resolved Prototype Compliance**:
   * **Venn**: Fully compliant (<span style="color:green">**PASS**</span>) after allocating the 12 Contact Points to Parnell (Fixer, C4/L2) and Dr. Caleb Ortiz (Streetdoc, C3/L3) from Chapter 7 (*The First Contract*).
   * **MAD Dalek**: Fully compliant (<span style="color:green">**PASS**</span>) after purchasing 1 month of Low Lifestyle (2,000¥), reducing pocket cash to 3,575¥ ($\le 5,000¥$).
   * **Reiko**: Note that her original base build retained ¥90,000 unallocated cash prior to session purchases.
