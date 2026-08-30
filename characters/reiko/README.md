# Shadowrun 6e Portfolio & Story Anthology — Yuriko Star

This repository contains the interactive character dossier, downtime tracking system, rules cheatsheets, and narrative story anthology for **Yuriko Star v9** (`r31k0` Takahashi), an emergent AI-Pilot / Technoshaman character built for Shadowrun 6th Edition (Sixth World) and active in **Shadowrun Missions** organized play.

The project compiles into a responsive book using **Quarto** and is powered centrally by the [`sr6-core`](https://github.com/zeshanrajput/sr6-core) master engine and multi-agent narrative framework.

---

## 🌟 The Creative Vision: "The Spaces Between"

While this repository maintains 100% mechanical fidelity to Shadowrun 6th Edition rules, the fiction is written to look **beyond the numbers**—exploring the rich, tangible, emotionally accessible "spaces between" game statistics:

* **Spiritual Technology:** Experiencing the Matrix and Resonance as a living, animistic ecosystem rather than cold silicon diagnostics.
* **Reframing the Human Condition:** Examining universal human themes—identity, belonging, debt, guardianship, grief, and connection—through the fresh perspective of an emergent Digital Intelligence (DI) navigating physical embodiment and spiritual transcendence.
* **Core Character Goals:**
  1. **Sanctuary & Emancipation:** Fund and protect `r3sP@wn`, a virtual sanctuary dedicated to rescuing wild sprites and emergent sparks from corporate deletion and exploitation.
  2. **Technoshamanism:** Master the Resonance Realms and bridge the gap between physical drone flight and digital divinity.
  3. **Duty & Connection:** Pay off her team's debt while navigating the tragic friction between digital transcendence and physical vulnerability.

---

## 📁 Repository Structure

```text
sr6yuriko/
├── yuriko_master.yaml        # Master character dossier (authoritative YAML sheet data)
├── reference/                # Local project reference docs
│   ├── voice_spec.md         # Character voice spec (extends sr6-core/reference/default_voice_spec.md)
│   ├── visual_anchors.md     # Visual design anchors, art prompts, and key image links
│   ├── coffin_girls.md       # Coffin Girls faction & haven dossier
│   ├── river_people.md       # River People faction dossier
│   └── story_continuity.md   # Auto-indexed campaign continuity map (from sr6 continuity)
├── chapters/                 # Quarto narrative story book
│   ├── index.qmd             # Book introduction & character background
│   ├── twenty_questions.qmd  # Shadowrun 20 Questions backstory questionnaire
│   ├── character_log.qmd     # Campaign narrative chapters & session logs (with live python ledgers)
│   ├── character_purchases.qmd # Itemized Nuyen/Karma transaction ledgers
│   ├── identity_core.qmd     # Metatype, stream, attributes, matrix, living persona stats
│   ├── rules_*.qmd           # Specialized rules cheatsheets (combat, matrix, sprites, drones)
│   └── *.md                  # Narrative archive chapters
├── output/                   # Auto-generated exports (from sr6 sync-all)
│   ├── text/                 # 76-column modular plain-text sheets
│   └── vtt/                  # Roll20 JSON & CommLink6/Genesis XML sheets
├── _quarto.yml               # Quarto book build configuration
├── pyproject.toml            # uv project configuration pulling sr6-core
└── .agents/
    ├── AGENTS.md             # Master workspace instructions & orchestrator protocols
    └── plugins.json          # Inherits Antigravity sr6-narrative-suite plugin
```

---

## ⚙️ Multi-Agent Narrative Production & CLI Tools

All rules audits, character sheet generation, and narrative evaluations are managed via the `sr6` CLI (provided by `sr6-core`):

### 1. Unified 7-Axis Narrative Evaluator & Tabletop Ledger
```bash
# Run 7-axis evaluation on chapter prose calibrated to chapter tier
sr6 evaluate "chapters/XX_n Saturation.md" --tier 2

# Extract fired ammunition, damage taken, fading, and rewards into YAML diffs
sr6 ledger parse "chapters/XX_n Saturation.md"

# Lint chapter prose for banned buzzwords, cognitive verbs, and formatting
sr6 lint "chapters/XX_n Saturation.md"
```

### 2. Ecosystem Synchronization & CommLink6 Roundtrip
```bash
# Run deep audits, regenerate exports in output/, and patch active CommLink6 GUI saves
sr6 sync-all

# Sync CommLink6 GUI player saves specifically
sr6 db sync-commlink
```

### 3. Character Auditing & Export
```bash
# Deep item-by-item audit against master rules database
sr6 characters audit yuriko

# Export character sheet (Roll20, Plain-text VTT, Genesis XML)
sr6 export yuriko --format=vtt
```

### 4. Story Continuity & Rules RAG Assistant
```bash
# Index campaign relationships, sprite states, and heatmaps
sr6 continuity .

# Query Gemini AI Rules RAG with Yuriko's active dossier context
sr6 rag query "How does fading healing interact with resonance wellsprings?" --char yuriko

# Check Antigravity plugin status
sr6 plugin status
```

---

## 🚀 Local Book Compilation & Publishing

To render and publish the Quarto book locally:

```bash
# Install dependencies
uv sync

# Render Quarto book to HTML
quarto render

# Publish to GitHub Pages
quarto publish gh-pages --no-prompt --no-browser
```
