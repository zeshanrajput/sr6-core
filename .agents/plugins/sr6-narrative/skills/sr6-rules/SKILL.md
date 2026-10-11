---
name: sr6-rules
description: Verify Shadowrun 6e rules, mechanics, and item stats.
version: 1.0.0
author: Zeshan Rajput (zeshanrajput), Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [shadowrun, sr6, rules, mechanics, items, rag]
    related_skills: [continuity-tracker, sr6-combat-choreography, narrative-director]
---

# Shadowrun 6e Rules & Mechanics Verification Skill (`sr6-rules`)

Use this skill to verify official Shadowrun 6th Edition (SR6) rules, matrix/drone combat mechanics, spell drain formulas, Edge expenditures, and tactical stat blocks against the local offline rules database.

## When to Use

- Verifying tabletop rules legality during narrative drafting or Stage 3 panel audits.
- Checking downtime advancement costs, Essence calculations, nuyen pricing, or item Availability.
- Resolving rules interactions between core rules and supplemental sourcebooks.

## How to Run

Execute local rules queries via the `run_command` tool from the workspace root:

```bash
# Display universal item or PACK reference card (weapons, qualities, spells, cyberware, packs, drones, metamagics)
uv run sr6 card "<item_name>"
uv run sr6 card metamagic "<metamagic_name>"
uv run sr6 card pack "<pack_name>"

# Search verbatim sourcebook chapters using book codes (6wc, bs, crb, hns, dc, fs, sw, cn, pp, so, da, srm)
uv run sr6 source <book_code> "<query>" [--context 12]

# Calculate cyberlimb essence, cost, and capacity with enhancements and Adapsin
uv run sr6 calc limb --limb cyberarm --grade used --adapsin --agi 4
uv run sr6 calc limb --limb cyberleg --grade used --adapsin --agi 4 --bulk 4

# Display tabletop rules cheatsheets (matrix, actions, monad, combat, metamagic)
uv run sr6 cheat <matrix|actions|monad|combat|metamagic>

# Query SQLite tables directly with read-only SQL (use --compact for clean Markdown tables)
# The Canonical 2-Step Fast Retrieval Protocol (Reduces 30+ queries to 2):
# Step 1: Search local 20,082-chunk FTS5 rules vault (displays ranked results with [RULE_ID])
uv run sr6 rag search "<topic_or_keyword>" --compact

# Step 2: Retrieve full text for one or multiple rule chunks in a single call (<5ms, zero LLM cost)
uv run sr6 rag get <ID1> <ID2> <ID3> ... --compact
# (Also works as: uv run sr6 rules get <ID1> <ID2> ... --compact)

# Search verbatim sourcebook chapters using book codes (crb, sw, srmg, 6wc, bs, hns, dc, fs, cn, pp, so, da, wl, ec, aw)
uv run sr6 source <book_code> "<query>" [--context 12]

# Query SQLite tables directly with read-only SQL (use --compact for clean Markdown tables)
uv run sr6 db query "SELECT id, topic, content FROM rules WHERE topic LIKE '%Channeling%' LIMIT 5;" --compact

# Inspect table schemas and column definitions
uv run sr6 db schema [table_name]

# General CommLink6 reference database search
uv run sr6 search "<item_name>"

# AI-assisted rules synthesis for complex multi-condition edge cases
uv run sr6 rag query "<rules_question>" --compact
```

> [!IMPORTANT]
> **The 2-Step Fast Rules Retrieval Protocol**:
> Always use the 2-step protocol for looking up subsystem mechanics, critter powers, metamagics, and SRM rulings:
> 1. `uv run sr6 rag search "<topic>" --compact` $\rightarrow$ identifies matching chunk IDs (`[SW-0520]`, `[SRMG-0304]`).
> 2. `uv run sr6 rag get <ID1> <ID2> ... --compact` $\rightarrow$ prints complete unabridged rule markdown for all IDs in one command.
>
> **Core SQLite Rules Schema (`~/.sr6/rules_index.db`)**:
> - `rules`: `id, source, chapter, topic, authority_level, tags, content`
> - `rules_fts`: `id, source, chapter, topic, tags, content`
> - `ref_spells`, `ref_adept_powers`, `ref_qualities`, `ref_cyberware`, `ref_gear`, `ref_weapons`, `ref_actions`, `ref_contacts`.
>
> **Direct Sourcebook Exploration (`converted_md/`)**:
> Full verbatim markdown conversions of all SR6 rulebooks and Missions guides reside in `converted_md/`. Use `uv run sr6 source <book_code> "<query>"` (e.g. `srmg`, `sw`, `crb`, `6wc`) or ripgrep in `converted_md/` to read full paragraphs and tables.
>
> **Strict Mandate: No Python Gymnastics**:
> Never execute ad-hoc `python -c "..."` scripts or one-liners to query databases. Always use `uv run sr6 rag get`, `uv run sr6 rag search`, `uv run sr6 source`, or `uv run sr6 db query "<SQL>"`.

## Mandatory Pre-Computation & Verification Protocols

1. **Rule of Zero Memory Guessing**:
   - Never guess Essence costs, Nuyen prices, Availability ratings, or Karma costs.
   - Always run `uv run sr6 card "<item>"`, `uv run sr6 db query "<SQL>"`, or `uv run sr6 rag get "<rule>"` before proposing mechanical moves, purchases, or ledger adjustments.
2. **Dynamic Tactical Arrays (`calculate_modified_weapon`)**:
   - Verify post-modification numbers depicted in narrative action:
     - **Smartlinks**: +2 Attack Rating, +2 Attack Dice (when using smartguns with DNI or smartlink goggle/eyeware).
     - **Barrel Modifications**: Extended Barrel (+1/+2 Far AR), Suppressors/Silencers.
     - **Ammunition**: APDS (increased Penetration / AR vs Armor), Explosive (+1 DV), Stick-n-Shock (Stun Damage + Shock status).
3. **Digital Intelligence & Monad Rules (*Null Value* & *Whisper Nets*)**:
   - **Mindspeech (Native Language)**: Official Logic-based language for DIs, Proto-SAPs, and Resonance entities (*Null Value, CAT28452*). Operates as non-acoustic, instantaneous ideational communication carrying emotional metadata and resonance frequency.
   - **Linguasofts & Acoustic Execution**: Pure DIs without biological vocal cords must execute rated Linguasofts (Rating 1–6) through hardware audio synthesizers or drone diaphragms to speak aloud to mundanes in meatspace.
   - **Monad Dual-Consciousness**: Asymmetric communication between biological host and internal emergent persona across direct neural interface (DNI).

## Authority Order Matrix (SRM 4-Level Model)

1. **[LEVEL 1] SRM Campaign Exceptions**: (`SRM 6E Guidebook`, `SRM 6E Missions FAQ`) — Absolute top authority for Missions play.
2. **[LEVEL 2] Supplemental Sourcebooks**: (`Hack and Slash`, `Companion`, `Double Clutch`, `Body Shop`, `Street Wyrd`, `Firing Squad`) — Modifies and expands base rules.
3. **[LEVEL 3] Standard Core Rulebook**: (`City Edition: Hong Kong` canonical, `Seattle`, `Berlin`) — Baseline mechanics.
4. **[LEVEL 4] Unofficial House Rules / FAQs**: (GM notes, fan conversion guides) — *Requires explicit disclaimer*.

## Audit Report Format

```markdown
### Axis: SR6 Rules & Mechanics Verification Evaluation
* **SR6 Rules Score**: [Score]/10 (Threshold: 8.5)

#### Key Findings & Rules Audit
- **Edge & Action Economy**: [Pass / Violations + Citations]
- **Matrix & Rigging Mechanics**: [Pass / Violations + Citations]
- **Spellcasting & Drain Formulas**: [Pass / Violations + Citations]
- **Combat Modifiers & Defense Tests**: [Pass / Violations + Citations]

#### Required Rule Fixes & Book Citations
- [ ] **Line X**: Update weapon Attack Rating to 12/12/10/-/- reflecting installed Smartlink per [City Edition: Hong Kong, p. 247].
```
