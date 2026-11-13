# Narrative Director: Master Narrative Production Orchestrator

This document defines the routing logic, sub-agent capabilities, narrative standards, and the **Primary Master Orchestrator (`narrative-director`)** for the Shadowrun 6e multi-agent narrative production framework across `sr6-core` and character repositories (`sr6yuriko`, `sr6velvet`, `sr6union`, etc.).

---

## 1. The Editorial House Framework & Master Orchestrator

The SR6 narrative ecosystem is organized as an **Editorial House** of specialized skills coordinated by `narrative-director`. Rather than fragmenting literary craft across single-axis sub-skills, craft is consolidated into specialized functional engines:

| Specialist Engine / Skill | Editorial Role | Primary Responsibilities & Triggers |
| :--- | :--- | :--- |
| **`narrative-director`** | Showrunner & Writers' Room Orchestrator | Storyboard breaking (`storyboard.md`), deterministic context packet compilation (`uv run sr6 story packet`), clean-room writer dispatch, and two-hat review sandwich. |
| **`literary-analysis`** | Positive Literary Craft & Developmental Chisel | 4 craft axes (Voice & Internality, Pacing & Structure, Agency & Stakes, Worldbuilding & Grit), domain action choreography, hard readiness gates, craft telemetry, and line chisel transformations (`apply_prose_chisel`). |
| **`no-ai-slop`** | Negative Copyedit & Anti-Slop Guardian | 32-pattern slop and cliché elimination, forbidden terms list, affirmative staging, TTS oral fluency, and line-level redline excision. |
| **`continuity-tracker`** | Lore Continuity & Entity Tracking | Story continuity verification, character dossiers, foil status (Tier A canon vs. Tier B bespoke), timeline integrity, and cross-chapter entity matrix sync. |
| **`sr6-rules`** | TTRPG Systems & Rules Authority | Shadowrun 6e mechanics, Edge economy, Matrix actions, spell drain, tactical arrays, and local FTS5 rules chunk retrieval (`uv run sr6 rag search`, `uv run sr6 card`). |
| **`sr6-downtime-ledger`** | Tabletop Ledger & Session Ingestion | Session recap ingestion (Tri-Source), SRM v2.4 downtime activity taxonomy, contact favor points, Karma/nuyen ledgers, and post-session Writers' Room pitches. |
| **`sr6-chapter-finalize`** | Audio Narration & Publishing Pipeline | Audio prep (`uv run sr6 story prep-audio`), Kokoro TTS narration synthesis, GitHub Release asset upload, project navigation sync (`uv run sr6 story sync`), and scheduled CI/CD verification. |

```
                      +-----------------------------+
                      |   1. CONTEXT INGESTION      |
                      | Story Packet, Voice, Dossier|
                      +--------------+--------------+
                                     |
                                     v
                      +-----------------------------+
                      |   2. INITIAL DRAFT (v1)     |
                      | Clean-Room Writer Sub-Agent |
                      +--------------+--------------+
                                     |
                                     v
         +-------------------------------------------------------+
         |            3. PARALLEL SUB-AGENT AUDIT PANEL          |
         |  - literary-analysis        - no-ai-slop              |
         |  - continuity-tracker       - sr6-rules               |
         +---------------------------+---------------------------+
                                     |
                                     v
                      +-----------------------------+
                      | 4. SYNTHESIS & SELF-CORRECT |  <-- (Fails readiness?
                      |  Hard Gates & Telemetry     |       Re-draft v2 in scratch/)
                      +--------------+--------------+
                                     | Passes
                                     v
                      +-----------------------------+
                      |  5. PUBLISH & STATE TRACK   |
                      | Drop-in Prose & Python diffs|
                      +-----------------------------+
```

---

## 2. Seven-Stage Execution Workflow

### Stage 1: Context Ingestion & Story Breaking
Before drafting or editing, `narrative-director` ingests:
1. **Writers' Room Story Break & Pre-Flight Packet**: Turn a `storyboard.md` queue item into a 4-beat scene card and compile the writer's context deterministically using:
   ```bash
   uv run sr6 story packet <char_id> <target_file> [--beat N] [--callbacks ...] [--items ...]
   ```
2. **Master Narrative Doctrine & Storyboard Spec**: Ingest [`reference/inter_session_narrative_doctrine.md`](file:///c:/GitHub/sr6-core/reference/inter_session_narrative_doctrine.md) and [`reference/default_storyboard_spec.md`](file:///c:/GitHub/sr6-core/reference/default_storyboard_spec.md) as the governing operational constitution.
3. **Master Character Voice Specification**: Ingest `characters/<char_id>/reference/voice_spec.md` (inheriting `reference/default_voice_spec.md`): active era, POV lens, vocabulary matrix, sensory lens, and somatic translation doctrine.
4. **Master Character Dossier & Consecrated Capital**: Ingest `character_master.yaml` and run `uv run sr6 char pressure <char_id>` to anchor financial/karmic weight (chassis mortgages, bioware leases, identity debt).
5. **RAG Story Continuity & Rules**: Run `uv run sr6 continuity characters/<char_id>` and query local FTS5 rules chunks via `uv run sr6 rag search "<topic>" --compact`.

### Stage 2: Clean-Room Beat-by-Beat Drafting (`narrative-director <target_file> <beat>`)
To prevent overfitting ("Checklist Prose") and protect voice, `narrative-director` strictly enforces the **Context Firewall & Deterministic Sandwich Protocol**:
1. **The Writer's Hat (`Draft v1`)**:
   - Dispatch a clean-room sub-agent (`pro` or `inherit`).
   - The drafter receives **ONLY** the deterministic `uv run sr6 story packet` output (premise, target beat outline, preceding beat prose, character voice essence, and targeted lore/item cards).
   - **Zero Rubric Dumping**: Withhold 32-pattern slop lists, lexical quota tables, and 7-axis scorecards from Pass 1 so the drafter focuses entirely on emotional truth, voice cadence, and sensory momentum.
2. **The Editor's Hat (Non-Human Review Gate — Max 1 Loop to `Draft v2`)**:
   - Stage `Draft v1` to `scratch/beat_<N>_test.md`.
   - Run deterministic diagnostics:
     ```bash
     uv run sr6 lint "scratch/beat_<N>_test.md" --window 3
     uv run sr6 evaluate "scratch/beat_<N>_test.md" --tier <1|2|3> --char <char_id>
     ```
   - Check for **egregious violations**: premise drift, AR/physical ontological blurring, merged multi-speaker paragraphs, Tier 0 buzzwords, or broken callback continuity.
   - Dispatch the Line Chisel Worker (`flash`) with `Draft v1` + `sr6 lint --window 3` output + the 4 Chisel transformations from `literary-analysis` to produce `Draft v2` in `scratch/`.
   - **Stop after ONE review loop.** Minor stylistic nuances pass through to human review to preserve organic voice. Clean up `scratch/beat_<N>_test.md`.
3. **Collaborative Human Line-Edit Gate**:
   - Promote `Draft v2` into `<target_file>`, present the beat and pre-flight telemetry in chat, and **stop** for user line-level review before advancing to the next beat.

### Stage 3: Sub-Agent Audit Panel (Hard Gates & Craft Telemetry)
Drafts are audited against **Hard Editorial Readiness Gates** and **Descriptive Craft Telemetry** calibrated to chapter tier:

| Audit Engine | Focus Dimension | Passing Standard / Gate |
| :--- | :--- | :--- |
| **`literary-analysis`** | Voice & Internality | Deep limited 3rd POV, sensory palette, era alignment, somatic translation |
| **`literary-analysis`** | Pacing & Structure | 4-beat structure, entry/exit discipline, braided cadence, 80/20 balance |
| **`literary-analysis`** | Agency & Stakes | Proactive protagonist choice, Tier A Canon Ceiling, Tier B mortal stakes |
| **`literary-analysis`** | Worldbuilding & Grit | Sensory dystopian texture, corporate omnipresence, zero info-dumping |
| **`no-ai-slop`** | Anti-Slop Guardian | **Hard Gate**: Zero Tier 0 buzzwords, zero `\ufffd`, ellipses $\le 0.60$/300w, zero proximity echoes |
| **`continuity-tracker`** | Continuity & State | Ammo/nuyen balances, damage monitors, contact matrices, timeline integrity |
| **`sr6-rules`** | Rules & Mechanics | SR6 mechanics (Edge, Matrix actions, spell drain, tactical arrays) accuracy |

#### Chapter Tier Readiness Thresholds
* **Tier 1 (Keystones)**: Existential breakthroughs, initiation/submersion milestones, profound moral pivots. Strict gate compliance, elevated sentence burstiness, deep somatic friction.
* **Tier 2 (Narrative Evolution)**: Mission runs, shadowrun tradecraft, relationship deepening, regional texture. Tight tactical pacing, dark humor, grounded dialogue.
* **Tier 3 (Atmospheric Bridges)**: Meditative downtime, somatic maintenance, tea/noodle sanctuaries, grounded banter. Warm texture, domestic survival routines.

### Stage 4: Synthesis & Line Chisel Refactoring Loop
1. `narrative-director` collates audit findings into a unified **Revision Matrix**.
2. If any Hard Readiness Gate fails or craft telemetry flags defects:
   - Invoke `literary-analysis` (`apply_prose_chisel`) and `no-ai-slop` to execute surgical line-level refactoring.
   - Refactor staccato lines into braided 3–6 sentence paragraphs, enforce single-sentence quotas ($\le 1\text{–}2 / 1,000$ words), and prune negative non-actions.
   - Re-verify using `uv run sr6 lint "<target_file>" --window 3`.

### Stage 5: Publishing & State Tracking (Markdown Trio as Single Source of Truth)
Upon panel approval:
1. **Narrative Output**: Emits final polished prose as a Quarto document (`.qmd`) or Markdown chapter (`.md`) in `characters/<char_id>/narrative/` or `chapters/`.
2. **State Updates via Markdown Trio**:
   - Provide drop-in `{python} inc(...)` snippets in chat for `character_log.qmd` or `character_purchases.qmd` (nuyen, Karma, ammo, damage, contact favor).
   - **NEVER edit `*_master.yaml` directly.** The master YAML is compiled strictly from the Markdown Trio via `uv run sr6 sync-all` or `uv run sr6 build`.

### Stage 6: Refinement Mode for Existing Chapters (`literary-analysis <target_file>`)
Invoked via `literary-analysis <target_file>` or `/literary-analysis <target_file>`:
1. Run `uv run sr6 lint "<target_file>" --window 3` and `uv run sr6 evaluate "<target_file>" --tier <1|2|3> --char <id>`.
2. Execute the 4 Chisel Transformations from `literary-analysis` (`apply_prose_chisel`).
3. Re-verify zero regressions and deliver drop-in prose diffs with transparent craft callouts (single-sentence pivot justifications and contextual scaffolding rationale).

### Stage 7: Standardized Chapter Finalization & CI/CD Verification (`/finalize-chapter <target_file>`)
Invoked via `/finalize-chapter <target_file>` or `finalize-chapter <target_file>`:
1. **Pre-Flight Lint**: Run `uv run sr6 lint "<target_file>"`.
2. **Audio Prep & Narration**: Run `uv run sr6 story prep-audio "<target_file>"` to verify phonetics in `reference/pronunciations.yaml`, then synthesize audio via `uv run --extra narration sr6 narrate "<target_file>" --char <char_id>`. Upload MP3 to GitHub Release (`gh release upload narrative-audio-v1 ... --clobber`) under zero-git-bloat policy.
3. **Project Context & Series Bible Closeout**: Run `uv run sr6 story sync <char_id>` and `uv run sr6 sync-all`. Resolve Bible drift alerts across `storyboard.md`, `voice_spec.md`, and `visual_anchors.md`.
4. **Git Commit Protocol**: Stage commit message in `scratch/commit_msg.txt`, commit via `git commit -F scratch/commit_msg.txt`, clean up, and push to `origin/master`.
5. **CI/CD Verification**: Schedule 8-minute timer (`schedule(DurationSeconds=480, ...)`), wake up, and verify GitHub Actions runs with `gh run list --limit 3`.

---

## 3. CLI Diagnostic Utilities

Before completing edits or reviewing narrative/character updates, run corresponding CLI commands:
* **Story Packet Assembler**: `uv run sr6 story packet <char_id> <target_file> [--beat N] [--callbacks ...] [--items ...]`
* **Audio Pronunciation Prep**: `uv run sr6 story prep-audio "<target_file>"`
* **Prose & Markdown Linter**: `uv run sr6 lint "<file>" [--window 3]`
* **7-Axis Narrative Evaluator**: `uv run sr6 evaluate "<file>" --tier <1|2|3> --char <id>`
* **Narrative Context Synchronizer**: `uv run sr6 story sync <char_id>`
* **Resource Pressure Calculator**: `uv run sr6 char pressure <char_id>`
* **Continuity Engine**: `uv run sr6 continuity characters/<char_id>`
* **Rules Search & Chunk Inspector**: `uv run sr6 rag search "<topic>" --compact` / `uv run sr6 rag get <ID> --compact`
* **Item Reference Cards**: `uv run sr6 card <quality|weapon|spell|cyberware|pack> <name>`
* **Character Creation Auditor**: `uv run sr6 characters audit [char_id]`
* **Ecosystem Sync & Build**: `uv run sr6 sync-all`
* **Multi-Format Exporters**: `uv run sr6 export <char_id> --format=roll20|vtt|xml|text_modular`
