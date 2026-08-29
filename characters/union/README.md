# Shadowrun 6e Portfolio - Venn

This repository contains the interactive character dossier, downtime tracking system, rules cheatsheets, and narrative anthology for **Venn** (Nathan Turrent & Veronica), a Monad (Human / AI Dual Entity) Technomancer & Operative character built for Shadowrun 6th Edition (Sixth World) and active in **Shadowrun Missions** organized play.

The project is compiled into a polished, responsive book using **Quarto** and powered by [`sr6-core`](https://github.com/zeshanrajput/sr6-core).

---

## Project Structure

- `union_master.yaml`: Authoritative master dossier file containing raw sheet statistics, attributes, living persona, qualities, skills, cyberware augmentations, activesofts, weapons, armor, and synergies.
- `chapters/`: The source files for the Quarto book:
  - `identity_core.qmd`: Metatype, background history, story context, and Monad identity core.
  - `character_build_pb.qmd`: Point-buy calculations and Karma breakdown.
  - `character_sheet.qmd`: Embeds modular plain-text character sheets with links to downloadable laserjet PDF card decks and CommLink XML/JSON saves.
  - `character_totals.qmd`: Career totals dashboard (Karma, Nuyen, Essence, Hooder obligations, and Contact network).
  - `character_log.qmd`: Complete run history, Karma trackers, Nuyen ledgers, and contact progressions.
  - `character_purchases.qmd`: Itemized gear, cyberware implants, activesofts, armor, SINs, and lifestyle expenses.
  - `rules_and_downtime.qmd`: Dynamic combat tables, Living Persona matrix actions, SRMG adrenaline stacking, and downtime expenses.
  - `twenty_questions.qmd`: Twenty Questions backstory questionnaire.
  - `narrative_outline.qmd`: 7-story narrative anthology overview.
  - `01 The Day a God Fell.qmd`, `story02_*.qmd`, etc.: Narrative story chapters.
- `input/`: Character source files (XML export from Chummer6/Genesis and JSON datasets).
- `output/`: Holds compiled modular text sub-sheets (`output/text/`) and CommLink/VTT files (`output/vtt/`).
- `reference/`: Master design references:
  - `voice_spec.md`: Character voice specification and schema (extends `sr6-core/reference/default_voice_spec.md`).
  - `visual_anchors.md`: Character design anchors, sensory palettes, and generative prompt templates.
  - `story_continuity.md`: Entity graph, contact relationships, and story continuity index.

---

## Local Development & Ecosystem Sync

`sr6union` relies on `sr6-core` for export generation, rules indexing, prose linting, multi-agent narrative orchestration, and CommLink GUI roundtrip synchronization.

1. **Setup Dependencies**:
   ```bash
   uv sync
   ```

2. **Ecosystem & CommLink GUI Sync**:
   ```bash
   uv run sr6 sync-all
   ```

3. **Export Specific Formats**:
   ```bash
   uv run sr6 export union --format=vtt
   uv run sr6 export union --format=xml
   uv run sr6 export union --format=roll20
   ```

4. **Lint Story Prose & Anti-Slop**:
   ```bash
   uv run sr6 lint "chapters/01 The Day a God Fell.qmd"
   ```

5. **Campaign Continuity Audit**:
   ```bash
   uv run sr6 continuity .
   ```

6. **Compile the Quarto Book**:
   ```bash
   quarto render
   ```

7. **Publish to GitHub Pages**:
   ```bash
   quarto publish gh-pages --no-prompt --no-browser
   ```
