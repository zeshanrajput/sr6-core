---
name: sr6-downtime-ledger
description: Manage SR6 downtime advancement, purchases, session recaps, and ledgers.
version: 1.1.0
author: Zeshan Rajput (zeshanrajput), Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [shadowrun, sr6, downtime, karma, nuyen, purchases, ledger, srm, contacts]
    related_skills: [sr6-rules, continuity-tracker, shadowrun-campaign-management]
---

# SR6 Downtime & Financial Ledger Skill (`sr6-downtime-ledger`)

Manage downtime progression, Karma advancements, nuyen transactions, contact favor point trading, and gear purchases within the `sr6-core` ecosystem, ensuring 100% compliance with the Markdown Trio architecture.

## When to Use

- Ingesting post-session recaps from varied GM styles into `character_log.qmd`.
- Executing official **Shadowrun Missions (SRM / SRMG v2.4)** Major and Minor downtime actions.
- Spending Karma on attributes, skills, specializations, qualities, or complex forms/spells.
- Purchasing weapons, cyberware, bioware, drones, vehicles, or lifestyle upkeep.
- Generating drop-in `{python} ...` snippets for `character_purchases.qmd` or `character_log.qmd`.
- Validating ecosystem compilation after tabletop advancement.

## Sourcebook & Reference Exploration (`converted_md/`)

Whenever exact wording, quality descriptions, or campaign rules are needed, leverage the local `converted_md/` directory:

```bash
# Search verbatim sourcebooks using book codes (crb, 6wc, hns, dc, fs, sw, bs)
uv run sr6 source <book_code> "<query>" [--context 12]

# Look up SRM campaign rules directly from the Missions Guidebook (v2.4)
uv run sr6 source 391504 "<query>"

# Search local 20,082-chunk FTS5 rules vault
uv run sr6 rag search "<topic>" --compact
```

## The Single Source of Truth Architecture

- **Core Markdown Trio**:
  1. `character_build.qmd`: Baseline attributes, permanent qualities, cyberware, and active foci declared via `{python} modifier(...)`.
  2. `character_purchases.qmd`: Downtime purchases, attribute/skill increments, and gear acquisitions using `sr6core.log_engine` helpers.
  3. `character_log.qmd`: Mission-by-mission Karma/Nuyen awards, contact favor adjustments, downtime actions, and physical/stun state.
- **NEVER edit `*_master.yaml` directly.** Master YAML is compiled from scratch via `uv run sr6 sync-all`.
- **Deliver drop-in snippets in chat**: Provide ready-to-paste Python blocks for the user to inspect and commit.

---

## SRM Guide v2.4 Downtime Activity Taxonomy (p. 17–19)

Between any two standard SRMs, a runner can perform **one Major and one Minor Downtime Activity**, OR **three Minor Downtime Activities**. After a CMP mission, they gain an additional **two Minor Downtime Activities**.

### Major Downtime Activities
| Major Action | Mechanics & Formulas | Python Helper Function |
| :--- | :--- | :--- |
| **Strengthen Connection** | **Non-canonical contacts only.** Target Connection $\times$ Major Actions at Target Rating $\times$ 1,000¥ each. Upon reaching target rating, grants Target Rating in Favor Points, allowing immediate Loyalty elevation. | `{python} strengthen_connection(name, target_connection=N, step=X)` |
| **Strengthen Loyalty (4+)** | Elevating Loyalty to 4 or higher requires a Major Action and spending FP equal to the next level of Loyalty. | `{python} strengthen_loyalty(name, target_loyalty=N)` |
| **Initiate / Submerge** | Increases Initiation or Submersion grade. Karma cost = $10 + (\text{Grade} \times 3)$ (or $10 + (\text{Grade} \times 2)$ with ordeal/task). | `{python} initiate(grade)` / `{python} submerge(grade)` |
| **Cybersurgery** | Surgical implantation or replacement of one or more cyberware/bioware items. | `{python} cybersurgery("Items")` |
| **Initial Geneware Treatment** | First application of a geneware therapy. | `{python} initial_geneware("Treatment")` |
| **Repair ALL Drones & Vehicles** | Full maintenance overhaul across all damaged vehicles and drones in the runner's inventory. | `{python} repair_all_drones()` |
| **Lay Low** | Reduces accumulated Heat. | `{python} lay_low(heat_reduction=1)` |
| **Transhumanist Training** | Advanced body/mind conditioning per *6WC* p. 146. | `{python} transhumanist_training()` |
| **Work a Contact** | Networking to acquire obscure data or favors per *SR6 CRB* p. 236. | `{python} work_contact(name)` |
| **Work for the Streetdoc** | (Shadow Healthcare Community): Convert unlimited Karma to nuyen for personal augmentations at 1 Karma $\rightarrow$ 7,000¥. | `{python} work_for_the_streetdoc(karma=N, target_item="...")` |
| **Buying Favor Points** | Purchase contact Favor Points per *6WC* p. 173. | `{python} buy_favor_points(name, nuyen=N, fp=N)` |
| **Conclave / Coven Task (5–8)** | Complete a high-tier magical group obligation (*Street Wyrd*). | `{python} conclave_task(level=N)` |

### Minor Downtime Activities
| Minor Action | Mechanics & Formulas | Python Helper Function |
| :--- | :--- | :--- |
| **Register Sprites\*** | Register up to 8 levels of sprites (buying hits: 4 dice = 1 hit). | `{python} register_sprite("Modular", 8)` |
| **Bind Spirits\*** | Bind an summoned spirit (buying hits). | `{python} bind_spirit("Fire", 5)` |
| **Learn Complex Form / Spell**| Expand known spells or complex forms (5 Karma flat). | `{python} learn_complex_form("Name")` / `{python} learn_spell("Name")` |
| **Repair or Modify ONE Drone\*** | Repair or install modifications on a single drone or vehicle. | `{python} repair_drone("Name")` |
| **Strengthen Loyalty (Up to 3)**| Spend Favor Points equal to next level of Loyalty (1, 2, or 3). | `{python} strengthen_loyalty(name, target_loyalty=N)` |
| **Work for the People** | Donate to charity / community: trade 2,000¥ for 1 Karma (limit 1/mission). | `{python} work_for_the_people()` |
| **Work for the Man** | Corporate / street sellout: trade 1 Karma for 2,000¥ (limit 1/mission). | `{python} work_for_the_man()` |
| **Bond a Focus** | Pay bonding Karma cost (Rating $\times$ multiplier) and bind focus. | `{python} bond_focus(name, rating=N, category="...")` |
| **Subsequent Geneware** | Follow-up booster therapy session. | `{python} subsequent_geneware("Treatment")` |
| **Shadow Healthcare Task** | Volunteer at Seattle community clinics (1/month for SHC members). | `{python} shadow_healthcare_task()` |
| **Matrix Search Bonus** | Gain +4 dice to any single downtime Matrix Search. | `{python} matrix_search_bonus()` |
| **Boost Contact Availability** | Increase effective Connection of a single contact for purchasing gear. | `{python} boost_contact_connection(name, bonus=1)` |
| **Build / Take Down Lodge** | Construct or dismantle a hermetic/shamanic lodge. | `{python} build_lodge(rating=N)` / `{python} take_down_lodge(rating=N)` |
| **Prepare a Vessel\*** | Prepare a physical body or object for spirit possession/inhabitation. | `{python} prepare_vessel("Type")` |

> [!NOTE]
> **The In-Session Downtime Asterisk (\*)**: Activities marked with an asterisk can be conducted **during active game sessions** if there is sufficient in-fiction downtime (e.g. 1–2 days between mission legs), provided they are resolved by **buying hits**.

---

## Lifestyle Costs vs. The Hooder Quality

It is essential not to conflate living expenses with community obligations:

1. **Lifestyle Maintenance Costs**:
   - Defined in *SR6 Core Rulebook* p. 238 (Squatter 500¥, Low 2,000¥, Middle 5,000¥, High 10,000¥, Luxury 100,000¥).
   - In SRM, rent is typically paid every two missions for active lifestyles, unless subsidized or waived by mission rewards.
2. **The Hooder Quality (*Sixth World Companion*, p. 137)**:
   - Negative quality (5 Karma/level, max 3).
   - **Obligation**: The runner must donate at least **1,000¥ per level** each month to support their neighborhood/community.
   - **Intersection with Downtime**: Funds paid to fulfill the Hooder obligation **may be used to "Work for the People"** (converting 2,000¥ into 1 Karma) or to purchase contact favors.
   - **Rule**: Normal lifestyle rent does **not** count toward fulfilling Hooder or Working for the People.

---

## Flexible Session Recap Ingestion Playbook

Game Masters format recaps differently (bullet points, news broadcasts, inline pings, narrative summaries). Follow this modular checklist to ingest any recap:

1. **Mission Header & Rewards**:
   - Extract: Mission Code, Date, GM, Runner Team, Base Karma, Nuyen Payout.
   - **Veteran Difficulty**: Awards +1 bonus Karma (e.g. 7 base + 1 Veteran = 8 Karma total).
   - **Reputation**: Update regional/faction standing (`rep={'SEA': 2}`).
2. **Contact Audit**:
   - Cross-reference mentioned contacts against `reference/contacts.yaml` and `sr6core/character/contacts.py`.
   - **Canonical Contacts**: Apply earned Favor Points (`{python} contact("Name", fp=N)`). Loyalty raises are free if funded by freshly earned FP.
   - **Non-Canonical Contacts**: Check whether they are newly met or existing. If newly met, establish baseline C/L ratings and generate a reference dossier (`characters/<id>/reference/<name>.md`).
3. **Loot & Exploit Software**:
   - Record unique mission loot, vehicle modifications, or exploit programs in `character_purchases.qmd` or `character_log.qmd`.
4. **Downtime Accounting**:
   - Clarify the player's chosen Major/Minor downtime actions.
   - Emit standardized `{python} ...` helper blocks.

---

## Multiple Skill Specializations

In long-running campaigns, runners can acquire multiple specializations across skills (e.g., Tasking with both `Registering` and `Compiling`; Electronics with both `Software` and `Complex Forms`):

1. **Logging in Purchases (`character_purchases.qmd`)**:
   ```markdown
   * **Tasking Specialization (Compiling):** `{python} inc('Karma', -5)`
   * **Electronics Specialization (Complex Forms):** `{python} inc('Karma', -5)`
   ```
2. **Storage in Master YAML**:
   - `specialization`: Retains primary specialization for legacy backward compatibility.
   - `specializations`: Stores full list of all active specializations (`["Registering", "Compiling"]`).
3. **Sheet Display**:
   - ASCII quick sheets and mobile PWA exports automatically iterate all specializations and render their specialized dice pools.

---

## Post-Update Verification Checklist

- [ ] All downtime actions adhere to 1 Major + 1 Minor (or 3 Minors) budget.
- [ ] In-session downtime actions are astericked activities using bought hits.
- [ ] Contact Favor Points and Connection/Loyalty math verified.
- [ ] Run `uv run sr6 characters audit <char_id>` (must return PASS).
- [ ] Run `uv run sr6 sync-all` to compile master YAML and regenerate exports.
- [ ] Run `uv run pytest` to ensure no regression.
