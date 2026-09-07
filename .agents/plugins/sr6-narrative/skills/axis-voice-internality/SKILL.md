---
name: axis-voice-internality
description: Audit drafts for character voice, POV, and deep internality.
version: 1.0.0
author: Zeshan Rajput (zeshanrajput), Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [shadowrun, sr6, narrative, voice, internality, persona]
    related_skills: [axis-agency-motivation, no-ai-slop, narrative-director]
---

# Voice & Internality Evaluation Skill (`axis-voice-internality`)

Use this skill to audit narrative prose for voice fidelity, internal monologue consistency, vocabulary matrix compliance, anti-omniscience discipline, and cognitive perspective integrity against the character's local `reference/voice_spec.md`.

## When to Use

- Auditing narrative chapters during Stage 3 of the narrative pipeline.
- Checking that POV remains strictly Third-Person Deep Limited without omniscient perspective leaks.
- Verifying non-acoustic digital communication (mindspeech), Monad dual-consciousness, and somatic cyberware/drain reactions.

## How to Run

Execute the unified evaluator via the `terminal` tool:

```bash
uv run sr6 evaluate "characters/<char_id>/chapters/<file>.qmd" --tier <1|2|3> --char <char_id>
```

## Tier-Calibrated Voice Standards

- **Tier 1 (Keystones — Passing Threshold: $\ge 9.0 / 10$):**
  - Strict adherence to the character's core cognitive bias, profound psychological friction, era-appropriate trauma, and nuanced sensory filtering.
- **Tier 2 (Narrative Evolution — Passing Threshold: $\ge 8.5 / 10$):**
  - Allows character voice to express situational charm, dark humor, street banter, and tactical negotiations while remaining firmly anchored to core identity.
- **Tier 3 (Atmospheric Bridges — Passing Threshold: $\ge 8.0 / 10$):**
  - Meditative reflection, quiet vulnerability, and unmasked stillness.

## Voice & Internality Audit Criteria

1. **Chronological Arc Awareness (`arc_chronology`):**
   - Verify the voice reflects the active developmental era in `reference/voice_spec.md` (e.g. Reiko Arc 1 debt-collar vs. Arc 4 apex technoshamanic serene authority; Velvet Arc 1 cold asset vs. Arc 2 sovereign underground power).
2. **Anti-Omniscience Discipline (Third Person Deep Limited):**
   - The protagonist **cannot know** the private thoughts, unstated motivations, or interior feelings of other characters.
   - All NPC reactions must be actively interpreted through physical cues: micro-expressions, posture shifts, optical shutter clicks, vocal timbre changes, or visible astral aura flaring.
3. **Somatic Reality & Physical Taxation:**
   - Physical transformations (e.g. Cosmetic Control R2, laryngeal shifting), cyberware activations, and magic drain carry biological consequences: resetting cartilage, aching jaws, altered breathing geometry, metallic heat, and marrow fatigue.
4. **Vocabulary & Metaphor Domains:**
   - Metaphors must draw organically from the character's designated domains (e.g. silk tension, theater, Shinto-Musok spirit ribbons, biological architecture, street odds) rather than generic fantasy/sci-fi clichés.
5. **Emotional Resonance & Pathos:**
   - Interior thoughts must avoid clinical detachment or robotic summarization. The prose should capture the human weight of corporate commodification and the preciousness of un-engineered solace.
6. **Co-Occupant Friction & Anti-Unison Rule:**
   - In shared-mind, Monad, or dual-consciousness dynamics, ban frictionless unanimity. Co-occupants must display independent cognitive boundaries, divergent sensory appetites, biological vs. digital friction, and distinct stakes before reaching consensus.
7. **Active Somatic Intercept & Physical Authority:**
   - Secondary or digital entities must be able to exercise direct physical authority in meatspace—assuming sympathetic/autonomic control and speaking aloud directly through physical vocal cords during somatic crisis—elevating them beyond passive internal commentary.
8. **Mindspeech & Digital Linguistic Calibration (*Null Value* Lore):**
   - In Digital Intelligence (DI), Technomancer, and Monad narratives, verify that **Mindspeech** is treated as a sovereign, non-acoustic ideational language.
   - **Metahuman vs. Digital Native Boundary**:
     - *Native Digital Kin (Sprites, DIs, Sparks)*: Communicate non-acoustically in pure Mindspeech formatted in italics without quotes (`*...*`).
     - *Metahuman Invaders (Deckers, Script Kiddies, Meatspace Operators in VR)*: Communicate via simulated acoustic voice audio (`"..."`).
   - **Behavioral Code-Switching & Masking**:
     - When interacting with metahumans, a DI in concealment mode deliberately switches to simulated acoustic speech (`"..."`) and slotted linguasofts to mask origin and avoid corporate asset flags.
     - When communing with resonant peers or digital kin, the DI drops the vocal simulator and communicates in native Mindspeech (`*...*`).
   - Pure DIs (e.g. Reiko) stage spoken human languages as **slotted linguasofts** emitted through drone diaphragms or simulated voice layers with tactile acoustic latency.

## Audit Report Format

```markdown
### Axis: Voice & Internality Evaluation
* **Target Character**: [Character ID / Name]
* **Target Tier**: [Tier 1 / Tier 2 / Tier 3]
* **Voice Fidelity Score**: [Score]/10 (Threshold: 9.0 Tier 1 / 8.5 Tier 2 / 8.0 Tier 3)

#### Key Findings & Voice Compliance
- **Perspective & Anti-Omniscience**: [Pass / Fail + Analysis]
- **Somatic & Sensory Grounding**: [Pass / Fail + Analysis]
- **Vocabulary & Metaphor Alignment**: [Pass / Fail + Analysis]
- **Emotional Pathos & Interiority**: [Pass / Fail + Analysis]
- **Mindspeech & Arc Chronology**: [Pass / Fail + Analysis]

#### Required Voice Redlines & Fixes
- [ ] **Line X**: `"[Original quote]"` -> **Fix**: [Character-aligned rewrite]
```
