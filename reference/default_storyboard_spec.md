# Default Narrative Storyboard Specification & Schema Template

This document defines the base structural schema and governance model for **Master Narrative Storyboards** across the Shadowrun 6e character portfolio framework (e.g., `characters/velvet/reference/storyboard.md`, `characters/reiko/reference/storyboard.md`, `characters/venn/reference/storyboard.md`).

Character storyboards extend this base specification to manage the character's living narrative architecture across non-linear campaign play.

**Parent Doctrine:** [`reference/inter_session_narrative_doctrine.md`](file:///c:/GitHub/sr6-core/reference/inter_session_narrative_doctrine.md)

---

## 1. Storyboard Philosophy & The Non-Linear Mandate

Tabletop play (Shadowrun Missions, Convention Mission Packs, Homebrew Runs) is inherently **non-linear**:
* Tables play modules out of chronological sequence (e.g., moving between 2081 Seattle and 2083 European arcs).
* Sessions alternate between high-speed tactical combat and quiet roleplay.
* A rigid linear "Arc 1 $\rightarrow$ Arc 2 $\rightarrow$ Arc 3" chronology breaks as soon as missions jump across timelines or geography.

The **Storyboard** replaces linear calendar files with **thematic verticals** (three external campaign vectors and three internal ontological crucibles). Any chapter or inter-session vignette, regardless of when or where it is played, anchors to 1–2 verticals, ensuring continuous thematic cohesion without chronological lock-in.

---

## 2. Storyboard Schema Definition

Every character storyboard MUST implement the following eight core sections:

```yaml
storyboard_schema:
  character_id: string                      # e.g., "velvet", "reiko", "venn"
  character_title: string                   # Full character handle & real identity
  archetype_summary: string                 # Metatype, tradition/mechanic, tactical table role
  extends: "reference/default_storyboard_spec.md"

  # Section I: Master Dashboard Overview
  thematic_verticals:
    external_vectors:
      - id: 1
        name: string                        # Corporate pursuit, syndicate pacts, or regional dragnet
        core_catalyst: string               # Primary inciting incident / macro-threat
        primary_adversary: string           # Opposing megacorp, faction, or vigilante cell
        current_phase: string               # Active status (e.g., "Asymmetric Counter-Play", "Dormant")
      - id: 2
        name: string
      - id: 3
        name: string
    internal_crucibles:
      - id: 4
        name: string                        # Ontological / psychological / spiritual tension
        core_catalyst: string               # Somatic friction, high-stat horror, or moral choice
        primary_adversary: string           # Internal doubt, cognitive trap, or dark mirror
        current_phase: string               # Active phase (e.g., "Active Exploration", "Hardened Parity")
      - id: 5
        name: string
      - id: 6
        name: string

  # Section II: Two-Tier Dramatic Sphere
  two_tier_separation:
    tier_a_campaign_canon:
      description: "Read-only orbit; Canon Ceiling protects shared SRM VIPs and metaplot"
      canon_quarantine_rules: list          # Specific future timeline events quarantined until played at table
    tier_b_bespoke_foils:
      description: "Full sovereign agency; original antagonists and allies who can die, redeem, or fracture"

  # Section III: Bespoke Adversaries & Controlled Foils
  controlled_antagonists:
    - name: string                          # Full handle and title
      affiliation: string                   # Megacorp, syndicate, or decentralized cell
      profile: string                       # Capabilities, cyberware/magic, operational role
      thematic_function: string             # Exact psychological/dramatic contrast to protagonist

  # Section IV & V: Narrative Verticals Detail
  vertical_detail_structure:
    core_focus: string                      # Strategic / existential thesis
    major_previous_events: list             # Key beats cross-referenced to chapter IDs [ch-XX]
    current_status: list                    # Operational reality right now
    potential_future_threads: list          # Evocative, actionable scene hooks

  # Section VI: Consecrated Telemetry & Active Registries
  consecrated_telemetry:
    bonded_foci_or_chassis: list            # Foci, bonded items, or anthrodrone frames
    active_sin_masks_or_identities: list    # Personas, SIN ratings, status (Active/Burned/Quarantined)
    existential_debt_and_capital: string    # Consecrated nuyen / karma anchors

  # Section VII: Post-Session Story Queue
  story_queue:
    - title: string                         # Working vignette title
      persona_or_chassis: string            # Active identity or vessel
      setting: string                       # Location
      verticals_touched: string             # Which 1-2 verticals are advanced
      concept: string                       # Scene synopsis

  # Section VIII: Bibliographic Reference Registry
  bibliographic_registry:
    table: "Table mapping semantic keys [key] to filenames, types, and descriptions"
    commonmark_definitions: "Centralized list of [key]: relative/path.md definitions"
```

---

## 3. The 6-Vertical Architectural Standard

Every character storyboard balances the operational demands of shadowrunning against the psychological depths of the character:

| Vertical ID | Domain | Purpose | Core Question |
| :--- | :--- | :--- | :--- |
| **Vertical 1** | **External: Primary Corporate Dragnet** | Tracks the original creator, hunter, or institutional owner. | *How do we starve the hunter's algorithms without running forever?* |
| **Vertical 2** | **External: The Broken Bond / Past Retribution** | Tracks the fallout of escape, betrayed peers, or collateral damage. | *What ghosts from the past demand restitution or blood?* |
| **Vertical 3** | **External: The Sovereign Web & Alliances** | Tracks syndicate treaties, fixers, street safehouses, and contacts. | *How do we build mutual deterrence so attacking us costs too much?* |
| **Vertical 4** | **Internal: The High-Stat / Mechanical Horror** | Explores the existential price of high attributes, chrome, or resonance. | *What does our signature mechanical power cost our humanity?* |
| **Vertical 5** | **Internal: Moral Crucible / The False Retreat** | Confronts ascetic cop-outs, ethical compromises, and the need for "teeth." | *How do we act in the mudsprawl without becoming the monster?* |
| **Vertical 6** | **Internal: The Engineered Self / Core Sovereignty** | The metaphysical foundation: synthetic souls, chrome dysmorphia, or digital peace. | *When the masks drop and the noise stops, who is actually here?* |

---

## 4. The Centralized Bibliographic Standard

To guarantee **zero maintenance drift** when files are renamed, converted to `.qmd`, or reorganized:
1. **Never use raw citation markers** (`[cite: ...]`).
2. **Never repeat long relative or absolute paths** across the body of the storyboard.
3. Use **semantic reference links** (`[Display Text][semantic-key]`) throughout Sections I–VII.
4. Define all paths in a **single centralized registry block** in Section VIII.

### Standard Semantic Key Conventions

| Key Prefix | Resource Type | Target Folder | Example |
| :--- | :--- | :--- | :--- |
| `[doctrine]` | Governing Narrative Doctrine | `reference/` | `[doctrine]: ../../../reference/inter_session_narrative_doctrine.md` |
| `[storyboard-spec]` | Parent Storyboard Spec | `reference/` | `[storyboard-spec]: ../../../reference/default_storyboard_spec.md` |
| `[voice-spec]` | Character Voice & Craft Spec | `reference/` | `[voice-spec]: voice_spec.md` |
| `[continuity]` | Deterministic Contact/Chapter Index | `reference/` | `[continuity]: story_continuity.md` |
| `[build]` | Character Build Specification | `core/` | `[build]: ../core/character_build.qmd` |
| `[purchases]` | Purchases & Consecrated Gear Log | `core/` | `[purchases]: ../core/character_purchases.qmd` |
| `[log]` | Session & Karma Progression Log | `core/` | `[log]: ../core/character_log.qmd` |
| `[ch-XX]` | Narrative Chapter | `narrative/` | `[ch-04]: ../narrative/04_sabotage.md` |
| `[sess-YY]` | Tabletop Session Record | `sessions/` | `[sess-01]: ../sessions/2083_02_royal_road.md` |
| `[lore-ZZ]` | Megacorp or Setting Dossier | `reference/` | `[lore-mct]: ../../../reference/megacorps_power_plays.md` |
