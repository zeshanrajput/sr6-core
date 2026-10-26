# Character Repository Architecture & Nomenclature Standard

This document defines the standardized directory layout, file nomenclature, and division of labor for character repositories within `sr6-core` (`characters/<char_id>/`).

Every character repository adheres to a strict **Single Source of Truth** model, separating deterministic tabletop mechanics from creative prose craft, strategic campaign roadmaps, and machine-generated continuity ledgers.

---

## 1. Standard Character Directory Structure

```text
characters/<char_id>/
├── core/                           # Deterministic Tabletop Source of Truth (Markdown Trio)
│   ├── character_build.qmd         # Chargen priorities, attributes, skills, qualities, magic/resonance
│   ├── character_purchases.qmd     # Consecrated gear purchases, nuyen ledger, bonded foci
│   └── character_log.qmd           # Session records, karma progression, contacts awarded
│
├── narrative/                      # Published Story Anthology
│   ├── 01_<title>.md               # Numbered narrative chapters (Quarto/Markdown)
│   ├── 02_<title>.md
│   └── audio/                      # Generated 160kbps Kokoro TTS MP3 narrations (Release assets)
│
├── reference/                      # Guidance, Craft Specs, & Storyboards
│   ├── storyboard.md               # The Strategic & Dramatic Roadmap (Thematic Verticals)
│   ├── voice_spec.md               # The Literary Craft & POV Spec (Sensory Lens, Anti-Slop)
│   ├── story_continuity.md         # Deterministic Contact & Chapter Ledger (sr6 story sync)
│   ├── mechanical_plan.md          # Future build theorycrafting & advancement roadmap
│   └── archive/                    # Superseded, legacy, or deprecated narrative files
│
├── _quarto.yml                     # Quarto book publication configuration
├── index.qmd                       # Character portfolio introduction & navigation hub
└── <char_id>_master.yaml           # Compiled deterministic character sheet (DO NOT EDIT BY HAND)
```

---

## 2. Division of Labor & Single Sources of Truth

| File / Folder | Role & Domain | Authority Level | Governing Rule / Spec |
| :--- | :--- | :--- | :--- |
| **`core/*.qmd`** (The Trio) | **Deterministic Tabletop State**<br>Build, purchases, and advancement. | **Master Source of Truth for Mechanics** | Compiled into `<char>_master.yaml` via `uv run sr6 sync-all`. Never edit master YAML directly. |
| **`reference/storyboard.md`** | **The Dramatic & Strategic Engine**<br>Tracks the 6 thematic verticals (3 external, 3 internal), bespoke foils, and story queue across non-linear campaign play. | **Master Source of Truth for Plot & Drama** | Extends [`reference/default_storyboard_spec.md`](file:///c:/GitHub/sr6-core/reference/default_storyboard_spec.md). Replaces legacy linear `story_arc*.md` files. |
| **`reference/voice_spec.md`** | **The Literary Craft & POV Specification**<br>POV, cognitive bias, sensory matrix, acoustic rules, and character-specific anti-slop redlines. | **Master Source of Truth for Prose Craft** | Extends [`reference/default_voice_spec.md`](file:///c:/GitHub/sr6-core/reference/default_voice_spec.md). Ingested by `literary-analysis` and `narrative-director`. |
| **`reference/story_continuity.md`** | **Machine-Generated Continuity Index**<br>Tracks contact appearances, chapter word counts, and verification status. | **Master Source of Truth for Historical Appearances** | Auto-updated by `uv run sr6 story sync <char_id>`. Never manual-edit tables managed by the engine. |
| **`narrative/*.md`** | **Published Prose Chapters**<br>The canonical inter-session literature. | **Immutable Creative Prose** | Governed by [`reference/inter_session_narrative_doctrine.md`](file:///c:/GitHub/sr6-core/reference/inter_session_narrative_doctrine.md). Stripped of game mechanics jargon. |
| **`reference/mechanical_plan.md`** | **Theorycrafting Roadmap**<br>Future karma investments, power point allocations, and augmentation paths. | **Advisory / Planning Only** | Synchronized with table legalities and archetype constraints. |

---

## 3. Inheritance Architecture (Parent-Child Specifications)

To eliminate copy-paste redundancy across character folders, character reference files inherit from workspace-level parent specifications located in `reference/`:

```text
[reference/inter_session_narrative_doctrine.md]  (Governing Theological & Psychological Doctrine)
     │
     ├──► [reference/default_storyboard_spec.md]  (Parent Storyboard Schema)
     │         ▲
     │         ├── characters/velvet/reference/storyboard.md
     │         ├── characters/reiko/reference/storyboard.md
     │         └── characters/venn/reference/storyboard.md
     │
     └──► [reference/default_voice_spec.md]       (Parent Voice & Craft Schema)
               ▲
               ├── characters/velvet/reference/voice_spec.md
               ├── characters/reiko/reference/voice_spec.md
               └── characters/venn/reference/voice_spec.md
```

### Inheritance Rules:
1. **Extend, Don't Re-Invent**: Child files declare `**Extends**: reference/default_<type>_spec.md` in their YAML frontmatter or document header.
2. **Override Only Specifics**: Child files define character-specific cognitive biases, unique sensory domains, bespoke foils, and personal thematic verticals. Common structural definitions (e.g. the 7-axis audit rubrics, the Two-Tier Dramatic Sphere, standard Markdown reference links) live in the parent specification.
3. **Legacy File Deprecation**: When a character adopts `storyboard.md`, fragmented arc planning files (`story_arc1.md`, `story_arc2.md`, `story_arc3.md`) and unintegrated lore dumps must be moved into `reference/archive/`.

---

## 4. Centralized Bibliographic Standard (`storyboard.md`)

Storyboards cross-reference chapters, session debriefs, and rule doctrines using **Semantic Reference-Style Links** (`[Display Text][key]`):

* **Prose & Tables**:
  ```markdown
  * **The Amsterdam Courier ([11_Silence][ch-11]):** Met **Min-seo** at a Prinsengracht café. Received the [Rating 3 Power Focus][purchases].
  ```
* **Registry Footer**:
  All paths are declared **once** at the bottom of the storyboard in Section VIII:
  ```markdown
  [ch-11]: ../narrative/11_Silence.md
  [purchases]: ../core/character_purchases.qmd
  ```
* **Result**: Zero maintenance friction when files are renamed or converted to `.qmd`. Updating one line at the footer updates every link throughout the entire storyboard.
