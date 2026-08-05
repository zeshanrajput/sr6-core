# SR6 Core (`sr6-core`)

The master engine, dataset compiler, and CLI portfolio manager for Shadowrun 6th Edition character portfolios (**Yuriko**, **Velvet**, **Union**), campaign narrative engines, creation auditing, multi-format exporters, and RAG rules assistance.

---

## 🌟 Features

- **CommLink6 XML Dataset Compiler**: Automatically indexes 7,500+ official XML dataset records (`ref_qualities`, `ref_spells`, `ref_complex_forms`, `ref_gear`, `ref_metatypes`) extracted directly from `CommLink6` JAR releases into SQLite.
- **CommLink6 GUI Automated Roundtrip Sync**: Scans player save directories (`~/CommLink6/player/myself/shadowrun6/`) and automatically patches character XML save files in place with live campaign Quarto totals (Karma, Nuyen, Reputation), standardized SRM contacts, and full ISO-8601 timestamps.
- **Rules Vault & RAG Subsystem**: Full-text FTS5 search and Gemini AI rules reference assistant enforcing the SRM 4-Level Authority hierarchy with physical book citations (`[Book, Page]`).
- **Official SRM Contacts Indexing**: Populates official SRM named contacts from SRMG v2.4 Appendix C (`SRMG-0492` & `SRMG-0493`), enforcing fixed SRM Connection ratings and canonical archetypes across character portfolios.
- **Enriched Cross-Referencing**: Merges CommLink6 stat parameters (Karma, Nuyen, Drain, Fading, ratings) with rules vault narrative descriptions into unified item cards.
- **Deep Creation Auditor & Flexible Pricing Engine**:
  - Item-by-Item verification of master YAML files against database schemas.
  - Distinguishes **Base Book Price** from **Actual Transaction Cost**, supporting quality discounts (*Smile for the Camera*), DIY rigger modification discounts (50% self-work), contact markups, and manual overrides.
- **Interactive Character Advancement & Shopping Wizard**: CLI wizard to search items/qualities, calculate transaction prices, and record purchases into character dossiers.
- **Multi-Format Exporters**: Generates Roll20 JSON, Plain-Text VTT, and 100% CommLink6 / Genesis-compliant XML character sheets.
- **Quarto Story Book Engine**:
  - `shortcodes`: Expands `{{< rule "Topic" >}}` and `{{< quality "id" >}}` into styled HTML callout boxes with stat blocks and book citations.
  - `dossier appendix`: Auto-generates dynamic `dossier_appendix.qmd` files in character repositories.
  - `prose linter`: Scans chapters for banned AI buzzwords, cognitive buffer verbs, and markdownlint formatting.
- **Ecosystem Sync (`sr6 sync-all`)**: Single-command workspace synchronizer that audits portfolios, regenerates VTT/JSON/XML sheets into `output/` folders, patches CommLink6 GUI player saves, and updates Quarto book dossier appendices across all character repos.

---

## 🔄 CommLink6 GUI Purchasing & Roundtrip Workflow

### Dual-Ledger Best Practice:
1. **In CommLink GUI (UUID & Stat Generation)**:
   Add physical items, gear modifications, or drones directly inside CommLink's GUI interface. CommLink handles internal UUID generation, capacity slots, and stat math.
2. **In Quarto Books (`character_log.qmd` / `character_purchases.qmd`)**:
   Log the exact financial transaction with your actual discounted cost paid:
   ```markdown
   * **Purchased FB Sky Commander:** `{python} inc('Nuyen', -12500)` *(DIY Rigger 50% modification discount)*
   * **Attribute Increase (Resonance 8):** `{python} inc_many(('Karma', -40), ('Resonance', 1))`
   ```
   > *CommLink GUI is unaware of custom downtime discounts (Smile for the Camera, DIY rigger self-work, contact markups, or house haggling).*
3. **Automated Ecosystem Sync (`sr6 sync-all`)**:
   Running `sr6 sync-all` (or `sr6 db sync-commlink`) reads your active CommLink GUI save file, evaluates your Quarto log to compute true available Karma (`karmaF`), spent Karma (`karmaI`), and Nuyen (`nuyen`), isolates base mission reward gains, and writes the updated XML back to CommLink without overwriting your GUI item edits.

---

## ⚙️ Configuration & Environment Overrides

`sr6-core` is fully configurable for different user environments, custom workspace paths, and arbitrary character rosters.

### 1. Character Roster Configuration (`characters.yaml`)
Define custom character portfolios in `characters.yaml`:
```yaml
characters:
  yuriko:
    name: "Yuriko Star"
    repo: "sr6yuriko"
    repo_path: "C:\\GitHub\\sr6yuriko"
    master_yaml: "yuriko_master.yaml"

  my_runner:
    name: "Ghost"
    repo: "sr6ghost"
    master_yaml: "ghost_master.yaml"
```

### 2. Environment Variables
Override default paths without modifying source code:
- **`SR6_WORKSPACE_ROOT`** (or `GITHUB_ROOT`): Root directory containing character repositories (defaults to parent directory or `C:\GitHub`).
- **`COMMLINK_PLAYER_DIR`** (or `SR6_COMMLINK_DIR`): Path to CommLink6 player saves (defaults to `~/CommLink6/player/myself/shadowrun6`).

---

## 🧹 Migration & Refactoring Checklist for Character Projects

When updating individual character repositories (`sr6yuriko`, `sr6velvet`, `sr6union`) to integrate with `sr6-core`:

### 1. Safe Deletions (Redundant Code & Skill Folders)
- [x] **Delete `.agents/skills/`**: Remove duplicate skill folders (`sr6-rules`, `no-ai-slop`, `literary-analysis`, `continuity-tracker`). These are now centrally managed in `c:\GitHub\sr6-core\.agents\skills\`.
- [x] **Delete Local Rules Vaults / Databases**: Remove any local `shadowrun_rules.db` or local `rules_vault/` copies. All rules queries now target the master database at `~/.sr6/rules_index.db`.
- [x] **Delete Redundant Python Scripts**: Remove local duplicate scripts (`linter.py`, `log_engine.py`, `continuity_engine.py`, `rules_engine.py`, `narration.py`). Use `sr6` CLI subcommands instead.

### 2. File Placement & Structure
- [x] **Master Dossier File**: Ensure `*_master.yaml` exists at the root of the character repository (e.g. `c:\GitHub\sr6yuriko\yuriko_master.yaml`).
- [x] **Quarto Book Structure**: Ensure narrative files live inside `chapters/` (e.g., `chapters/index.qmd`, `chapters/character_log.qmd`, `chapters/twenty_questions.qmd`).
- [x] **Quarto Book Config**: Include `- chapters/dossier_appendix.qmd` in `_quarto.yml` under `book.chapters`.

### 3. Agent Instructions
- [x] **Update `.agents/AGENTS.md`**: Update character repo instructions to use `sr6` CLI subcommands:
  - Rules Lookup: `sr6 rag query "<query>"` or `sr6 search "<item>"`
  - Prose Linter: `sr6 lint chapters/<file>.qmd`
  - Continuity Audit: `sr6 continuity .`
  - Sheet Exporters: `sr6 export <char_id> --format=xml|vtt|roll20`

### 4. Verification
- [x] **Run Ecosystem Sync**: Execute `uv run sr6 sync-all` from `sr6-core` to perform deep audits, regenerate `output/` sheets, patch active CommLink6 GUI saves, and build the dynamic Quarto dossier appendix for the character repository.

---

## 📁 Standard Character Portfolio Architecture & Templates

Each character managed by `sr6-core` (e.g. `sr6yuriko`, `sr6velvet`, `sr6union`) follows a standardized repository layout:

```text
sr6<char_id>/
├── <char_id>_master.yaml     # Master character dossier (authoritative sheet data)
├── chapters/                 # Quarto narrative story book
│   ├── index.qmd             # Book introduction & character background
│   ├── twenty_questions.qmd  # Shadowrun 20 Questions backstory questionnaire
│   ├── character_log.qmd     # Campaign narrative chapters & session logs
│   ├── character_purchases.qmd # Nuyen/Karma transactions ledger
│   └── dossier_appendix.qmd  # Live auto-generated dossier appendix (from sr6 sync-all)
├── output/                   # Auto-generated exports (from sr6 sync-all)
│   ├── <char_id>_sheet.json  # Roll20 JSON sheet
│   ├── <char_id>_sheet.txt   # Plain-text VTT sheet
│   └── <char_id>_sheet.xml   # CommLink6 / Genesis compliant XML sheet
└── _quarto.yml               # Quarto book build configuration
```

### Included Starter Templates (`templates/`)

`sr6-core` provides starter templates for bootstrapping new character portfolio projects:
- `templates/character_master.yaml.template`: Master YAML sheet template.
- `templates/quarto/_quarto.yml.template`: Starter Quarto book YAML configuration.
- `templates/quarto/index.qmd.template`: Character overview & background.
- `templates/quarto/twenty_questions.qmd.template`: 20 Questions backstory questionnaire.
- `templates/quarto/character_log.qmd.template`: Session log with rule shortcodes.
- `templates/quarto/character_purchases.qmd.template`: Transaction ledger.

---

## 🚀 Quick Start

### Installation

```bash
uv sync
```

### Launch Interactive CLI Menu

```bash
sr6
# or
uv run sr6
```

---

## 🛠️ CLI Command Reference

### Ecosystem One-Command Sync & CommLink GUI Roundtrip
```bash
# Run deep audits, regenerate exports in output/, patch CommLink6 saves, and update Quarto dossier appendices
sr6 sync-all

# Sync CommLink6 GUI player saves specifically (C:\Users\<user>\CommLink6\player\myself\shadowrun6\)
sr6 db sync-commlink
```

### Rules & CommLink6 Datasets
```bash
# Display database status and CommLink6 dataset counts
sr6 db info

# Extract and index datasets from CommLink6 JAR
sr6 db import-commlink

# Re-index Shadowrun Rules Vault markdown files
sr6 db compile-vault

# Search rules and display enriched stat + citation cards
sr6 search "augmentation_acclimation"

# Query Rules RAG AI Assistant
sr6 rag query "How can I heal fading damage?"
```

### Portfolio & Character Management
```bash
# List configured character portfolios
sr6 characters list

# Run deep item-by-item audit on character portfolio
sr6 characters audit union

# Interactively purchase gear/qualities for character
sr6 characters advance union cyberjack

# Export character sheet (Roll20 JSON, VTT Text, Genesis XML)
sr6 export velvet --format=xml
```

### Campaign & Quarto Prose Tools
```bash
# Lint Quarto chapter prose for style and AI buzzwords
sr6 lint C:\GitHub\sr6yuriko\chapters\character_log.qmd

# Run campaign story continuity audit
sr6 continuity C:\GitHub\sr6yuriko

# Generate TTS audio narration for chapter
sr6 narrate C:\GitHub\sr6yuriko\chapters\character_log.qmd
```
