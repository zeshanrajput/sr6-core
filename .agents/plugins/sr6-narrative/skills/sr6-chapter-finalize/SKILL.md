---
name: sr6-chapter-finalize
description: Finalize narrative chapter with Kokoro TTS audio, project cross-linking, git commit/push, and scheduled GitHub Actions verification.
version: 1.0.0
author: Zeshan Rajput (zeshanrajput), Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [shadowrun, narrative, publishing, tts, kokoro, git, cicd, github-actions]
    related_skills: [sr6-narration-tts, continuity-tracker, no-ai-slop, narrative-director]
---

# SR6 Chapter Finalization & Publishing Skill (`sr6-chapter-finalize`)

Standardized end-to-end publishing pipeline for finalized Shadowrun 6e narrative chapters. This skill automates the transition from approved prose into audio narration, project context navigation, version control, and CI/CD deployment verification.

---

## When to Use

- When a chapter draft has passed all 7 sub-agent audit panel dimensions and has completed Stage 4/6 line-level prose chiseling.
- When generating Kokoro TTS audio narration and embedding character metadata tags.
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
 | 1. PRE-FLIGHT VALIDATION                                |
 | uv run sr6 lint "<target_file>"                         |
 | (Zero slop, zero \ufffd artifacts, ellipses <= 0.60)    |
 +----------------------------+----------------------------+
                              |
                              v
 +---------------------------------------------------------+
 | 2. KOKORO TTS AUDIO GENERATION                          |
 | uv run --extra narration sr6 narrate "<target>" --char  |
 | (Sniffs <audio src="..."> tag; encodes 160kbps ID3 MP3) |
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

### Step 1: Pre-Flight Lint & Sanitization
Verify the chapter meets all stylistic and technical criteria before generating audio:
```bash
uv run sr6 lint "<target_file>"
```
- **Zero AI Slop**: No banned buzzwords, throat-clearers, cognitive buffers, or binary contrasts.
- **TTS Readability**: Em-dash / ellipsis ceiling $\le 0.60$ per 300 words.
- **Zero Unicode Artifacts**: Zero `\ufffd` replacement characters.

---

### Step 2: Kokoro TTS Audio Generation
Synthesize high-fidelity 160kbps MP3 audio narration using Kokoro GPU:
```bash
uv run --extra narration sr6 narrate "<target_file>" --char <char_id>
```
- **Audio Tag Sniffing**: The engine automatically detects the `<audio controls src="audio/(.*?)">` tag in the markdown header (e.g. `audio/12_Iron.mp3`) and targets that exact file name.
- **Character ID3 Tagging**: Automatically embeds Title, Track Number, Artist (Character Handle/ID), and Album (*Shadowrun 6e: <Character Name>*).

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
To prevent PowerShell whitespace, quote-escaping, and newline truncation issues when committing multi-line messages, always stage the commit message in a temporary file:

```powershell
@"
feat(<char_id>): add Chapter <num> <Title>, audio narration, and project links

- Finalize Chapter <num>: <Title> (<filename>) with surgical line polishes
- Generate Kokoro TTS audio narration track (<audio_file>)
- Register chapter in _quarto.yml and index.qmd
- Synchronize character relationship matrix and chapter breakdown in story_continuity.md
"@ | Set-Content -Path "scratch_commit_msg.txt" -Encoding utf8

git add "<target_file>" "characters/<char_id>/narrative/audio/<audio_file>" "characters/<char_id>/_quarto.yml" "characters/<char_id>/index.qmd" "characters/<char_id>/reference/story_continuity.md"
git commit -F scratch_commit_msg.txt
Remove-Item "scratch_commit_msg.txt"
git push origin master
```

---

### Step 5: Autonomous CI/CD Verification (8-Minute Schedule Timer)
After pushing, schedule an 8-minute timer using the Antigravity `schedule` tool to allow GitHub Actions builders to complete:

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
