---
name: axis-pacing-structure
description: Evaluates scene structure, entry/exit points, tension build-up, climax delivery, and action-to-exposition ratios based on reference/narrative_standards.md.
---

# Pacing & Scene Structure Evaluation Skill (`axis-pacing-structure`)

Use this skill to audit narrative drafts for structural integrity, scene entry/exit discipline, tension progression curves, climax delivery, and action-to-exposition ratio compliance.

---

## Evaluation Workflow

1. **Standards Ingestion**:
   - Read [`sr6-core/reference/narrative_standards.md`](file:///c:/GitHub/sr6-core/reference/narrative_standards.md).

2. **Structural Audit Criteria**:
   - **Arrive Late & Leave Early**: Check scene entry point. Does it skip mundane setup and start immediately at the friction point? Check scene exit point. Does it cut cleanly after the climax/turn without anti-climactic recaps?
   - **4-Beat Arc Evaluation**:
     1. *Inciting Friction (0-20%)*: Is immediate obstacle established without throat-clearing?
     2. *Rising Tension & Escalation (20-60%)*: Do complications stack logically? Does the plan fail or adapt under pressure?
     3. *Climax & Decision (60-85%)*: Is there a pivotal, high-stakes tactical or emotional choice?
     4. *Resonance & Aftermath (85-100%)*: Is the fallout concrete and immediate?
   - **Action-to-Exposition Ratio**: Verify 80/20 balance (80% active sensory prose/dialogue/tactical action; <=20% background context/exposition).
   - **Cadence & Sentence Rhythm**: Ensure fast-paced action scenes use terse, high-momentum sentences while tension-building moments expand rhythmically.

3. **Scoring & Redline Output**:
   - **Pacing & Structure Score**: Rate from **1 to 10** (Pass threshold: **8.0+**).
   - **Structural Recommendations**: Identify sluggish passages, bloated entries/exits, or exposition dumps requiring trimming or restructuring.

---

## Audit Report Format

```markdown
### Axis: Pacing & Structure Evaluation
* **Standards Referenced**: reference/narrative_standards.md
* **Pacing & Structure Score**: [Score]/10 (Threshold: 8.0)

#### Key Findings & Structural Breakdown
- **Scene Entry / Exit Discipline**: [Pass / Fail + Analysis]
- **4-Beat Progression (Inciting -> Escalation -> Climax -> Aftermath)**: [Pass / Fail + Analysis]
- **Action-to-Exposition Ratio**: [Current Ratio % / 80-20 Standard Compliance]
- **Cadence & Rhythm**: [Pass / Fail + Analysis]

#### Required Structural Cuts & Adjustments
- [ ] **Section / Lines X-Y**: Trim exposition dump; convert into active sensory observation during combat.
- [ ] **Scene Exit**: Cut final paragraph (lines A-B); end scene cleanly at concrete aftermath line.
```
