# Workspace Agent Instructions: sr6velvet (Velvet Portfolio)

This document defines character-specific bindings and constraints for **Velvet (Kim Jin-Young)** in the `sr6velvet` repository. Core workflow orchestration, the 6-stage lifecycle, 7-axis evaluation metrics, and anti-slop rules are inherited directly from the **`sr6-narrative-suite`** plugin ([`.agents/plugins.json`](file:///c:/GitHub/sr6velvet/.agents/plugins.json)).

---

## 1. Authoritative Character State & Master Documents

When executing narrative generation, evaluation, or state tracking for Velvet, bind to the following workspace files:

| Dimension | Primary Workspace File | Purpose |
| :--- | :--- | :--- |
| **Character Dossier** | [`velvet_master.yaml`](file:///c:/GitHub/sr6velvet/velvet_master.yaml) | Authoritative tabletop play state (attributes, skills, spells, adept powers, inventory, karma, nuyen balances). |
| **Voice Specification** | [`reference/voice_spec.md`](file:///c:/GitHub/sr6velvet/reference/voice_spec.md) | Character voice rules, somatic shift discipline, TTS fluency, domain vocabulary, and chapter tier calibrations (Extends `sr6-core/reference/default_voice_spec.md`). |
| **Philosophical Framework** | [`reference/philosophical_framework.md`](file:///c:/GitHub/sr6velvet/reference/philosophical_framework.md)<br>[`reference/karmic_persona_log.md`](file:///c:/GitHub/sr6velvet/reference/karmic_persona_log.md) | Metaphysical grounding of the Thousand Lives (*Anatta*, *Mansin*, *Upāya*, *Kagami*) and master registry of lived personas & somatic shift mechanics. |
| **Active Story Arcs** | [`reference/story_arc1.md`](file:///c:/GitHub/sr6velvet/reference/story_arc1.md)<br>[`reference/story_arc2.md`](file:///c:/GitHub/sr6velvet/reference/story_arc2.md) | Arc 1: *Manufactured Solace & The Honeytrap* (Ch 01–08)<br>Arc 2: *The Sovereign Underground* (Ch 09–18+) |
| **Story Continuity** | [`reference/story_continuity.md`](file:///c:/GitHub/sr6velvet/reference/story_continuity.md) | Continuity index, contact favor points, and entity heatmaps maintained via `sr6 continuity .`. |
| **Quarto Narrative Book** | [`chapters/`](file:///c:/GitHub/sr6velvet/chapters/) & [`_quarto.yml`](file:///c:/GitHub/sr6velvet/_quarto.yml) | Published Quarto story anthology and modular dossier chapters. |

---

## 2. Character-Specific Constraints & Somatic Rules

All narrative drafting, editing, and evaluation in this workspace must enforce these character-specific rules:

### A. Persona & Biological Pronoun Discipline

Pronouns and demeanor are strictly locked to Velvet's active biological persona:

- **Lee Ji-yoo**: `she/her` (soft, algorithmic elegance, high-fashion face).
- **Tanaka Ryo**: `he/him` (clean corporate authority, sharp masculine presence).
- **Mei Jing**: `she/her` (Cantonese triad/commercial persona).
- **Zhang Wei**: `he/him` (calm senior Cantonese freight expediter, unhurried veteran authority).
- **Leung Hoi-ching**: `she/her` (grounded, low-rasping Cantonese, working-class dockside persona).
- **Kim Jin-Young (Un-sculpted)**: `he/they` or raw baseline self.

### B. Somatic Reality of Cosmetic Control (R2)

- Shifting between personas carries a heavy visceral tax: bone cartilage resetting with wet clicks, dull metallic heat behind the jaw, shortened or broadened ribcages, and localized DNA re-keying.
- Beneath every sculpted mask lies the un-sculpted obsidian iris baseline of his birth heritage.
- Never portray physical transformation as instantaneous, painless, or effortless shape-shifting.

### C. Charisma 10 (14) Horror & Engineered Gravity

- Treat Charisma 10 (14 with buff spells) as an uncanny, suffocating psychological pressure—the pinnacle of unrestricted corporate engineering.
- Avoid smutty or pulp-romance tropes. Velvet's central tragedy is that he can never know if anyone's affection, pity, or compliance is authentic, or merely their nervous system collapsing into his manufactured biological gravity.

### D. Shinto-Musok Astral Phenomenology

- Describe magic as spirit ribbons, kami whispers, talismanic paper foci, and subtle emotional hue shifts in metahuman auras.
- Visceral drain taxation must be grounded in physical exhaustion: dry throat, bone fatigue, and metabolic strain.

### E. The Path of the Thousand Lives (*Mansin* & *Upāya*)

- Respect the 3-phase progression from identity erasure trauma (*Sinbyeong*) to the composite mosaic (*Echo phenomenon*) and sovereign emanation (*Upāya* / *Mansin*).
- Past personas are not disposable lies; each contributes a permanent neuro-somatic layer of human wisdom, virtue, and coping capacity. (See [`reference/philosophical_framework.md`](file:///c:/GitHub/sr6velvet/reference/philosophical_framework.md)).

---

## 3. Workspace Diagnostic Commands & MCP Resources

When auditing character files or evaluating drafts, use the following workspace-bound commands and MCP tools:

```bash
# Character & Tabletop State Audit
uv run sr6 characters audit velvet

# Chapter Prose Linter & Anti-Slop Audit
uv run sr6 lint "chapters/<chapter_file>.md"

# 7-Axis Narrative Evaluator (Tier 1: 9.0, Tier 2: 8.5, Tier 3: 8.0)
uv run sr6 evaluate "chapters/<chapter_file>.md" --tier 1|2|3

# Tabletop Action & Combat Ledger Extractor
uv run sr6 ledger parse "chapters/<chapter_file>.md"

# Story Continuity Indexer
uv run sr6 continuity .

# Ecosystem Sync & CommLink6 GUI Save Patching
uv run sr6 sync-all
```

### Native MCP Resources

- `sr6://characters/velvet/master`: Live character sheet and dossier data.
- `sr6://campaign/contacts`: Campaign contact registry and favor point balances.
- `sr6://rules/summary`: Summary of core rules and authority citations.
