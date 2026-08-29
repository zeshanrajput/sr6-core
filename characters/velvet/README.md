# Shadowrun 6e Portfolio & Story Anthology — Velvet

This repository contains the interactive character dossier, career ledger, rules cheat sheets, 20 questions questionnaire, and narrative story anthology for **Velvet** (Kim Jin-Young / Tanaka Ryo / Lee Ji-yoo / Mei Jing), an engineered Elf Shinto/Musok Mystic Adept built for Shadowrun 6th Edition (Sixth World) and active in **Shadowrun Missions** organized play.

The project compiles into a responsive book using **Quarto** and is powered centrally by the [`sr6-core`](https://github.com/zeshanrajput/sr6-core) master engine and multi-agent narrative framework.

---

## 🌟 The Creative Vision: "The Thousand Lives & Engineered Gravity"

While maintaining 100% mechanical fidelity to official Shadowrun 6th Edition rules, the fiction explores deep speculative and metaphysical themes:

* **Engineered Gravity & The Horror of Charisma 10 (14):** Jin-Young was bio-sculpted by Mitsuhama to be a miracle of mass-market desire. Charisma 10 (14 with buff spells) is an uncanny, suffocating psychological pressure. Velvet can never know if anyone's affection, pity, or compliance is authentic, or merely their nervous system collapsing into his manufactured biological gravity.
* **The Somatic Reality of Cosmetic Control (R2):** Shifting between Tanaka Ryo, Lee Ji-yoo, and temporary personas is never instantaneous or painless. It carries a heavy biological tax: bone cartilage resetting with wet clicks, metallic heat behind the jaw, shortened ribcages, and localized DNA re-keying. Beneath every sculpted mask lies the un-sculpted obsidian baseline of his true heritage.
* **The Path of the Thousand Lives (*Sinbyeong* $\rightarrow$ *Living Mosaic* $\rightarrow$ *Upāya*):** Forced transformations evolve into an artificial reincarnation cycle. Velvet retains neuro-somatic skills, virtues, and grief (*Han*) from every lived persona, moving from traumatic fragmentation (*Sinbyeong*) to becoming an empty vessel (*Bin Geureut*) and master of ten thousand lived spirits (*Mansin*), utilizing multiple personas as skillful means (*Upāya*) to protect the vulnerable.
* **The Discovery of Empathy:** Moving from cold algorithmic performance and corporate asset conditioning to crafting quiet, un-monetized sanctuaries (tea, noodles, silence) for broken people in the shadows.

---

## 🗺️ The 3-Arc Tripartite Architecture

```text
┌─────────────────────────────────────────────────────────────────────────────────────────────┐
│ ARC 1: MANUFACTURED SOLACE & THE HONEYTRAP (Chapters 01–08)                                 │
├───────────────────┬─────────────────────────────────────────────────────────────────────────┤
│ • World Basis:    │ Manufactured Solace & The Honeytrap (Fleeing MCT, Sprawl baseline)      │
│ • Internal Basis: │ Sinbyeong (신병) — The Broken Vessel, bodily trauma & identity sickness │
│ • Mechanical:     │ Character Creation & Early Street Play (Magic 6, Grade 1 Channeling)   │
├───────────────────┴─────────────────────────────────────────────────────────────────────────┤
│ ARC 2: THE SOVEREIGN UNDERGROUND & THE PUSH FOR POWER (Chapters 09–18+)                     │
├───────────────────┬─────────────────────────────────────────────────────────────────────────┤
│ • World Basis:    │ Sovereign Underground (Maslow's Safety Need: subterranean fortresses)   │
│ • Internal Basis: │ The Living Mosaic — Accretion of lived human wisdom & Echo phenomenon   │
│ • Mechanical:     │ First 100 TKE (Magic 6, Initiation Grades 2–4, Power Focus R3)          │
├───────────────────┴─────────────────────────────────────────────────────────────────────────┤
│ ARC 3: THE PACIFIC RECKONING & SOVEREIGN EMANATION (Chapters 19+)                           │
├───────────────────┬─────────────────────────────────────────────────────────────────────────┤
│ • World Basis:    │ Pacific Counter-Strike & Sovereign Sanctuary (Hong Kong / Neo-Seoul)    │
│ • Internal Basis: │ Upāya (방편) & The Sovereign Mansin (만신) — The Sacred Mirror (Kagami) │
│ • Mechanical:     │ 200+ TKE (Magic 8, Initiation Grades 6–8, Invocation, Great Forms, Foci)│
└─────────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 📁 Repository Structure

```text
sr6velvet/
├── velvet_master.yaml        # Master character dossier (authoritative YAML sheet data)
├── reference/                # Local project reference docs & continuity
│   ├── voice_spec.md         # Character voice spec (extends sr6-core/reference/default_voice_spec.md)
│   ├── philosophical_framework.md # Metaphysical grounding of the Thousand Lives
│   ├── karmic_persona_log.md # Master registry of lived personas, somatics & neuro-somatic echoes
│   ├── philosophical_framework_report.md # 45-page comprehensive philosophical treatise
│   ├── upgrade_priorities.md # Mechanical upgrade matrix & 3-arc progression milestones
│   ├── story_arc1.md         # Arc 1: Manufactured Solace & The Honeytrap (Ch 01–08)
│   ├── story_arc2.md         # Arc 2: The Sovereign Underground (Ch 09–18+)
│   ├── story_arc3.md         # Arc 3: The Pacific Reckoning (Ch 19+)
│   └── story_continuity.md   # Auto-indexed campaign continuity map (from sr6 continuity)
├── chapters/                 # Quarto narrative story book
│   ├── index.qmd             # Book introduction & character background
│   ├── twenty_questions.qmd  # Shadowrun 20 Questions backstory questionnaire
│   ├── character_log.qmd     # Campaign narrative chapters & session logs (with live python ledgers)
│   ├── character_purchases.qmd # Itemized Nuyen/Karma transaction ledgers
│   ├── character_sheet.qmd   # Embeds modular 76-column plain-text sheets & download links
│   ├── character_totals.qmd  # Career totals dashboard & Active Spirit Stable
│   ├── character_build_point_buy.qmd # Point buy character creation mechanics
│   ├── rules_and_downtime.qmd # Shinto-Musok spellcasting, drain math, & downtime protocols
│   ├── appendix_dossier.qmd  # Auto-generated tactical appendix dossier (from sr6 sync-all)
│   └── *.md                  # Narrative archive chapters (Ch 01–09+)
├── output/                   # Auto-generated exports (from sr6 sync-all)
│   ├── text/                 # Strict 76-column modular plain-text sheets
│   └── vtt/                  # Roll20 JSON & CommLink6/Genesis XML sheets
├── _quarto.yml               # Quarto book build configuration
├── pyproject.toml            # uv project configuration pulling sr6-core
└── .agents/
    ├── AGENTS.md             # Master workspace instructions & orchestrator protocols
    └── plugins.json          # Inherits Antigravity sr6-narrative-suite plugin
```

---

## 🔄 CommLink6 GUI Purchasing & Dual-Ledger Workflow

`sr6-core` provides automatic two-way roundtrips with CommLink6:

1. **In CommLink GUI (UUID & Stat Generation):**
   Add physical items, gear modifications, or foci directly inside CommLink's GUI interface (`~/CommLink6/player/myself/shadowrun6/<UUID>/Velvet.xml`). CommLink handles internal UUID generation, capacity slots, and stat math.
2. **In Quarto Books (`character_log.qmd` / `character_purchases.qmd`):**
   Log the exact financial transaction with your actual discounted cost paid:

   ```markdown
   * **Qi Focus (Rating 4) — Sharp Tongue:** `{python} inc('Nuyen', -12000)` `{python} inc('Karma', -8)` *(Smooth Operations p. 1)*
   * **Initiation (Channeling):** `{python} initiate("Channeling", coven_loyalty=Coven_Loyalty)`
   ```

3. **Automated Ecosystem Sync (`sr6 sync-all`):**
   Running `sr6 sync-all` (or `sr6 db sync-commlink`) reads your active CommLink GUI save file, evaluates your Quarto log to compute true available Karma (`karmaF`), spent Karma (`karmaI`), and Nuyen (`nuyen`), isolates base mission reward gains, and writes the updated XML back to CommLink without overwriting your GUI item edits.

---

## ⚙️ Multi-Agent Narrative Production & CLI Tools

All rules audits, character sheet generation, and narrative evaluations are managed via the `sr6` CLI (provided by `sr6-core`):

### 1. Unified 7-Axis Narrative Evaluator & Tabletop Ledger

```bash
# Run 7-axis evaluation on chapter prose calibrated to chapter tier (Tier 1: 9.0, Tier 2: 8.5, Tier 3: 8.0)
uv run sr6 evaluate "chapters/09_Heat.md" --tier 2

# Extract fired ammunition, damage taken, drain suffered, and rewards into YAML diffs
uv run sr6 ledger parse "chapters/09_Heat.md"

# Lint chapter prose for banned buzzwords, cognitive buffer verbs, and ellipses density (<= 0.6 / 300 words)
uv run sr6 lint "chapters/09_Heat.md"
```

### 2. Ecosystem Synchronization & CommLink6 Roundtrip

```bash
# Run deep audits, regenerate exports in output/, and patch active CommLink6 GUI saves
uv run sr6 sync-all

# Sync CommLink6 GUI player saves specifically
uv run sr6 db sync-commlink
```

### 3. Character Auditing & Export

```bash
# Deep item-by-item audit against master rules database
uv run sr6 characters audit velvet

# Export character sheet (Roll20, Plain-text VTT, Genesis XML, PDF card deck)
uv run sr6 export velvet --format=text_modular
uv run sr6 export velvet --format=pdf_deck
uv run sr6 export velvet --format=pdf_base
```

### 4. Story Continuity & Rules RAG Assistant

```bash
# Index campaign relationships, spirit states, and heatmaps
uv run sr6 continuity .

# Query Gemini AI Rules RAG with Velvet's active dossier context
uv run sr6 rag query "How does Focused Concentration interact with sustained Increase Attribute spells?" --char velvet

# Check Antigravity plugin status
uv run sr6 plugin status
```

### 5. Compile the Quarto Story Book

```bash
uv run quarto render
```

---

## 🔌 Antigravity Agent Plugin (`sr6-narrative-suite`) & MCP Tools

When working inside this repository, the Antigravity agent inherits specialized narrative capabilities and native MCP tools:

* `sr6_evaluate_draft(text_or_path, tier, char_id)`: Unified 7-axis evaluation and scorecard generation.
* `sr6_parse_combat_ledger(text_or_path)`: Prose combat extraction and proposed YAML patches.
* `sr6_search_rules(query)`: FTS5 rules lookups and item stat cards.
* `sr6_query_rag(prompt, char_id)`: Rules assistant with authority ranking.
* `sr6_lint_prose(file_path)`: Scans chapters for ellipses ceiling and buzzwords.
* `sr6_audit_character(char_id)`: Character creation and YAML validation.
* `sr6://` Live URI resources (`sr6://characters/velvet/master`, `sr6://campaign/contacts`, `sr6://rules/summary`).
