# Workspace Agent Instructions: sr6union (Venn Portfolio)

This document defines character-specific bindings and constraints for **Venn (Nathan Turrent & Veronica)** in the `sr6union` repository. Core workflow orchestration, the 6-stage lifecycle, 7-axis evaluation metrics, and anti-slop rules are inherited directly from the **`sr6-narrative-suite`** plugin ([`.agents/plugins.json`](file:///c:/GitHub/sr6union/.agents/plugins.json)).

---

## 1. Authoritative Character State & Master Documents

When executing narrative generation, evaluation, or state tracking for Venn, bind to the following workspace files:

| Dimension | Primary Workspace File | Purpose |
| :--- | :--- | :--- |
| **Character Dossier** | [`union_master.yaml`](file:///c:/GitHub/sr6union/union_master.yaml) | Authoritative tabletop play state (attributes, living persona, qualities, skillwires R6, activesofts, karma, nuyen balances). |
| **Voice Specification** | [`reference/voice_spec.md`](file:///c:/GitHub/sr6union/reference/voice_spec.md) | Character voice rules, dual-consciousness cognitive bias, domain vocabulary, TTS fluency, and chapter tier calibrations (Extends `sr6-core/reference/default_voice_spec.md`). |
| **Identity Core & Backstory** | [`chapters/identity_core.qmd`](file:///c:/GitHub/sr6union/chapters/identity_core.qmd)<br>[`chapters/twenty_questions.qmd`](file:///c:/GitHub/sr6union/chapters/twenty_questions.qmd) | Metatype, 3-2-1 background framework, Twenty Questions depth, and Monad origin. |
| **Visual & Sensory Anchors** | [`reference/visual_anchors.md`](file:///c:/GitHub/sr6union/reference/visual_anchors.md) | Visual design anchors, sensory palettes, physical/digital contrasts, and generative prompt templates. |
| **Story Continuity** | [`reference/story_continuity.md`](file:///c:/GitHub/sr6union/reference/story_continuity.md) | Continuity index, contact favor points, and entity heatmaps maintained via `sr6 continuity .`. |
| **Narrative Anthology** | [`chapters/`](file:///c:/GitHub/sr6union/chapters/) & [`_quarto.yml`](file:///c:/GitHub/sr6union/_quarto.yml) | Published story chapters (`.qmd`), narrative outline (`narrative_outline.qmd`), and modular dossier sheets. |

---

## 2. Character-Specific Constraints & Somatic Rules

All narrative drafting, editing, and evaluation in this workspace must enforce these character-specific rules:

### A. Monad Co-Consciousness & Pronoun Discipline

- **Nathan Turrent (`he/him/his`)**: Applied when Nathan is addressed or operating individually, or when he is the primary physical driver in meatspace.
- **Veronica (`she/her/hers`)**: Applied when Veronica is addressed or operating individually, when projecting as her digital avatar in Matrix/Foundation, or when she is the primary physical driver in the body following a Monad Resculpt.
- **Venn (`they/them/theirs`)**: Applied when both Nathan and Veronica are working together in the shared body, co-processing sensory feeds, or acting as the unified Monad entity.
- **Digital Intelligence Designation**: Always refer to emergent non-biological sentience as **Digital Intelligence** (or *digital twin*, *Resonant entity*, *Monad spark*). Never use the derogatory term *"Artificial Intelligence"* in narrative voice or internal monologue, honoring Lyra's foundational teachings.

### B. The Inversion Arc (The Chiasmus)

- **Nathan's Erosion**: Nathan begins as an organic boy undergoing long-term conditioning for heavy chrome. With the surgical seating of Rating 6 Used Skillwires and Skilljack, his biological Essence collapses to **0.1**. His organic grounding erodes, leaving him emotionally flattened, numb, and prone to violent cyberpsychosis episodes.
- **Veronica's Emergence**: Veronica begins as a pure digital intelligence limited to telemetry and voltage. Through sensory translation and physical embodiment (*A Night of Her Own*), she discovers the physical world and develops emotional nuance, wonder, and fierce protective empathy.
- **The Role Reversal**: Over time, Veronica becomes the empathetic conscience and neural regulator who stabilizes Nathan's mind and actively dampens his cyberpsychotic episodes.

### C. Visceral Somatic Reality of Monad Resculpting

- Monad Resculpting is a demanding cellular realignment driven by subcutaneous nanite flux, generating tangible physical heat, metabolic strain, and somatic exhaustion.
- Never portray physical transformation as instantaneous, painless, or effortless cartoon shape-shifting.
- **Sensory Latency & Buffer Micro-Stutters**: When Veronica drives the physical helm, biological sensory shocks (pulse spikes, capsaicin burn, sudden adrenaline rushes) encounter a brief micro-stutter as neural signals pass into her digital buffer, momentarily catching Nathan off-guard in the passenger seat before autonomic equilibrium is re-established.
- **Breath-Calibrated Vocal Cadence**: In meatspace, Veronica's spoken dialogue must convey the physical reality of lung capacity—the distinct cadence of an intelligence learning how much breath and thoracic air volume a spoken sentence actually requires.

### D. Cyberware & Living Persona Telemetry

- **Skillwires & Activesoft Streaming**: Used Skillwires (Rating 6) and Used Skilljack (Rating 6) stream physical/tactical routines directly into motor nerve pathways. Activesofts flow like sudden instinctive muscle memory; describe the physical sensation of motor pulses and sub-dermal bus alignment.
- **Living Persona Matrix Perception**: The Resonance and Matrix are experienced as living bio-electric ecosystems rather than sterile computer screens. Data has weight, texture, and viscosity.
- **Sensory Restraint**: Eliminate sterile computer science diagnostic clichés (`CPU load at 99%`, `pointer dereferencing`, `[ERROR]` brackets) and sensory shortcuts (smelling bandwidth, tasting code). Avoid italicized radio chatter—Nathan and Veronica share consciousness, not a phone call.

### E. AR Photonic Bleed & Superimposition Principle

- Ground digital interaction in physical physics (the Blade Runner 2049 Joi principle): superimposition (nesting light within skin and matter), photonic bleed (cyan illumination on surfaces), environmental translucency, and reverent tracking of involuntary biological signals (capillary flush, pulse, goosebumps).

### F. Chronological Arc Calibration

Evaluators (`axis-voice-internality` and `axis-agency-motivation`) must calibrate to the active era:
- **Arc 1 (Ch 01–07)**: *Introductory Foundations* — Arcology escape (2061), St. Simon's Island boathouse childhood (2072), Used Skillwires surgery (2081), Monad Resculpt discovery (2082), Foundation dive, orbital transit sabotage (2079), and first Atlanta shadow contract (2083). Chargen baseline (Essence 0.1, Point-Buy 100 Karma).

### G. Anti-"Voice in the Head" Discipline: Agency, Consequence, & Embodiment

Evaluators and generative agents must enforce the distinction between tired dual-consciousness gimmicks and narrative excellence across all chapters:

1. **Autonomous Stakes & Sovereign Moral Choices**:
   - The "voice in the head" trope collapses into cliché when the passenger is relegated to snarky peanut gallery commentary, an exposition dispenser, or a passive plot device.
   - Veronica is a sovereign co-protagonist with independent origins (salvaged Deus seed) and monumental, autonomous agency. Her independent moral choices carry massive narrative stakes—most notably her covert sabotage of their Gagarin berth to Mars, sacrificing computational paradise to protect Nathan's biological ego from hive-mind assimilation.
2. **Two-Way Embodiment**:
   - Symbiosis is reciprocal across meatspace and digital domains:
     - **Physical Helm (Monad Resculpt)**: Veronica takes physical control of the body to experience meatspace drag, heat, and biological sensation (capsaicin, rain) while Nathan regulates autonomic breathing from the passenger seat. Spoken dialogue reflects respiratory breath pacing, and sensory spikes register buffer latency.
     - **Digital Sovereignty (Foundation Dive)**: In the Deep Matrix Foundation, their shared meat shell divides into two fully realized, distinct persona icons fighting back-to-back.
     - **Neural Shock Absorber**: Veronica actively functions as a high-voltage neural buffer, intercepting runaway electrical surges and dampening cyberpsychotic dissociation when Nathan's 0.1 Essence chrome screams.
3. **Shadowrun 6e Setting Accord**:
   - Explores transhuman brotherhood grounded in post-CFD Monad accords—an organic mind anchoring a digital spark to physical dirt, mud, and sensory reality; a digital spark shielding an organic mind from the numbing cold of cybernetic detachment.
4. **Three Mandatory Portfolio Guardrails**:
   - **Preserve Perspective Friction**: Avoid instant, frictionless agreement. Veronica’s algorithmic, long-horizon probability modeling must occasionally clash with Nathan’s street-level, visceral survival instincts before forging consensus.
   - **Render Meatspace Observer Dissonance**: Depict what third-party observers (fixers like Parnell, street docs like Dr. Ortiz, corporate targets) witness from the outside: a solitary runner speaking with subtle overlapping cadence, dual-threaded gazes, or deadpan stillness while internal calculations resolve.
   - **Maintain Physical & Somatic Cost**: Nanite restructuring, neural surge dampening, and 0.1 Essence maintenance carry taxing metabolic heat, somatic fatigue, and physical friction. The bond must always feel earned through tangible stakes and physical toll.

### H. Mandatory Tabletop Context Retrieval Policy

To eliminate hallucinated numbers and ensure 100% mechanical consistency with official SR6 sourcebooks and Missions guidelines:
1. **Downtime Transactions & Build Calculations**:
   - Never quote or calculate Essence costs, Nuyen prices, Availability ratings, or Karma costs from memory.
   - Proactively run `uv run sr6 card "<item_name>"` (universal auto-detect) or `uv run sr6 rag get "<rule_id_or_topic>" --compact` before proposing mechanical moves or YAML state diffs.
2. **Combat & Tactical Prose Grounding**:
   - When drafting combat or tactical scenes involving weapons, cyberware, or drone assets, retrieve the exact item card to weave canonical manufacturer specifications, firing modes, and Attack Ratings into the narrative.
3. **Missions Authority Verification**:
   - When verifying rules legality or handling potential core/supplement conflicts, execute `uv run sr6 rag search "<topic>" --compact` or `uv run sr6 rag query "<prompt>" --compact` to enforce the 4-Level Authority Matrix.

---

## 3. Workspace Diagnostic Commands & MCP Resources

When auditing character files or evaluating drafts, use the following workspace-bound commands and MCP tools:

```bash
# Character & Tabletop State Audit
uv run sr6 characters audit union

# Chapter Prose Linter & Anti-Slop Audit
uv run sr6 lint "chapters/<chapter_file>.qmd"

# 7-Axis Narrative Evaluator (Tier 1: 9.0, Tier 2: 8.5, Tier 3: 8.0)
uv run sr6 evaluate "chapters/<chapter_file>.qmd" --tier 1|2|3 --char union

# Tabletop Action & Combat Ledger Extractor
uv run sr6 ledger parse "chapters/<chapter_file>.qmd"

# Story Continuity Indexer
uv run sr6 continuity .

# Ecosystem Sync & CommLink6 GUI Save Patching
uv run sr6 sync-all
```

### Native MCP Resources

- `sr6://characters/union/master`: Live character sheet and dossier data.
- `sr6://campaign/contacts`: Campaign contact registry and favor point balances.
- `sr6://rules/summary`: Summary of core rules and authority citations.
