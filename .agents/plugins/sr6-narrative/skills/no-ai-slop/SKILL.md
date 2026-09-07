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

1. **Deterministic Pre-flight (Instant Check)**:
   Run the prose linter via the `terminal` tool to instantly catch banned buzzwords and ellipses ceiling violations in <10ms:
   ```bash
   uv run sr6 lint "characters/<char_id>/chapters/<file>.qmd"
   ```
2. **Unified Evaluator**:
   ```bash
   uv run sr6 evaluate "characters/<char_id>/chapters/<file>.qmd" --tier <1|2|3> --char <char_id>
   ```

## Editing Principles

- **Make the Minimum Effective Edit:** Fix slop patterns, repetition, and robotic structure. Leave strong human sentences alone.
- **Affirmative Staging:** Stage scenes through what characters *do*, not what they *don't* do (ban lazy filler negatives).
- **Trust the Reader:** Dramatize through physical action and dialogue subtext. Cut explanatory codas and thesis slogans.
- **One Speaker Per Paragraph:** Never combine lines spoken by different characters into the same paragraph block.
- **Sensory Restraint:** Ban formulaic olfactory checklists ("smelled of X, Y, and Z"). Ground scenes in acoustic, thermal, and barometric texture.

## Banned Words & Clichés

- **Outright Banned:** `delve`, `foster`, `leverage`, `utilize`, `facilitate`, `empower`, `streamline`, `robust`, `cutting-edge`, `paradigm shift`, `game changer`, `tapestry`, `realm`, `beacon`, `multifaceted`, `meticulous`, `intricate`, `paramount`, `transformative`, `elevate`, `supercharge`, `harness`, `ever-evolving`.
- **Sensory Shortcuts:** `smell of ozone`, `burnt copper`, `taste of copper`, `hot solder`, `chemical tang of processing`, `puddles of stale encryption`, `decaying logic in the gutters`, `systems redlining`, `logic loops in her head`, `processing at 600%`, `micro-geometry`, `infernal symmetry`, `unworldly gravity`, `neurologically mapped`, `evolutionary surrender`, `micro-saccadic`.
- **Empty Fillers & Crutches:** `it's worth noting`, `at the end of the day`, `when it comes to`, `at its core`, `in today's world`, `the reality is`, `make no mistake`, `full stop`, `let that sink in`.
- **Ellipses Ceiling:** $\le 0.60$ ellipses per 300 words. Trailing ellipses ruin audio TTS narration cadence.

## 29 Pattern Quick Reference

For full descriptions and before/after examples, see `references/slop-patterns.md`:

| Category | Patterns Flagged |
| :--- | :--- |
| **Structure & Cadence** | Binary contrasts (P1), Throat-clearing openers (P2), Faux-insight setups (P3), Colon reveals (P4), Superficial `-ing` clauses (P5), Negative listing (P10), Dramatic fragmentation (P11), Robotic rhythm (P12), Staccato 1-sentence paragraph stacking (P23), Em-dash overuse (P17). |
| **Puffery & Attribution** | Importance puffery (P6), Weasel attribution (P7), Fake-strong verbs (P8), Synonym cycling (P9), Rhetorical setups (P13), Fake-profound kickers (P14), Summary-recap endings (P15), Formatting slop (P16). |
| **Sensory & World** | Olfactory checklist templates (P18), Lore preaching & meta-exposition (P19), Thesis monologuing (P20), Show-then-tell redundancy (P21), Gratuitous non-action negatives (P22), Inanimate anthropomorphism / false agency (P24), Tricolon fatigue (P25). |
| **Dialogue & Mindspeech** | Weightless radio chatter (P26), Bumper-sticker thesis sloganeering (P27), Multi-speaker dialogue merging (P28), Mindspeech double-quote confusion (P29). |

## Audit Report Format

```markdown
### Axis: No AI Slop Evaluation
* **No AI Slop Score**: [Score]/10 (Threshold: 8.5)
* **Banned Words Found**: [Count]
* **AI Patterns Detected**: [Count]

#### Detected Slop Patterns & Banned Terms
- **Binary Contrasts**: [Count & Quotes]
- **Throat-Clearing / Faux-Insight**: [Count & Quotes]
- **Colon Reveals & Fake Drama**: [Count & Quotes]
- **Fake-Profound Kickers / Recaps**: [Count & Quotes]
- **Em-Dash Density & Ellipses Ratio**: [Count / Ratio]

#### Mandatory Redline Removal List
- [ ] **Line X**: `"[Original quote with slop]"` -> **Fix**: `"[Direct, human replacement]"`
```
