---
name: axis-agency-motivation
description: Verifies that the main character makes proactive, consequential choices that drive the plot forward rather than passively reacting to events.
---

# Character Agency & Motivation Evaluation Skill (`axis-agency-motivation`)

Use this skill to audit narrative drafts for protagonist agency, active goal-seeking behavior, consequential decision-making, and motivation alignment.

---

## Evaluation Workflow

1. **Protagonist Agency Audit Criteria**:
   - **Active Driver vs Passive Passenger**: Does the protagonist make deliberate, tactical decisions that shape scene events? Or are they simply dragged along by NPCs, explosions, or external scripting?
   - **Consequential Choices**: Do decisions carry real stakes and permanent consequences (e.g., spending Edge, burning nuyen, taking physical/astral damage, altering contact trust, risking compromised SINs)?
   - **Motivation Consistency & Era Alignment**: Are the protagonist's actions aligned with their active narrative arc in `reference/voice_spec.md` (e.g., solitary survival -> peer alliances -> collective stewardship -> apex adversaries) and their core drives/qualities in `character_master.yaml`?
   - **Absence of Deus Ex Machina**: Does the protagonist resolve their own tactical dilemmas through skill and resourcefulness rather than convenient external miracles or unearned luck?

2. **Scoring & Redline Output**:
   - **Agency & Motivation Score**: Rate from **1 to 10** (Pass threshold: **8.0+**).
   - **Redline List**: Identify passive scenes or weak choices requiring protagonist assertion.

---

## Audit Report Format

```markdown
### Axis: Agency & Motivation Evaluation
* **Agency & Motivation Score**: [Score]/10 (Threshold: 8.0)

#### Key Findings & Agency Analysis
- **Proactive Decision-Making**: [Pass / Fail + Analysis]
- **Stakes & Consequential Impact**: [Pass / Fail + Analysis]
- **Motivation Alignment**: [Pass / Fail + Analysis]
- **Self-Directed Problem Solving**: [Pass / Fail + Analysis]

#### Required Agency Revisions
- [ ] **Scene Beat X**: Shift protagonist from passive observer to active initiator of the break-in sequence.
```
