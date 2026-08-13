---
name: continuity-tracker
description: Cross-checks gear, ammunition, spell drain, damage state, nuyen balances, and contact locations against character_master.yaml and past log context. Proposes explicit YAML state diffs.
---

# Story Continuity & State Tracker Skill (`continuity-tracker`)

Use this skill to audit narrative drafts for state consistency against the character's `*_master.yaml` dossier (e.g., `yuriko_master.yaml`, `velvet_master.yaml`) and prior chapter log context.

---

## Evaluation Workflow

1. **State Baseline Ingestion**:
   - Locate and read the target character's dossier (`*_master.yaml`).
   - Query recent chapter log context via `sr6 continuity <repo_path>` or narrative index.

2. **State & Inventory Audit Criteria**:
   - **Resource Ledger**: Track ammunition consumed, grenades thrown, reagents used, nuyen spent/received, and Karma earned.
   - **Physical & Matrix Health**: Track Physical damage boxes, Stun damage, Matrix persona damage, sprite fading, and spell drain suffered in the scene.
   - **Gear & Cyberware**: Verify that weapons, armor, active drones, decks, and foci used in prose are actually present in `*_master.yaml`.
   - **Contacts & Locations**: Verify contact names, locations, and relationship states match established continuity.

3. **Sub-Agent Audit Report & State Diff Generation**:
   - **Continuity Score**: Rate from **1 to 10** (Pass threshold: **8.5+**).
   - **State Diff Output**: Generate an explicit YAML patch/diff for `*_master.yaml` summarizing state changes.

---

## Audit Report Format

```markdown
### Axis: Continuity & State Tracking Evaluation
* **Master Dossier Referenced**: [Path to *_master.yaml]
* **Continuity Score**: [Score]/10 (Threshold: 8.5)

#### State & Inventory Discrepancies
- **Ammunition & Consumables**: [Pass / Discrepancy details]
- **Damage & Spell Drain**: [Pass / Discrepancy details]
- **Gear & Implant Verification**: [Pass / Discrepancy details]
- **Contact & Location Anchors**: [Pass / Discrepancy details]

#### Proposed `*_master.yaml` State Diff
```yaml
# Proposed Updates to character_master.yaml
nuyen:
  current: 12450 # -350 Nuyen spent on bribe at Club Inferno
damage_track:
  physical: 2    # +2 Physical damage boxes from heavy pistol shot
  stun: 1        # +1 Stun damage box from spell drain
inventory:
  ammo:
    heavy_pistol_regular: 42 # -6 rounds fired in scene
```
```
