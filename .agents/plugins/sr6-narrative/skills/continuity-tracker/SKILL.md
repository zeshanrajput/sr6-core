---
name: continuity-tracker
description: Track story continuity, gear, damage, and ledger state.
version: 1.0.0
author: Zeshan Rajput (zeshanrajput), Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [shadowrun, sr6, continuity, ledger, character-sheet]
    related_skills: [sr6-rules, sr6-downtime-ledger, narrative-director]
---

# Story Continuity & State Tracker Skill (`continuity-tracker`)

Use this skill to audit narrative drafts and downtime proposals for state consistency against the character's compiled dossier (`*_master.yaml`) and prior chapter log context within the `sr6-core` pipeline.

## When to Use

- Auditing narrative chapters during Stage 3 of the narrative pipeline.
- Cross-referencing ammo expenditure, damage tracks, nuyen, karma, and contact favor points against canonical character records.
- Verifying downtime purchases and proposing drop-in `{python} inc(...)` state adjustments for the Markdown Trio.

## How to Run

Execute deterministic continuity audits and ledger parsing via the `terminal` tool:

```bash
# Run campaign timeline & story continuity indexer
uv run sr6 continuity "characters/<char_id>"

# Parse combat ledger actions, ammo spent, and damage deltas from chapter prose
uv run sr6 ledger parse "characters/<char_id>/chapters/<file>.qmd"

# Verify exact item stats, nuyen price, and Essence cost before proposing updates
uv run sr6 card "<item_name>"
```

## Tabletop Play Firewall & Markdown Trio Rules

1. **The Tabletop Play Firewall**: Master dossiers (`*_master.yaml`) track **tabletop play session records only**. Fiction chapters serve as atmospheric framing between sessions. Fiction cannot spend unearned millions, wield unowned military hardware, or resurrect deceased contacts.
2. **Markdown Trio as Single Source of Truth**:
   - Tabletop state changes (nuyen, Karma, contacts, foci, ammo, purchases) must ALWAYS be recorded in the core Markdown Trio (`character_log.qmd`, `character_purchases.qmd`, `character_build.qmd`).
   - **NEVER propose direct edits or diffs to `*_master.yaml`.** Master YAML is auto-compiled from scratch via `sr6 sync-all` or `sr6 build`.
   - **Deliver drop-in snippets in chat**: Provide adjustments as ready-to-paste `{python} inc(...)` snippets or markdown list items.

## State & Inventory Audit Criteria

1. **Pre-Validation of Purchases / Installs:**
   - Always run `uv run sr6 card "<item>"` to confirm exact Essence cost, Nuyen price, and Availability before proposing state changes.
2. **Capability Consistency:**
   - Ensure gear, spells, and implants depicted in fiction exist on the character sheet.
3. **Narrative Anchor Consistency:**
   - Ensure contact names, locations, and relationships align with established campaign history.
4. **Chronological Causal Matrix Audit:**
   - Cross-reference chapter dates and timeline headers against intra-chapter backstory references (character age, dates of surgical procedures, death/burial dates of NPCs). Ensure causality flows consistently forward without temporal paradoxes.

## Audit Report Format

```markdown
### Axis: Continuity & State Tracking Evaluation
* **Master Dossier Referenced**: [Path to *_master.yaml]
* **Continuity Score**: [Score]/10 (Threshold: 8.5)

#### Capability & Continuity Verification
- **Capability Compliance**: [Pass / Violations (e.g. using unowned spells/gear)]
- **Contact & Location Anchors**: [Pass / Consistency with established contacts]
- **Tabletop Firewall**: Verified (Fiction does not alter official play ledger)
- **Chronological Causal Flow**: [Pass / Temporal contradictions detected]

#### Proposed Markdown Trio Adjustments (Drop-in Snippets)
```markdown
* **Ammo Expenditure (Ares Predator VI):** `{python} inc('Ammo_Heavy_Pistol', -6)`
* **Medical Patch Use (Trauma Patch):** `{python} inc('Trauma_Patch', -1)`
```
```
