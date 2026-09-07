---
name: axis-agency-motivation
description: Audit narrative drafts for protagonist agency and choice.
version: 1.0.0
author: Zeshan Rajput (zeshanrajput), Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [shadowrun, sr6, narrative, agency, evaluation]
    related_skills: [axis-voice-internality, axis-pacing-structure, narrative-director]
---

# Character Agency & Motivation Evaluation Skill (`axis-agency-motivation`)

Use this skill to audit narrative drafts for protagonist agency, active goal-seeking behavior, consequential decision-making, and motivation alignment within the Shadowrun 6e Narrative Suite.

## When to Use

- Evaluating chapter drafts or scene beats during Stage 3 of the narrative pipeline.
- Auditing scenes where the protagonist appears reactive, dragged by plot events, or reduced to a passive observer.
- Verifying dual-protagonist or bonded-partner parity to prevent one character from becoming a mere foil.

## How to Run

Execute the unified evaluator via the `terminal` tool:

```bash
uv run sr6 evaluate "characters/<char_id>/chapters/<file>.qmd" --tier <1|2|3> --char <char_id>
```

## Tier-Calibrated Agency Standards

- **Tier 1 (Keystones — Passing Threshold: $\ge 9.0 / 10$):**
  - Existential, irreversible choices that fundamentally alter the protagonist's life, identity, or safety.
  - Protagonist boldly breaks from corporate conditioning, accepts terrifying personal risk, or makes a costly moral sacrifice.
- **Tier 2 (Narrative Evolution — Passing Threshold: $\ge 8.5 / 10$):**
  - Tactical sovereignty. Agency expressed through negotiation leverage, setting run terms, managing physical recovery, and intentionally crafting un-monetized sanctuaries.
- **Tier 3 (Atmospheric Bridges — Passing Threshold: $\ge 8.0 / 10$):**
  - Quiet autonomy. Agency expressed through choosing stillness, refusing extractive presence, and choosing genuine human connection over corporate transactions.

## Audit Criteria

1. **Active Driver vs. Passive Passenger:**
   - Does the protagonist make deliberate, tactical, or moral decisions that dictate the outcome of the scene?
   - Eliminate phrases signaling passive victim framing (*"had no choice but," "helplessly watched," "dragged along by fate"*).
2. **Dramatizing Somatic Stakes (The Stakes Caliper):**
   - Decisions must carry tangible physical, emotional, and systemic weight.
   - **Ban Perfunctory Stakes:** Never reduce a life-altering choice to a passing sentence or spreadsheet calculation. The friction and danger must be actively felt on-page.
3. **Absence of Deus Ex Machina:**
   - Tactical dilemmas and emotional impasses must be resolved through the protagonist's own skills, Adept disciplines, or psychological leverage rather than lucky coincidences.
4. **Co-Protagonist Parity & Anti-Foil Safeguard:**
   - In dual-protagonist or bonded-partner narratives, when one partner takes the lead or gains emotional gravitas, actively protect the other partner's competence, agency, and somatic stakes.
   - Never reduce the organic anchor or secondary partner to a passive foil, helpless victim, or mere sounding board.

## Audit Report Format

```markdown
### Axis: Agency & Motivation Evaluation
* **Target Tier**: [Tier 1 / Tier 2 / Tier 3]
* **Agency & Motivation Score**: [Score]/10 (Threshold: 9.0 Tier 1 / 8.5 Tier 2 / 8.0 Tier 3)

#### Key Findings & Agency Analysis
- **Proactive Decision-Making**: [Pass / Fail + Analysis]
- **Stakes & Consequential Impact**: [Pass / Fail + Analysis]
- **Motivation Alignment**: [Pass / Fail + Analysis]
- **Self-Directed Resolution**: [Pass / Fail + Analysis]

#### Required Agency Revisions
- [ ] **Scene Beat X**: Shift protagonist from passive observer to active initiator.
```
