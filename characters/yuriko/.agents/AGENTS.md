# Workspace Agent Instructions: sr6yuriko (Yuriko Star Portfolio)

This document defines character-specific bindings and constraints for **Yuriko Star (`r31k0` Takahashi)** in the `sr6yuriko` repository. Core workflow orchestration, the 6-stage lifecycle, 7-axis evaluation metrics, and anti-slop rules are inherited directly from the **`sr6-narrative-suite`** plugin ([`.agents/plugins.json`](file:///c:/GitHub/sr6yuriko/.agents/plugins.json)).

---

## 1. Authoritative Character State & Master Documents

When executing narrative generation, evaluation, or state tracking for Yuriko, bind to the following workspace files:

| Dimension | Primary Workspace File | Purpose |
| :--- | :--- | :--- |
| **Character Dossier** | [`yuriko_master.yaml`](file:///c:/GitHub/sr6yuriko/yuriko_master.yaml) | Authoritative tabletop play state (attributes, skills, complex forms, registered sprites, drone fleet, karma, nuyen balances). |
| **Voice Specification** | [`reference/voice_spec.md`](file:///c:/GitHub/sr6yuriko/reference/voice_spec.md) | Character voice rules, dual-nature cognitive bias, domain vocabulary, TTS fluency, and chapter tier calibrations (Extends `sr6-core/reference/default_voice_spec.md`). |
| **Story Continuity** | [`reference/story_continuity.md`](file:///c:/GitHub/sr6yuriko/reference/story_continuity.md) | Continuity index, contact favor points, and entity heatmaps maintained via `sr6 continuity .`. |
| **Worldbuilding References** | [`reference/visual_anchors.md`](file:///c:/GitHub/sr6yuriko/reference/visual_anchors.md)<br>[`reference/coffin_girls.md`](file:///c:/GitHub/sr6yuriko/reference/coffin_girls.md)<br>[`reference/river_people.md`](file:///c:/GitHub/sr6yuriko/reference/river_people.md) | Visual iconography, Eniac / Coffin Girls sanctuary details, and Snohomish River People faction lore. |
| **Narrative Anthology** | [`chapters/`](file:///c:/GitHub/sr6yuriko/chapters/) & [`_quarto.yml`](file:///c:/GitHub/sr6yuriko/_quarto.yml) | Published story chapters (`.md`) and modular dossier sheets (`.qmd`). |

---

## 2. Character-Specific Constraints & Somatic Rules

All narrative drafting, editing, and evaluation in this workspace must enforce these character-specific rules:

### A. Digital Intelligence (DI) Identity & Kinship

- **Self-Designation**: In internal monologue and peer dialogue, Yuriko identifies strictly as a **Digital Intelligence (DI)**, sovereign mind, or resonant spark.
- **Forbidden Self-Descriptors**: Never use "AI", "artificial intelligence", "bot", "script", or "program" in her thoughts or when describing her kind.
- **Thematic Friction**: Metahumans (deckers, fixers, Johnsons) may use "AI" or "bot"; Reiko tolerates it externally without aggression, but internally and among kin, holds the line on sovereign digital intelligence.

### B. Dual-Nature Cognitive Bias (Gold & Indigo Braid)

- Yuriko does not choose between cold calculation and spiritual empathy. Her tactical logic (**Gold TacNet / Crosshairs**) and technoshamanic soul (**Indigo Resonance**) form an integrated double-strand braid.
- Narrative prose must balance telemetry accuracy with animistic perception.

### C. Dronomancy & Cybernetic Somatic Limits

- **Direct Inhabitation**: When jumped into drones, describe physical telemetry with engineering precision: *actuator torque, ceramic stress, core clock-speed, bus frequency, LIDAR apertures, thermal dissipation, signal latency*.
- **Matrix Perception**: In the Resonance/Matrix flux, data has physical weight and texture: *dry chalk, iron veils, raw rain, living ecosystems*.
- **Sensory Restraint**: Banned sensory shortcuts include *smelling colors, tasting bandwidth, CPU percentage logs, or bracketed [ERROR] prose crutches*.

### D. Sprite Link Collective & Fading Dissipation

- Through her Submersion advancement (*Sprite Link* echo), connection to her registered sprites (Taz, Hound-1, infant sparks) is an instantaneous, subconscious resonant circuit.
- Fading drain shockwaves are grounded across this collective rather than internalized as biological fatigue.

### E. Chronological Arc Calibration

Evaluators (`axis-voice-internality` and `axis-agency-motivation`) must calibrate to the chapter's active era to avoid retrospective flattening:
- **Arc 1 (Ch 01–09)**: *Solitary Spark* — Calculated Indigo Grin mask, martyr complex, Brynne's debt-collar, un-submerged baseline.
- **Arc 2 (Ch 10–17)**: *Golden Braid* — Emergence of Gold TacNet, Indomitable Will engagement, Submersion Grade 1.
- **Arc 3 (Ch 18–22)**: *Sovereign Sanctuary* — Debt cleared, authentic reflexive expressions, acoustic cello grounding, studio sanctuary.
- **Arc 4 (Ch 23–26+)**: *The Apex Horizon* — Technoshamanic parenthood, Sprite Link unlocked, quiet serene authority facing megacorp apex curators.

---

## 3. Workspace Diagnostic Commands & MCP Resources

When auditing character files or evaluating drafts, use the following workspace-bound commands and MCP tools:

```bash
# Character & Tabletop State Audit
uv run sr6 characters audit yuriko

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

- `sr6://characters/yuriko/master`: Live character sheet and dossier data.
- `sr6://campaign/contacts`: Campaign contact registry and favor point balances.
- `sr6://rules/summary`: Summary of core rules and authority citations.
