---
name: continuity-tracker
description: Cross-checks gear, ammunition, spell drain, damage state, nuyen balances, and contact locations against character_master.yaml and past log context. Proactively retrieves canonical item stats via 'sr6 card' to validate downtime moves and propose explicit YAML state diffs.
---

# Story Continuity & State Tracker Skill (`continuity-tracker`)

Use this skill to audit narrative drafts and downtime proposals for state consistency against the character's `*_master.yaml` dossier (e.g., `union_master.yaml`, `yuriko_master.yaml`, `velvet_master.yaml`) and prior chapter log context.

---

## Evaluation Workflow

1. **State Baseline Ingestion & Tabletop Play Firewall**:
   - Locate and read the target character's dossier (`*_master.yaml`).
   - Query recent chapter log context via `sr6 continuity <repo_path>` or narrative index.
   - **The Tabletop Play Firewall**: Master dossiers (`*_master.yaml`) track **tabletop play session records only**. Fiction chapters serve as atmospheric framing between sessions.
   - **Continuity Verification (Non-Destructive)**: Verify that fiction does not violate existing capabilities (e.g., spending millions not owned, wielding unowned implants, or resurrecting deceased contacts). Do **NOT** propose patches to `*_master.yaml` for casual fiction purchases or background flavour costs.

2. **State & Inventory Audit Criteria**:
   - **Pre-Validation of Purchases / Installs**: When auditing or proposing downtime acquisitions, always verify stats via `uv run sr6 card "<item>"` to confirm exact Essence cost, Nuyen price, and Availability before writing state changes.
   - **Capability Consistency**: Ensure gear, spells, and implants depicted in fiction exist on the character sheet.
   - **Narrative Anchor Consistency**: Ensure contact names, locations, and relationships align with established campaign history.


3. **Sub-Agent Audit Report & State Diff Generation**:
   - **Continuity Score**: Rate from **1 to 10** (Pass threshold: **8.5+**).
   - **State Diff Output**: Generate an explicit YAML patch/diff for `*_master.yaml` summarizing state changes.

---

## Audit Report Format

```markdown
### Axis: Continuity & State Tracking Evaluation
* **Master Dossier Referenced**: [Path to *_master.yaml]
* **Continuity Score**: [Score]/10 (Threshold: 8.5)

#### Capability & Continuity Verification
- **Capability Compliance**: [Pass / Violations (e.g., using unowned spells/gear)]
- **Contact & Location Anchors**: [Pass / Consistency with established contacts]
- **Tabletop Firewall**: Verified (Fiction does not alter official play ledger)
```

