---
name: sr6-chapter-finalize
description: Finalize narrative chapter with Kokoro TTS audio narration, GitHub Release asset upload, project cross-linking, and CI/CD verification.
version: 2.0.0
author: Zeshan Rajput (zeshanrajput), Antigravity Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [shadowrun, narrative, publishing, tts, kokoro, audio, git, cicd, github-actions]
    related_skills: [literary-analysis, continuity-tracker, no-ai-slop, narrative-director]
---

# SR6 Chapter Finalization & Publishing Skill (`sr6-chapter-finalize`)

Standardized end-to-end publishing and audio narration pipeline for finalized Shadowrun 6e narrative chapters. This skill automates the transition from approved prose into audiobook-grade Kokoro TTS narration, GitHub Release asset distribution, project context navigation, version control, and CI/CD deployment verification.

---

## When to Use

- When a chapter draft has passed all audit panel dimensions and completed Stage 4/6 line-level prose chiseling.
- When generating Kokoro TTS audio narration and embedding character metadata tags.
- When uploading newly synthesized chapter MP3s directly to GitHub Release assets under the zero-git-bloat policy.
- When registering a newly completed chapter across `_quarto.yml`, `index.qmd`, and `story_continuity.md`.
- When pushing the completed chapter to Git and autonomously waiting/verifying GitHub Actions workflows.

---

## Command Triggers

Invoke directly in chat:
```text
/finalize-chapter <target_file>
/publish-chapter <target_file>
finalize-chapter <target_file>
```
*Example: `/finalize-chapter characters/velvet/narrative/12_Iron.md`*

---

## The 5-Step Finalization Workflow

```
 +---------------------------------------------------------+
 | 1. PRE-FLIGHT VALIDATION & TTS CADENCE AUDIT            |
 | uv run sr6 lint "<target_file>"                         |
 | (Zero slop, zero \ufffd artifacts, ellipses <= 0.60)    |
 +----------------------------+----------------------------+
                              |
                              v
 +---------------------------------------------------------+
 | 2. KOKORO TTS AUDIO GENERATION & RELEASE UPLOAD         |
 | uv run --extra narration sr6 narrate "<target>" --char  |
 | gh release upload narrative-audio-v1 "<mp3>" --clobber  |
 +----------------------------+----------------------------+
                              |
                              v
 +---------------------------------------------------------+
 | 3. PROJECT CONTEXT & NAVIGATION SYNCHRONIZATION         |
 | uv run sr6 story sync <char_id>                         |
 | (Updates _quarto.yml, index.qmd, story_continuity.md)   |
 +----------------------------+----------------------------+
                              |
                              v
 +---------------------------------------------------------+
 | 4. WINDOWS POWERSHELL GIT COMMIT & PUSH                 |
 | git commit -F scratch/commit_msg.txt && git push        |
 +----------------------------+----------------------------+
                              |
                              v
 +---------------------------------------------------------+
 | 5. SCHEDULED CI/CD VERIFICATION (8-MINUTE TIMER)        |
 | schedule(DurationSeconds="480", Prompt="Verify CI...")  |
 | Check gh run list & gh run view upon wakeup             |
 +---------------------------------------------------------+
```

---

### Step 1: Pre-Flight Lint & TTS Cadence Validation

Verify the chapter meets all stylistic, technical, and audio readability criteria before generating audio:
```bash
uv run sr6 lint "<target_file>"
```
- **Zero AI Slop**: No banned buzzwords, throat-clearers, cognitive buffers, or binary contrasts.
- **The Ellipses Ceiling ($\le 0.60$ per 300 words)**:
  - TTS speech synthesis models parse ellipses as awkward multi-second silences or pitch drops that disrupt spoken cadence.
  - If `uv run sr6 lint` reports an ellipses ratio $> 0.60$, replace trailing ellipses with commas, em-dashes, or complete affirmative sentences.
- **Markdown Normalization for Spoken Voice**:
  - The narration engine (`clean_markdown_for_tts`) automatically strips markdown links, image tags, callout boxes (`::: {.callout-note}`), and code blocks.
  - Prose must not rely on typography gimmicks (ALL CAPS screaming, bracketed `[ERROR]` logs, or raw URLs) that sound unnatural when read aloud.
- **Mindspeech & Dialogue Cadence**:
  - Pure non-acoustic mindspeech (`*...*`) is automatically converted to spoken cadence during TTS synthesis.
  - Ensure mindspeech sentences end with standard punctuation (`.`, `?`, `!`) inside the asterisks so speech engines do not elide sentences together.
- **Zero Unicode Artifacts**: Zero `\ufffd` replacement characters.

---

### Step 2: Kokoro TTS Audio Generation & Release Asset Upload

#### 1. Pronunciation & Heteronym Calibration
Before generating audio, verify phonetics for Sixth World jargon and character handles in `reference/pronunciations.yaml`:
- **Sixth World Proper Nouns**:
  - `nuyen`: *new-yen*
  - `mitsuhama`: *meet-soo-hah-mah*
  - `aztechnology`: *az-tek-nahl-oh-jee*
  - `r31k0`: *ray-koh*
  - `dronomancy`: *droh-noh-man-see*
- **Contextual Heteronyms & Homographs**:
  - English G2P phonemizers (Kokoro / Misaki) cannot infer semantic context for heteronyms and default to the primary dictionary entry.
  - **The Keigo / Ceremonial Bow Rule**: In syndicate/corporate keigo fiction, "bow" almost always refers to the physical gesture `/baʊ/` rather than archery/ribbon `/boʊ/`. Map forms to exact phonetic homophones (`bow: bough`, `bows: boughs`, `bowed: boughed`, `bowing: boughing`).
  - Watch for other high-frequency heteronyms: *tear* (weep vs rip), *lead* (metal vs guide), *read* (past vs present), *wind* (breeze vs coil).

#### 2. Synthesize MP3 Audio Narration
Synthesize high-fidelity 160kbps MP3 audio narration using Kokoro GPU:
```bash
uv run --extra narration sr6 narrate "<target_file>" --char <char_id>
```
- **Audio Tag Sniffing**: The engine automatically detects the `<audio controls src="audio/(.*?)">` tag in the markdown header (e.g. `audio/12_Iron.mp3`) and targets that exact file name in `characters/<char_id>/narrative/audio/<audio_file>`.
- **Character ID3 Tagging**: Automatically embeds Title, Track Number, Artist (Character Handle/ID), and Album (*Shadowrun 6e: <Character Name>*).

#### 3. Upload to GitHub Release (Zero-Git-Bloat Policy)
To maintain the repository under the **12 MB ceiling** for Gemini web app compatibility, **NEVER commit `.mp3` files to Git**. Upload directly to the GitHub Release:
```bash
gh release upload narrative-audio-v1 "characters/<char_id>/narrative/audio/<audio_file>" --clobber
```
*(The GitHub Actions deploy workflow automatically downloads this asset into `_site/` during deployment, making it live on GitHub Pages with zero Git bloat).*

---

### Step 3: Project Context Synchronization

Run the narrative context synchronizer to wire the chapter into the web book and continuity ledger:
```bash
uv run sr6 story sync <char_id>
```
Automatically updates:
1. **`characters/<id>/_quarto.yml`**: Registers the chapter under `part: "Narrative Log"`.
2. **`characters/<id>/index.qmd`**: Appends the chapter under `### 2. Background & Campaign Narratives`.
3. **`characters/<id>/reference/story_continuity.md`**:
   - Updates contact appearances in Section 1.
   - Appends verified word count row to `## 3. Anthology Narrative Chapter Index`.
   - Recalculates total anthology word count.
   - Strips any stray `\ufffd` artifacts.

---

### Step 4: Windows PowerShell Git Commit Protocol

Stage the commit message in a temporary file (do NOT stage `.mp3` files):

```powershell
@"
feat(<char_id>): add Chapter <num> <Title> and project links

- Finalize Chapter <num>: <Title> (<filename>) with surgical line polishes
- Generate Kokoro TTS audio narration track and upload to narrative-audio-v1 release
- Register chapter in _quarto.yml and index.qmd
- Synchronize character relationship matrix and chapter breakdown in story_continuity.md
"@ | Set-Content -Path "scratch/commit_msg.txt" -Encoding utf8

git add "<target_file>" "characters/<char_id>/_quarto.yml" "characters/<char_id>/index.qmd" "characters/<char_id>/reference/story_continuity.md"
git commit -F scratch/commit_msg.txt
Remove-Item "scratch/commit_msg.txt"
git push origin master
```

---

### Step 5: Autonomous CI/CD Verification (8-Minute Schedule Timer)

Schedule an 8-minute timer using the Antigravity `schedule` tool to allow GitHub Actions builders to complete:

```json
{
  "DurationSeconds": "480",
  "Prompt": "Verify GitHub Actions build and CI test workflows for the latest commit pushed to master.",
  "TimerCondition": "never"
}
```

When the timer fires and wakes up the assistant:
1. Inspect recent workflow runs:
   ```bash
   gh run list --limit 3
   ```
2. Verify both required jobs are `completed` with `success`:
   - `CI Test & Quality Gate`
   - `Build & Deploy Unified SR6 Books & Mobile PWA`
3. Deliver the final status summary to the user with run IDs and verified deployment links.
