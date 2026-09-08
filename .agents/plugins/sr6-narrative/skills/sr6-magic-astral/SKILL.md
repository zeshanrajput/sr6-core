---
name: sr6-magic-astral
description: Choreograph SR6 Awakened spellcasting, astral perception, and spirit conjuring.
version: 1.0.0
author: Zeshan Rajput (zeshanrajput), Antigravity Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [shadowrun, sr6, magic, sorcery, conjuring, astral, spirits, adept]
    related_skills: [sr6-rules, axis-voice-internality, axis-worldbuilding-grit, narrative-director]
---

# SR6 Magic & Astral Narrative Skill (`sr6-magic-astral`)

Translate Shadowrun 6th Edition magic, sorcery, astral perception, and spirit interactions into evocative, visceral speculative fiction without info-dumping spell tables.

## When to Use

- Writing spellcasting, counterspelling, spirit summoning/binding, or adept power manifestations.
- Staging Awakened POVs (e.g. Velvet's adept and hermetic/shamanic operations).
- Depicting the sensory transitions between physical meatspace and the emotional landscape of the Astral Plane.

## On-Demand Rulebook References (No Rules Duplication)

Do not duplicate spell statblocks or tradition rules inside drafts. Query the database directly via CLI when stats or rules are needed:

```bash
# Query exact spell profile (Direct/Indirect, Drain, Range, Duration)
uv run sr6 card spell "<spell_name>"

# Query spirit or adept power profiles
uv run sr6 card spirit "<spirit_type>"
uv run sr6 card adept_power "<power_name>"

# Search magic rules and rulings in the offline vault
uv run sr6 rag search "astral perception auras" --compact
uv run sr6 rag search "spirit services and bargaining" --compact
```

## Astral & Magical Choreography Principles

### 1. Astral Perception: The Emotional Gray
- When an Awakened character shifts perception to the astral plane:
  - Physical objects (concrete, chrome, plasteel) lose color and texture, flattening into mute, pale gray shadows.
  - Living things flare with vibrant, swirling emotional auras—health radiates as steady luminance; terror or deception flashes in jagged chromatic ripples.
  - **Cyberware & Invasions:** Cybernetic augmentations do not glow—they appear as dark, necrotic hollows or jagged glass scars carved through the aura where biological life was excised.
  - **Mana Barriers & Wards:** Ward perimeters shimmer like iridescent soap bubbles or heavy pressure walls that resist passage.

### 2. The Somatic Price of Magic: Drain & Backlash
- Magic is a physical demand placed upon the mortal vessel. It is never free:
  - **Minor Drain:** Throbbing temples, metallic copper taste on the tongue, sudden nosebleed, stinging sinuses, cracked capillary vessels.
  - **Severe Drain:** Jaw cartilage locking, knees trembling, sensory blurring, cold sweat, raw agony in the sternum.
  - Direct Combat spells pummel the target's life force from within (unresisted); Indirect spells conjure physical kinetic or thermal forces (resisted by Body).

### 3. Spirits as Alien Sentience
- Spirits are not generic video game summons or elemental pets:
  - Spirits have distinct alien paradigms, elemental viewpoints, and intrinsic dignity.
  - A Fire Spirit perceives the world as fuel waiting to be ignited; a Spirit of Man is steeped in human memories and city whispers; an Earth Spirit thinks with slow, grinding geologic patience.
  - Summoning is an exertion of authority; binding is a formal contract of service. Spirits obey the letter of their commands, but resent careless or humiliating servitude.

### 4. Adept Powers: Subconscious Perfection
- Physical adepts do not recite incantations—their magic expresses as supernatural physical economy:
  - Movements are devoid of wasted inertia; footing on slick gravel is impossibly firm.
  - Social adept powers (like *Kinesics* or *Voice Modulation*) manifest as micro-expression stillness, harmonic vocal resonance that bypasses skepticism, and supernatural rapport.
