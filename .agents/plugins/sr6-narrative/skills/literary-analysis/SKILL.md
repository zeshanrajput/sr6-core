---
name: literary-analysis
description: Positive literary craft engine: 4 developmental craft axes, domain action choreography, and prose chisel refactoring.
version: 2.1.0
author: Zeshan Rajput (zeshanrajput), Antigravity Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [shadowrun, narrative, craft, audit, choreography, prose-chisel, refactoring, literary]
    related_skills: [no-ai-slop, sr6-rules, narrative-director, sr6-chapter-finalize, continuity-tracker]
---

# Literary Craft, Action Staging & Prose Chisel Skill (`literary-analysis`)

The central **Positive Literary Craft Engine** for the Shadowrun 6e Narrative Suite. This skill serves three core functions across the narrative lifecycle:
1. **Developmental Craft Audit & Telemetry**: Evaluates scene drafts across Voice, Pacing, Agency, and Worldbuilding using deterministic readiness gates and descriptive craft metrics.
2. **Domain Action Choreography**: Guides visceral staging for tactical firefights, astral perception/sorcery, and matrix decking/technomancy.
3. **Line Chisel Engine (`apply_prose_chisel`)**: Executes line-level refactoring to braid staccato lines, translate mechanics into consecrated debt/capital, prune negative non-actions, and preserve essential domain scaffolding.

---

## When to Use

- Conducting developmental craft audits on chapter drafts or scene beats.
- Staging action scenes involving smartlink ballistics, spellcasting drain, or matrix/resonance hacking.
- Executing line-level prose chisel refactoring (`apply_prose_chisel`) in Stage 4 and Stage 6.
- Resolving staccato paragraph stacking, exposition bloat, or passive protagonist syndrome.
- Measuring sentence-length burstiness, paragraph braiding ratios, and cross-chapter echo proximity.

---

## Command Triggers & Diagnostics

Invoke directly in chat:
```text
literary-analysis <target_file>
/literary-analysis <target_file>
```
*Example: `literary-analysis characters/velvet/narrative/02_faceless_mirror.md`*

Execute baseline diagnostics via CLI (running the unified linter + tier/character calibration in one pass):
```bash
# Automated paragraph braid ratios, cluster saturation, ellipses ceiling, buzzwords, N-3 echoes, and tier/voice calibration
uv run sr6 lint "characters/<char_id>/narrative/<file>.md" --window 3 --tier <1|2|3> --char <char_id>
```
*(Note: `sr6 evaluate` remains available as an alias for the same unified analyzer.)*

### Sub-Agent Delegation Protocol (Token & Speed Optimization)
- **Series Bible & Continuity Cross-Checks (Stage 3 / Stage 6)**: Delegate multi-file audits across `storyboard.md`, `voice_spec.md`, `visual_anchors.md`, and `story_continuity.md` to a `research` (read-only) or `flash` sub-agent with explicit file paths and verification questions rather than polling them piecemeal in the parent context.
- **Line Chisel Execution (Stage 4 / Stage 6)**: Dispatch a `flash` Line Chisel Worker (`apply_prose_chisel`) for surgical line edits and lexical cluster de-duplication, keeping high-reasoning coordination focused on macro craft and user feedback.

---

## Chapter Tiers & Qualitative Craft Expectations

Prose expectations scale with the chapter's designated tier in `reference/voice_spec.md`:

- **Tier 1 (Keystones)**:
  - *Dramatic Scope*: Existential breakthroughs, foundational pivots, initiation/submersion milestones, profound moral tragedy.
  - *Craft Standards*: Zero gate tolerance; elevated sentence-length burstiness (CV $\ge 0.45$); deep somatic friction; irreversible protagonist agency. Target: 1,500 – 2,500+ words.
- **Tier 2 (Narrative Evolution)**:
  - *Dramatic Scope*: Mission runs, operational tradecraft, shadowrun negotiations, relationship deepening, regional sprawl texture, dark humor, tactical momentum.
  - *Craft Standards*: High kinetic rhythm; balanced dialogue and physical micro-action; crisp sensory staging. Target: 1,200 – 1,800+ words.
- **Tier 3 (Atmospheric Bridges)**:
  - *Dramatic Scope*: Meditative downtime, procedural maintenance, un-monetized tea/noodle sanctuaries, somatic healing truces, affectionately grounded banter.
  - *Craft Standards*: Warm tactile texture; domestic survival routines; comfortable conversational cadence. Target: 1,000 – 1,600+ words.

---

## Hard Editorial Readiness Gates & Descriptive Craft Telemetry

Rather than relying on arbitrary synthetic numeric scores (e.g. `X/10`), drafts are evaluated using deterministic gates and descriptive craft metrics:

### 1. Hard Editorial Readiness Gates (Must Pass Cleanly)
- **Zero Tier 0 Banned Buzzwords**: Absolute zero-tolerance for editorial clichés (*testament*, *tapestry*, *dance*, *palpable*, *labyrinthine*, *symphony*, *cacophony*).
- **Zero Multi-Speaker Paragraphs**: Strictly one speaker per paragraph, braiding each speaker turn with that character's own physical micro-actions and delivery.
- **The Ellipses Ceiling**: Trailing ellipses must not exceed $\le 0.60$ per 300 words to ensure natural Kokoro TTS cadence.
- **Zero Proximity Echoes**: No prominent nouns or idiosyncratic verbs repeated within 3 paragraphs intra-beat, and zero cross-chapter echo collisions across the `N-3` chapter window (`uv run sr6 lint <file> --window 3`).
- **Zero Unicode Artifacts**: Zero `\ufffd` replacement characters.

### 2. Descriptive Craft Telemetry (Developmental Health)
- **Braided Paragraph Cadence**: $\ge 75\%$ of non-dialogue paragraphs must fall within 3 to 6 sentences, weaving sensory atmosphere, physical action, and immediate consequences.
- **Single-Sentence Pivot Audit**: Single-sentence paragraphs are a high-impact literary tool reserved strictly for irreversible dramatic pivots or flashback hinges. Calibrated to **no more than 1 or 2 per thousand words** ($\le 1\text{–}2 / 1,000$ words).
- **Sentence-Length Burstiness (Coefficient of Variation)**: Sentence-length CV should achieve $\ge 0.45$, confirming dynamic rhythmic variation between short punchy clauses and flowing compound sentences.
- **Cross-Chapter Echo Window (`N-3`)**: Scans previous 3 chapters for recurring signature phrases to prevent stylistic homogenization.

---

## The 4 Evaluation Axes

### Axis 1: Character Voice & Internality
- **Deep Limited Third-Person POV**: Stay anchored behind the protagonist’s eyes, sensors, and cognitive biases. Never float into omniscient narrator territory.
- **Sensory Palette & Vocabulary Matrix**: Ground metaphors in the character's lived professional reality (e.g., Reiko's dual Gold TacNet / Indigo Resonance telemetry; Velvet's transmutational body and aesthetic geomancy; Venn's monad bus clocks and ceramic stress).
- **Chronological Arc Calibration**: Calibrate to the chapter's active era from `voice_spec.md` (e.g. Arc 1 debt-collar vs. Arc 4 sovereign authority). Avoid retrospective flattening.

### Axis 2: Pacing & Structure
- **4-Beat Scene Architecture**: Inciting Friction $\rightarrow$ Escalation $\rightarrow$ Climax $\rightarrow$ Aftermath. Arrive late, leave early.
- **Paragraph Braiding (3 to 6 Sentences)**: Group sensory atmosphere, physical micro-action, gear interaction, and immediate somatic consequences into cohesive braided paragraphs.
- **Single-Sentence Lines as a Deliberate Literary Tool**: Strictly reserved for irreversible turns, capped at $\le 1\text{–}2 / 1,000$ words.
- **One Speaker Per Paragraph**: Every speaker turn is an independent paragraph braiding dialogue with that character's own physical micro-actions.

### Axis 3: Protagonist Agency & Stakes
- **Active Driver vs. Passive Passenger**: The protagonist must make deliberate tactical or moral decisions that dictate the outcome of the scene.
- **Two-Tier Dramatic Sphere**:
  - *Tier A Campaign Canon (`canonical: true`)*: Respects the Canon Ceiling. Read-only relational orbit; other PCs and campaign VIPs are inviolable.
  - *Tier B Bespoke Foils (`canonical: false`)*: Carry full sovereign agency, permanent moral reckoning, and mortal stakes.
- **Moral Friction**: Decisions must cost something tangible (nuyen, reputation, physical strain, emotional security).

### Axis 4: Worldbuilding & Dystopian Grit
- **Sensory Dystopian Texture**: Smells of ozone, synthetic soy, wet ferroconcrete, sulfurous drizzle, and industrial cooling hums.
- **Corporate Omnipresence**: Megacorps permeate daily existence through intrusive AR billboards, bioware licensing rent, and biometric checkpoints.
- **Zero Info-Dumping**: Never deliver encyclopedic lectures on safehouses or market economics. Embed world details naturally through character interaction and somatic friction.

---

## Domain Action Choreography

### 1. Tactical Combat & Firefights (`sr6-combat-choreography`)
- **Weapons & Gear Mechanics**: Query exact profiles via `uv run sr6 card weapon "<name>"` or simulate attacks via `uv run sr6 combat attack`.
- **Braided Action Paragraphs**: Weave three elements into active combat exchanges:
  1. *Physical Micro-Movement & Cover Geometry*: Squeezing behind concrete pillars, ducking beneath window sills, brass casing clatter.
  2. *Tactile Gear Telemetry*: Smartlink reticle jitter, suppressor hiss, recoil kick against dermal plating, barrel heat.
  3. *Immediate Somatic Consequence*: Impact shock, splintering plaster, ringing ears, adrenaline burn.

### 2. Astral Perception & Spellcasting (`sr6-magic-astral`)
- **Astral Emotional Gray**: Physical objects lose color into pale gray shadows; living things flare with vibrant chromatic emotional auras; cyberware appears as dark necrotic voids.
- **Somatic Drain & Backlash**: Magic demands a mortal price. Minor Drain = metallic copper taste, throbbing temples, cracked capillaries. Severe Drain = jaw cartilage locking, knees trembling, raw sternum agony.
- **Spirits as Alien Sentience**: Spirits are not video game pets; they hold elemental worldviews, distinct dignity, and strict transactional adherence to summoning agreements.

### 3. Matrix Decking & Technomancy (`sr6-matrix-narrative`)
- **Sensory Modes**:
  - *AR*: Translucent heads-up glyphs, icon clutter, flickering corporate advertising floating over wet asphalt.
  - *Cold-Sim VR*: Complete physical detachment; hosts render as sculpted architectural spaces (Mitsuhama obsidian temples, Renraku geometric grids).
  - *Hot-Sim VR*: All sensory limiters stripped away; dangerously seductive; biofeedback hits like lightning through the spine, tasting of ozone and burnt copper.
- **Decker vs Technomancer**: Deckers operate through humming military hardware and cooling fans; technomancers experience the Deep Resonance as an organic ecosystem with living digital fauna.

---

## The 4 Chisel Transformations (`apply_prose_chisel`)

When refactoring drafts during Stage 4/6, apply these four transformations:

1. **Braid Fragmented Lines into Cohesive Paragraphs**:
   - Merge isolated 1–2 sentence lines into flowing 3–6 sentence paragraphs.
   - Enforce single-sentence quota ($\le 1\text{–}2 / 1000$ words) reserved for dramatic hinges.
   - Enforce one speaker per paragraph.
2. **Translate Dry TTRPG Math -> Consecrated Fiction**:
   - *Nuyen as Existential Debt*: Rent, identity masks, cyberware maintenance leases, chassis mortgages.
   - *Downtime as Somatic Homeostasis*: The sweat equity of maintenance as artificial metabolism.
   - *Karma as Spiritual Accretion*: Character growth through traumatic survival, shedding masks, or ethical reckoning.
   - Completely strip game mechanic labels (Edge, Drain points, Defense Rating, dice pools).
3. **Trust the Reader vs. Contextual Scaffolding**:
   - *Prune Lazy Meta-Exposition*: Cut introductory comparative essays, thesis announcements, and character sheet recaps.
   - *Preserve Essential Contextual Scaffolding*: Provide grounded sensory details when a reader cannot reasonably deduce specialized dynamics (e.g. medical triage desensitization buffering against charisma until the smock comes off; Reiko's gold tactical logic versus indigo resonant soul).
4. **Affirmative Staging & Non-Action Pruning**:
   - Strip gratuitous negative non-actions (*"did not flinch"*, *"did not look back"*) whenever the positive physical detail (*"her hands remained flat against her knees"*) already carries the weight.

---

## Output Deliverables

When evaluating or chiseling a chapter, deliver:
1. **Editorial Readiness Gates & Craft Telemetry Table**:
   - Status of all hard gates (buzzwords, multi-speaker paragraphs, ellipses, proximity echoes, unicode).
   - Descriptive craft metrics (braiding cadence, single-sentence quota, burstiness CV).
2. **Transparent Craft Callouts**:
   - Single-sentence paragraph justifications (identify quote, line, and the dramatic hinge, or "None deployed").
   - Contextual scaffolding justifications (identify domain mechanic or proprietary motif scaffolded, or "None required").
3. **Drop-in Polished Prose**: Ready-to-paste markdown replacements or direct file updates.
