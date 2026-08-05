# Character Portfolio Migration & Refactoring Guide

This guide outlines the complete steps to clean up, refactor, and decouple derivative character repositories (`sr6yuriko`, `sr6velvet`, `sr6union`) to take full advantage of `sr6-core`.

---

## 1. What to Delete (Redundant Files & Folders)

To eliminate redundancy across character repositories, delete the following:

- 🗑️ **`.agents/skills/`**: Delete local duplicate skills (`sr6-rules`, `no-ai-slop`, `literary-analysis`, `continuity-tracker`). All skills are now centrally executed from `c:\GitHub\sr6-core\.agents\skills\`.
- 🗑️ **Local `shadowrun_rules.db` / `rules_vault/`**: Remove any local copy of the rules database or rules vault files. The rules database is now centralized at `~/.sr6/rules_index.db`.
- 🗑️ **Legacy Python Engines**: Delete local Python helper scripts (`linter.py`, `log_engine.py`, `continuity_engine.py`, `rules_engine.py`, `narration.py`). Use `sr6` CLI subcommands instead.

---

## 2. Refactoring Embedded Python Code in Quarto Books (`chapters/*.qmd`)

Previously, Quarto session logs often defined their own Python state functions or setup blocks. 

### Recommended Quarto Refactor:
1. **Clean Top-of-File Import Cell**: At the top of `chapters/character_log.qmd`, replace inline helper definitions with:
   ```markdown
   ```{python}
   #| echo: false
   from sr6core.log_engine import inc, inc_many, contact, add_sprite, add_rep, start_mission
   ```
   ```
2. **Keep Inline Calls Minimal & Clean**:
   - Rewards: `{python} inc('Karma', 7)`, `{python} inc('Nuyen', 9500)`
   - Contacts: `{python} contact("Sigrún", connection=5, fp=2, type_name="Shadowrunner")`
   - Sprites: `{python} add_sprite('Sprite-M21', 7, 'Modular', 'Shield')`
   - Reputation: `{python} add_rep('UNL', 1)`

`sr6core.log_engine` automatically handles all state evaluation, Karma math, Nuyen running totals, and active sprite counts across all files!

### 2.1 Submersion Grade & Echo Rules in Log Files
- **Base Submersion Grade**: Initialize baseline Submersion Grade at chargen using `assign("Submersion_Grade", 2)` (or character starting grade).
- **Stream Path Powers**: Do NOT increment Submersion Grade for path powers gained through stream advancement (e.g. *Hybrid Sprites* from Technoshaman stream).
- **Earned Echoes**: Increment Submersion Grade only when logging earned submersions:
  ```markdown
  * *Submersion - Living Network:* `{python} inc_many(('Karma', -11-Submersion_Grade), ('Submersion_Grade', 1))`
  ```

---

## 3. GitHub Pages CI/CD & `pyproject.toml` Git Dependency

When publishing character Quarto books via GitHub Actions (`publish.yml`), relative workspace dependencies (`path = "../sr6-core"`) fail on CI runners because sibling repositories are not checked out.

### Resolution:
Configure `pyproject.toml` in character repositories to pull directly from the master Git branch:

```toml
[tool.uv.sources]
sr6-core = { git = "https://github.com/zeshanrajput/sr6-core.git", branch = "master" }
```

Running `uv sync` locally and on GitHub Actions seamlessly builds `sr6-core` from Git without requiring relative directory pathing.

---

## 4. CommLink6 GUI Player Save Sync & Dual-Ledger Workflow

`sr6-core` provides automatic two-way roundtrips with CommLink6:

1. **Player Save Location**: CommLink GUI saves live player files at `~/CommLink6/player/myself/shadowrun6/<UUID>/<CharName>.xml`.
2. **GUI Item Edits**: Tweak gear, purchase items, or modify drones directly inside CommLink's GUI (generating internal UUIDs and stat blocks).
3. **Quarto Financial Ledger**: Log exact transactions in `character_log.qmd` with custom discounts (*Smile for the Camera*, DIY rigger 50% work, contact haggling).
4. **Automated Sync (`sr6 sync-all` or `sr6 db sync-commlink`)**:
   - Updates `karmaF` (karmaFree / available Karma) and `karmaI` (karmaInvested / spent Karma).
   - Updates available Nuyen balance (`nuyen="..."`).
   - Standardizes official SRM contacts with Appendix C defaults.
   - Isolates base mission gains into `<reward>` tags (`<title>` & `<gamemaster>` child elements).
   - Formats reward dates as full ISO-8601 timestamps (`YYYY-MM-DDTHH:MM:SS.000Z`).

---

## 4. User Environment & Path Customization

Users running `sr6-core` on different machines or with custom character rosters can easily configure paths via environment variables or `characters.yaml`:

- **Custom Character Rosters**: Add character entries to `characters.yaml` with custom names, repository folders, and master YAML filenames.
- **Environment Variable Overrides**:
  - `SR6_WORKSPACE_ROOT`: Path to code workspace directory (defaults to parent directory or `C:\GitHub`).
  - `COMMLINK_PLAYER_DIR`: Path to CommLink user saves directory (defaults to `~/CommLink6/player/myself/shadowrun6`).

---

## 5. Directory Structure Verification

Ensure the character repository matches the standard layout:

```text
sr6<char_id>/
├── <char_id>_master.yaml     # Master character dossier (authoritative YAML)
├── chapters/                 # Quarto narrative story book
│   ├── index.qmd             # Book intro & character background
│   ├── twenty_questions.qmd  # Shadowrun 20 Questions backstory questionnaire
│   ├── character_log.qmd     # Campaign narrative chapters & session logs
│   └── character_purchases.qmd # Transaction ledgers
├── output/                   # Auto-generated exports (from sr6 sync-all)
│   ├── <char_id>_sheet.json  # Roll20 JSON sheet
│   ├── <char_id>_sheet.txt   # Plain-text VTT sheet
│   └── <char_id>_sheet.xml   # 100% CommLink6 / Genesis XML sheet
└── _quarto.yml               # Quarto book build configuration
```

---

## 6. Quarto Book Configuration (`_quarto.yml`)

Update `_quarto.yml` under `book.chapters`:

```yaml
book:
  title: "Shadowrun 6e Narrative Book"
  chapters:
    - chapters/index.qmd
    - chapters/twenty_questions.qmd
    - chapters/character_log.qmd
    - chapters/character_purchases.qmd
```

---

## 7. Agent Instructions (`.agents/AGENTS.md`)

Update instructions in `.agents/AGENTS.md` to reference `sr6` CLI subcommands:

```markdown
- Rules Verification: Run `sr6 rag query "<query>"` or `sr6 search "<item>"`
- Prose Linter: Run `sr6 lint "chapters/<file>.qmd"`
- Story Continuity Audit: Run `sr6 continuity .`
- Export Sheets: Run `sr6 export <char_id> --format=xml|vtt|roll20`
- CommLink GUI Save Sync: Run `sr6 db sync-commlink`
```

---

## 8. Final Ecosystem Synchronization

From `sr6-core`, run the ecosystem synchronizer:

```bash
sr6 sync-all
```

This will automatically perform deep item audits, regenerate VTT/JSON/XML sheets into `output/`, patch active CommLink6 GUI player saves, and build the live Quarto dossier appendix for each character repo!
