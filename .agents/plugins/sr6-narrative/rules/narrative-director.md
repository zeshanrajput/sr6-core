# Narrative Director: Master Narrative Production Orchestrator

This document defines the routing logic, sub-agent capabilities, narrative standards, and the **Primary Master Orchestrator (`narrative-director`)** for the Shadowrun 6e multi-agent narrative production framework across `sr6-core` and character repositories (`sr6yuriko`, `sr6velvet`, `sr6union`, etc.).

---

## 1. Master Orchestrator: `narrative-director`

The `narrative-director` is the primary autonomous orchestrator responsible for end-to-end narrative generation, multi-agent evaluation, iterative self-correction, and state tracking.

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
                      |  Output .qmd & YAML diffs   |
                      +-----------------------------+
```

---

## 2. Six-Stage Execution Workflow

### Stage 1: Context Ingestion
Before drafting or editing, `narrative-director` ingests:
1. **Scene Outline / Prompt**: User-provided beat sheet, plot points, or target goals.
2. **Sub-Agent Evaluation Skills**: Calibrated directly by `sr6-narrative-suite` skills (`no-ai-slop`, `axis-pacing-structure`, `axis-worldbuilding-grit`, `axis-voice-internality`, `axis-agency-motivation`, `sr6-rules`, `continuity-tracker`, `literary-analysis`).
3. **Character Voice Specification**: Loads local character repository `reference/voice_spec.md` (e.g., `sr6yuriko/reference/voice_spec.md`, `sr6velvet/reference/voice_spec.md`), which inherits/extends `sr6-core/reference/default_voice_spec.md`.
4. **Master Character Dossier**: Reads `character_master.yaml` (attributes, inventory, ammo, nuyen, debt, qualities, spells, cyberware) as authoritative tabletop play state.
5. **RAG Story Continuity & Rules**: Queries recent chapter logs via `sr6 continuity` and rule queries via `sr6-rules`.

### Stage 2: Initial Draft Generation (`v1`)
`narrative-director` invokes the drafting sub-agent to generate Scene Draft `v1`, adhering to:
* POV, active era from `arc_chronology`, and cognitive bias from `voice_spec.md`.
* 4-beat scene structure (Inciting Friction -> Escalation -> Climax -> Aftermath) and braided paragraph cadence from `axis-pacing-structure`.
* Thematic worldbuilding and atmospheric friction from `axis-worldbuilding-grit`.
* 23 anti-slop rules, affirmative staging, and "Trust the Reader" discipline from `no-ai-slop`.
* Mechanical reality constraints from `character_master.yaml` (without modifying tabletop balances).
* Audio narration and TTS readability guidelines (ellipses ceiling $\le 0.6$ per 300 words).

### Stage 3: Parallel Sub-Agent Audit Panel
Draft `v1` is dispatched simultaneously to all **7 sub-agent evaluators**:

| Sub-Agent Skill | Focus Dimension | Passing Threshold |
| :--- | :--- | :--- |
| **`axis-voice-internality`** | Character voice, POV integrity, vocabulary matrix, sensory lens, era calibration | **8.0 / 10** *(Calibrated to Tier)* |
| **`axis-pacing-structure`** | 4-beat structure, entry/exit discipline, action-to-exposition (80/20) | **8.0 / 10** *(Calibrated to Tier)* |
| **`axis-agency-motivation`** | Protagonist proactive choice, consequential stakes, drive alignment | **8.0 / 10** *(Calibrated to Tier)* |
| **`axis-worldbuilding-grit`** | Dystopian texture, corporate omnipresence, AR clutter, zero info-dumps | **8.0 / 10** *(Calibrated to Tier)* |
| **`no-ai-slop`** | Anti-slop pattern detection, forbidden terms list, redline removal, TTS fluency | **8.5 / 10** |
| **`continuity-tracker`** | Ammo/nuyen balances, damage tracks, contacts, state diff generation | **8.5 / 10** |
| **`sr6-rules`** | SR6 mechanics (Edge, Matrix actions, spell drain, modifiers) accuracy | **8.5 / 10** |

#### Chapter Tier Threshold Calibration
* **Tier 1 (Keystones)**: Passing threshold **9.0 / 10** (Existential breakthroughs, initiation/submersion milestones, foundational pivots).
* **Tier 2 (Narrative Evolution)**: Passing threshold **8.5 / 10** (Mission runs, relationship deepening, regional texture, evolutionary steps).
* **Tier 3 (Atmospheric Bridges)**: Passing threshold **8.0 / 10** (Slice-of-life downtime, procedural mechanics, affectionately grounded banter).

### Stage 4: Synthesis & Automated Self-Correction Loop
1. `narrative-director` collates the audit reports into a unified **Revision Matrix**.
2. If any sub-agent score falls below its passing threshold, `narrative-director` automatically formulates a targeted re-draft prompt combining all redline fixes.
3. The re-draft cycle (`v1` -> `v2` -> `v3`) repeats autonomously until **all 7 sub-agents pass threshold standards**.

### Stage 5: Publishing & State Tracking
Upon successful panel approval:
1. **Narrative Output**: Emits the final polished prose as a clean Quarto markdown file (`.qmd`) in `chapters/` (e.g., `chapters/chapter_04.qmd`).
2. **State Diff Proposal**: Emits an explicit YAML patch proposing updates to `character_master.yaml` for changes in nuyen, ammunition, physical/stun damage, Karma, or contact relationships.

### Stage 6: Refinement Mode for Existing Chapters (`literary-analysis <target>`)
Invoked via the command/trigger: **`literary-analysis <target_file>`** (or `/literary-analysis <target_file>`):
1. **Deterministic Diagnostics**: Run `uv run sr6 lint` and `uv run sr6 evaluate` on the target file.
2. **Methodical Prose Chisel Protocol (`apply_prose_chisel`)**:
   - **Paragraph Braiding & Calibrated Cadence**: Weave sensory texture, physical action, and dialogue into cohesive 3-to-6 sentence paragraphs. Single-sentence paragraphs are a high-impact literary tool for irreversible pivots or flashback hinges—use deliberately and sparingly ($\le 1\text{–}2 / 1,000$ words).
   - **One Speaker Per Paragraph**: Every speaker turn is an independent paragraph braiding dialogue with that character's own physical micro-action.
   - **Trust the Reader vs. Contextual Scaffolding**: Prune lazy meta-exposition, comparative preamble essays, and dialogue dossier dumps. Preserve essential grounded scaffolding when specialized professional dynamics (e.g. clinical triage detachment vs. supernatural charisma) or proprietary character motifs (e.g. gold vs. indigo pathways) cannot reasonably be deduced by the reader alone.
   - **Affirmative Staging & Non-Action Pruning**: Strip filler negatives (*"did not flinch"*) when the subsequent positive physical action (*"her hands remained flat against her knees"*) carries the weight.
3. **Pre-Commit Verification**: Run `uv run sr6 lint` and `uv run sr6 evaluate` on revised prose.
4. **Deliver Scorecard & Drop-in Prose**: Emit the unified 7-axis scorecard and expanded literary craft telemetry, and write revised prose directly to the target file for immediate git diff review.
5. **Transparent Literary Craft Breakdown**: In the chat response, explicitly call out where and why any deliberate single-sentence paragraphs or contextual scaffolding tools were deployed (or explicitly note "None deployed / required").

---

## 3. CLI Diagnostic Utilities

Before completing edits or reviewing narrative/character updates, run corresponding CLI commands:
* **Prose & Markdown Linter**: `sr6 lint "chapters/<file>.qmd"`
* **Continuity Engine**: `sr6 continuity <repo_path>`
* **Character Creation Auditor**: `sr6 characters audit [char_id]`
* **Multi-Format Exporters**: `sr6 export <char_id> --format=roll20|vtt|xml`
