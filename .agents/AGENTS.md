# Master Workspace Agent Instructions: SR6 Core (`sr6-core`)

## Shadowrun 6e Rules & Mechanics Verification

When answering rules questions, updating character dossier files (`*_master.yaml`), auditing Karma/Nuyen ledgers, or verifying matrix/drone combat mechanics:
- Trigger the `sr6-rules` skill or run `sr6 rag query "<query>"` to consult the authoritative Shadowrun 6e Gemini RAG vault.
- Ensure all rules assertions follow the SRM 4-level authority hierarchy (Level 1 SRM Exception > Level 2 Supplements > Level 3 Core > Level 4 Homebrew).
- Provide explicit book and page citations wherever applicable (`[Book Name, Page Number]`).

## Writing & Narrative Anti-Slop (No AI Slop)

When writing or editing prose, narrative chapters (`chapters/*.md` / `chapters/*.qmd`), character questionnaire answers (`twenty_questions.qmd`), or user-facing summaries:
- Trigger or adhere to the `no-ai-slop` skill instructions (`.agents/skills/no-ai-slop/SKILL.md`).
- Avoid banned words (`delve`, `foster`, `leverage`, `robust`, `tapestry`, `realm`, `beacon`, `multifaceted`, `paradigm shift`, `cutting-edge`, `ever-evolving`).
- Eliminate AI writing patterns: binary contrasts ("not X, but Y"), colon reveals, fake-profound kickers, summary recaps, and throat-clearing openers.
- Run `sr6 lint <file>` to verify formatting, em-dash density, and style.
- **Walkthrough Metrics Logging:** Whenever `no-ai-slop` is invoked (for audits or editing), record the full performance metrics (banned word count, cognitive verb count, throat-clearing count, binary contrast count, em-dash density) in the run's `walkthrough.md` artifact.

## Literary Analysis & Prose Refactoring

When evaluating, scoring, or refactoring narrative chapters:
- Trigger the `literary-analysis` skill (`.agents/skills/literary-analysis/SKILL.md`).
- Execute sub-skills as required:
  1. `stage1_thematic_centering` for moral axis, SRM lore alignment, and exploring "the spaces between" (human condition via digital/spiritual phenomenology).
  2. `stage2_quality_benchmarking` for 1-10 literary scoring & artistic elevation of Shadowrun mechanics.
  3. `five_dimensional_scoring_matrix` for 1-100 metric evaluation across Concept, Prose, Characterization, Structure, and Meatspace/Matrix friction.
  4. `apply_prose_chisel` for line-level techno-poetic refactoring.
- **Walkthrough Metrics Logging:** Whenever `literary-analysis` is invoked, capture and record all scores, sub-skill metrics, and the 5D scoring matrix breakdown in the run's `walkthrough.md` artifact.

## Master Portfolio & Campaign Diagnostic Utilities

Before completing edits or reviewing narrative/character updates, run the corresponding CLI utilities:
- **Prose & Markdown Linter:** Run `sr6 lint "chapters/<file>.qmd"` to get instant diagnostics on markdownlint syntax formatting, em-dash density, cognitive verbs, banned words, and sentence length cadence.
- **Continuity Engine:** Run `sr6 continuity <repo_path>` or trigger `continuity-tracker` to index character relationships, sprite states, locations, and narrative heatmaps.
- **Character Creation Auditor:** Run `sr6 characters audit [char_id]` to verify Karma/Nuyen balance consistency and creation budget compliance across Yuriko, Velvet, and Union.
- **Multi-Format Sheet Exporters:** Run `sr6 export <char_id> --format=roll20|vtt|xml` to generate VTT sheets.
