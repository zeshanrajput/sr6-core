---
name: sr6-downtime-ledger
description: Manage SR6 downtime advancement, purchases, and ledgers.
version: 1.0.0
author: Zeshan Rajput (zeshanrajput), Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [shadowrun, sr6, downtime, karma, nuyen, purchases, ledger]
    related_skills: [sr6-rules, continuity-tracker, shadowrun-campaign-management]
---

# SR6 Downtime & Financial Ledger Skill (`sr6-downtime-ledger`)

Manage downtime progression, Karma advancements, nuyen transactions, contact favor point trading, and gear purchases within the `sr6-core` ecosystem, ensuring 100% compliance with the Markdown Trio architecture.

## When to Use

- Spending Karma on attributes, skills, specializations, qualities, or complex forms/spells.
- Purchasing weapons, cyberware, bioware, drones, vehicles, or lifestyle upgrades.
- Generating drop-in `{python} inc(...)` snippets for `character_purchases.qmd` or `character_log.qmd`.
- Validating ecosystem compilation after tabletop advancement.

## How to Run

Execute lookup and ecosystem compilation via the `terminal` tool:

```bash
# Verify item price, Availability, and Essence cost before purchase
uv run sr6 card "<item_name>"

# Query advancement rules and karma costs
uv run sr6 rag search "<advancement_topic>" --compact

# Recompile master YAML and validate all balances from Markdown Trio
uv run sr6 sync-all

# Audit character compliance
uv run sr6 characters audit <char_id>
```

## The Single Source of Truth Architecture

- **Core Markdown Trio**:
  1. `character_build.qmd`: Baseline attributes, permanent qualities, cyberware, and active foci declared via `{python} modifier(...)`.
  2. `character_purchases.qmd`: Downtime purchases, attribute/skill increments, and gear acquisitions using `sr6core.log_engine` helpers.
  3. `character_log.qmd`: Mission-by-mission Karma/Nuyen awards, contact favor adjustments, and physical/stun state.
- **NEVER edit `*_master.yaml` directly.** Master YAML is compiled from scratch via `sr6 sync-all`.
- **Deliver drop-in snippets in chat**: Provide ready-to-paste Python blocks for the user to insert into their IDE.

## Downtime Advancement Calculation Formulas

| Advancement Target | Karma Formula (SR6 Standard) | Example |
| :--- | :--- | :--- |
| **New Attribute Rating** | New Rating $\times 5$ Karma | Raising Logic from 4 to 5 = $5 \times 5 = 25$ Karma |
| **New Skill Rating** | New Rating $\times 5$ Karma | Raising Cracking from 5 to 6 = $6 \times 5 = 30$ Karma |
| **Skill Specialization** | 5 Karma (flat) | Specialization: Cybercombat = 5 Karma |
| **Skill Expertise** | 5 Karma (after specialization) | Expertise: Cybercombat = 5 Karma |
| **New Spell / Complex Form**| 5 Karma (flat) | Resonance Veil = 5 Karma |
| **New Positive Quality** | Listed Quality Cost $\times 2$ (Downtime) | Quality costing 6 at creation = 12 Karma downtime |
| **Buying Off Negative Quality**| Listed Quality Bonus $\times 2$ (Downtime) | Removing 8 Karma negative quality = 16 Karma |

## Drop-in Code Snippet Templates

### 1. Attribute or Skill Increase (`character_purchases.qmd`)
```markdown
* **Attribute Increase (Logic 5):** `{python} inc_many(('Karma', -25), ('Logic', 1))`
* **Skill Increase (Cracking 6):** `{python} inc_many(('Karma', -30), ('Cracking', 1))`
* **Skill Specialization (Electronics: Hardware):** `{python} inc('Karma', -5)`
```

### 2. Gear & Cyberware Purchases (`character_purchases.qmd`)
Always verify exact nuyen price and Availability via `uv run sr6 card "<item>"` first:
```markdown
* **Purchased Ares Predator VI (Concealed Holster, 2 Spare Clips):** `{python} inc('Nuyen', -1450)` *(Contact: Street Doc Kazuo)*
* **Purchased Suzuki Mirage:** `{python} inc('Nuyen', -8500)` *(Chummer discount)*
```

### 3. Mission Rewards & Contact Favor (`character_log.qmd`)
```markdown
* **Mission Payout:** `{python} inc_many(('Karma', 6), ('Nuyen', 12000))`
* **Contact Favor Earned (Kazuo):** `{python} inc('Favor_Kazuo', 1)`
```

### 4. Active Foci & Modifiers (`character_build.qmd`)
```markdown
`{python} modifier("Power Focus (R4)", "magic", 4, type="focus", rule_anchor="Street Wyrd p. 45", notes="Bonded Rating 4 Power Focus")`
```

## Post-Advancement Verification Checklist

- [ ] Item Availability verified via `uv run sr6 card "<item>"`.
- [ ] Karma and nuyen math checked against current balances.
- [ ] Drop-in `{python} inc(...)` snippet formatted for chat.
- [ ] User runs `uv run sr6 sync-all` in their IDE to recompile master YAML.
