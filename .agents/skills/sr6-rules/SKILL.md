---
name: sr6-rules
description: Query official Shadowrun 6th Edition (SR6) rules, character creation costs, matrix actions, drone combat, spell mechanics, and Missions authority levels using the Gemini RAG rules vault service.
---

# Shadowrun 6e Rules & Mechanics Verification Skill (`sr6-rules`)

Use this skill to query official Shadowrun 6th Edition (SR6) rules, verify matrix/drone combat mechanics, check spell drain formulas, evaluate Edge expenditures, and ensure mechanical accuracy underpins narrative prose.

---

## Quick Execution & RAG Lookup

To query the Shadowrun 6e Gemini RAG vault non-interactively:

```powershell
python C:\github\sr6rag\query_rules.py "<YOUR_RULES_QUESTION>"
```

### Options:
- `--model <gemini-3.7-flash|gemini-flash-lite-latest>` : Select Gemini model (default: `gemini-3.7-flash`).
- `--thinking <high|low>` : Select reasoning depth (default: `high`).
- `--fallback-only` : Force local SQLite database search (`shadowrun_rules.db`) without using the Gemini API.

---

## Authority Order Matrix (SRM 4-Level Model)

1. **[LEVEL 1] SRM Campaign Exceptions**: (`SRM 6E Guidebook`, `SRM 6E Missions FAQ`) - Absolute top authority.
2. **[LEVEL 2] Supplemental Sourcebooks**: (`Hack and Slash`, `Companion`, `Double Clutch`, etc.) - Modifies and expands base rules.
3. **[LEVEL 3] Standard Core Rulebook**: (`SR6 Core Rulebook`) - Baseline mechanics.
4. **[LEVEL 4] Unofficial House Rules / FAQs**: (GM notes, fan conversion guides) - *Requires explicit disclaimer*.

---

## Sub-Agent Audit Workflow & Rules Verification

When auditing narrative drafts for SR6 rules accuracy:
1. **Identify Mechanics in Prose**: Check Edge gains/expenditures, Matrix actions (Format Device, Spoof Command, Hack Into Host), spell drain, recoil, defense tests, and vehicle/drone rigging tests.
2. **RAG Lookup**: Run `query_rules.py` for any ambiguous or high-stakes mechanical interaction.
3. **Verification**: Confirm that prose actions follow valid SR6 rules constraints (e.g., Major vs Minor actions, Edge action costs, spell drain minimums).

---

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
- [ ] **Line X**: Update Matrix action description to require a Major Action per [Hack and Slash, p. 38].
```
