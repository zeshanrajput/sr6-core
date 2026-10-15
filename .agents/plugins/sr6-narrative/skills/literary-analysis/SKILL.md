---
name: literary-analysis
description: Unified literary craft engine: 7-axis audit rubrics, action choreography, and prose chisel refactoring.
version: 2.0.0
author: Zeshan Rajput (zeshanrajput), Antigravity Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [shadowrun, narrative, craft, audit, choreography, prose-chisel, refactoring, literary]
    related_skills: [no-ai-slop, sr6-rules, narrative-director, sr6-chapter-finalize]
---

# Literary Craft, Audit & Prose Chisel Skill (`literary-analysis`)

The central speculative fiction craft engine for the Shadowrun 6e Narrative Suite. This skill serves a dual purpose across the development lifecycle:
1. **Stage 3 Unified Audit Panel**: Evaluates scene drafts across Voice, Pacing, Agency, and Worldbuilding against tier-calibrated standards.
2. **Domain Action Choreography**: Guides visceral staging for tactical firefights, astral perception/sorcery, and matrix decking/technomancy.
3. **Stage 4 & 6 Prose Chisel Engine (`apply_prose_chisel`)**: Executes line-level refactoring to braid staccato lines, translate dry mechanics into consecrated capital/debt, and strip negative non-actions.

---

## When to Use

- Running the Stage 3 multi-axis qualitative audit on chapter drafts or scene beats.
- Staging action scenes involving smartlink combat, spellcasting/drain, or matrix/resonance hacking.
- Executing Stage 4/6 line-level prose chisel refactoring (`apply_prose_chisel`).
- Fixing staccato paragraph stacking, show-then-tell redundancy, or passive protagonist syndrome.

## Command Triggers & Diagnostics

Invoke directly in chat:
```text
literary-analysis <target_file>
/literary-analysis <target_file>
```
*Example: `literary-analysis characters/velvet/narrative/02_faceless_mirror.md`*

Execute baseline diagnostics via CLI:
```bash
# Automated paragraph braid ratios, ellipses ceiling, and buzzwords
uv run sr6 lint "characters/<char_id>/chapters/<file>.qmd"

# 7-axis baseline scorecard and tier-calibrated compliance
uv run sr6 evaluate "characters/<char_id>/chapters/<file>.qmd" --tier <1|2|3> --char <char_id>
```

---

## Tier-Calibrated Standards (Unified 1.0–10.0 Scale)

Prose expectations scale with the chapter's designated tier in `reference/voice_spec.md`:

- **Tier 1 (Keystones — Passing Threshold: $\ge 9.0 / 10$):**
  - Existential breakthroughs, foundational pivots, initiation/submersion milestones, profound moral tragedy.
  - Irreversible choices; protagonist boldly breaks from conditioning; deep somatic friction. Zero fluff. Word count: 1,500 – 2,500+ words.
- **Tier 2 (Narrative Evolution — Passing Threshold: $\ge 8.5 / 10$):**
  - Mission runs, operational tradecraft, shadowrun negotiations, relationship deepening, regional sprawl texture, dark humor, tactical momentum. Word count: 1,200 – 1,800+ words.
- **Tier 3 (Atmospheric Bridges — Passing Threshold: $\ge 8.0 / 10$):**
  - Meditative downtime, procedural maintenance, un-monetized tea/noodle sanctuaries, somatic healing truces, affectionately grounded banter. Word count: 1,000 – 1,600+ words.

---

## The 4 Evaluation Axes

### Axis 1: Character Voice & Internality (`axis-voice-internality`)
- **Deep Limited Third-Person POV**: Stay anchored behind the protagonist’s eyes, sensors, and cognitive biases. Never float into omniscient narrator territory.
- **Sensory Palette & Vocabulary Matrix**: Ground metaphors in the character's lived professional reality (e.g., Reiko's dual Gold TacNet / Indigo Resonance telemetry; Velvet's transmutational body and aesthetic geomancy; Venn's monad bus clocks and ceramic stress).
- **Chronological Arc Calibration**: Calibrate to the chapter's active era from `voice_spec.md` (e.g. Arc 1 debt-collar vs. Arc 4 sovereign authority). Avoid retrospective flattening.

### Axis 2: Pacing & Structure (`axis-pacing-structure`)
- **4-Beat Scene Architecture**: Inciting Friction $\rightarrow$ Escalation $\rightarrow$ Climax $\rightarrow$ Aftermath. Arrive late, leave early.
- **Paragraph Braiding (3 to 6 Sentences)**: Group sensory atmosphere, physical micro-action, gear interaction, and immediate somatic consequences into cohesive braided paragraphs.
- **Single-Sentence Lines as a Deliberate Literary Tool**: Single-sentence paragraphs are a high-impact literary tool for irreversible pivots or existential turning points. Strictly calibrated to **no more than 1 or 2 per thousand words** ($\le 1\text{–}2 / 1,000$ words).
- **One Speaker Per Paragraph (Mandatory)**: Never combine lines spoken by different characters into one paragraph. Braid each speaker turn with their own delivery and physical micro-action.

### Axis 3: Protagonist Agency & Stakes (`axis-agency-motivation`)
- **Active Driver vs. Passive Passenger**: The protagonist must make deliberate tactical or moral decisions that dictate the outcome of the scene.
- **Two-Tier Dramatic Sphere**:
  - *Tier A Campaign Canon (`canonical: true`)*: Respects the Canon Ceiling. Read-only relational orbit; other PCs and campaign VIPs are inviolable.
  - *Tier B Bespoke Foils (`canonical: false`)*: Carry full sovereign agency, permanent moral reckoning, and mortal stakes.
- **Moral Friction**: Decisions must cost something tangible (nuyen, reputation, physical strain, emotional security).

### Axis 4: Worldbuilding & Dystopian Grit (`axis-worldbuilding-grit`)
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
   - *Preserve Essential Contextual Scaffolding*: Provide grounded sensory grounding when a reader cannot reasonably deduce specialized dynamics (e.g. medical triage desensitization buffering against charisma until the smock comes off).
4. **Affirmative Staging & Non-Action Pruning**:
   - Strip gratuitous negative non-actions (*"did not flinch"*, *"did not look back"*) whenever the positive physical detail (*"her hands remained flat against her knees"*) already carries the weight.

---

## Output Deliverables

When evaluating or chiseling a chapter, deliver:
1. **The Unified 7-Axis Scorecard**:
   - Scores across Voice, Pacing, Agency, Worldbuilding, Slop, Continuity, and Rules.
   - Final composite score vs. designated tier passing threshold.
2. **Expanded Literary Craft Telemetry**:
   - Paragraph braiding ratio, single-sentence line quota compliance, speaker-turn integrity.
3. **Transparent Craft Callouts**:
   - Single-sentence paragraph justifications (or "None deployed").
   - Contextual scaffolding justifications (or "None required").
4. **Drop-in Polished Prose**: Ready-to-paste markdown replacements or direct file updates.
