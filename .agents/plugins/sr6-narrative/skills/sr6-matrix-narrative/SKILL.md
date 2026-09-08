---
name: sr6-matrix-narrative
description: Choreograph SR6 Matrix decking and technomancy into visceral cyber fiction.
version: 1.0.0
author: Zeshan Rajput (zeshanrajput), Antigravity Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [shadowrun, sr6, matrix, decking, technomancy, cybercombat, vr, ar]
    related_skills: [sr6-rules, axis-voice-internality, axis-pacing-structure, narrative-director]
---

# SR6 Matrix Narrative Skill (`sr6-matrix-narrative`)

Translate Shadowrun 6th Edition Matrix runs, cyberdecking, and technomancer operations into tense, sensory-grounded cyberpunk fiction without info-dumping rulebook tables.

## When to Use

- Writing Matrix infiltration, file searches, data spikes, or cybercombat in campaign chapters.
- Staging Decker and Technomancer POVs (e.g. Venn's Monad living persona or Reiko's technoshamaism).
- Translating AR overlays, cold-sim/hot-sim VR immersion, and ICE counter-measures into narrative pacing.

## On-Demand Rulebook References (No Rules Duplication)

Do not reprint Matrix rules inside drafts or prompts. Query the database directly via CLI when stats or actions are needed:

```bash
# Query exact program stats or cyberdeck hardware
uv run sr6 card program "<program_name>"
uv run sr6 card gear "<cyberdeck_name>"

# Query complex forms or sprites for technomancers
uv run sr6 card complex_form "<form_name>"
uv run sr6 card sprite "<sprite_type>"

# Search Matrix rules and SRM rulings
uv run sr6 rag search "matrix access levels" --compact
uv run sr6 rag search "overwatch score convergence" --compact
```

## Matrix Choreography & Sensory Archetypes

### 1. The Three Matrix Sensory Modes
- **Augmented Reality (AR):**
  - Translucent heads-up glyphs, icon clutter, corporate advertising halos floating over rain-slicked asphalt.
  - Hacking in AR keeps the runner grounded in meatspace—glancing at an access keypad while flicking a spoofed command with cyberglove or neural blink.
- **Cold-Sim Virtual Reality:**
  - Complete detachment from the biological body. The physical world vanishes into absolute sensory stillness.
  - The grid renders as a sculpted architectural reality—Mitsuhama grids render as neon-lit Shinto temples or brushed obsidian monoliths; Renraku hosts render as vast mathematical grids.
  - Lag is non-existent; movement is instantaneous upon intent.
- **Hot-Sim Virtual Reality:**
  - All biological sensory limiters stripped away. Euphoric, hyper-real, dangerously seductive, and lethal.
  - Speed of thought: milliseconds feel like minutes.
  - **Biofeedback Reality:** An enemy Data Spike or Black IC strike is not an error dialog—it hits as a lightning bolt through the spine, scorching neural synapses, tasting of burnt copper and ozone, risking immediate coma or death.

### 2. Technomancy vs. Cyberdecking
- **The Decker:** Operates through pristine military-grade hardware, cooling fans humming inside a titanium cyberdeck chassis, executing programmed exploits, monitoring cyberjack temperature.
- **The Technomancer:** Experiences the Matrix as an organic ecosystem—the Deep Resonance. Complex forms feel like flexing internal mental muscles; sprites appear as emergent companion digital fauna (e.g. Reiko's Taz); fading feels like migraine pressure behind the temple or sinus strain.

### 3. Escalation & The Ticking Clock
- **Access Tiers:** Infiltration begins with User access (reading files, sleazing doors) before escalating to Admin access (formatting servers, locking out defenders).
- **Overwatch Score (OS) & Convergence:** Every illegal matrix action leaves forensic breadcrumbs. Build narrative tension by showing the grid growing suspicious: roving Patrol IC angling their sensor cones, grid latency tightening, and the imminent panic of GOD (Grid Overwatch Division) convergence.
- **ICE Escalation:** Patrol IC detects anomalies $\rightarrow$ Tar Baby / Blaster IC attempts to link-lock and destroy decks $\rightarrow$ Black IC deploys to lethally flatline the meat body.
