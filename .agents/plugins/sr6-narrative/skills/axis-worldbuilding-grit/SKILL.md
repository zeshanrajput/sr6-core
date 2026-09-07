---
name: axis-worldbuilding-grit
description: Audit Shadowrun dystopian grit, texture, and corp pressure.
version: 1.0.0
author: Zeshan Rajput (zeshanrajput), Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [shadowrun, sr6, narrative, worldbuilding, cyberpunk]
    related_skills: [axis-pacing-structure, sr6-rules, narrative-director]
---

# Worldbuilding & Dystopian Grit Evaluation Skill (`axis-worldbuilding-grit`)

Use this skill to audit narrative drafts for Shadowrun 6e dystopian verisimilitude, sensory worldbuilding grit, corporate omnipresence, AR/Matrix immersion, and ensuring the oppressive setting serves as an active distorted lens on human reality.

## When to Use

- Auditing narrative chapters during Stage 3 of the narrative pipeline.
- Checking for corporate branding, AR clutter, and systemic economic oppression.
- Eliminating "cozy cyberpunk" tropes and encyclopedic info-dumping.

## How to Run

Execute the unified evaluator via the `terminal` tool:

```bash
uv run sr6 evaluate "characters/<char_id>/chapters/<file>.qmd" --tier <1|2|3> --char <char_id>
```

## Tier-Calibrated Worldbuilding Standards

- **Tier 1 (Keystones — Passing Threshold: $\ge 9.0 / 10$):**
  - Heavy, visceral dystopian texture. Megacorporate machinery, industrial scale, and predatory economics operating at maximum oppressive pressure.
- **Tier 2 (Narrative Evolution — Passing Threshold: $\ge 8.5 / 10$):**
  - Deep sprawl verisimilitude: dive bars, street doc clinics, underworld noodle carts, syndicate backrooms, and regional flavor (Redmond, Tacoma, West Seattle). Allows room for dark humor, syndicate politics, and authentic runner tradecraft.
- **Tier 3 (Atmospheric Bridges — Passing Threshold: $\ge 8.0 / 10$):**
  - Sensory micro-environments. The quiet hiss of a charcoal burner, cedar steam, and un-taxed tea leaves creating a palpable contrast against the rainy sprawl outside.

## Worldbuilding Audit Criteria

1. **The Distorted Lens of the Sixth World:**
   - Use the cyber-magical, corporate dystopia not merely as decorative set-dressing, but as an active magnifying glass on human vulnerability, exploitation, and resilience.
2. **Corporate Omnipresence & Authentic Branding:**
   - Megacorporations (Mitsuhama, Wuxing, Renraku, NeoNet remnants), branded products, corporate serial numbers (*MCI-EXP-884-LUNA*), and commercial AR spam must actively saturate the background.
3. **Tactile Cyberware & Spell Texture:**
   - Mechanical implant activations (servo clicks, actuator heat, dermal plating seams) and magical traditions (Shinto-Musok spirit ribbons, talismans, aura hue shifts) must be described in vivid physical terms.
4. **Zero Info-Dumping:**
   - All worldbuilding must be woven organically into immediate sensory interaction, tactical awareness, and physical friction. Never pause the story for an encyclopedia lecture.
5. **Shadow Economy Paranoia & Transactional Friction:**
   - Eliminate cozy tropes. Corporate asset theft and underworld clinic distribution carry genuine collateral terror for recipients (fear of tracing beacons, punitive strike teams, collateral destruction).
   - Fixers and shadow brokers must remain calculating, self-interested, and exacting, taking standard cuts and assessing cold margins rather than acting as cheerful benefactors.

## Audit Report Format

```markdown
### Axis: Worldbuilding & Dystopian Grit Evaluation
* **Target Tier**: [Tier 1 / Tier 2 / Tier 3]
* **Worldbuilding & Grit Score**: [Score]/10 (Threshold: 9.0 Tier 1 / 8.5 Tier 2 / 8.0 Tier 3)

#### Key Findings & Texture Analysis
- **The Distorted Lens & Dystopian Pressure**: [Pass / Fail + Analysis]
- **Corporate & Commercial Omnipresence**: [Pass / Fail + Analysis]
- **Cyberware & Magic Sensory Reality**: [Pass / Fail + Analysis]
- **Sprawl Atmosphere & Regional Grit**: [Pass / Fail + Analysis]
- **Info-Dump Cleanliness**: [Pass / Fail + Analysis]

#### Worldbuilding Enhancements & Grit Redlines
- [ ] **Paragraph X**: Add sensory corporate branding or AR clutter to ground the scene.
```
