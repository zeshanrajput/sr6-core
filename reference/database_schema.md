# Shadowrun 6e Rules Database & Schema Reference

This reference documents the centralized SQLite rules database, table catalog, column definitions, and CLI inspection tools for `sr6-core`.

---

## 1. Database Location & Architecture

* **Primary Active Database**: Located at `~/.sr6/rules_index.db` (centralized user profile directory).
* **Environment Override**: `SR6_RULES_DB_PATH` can point to an alternative database if needed.
* **Workspace Cleanliness**: Do **not** create or expect `.db` or `.sqlite` files in the repository root. All temporary or decoy databases in the root are ignored via `.gitignore` and removed.
* **CommLink6 Integration**: The database is compiled from CommLink6 XML datasets, official SRM FAQ documents, and the atomized 20,082-chunk Shadowrun Rules Vault.

---

## 2. CLI Inspection & Query Tools (No Python Gymnastics!)

Never write one-off `python -c` scripts with fragile string escaping to query rules or tables. Use the native `sr6 db` CLI commands:

### A. Run SQL Queries
```bash
# General query (Rich table output)
uv run sr6 db query "SELECT id, name, cost, essence, capacity FROM ref_cyberware WHERE name LIKE '%Cyberarm%'"

# SQL alias
uv run sr6 db sql "SELECT count(*) AS total_rules FROM rules"

# Agent & Markdown mode (--compact outputs a clean markdown table)
uv run sr6 db query "SELECT id, name, category, cost, avail FROM ref_weapons WHERE category = 'Heavy Pistols' LIMIT 5" --compact

# JSON or CSV output
uv run sr6 db query "SELECT * FROM ref_actions WHERE category = 'Matrix'" --json
uv run sr6 db query "SELECT id, name, cost, avail FROM ref_gear WHERE category = 'Commlinks'" --csv
```

### B. Inspect Table Schemas
```bash
# List all tables with row counts and sample columns
uv run sr6 db schema

# View detailed column definitions, data types, primary keys, and a sample row for any table
uv run sr6 db schema ref_cyberware
uv run sr6 db schema ref_weapons
uv run sr6 db schema rules
```

---

## 3. Complete Table Catalog

| Table Name | Rows | Description & Key Columns |
| :--- | :--- | :--- |
| **`rules`** | 20,082 | Official rules text chunked from 35+ books. Columns: `id`, `source`, `chapter`, `topic`, `authority_level`, `tags`, `status`, `overrides`, `content`, `page`. |
| **`rules_fts`** | 20,082 | SQLite FTS5 full-text search index matching against `id`, `topic`, `tags`, `source`, and `content`. |
| **`ref_cyberware`** | 435 | Augmentations, cyberlimbs, bioware, and geneware. Columns: `id`, `name`, `category`, `essence`, `capacity`, `cost`, `avail`, `source`, `raw_xml`, `modifiers_json`, `srm_status`. |
| **`v_cyberware_grades`** | 435 | Pre-calculated view of Standard, Used, Alphaware, and Betaware costs, essence discounts, and availability modifiers. |
| **`ref_weapons`** | 827 | Firearms, melee weapons, explosives, and heavy weapons. Columns: `id`, `name`, `category`, `damage`, `ap`, `attack_rating`, `modes`, `ammo`, `cost`, `avail`, `source`, `mounts`, `modifiers_json`, `srm_status`. |
| **`ref_gear`** | 3,045 | Tools, armor, sensors, electronics, commlinks, ammunition, medical gear. Columns: `id`, `name`, `category`, `cost`, `avail`, `source`, `raw_xml`, `srm_status`, `modifiers_json`. |
| **`ref_qualities`** | 710 | Positive and negative qualities. Columns: `id`, `name`, `karma`, `quality_type` (Positive/Negative), `max_rating`, `source`, `raw_xml`, `modifiers_json`, `srm_status`. |
| **`ref_spells`** | 188 | Awakened spells. Columns: `id`, `name`, `category`, `drain`, `range`, `duration`, `source`, `raw_xml`, `modifiers_json`, `srm_status`. |
| **`ref_complex_forms`** | 42 | Technomancer complex forms. Columns: `id`, `name`, `fade`, `duration`, `target`, `source`, `raw_xml`, `modifiers_json`. |
| **`ref_adept_powers`** | 95 | Physical Adept powers. Columns: `id`, `name`, `cost` (Power Points), `max_rating`, `source`, `raw_xml`, `modifiers_json`, `srm_status`. |
| **`ref_vehicles`** | 1,138 | Groundcraft, aircraft, watercraft, and drones. Columns: `id`, `name`, `category`, `handling`, `speed`, `accel`, `body`, `armor`, `sensor`, `seats`, `cost`, `avail`, `source`, `modifiers_json`. |
| **`ref_programs`** | 79 | Basic and cyberdeck software programs. Columns: `id`, `name`, `category`, `cost`, `source`, `raw_xml`, `modifiers_json`. |
| **`ref_actions`** | 22 | Major and Minor tactical, matrix, and magic actions. Columns: `id`, `name`, `action_type`, `category`, `test`, `opposed`, `threshold`, `description`, `source`. |
| **`ref_packs`** | 867 | Pre-assembled character, weapon, armor, and cyberware PACKs from Sixth World Companion. Columns: `id`, `name`, `category`, `cost`, `essence`, `description`, `contents`, `alternate_grades_json`, `source`, `page`. |
| **`ref_status_effects`** | 19 | Status effects (Blind, Burning, Dazed, Hobbled, Prone, Stunned, etc.). Columns: `id`, `name`, `category`, `effect`, `duration`, `recovery_test`, `source`. |
| **`ref_edge_boosts`** | 12 | Official Edge actions and expenditures (Reroll 1 die, Buy hit, Add Edge to pool). Columns: `id`, `name`, `cost`, `timing`, `category`, `effect`, `source`. |
| **`ref_contacts`** | 36 | Official SRM contacts. Columns: `id`, `name`, `connection`, `archetype`, `region`, `types`, `uses`, `source`, `city`, `season`. |
| **`srm_rulings`** | 8 | Campaign exceptions and FAQ rulings from the SRM FAQ and Guidebook. Columns: `id`, `topic`, `category`, `rule_or_item_id`, `ruling`, `source`, `applies_to`, `status`. |

---

## 4. Query & Accessibility Cheat Sheet

### PACKs Catalog Lookups
```bash
# Look up PACK by name or category
uv run sr6 card pack "Excellence"
uv run sr6 db query "SELECT name, cost, essence, category FROM ref_packs WHERE category = 'Cyberlimbs'" --compact
```

### Raw Sourcebook Search (`converted_md/`)
```bash
# Search verbatim sourcebook chapters with book acronyms (6wc, bs, crb, hns, dc, fs, sw, cn, pp)
uv run sr6 source 6wc "Cyberarm: Excellence" --context 10
uv run sr6 source bs "Bulk Modification"
```

### Cyberlimb & Augmentation Mathematics Calculator
```bash
# Calculate cyberlimb essence, cost, and capacity with Adapsin and enhancements
uv run sr6 calc limb --limb cyberarm --grade used --adapsin --agi 4
uv run sr6 calc limb --limb cyberleg --grade used --adapsin --agi 4 --bulk 4
```

### Tabletop Subsystem Rulesheets
```bash
# Display core rules cheat sheets
uv run sr6 cheat matrix
uv run sr6 cheat actions
uv run sr6 cheat monad
uv run sr6 cheat combat
```

### Find Cyberware Cost, Capacity, and Essence
```bash
uv run sr6 db query "SELECT name, essence, capacity, cost, avail, source FROM ref_cyberware WHERE name LIKE '%Nanohive%' OR name LIKE '%Hydraulic%'" --compact
```

### Compare Weapons in a Category
```bash
uv run sr6 db query "SELECT name, damage, attack_rating, modes, ammo, cost, avail FROM ref_weapons WHERE category = 'Heavy Pistols' ORDER BY cost DESC LIMIT 10" --compact
```

### Check Available Qualities for a Role
```bash
uv run sr6 db query "SELECT name, karma, quality_type, max_rating, source FROM ref_qualities WHERE name LIKE '%Techno%' OR name LIKE '%Monad%' OR name LIKE '%Analytical%'" --compact
```

### Lookup Specific Rule or Table by Topic
```bash
uv run sr6 db query "SELECT id, topic, source, page FROM rules WHERE topic LIKE '%Initiative%' OR topic LIKE '%Action%'" --compact
```

---

## 5. Finding Full Book Text in `converted_md/`

When a table or PACK is summarized or split across RAG chunks (such as Sixth World Companion character PACKs or detailed Body Shop modification tables), search the source markdown file directly:

* **Location**: `converted_md/` (contains 72 complete book conversions, e.g. `CAT28005_Sixth_World_Companion.md`, `CAT28007_Body_Shop.md`, `CAT28000S_SR6 Core City Edition Seattle.md`).
* **Tool to Use**: `grep_search` with `SearchPath="c:\\GitHub\\sr6-core\\converted_md"`.
* **Example**:
  Search for `## Cyberarm: Excellence` in `CAT28005_Sixth_World_Companion.md` to get the entire alternate grade cost table and verbatim source description.
