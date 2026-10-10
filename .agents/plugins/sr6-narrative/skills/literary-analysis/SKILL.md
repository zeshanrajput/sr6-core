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

## How to Run / Command Trigger

Invoke directly via the chat trigger:
```text
literary-analysis <target_file>
```
*(Also accepts `/literary-analysis <target_file>`)*

Execute baseline diagnostics via CLI:
```bash
uv run sr6 lint "characters/<char_id>/chapters/<file>.qmd"
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
- **Single-Sentence Lines as a Deliberate Literary Tool:** Solitary 1-sentence paragraphs are not forbidden—they are a high-impact literary tool for irreversible pivots, flashback hinges, or existential turning points (e.g., *“Jin-Young looked into the metal.”* in `02_faceless_mirror.md`). Use them deliberately and sparingly, calibrated to **no more than 1 or 2 per thousand words** ($\le 1\text{–}2 / 1,000$ words).
- Maintain dialogue integrity: **one speaker per paragraph**. Braid that speaker's dialogue with their own physical micro-action (2–4 sentences per turn).

### 2. Translate Dry TTRPG Math -> Consecrated Fiction ([`narrative doctrine`](file:///c:/GitHub/sr6-core/reference/inter_session_narrative_doctrine.md))
Seamlessly transform tabletop rules and financial arithmetic into visceral, existential reality:
- **Nuyen as Consecrated Capital & Existential Debt:**
  - Translate gear and augmentations into somatic mortgages (Reiko's Shiawase chassis as indentured metal), sacred ritual vestments (Velvet's fake SINs and high fashion), or bioware rent (Venn's chrome keeping host flesh intact).
- **Matrix Perception / Slicing:**
  - *Dry:* "She rolled Matrix Perception to scan the node."
  - *Chiseled:* "She plucked the hidden chords of the underlying wire, feeling the cold, rhythmic heartbeat of corporate traffic pulsing through the junction."
- **Spellcasting / Drain:**
  - *Dry:* "He cast Stunball and suffered 2 Drain."
  - *Chiseled:* "The mana flared white-hot through his palms; behind his collarbones, cartilage locked and metallic heat surged up his throat as the backlash grounded into his marrow."
- **Rigging / Inhabitation:**
  - *Dry:* "She jumped into the Fly-Spy drone."
  - *Chiseled:* "Her perspective collapsed through the neural jack, expanding instantly into the icy, low-bitrate greyscale vision of twin composite rotors biting into rain."

### 3. Trust the Reader vs. Essential Contextual Scaffolding
- **Cut Show-Then-Tell Redundancy & Redundant Negatives:**
  - Delete trailing explanatory codas that summarize the meaning of an action (*"She double-checked the seal on the medkit. She was terrified of sepsis."* $\rightarrow$ *"She double-checked the cylinder seal on the medkit, thumb running twice along the rubber seating."*).
  - Strip leading non-action negatives when the following physical action carries the weight (*"Reiko did not flinch, her hands remaining flat against her knees."* $\rightarrow$ *"Reiko's hands remained flat against her knees."*).
  - Cut throat-clearing comparative essays and thesis announcements before entering a scene. Let the sensory threshold speak for itself.
  - Subtextualize dialogue: replace character resumes, corporate dossiers, and past chapter plot recaps with guarded, stakes-driven conversation.
- **Preserve Essential Contextual Scaffolding:**
  - Help the reader when an expected reader cannot reasonably deduce the cause-and-effect without subtle narrative grounding.
  - Provide grounded sensory, physical, or psychological cues for:
    - *Specialized professional or mechanical dynamics* (e.g., in `02_faceless_mirror.md`, medical triage desensitization buffering a clinician against supernatural charisma until the smock comes off).
    - *Proprietary symbolic motifs* (e.g., Reiko's gold tactical logic versus indigo resonant soul).

### 4. Affirmative Staging & Sensory De-familiarization
- Replace passive negative staging (*"did not speak," "without looking"*) with direct physical actions or stillness.
- Replace formulaic sensory checklists (*"smelled of ozone and copper"*) with thermal, acoustic, and barometric weight (*"drizzle sizzled against the heat sink of the cyberjack"*).

## Chisel Output Format

When invoking `literary-analysis <target_file>`, output the evaluation scorecard, expanded craft telemetry, transparent callouts, and the chiseled prose:

```markdown
# 📊 SR6 Literary Analysis & Chisel Audit: `[Chapter Target]`
* **Target Tier**: Tier [1|2|3] (Passing Threshold: **[Threshold]/10**)
* **Word Count**: [Count] words (Target: [Tier Min]+ words)
* **Overall Status**: [✅ PASS (PANEL APPROVED) / ⚠️ REVISION REQUIRED]

### 1. Unified 7-Axis Narrative Scorecard

| Axis Dimension | Score | Threshold | Status | Key Findings & Craft Notes |
| :--- | :---: | :---: | :---: | :--- |
| **`axis-voice-internality`** | [Score] | [Min] | [Pass/Fail] | [POV depth, sensory lens, era vocabulary] |
| **`axis-pacing-structure`** | [Score] | [Min] | [Pass/Fail] | [4-beat progression, entry/exit discipline, 80/20 balance] |
| **`axis-agency-motivation`** | [Score] | [Min] | [Pass/Fail] | [Protagonist proactive choice, consequential stakes] |
| **`axis-worldbuilding-grit`** | [Score] | [Min] | [Pass/Fail] | [Dystopian texture, corporate omnipresence, zero info-dumps] |
| **`no-ai-slop`** | [Score] | 8.5 | [Pass/Fail] | [Zero buzzwords, affirmative staging, clean cadence] |
| **`continuity-tracker`** | [Score] | 8.5 | [Pass/Fail] | [Ammo, nuyen, damage tracks, contacts, state parity] |
| **`sr6-rules`** | [Score] | 8.5 | [Pass/Fail] | [Tactical mechanics, Edge, Drain, Matrix actions accuracy] |

### 2. Expanded Literary Craft & Telemetry Metrics

| Craft Dimension | Target Standard | Observed Metric | Status |
| :--- | :--- | :--- | :---: |
| **Paragraph Braiding Cadence** | Cohesive 3–6 sentence paragraphs | [Avg sentences/para] | [Pass/Fail] |
| **Single-Sentence Lines** | $\le 1\text{–}2$ per 1,000 words (Major pivots only) | [Count] ([Density] / 1k words) | [Pass/Fail] |
| **Dialogue Braiding** | 100% One-Speaker-Per-Paragraph | [100% / Merged turns detected] | [Pass/Fail] |
| **Exposition vs. Action Ratio** | $\le 20\%$ Context / $\ge 80\%$ Active Fiction | [Context %] / [Action %] | [Pass/Fail] |
| **Affirmative Staging** | 0 gratuitous non-actions / filler negatives | [Count flagged] | [Pass/Fail] |
| **Audio / TTS Fluency** | Em-dashes $\le 1.20$, Ellipses $\le 0.60$ / 300w | [Em-dash dens] / [Ellipses dens] | [Pass/Fail] |

### 3. 🧠 Transparent Craft Callouts (Tools Deployed)
- **Single-Sentence Lines**:
  - *Quote / Location*: [Quote line, e.g. "Jin-Young looked into the metal."]
  - *Justification*: [Explain why this moment constitutes an existential hinge, irreversible choice, or flashback pivot that justifies isolating it — or "None deployed"]
- **Contextual Scaffolding**:
  - *Passage / Location*: [Quote passage]
  - *Justification*: [Explain the specialized professional dynamics, tabletop rules nuance, or proprietary character motifs that an expected reader could not reasonably deduce alone — or "None required"]

### 4. ✂️ Chiseled Prose & Line Refactoring Pass
> **Original Snippet / Scene**:
> [Quote key original passage with flagged issues]

> **Chiseled Prose**:
> [Polished, braided replacement text with elevated sensory grounding]

#### What Changed & Why
- Merged staccato lines into a cohesive braided paragraph.
- Pruned meta-exposition while preserving essential contextual scaffolding.
- Converted dry TTRPG mechanics into visceral sensory fiction.
- Subtextualized dialogue to eliminate dossier-style lore dumps.
```
