---
name: literary-analysis
description: Perform high-end speculative fiction analysis, 1-100 5-dimensional quality matrix scoring, Shadowrun lore & mechanics elevation, thematic centering audits, and prose chisel refactoring on narrative chapters.
---

# Literary Analysis & Revision Skills Matrix

This skill specification enables agentic LLMs to evaluate, score, and edit speculative fiction drafts up to high-end literary standards (*Clarkesworld*, *Asimov's*, *The New Yorker*) while artistically leveraging the unique strengths of the Shadowrun 6th Edition / Shadowrun Missions setting.

---

## 🛠️ Skill 1: `stage1_thematic_centering`

**Description:** Evaluates whether a narrative chapter cleanly adheres to core thematic pillars, moral complexity, and campaign/setting canon.

### Inputs
* `draft_text`: The prose manuscript under review.
* `character_dossier`: Core identity, origin, and overarching goals of the protagonist.
* `setting_lore`: Rules and world boundaries (e.g., Shadowrun 6th Edition / SRM constraints).

### Execution Checklist
1. **Identify the Core Conflict:** Verify if the scene centers on the friction between digital-native/emergent AI consciousness and rigid corporate/physical systems.
2. **Moral Axis Audit:** Ensure the conflict avoids simple binary "good vs. evil" tropes. Check for tragic or complex moral choices (e.g., the *Architect of Chains* paradox: saving/stabilizing a wild spirit requires domesticating its wildness).
3. **Canon & Continuity Verification:** Check for 100% lore integrity (e.g., in Shadowrun, ensure Magic and Resonance remain strict, non-overlapping domains; enforce network latency, line-of-sight constraints, and SRM campaign rules).
4. **The Spaces Between Audit:** Ensure the narrative goes beyond numbers and mechanics to explore the spiritual dimension of technology—using Yuriko's digital-native perspective to examine human condition issues (belonging, identity, debt, guardianship, grief, connection) with fresh, tangible, emotionally accessible intimacy.

### Output Standard
```yaml
stage1_analysis:
  thematic_alignment: "PASS | FAIL"
  primary_moral_conflict: "Summary of complex moral tension"
  lore_violations: ["List of canon errors, if any"]
  actionable_recommendations: ["Specific plot/lore fixes"]
```

---

## 🛠️ Skill 2: `stage2_quality_benchmarking`

**Description:** Assesses line-level prose quality against a 1-to-10 literary scale (*Clarkesworld* / *The New Yorker* benchmark) and artistically elevates Shadowrun mechanics into visceral speculative fiction.

### Scoring Scale Benchmark
* **1–3 (High School Fanfiction / Dry Math Log):** Heavy reliance on explicit game math (dice pools, condition monitor boxes), generic sci-fi tropes, heavy exposition, and passive "telling."
* **4–6 (Competent Pulp / TTRPG Recap):** Narrative moves briskly, but treats game elements as dry recap and contains repetitive "glitch" verbs (*shuddered*, *flared*, *jittered*) or cognitive buffer words (*realized*, *felt*, *decided*).
* **7–8 (Professional Genre Fiction):** Strong sensory details, distinct voice, tight pacing, artistic use of Shadowrun lore (Resonance, Fading, Rigging), but contains minor structural loops or overly technical infodumps.
* **9–10 (Transcendent Speculative Fiction):** High prose density, zero filler words, deep interiority, implicit subtext, and visceral sensory de-familiarization that seamlessly transforms Shadowrun mechanics into evocative literature.

### Execution Checklist
1. **Elevate Mechanics into Fiction:** Identify dry rulebook math (e.g. "rolled 12 dice on Matrix Perception", "took 3 boxes of Fading") and translate them into in-world physical, digital, and spiritual reality (*Matrix Perception -> wire-plucking sensory sweep; Fading -> spiritual fever scorching internal pathways*).
2. **Harness Shadowrun Strengths:** Do **not** purge authentic Shadowrun concepts (Resonance, Fading, Cyberdecking, Sprite Powers, Rigger Networks, Megacorp Intrigue). Use them as the story's narrative engine and thematic bedrock.
3. **Identify Redline Loops:** Check if the protagonist repeatedly "redlines processing -> experiences brief epiphany -> auto-stabilizes." Flag for permanent systemic or narrative consequences.

### Output Standard
```yaml
stage2_analysis:
  literary_score: 8.5 # Scale 1.0 - 10.0
  shadowrun_mechanics_elevated: ["List of TTRPG concepts translated into rich fiction"]
  prose_redundancies: ["List of filler phrases or weak verbs"]
```

---

## 🛠️ Skill 3: `five_dimensional_scoring_matrix`

**Description:** Performs a quantitative 1–100 analysis across five structural narrative dimensions.

### Dimensions & Metrics

| Dimension | Target Score | What to Evaluate |
| --- | --- | --- |
| **1. Concept & World-Building** | 90–100 | Is the Shadowrun universe—the Matrix as an animistic ecosystem ("The Holy Wild"), megacorps as brutalist cathedrals, Resonance vs. Magic—artistically integrated and mythologized rather than treated as generic sci-fi? |
| **2. Prose & Style** | 90–100 | Is there high line-level density? Are computer science and game mechanics translated into tactile, animistic equivalents (*deletion = asphyxiation; Fading = spiritual fever; encryption = iron veils*)? |
| **3. Characterization & Foils** | 90–100 | Does the AI exhibit non-human interiority and explore the spiritual side of technology? Does the narrative use the AI/emergent perspective to view human condition issues (belonging, identity, debt, guardianship, grief, connection) with fresh, emotionally accessible intimacy? Are human companions active agents of friction rather than props? |

| **4. Narrative Structure & Pacing** | 90–100 | Does the scene enforce real network latency, global signal attenuation, and irreversible consequences? Is pacing kinetic without being frantic? |
| **5. Meatspace / Matrix Friction** | 90–100 | Is physical existence depicted as sensory starvation or a heavy "iron cage"? Is there a sharp contrast between digital fluency and physical drone/rigging limitation? |

### Output Standard
```yaml
matrix_score:
  concept_worldbuilding: 95
  prose_style: 90
  characterization_foils: 88
  structure_pacing: 92
  meatspace_matrix_friction: 94
  overall_composite: 91.8
```

---

## 🛠️ Skill 4: `apply_prose_chisel` (Refactoring Engine)

**Description:** A line-level editing transformation function that rewrites flagged text to maximize density, sensory precision, AI interiority, and authentic Shadowrun atmosphere.

### Refactoring Rules & Substitution Patterns

1. **Eliminate Cognitive Buffer Verbs:**
   * `"Reiko realized that"` -> `""` [Show direct system output or state shift]
   * `"She felt the"` -> `""` [Replace with haptic/sensory feedback]

2. **Replace Generic Sci-Fi Verbs:**
   * `"flared" / "shuddered" / "jittered"` -> `"strobbed" / "dilated" / "stuttered" / "dereferenced"`

3. **Translate Dry TTRPG Math -> Techno-Poetic Shadowrun Fiction:**
   * `"rolled Matrix Perception"` -> `"plucked the hidden chords of the underlying wire, listening for corporate traffic"`
   * `"took 3 boxes of Fading damage"` -> `"pathways scorched with a solar golden fever as the Resonance claimed its toll"`
   * `"entered the Nissan Samurai drone"` -> `"squeezing her vast indigo light into the cold, low-bitrate grey-scale caricature of a two-legged warform"`

### Transformation Example

* ❌ **Dry TTRPG Draft:** *Reiko took 3 boxes of Fading while using Matrix Perception to find the enemy decker, realizing her host was under attack.*
* ⚡ **Chiseled Output:** *A solar golden fever scorched Reiko’s pathways as the Resonance claimed its toll. She plucked the hidden chords of the wire, sensing the enemy decker’s Spines—a field of barbed-glass logic—encroaching on her local directory.*

---

## 🔄 Integrated Workflow Pipeline (`review_and_refactor_chapter`)

When reviewing or generating a full narrative chapter, execute the following sub-skills sequentially:

```mermaid
graph TD
    A[Input Draft Manuscript] --> B[Skill 1: Stage 1 Thematic Centering]
    B --> C[Skill 2: Stage 2 Quality Benchmarking]
    C --> D[Skill 3: Five-Dimensional Matrix Scoring]
    D --> E[Skill 4: Apply Prose Chisel Refactoring]
    E --> F[Final Refactored Manuscript & Scorecard]
```

1. **Step 1:** Call `stage1_thematic_centering` to audit plot integrity, moral complexity, and SRM lore.
2. **Step 2:** Call `stage2_quality_benchmarking` to score against the 1–10 scale and artistically elevate Shadowrun mechanics.
3. **Step 3:** Call `five_dimensional_scoring_matrix` to generate quantitative metrics.
4. **Step 4:** Execute `apply_prose_chisel` on low-scoring sentences to deliver a publication-ready revision.
5. **Step 5 (Walkthrough Metrics Capture):** Record all resulting performance metrics, sub-skill evaluations, and 5-dimensional matrix scores directly in the run's `walkthrough.md` artifact (`<appDataDir>/brain/<conversation-id>/walkthrough.md`).
