---
name: narrative-director
description: Orchestrate 6-stage SR6 narrative generation and audits.
version: 1.0.0
author: Zeshan Rajput (zeshanrajput), Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [shadowrun, sr6, orchestration, narrative, sub-agents]
    related_skills: [axis-voice-internality, axis-pacing-structure, axis-agency-motivation, axis-worldbuilding-grit, no-ai-slop, continuity-tracker, sr6-rules, literary-analysis]
---

# Master Narrative Director Skill (`narrative-director`)

The primary autonomous orchestrator for end-to-end Shadowrun 6e narrative generation, multi-agent evaluation, iterative self-correction, and state tracking across the 6-stage lifecycle.

```
                      +-----------------------------+
                      |   1. CONTEXT INGESTION      |
                      | Outline, Voice Spec, Dossier|
                      +--------------+--------------+
                                     |
                                     v
                      +-----------------------------+
                      |   2. INITIAL DRAFT (v1)     |
                      +--------------+--------------+
                                     |
                                     v
         +-------------------------------------------------------+
         |            3. PARALLEL SUB-AGENT AUDIT PANEL          |
         |  - axis-voice-internality   - axis-pacing-structure   |
         |  - axis-agency-motivation   - axis-worldbuilding-grit |
         |  - no-ai-slop               - continuity-tracker      |
         |  - sr6-rules                                          |
         +---------------------------+---------------------------+
                                     |
                                     v
                      +-----------------------------+
                      | 4. SYNTHESIS & SELF-CORRECT |  <-- (Fails threshold?
                      |  Passes all 7 thresholds?   |       Re-draft v2, v3)
                      +--------------+--------------+
                                     | Passes
                                     v
                      +-----------------------------+
                      |  5. PUBLISH & STATE TRACK   |
                      | Drop-in Prose & Python diffs|
                      +-----------------------------+
```

## When to Use

- Writing a new campaign chapter from an outline, mission log, or table beat sheet.
- Auditing and refining an existing chapter (`.qmd` or `.md`) to high-end speculative fiction standards.
- Orchestrating the 7-axis evaluation panel and automated re-draft loop.

## How to Run

1. **Deterministic Pre-flight & Linting**:
   ```bash
   uv run sr6 lint "characters/<char_id>/chapters/<file>.qmd"
   ```
2. **Unified 7-Axis Evaluation**:
   ```bash
   uv run sr6 evaluate "characters/<char_id>/chapters/<file>.qmd" --tier <1|2|3> --char <char_id>
   ```

---

## The 6-Stage Execution Procedure

### Stage 1: Context Ingestion
Before drafting or editing, assemble and ingest:
1. **Scene Outline / Prompt**: User-provided beat sheet, plot points, or run objectives.
2. **Character Voice Specification**: Read `characters/<char_id>/reference/voice_spec.md` (check `arc_chronology`, active era, cognitive bias, and domain vocabulary).
3. **Master Character Dossier**: Read `characters/<char_id>/<char_id>_master.yaml` for authoritative stats, implants, foci, ammo, and nuyen balances.
4. **Continuity & Rules**: Run `uv run sr6 continuity "characters/<char_id>"` and query rules via `uv run sr6 rag search "<topic>" --compact`.

### Stage 2: Initial Draft Generation (`v1`)
Draft the scene adhering to the core narrative disciplines:
- **Pacing**: Strict 4-beat structure (Inciting Friction $\rightarrow$ Escalation $\rightarrow$ Climax $\rightarrow$ Aftermath).
- **Paragraph Cadence**: Braided 3–6 sentence paragraphs weaving physical action, sensory cues, and consequences.
- **Dialogue Integrity**: One speaker per paragraph (braided with that speaker's physical actions).
- **Anti-Slop**: Zero banned buzzwords, no olfactory checklist templates, affirmative staging (ban filler negatives), and ellipses ceiling $\le 0.60$ per 300 words.
- **Mindspeech**: Italics without quotes (`*...*`) for resonant kin; simulated acoustic quotes (`"..."`) when code-switching for metahumans.

### Stage 3: Deterministic Pre-Flight & Parallel Sub-Agent Audit Panel
1. **Deterministic Pre-Flight**: Run `uv run sr6 lint` and `uv run sr6 evaluate` to gather automated metrics (word count, braiding ratio, ellipses ratio, banned buzzwords, corporate presence).
2. **Panel Audit**: Audit the draft across all 7 evaluation dimensions against the chapter tier threshold:
   - **Tier 1 (Keystones)**: Passing threshold **9.0 / 10**
   - **Tier 2 (Narrative Evolution)**: Passing threshold **8.5 / 10**
   - **Tier 3 (Atmospheric Bridges)**: Passing threshold **8.0 / 10**

   *In Hermes Agent, dispatch parallel sub-agent audits via `delegate_task` when evaluating complex full-length chapters.*

| Sub-Agent Skill | Focus Dimension | Passing Threshold |
| :--- | :--- | :--- |
| **`axis-voice-internality`** | Character voice, deep limited POV, vocabulary matrix, sensory lens, era calibration | Tier Calibrated (8.0–9.0) |
| **`axis-pacing-structure`** | 4-beat structure, entry/exit discipline, paragraph braiding, 80/20 balance | Tier Calibrated (8.0–9.0) |
| **`axis-agency-motivation`** | Protagonist proactive choice, consequential stakes, anti-foil parity | Tier Calibrated (8.0–9.0) |
| **`axis-worldbuilding-grit`** | Dystopian texture, corporate omnipresence, AR clutter, zero info-dumps | Tier Calibrated (8.0–9.0) |
| **`no-ai-slop`** | Anti-slop pattern detection, forbidden terms list, redline removal, TTS fluency | **8.5 / 10** |
| **`continuity-tracker`** | Ammo/nuyen balances, damage tracks, contacts, state verification | **8.5 / 10** |
| **`sr6-rules`** | SR6 mechanics (Edge, Matrix actions, spell drain, tactical arrays) accuracy | **8.5 / 10** |

### Stage 4: Synthesis & Automated Self-Correction Loop
1. Collate audit scores into a unified **Revision Matrix**.
2. If any sub-agent score falls below its passing threshold:
   - Invoke `literary-analysis` (`apply_prose_chisel`) to formulate line-level fixes.
   - Generate redraft `v2` addressing every redline.
   - Re-evaluate until **all 7 sub-agents pass threshold standards**.

### Stage 5: Publishing & State Tracking
Upon panel approval:
1. **Prose Delivery**: Present the polished chapter text in chat for review, or write directly to the target `.qmd` in `chapters/` if requested.
2. **State Updates via Markdown Trio**:
   - Provide drop-in `{python} inc(...)` snippets in chat for `character_log.qmd` or `character_purchases.qmd`.
   - **NEVER edit `*_master.yaml` directly.** The user runs `uv run sr6 sync-all` to recompile the master YAML from the Markdown Trio.

### Stage 6: Refinement Mode for Existing Chapters
When polishing an existing chapter file:
1. Run `uv run sr6 lint` and `uv run sr6 evaluate` on the file.
2. Synthesize line-level chisel edits for any flagged sections.
3. Deliver drop-in replacements or update the target `.qmd` file so changes can be inspected via git diff.

---

## Sub-Agent Audit Panel Scorecard Format

```markdown
# 📊 SR6 Narrative Evaluation Scorecard
* **Chapter Target**: `[File or Scene]`
* **Target Tier**: Tier [1|2|3] (Passing Threshold: **[Threshold]/10**)
* **Word Count**: [Word Count] words
* **Panel Status**: [✅ PASS (PANEL APPROVED) / ⚠️ REVISION REQUIRED]

| Axis Dimension | Score | Threshold | Status | Key Findings |
| :--- | :---: | :---: | :---: | :--- |
| `axis-voice-internality` | [Score] | [Min] | [Pass/Fail] | [Findings] |
| `axis-pacing-structure` | [Score] | [Min] | [Pass/Fail] | [Findings] |
| `axis-agency-motivation` | [Score] | [Min] | [Pass/Fail] | [Findings] |
| `axis-worldbuilding-grit`| [Score] | [Min] | [Pass/Fail] | [Findings] |
| `no-ai-slop` | [Score] | 8.5 | [Pass/Fail] | [Findings] |
| `continuity-tracker` | [Score] | 8.5 | [Pass/Fail] | [Findings] |
| `sr6-rules` | [Score] | 8.5 | [Pass/Fail] | [Findings] |

### 🛠️ Unified Revision Matrix
1. [ ] **[Axis Name]**: [Specific line-level redline and fix]
```
