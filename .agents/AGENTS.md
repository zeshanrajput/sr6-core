# Master Workspace Agent Instructions: SR6 Core (`sr6-core`) & Portfolio Pipeline

This workspace provides the core engine, CLI tools, datasets, and the **Shadowrun 6e Narrative Suite Plugin (`sr6-narrative-suite`)** located at [`.agents/plugins/sr6-narrative/`](file:///c:/GitHub/sr6-core/.agents/plugins/sr6-narrative/).

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
3. **Character Voice Specification**: Loads local character repository `reference/voice_spec.md` (e.g., `sr6yuriko/reference/voice_spec.md`, `sr6velvet/reference/voice_spec.md`), which inherits/extends [`sr6-core/reference/default_voice_spec.md`](file:///c:/GitHub/sr6-core/reference/default_voice_spec.md).
4. **Master Character Dossier**: Reads `character_master.yaml` (attributes, inventory, ammo, nuyen, debt, qualities, spells, cyberware) as authoritative tabletop play state.
5. **RAG Story Continuity & Rules**: Queries recent chapter logs via `sr6 continuity` and rule context via `sr6-rules` (always querying local offline FTS5 vault first via `sr6 rag search` before cloud AI synthesis).

### Stage 2: Initial Draft Generation (`v1`)
`narrative-director` invokes the drafting sub-agent to generate Scene Draft `v1`, adhering to:
* POV, active era from `arc_chronology`, and cognitive bias from `voice_spec.md`.
* 4-beat scene structure (Inciting Friction -> Escalation -> Climax -> Aftermath) and braided paragraph cadence from `axis-pacing-structure`.
* Thematic worldbuilding and atmospheric friction from `axis-worldbuilding-grit`.
* 23 anti-slop rules, affirmative staging, and "Trust the Reader" discipline from `no-ai-slop`.
* Mechanical reality constraints from `character_master.yaml` and dynamic weapon arrays (`calculate_modified_weapon`) without modifying tabletop balances.
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
| **`sr6-rules`** | SR6 mechanics (Edge, Matrix actions, spell drain, tactical arrays) accuracy | **8.5 / 10** |

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

### Stage 6: Refinement Mode for Existing `.qmd` Files
When requested to refine an existing chapter (`.qmd`):
1. Load and dispatch the existing file directly to the 7-sub-agent audit panel.
2. Synthesize feedback and execute line-level prose chisel refactoring.
3. Write the revised content **directly to the target `.qmd` file** so changes can be inspected instantly using the native IDE side-by-side git diff view.

---

## 3. CLI Diagnostic Utilities

Before completing edits or reviewing narrative/character updates, run corresponding CLI commands:
* **Local Offline Rules Search**: `sr6 rag search "<topic>"` (instant 5-stage hybrid search with cross-edition references and statblocks)
* **Item Reference Cards**: `sr6 card <quality|weapon|spell|cyberware|vehicle|program> <name>`
* **Prose & Markdown Linter**: `sr6 lint "chapters/<file>.qmd"`
* **7-Axis Narrative Evaluator**: `sr6 evaluate "chapters/<file>.qmd" --tier <1|2|3> --char <id>`
* **Combat Ledger Action Parser**: `sr6 ledger parse "chapters/<file>.qmd"`
* **Continuity Engine**: `sr6 continuity <repo_path>`
* **Character Creation Auditor**: `sr6 characters audit [char_id]`
* **Multi-Format Exporters**: `sr6 export <char_id> --format=roll20|vtt|xml|cards`
* **Plugin Management**: `sr6 plugin install` / `sr6 plugin status`
