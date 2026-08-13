---
name: axis-voice-internality
description: Audits narrative drafts against the target character's local reference/voice_spec.md (falling back to default_voice_spec.md). Evaluates sentence structure, vocabulary, inner monologue, and perspective integrity.
---

# Voice & Internality Evaluation Skill (`axis-voice-internality`)

Use this skill to audit narrative prose for voice fidelity, internal monologue consistency, vocabulary matrix compliance, and cognitive perspective integrity.

---

## Evaluation Workflow

1. **Voice Spec Ingestion**:
   - Locate and read the target character's local `reference/voice_spec.md` (e.g., `sr6yuriko/reference/voice_spec.md`, `sr6velvet/reference/voice_spec.md`).
   - If not found, fall back to [`sr6-core/reference/default_voice_spec.md`](file:///c:/GitHub/sr6-core/reference/default_voice_spec.md).

2. **Prose Audit & Verification**:
   - **Chronological Growth Arc & Tier Calibration**:
     - Check the character's `arc_chronology` in `reference/voice_spec.md` to identify the active developmental era. Evaluate cognitive biases and expressivity against that era baseline to prevent retrospective flattening.
     - Check `chapter_tiers` to identify whether the target chapter is Tier 1 (Keystone: 9.0+ passing threshold), Tier 2 (Narrative Evolution: 8.5+ threshold), or Tier 3 (Atmospheric Bridge: 8.0+ threshold).

   - **POV & Cognitive Bias**: Verify that the story is strictly filtered through the protagonist's specific cognitive bias (e.g., Yuriko's tactical telemetry vs. Velvet's social/aura perception). Check for accidental omniscient leaks.
   - **Vocabulary & Metaphor Domains**: Verify that metaphors draw from the character's designated domains (e.g., compiler routines vs. Shinto spirit ribbons). Flag any out-of-character jargon or generic buzzwords.
   - **Internal Monologue & Cadence**: Check sentence rhythm, paragraph flow, and internal realization style against the voice schema. Ensure internal thoughts feel organic and unforced.
   - **Sensory Lens**: Confirm that sensory descriptions prioritize the character's primary sensory lens (e.g., AR LIDAR arrays, aura color shifts, thermal signatures).

3. **Scoring & Redline Output**:
   - **Voice Fidelity Score**: Rate from **1 to 10** (Pass threshold: **8.0+**).
   - **Redline List**: Highlight exact line numbers or quotes that break character voice, with required rewrites.

---

## Audit Report Format

```markdown
### Axis: Voice & Internality Evaluation
* **Target Character**: [Character ID / Name]
* **Voice Spec Referenced**: [Path to voice_spec.md]
* **Voice Fidelity Score**: [Score]/10 (Threshold: 8.0)

#### Key Findings & Voice Compliance
- **Perspective & Cognitive Bias**: [Pass / Fail + Analysis]
- **Vocabulary & Metaphor Alignment**: [Pass / Fail + Analysis]
- **Internal Monologue Cadence**: [Pass / Fail + Analysis]
- **Sensory Lens Integrity**: [Pass / Fail + Analysis]

#### Required Voice Redlines & Fixes
- [ ] **Line X**: `"[Original quote]"` -> **Fix**: [Character-aligned rewrite]
```
