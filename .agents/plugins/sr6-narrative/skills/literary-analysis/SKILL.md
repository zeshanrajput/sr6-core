---
name: literary-analysis
description: Elevate chapter prose with line-level chisel refactoring.
version: 1.0.0
author: Zeshan Rajput (zeshanrajput), Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [shadowrun, narrative, prose-chisel, refactoring, literary]
    related_skills: [axis-voice-internality, axis-pacing-structure, no-ai-slop, narrative-director]
---

# Literary Analysis & Prose Chisel Skill (`literary-analysis`)

Consolidated into the SR6 development pipeline as the Stage 4 **Prose Elevation & Chisel Engine (`apply_prose_chisel`)**. This skill synthesizes feedback from the 7-axis audit panel, elevates prose quality to high-end speculative fiction standards, and transforms dry game mechanics into evocative literature.

## When to Use

- Stage 4 of the narrative pipeline: synthesizing panel audit findings into concrete line edits.
- Refactoring flagged scenes to fix staccato paragraphs, show-then-tell redundancy, and robotic cadence.
- Elevating dry TTRPG math (Edge, Drain, Matrix tests, Rigging) into visceral sensory narrative.

## How to Run

Execute evaluation and linter diagnostics via the `terminal` tool:

```bash
uv run sr6 evaluate "characters/<char_id>/chapters/<file>.qmd" --tier <1|2|3> --char <char_id>
```

## Tier-Calibrated Standards (Unified 1.0–10.0 Scale)

Prose is evaluated against its designated tier in `reference/voice_spec.md`:

- **Tier 1 (Keystones — Passing Threshold: $\ge 9.0 / 10$):**
  - Existential breakthroughs, profound moral tragedy, life-altering turning points, visceral somatic friction, and strict thematic discipline. Zero fluff. Word count: 1,500 – 2,500+ words.
- **Tier 2 (Narrative Evolution — Passing Threshold: $\ge 8.5 / 10$):**
  - Operational tradecraft, shadowrun negotiations, relationship deepening, regional sprawl texture, dark humor, and tactical momentum. Word count: 1,200 – 1,800+ words.
- **Tier 3 (Atmospheric Bridges — Passing Threshold: $\ge 8.0 / 10$):**
  - Procedural downtime, clinic maintenance, un-monetized tea/noodle sanctuaries, meditative character breathing room. Word count: 1,000 – 1,600+ words.

## The 4 Chisel Transformations (`apply_prose_chisel`)

When refactoring prose from panel redlines, apply these four transformations:

### 1. Braid Fragmented Lines into Cohesive Paragraphs
- Merge isolated 1–2 sentence lines into flowing 3–6 sentence paragraphs grouping action, sensory texture, and immediate consequences.
- Maintain dialogue integrity: **one speaker per paragraph**. Braid that speaker's dialogue with their own physical micro-action (2–4 sentences per turn).

### 2. Translate Dry TTRPG Math -> Techno-Poetic Shadowrun Fiction
Seamlessly transform tabletop rules into sensory experience:
- **Matrix Perception / Slicing:**
  - *Dry:* "She rolled Matrix Perception to scan the node."
  - *Chiseled:* "She plucked the hidden chords of the underlying wire, feeling the cold, rhythmic heartbeat of corporate traffic pulsing through the junction."
- **Spellcasting / Drain:**
  - *Dry:* "He cast Stunball and suffered 2 Drain."
  - *Chiseled:* "The mana flared white-hot through his palms; behind his collarbones, cartilage locked and metallic heat surged up his throat as the backlash grounded into his marrow."
- **Rigging / Inhabitation:**
  - *Dry:* "She jumped into the Fly-Spy drone."
  - *Chiseled:* "Her perspective collapsed through the neural jack, expanding instantly into the icy, low-bitrate greyscale vision of twin composite rotors biting into rain."

### 3. Cut Show-Then-Tell Redundancy (Trust the Reader)
- Delete trailing explanatory codas that summarize the meaning of an action.
- *Before:* "She double-checked the cylinder seal on the medkit. She was terrified of sepsis."
- *Chiseled:* "She double-checked the cylinder seal on the medkit, thumb running twice along the rubber seating."

### 4. Affirmative Staging & Sensory De-familiarization
- Replace passive negative staging (*"did not speak," "without looking"*) with direct physical actions.
- Replace formulaic sensory checklists (*"smelled of ozone and copper"*) with thermal, acoustic, and barometric weight (*"drizzle sizzled against the heat sink of the cyberjack"*).

## Chisel Output Format

Deliver revised passages in chat as ready-to-inspect diffs or drop-in markdown blocks:

```markdown
### ✂️ Prose Chisel Refactoring Pass
* **Target Scene**: [Chapter and paragraph numbers]
* **Target Tier**: Tier [1|2|3] (Threshold: [Score]/10)

#### Before & After Line Chisels
> **Original**:
> [Quote original text with flagged slop/pacing issues]

> **Chiseled**:
> [Polished, braided replacement text with elevated sensory grounding]

#### What Changed & Why
- Merged 3 isolated staccato lines into a cohesive 4-sentence braided paragraph.
- Converted dry Matrix Perception roll into physical cable and resonance interaction.
- Cut explanatory summary sentence at the end of paragraph 2.
```
