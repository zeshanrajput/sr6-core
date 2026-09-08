# Master Workspace Agent Instructions: SR6 Core (`sr6-core`) & Portfolio Pipeline

This workspace provides the core engine, CLI tools, datasets, and the **Shadowrun 6e Narrative Suite Plugin (`sr6-narrative-suite`)** located at `.agents/plugins/sr6-narrative/`.

---

## 0. Core Tabletop Companion Philosophy & Non-Negotiable Mandates

The primary purpose of `sr6-core` is to **support physical tabletop roleplay**. 

* **The Companion Role**: The tool does the heavy cognitive lifting—calculating situational modifiers, stacking bonuses, computing net dice pools, determining defense ratings, and presenting relevant rules in context.
* **No Digital Dice Rollers**: We deliberately do **NOT** implement digital dice rollers in books, web apps, or character sheets. Tabletop players roll physical dice at the table. Companion tools present the final pool (e.g. `14d6`) and let the player grab their physical dice.
* **Data-Driven Architecture (No Hardcoded Character Hacks)**: The engine must remain character-agnostic. All mechanics (ASDF arrays, Monad abilities, living personas, augmentations, and armor) must be derived dynamically from dossiers and database models (`ref_qualities`, `ref_cyberware`, etc.) rather than hardcoded character ID checks (`if char_id == "venn":`).

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
                      | Drop-in Prose & Python diffs|
                      +-----------------------------+
```

---

## 2. Six-Stage Execution Workflow

### Stage 1: Context Ingestion
Before drafting or editing, `narrative-director` ingests:
1. **Scene Outline / Prompt**: User-provided beat sheet, plot points, or target goals.
2. **Sub-Agent Evaluation Skills**: Calibrated directly by `sr6-narrative-suite` skills (`no-ai-slop`, `axis-pacing-structure`, `axis-worldbuilding-grit`, `axis-voice-internality`, `axis-agency-motivation`, `sr6-rules`, `continuity-tracker`, `literary-analysis`, `sr6-combat-choreography`, `sr6-downtime-ledger`, `sr6-narration-tts`).
3. **Character Voice Specification**: Loads local character repository `reference/voice_spec.md` (e.g., `characters/reiko/reference/voice_spec.md`, `characters/velvet/reference/voice_spec.md`), which inherits/extends `reference/default_voice_spec.md`.
4. **Master Character Dossier**: Reads `character_master.yaml` (attributes, inventory, ammo, nuyen, debt, qualities, spells, cyberware) as authoritative tabletop play state.
5. **RAG Story Continuity & Rules**: Queries recent chapter logs via `uv run sr6 continuity` and rule context via `sr6-rules` (always querying local offline FTS5 vault first via `uv run sr6 rag search` before cloud AI synthesis).

### Stage 2: Initial Draft Generation (`v1`)
`narrative-director` invokes the drafting sub-agent to generate Scene Draft `v1`, adhering to:
* POV, active era from `arc_chronology`, and cognitive bias from `voice_spec.md`.
* 4-beat scene structure (Inciting Friction $\rightarrow$ Escalation $\rightarrow$ Climax $\rightarrow$ Aftermath) and braided paragraph cadence from `axis-pacing-structure`.
* Thematic worldbuilding and atmospheric friction from `axis-worldbuilding-grit`.
* 29 anti-slop rules, affirmative staging, and "Trust the Reader" discipline from `no-ai-slop`.
* Tactical action and combat staging using `sr6-combat-choreography` when firefights, drone combat, or spellcasting occur.
* Mechanical reality constraints from `character_master.yaml` and dynamic weapon arrays (`calculate_modified_weapon`) without modifying tabletop balances.
* Audio narration and TTS readability guidelines (ellipses ceiling $\le 0.60$ per 300 words) from `sr6-narration-tts`.

### Stage 3: Parallel Sub-Agent Audit Panel
Draft `v1` is first analyzed using deterministic CLI utilities, then dispatched to the **7 sub-agent evaluators**:

1. **Deterministic Pre-Flight Check**:
   - Run `uv run sr6 lint "chapters/<file>.qmd"` for instant automated metrics on word count, paragraph braid ratios, ellipses ceiling, and banned buzzwords.
   - Run `uv run sr6 evaluate "chapters/<file>.qmd" --tier <1|2|3> --char <id>` to generate the baseline 7-axis scorecard.
2. **Sub-Agent Panel Dispatch**:
   - In Hermes Agent, dispatch parallel sub-agent audits via `delegate_task` across all 7 evaluation dimensions against the calibrated tier threshold:

| Sub-Agent Skill | Focus Dimension | Passing Threshold |
| :--- | :--- | :--- |
| **`axis-voice-internality`** | Character voice, POV integrity, vocabulary matrix, sensory lens, era calibration | Tier Calibrated (8.0–9.0) |
| **`axis-pacing-structure`** | 4-beat structure, entry/exit discipline, action-to-exposition (80/20) | Tier Calibrated (8.0–9.0) |
| **`axis-agency-motivation`** | Protagonist proactive choice, consequential stakes, drive alignment | Tier Calibrated (8.0–9.0) |
| **`axis-worldbuilding-grit`** | Dystopian texture, corporate omnipresence, AR clutter, zero info-dumps | Tier Calibrated (8.0–9.0) |
| **`no-ai-slop`** | Anti-slop pattern detection, forbidden terms list, redline removal, TTS fluency | **8.5 / 10** |
| **`continuity-tracker`** | Ammo/nuyen balances, damage tracks, contacts, state verification | **8.5 / 10** |
| **`sr6-rules`** | SR6 mechanics (Edge, Matrix actions, spell drain, tactical arrays) accuracy | **8.5 / 10** |

#### Chapter Tier Threshold Calibration (Unified 1.0–10.0 Scale)
* **Tier 1 (Keystones)**: Passing threshold **9.0 / 10** (Existential breakthroughs, initiation/submersion milestones, foundational pivots).
* **Tier 2 (Narrative Evolution)**: Passing threshold **8.5 / 10** (Mission runs, relationship deepening, regional texture, evolutionary steps).
* **Tier 3 (Atmospheric Bridges)**: Passing threshold **8.0 / 10** (Slice-of-life downtime, procedural mechanics, affectionately grounded banter).

### Stage 4: Synthesis & Automated Self-Correction Loop
1. `narrative-director` collates the audit reports into a unified **Revision Matrix**.
2. If any sub-agent score falls below its passing threshold, invoke `literary-analysis` (`apply_prose_chisel`) to formulate targeted line-level fixes.
3. The re-draft cycle (`v1` $\rightarrow$ `v2` $\rightarrow$ `v3`) repeats autonomously until **all 7 sub-agents pass threshold standards**.

### Stage 5: Publishing & State Tracking
Upon successful panel approval:
1. **Narrative Output**: Emits the final polished prose in chat for review, or writes to a clean Quarto markdown file (`.qmd`) in `chapters/` (e.g., `chapters/chapter_04.qmd`) if requested.
2. **State Updates (Markdown Trio as Single Source of Truth)**:
   - Tabletop state updates (nuyen, Karma, contacts, foci, ammo, purchases) must ALWAYS be proposed/recorded in the core Markdown Trio (`character_log.qmd`, `character_purchases.qmd`, `character_build.qmd`).
   - Deliver adjustments as ready-to-paste `{python} inc(...)` snippets in chat.
   - **NEVER edit `*_master.yaml` by hand.** The master YAML is compiled from scratch from the core markdown files via `uv run sr6 sync-all` or `uv run sr6 build`.

### Stage 6: Refinement Mode for Existing `.qmd` Files
When requested to refine an existing chapter (`.qmd`):
1. Run `uv run sr6 lint` and `uv run sr6 evaluate` on the existing file.
2. Dispatch feedback to the sub-agent audit panel and synthesize line-level chisel refactoring via `literary-analysis`.
3. Deliver drop-in replacements in chat or write the revised content directly to the target `.qmd` file so changes can be inspected instantly via git diff.

---

## 3. CLI Diagnostic Utilities

Before completing edits or reviewing narrative/character updates, run corresponding CLI commands:
* **Local Offline Rules Search**: `uv run sr6 rag search "<topic>" --compact` (instant 5-stage hybrid search with cross-edition references and statblocks)
* **Item Reference Cards**: `uv run sr6 card <quality|weapon|spell|cyberware|vehicle|program> <name>`
* **Prose & Markdown Linter**: `uv run sr6 lint "chapters/<file>.qmd"`
* **7-Axis Narrative Evaluator**: `uv run sr6 evaluate "chapters/<file>.qmd" --tier <1|2|3> --char <id>`
* **Combat Ledger Action Parser**: `uv run sr6 ledger parse "chapters/<file>.qmd"`
* **Continuity Engine**: `uv run sr6 continuity <repo_path>`
* **Character Creation Auditor**: `uv run sr6 characters audit [char_id]`
* **Combat Opposed Simulation**: `uv run sr6 combat attack --pool <X> --ar <Y> --target-dr <Z>`
* **Dice Pool Roller**: `uv run sr6 roll <dice_pool> [--edge]`
* **TTS Narration Generation**: `uv run sr6 narrate "chapters/<file>.qmd" --voice af_heart`
* **Ecosystem Sync & Build**: `uv run sr6 sync-all`
* **Multi-Format Exporters**: `uv run sr6 export <char_id> --format=roll20|vtt|xml|text_modular`
* **Plugin Management**: `uv run sr6 plugin status` / `uv run sr6 plugin install`

---

## 4. The 12-Skill Narrative Suite Reference

| Skill Name | Role | Primary Command / Pre-Flight |
| :--- | :--- | :--- |
| **`narrative-director`** | Master autonomous orchestrator for 6-stage lifecycle | `uv run sr6 evaluate` |
| **`axis-voice-internality`** | Character voice, deep limited POV, vocabulary matrix | `uv run sr6 evaluate` |
| **`axis-pacing-structure`** | 4-beat structure, paragraph braiding, dialogue integrity | `uv run sr6 lint` |
| **`axis-agency-motivation`** | Protagonist proactive choice, consequential stakes, parity | `uv run sr6 evaluate` |
| **`axis-worldbuilding-grit`** | Dystopian texture, corporate omnipresence, zero info-dumping | `uv run sr6 evaluate` |
| **`no-ai-slop`** | 29 anti-slop patterns, banned terms, affirmative staging | `uv run sr6 lint` |
| **`continuity-tracker`** | Ammo/nuyen/damage verification, Markdown Trio drop-ins | `uv run sr6 continuity` |
| **`sr6-rules`** | SR6 mechanics, stat blocks, local SQLite FTS5 queries | `uv run sr6 card` / `rag search` |
| **`literary-analysis`** | Stage 4 Prose Elevation & Chisel Engine (`apply_prose_chisel`) | `uv run sr6 evaluate` |
| **`sr6-combat-choreography`** | Tactical mechanics into somatic, braided action fiction | `uv run sr6 combat attack` |
| **`sr6-downtime-ledger`** | Karma progression, gear buying, `{python} inc(...)` snippets | `uv run sr6 card` / `sync-all` |
| **`sr6-narration-tts`** | Kokoro TTS audio prep, ellipses ceiling, phonetics | `uv run sr6 lint` / `narrate` |
