---
name: sr6-rules
description: Authoritative Shadowrun 6e rules, mechanics, and item stats lookup. Trigger whenever discussing character progression, downtime moves, cyberware/bioware essence costs, nuyen pricing, weapon modifications, matrix actions, drone combat, spell drain, or SRM rules interpretations.
---

# Shadowrun 6e Rules & Mechanics Verification Skill (`sr6-rules`)

Use this skill to verify official Shadowrun 6th Edition (SR6) rules, matrix/drone combat mechanics, spell drain formulas, Edge expenditures, and tactical stat blocks.

---

## ⚡ Mandatory Pre-Computation & Context Retrieval Protocols

To ensure 100% mechanical consistency and prevent hallucinations, **always execute local lookup commands before answering or planning**:

1. **Downtime Moves & Character Advancement**:
   * **Rule of Zero Memory Guessing**: Never guess Essence costs, Nuyen prices, Availability ratings, or Karma costs.
   * **Action**: Always run `uv run sr6 card "<item_name>"` or `uv run sr6 rag get "<rule_id_or_topic>" --compact` before proposing mechanical moves or YAML diffs.
2. **Scene Drafting (Combat / Matrix / Rigging)**:
   * **Rule of Sensory Grounding**: Ground weapon firing modes, Attack Ratings, Matrix ASDF stats, and drone attributes in canonical manufacturer descriptions.
   * **Action**: Run `uv run sr6 card "<weapon|cyberware|drone>"` to pull exact stats, firing modes, and manufacturer flavor directly into the prose.
3. **Missions Rules & Edge Case Ambiguities**:
   * **Rule of Authority Matrix**: When evaluating rule conflicts between core and supplements, run `uv run sr6 rag search "<topic>" --compact` to check the 4-tier Authority Matrix.

---

## 🔍 Local-First Rules Lookup Strategy

To optimize token efficiency, reduce cloud latency, and retrieve authoritative tabletop stats, **always attempt local search first**:

### 1. Primary: Local Offline Search (Fast & Zero-Cost)
Search the local 20,082-chunk FTS5 rules vault and CommLink6 reference database:

```bash
# Keyword / Topic search with stop-word filtering & BM25 ranking (--compact for agent mode)
sr6 rag search "<TOPIC_OR_KEYWORD>" [--compact]

# Instant full rule chunk extraction directly from SQLite in <5ms (zero AI tokens)
sr6 rag get "<RULE_ID_OR_TOPIC>" [--compact]

# Universal item reference card (category auto-detected, with formula rating math)
sr6 card "<ITEM_NAME>"
# Or explicit category: sr6 card <bioware|cyberware|weapon|quality|spell|drone> "<ITEM_NAME>"

# General CommLink6 reference dataset search
sr6 search "<ITEM_NAME>"
```

* **Local Capabilities**: Automatically consolidates duplicate regional entries (*City Edition: Hong Kong* canonical primary, *Seattle*, *Berlin* cross-references), evaluates rating multiplier formulas (`Rating × 0.2 Ess | Rating × 50,000¥`), and attaches typed Pydantic stat blocks (`WeaponStatBlock`, `SpellStatBlock`, `VehicleStatBlock`, etc.).

### 2. Secondary: Cloud / Local AI Rules Synthesis (When Required)
Invoke AI reasoning only when resolving complex multi-condition interactions or ambiguous rule interpretations:

```bash
# Query Gemini RAG rules assistant (--compact for clean Markdown without ASCII box art)
sr6 rag query "<YOUR_RULES_QUESTION>" [--compact]

# Query with character dossier context (attributes, skills, cyberware)
sr6 rag query "<YOUR_RULES_QUESTION>" --char <char_id> [--compact]

# Offline local model query (llama.cpp / Gemma)
sr6 rag query "<YOUR_RULES_QUESTION>" --provider llama --model gemma-2-9b-it [--compact]
```

---

## 📊 Pydantic Stat Block & Tactical Array Verification

When auditing combat, spellcasting, or rigging scenes:
1. **Dynamic Weapon Arrays (`calculate_modified_weapon`)**:
   Verify post-modification numbers depicted in narrative action:
   - **Smartlinks**: +2 Attack Rating, +2 Attack Dice (when using smartguns).
   - **Barrel Modifications**: Extended Barrel (+1/+2 Far AR), Suppressors/Silencers.
   - **Ammunition**: APDS (increased Penetration / AR vs Armor), Explosive (+1 DV), Stick-n-Shock (Stun Damage + Shock status).
2. **Entity Validation Constraints**:
   - Living & AI Attributes $\ge 1$, $0.0 < \text{Essence} \le 6.0$.
   - AI Matrix Condition Monitor strictly $\lceil \text{Willpower}/2 \rceil + 8$.
   - Spell Drain & Fading minimums $\ge 1$.

---

## Authority Order Matrix (SRM 4-Level Model)

1. **[LEVEL 1] SRM Campaign Exceptions**: (`SRM 6E Guidebook`, `SRM 6E Missions FAQ`) - Absolute top authority.
2. **[LEVEL 2] Supplemental Sourcebooks**: (`Hack and Slash`, `Companion`, `Double Clutch`, `Body Shop`, `Street Wyrd`, `Firing Squad`) - Modifies and expands base rules.
3. **[LEVEL 3] Standard Core Rulebook**: (`City Edition: Hong Kong` canonical, `Seattle`, `Berlin`) - Baseline mechanics.
4. **[LEVEL 4] Unofficial House Rules / FAQs**: (GM notes, fan conversion guides) - *Requires explicit disclaimer*.

---

## Sub-Agent Audit Workflow

When auditing narrative drafts for SR6 rules accuracy:
1. **Identify Mechanics in Prose**: Check Edge gains/expenditures, Matrix actions, spell drain, weapon firing modes, defense tests, and vehicle/drone rigging tests.
2. **Local-First Check**: Run `sr6 rag search` or `sr6 card` to obtain the exact stat block, firing mode, or drain value.
3. **Synthesis Check**: If edge-case ambiguity remains, run `sr6 rag query`.
4. **Enforce Tabletop Firewall**: Verify rules legality without modifying character tabletop play ledgers.

---

## Audit Report Format

```markdown
### Axis: SR6 Rules & Mechanics Verification Evaluation
* **SR6 Rules Score**: [Score]/10 (Threshold: 8.5)

#### Key Findings & Rules Audit
- **Edge & Action Economy**: [Pass / Violations + Citations]
- **Matrix & Rigging Mechanics**: [Pass / Violations + Citations]
- **Spellcasting & Drain Formulas**: [Pass / Violations + Citations]
- **Combat Modifiers & Defense Tests**: [Pass / Violations + Citations]

#### Required Rule Fixes & Book Citations
- [ ] **Line X**: Update weapon Attack Rating to 12/12/10/-/- reflecting installed Smartlink per [City Edition: Hong Kong, p. 247].
```
