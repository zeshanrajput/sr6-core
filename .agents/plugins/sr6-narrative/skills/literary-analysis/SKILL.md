---
name: literary-analysis
description: Perform high-end speculative fiction analysis, 6-dimensional quality matrix scoring, tier-calibrated prose elevation, thematic centering audits, and prose chisel refactoring on narrative chapters.
---

# Literary Analysis & Revision Skills Matrix

This skill specification enables agentic LLMs to evaluate, score, and edit speculative fiction drafts up to high-end literary standards (*Clarkesworld*, *Asimov's*, *The New Yorker*) while artistically leveraging the unique strengths of the Shadowrun 6th Edition / Shadowrun Missions setting.

---

## 🏛️ Tier-Aware Calibration Framework

Prose must be evaluated according to its designated tier in `reference/voice_spec.md`. Word counts across all tiers must have ample room to breathe ($\ge 1,500$ words). What distinguishes tiers is not brevity, but artistic constraint and narrative function:

* **Tier 1 (Keystones — e.g., Ch 01, Ch 04, Ch 06):**
  - **Benchmark:** Strict *The New Yorker* / *Clarkesworld* speculative fiction standard (Passing threshold: $\ge 9.0 / 10$ or $\ge 90 / 100$).
  - **Focus:** Existential breakthroughs, profound moral tragedy, life-altering turning points, visceral somatic friction, and strict thematic discipline. Zero fluff.
  - **Scope:** 1,500 – 2,500+ words.

* **Tier 2 (Narrative Evolution — e.g., Ch 02, Ch 03, Ch 05, Ch 07, Ch 08):**
  - **Benchmark:** High-end genre fiction (*Asimov's*, *Lightspeed*) (Passing threshold: $\ge 8.5 / 10$ or $\ge 85 / 100$).
  - **Focus:** Operational tradecraft, shadowrun negotiations, relationship deepening, regional sprawl texture, dark humor, and tactical momentum. More relaxed, allowing the prose to savor lore and conversational cadence.
  - **Scope:** 1,200 – 1,800+ words.

* **Tier 3 (Atmospheric Bridges & Defiant Solace):**
  - **Benchmark:** Literary slice-of-life and contemplative speculative fiction (Passing threshold: $\ge 8.0 / 10$ or $\ge 80 / 100$).
  - **Focus:** Procedural downtime, clinic maintenance, un-monetized tea/noodle sanctuaries, meditative character breathing room. Defiantly warm moments in a cold world.
  - **Scope:** 1,000 – 1,600+ words.

---

## 🛠️ Skill 1: `stage1_thematic_centering`

**Description:** Evaluates whether a narrative chapter cleanly adheres to core thematic pillars, moral complexity, and campaign/setting canon.

### Execution Checklist
1. **The Distorted Lens of the Sixth World:** Verify that the chapter uses the dark, oppressive, and commodified machinery of Shadowrun (megacorporate IP, bio-sculpting, astral siphons, debt-traps) as a distorted lens to explore fundamental human questions (identity, parenthood, grief, authentic connection).
2. **The Contrast of Defiant Solace:** When a scene features comfort (a cup of tea, a bowl of noodles, quiet breathing), ensure that solace feels earned and precious because the surrounding world is so thoroughly commercialized and predatory.
3. **Moral Axis Audit:** Ensure the conflict avoids simple binary "good vs. evil" tropes. Check for complex trade-offs (e.g., incurring personal debt to spare a mark; choosing treason and losing everything to save an empty shell).
4. **Canon & Continuity Verification:** Check for 100% lore integrity (e.g., Magic and Resonance remain strict, non-overlapping domains; enforce network latency, background count, and line-of-sight constraints).
5. **Thematic Subtext (Trust the Reader):** Ensure themes are dramatized entirely through **tactical choices, dialogue subtext, and physical friction**. Never preach or summarize the theme in reflective voice-overs.

---

## 🛠️ Skill 2: `stage2_quality_benchmarking`

**Description:** Assesses line-level prose quality against a 1-to-10 literary scale (*Clarkesworld* / *The New Yorker* benchmark) and artistically elevates Shadowrun mechanics into visceral speculative fiction.

### Scoring Scale Benchmark
* **1–3 (Dry Rule Log / Cereal-Box Ingredients):** Sterile checklist execution, heavy exposition, passive "telling," and emotionless clinical summaries.
* **4–6 (Competent Pulp / TTRPG Recap):** Fast-moving narrative, but contains repetitive action clichés, thriller single-sentence stacking, or cognitive buffer words.
* **7–8 (Professional Genre Fiction):** Strong sensory details, distinct voice, tight pacing, artistic use of Shadowrun lore (Resonance, Fading, Magic Drain, Rigging, Adept Powers), but minor structural loops.
* **9–10 (Transcendent Speculative Fiction):** Rich prose density with generous breathing room, deep interiority, implicit subtext, cohesive braided paragraphs, and visceral sensory de-familiarization that seamlessly transforms Shadowrun mechanics into evocative literature.

---

## 🛠️ Skill 3: `stage3_6d_matrix_scoring`

**Description:** Evaluates the draft across six key literary dimensions (1–120 total score, normalized to 100%).

### 6-Dimensional Matrix (20 Points Each)
1. **Thematic Centering & The Distorted Lens (0–20):** Degree to which the story explores profound speculative fiction themes using cyberpunk/magical reality without binary morality or thematic preaching.
2. **Prose Density, Music & Sensory De-familiarization (0–20):** Economy of language, rhythm, unique metaphors from character domains, barometric/acoustic grounding, and absence of AI tropes.
3. **Paragraph Braiding & Cadence Discipline (0–20):** Mature 3–6 sentence paragraphs that weave sensory environment, physical micro-action, dialogue, and internal consequence into cohesive units. Maximum 1–2 isolated single-sentence paragraphs per chapter.
4. **Pacing, Escalation & Structural Discipline (0–20):** Strict 4-beat structure (Inciting Friction $\rightarrow$ Escalation $\rightarrow$ Climax $\rightarrow$ Aftermath), arrive-late/leave-early discipline, and generous room for scenes to breathe.
5. **Shadowrun Mechanic & Lore Integration (0–20):** Seamless translation of TTRPG mechanics into vivid fiction with zero rulebook jargon.
6. **Character Interiority, Cognitive Bias & Pathos (0–20):** Deep psychological filtration through the protagonist's specific sensory lens, genuine emotional stakes, and era-appropriate worldview.

### Output Standard
```yaml
stage3_6d_scores:
  thematic_centering: 19  # / 20
  prose_density_music: 19 # / 20
  paragraph_braiding: 19  # / 20
  pacing_structure: 19    # / 20
  mechanic_elevation: 19  # / 20
  interiority_pathos: 19  # / 20
  total_score: 95         # / 100 (Normalized)
```

---

## 🛠️ Skill 4: `apply_prose_chisel` (Refactoring Engine)

**Description:** A line-level editing transformation function that rewrites flagged text to maximize density, sensory precision, emotional resonance, and authentic Shadowrun atmosphere.

### Refactoring Rules & Execution

1. **Enforce `no-ai-slop` Bans:**
   * Enforce the 25 rules in [`sr6-core/.agents/skills/no-ai-slop/SKILL.md`](file:///c:/GitHub/sr6-core/.agents/skills/no-ai-slop/SKILL.md) (eliminate cognitive buffer verbs, olfactory templates, lore preaching, tricolon fatigue, false agency, and binary contrasts).

2. **Braid Fragmented Lines into Cohesive Paragraphs:**
   * Merge isolated 1–2 sentence lines into flowing 3–6 sentence narrative paragraphs grouping action, dialogue, and environment.

3. **Translate Dry TTRPG Math -> Techno-Poetic Shadowrun Fiction:**
   * Matrix/Resonance: *"rolled Matrix Perception"* $\rightarrow$ *"plucked the hidden chords of the underlying wire, listening for corporate traffic"*
   * Spellcasting/Drain: *"suffered 2 drain"* $\rightarrow$ *"metallic heat flared behind the larynx as cartilage locked against the mana flow"*
   * Rigging: *"jumped into drone"* $\rightarrow$ *"squeezing awareness into the cold, low-bitrate grey-scale caricature of a twin-rotor frame"*

4. **Trust the Reader (Cut Show-Then-Tell Explanatory Codas):**
   * Delete summary codas that explain the meaning of an action. Let the dramatized action carry the full weight.
