---
name: no-ai-slop
description: Strip AI slop patterns and clichés from narrative drafts.
version: 1.0.0
author: Zeshan Rajput (zeshanrajput), Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [shadowrun, writing, editing, anti-slop, humanizer]
    related_skills: [axis-pacing-structure, axis-voice-internality, narrative-director]
---

# No AI Slop Skill (`no-ai-slop`)

Audit narrative chapters, dialogue, and campaign fiction to strip AI clichés, robotic rhythms, false agency, and empty prose crutches while preserving the author's authentic voice.

## When to Use

- Auditing narrative chapters during Stage 3 of the narrative pipeline.
- Editing a draft to make it sharper, more direct, and somatic.
- Running line-level redline removal on flagged prose.

## How to Run

1. **Deterministic Pre-flight & Unified Diagnostics**:
   Run the unified prose linter via the `terminal` tool to catch banned buzzwords, ellipses ceiling violations, cluster saturation, tier/voice calibration, and zero-rent eviction suspects:
   ```bash
   uv run sr6 lint "characters/<char_id>/narrative/<file>.md" --window 3 --tier <1|2|3> --char <char_id>
   ```
   *(Note: `sr6 evaluate` remains available as an alias for the same unified analyzer.)*

## Editing Principles

- **Make the Minimum Effective Edit:** Fix slop patterns, repetition, and robotic structure. Leave strong human sentences alone.
- **Active Eviction & Load-Bearing Readback (Saunders / Klinkenborg Loop):** Never rely on passive re-reading. Declare the paragraph's load-bearing job first, actively hunt for zero-rent words (tautological modifiers, pre-action emotional spoilers, stacked horror intensifiers, pacing throat-clearers, sensory filter scaffolding) targeting a `-5%` to `-8%` word delta, then run a post-cut readback to verify 100% of the paragraph's job remains intact.
- **Affirmative Staging & Non-Action Pruning:** Stage scenes through what characters *do*, not what they *don't* do. When an affirmative physical micro-action or posture carries the weight (e.g. *"her hands remained flat against her knees"*), ruthlessly delete the leading filler negative (*"did not flinch"*).
- **Trust the Reader vs. Contextual Scaffolding:** Dramatize through physical action and dialogue subtext. Cut explanatory codas, thesis slogans, and comparative essay preambles. However, preserve essential grounded scaffolding when specialized professional dynamics (e.g. medical triage detachment buffering supernatural charisma) or proprietary character motifs (e.g. gold vs. indigo pathways) cannot reasonably be deduced by the reader alone.
- **One Speaker Per Paragraph:** Never combine lines spoken by different characters into the same paragraph block. Braid that speaker's dialogue with their own physical micro-action.
- **Sensory Restraint:** Ban formulaic olfactory checklists ("smelled of X, Y, and Z"). Ground scenes in acoustic, thermal, and barometric texture.

## 4-Tier Lexical Budget & Quota Architecture

Instead of rigid binary blocklists that encourage synonym treadmills, `no-ai-slop` enforces a tiered currency system:

- **Tier 0: Hard-Banned Corporate & AI Idioms (Quota: 0):** `delve`, `foster`, `leverage`, `utilize`, `facilitate`, `empower`, `streamline`, `robust`, `cutting-edge`, `paradigm shift`, `game changer`, `this is huge`, `this changes everything`, `realm`, `beacon`, `multifaceted`, `meticulous`, `paramount`, `transformative`, `elevate`, `embark`, `supercharge`, `harness`, `ever-evolving`, `it's worth noting`, `at the end of the day`, `when it comes to`, `at its core`, `in today's world`, `the reality is`, `make no mistake`, `full stop`, `let that sink in`.
- **Tier 1: High-Salience Sensory Clichés (Quota: 1 per 3,000 words):** `smell of ozone`, `burnt copper`, `taste of copper`, `hot solder`, `chemical tang of processing`, `puddles of stale encryption`, `decaying logic in the gutters`, `systems redlining`, `logic loops in her head`, `processing at 600%`, `micro-geometry`, `infernal symmetry`, `unworldly gravity`, `neurologically mapped`, `evolutionary surrender`, `micro-saccadic`, `silver-chimed`, `tapestry`, `mosaic`, `intricate`, `absolute`. Allowed once if physically grounded in the scene; overages are strictly flagged.
- **Tier 2: Rare Lexicon Single-Use Budget (The "Alluvial" Rule: Quota: 1 per chapter):** `alluvial`, `petrichor`, `crepuscular`, `susurrus`, `palimpsest`, `labyrinthine`, `effulgence`, `chiaroscuro`, `chert`, `iridescent`, `gossamer`, `liminal`, `sepulchral`, `miasma`, `vertiginous`, `tessellated`, `punctate`, `incandescent`, `penumbra`, `thalassic`, `ossified`, `calcified`. Treat non-colloquial vocabulary as precious currency: spend once, then vary through grounded somatic nouns.
- **Tier 3: Sensory Modifiers & Palette Density (Density Ceiling: $\le 3.5$ per 1k words):** `dark`, `cold`, `sharp`, `shadow`, `silt`, `hum`, `amber`, `indigo`, `crimson`, `neon`. Modifiers must not crowd out competing sensory registers (thermal, barometric, tactile).
- **Universal Constraint: Proximity Echo Window:** Zero content bigram repetition within 45 words, and zero distinctive content word repetition within 20 words (e.g. banning accidental echoes like *"dark water... dark water"* or *"curled... curled"*).
- **Ellipses Ceiling:** $\le 0.60$ ellipses per 300 words. Trailing ellipses ruin audio TTS narration cadence.

## 32 Pattern Quick Reference

For full descriptions and before/after examples, see `references/slop-patterns.md`:

| Category | Patterns Flagged |
| :--- | :--- |
| **Structure & Cadence** | Binary contrasts (P1), Throat-clearing openers (P2), Faux-insight setups (P3), Colon reveals (P4), Superficial `-ing` clauses (P5), Negative listing (P10), Dramatic fragmentation (P11), Robotic rhythm (P12), Staccato 1-sentence paragraph stacking (P23), Em-dash overuse (P17), Proximity Lexical Echoes (P31). |
| **Puffery & Attribution** | Importance puffery (P6), Weasel attribution (P7), Fake-strong verbs (P8), Synonym cycling (P9), Rhetorical setups (P13), Fake-profound kickers (P14), Summary-recap endings (P15), Formatting slop (P16). |
| **Sensory & World** | Olfactory checklist templates (P18), Lore preaching & meta-exposition (P19), Thesis monologuing (P20), Show-then-tell redundancy (P21), Gratuitous non-action negatives (P22), Inanimate anthropomorphism / false agency (P24), Tricolon fatigue (P25), Lexical Saturation & Quota Overages (P32). |
| **Dialogue & Mindspeech** | Weightless radio chatter (P26), Bumper-sticker thesis sloganeering (P27), Multi-speaker dialogue merging (P28), Mindspeech double-quote confusion (P29). |
| **Game Scaffolding Leak** | Tabletop mechanics jargon in prose (P30: *Condition Monitor, dice pool, Edge tokens, Minor/Major actions, Drain codes, test thresholds*). Strip rulebook shorthand and render as tactile physics per [`reference/inter_session_narrative_doctrine.md`](file:///c:/GitHub/sr6-core/reference/inter_session_narrative_doctrine.md). |

## Audit Report Format

```markdown
### Axis: No AI Slop Evaluation
* **No AI Slop Score**: [Score]/10 (Threshold: 8.5)
* **Tier 0 Banned Words Found**: [Count]
* **Tier 1 & 2 Quota Overages**: [Count & Words]
* **Tier 3 Density Alerts**: [Count & Words]
* **Proximity Echo Violations (P31)**: [Count & Quotes]
* **AI Patterns Detected**: [Count]
* **Game Scaffolding Leaks (P30)**: [Count & Quotes]

#### Detected Slop Patterns & Quota Overages
- **Proximity Echoes (P31)**: [Lines & Quotes]
- **Rare-Word & Cliché Overages (P32)**: [Words, Counts & Lines]
- **Sensory Density Outliers**: [Words & Rates]
- **Binary Contrasts**: [Count & Quotes]
- **Throat-Clearing / Faux-Insight**: [Count & Quotes]
- **Colon Reveals & Fake Drama**: [Count & Quotes]
- **Fake-Profound Kickers / Recaps**: [Count & Quotes]
- **Em-Dash Density & Ellipses Ratio**: [Count / Ratio]
- **Game Scaffolding Leaks (P30)**: [Count & Quotes]

#### Mandatory Redline Removal List
- [ ] **Line X**: `"[Original quote with slop]"` -> **Fix**: `"[Direct, human replacement]"`
```
