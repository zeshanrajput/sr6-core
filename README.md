# SR6 Core (`sr6-core`)

The master engine, dataset compiler, and CLI portfolio manager for Shadowrun 6th Edition character portfolios (**Yuriko**, **Velvet**, **Union**), multi-agent narrative orchestration, campaign narrative engines, creation auditing, multi-format exporters, and RAG rules assistance.

---

## 🌟 Features

- **Multi-Agent Narrative Production Framework (`narrative-director`)**:
  - Autonomous 6-stage drafting, evaluation, and self-correction loop.
  - 7-Sub-Agent Parallel Audit Panel: `axis-voice-internality`, `axis-pacing-structure`, `axis-agency-motivation`, `axis-worldbuilding-grit`, `no-ai-slop`, `continuity-tracker`, and `sr6-rules`.
  - **Era-Aware Voice Specs (`arc_chronology`)**: Prevents retrospective flattening by scoring against active developmental eras.
  - **Tiered Chapter Architecture (`chapter_tiers`)**: Calibrates thresholds across Tier 1 Keystones (9.0/10), Tier 2 Narrative Evolution (8.5/10), and Tier 3 Atmospheric Bridges (8.0/10).
  - **Audio Narration & TTS Fluency Discipline**: Strict ellipses density budget ($\le 0.6$ per 300 words), dialogue stitching, and elimination of sensory shortcuts.
- **Antigravity Agent Plugin (`sr6-narrative-suite`) & Native MCP Server**:
  - Bundles 8 sub-agent evaluation skills, modular `narrative-director` rules, and real-time lifecycle hooks.
  - Exposes 6 native Agent tools (`sr6_evaluate_draft`, `sr6_parse_combat_ledger`, `sr6_search_rules`, `sr6_query_rag`, `sr6_lint_prose`, `sr6_audit_character`), live URI resources (`sr6://`), and pre-engineered prompt templates over stdio MCP.
- **Unified 7-Axis Narrative Evaluator (`sr6 evaluate`)**:
  - Scores chapter prose across all 7 evaluation dimensions with Tier 1 (9.0), Tier 2 (8.5), and Tier 3 (8.0) thresholds and generates a rich Markdown scorecard.
- **Tabletop Combat Action & Ledger Parser (`sr6 ledger parse`)**:
  - Automatically extracts fired ammunition (APDS, Gel, Regular, Flechette), physical/stun damage taken, drain/fading suffered, and rewards from chapter prose into explicit `character_master.yaml` patches.
- **CommLink6 XML Dataset Compiler**: Automatically indexes 7,500+ official XML dataset records (`ref_qualities`, `ref_spells`, `ref_complex_forms`, `ref_gear`, `ref_metatypes`) extracted directly from `CommLink6` JAR releases into SQLite.
- **CommLink6 GUI Automated Roundtrip Sync**: Scans player save directories (`~/CommLink6/player/myself/shadowrun6/`) and automatically patches character XML save files in place with live campaign Quarto totals (Karma, Nuyen, Reputation), standardized SRM contacts, full ISO-8601 timestamps, and terminal visual diffs.
- **Pydantic Stat Block Subsystem & Dynamic Weapon Array Engine**:
  - 9 Strictly validated Pydantic models (`WeaponStatBlock`, `ArmorStatBlock`, `VehicleStatBlock`, `SpellStatBlock`, `ComplexFormStatBlock`, `SpriteStatBlock`, `SpiritStatBlock`, `AIStatBlock`, `NPCStatBlock`) enforcing tabletop constraints ($B,A,R,S,W,L,I,C \ge 1$, $0.0 < \text{Essence} \le 6.0$, valid damage notation, AI Matrix Condition Monitor $\lceil \text{WIL}/2 \rceil + 8$).
  - **Dynamic Post-Modification Arrays (`calculate_modified_weapon`)**: Automatically computes modified Attack Ratings (+2 Smartlink, +2 Attack Dice), barrel ranges, extended clip capacities, and ammo damage modifiers across cards, text sheets, and Quarto appendix dossiers.
  - **Dual Stat Block Formatters**: `format_statblock_markdown` (Quarto callouts) and `format_statblock_plaintext` (76-column ASCII bordered tables).
- **GPU CUDA Docling Layout & Extraction Pipeline (`sr6 vault`)**:
  - IBM Docling deep learning engine (`DocLayNet` + `TableFormer`) accelerated by NVIDIA CUDA for multi-column layout separation and authentic 2D Markdown table reconstruction.
  - 20,082 atomic rule chunks indexed across 51 official SR6 publications with *City Edition: Hong Kong* (`SR6H`) as the canonical core baseline.
  - Parallel vector synchronization (`sync_gemini_store`) with SHA-256 hash tracking to the Google Gemini File Search Store (`Shadowrun 6E SRM Vault`).
- **Advanced Offline 5-Stage Hybrid Search & Cross-Edition Consolidation (`sr6 rag search`)**:
  - 5-Stage search cascade: O(1) Topic Match $\rightarrow$ Multi-Word Topic Containment $\rightarrow$ Topic Prefix $\rightarrow$ BM25 Column-Weighted FTS5 (`topic` x5.0, `tags` x3.0) $\rightarrow$ Substring Fallback.
  - **Canonical Edition Consolidation**: Merges identical topics across *City Edition: Hong Kong*, *Seattle*, and *Berlin* into a single canonical entry with automatic cross-edition page references (`+ Also in: Seattle p. 5, Berlin p. 247`).
  - **Instant Pydantic Statblock Attachment (`r["statblock"]`)**: Automatically parses and attaches typed models to offline search results without cloud API dependencies.
  - **Keyword-Centered Context Snippets**: FTS5 snippet extraction with keyword highlighting in rich terminal tables.
- **Official SRM Contacts Indexing**: Populates official SRM named contacts from SRMG v2.4 Appendix C (`SRMG-0492` & `SRMG-0493`), enforcing fixed SRM Connection ratings and canonical archetypes across character portfolios.
- **Enriched Cross-Referencing**: Merges CommLink6 stat parameters (Karma, Nuyen, Drain, Fading, ratings) with rules vault narrative descriptions into unified item cards.
- **Deep Creation Auditor & Flexible Pricing Engine**:
  - Item-by-Item verification of master YAML files against database schemas.
  - Distinguishes **Base Book Price** from **Actual Transaction Cost**, supporting quality discounts (*Smile for the Camera*), DIY rigger modification discounts (50% self-work), contact markups, and manual overrides.
- **Interactive Character Advancement & Shopping Wizard**: CLI wizard to search items/qualities, calculate transaction prices, and record purchases into character dossiers.
- **Multi-Format Exporters**: Generates Roll20 JSON, Plain-Text VTT, and 100% CommLink6 / Genesis-compliant XML character sheets.
- **Quarto Story Book Engine**:
  - `log_engine`: In-memory evaluation tracking of global Karma, Lifetime Karma, Nuyen ledgers, Submersion echo grades, active registered sprite expiration (3-mission limit), and heat across multi-file Quarto story books (`character_log.qmd`, `character_purchases.qmd`).
  - `shortcodes`: Expands `{{< rule "Topic" >}}` and `{{< quality "id" >}}` into styled HTML callout boxes with stat blocks and book citations.
  - `prose linter`: Scans chapters for banned AI buzzwords, cognitive buffer verbs, ellipses density, and markdownlint formatting.
- **CI/CD & GitHub Pages Integration**: Native `pyproject.toml` Git dependency specifications (`[tool.uv.sources] sr6-core = { git = "...", branch = "master" }`) enabling headless `uv run quarto render` builds on remote GitHub Actions runners without requiring relative directory pathing.
- **Ecosystem Sync (`sr6 sync-all`)**: Single-command workspace synchronizer that audits portfolios, regenerates VTT/JSON/XML sheets into `output/` folders, and patches CommLink6 GUI player saves across all character repos.

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

  velvet:
    name: "Velvet"
    repo: "sr6velvet"
    repo_path: "C:\\GitHub\\sr6velvet"
    master_yaml: "velvet_master.yaml"

  union:
    name: "Union"
    repo: "sr6union"
    repo_path: "C:\\GitHub\\sr6union"
    master_yaml: "union_master.yaml"
```

### 2. Environment Variables
Override default paths without modifying source code:
- **`SR6_WORKSPACE_ROOT`** (or `GITHUB_ROOT`): Root directory containing character repositories (defaults to parent directory or `C:\GitHub`).
- **`COMMLINK_PLAYER_DIR`** (or `SR6_COMMLINK_DIR`): Path to CommLink6 player saves (defaults to `~/CommLink6/player/myself/shadowrun6`).
- **`SR6_DEFAULT_MODEL`**: Default LLM model identifier (defaults to `gemini-flash-latest`).
- **`SR6_LLAMA_URL`**: Base URL of local `llama.cpp` server (defaults to `http://localhost:8080/v1`).
- **`SR6_LLAMA_BIN`**: Path to `llama-server.exe` for auto-launching local model server.
- **`SR6_LLAMA_MODEL_PATH`**: Path to local `.gguf` model file for auto-launching.

---

## 🎭 Multi-Agent Narrative Production Architecture

`sr6-core` powers autonomous narrative drafting and refinement across character books via the `narrative-director` orchestrator:

```
                      +-----------------------------+
                      |   1. CONTEXT INGESTION      |
                      | Outline, Voice Spec, Dossier|
                      +--------------+--------------+
                                     |
                                     v
                      +-----------------------------+
                      |   2. INITIAL DRAFT (v1)     |
                      +--------------+--------------+
                                     |
                                     v
         +-------------------------------------------------------+
         |            3. PARALLEL SUB-AGENT AUDIT PANEL          |
         |  - axis-voice-internality   - axis-pacing-structure   |
         |  - axis-agency-motivation   - axis-worldbuilding-grit |
         |  - no-ai-slop               - continuity-tracker      |
         |  - sr6-rules                                          |
         +---------------------------+---------------------------+
                                     |
                                     v
                      +-----------------------------+
                      | 4. SYNTHESIS & SELF-CORRECT |  <-- (Fails threshold?
                      |  Passes all 7 thresholds?   |       Re-draft v2, v3)
                      +--------------+--------------+
                                     | Passes
                                     v
                      +-----------------------------+
                      |  5. PUBLISH & STATE TRACK   |
                      |  Output .qmd & YAML diffs   |
                      +-----------------------------+
```

### 7-Sub-Agent Evaluation Panel
1. **`axis-voice-internality`**: Audits character voice, POV, internal monologue, and era calibration against `reference/voice_spec.md`.
2. **`axis-pacing-structure`**: Enforces 4-beat structure (Inciting Friction -> Escalation -> Climax -> Aftermath) and 80/20 action-to-exposition ratio.
3. **`axis-agency-motivation`**: Verifies protagonist proactive choice, consequential stakes, and arc alignment.
4. **`axis-worldbuilding-grit`**: Injects dystopian texture, corporate omnipresence, and AR noise with zero info-dumps.
5. **`no-ai-slop`**: Redlines AI clichés, banned phrases, binary contrasts, and excessive ellipses ($\le 0.6 / 300\text{ words}$).
6. **`continuity-tracker`**: Cross-checks ammo, nuyen, damage tracks, and gear against `character_master.yaml` and logs.
7. **`sr6-rules`**: Verifies authentic SR6 mechanics, spell drain, Matrix actions, and Edge expenditures via Gemini RAG.

---

## 📁 Standard Character Portfolio Architecture & Templates

Each character managed by `sr6-core` (e.g. `sr6yuriko`, `sr6velvet`, `sr6union`) follows a standardized repository layout:

```text
sr6<char_id>/
├── <char_id>_master.yaml     # Master character dossier (authoritative sheet data)
├── reference/                # Local project reference docs
│   └── voice_spec.md         # Character voice spec (extends sr6-core/reference/default_voice_spec.md)
├── chapters/                 # Quarto narrative story book
│   ├── index.qmd             # Book introduction & character background
│   ├── twenty_questions.qmd  # Shadowrun 20 Questions backstory questionnaire
│   ├── character_log.qmd     # Campaign narrative chapters & session logs
│   └── character_purchases.qmd # Nuyen/Karma transactions ledger
├── output/                   # Auto-generated exports (from sr6 sync-all)
│   ├── <char_id>_sheet.json  # Roll20 JSON sheet
│   ├── <char_id>_sheet.txt   # Plain-text VTT sheet
│   └── <char_id>_sheet.xml   # CommLink6 / Genesis compliant XML sheet
└── _quarto.yml               # Quarto book build configuration
```

### Included Starter Templates (`templates/`)

`sr6-core` provides starter templates for bootstrapping new character portfolio projects:
- `templates/character_master.yaml.template`: Master YAML sheet template.
- `templates/reference/voice_spec.md.template`: Starter character voice specification template with era arcs and chapter tiers.
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

# Inspect specific item reference card (quality, weapon, spell, cyberware, vehicle, program)
sr6 card quality ambidextrous
sr6 card weapon ares_predator_vi

# Query Rules RAG AI Assistant (Gemini API)
sr6 rag query "How can I heal fading damage?"

# Query Local llama.cpp / Gemma instance
sr6 rag query "How does fading healing work?" --provider llama --model gemma-2-9b-it

# Query RAG with Active Runner Dossier Context
sr6 rag query "What matrix actions can I take?" --char yuriko --provider llama
```

### Portfolio & Character Management
```bash
# List configured character portfolios
sr6 characters list

# Run deep item-by-item audit on character portfolio
sr6 characters audit union
sr6 characters audit velvet

# Interactively purchase gear/qualities for character
sr6 characters advance union cyberjack

# Export character sheet (Roll20 JSON, VTT Text, Genesis XML, Cards Deck)
sr6 export velvet --format=cards
```

### Campaign & Quarto Prose Tools
```bash
# Lint Quarto chapter prose for style, ellipses density, and AI buzzwords
sr6 lint C:\GitHub\sr6yuriko\chapters\character_log.qmd

# Unified 7-axis narrative audit with tier-calibrated scoring (Tier 1: 9.0, Tier 2: 8.5, Tier 3: 8.0)
sr6 evaluate C:\GitHub\sr6yuriko\chapters\character_log.qmd --tier 2 --char yuriko

# Tabletop combat action extraction & YAML state patch generator
sr6 ledger parse C:\GitHub\sr6yuriko\chapters\character_log.qmd

# Run campaign story continuity audit
sr6 continuity C:\GitHub\sr6yuriko

# Generate TTS audio narration for chapter
sr6 narrate C:\GitHub\sr6yuriko\chapters\character_log.qmd
```

### Antigravity Agent Plugin (`sr6-narrative-suite`)
```bash
# Check plugin installation and skills status
sr6 plugin status

# Install plugin globally to ~/.gemini/config/plugins/
sr6 plugin install --symlink

# Initialize .agents/plugins.json inheritance in a character repository
sr6 plugin init-repo C:\GitHub\sr6yuriko
```
