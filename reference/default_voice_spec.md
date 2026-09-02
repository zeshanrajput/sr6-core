# Default Character Voice Specification & Schema Template

This document defines the base structural schema for character voices across the Shadowrun 6e portfolio framework. Character repositories (e.g., `sr6yuriko/reference/voice_spec.md`, `sr6velvet/reference/voice_spec.md`) extend this base specification to define character-specific voice fidelity rules.

---

## 1. Voice Specification Schema

Every character voice specification MUST define the following core dimensions:

```yaml
voice_schema:
  character_id: string          # e.g., "yuriko", "velvet", "union"
  narrative_pov: string         # e.g., "First Person Limited", "Third Person Deep Limited"
  cognitive_bias: string        # Primary lens through which character interprets events
  vocabulary_matrix:
    register: string            # Formal, Street, Tactical, Corporate, Metaphysical
    jargon_density: string      # Low, Medium, High
    forbidden_tropes: list      # Character-specific banned phrases or framing
    metaphor_domains: list      # Specific fields drawn from for analogies (e.g., code, aura, firearms)
  sensory_lens:
    primary_sense: string       # Visual/AR, Auditory, Thermal, Resonance, Astral Aura
    secondary_sense: string     # Tactile, Olfactory, Electromagnetic
    blind_spots: string         # What the character consistently misses or ignores
  emotional_baseline:
    default_affect: string      # Controlled, Volatile, Cynical, Playful, Clinical
    stress_triggers: list       # Events that break emotional control
    defense_mechanisms: list    # Coping behaviors under fire (e.g., gallows humor, cold calculation)
  syntax_cadence:
    sentence_length: string     # Short & clipped, Long & rhythmic, Varied tactical
    paragraph_flow: string      # Dense analysis, Rapid staccato beats, Stream-of-consciousness
    internal_monologue: string  # Format of inner thoughts (e.g., italicized telemetries, spoken subtext)

# Multi-era narrative growth arcs (prevents retrospective flattening across campaign progression)
arc_chronology:
  arc_1:
    chapters: string            # e.g., "01 – 09"
    narrative_state: string     # Primary campaign context / stakes
    expressivity: string        # Physical/vocal masks vs. authentic expression
    cognitive_bias: string      # Perspective limitations, trauma, or active biases
    visual_palette: string      # Color themes, sensory contrast
    mechanical_state: string    # Chargen baseline, initiation/submersion grade, gear loadout
  # arc_2, arc_3, ...

# Structural chapter tiers and benchmark score expectations
chapter_tiers:
  tier_1_keystones:
    passing_threshold: "9.0 / 10"
    role: "Existential breakthroughs, initiation/submersion milestones, major turning points"
    chapters: list
  tier_2_narrative_evolution:
    passing_threshold: "8.5 / 10"
    role: "Mission runs, relationship deepening, regional texture, evolutionary steps"
    chapters: list
  tier_3_atmospheric_bridges:
    passing_threshold: "8.0 / 10"
    role: "Slice-of-life downtime, procedural mechanics, affectionately grounded banter"
    chapters: list

# Domain-specific vocabulary rules evaluated during multi-agent audits
domain_vocabulary_rules:
  domain_1_core_perception:
    context: string             # Internal monologue, sensory perception
    rule: string
    approved_terms: list
    banned_cliches: list
  domain_2_mechanical_action:
    context: string             # Combat, rigging, decking, spellcraft
    rule: string
    approved_terms: list
  domain_3_dialogue:
    context: string             # Direct communication, street/corporate dialects
    rule: string
    approved_terms: list
```

---

## 2. Default Voice Baseline Rules

Unless overridden by a character-specific `voice_spec.md`, the following baseline rules apply:

### 2.1 Perspective & Point of View (POV)

* **Default**: Third Person Deep Limited. The narrative stays strictly inside the protagonist's skull. No omniscience. If the protagonist cannot perceive a threat, the reader does not know about it.

### 2.2 Sensory Processing

* **Default**: Physical-first sensory priority (visual, auditory, tactile). Environmental details should emphasize gritty urban reality—rain, cold neon reflections, mechanical vibration, synthetic food odors.

### 2.3 Internal Monologue Style

* **Default**: Seamless integration of internal thoughts into prose flow without intrusive tags like "she thought to herself". Use italics sparingly for acute internal realization.

### 2.4 Stress & Injury Response

* **Default**: Stress causes narrowing of focus (tunneling) and heightened reliance on primary skills. Injury induces physical friction, pain penalty reflection, and tactical reassessment.

### 2.5 Audio Narration & TTS Fluency Discipline

* **Default**: Maintain an ellipses density ceiling of $\le 0.6$ per 300 words. Stitch fragmented sentences and avoid trailing hesitations that degrade spoken TTS delivery.

### 2.6 Mindspeech & Communication Medium Separation

* **Print Convention (`.md` / `.qmd`)**:
  * Pure non-acoustic mindspeech / DNI transmissions / resonant ideation: formatted in italics without quotes (`*...*`).
  * Acoustic speech / simulated metahuman voice synthesis / drone speaker audio: formatted in double quotation marks (`"..."`).
* **Entity Distinction & Tactical Code-Switching**:
  * *Native Digital Intelligences & Sparks*: Communicate non-acoustically in native Mindspeech (`*...*`).
  * *Metahuman Invaders in VR / Sprawl Meatspace*: Communicate in acoustic or serialized speech (`"..."`).
  * *DI Concealment*: When a digital intelligence interacts with metahumans, they deliberately code-switch to simulated acoustic speech (`"..."`) and slotted human linguasofts to mask their true nature and avoid corporate asset recovery flags.
* **Audio TTS Integration**: `sr6core.narration` dynamically converts `*...*` mindspeech into spoken quotes `"..."` during TTS preprocessing for seamless audio delivery.

---

## 3. Extension & Override Guidelines for Character Repositories

When creating or editing `reference/voice_spec.md` in individual character repos:

1. **Inheritance**: Include an explicit header referencing this default template:

   ```markdown
   Extends: sr6-core/reference/default_voice_spec.md
   ```

2. **Override Rules**:
   * Any section explicitly defined in the local `voice_spec.md` **completely replaces** the default baseline rule for that section.
   * Any unmentioned section automatically inherits the defaults from `default_voice_spec.md`.
3. **Character-Specific Metaphor Domains**: Define at least 3 unique metaphor domains (e.g., Yuriko: *Matrix architecture, compiler routines, tactile animism*; Velvet: *Shinto-Musok spirit ribbons, street negotiation, high-fashion silk tension*).
4. **Forbidden Slop & Anti-Voice Patterns**: List words, idioms, or phrasing styles that break character immersion.
