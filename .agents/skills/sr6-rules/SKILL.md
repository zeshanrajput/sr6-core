---
name: sr6-rules
description: Query official Shadowrun 6th Edition (SR6) rules, character creation costs, matrix actions, drone combat, spell mechanics, and Missions authority levels using the Gemini RAG rules vault service.
---

# Shadowrun 6e Rules & RAG Reference Skill

Use this skill whenever you need to check official Shadowrun 6th Edition (SR6) rules, calculate Karma or Nuyen advancement costs, verify matrix or rigging mechanics, look up spell/drone stats, or resolve rules priority according to official Shadowrun Missions (SRM) guidelines.

## Quick Execution

To query the Shadowrun 6e Gemini RAG vault non-interactively, run the `query_rules.py` script via shell:

```powershell
python C:\github\sr6rag\query_rules.py "<YOUR_RULES_QUESTION>"
```

### Options:
- `--model <gemini-flash-latest|gemini-flash-lite-latest>` : Select Gemini model (default: `gemini-flash-latest`).
- `--thinking <high|low>` : Select reasoning depth (default: `high`).
- `--fallback-only` : Force local SQLite database search (`shadowrun_rules.db`) without using the Gemini API.

## Authority Order Matrix (SRM 4-Level Model)

When evaluating retrieved rules or resolving conflicting texts:
1. **[LEVEL 1] SRM Campaign Exceptions**: (`SRM 6E Guidebook`, `SRM 6E Missions FAQ`) - Absolute top authority for campaign play.
2. **[LEVEL 2] Supplemental Sourcebooks**: (`Hack and Slash`, `Companion`, `Double Clutch`, etc.) - Modifies and expands base rules.
3. **[LEVEL 3] Standard Core Rulebook**: (`SR6 Core Rulebook`) - Baseline mechanics.
4. **[LEVEL 4] Unofficial House Rules / FAQs**: (GM notes, fan conversion guides) - *Requires explicit disclaimer if referenced*.

## Output Format & Citation Requirements

When presenting rule answers to the user:
- Cite exact source and physical page numbers in format: `[Book Name, Page Number]`.
- Note any Level 1 SRM overrides that modify standard core rules.
