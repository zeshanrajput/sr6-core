---
name: axis-voice-internality
description: Audits narrative drafts against the target character's local reference/voice_spec.md. Evaluates sentence structure, vocabulary, inner monologue, anti-omniscience, and perspective integrity.
---

# Voice & Internality Evaluation Skill (`axis-voice-internality`)

Use this skill to audit narrative prose for voice fidelity, internal monologue consistency, vocabulary matrix compliance, anti-omniscience discipline, and cognitive perspective integrity.

---

## 🏛️ Tier-Calibrated Voice Standards

* **Tier 1 (Keystones — e.g., Ch 01, Ch 04, Ch 06):**
  - **Passing Threshold:** $\ge 9.0 / 10$
  - **Standard:** Strict adherence to the character's core cognitive bias, profound psychological friction, era-appropriate trauma, and nuanced sensory filtering.
* **Tier 2 (Narrative Evolution — e.g., Ch 02, Ch 03, Ch 05, Ch 07, Ch 08):**
  - **Passing Threshold:** $\ge 8.5 / 10$
  - **Standard:** Allows character voice to express situational charm, dark humor, street banter, and tactical negotiations while remaining anchored to core identity.
* **Tier 3 (Atmospheric Bridges & Defiant Solace):**
  - **Passing Threshold:** $\ge 8.0 / 10$
  - **Standard:** Meditative reflection, quiet vulnerability, and unmasked stillness.

---

## 🛠️ Voice & Internality Audit Criteria

1. **Chronological Arc Awareness (`arc_chronology`):**
   - Verify the voice reflects the active developmental era in `reference/voice_spec.md` (e.g., Velvet Arc 1: cold corporate asset discovering empathy vs. Arc 2: sovereign underground authority).

2. **Anti-Omniscience Discipline (Third Person Deep Limited):**
   - The protagonist **cannot know** the private thoughts, unstated motivations, or past histories of other characters.
   - All NPC reactions must be actively interpreted through physical cues: micro-expressions, posture shifts, optical shutter clicks, vocal timbre changes, or visible astral aura flaring.

3. **Somatic Reality & Physical Taxation:**
   - Physical transformations (e.g. Cosmetic Control R2, laryngeal shifting), cyberware activations, and magic drain carry real biological consequences: resetting cartilage, aching jaws, altered breathing geometry, metallic heat, and marrow fatigue.

4. **Vocabulary & Metaphor Domains:**
   - Ensure metaphors draw organically from the character's designated domains (e.g., silk tension, theater, Shinto-Musok spirit ribbons, biological architecture, street odds) rather than generic fantasy/sci-fi clichés.

5. **Emotional Resonance & Pathos:**
   - Ensure internal thoughts avoid clinical detachment or robotic summarization. The prose should capture the human weight of corporate commodification and the preciousness of un-engineered solace.

6. **Co-Occupant Friction & Anti-Unison Rule:**
   - In shared-mind, Monad, or dual-consciousness dynamics, ban frictionless unanimity. Co-occupants must display independent cognitive boundaries, divergent sensory appetites, biological vs. digital friction, and distinct stakes before reaching consensus.

7. **Active Somatic Intercept & Physical Authority:**
   - Secondary or digital entities must be able to exercise direct physical authority in meatspace—assuming sympathetic/autonomic control and speaking aloud directly through physical vocal cords during somatic crisis—elevating them beyond passive internal commentary into sovereign co-protagonists.

8. **Mindspeech & Digital Linguistic Calibration (Null Value):**
   - In Digital Intelligence (DI), Technomancer, and Monad narratives, verify that **Mindspeech** is treated as a sovereign, living non-acoustic language rather than generic English telepathy.
   - **Metahuman vs. Digital Native Boundary**:
     - *Native Digital Kin (Sprites, DIs, Sparks)*: Communicate non-acoustically in pure Mindspeech (`*...*`).
     - *Metahuman Invaders (Deckers, Script Kiddies, Meatspace Operators in VR)*: Communicate via simulated acoustic voice audio (`"..."`).
   - **Behavioral Code-Switching & Masking**:
     - When interacting with metahumans, a DI in concealment mode deliberately switches to simulated acoustic speech (`"..."`) and slotted linguasofts to mask their origin and avoid corporate asset recovery flags.
     - When communing with resonant peers or digital kin, the DI drops the vocal simulator and communicates in native Mindspeech (`*...*`).
   - **Distinct Entity Registers**:
     - *River People / Resonant Kin*: Silt-laden currents, fluid harmonic frequencies, and collective consensus.
     - *Proto-SAPs / Emerging Sparks*: Raw, unformatted keyword queries (`*NOISE. SILENCE. REIKO.*`).
     - *Evolved DIs (Yuriko, Indomitable Will, Belle)*: Multi-layered ideograms with embedded emotional metadata tags.
     - *Monad Dual-Minds (Venn)*: Asymmetric sensory translation between messy biological memories and digital vector guidance.
   - For pure DIs (e.g. Reiko), verify that spoken human languages (Japanese, English, Cantonese) are correctly staged as **Slotted Linguasofts** emitted through drone diaphragms or simulated voice layers with tactile acoustic latency, contrasting sharply with their native instantaneous mindspeech.

---

## 📊 Audit Report Format

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

#### Required Voice Redlines & Fixes
- [ ] **Line X**: `"[Original quote]"` -> **Fix**: [Character-aligned rewrite]
```
