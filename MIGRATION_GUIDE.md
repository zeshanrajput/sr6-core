# Character Portfolio Migration & Refactoring Guide

This guide outlines the complete steps to clean up, refactor, and decouple derivative character repositories (`sr6yuriko`, `sr6velvet`, `sr6union`) to take full advantage of `sr6-core`.

---

## 1. What to Delete (Redundant Files & Folders)

To eliminate redundancy across character repositories, delete the following:

- 🗑️ **`.agents/skills/`**: Delete local duplicate skills (`sr6-rules`, `no-ai-slop`, `literary-analysis`, `continuity-tracker`, `axis-*`). Skills are now bundled in the **Antigravity Agent Plugin (`sr6-narrative-suite`)** and inherited globally (`sr6 plugin install`) or via `.agents/plugins.json` (`sr6 plugin init-repo .`).
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

## 5. User Environment & Path Customization

Users running `sr6-core` on different machines or with custom character rosters can easily configure paths via environment variables or `characters.yaml`:

- **Custom Character Rosters**: Add character entries to `characters.yaml` with custom names, repository folders, and master YAML filenames.
- **Environment Variable Overrides**:
  - `SR6_WORKSPACE_ROOT`: Path to code workspace directory (defaults to parent directory or `C:\GitHub`).
  - `COMMLINK_PLAYER_DIR`: Path to CommLink user saves directory (defaults to `~/CommLink6/player/myself/shadowrun6`).

---

## 6. Directory Structure Verification

Ensure the character repository matches the standard layout:

```text
sr6<char_id>/
├── <char_id>_master.yaml     # Master character dossier (authoritative YAML)
├── reference/                # Local project reference docs
│   └── voice_spec.md         # Character voice spec (extends sr6-core/reference/default_voice_spec.md)
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

## 7. Instantiating Character Voice Specifications (`reference/voice_spec.md`)

Each character repository MUST instantiate its own local voice specification at `reference/voice_spec.md`:

1. **Copy Starter Template**: Copy `sr6-core/templates/reference/voice_spec.md.template` into `reference/voice_spec.md` (or adapt from existing character repos like `sr6yuriko/reference/voice_spec.md`).
2. **Inheritance Header**: Ensure the top of the file explicitly declares inheritance:
   ```markdown
   Extends: sr6-core/reference/default_voice_spec.md
   ```
3. **Define Voice Schema**: Fill out the `voice_schema` block covering narrative POV, cognitive bias, vocabulary register & metaphor domains, primary/secondary sensory lens, emotional baseline/stress triggers, and syntax cadence.
4. **Define Chronological Growth Arcs (`arc_chronology`)**: Break character evolution into narrative eras to prevent retrospective flattening (e.g. early solitary survival vs mid-game alliances vs late-game stewardship).
5. **Define Chapter Tiers (`chapter_tiers`)**: Map chapters to Tier 1 Keystones (9.0/10 passing threshold), Tier 2 Narrative Evolution (8.5/10), and Tier 3 Atmospheric Bridges (8.0/10).
6. **Define Domain Vocabulary Rules**: Specify context-specific vocabulary rules for internal consciousness, mechanical action, and dialogue.
7. **Audio Narration & TTS Readability**: Enforce an ellipses ceiling of $\le 0.6$ per 300 words and natural spoken dialogue rhythm.

---

## 8. Quarto Book Configuration (`_quarto.yml`)

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

## 9. Antigravity Agent Plugin Integration (`.agents/plugins.json`)

To enable the complete 7-panel evaluation suite, narrative director rules, and anti-slop tools in a character repository:

### Option A: Initialize Repo Plugin Configuration (Workspace Scope)
Run the SR6 CLI tool inside your character repository:
```powershell
sr6 plugin init-repo .
```
This generates `.agents/plugins.json`:
```json
{
  "inherits": [
    {
      "path": "../sr6-core/.agents/plugins/sr6-narrative"
    }
  ]
}
```

### Option B: Machine-Wide Global Plugin
Install the plugin globally once to enable it automatically in all Shadowrun workspaces:
```powershell
sr6 plugin install --symlink
```

### CLI Diagnostic Reference in Agent Workflows:
```markdown
- Plugin Status: Run `sr6 plugin status`
- 7-Axis Narrative Evaluator: Run `sr6 evaluate "chapters/<file>.qmd" --tier 2`
- Combat Ledger & Ammo Extraction: Run `sr6 ledger parse "chapters/<file>.qmd"`
- Rules Verification: Run `sr6 rag query "<query>"` or `sr6 search "<item>"`
- Prose Linter: Run `sr6 lint "chapters/<file>.qmd"`
- Story Continuity Audit: Run `sr6 continuity .`
- Export Sheets: Run `sr6 export <char_id> --format=xml|vtt|roll20`
- CommLink GUI Save Sync: Run `sr6 db sync-commlink`
- Narrative Production: Invoke `narrative-director` orchestrator for 7-sub-agent drafting & self-correction
```

### Native Agent Tools via MCP (`mcp_config.json`):
When the plugin is active, the Antigravity agent has direct access to:
- `sr6_evaluate_draft(text_or_path, tier, char_id)`: Unified 7-axis evaluation and scorecard generation.
- `sr6_parse_combat_ledger(text_or_path)`: Prose combat extraction and proposed YAML patches.
- `sr6_search_rules(query)`: FTS5 rules lookups and item stat cards.
- `sr6_query_rag(prompt, char_id)`: Rules assistant with authority ranking.
- `sr6_lint_prose(file_path)`: Scans chapters for ellipses ceiling and buzzwords.
- `sr6_audit_character(char_id)`: Character creation and YAML validation.
- `sr6://` Resources: Live URI links to `sr6://characters/<char_id>/master`, `sr6://campaign/contacts`, and `sr6://rules/summary`.

---

## 10. SRM Canonical Contacts Registry & Advancement Ledger

Character repositories should leverage `sr6core.contacts` and `sr6core.log_engine`:

1. **Official SRM Appendix C Canonical Contacts**:
   - Canonical contacts (Seattle 2081, New Orleans 2083, Kentucky Fried Shadows 2) have hardcoded, immutable Connection ratings and exact SRM Guide text descriptions.
   - Initialized automatically via `contact("Brynne Taggart", ...)` or `yuriko_master.yaml`.
2. **Non-Canonical Mission Contacts**:
   - Connection and Loyalty can be raised through mission actions and downtime.
   - Description is locked upon first naming.
3. **Favor Points & Automatic Loyalty Progression**:
   - Passing `fp=N` accumulates favor points on the contact.
   - The engine automatically promotes Loyalty by +1 whenever $FP \ge \text{Loyalty} + 1$ (spending $L+1$ FP per promotion).
4. **Inline Quarto Markdown Returns**:
   - Inline `{python} contact(...)` calls return clean, compact Markdown strings (e.g. `**Piotr Krolik** (NOLA Vory) [C:4 L:1] (+1 Favor)` or `**Renée Martin** (+3 Favor → Auto-Promoted to Loyalty 2!)`).
5. **Career Lifetime Ledgers**:
   - **Lifetime Karma**: Tracks all earned in-game Karma + initial chargen carryover.
   - **Lifetime Nuyen**: Tracks all earned in-game Nuyen + initial chargen carryover.
   - Excludes all internal character creation point-buy allocations.

---

## 11. Plain-Text Modular Sheet Standards (76-Column Limit)

All character text exports in `output/text/` strictly adhere to a maximum line length of **76 columns** (matching the visual divider width):

- `<char_id>_base.txt`: 1-page dossier with identity, attributes, effective dice pools, and defenses.
- `<char_id>_contacts.txt`: Regional contacts directory with canonical descriptions and history.
- `<char_id>_combat.txt`: Weapons, firing modes, attack ratings (AR), and ballistic armor.
- `<char_id>_inventory.txt`: Matrix devices, categorized software (Basic, Hacking, Rigging, Autosoft, Commlink), munitions, and gear.
- `<char_id>_vehicles.txt`: Vehicles and drones with single-line abbreviations and inhabited action pools.
- `<char_id>_powers.txt`: Complex Forms, Spells, Adept Powers, and Metamagic/Echoes.
- `<char_id>_ledger.txt`: Financial transactions and career totals.

### Software De-Duplication & Clean Autosoft Suffixes:
- Strips redundant `"Autosoft"` suffixes from autosoft listings while displaying ratings (e.g. `Biotech R9`, `Clearsight R9`).
- Categorizes commlink applications (`Facial Scanner`, `P-ICE Spines`, `Social HUD`, etc.) under `Commlink:` software rather than physical gear.

---

## 12. Dynamic Domain Rules Chapter Integration

Replace static markdown tables in domain rules chapters with dynamic renderers from `sr6core.rules_engine`:

1. **Combat Chapter (`rules_combat.qmd`)**: `get_weapon_attack_table(char_id)`
2. **Matrix Chapter (`rules_matrix.qmd`)**: `get_matrix_action_table(char_id)` and `get_matrix_asdf_derivation_table(char_id)`
3. **Drones Chapter (`rules_drones.qmd`)**: `get_drone_statblock_table(char_id, drone_name)` and `get_drone_action_table(char_id, mode)`
4. **Sprites & Emergence Chapter (`rules_sprites.qmd`)**: `get_sprite_action_table(char_id)` and `get_sprite_commands_table(char_id)`

---

## 13. Standardized Pydantic Stat Blocks & Dynamic Weapon Arrays

`sr6-core` includes a full Pydantic stat block engine (`sr6core.models` & `sr6core.vault.statblock_parser`) supporting typed models across all 9 tabletop entity categories (`WeaponStatBlock`, `ArmorStatBlock`, `VehicleStatBlock`, `SpellStatBlock`, `ComplexFormStatBlock`, `SpriteStatBlock`, `SpiritStatBlock`, `AIStatBlock`, `NPCStatBlock`).

### Key Capabilities for Character Portfolios:
1. **Dynamic Post-Modification Weapon Arrays (`calculate_modified_weapon`)**:
   Automatically calculates modified Attack Ratings (+2 for active Smartlink, +2 Attack Dice for Smartguns), extended barrel range extensions, expanded magazine capacities, and ammunition DV modifiers (APDS, Explosive, Gel, Stick-n-Shock) without manual spreadsheet calculation.
2. **Dual Callout & Plain-Text Formatters**:
   - **Quarto Callouts (`format_statblock_markdown`)**: Renders clean, copy-pasteable callouts for character narrative chapters and rules appendices:
     ```markdown
     ::: {.callout-note icon=false title="⚔️ WEAPON: ARES PREDATOR VI (HEAVY PISTOL)"}
     **DV:** 3P | **Modes:** SA/BF | **Attack Ratings:** 12/12/10/-/- | **Ammo:** 15(c)
     *Mods: Internal Smartgun System (+2 AR, +2 Attack Dice)*
     :::
     ```
   - **76-Column ASCII Bordered Tables (`format_statblock_plaintext`)**: Produces strict 76-column tables for modular text exports (`output/text/<char>_combat.txt`).
3. **Automated Appendix Generation**:
   `sr6 sync-all` automatically builds a tactical appendix dossier (`chapters/character_dossier_appendix.qmd`) in each character repository, detailing full tactical profiles for all installed cyberware, modified weapons, and gear arrays.

---

## 14. Final Ecosystem Synchronization

From `sr6-core`, run the ecosystem synchronizer:

```bash
sr6 sync-all
```

This will automatically perform deep item audits across all character portfolios, calculate post-modification weapon arrays, regenerate VTT/JSON/XML/PDF/Text sheets into `output/`, patch active CommLink6 GUI player saves, and build Quarto tactical appendix dossiers.
