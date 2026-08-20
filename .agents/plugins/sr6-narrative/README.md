# Shadowrun 6e Narrative Suite Plugin (`sr6-narrative`)

An Antigravity Agent Plugin providing the complete multi-agent narrative generation, evaluation, rules verification, and state tracking framework for Shadowrun 6th Edition character portfolios.

---

## Included Customizations

### 1. Rules (`rules/`)
* **`narrative-director.md`**: Master Orchestrator workflow implementing the 6-stage autonomous narrative drafting, 7-panel evaluation panel, tier-calibrated quality thresholds (Tier 1/2/3), self-correction loop, and CLI diagnostics.

### 2. Evaluation Skills (`skills/`)
1. **`axis-voice-internality`**: Audits character voice fidelity, POV integrity, vocabulary matrix, sensory lens, and era calibration against `reference/voice_spec.md`.
2. **`axis-pacing-structure`**: Evaluates 4-beat structure, entry/exit discipline, paragraph braiding cadence, and action-to-exposition balance (80/20).
3. **`axis-agency-motivation`**: Verifies proactive, consequential protagonist choices and drive alignment.
4. **`axis-worldbuilding-grit`**: Audits dystopian texture, megacorporate omnipresence, AR clutter, and street grit without info-dumping.
5. **`no-ai-slop`**: 23 anti-slop rules, forbidden terms redlines, affirmative staging, and TTS fluency.
6. **`continuity-tracker`**: Cross-checks ammo/nuyen balances, damage tracks, contacts, and state diff generation against `character_master.yaml`.
7. **`sr6-rules`**: SR6 mechanics (Edge, Matrix actions, spell drain, modifiers) accuracy via Gemini RAG rules vault.
8. **`literary-analysis`**: Speculative fiction prose chisel refactoring and quality scoring.

### 3. Hooks (`hooks.json`)
* Configurable lifecycle hooks for automated prose linting and diagnostic validation.

### 4. Native MCP Server Tools (`mcp_config.json`)
Exposes direct agent tools implemented in `sr6core.mcp`:
* **`sr6_search_rules(query)`**: Instant FTS5 lookup for spells, qualities, cyberware, weapons, and gear stats with book citations `[Book, Page]`.
* **`sr6_query_rag(prompt, char_id)`**: AI rules reference assistant with SRM 4-level authority hierarchy and runner dossier context.
* **`sr6_lint_prose(file_path)`**: Scans `.qmd` files for ellipses density ($\le 0.6$ budget), forbidden AI slop buzzwords, and structural issues.
* **`sr6_audit_character(char_id)`**: Item-by-item character creation & YAML state validator.
* **`sr6_check_continuity(repo_path)`**: Verifies campaign karma, nuyen, ammo, and contacts across chapter logs.
* **`sr6_get_item_card(category, item_id)`**: Formats and returns enriched item reference card markdown.

---

## Installation & Consumption in Character Repositories

### Option A: Global Installation (Recommended)
Install the plugin into your machine's global Antigravity config (`~/.gemini/config/plugins/`):
```powershell
sr6 plugin install
```
Once installed, the plugin is active across **all** Shadowrun character workspaces on your system.

### Option B: Workspace Inheritance (`.agents/plugins.json`)
In a character repository (e.g. `sr6yuriko`, `sr6velvet`, `sr6union`), create `.agents/plugins.json`:
```json
{
  "inherits": [
    {
      "path": "../sr6-core/.agents/plugins/sr6-narrative"
    }
  ]
}
```
