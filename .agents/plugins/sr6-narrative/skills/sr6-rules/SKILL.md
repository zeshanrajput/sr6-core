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

Execute local rules queries via the `terminal` tool from the workspace root:

```bash
# Display universal item reference card (weapons, qualities, spells, cyberware, drones)
uv run sr6 card "<item_name>"

# Search local 20,082-chunk FTS5 rules vault (--compact for agent mode)
uv run sr6 rag search "<topic_or_keyword>" --compact

# Retrieve exact rule chunk from SQLite in <5ms without LLM overhead
uv run sr6 rag get "<rule_id_or_topic>" --compact

# General CommLink6 reference database search
uv run sr6 search "<item_name>"

# AI-assisted rules synthesis for complex multi-condition edge cases
uv run sr6 rag query "<rules_question>" --compact
```

## Mandatory Pre-Computation & Verification Protocols

1. **Rule of Zero Memory Guessing**:
   - Never guess Essence costs, Nuyen prices, Availability ratings, or Karma costs.
   - Always run `uv run sr6 card "<item>"` or `uv run sr6 rag get "<rule>"` before proposing mechanical moves, purchases, or ledger adjustments.
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
