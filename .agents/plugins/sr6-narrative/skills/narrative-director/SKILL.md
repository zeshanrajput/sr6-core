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

- Drafting a new campaign chapter iteratively beat-by-beat using a clean-room sub-agent (`narrative-director <target_file> <beat>` or `/draft-beat <target_file> <beat>`).
- Writing a campaign chapter from an outline, mission log, or table beat sheet.
- Auditing and refining an existing chapter (`.qmd` or `.md`) to high-end speculative fiction standards.
- Orchestrating the 7-axis evaluation panel and automated re-draft loop.

## Command Triggers & How to Run

1. **Beat-by-Beat Clean-Room Drafting (Primary Interactive Mode)**:
   Invoke directly in chat:
   ```text
   narrative-director <target_file> <beat>
   /draft-beat <target_file> <beat>
   ```
   *Examples:*
   - `narrative-director characters/reiko/narrative/36.md 2`
   - `/draft-beat characters/reiko/narrative/36.md "Beat 2"`
2. **Deterministic Pre-flight & Linting**:
   ```bash
   uv run sr6 lint "characters/<char_id>/chapters/<file>.qmd"
   ```
3. **Unified 7-Axis Evaluation**:
   ```bash
   uv run sr6 evaluate "characters/<char_id>/chapters/<file>.qmd" --tier <1|2|3> --char <char_id>
   ```

---

## Beat-by-Beat Clean-Room Drafting Protocol (`narrative-director <target_file> <beat>`)

To prevent overfitting ("Checklist Prose") and preserve organic literary voice, this workflow strictly separates **The Writer's Hat** (pure creative synthesis in an unpolluted sub-agent context window) from **The Editor's Hat** (deterministic linting and a single non-human review loop for egregious violations).

### Step 1: Just-in-Time (JIT) Creative Packet Curation
The coordinator assembles a focused, high-signal creative brief for the target beat containing **only** generative fuel—deliberately withholding 32-pattern slop lists, lexical quota tables, and 7-axis scorecards:
1. **Central Premise & Beat Target**: The chapter's governing premise, the target Beat outline from `<target_file>`, and the full prose of any preceding beats already drafted in `<target_file>` (to ensure seamless narrative flow and prevent cross-beat repetition).
2. **Character Voice Essence**: The protagonist's POV lens, active chronological era, Mindspeech (`*...*`) vs. acoustic speech (`"..."`) convention, and physical-vs-AR ontological grounding from `characters/<char_id>/reference/voice_spec.md`.
3. **Targeted Continuity & Canonical Excerpts**:
   - Excerpts (30–60 lines) from the 1–2 prior narrative chapters explicitly called back to in the beat.
   - Canonical SR6 hardware, quality, complex form, or spell descriptions queried via `uv run sr6 rag search` or `uv run sr6 card` for items featured in the beat.

### Step 2: Clean-Room Sub-Agent Dispatch — "The Writer's Hat" (`Draft v1`)
Invoke `invoke_subagent(TypeName="self", Role="Beat N Creative Drafter", ...)` with the curated creative packet.
- **No Rubric Policing in Pass 1**: Instruct the sub-agent to focus purely on emotional truth, sensory atmosphere, character voice, and scene momentum—with only basic structural framing (3–6 sentence braided paragraphs, one speaker per paragraph, and somatic translation of mechanics rather than tabletop jargon).
- Wait for the sub-agent to return `Draft v1`.

### Step 3: Non-Human Review Gate — "The Editor's Hat" (Max 1 Loop)
1. **Deterministic Diagnostics**: Write `Draft v1` to `scratch/beat_<N>_test.md` and run:
   ```bash
   uv run sr6 lint "scratch/beat_<N>_test.md"
   uv run sr6 evaluate "scratch/beat_<N>_test.md" --tier <1|2|3> --char <char_id>
   ```
2. **Egregious Violation Check**: Evaluate `Draft v1` alongside the CLI diagnostics to catch **egregious** narrative standard violations:
   - *Premise Drift*: Paragraphs that wander away from the central premise into encyclopedic tangents.
   - *Ontological / Continuity Breaks*: Mixing AR projections with physical mass, misrepresenting canonical SR6 hardware/mechanics, or breaking callback continuity.
   - *Structural & Slop Redlines*: Merged multi-speaker paragraphs, thesis-statement preaching, banned Tier 0 buzzwords, or glaring proximity echoes.
3. **Single-Loop Feedback (`v1` $\rightarrow$ `v2`)**:
   - Send a single targeted editorial note back to the drafting sub-agent via `send_message` (or apply a surgical micro-chisel if only 1–2 words are flagged) to resolve egregious violations.
   - **Stop after ONE review loop.** Do not iterate endlessly to force a sterile 10/10 mechanical score; it is completely acceptable for minor stylistic nuances to pass through to human review so the prose retains its pulse.
4. Remove `scratch/beat_<N>_test.md`.

### Step 4: Collaborative Human Line-Edit Gate
Write `Draft v2` into `<target_file>` (keeping any remaining undrafted beat outlines below a `---` divider), present the drafted beat and a concise pre-flight summary in chat, and **stop** for user line-level review before proceeding to the next beat.

---

## The 6-Stage Execution Procedure

### Stage 1: Context Ingestion
Before drafting or editing, assemble and ingest:
1. **Scene Outline / Prompt**: User-provided beat sheet, plot points, or run objectives.
2. **Master Narrative Doctrine & Storyboard Spec**: Read [`reference/inter_session_narrative_doctrine.md`](file:///c:/GitHub/sr6-core/reference/inter_session_narrative_doctrine.md) and [`reference/default_storyboard_spec.md`](file:///c:/GitHub/sr6-core/reference/default_storyboard_spec.md).
3. **Master Narrative Storyboard**: Read `characters/<char_id>/reference/storyboard.md` (check the active 6 thematic verticals, Tier B foils, consecrated telemetry, and story queue).
4. **Character Voice Specification / Craft Spec**: Read `characters/<char_id>/reference/voice_spec.md` (check `arc_chronology`, active era, cognitive bias, and domain vocabulary).
5. **Master Character Dossier & Resource Pressure**: Read `characters/<char_id>/<char_id>_master.yaml` and execute `uv run sr6 pressure <char_id> --yaml` to calculate exact financial mortgages and spiritual karma allocations.
6. **Continuity & Rules**: Run `uv run sr6 continuity "characters/<char_id>"` and query rules via `uv run sr6 rag search "<topic>" --compact`.

### Stage 2: Initial Draft Generation (`v1`)
Draft the scene adhering to the core narrative disciplines:
- **Pacing**: Strict 4-beat structure (Inciting Friction $\rightarrow$ Escalation $\rightarrow$ Climax $\rightarrow$ Aftermath).
- **Paragraph Cadence**: Braided 3–6 sentence paragraphs weaving physical action, sensory cues, and consequences.
- **Dialogue Integrity**: One speaker per paragraph (braided with that speaker's physical actions).
- **Anti-Slop & Scaffolding Removal**: Zero banned buzzwords, no olfactory checklist templates, affirmative staging (ban filler negatives), and zero game scaffolding/mechanics jargon (P30: no condition monitors, dice pools, action labels).
- **Two-Tier Dramatic Sphere**: Respect the Canon Ceiling on Tier A NPCs; direct permanent relational fractures and moral reckoning toward Tier B bespoke foils.
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
