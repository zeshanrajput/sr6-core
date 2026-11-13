# Master Workspace Agent Instructions: SR6 Core (`sr6-core`) & Portfolio Pipeline

This workspace provides the core engine, CLI tools, datasets, and the **Shadowrun 6e Narrative Suite Plugin (`sr6-narrative-suite`)** located at `.agents/plugins/sr6-narrative/`.

---

## 0. Core Tabletop Companion Philosophy & Non-Negotiable Mandates

The primary purpose of `sr6-core` is to **support physical tabletop roleplay**. 

* **The Companion Role**: The tool does the heavy cognitive lifting—calculating situational modifiers, stacking bonuses, computing net dice pools, determining defense ratings, and presenting relevant rules in context.
* **No Digital Dice Rollers**: We deliberately do **NOT** implement digital dice rollers in books, web apps, or character sheets. Tabletop players roll physical dice at the table. Companion tools present the final pool (e.g. `14d6`) and let the player grab their physical dice.
* **Data-Driven Architecture (No Hardcoded Character Hacks)**: The engine must remain character-agnostic. All mechanics (ASDF arrays, Monad abilities, living personas, augmentations, and armor) must be derived dynamically from dossiers and database models (`ref_qualities`, `ref_cyberware`, etc.) rather than hardcoded character ID checks (`if char_id == "venn":`).
* **CommLink 6 XML Character Export Standards**:
  * *Strict Enum Sanitization*: Tabletop weapon firing modes (`SA/BF/SS`, `SS`) must never be assigned to the XML `mode` attribute; map strictly to CommLink 6's Java `ItemUsage` enum (`CARRIED`, `EQUIPPED`, `HOLSTERED`, `IMPLANTED`, `EMBEDDED`, `VIRTUAL`).
  * *Vehicle Condition Tracking*: All vehicle and drone root `<item>` elements require `changes="0,0,0"` to initialize clean damage monitors.
  * *Factory Embeds vs. Aftermarket Accessories*: Query `ref_vehicles` dynamically for factory embeds (`integrated_cyberarm`, `weapon_mount_standard`) and serialize installed weapons/implants into `<accessoriesInFact inFactoryItem="<UUID>">` with appropriate `CYBERLIMB_IMPLANT` or `VEHICLE_WEAPON_LARGE` slots; aftermarket modifications route to `<accessories>` across canonical `ItemHook` slots (`VEHICLE_POWERTRAIN`, `VEHICLE_CHASSIS`, `VEHICLE_HARDPOINT`, `VEHICLE_ELECTRONICS`, `VEHICLE_TIRES`).
  * *Canonical Decisions*: Numerical ratings (1–6) use decision choice `c2d17c87-1cfe-4355-9877-a20fe09c170d`; cyberware grades use decision choice `c2d17c87-1cfe-4355-9877-a20fe09c170c` with uppercase values (`USED`, `STANDARD`, `ALPHA`, etc.); ammo types use `b015341d-24dc-42bb-a46b-781a5340e0b3`.
  * *Echo & Foci Segregation*: Resonance data structures belong in `<datastructures>`, not magic `<foci>`. Submersion echoes must be deduplicated across build and log sources to maintain exact Submersion Grade.
* **The Inter-Session Narrative Mandate (Theological & Psychological Engine)**: Inter-session prose operates in deliberate counterbalance to the mechanical and social constraints of the gaming table, adhering to [`reference/inter_session_narrative_doctrine.md`](file:///c:/GitHub/sr6-core/reference/inter_session_narrative_doctrine.md):
  * *Division of Labor*: Tabletop is the Operational Layer (action economy, collective table oxygen, physical dice); Prose is the Ontological Layer (metaphysical terror, somatic friction, moral weight). The prose retroactively charges table moments with unspoken gravity without causing table drag.
  * *Diegetic Consecration*: Money is consecrated capital/existential debt (chassis mortgages, identity masks, bioware rent); downtime labor is artificial somatic homeostasis (the sweat equity of maintenance as metabolism); karma is spiritual evolution. Game mechanics scaffolding (Condition Monitors, Edge tokens, dice pools, action labels) is completely stripped from prose.
  * *Two-Tier Dramatic Sphere*: Tier A Campaign Canon (`canonical: true`) respects the Canon Ceiling (read-only relational orbit; other PCs and campaign VIPs are inviolable). Tier B Bespoke Foils (`canonical: false`) carry full sovereign agency and permanent moral reckoning.
  * *Psychological Verisimilitude*: Healing is a negotiated truce rather than a clean toggle; survival disguises are operational armor, not self-loathing Pinocchio shame; virtues are weaponized against the self.
* **The Evergreen Reference Architecture Protocol (Decoupling History from Living State)**:
  To keep character `reference/` folders evergreen, maintainable, and free of context-bloating legacy debris:
  * *Hardware-Visual Coupling*: Any physical modification recorded in `character_purchases.qmd` (weapons, propulsion, limbs, chassis alterations, sensor apertures, deployers) must immediately trigger a corresponding update to `reference/visual_anchors.md` in the same turn. Purge obsolete equipment prompts and render new active hardware (e.g. vector thrusters, laser mounts, drone bays).
  * *Forward-Looking Plans Only*: `mechanical_plan.md` tracks *future/pending* upgrades. Once an upgrade is purchased in `character_purchases.qmd`, delete or collapse the derivation math into a concise active stat. Historical math belongs in git history and purchasing ledgers, not active planning documents.
  * *Single Authoritative Voice Spec (No Spec Bifurcation)*: Each character maintains exactly one living voice & narrative specification (`reference/voice_spec.md`). Never maintain parallel `narrative_spec.md` files; merge operational doctrine and somatic mortgage directly into `voice_spec.md`.
  * *Archive-by-Default for Superseded State*: When sanctuaries/safehouses are relocated (e.g. `r3sP@wn` $\rightarrow$ `~`), exploratory worldbuilding essays are completed, or contacts are compiled into `character_master.yaml`, move older standalone files into `reference/archive/`. The root `reference/` directory must strictly represent *active, living reality*.
  * *Continuity Matrix Catchup*: When finalizing chapters or running `sr6 story sync`, ensure the Key Character Foils & Entity Tracker in `reference/story_continuity.md` includes the newly completed chapter appearances.
  * *WebP-Only Image Hygiene*: All character gallery images (`characters/*/images/`) must use `.webp`. Raw `.jpg`/`.jpeg` files are git-ignored and automatically converted to `.webp` with markdown references updated via `uv run sr6 sync-all` or `uv run sr6 story sync <char_id>`.
* **Windows PowerShell Git Commit Protocol**: To prevent PowerShell whitespace, quote-escaping, and newline truncation issues when committing multi-line messages, always stage the commit message in a temporary file (e.g. `scratch/commit_msg.txt`), execute `git commit -F scratch/commit_msg.txt`, and immediately clean up the temporary file. Never pass complex multi-line strings directly via `git commit -m "..."`.

---

## 1. Editorial House Narrative Pipeline (`sr6-narrative-suite`)

All inter-session story breaking, clean-room beat drafting, parallel sub-agent audits, developmental/line editing, and chapter finalization are governed by [`.agents/plugins/sr6-narrative/rules/narrative-director.md`](file:///c:/GitHub/sr6-core/.agents/plugins/sr6-narrative/rules/narrative-director.md) and its plugin skills (`narrative-director`, `literary-analysis`, `no-ai-slop`, `sr6-rules`, `continuity-tracker`, `sr6-downtime-ledger`, `sr6-chapter-finalize`).

Summary pipeline:
- **Stage 0 (Story Break):** Break 3–5 beats in `reference/storyboard.md` and lock Tier 1/2/3 passing thresholds (**9.0 / 8.5 / 8.0**) before drafting.
- **Stage 1 (Context & JIT Packet):** Build a clean-room creative packet via `uv run sr6 story packet <char_id> "<target>" [--beat N]` (stripping lint checklists/rubrics) and run `uv run sr6 char pressure <id>`.
- **Stage 2 (Clean-Room Draft):** Dispatch a `self` sub-agent ("The Writer's Hat") to draft from the packet only; enforce a single pre-flight pass ("The Editor's Hat") via `uv run sr6 lint "<target>" --window 3` + `uv run sr6 evaluate "<target>" --tier <1|2|3> --char <id>`, then pause for collaborative human line-editing.
- **Stage 3–4 (Parallel Audit & Refinement):** Audit across the 7 craft/continuity/rules dimensions (and run `literary-analysis` prose-chisel passes when revising existing chapters).
- **Stage 5–6 (State Tracking & Series Bible Closeout):** Emit `{python} inc(...)` snippets for the Markdown Trio (`character_log.qmd`, `character_purchases.qmd`, `character_build.qmd` — **never** hand-edit `*_master.yaml`), and update `storyboard.md`, `voice_spec.md`, `visual_anchors.md`, and `story_continuity.md` via `uv run sr6 story sync <char_id>`.
- **Stage 7 (Publish & Finalize):** Run `uv run sr6 story prep-audio "<target>"` to catch heteronyms/unmapped proper nouns, generate Kokoro TTS audio (`uv run --extra narration sr6 narrate`), upload MP3s to the GitHub Release (never commit `.mp3` files), commit/push via `scratch/commit_msg.txt`, and verify CI/CD workflows.

---

## 2. CLI Diagnostic Utilities

Before completing edits or reviewing narrative/character updates, run corresponding CLI commands:
* **The 2-Step Rules Retrieval Protocol**:
  1. *Search*: `uv run sr6 rag search "<topic>" --compact` (5-stage hybrid search; outputs ranked results with `[RULE_ID]`)
  2. *Inspect*: `uv run sr6 rag get <ID1> <ID2> ... --compact` (returns full markdown rule chunks in a single call)
* **Direct SQLite Query (No Python Gymnastics)**: `uv run sr6 db query "<SQL>" --compact` (table `rules`: `id, source, chapter, topic, authority_level, tags, content`; see [database_schema.md](file:///c:/GitHub/sr6-core/reference/database_schema.md))
* **Database Schema Inspector**: `uv run sr6 db schema [table_name]` (inspect column definitions, types, and sample data)
* **Raw Sourcebook Explorer**: `uv run sr6 source <book_code> "<query>" [--context 12]` (instant chapter excerpts from converted_md/; codes: `crb`, `sw`, `srmg`, `6wc`, `bs`, `hns`, `dc`, `fs`, `cn`, `pp`, `so`, `da`, `wl`, `ec`, `aw`)
* **Cyberlimb & Augmentation Calculator**: `uv run sr6 calc limb --limb <arm|leg> [--grade <grade>] [--adapsin] [--agi N]`
* **Subsystem Rules Cheatsheets**: `uv run sr6 cheat <matrix|actions|monad|combat>`
* **Item & PACK Reference Cards**: `uv run sr6 card <quality|weapon|spell|cyberware|pack> <name>`
* **Prose & Markdown Linter**: `uv run sr6 lint "chapters/<file>.qmd" [--window 3]`
* **7-Axis Narrative Evaluator**: `uv run sr6 evaluate "chapters/<file>.qmd" --tier <1|2|3> --char <id>`
* **Clean-Room JIT Story Packet Compiler**: `uv run sr6 story packet <char_id> "<chapter_path>" [--beat N]`
* **Audiobook Pronunciation & Heteronym Scanner**: `uv run sr6 story prep-audio "<chapter_path>"`
* **Narrative Context Synchronizer**: `uv run sr6 story sync <char_id>`
* **Combat Ledger Action Parser**: `uv run sr6 ledger parse "chapters/<file>.qmd"`
* **Continuity Engine**: `uv run sr6 continuity <repo_path>`
* **Character Creation Auditor**: `uv run sr6 characters audit [char_id]`
* **Combat Opposed Simulation**: `uv run sr6 combat attack --pool <X> --ar <Y> --target-dr <Z>`
* **Dice Pool Roller**: `uv run sr6 roll <dice_pool> [--edge]`
* **TTS Narration Generation**: `uv run --extra narration sr6 narrate "chapters/<file>.qmd" --voice af_heart`
* **Ecosystem Sync & Build**: `uv run sr6 sync-all`
* **Multi-Format Exporters**: `uv run sr6 export <char_id> --format=roll20|vtt|xml|text_modular`
* **Plugin Management**: `uv run sr6 plugin status` / `uv run sr6 plugin install`

---

## 3. The Consolidated 7-Skill Narrative Suite Reference

| Skill Name | Role | Primary Command / Pre-Flight |
| :--- | :--- | :--- |
| **`narrative-director`** | Master orchestrator & clean-room beat drafter | `narrative-director <file> <beat>` / `/draft-beat` |
| **`literary-analysis`** | Unified craft engine: 7-axis audit rubrics, action choreography & chisel | `literary-analysis <file>` / `sr6 evaluate` |
| **`no-ai-slop`** | 30 anti-slop patterns, banned terms list, affirmative staging | `uv run sr6 lint` |
| **`sr6-rules`** | SR6 mechanics, stat blocks, local SQLite FTS5 queries & RAG vault | `uv run sr6 card` / `rag search` |
| **`sr6-chapter-finalize`** | Stage 7 publishing: Kokoro TTS audio, release asset upload, story sync, CI/CD | `/finalize-chapter` / `sr6 story sync` |
| **`continuity-tracker`** | Timeline continuity, causal matrix, contacts & Markdown Trio verification | `uv run sr6 continuity` |
| **`sr6-downtime-ledger`** | Karma progression, gear buying, `{python} inc(...)` trio snippets | `uv run sr6 card` / `sync-all` |
