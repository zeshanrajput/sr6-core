---
name: axis-pacing-structure
description: Audit narrative pacing, paragraph braiding, and structure.
version: 1.0.0
author: Zeshan Rajput (zeshanrajput), Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [shadowrun, sr6, narrative, pacing, structure]
    related_skills: [no-ai-slop, axis-voice-internality, narrative-director]
---

# Pacing & Scene Structure Evaluation Skill (`axis-pacing-structure`)

Use this skill to audit narrative drafts for structural integrity, scene entry/exit discipline, tension progression curves, climax delivery, paragraph braiding cadence, and tier-calibrated pacing within the Shadowrun 6e Narrative Suite.

## When to Use

- Auditing narrative chapters during Stage 3 of the narrative pipeline.
- Evaluating drafts for staccato single-sentence line stacking or LinkedIn-style formatting.
- Ensuring dialogue adheres to the one-speaker-per-paragraph rule and 80/20 action-to-exposition balance.

## How to Run

1. **Deterministic Pre-flight (Fast Check)**:
   Run the prose linter via the `terminal` tool to instantly measure word count, paragraph braiding ratios, and ellipses ceiling:
   ```bash
   uv run sr6 lint "characters/<char_id>/chapters/<file>.qmd"
   ```
2. **Unified Evaluator**:
   ```bash
   uv run sr6 evaluate "characters/<char_id>/chapters/<file>.qmd" --tier <1|2|3> --char <char_id>
   ```

## Tier-Calibrated Structural Standards

Word counts across all tiers must have ample room to breathe ($\ge 1,500$ words). Structural expectations scale with chapter tier:

- **Tier 1 (Keystones — Passing Threshold: $\ge 9.0 / 10$):**
  - Strict 4-beat architecture (Inciting Friction $\rightarrow$ Escalation $\rightarrow$ Climax $\rightarrow$ Aftermath).
  - Razor-sharp entry/exit points, high stakes, and profound turning points.
- **Tier 2 (Narrative Evolution — Passing Threshold: $\ge 8.5 / 10$):**
  - Room to savor operational tradecraft, shadowrun negotiations, tactical maneuvering, dark humor, and relationship building.
- **Tier 3 (Atmospheric Bridges — Passing Threshold: $\ge 8.0 / 10$):**
  - Meditative, contemplative pacing. Savoring quiet rituals (tea, noodle sanctuaries, wound care, drone calibration) in defiance of the oppressive sprawl.

## Structural Audit Criteria

1. **Paragraph Braiding & Anti-Staccato Discipline:**
   - **Enforce Mature Braided Paragraphs:** In descriptive narrative and continuous action, weave physical micro-movement, sensory atmosphere, gear interaction, and immediate consequences into cohesive paragraphs of **3 to 6 sentences**.
   - **Ban Habitual Single-Sentence Narrative Stacking:** Strictly eliminate the LinkedIn / thriller crutch of isolating solitary descriptive observations onto single lines.
   - **Isolate Single Sentences Only for Major Pivots:** An isolated single-sentence paragraph should appear **at most once or twice in an entire chapter**, reserved strictly for irreversible choices or climax pivots.
2. **One Speaker Per Paragraph (MANDATORY):**
   - In dialogue exchanges, **never combine lines spoken by different characters into the same paragraph**. Every new speaker gets a fresh paragraph.
   - Within that speaker's paragraph, braid their spoken/transmitted words with *their own* vocal delivery, physical micro-action, or sensory perception (2–4 sentences per speaker turn).
3. **Protect Atmospheric Connective Tissue:**
   - Do **NOT** mistake atmospheric pauses, character breathing room, or sensory worldbuilding for "throat-clearing" or "exposition."
   - Give scenes spatial and temporal room to live: let characters finish a breath, let rain drum against the ferroconcrete, let silence linger.
4. **Arrive Late & Leave Early:**
   - **Entry Point:** Skip mundane logistical setups. Open immediately at the sensory friction point or atmospheric threshold.
   - **Exit Point:** Cut cleanly after the climax/aftermath without appending moralizing summaries or epigrams.
5. **Action-to-Exposition Balance (80/20 Standard):**
   - 80% active sensory prose/dialogue/tactical interaction; $\le 20\%$ background context.
   - Immediate sensory environment, tactile gear interaction, and active AR HUD observation count as **active action**, not exposition.

## Audit Report Format

```markdown
### Axis: Pacing & Structure Evaluation
* **Target Tier**: [Tier 1 Keystone / Tier 2 Evolution / Tier 3 Bridge]
* **Word Count**: [Count] words (Target: 1,500+ words)
* **Pacing & Structure Score**: [Score]/10 (Threshold: 9.0 Tier 1 / 8.5 Tier 2 / 8.0 Tier 3)

#### Key Findings & Structural Breakdown
- **Paragraph Braiding & Cadence**: [Pass / Fail + Analysis of paragraph sizes]
- **Atmospheric Connective Tissue**: [Pass / Fail + Analysis]
- **Scene Entry / Exit Discipline**: [Pass / Fail + Analysis]
- **4-Beat Progression**: [Pass / Fail + Analysis]
- **Action-to-Exposition Ratio**: [Current Ratio % / 80-20 Standard Compliance]

#### Required Structural Cuts & Adjustments
- [ ] **Paragraph X**: Merge single-sentence lines into a cohesive 4-sentence braided paragraph.
```
