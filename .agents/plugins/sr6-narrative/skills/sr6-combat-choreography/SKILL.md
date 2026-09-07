---
name: sr6-combat-choreography
description: Choreograph SR6 tactical combat into cinematic fiction.
version: 1.0.0
author: Zeshan Rajput (zeshanrajput), Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [shadowrun, sr6, combat, tactics, action, choreography]
    related_skills: [sr6-rules, axis-pacing-structure, narrative-director]
---

# SR6 Combat Choreography Skill (`sr6-combat-choreography`)

Translate Shadowrun 6th Edition tactical combat mechanics (initiative passes, Attack/Defense ratings, Edge maneuvers, smartlink telemetry, spell drain, and drone rigging) into visceral, somatic speculative fiction without dry rulebook recitation.

## When to Use

- Writing firefights, close combat exchanges, astral duels, or matrix cybercombat in campaign chapters.
- Staging action scenes where tactical gear (smartguns, suppressors, dermal armor, combat drones) must feel mechanically grounded.
- Resolving opposed combat tests using the CLI simulator before writing the narrative beat.

## How to Run

Execute combat simulations and dice mechanics via the `terminal` tool:

```bash
# Display exact weapon stat block (firing modes, ammo capacity, damage value, AR)
uv run sr6 card weapon "<weapon_name>"

# Roll an opposed dice pool (e.g. 14 dice with exploding 6s)
uv run sr6 roll 14 --edge

# Simulate an opposed ranged combat attack test
uv run sr6 combat attack --pool 14 --ar 12 --target-dr 8 --target-pool 10 --dv 4P
```

## Choreography Principles

1. **The 3-to-6 Sentence Braided Action Paragraph:**
   - In active firefights, weave three elements into every action paragraph:
     1. **Physical Micro-Movement & Cover Geometry:** Squeezing behind concrete pillars, ducking below window sills, brass casing clatter.
     2. **Tactile Gear & Telemetry Feedback:** Smartlink reticle jitter, suppressor hiss, recoil kick against dermal plating, barrel heat.
     3. **Immediate Somatic Consequence:** Impact shock, splintering plaster, ear ringing, or adrenaline burn.
2. **Translating TTRPG Mechanics into Sensory Experience:**
   - **Edge Advantage:** Stage Edge gain as tactical anticipation, spatial awareness, or noticing an enemy's delayed trigger squeeze—not as lucky movie magic.
   - **Smartlink Telemetry:** Smartguns project dynamic range readouts, windage correction, and crosshair locking directly onto the retina or cybereyes. Never describe the shooter manually squinting down iron sights when smartlinked.
   - **Armor & Penetration:** High Defense Rating means rounds glance harmlessly off armored leather jackets or ballistic plates; penetration cracks the ceramic core and drives blunt force into the ribs.
   - **Spell Drain & Resonant Fading:** Magic is not free fireworks. Mana channel backlash fractures blood vessels, locks jaw cartilage, and tastes like bitter copper or burning wire in the sinuses.
3. **Rigged Fire Support & Dronomancy:**
   - Rigged combat merges the character's sensory motor cortex directly with the vehicle/drone frame:
     - Rotors feel like shoulder blades; gimbals feel like eye sockets.
     - Ammunition feeds render as diminishing numeric meters in the peripheral field.
     - Taking damage creates phantom amputation or static blinding.

## Combat Scene Beat Sheet (4-Beat Action Model)

```
[Inciting Shot / Contact] ──> [Escalation / Maneuver] ──> [Climax / Lethal Pivot] ──> [Aftermath / Suppression]
```

- **Inciting Friction:** Opening salvo, surprise ambush, or failed negotiation threshold.
- **Escalation:** Maneuvering between cover, cycling fire modes (Semi-Auto to Burst Fire), calling drone strikes.
- **Climax:** Irreversible combat pivot—point-blank headshot, spirit banishing, or vehicle ramming.
- **Aftermath:** Spent brass cooling, smoke ventilation, trauma patch application, and checking remaining ammunition.

## Output Example

```markdown
Reiko dropped into a low crouch behind the rusted shipping crate, the first burst of 9mm rounds chewing through the corrugated steel three inches above her helmet. Her smartlink HUD flashed amber, feeding windage and target vectors from the Fly-Spy hovering forty feet above the alley. She thumbed the Ares Predator VI from single-fire to burst, the internal solenoid clicking sharp against the palm of her glove. When the corp guard broke cover to reload, the crosshairs locked solid green; she squeezed twice, the heavy pistol barking with muffled, concussive thuds that drove two rounds through his ballistic vest and dropped him onto the slick asphalt.
```
