---
name: narrative-director
description: Orchestrate 6-stage SR6 narrative generation, writers' room story breaking, and editorial audits.
version: 2.0.0
author: Zeshan Rajput (zeshanrajput), Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [shadowrun, sr6, orchestration, narrative, sub-agents, writers-room, showrunner]
    related_skills: [literary-analysis, no-ai-slop, continuity-tracker, sr6-rules, sr6-downtime-ledger, sr6-chapter-finalize]
---

# Master Narrative Director Skill (`narrative-director`)

The **Showrunner & Writers' Room Orchestrator** for Shadowrun 6e narrative generation, sub-agent delegation, iterative self-correction, and state tracking.

`narrative-director` coordinates the **Editorial House**, enforcing strict context boundaries between generative authoring ("The Writer's Hat") and deterministic diagnostic auditing ("The Editor's Hat").

```
                      +-----------------------------+
                      |   1. CONTEXT INGESTION      |
                      | Story Break & Story Packet  |
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
                      | 4. SYNTHESIS & CHISEL LOOP  |  <-- (Fails gates?
                      |  Line Chisel Worker (flash) |       Draft v2 in scratch/)
                      +--------------+--------------+
                                     | Passes
                                     v
                      +-----------------------------+
                      |  5. PUBLISH & STATE TRACK   |
                      | Drop-in Prose & Python diffs|
                      +-----------------------------+
```

---

## When to Use

- Breaking a new chapter or arc beat in the Writers' Room from `reference/storyboard.md`.
- Drafting a chapter beat-by-beat via a clean-room sub-agent (`narrative-director <target_file> <beat>` or `/draft-beat <target_file> <beat>`).
- Assembling deterministic JIT creative packets with `uv run sr6 story packet`.
- Orchestrating the Editorial House audit panel (`literary-analysis`, `no-ai-slop`, `continuity-tracker`, `sr6-rules`).
- Directing the Line Chisel Worker (`flash`) to polish drafts against hard editorial readiness gates.
- Managing inter-session state handoffs and the Markdown Trio single-source-of-truth architecture.

---

## Command Triggers & CLI Diagnostics

1. **Beat-by-Beat Clean-Room Drafting (Primary Interactive Trigger)**:
   ```text
   narrative-director <target_file> <beat>
   /draft-beat <target_file> <beat>
   ```
   *Examples:*
   - `narrative-director characters/reiko/narrative/36.md 2`
   - `/draft-beat characters/velvet/narrative/14_Opal.md "Beat 3"`

2. **Deterministic Context Packet Assembly** (write directly to `scratch/` so large packets do not bloat parent chat context):
   ```bash
   uv run sr6 story packet <char_id> <target_file> [--beat N] [--callbacks ...] [--items ...] --output scratch/packet_<char_id>_beat_<N>.md
   ```

3. **Deterministic Linting, N-3 Echo Window & Tier/Voice Calibration**:
   ```bash
   uv run sr6 lint "characters/<char_id>/narrative/<file>.md" --window 3 --tier <1|2|3> --char <char_id>
   ```
   *(Replaces separate `sr6 lint` + `sr6 evaluate` calls; `sr6 evaluate` remains available as an alias.)*

---

## The Writers' Room & Context Firewall Protocol

To prevent overfitting ("Checklist Prose") and protect natural prose rhythm, `narrative-director` strictly separates creative generative synthesis from mechanical copyediting across two distinct phases.

### Phase 1: Writers' Room Story Break & Pre-Flight Packet

Before dispatching any writing agent, the showrunner transforms story intent into a clean generative brief:
1. **Story Break**: Select a Story Queue item from `characters/<char_id>/reference/storyboard.md` and decompose it into a crisp 4-beat structure (Inciting Friction $\rightarrow$ Escalation $\rightarrow$ Climax $\rightarrow$ Aftermath).
2. **Deterministic Packet Assembly**: Run `sr6 story packet` to curate an isolated context packet directly to `scratch/`:
   ```bash
   uv run sr6 story packet <char_id> <target_file> --beat <N> --output scratch/packet_<char_id>_beat_<N>.md
   ```
   The generated packet bundles:
   - Chapter Central Premise and target Beat outline.
   - Verbatim prose of preceding drafted beats in `<target_file>` (preventing repetition and preserving momentum).
   - Character Voice Essence: POV constraints, active chronological era, Mindspeech (`*...*`) vs acoustic speech (`"..."`) rules, and sensory/somatic translation lenses from `reference/voice_spec.md`.
   - Canonical SR6 item and quality reference cards queried from the rules vault.
   - Targeted excerpts (30–60 lines) from the 1–2 prior narrative chapters called back to in the beat.

---

### Phase 2: Context Firewall & Deterministic Sandwich Protocol for Sub-Agents

```
 [JIT Story Packet] 
         │
         ▼
 ┌────────────────────────────────────────┐
 │ 1. Clean-Room Writer Sub-Agent         │  Model: inherit / pro
 │    - Receives ONLY the story packet    │  Focus: Voice, sensory truth, emotional stakes
 │    - ZERO slop lists or scorecards     │  Produces: Draft v1
 └───────────────────┬────────────────────┘
                     │ Draft v1
                     ▼
 ┌────────────────────────────────────────┐
 │ 2. Non-Human Review Gate (CLI Linter)   │  Deterministic diagnostic checks
 │    - uv run sr6 lint --window 3        │  Flags hard gates, cluster saturation,
 │      --tier <1|2|3> --char <id>        │  tier benchmarks & voice_spec rules
 └───────────────────┬────────────────────┘
                     │ Draft v1 + Linter Diffs
                     ▼
 ┌────────────────────────────────────────┐
 │ 3. Line Chisel Worker Sub-Agent        │  Model: flash
 │    - Receives Draft v1 + Linter output │  Applies: 5 Chisel Transformations
 │    - Stages Draft v2 in scratch/       │  Max 1 Loop before human review
 └───────────────────┬────────────────────┘
                     │ Draft v2
                     ▼
 ┌────────────────────────────────────────┐
 │ 4. Collaborative Human Line-Edit Gate  │  Presents Draft v2 + Telemetry in chat
 │    - Stops for user line review        │  User approves before next beat
 └────────────────────────────────────────┘
```

#### Step 1: Clean-Room Writer (`inherit` / `pro`) — "The Writer's Hat"
Invoke `invoke_subagent(TypeName="self", Role="Beat N Creative Drafter", ...)` passing **ONLY** the assembled `sr6 story packet` output.
- **Context Firewall**: Withhold all 32-pattern slop lists, negative rules, lexical quota tables, and 7-axis evaluation scorecards.
- **Generative Prompt**: Instruct the drafter to focus 100% on emotional authenticity, sensory immersion, character voice, and pacing friction. The only structural constraints provided are: braided 3–6 sentence paragraphs, one speaker per paragraph, and somatic translation of mechanics rather than tabletop jargon.
- Drafter returns `Draft v1`.

#### Step 2: Line Chisel Worker (`flash`) — "The Editor's Hat"
1. Stage `Draft v1` to `scratch/beat_<N>_test.md` and run unified deterministic diagnostics:
   ```bash
   uv run sr6 lint "scratch/beat_<N>_test.md" --window 3 --tier <1|2|3> --char <char_id>
   ```
2. If `sr6 lint` flags defects or any hard gate fails, invoke a fast line-chisel sub-agent (`flash`):
   - Provide the chisel worker with **ONLY** `Draft v1`, the specific line warnings and `ZERO-RENT SUSPECTS` from `sr6 lint`, and the 5 Chisel Transformations + 3-Step Active Chisel Discipline (Declare Paragraph Job $\rightarrow$ Active Eviction Pass targeting `-5%` to `-8%` words $\rightarrow$ Post-Cut Load-Bearing Readback Test, reporting net word-count delta) from [`literary-analysis`](file:///c:/GitHub/sr6-core/.agents/plugins/sr6-narrative/skills/literary-analysis/SKILL.md) (`apply_prose_chisel`).
   - The worker executes surgical line adjustments and saves `Draft v2` in `scratch/beat_<N>_test.md`.
3. **Hard Constraint: Max 1 Review Loop**:
   - The system executes at most **ONE** automated chisel pass. Minor stylistic nuances are preserved for the human editor rather than over-sterilizing the prose to satisfy a mechanical metric.
4. Clean up `scratch/beat_<N>_test.md`.

#### Step 3: Collaborative Human Line-Edit Gate
Write `Draft v2` into `<target_file>` (retaining undrafted beat outlines below a `---` divider). Present the drafted beat and a concise craft telemetry summary in chat, then **stop** for user line-level review before advancing to the next beat.

---

## The 6-Stage Narrative Lifecycle

### Stage 1: Context Ingestion & Pre-Flight
- Showrunner pulls active arc milestones from `reference/storyboard.md` and `reference/voice_spec.md`.
- Gathers financial mortgages and spiritual debt via `uv run sr6 char pressure <char_id>`.
- Generates creative packet via `uv run sr6 story packet <char_id> <target_file> --beat <N> --output scratch/packet_<char_id>_beat_<N>.md`.

### Stage 2: Initial Draft Generation (`v1`)
- Authored beat-by-beat behind the Context Firewall.
- Strict deep-limited third-person POV.
- Somatic translation: Mechanics are felt (chassis fatigue, buffer overflow, recoil ache), never named as game tokens (Edge points, dice pools, condition boxes).
- Adheres to the Two-Tier Dramatic Sphere: Tier A campaign NPCs respect the Canon Ceiling; Tier B bespoke foils carry mortal consequence.

### Stage 3: Editorial House Audit Panel
Audit drafts across the Editorial House framework (dispatch `research` or `flash` sub-agents for parallel Series Bible, continuity, and craft checks before parent synthesis):
- **Positive Craft & Action**: Governed by [`literary-analysis`](file:///c:/GitHub/sr6-core/.agents/plugins/sr6-narrative/skills/literary-analysis/SKILL.md).
- **Negative Copyedit & Anti-Slop**: Governed by [`no-ai-slop`](file:///c:/GitHub/sr6-core/.agents/plugins/sr6-narrative/skills/no-ai-slop/SKILL.md).
- **Continuity & Entity Tracking**: Governed by [`continuity-tracker`](file:///c:/GitHub/sr6-core/.agents/plugins/sr6-narrative/skills/continuity-tracker/SKILL.md).
- **TTRPG Mechanics & Gear**: Governed by [`sr6-rules`](file:///c:/GitHub/sr6-core/.agents/plugins/sr6-narrative/skills/sr6-rules/SKILL.md).

### Stage 4: Synthesis & Line Chisel Refactoring
- Collates diagnostic warnings into a focused revision matrix.
- The Line Chisel Worker applies the 5 Chisel Transformations using the **3-Step Active Chisel Discipline** (Lock Paragraph Job $\rightarrow$ Active Eviction Pass targeting `-5%` to `-8%` words using `ZERO-RENT SUSPECTS` $\rightarrow$ Load-Bearing Readback Test, reporting net word-count delta):
  1. Braiding fragmented staccato lines into flowing 3–6 sentence paragraphs.
  2. Converting tabletop math into consecrated capital and somatic rent.
  3. Pruning lazy meta-exposition while preserving essential domain scaffolding.
  4. Enforcing affirmative staging (eliminating gratuitous filler negatives).
  5. Executing the "Pay Rent" Modifier & Stage-Direction Scalpel (stripping tautological adjectives, horror intensifiers, pre-action emotion labels, clinical intrusions, and adjacent body/image echoes).

### Stage 5: Publishing & State Tracking (Markdown Trio)
- Write polished prose directly to `characters/<char_id>/narrative/<file>.md` or `chapters/<file>.qmd`.
- Propose any in-fiction tabletop resource expenditures (nuyen, Karma, ammo, damage, contact favor) as drop-in `{python} inc(...)` snippets for `character_log.qmd` or `character_purchases.qmd`.
- **NEVER edit `*_master.yaml` directly.** The user or pipeline runs `uv run sr6 sync-all` to recompile master state.

### Stage 6: Refinement Mode for Existing Chapters
Invoked via `literary-analysis <target_file>` to run unified diagnostics (`uv run sr6 lint "<target_file>" --window 3 --tier <1|2|3> --char <char_id>`), delegate Series Bible cross-checks (`research`/`flash`) and active line chiseling (`flash` Line Chisel Worker running the 3-Step Active Chisel Discipline with net word-count delta), and output drop-in diffs.

---

## Editorial Readiness Gates & Craft Telemetry Format

Replaces legacy synthetic scorecards with deterministic gates and descriptive craft metrics:

```markdown
# 📋 SR6 Narrative Editorial Telemetry

* **Target File**: `[characters/<char_id>/narrative/<file>.md]`
* **Designated Tier**: Tier [1|2|3]
* **Word Count**: [N] words | **Average Sentence Length**: [N] words (CV: [N])

### 🚦 Hard Editorial Readiness Gates
| Gate | Target Standard | Measured Value | Status |
| :--- | :--- | :---: | :---: |
| **Tier 0 Banned Buzzwords** | Exactly 0 | [N] | [✅ PASS / ❌ FAIL] |
| **Multi-Speaker Paragraphs** | Exactly 0 (1 speaker/para) | [N] | [✅ PASS / ❌ FAIL] |
| **Ellipses Density** | $\le 0.60$ per 300 words | [N] | [✅ PASS / ❌ FAIL] |
| **N-3 Proximity Echo Window** | Zero cross-chapter echo collisions | [N] | [✅ PASS / ❌ FAIL] |
| **Unicode Cleanliness** | Exactly 0 `\ufffd` artifacts | [0] | [✅ PASS / ❌ FAIL] |

### 📊 Descriptive Craft Telemetry
| Metric | Observed Range | Target Benchmark | Craft Assessment |
| :--- | :---: | :---: | :--- |
| **Braided Paragraph Cadence** | [N]% | $\ge 75\%$ (3–6 sentences) | [Cohesive flow / Staccato warnings] |
| **Single-Sentence Pivots** | [N] / 1k words | $\le 1\text{–}2$ per 1k words | [Reserved for dramatic pivots] |
| **Sentence Burstiness (CV)** | [Value] | $\ge 0.45$ | [Rhythmic variation vs. monotone] |
| **Domain Staging & Somatic Rent**| [Verified] | Zero game jargon | [Clean somatic immersion] |

### 🛠️ Line Chisel Actions & Next Steps
1. [ ] **Line [N]**: [Specific chisel transformation applied or recommended]
```
