---
name: sr6-narration-tts
description: Prepare and validate chapter prose for Kokoro TTS audio.
version: 1.0.0
author: Zeshan Rajput (zeshanrajput), Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [shadowrun, sr6, tts, kokoro, audio, narration]
    related_skills: [no-ai-slop, axis-pacing-structure, narrative-director]
---

# SR6 Audio Narration & TTS Skill (`sr6-narration-tts`)

Validate, sanitize, and generate audiobook-grade narration from campaign chapter prose using the Kokoro TTS PyTorch GPU engine and `sr6-core/sr6core/narration.py`.

## When to Use

- Pre-flight auditing of chapter prose for audio readability before rendering audiobooks.
- Checking that ellipses density meets the strict $\le 0.60$ ceiling per 300 words.
- Managing Shadowrun term pronunciations in `reference/pronunciations.yaml`.
- Generating 160kbps MP3 audio files with Mutagen metadata tags for mobile listening.

## How to Run

Execute linting and narration generation via the `terminal` tool:

```bash
# Verify ellipses ceiling and audio cadence compliance
uv run sr6 lint "characters/<char_id>/chapters/<file>.qmd"

# Generate TTS audio for a single chapter using the 'af_heart' voice
uv run sr6 narrate "characters/<char_id>/chapters/<file>.qmd" --voice af_heart

# Batch generate TTS audio for all chapters in a portfolio
uv run sr6 narrate batch "characters/<char_id>/chapters/" --output "characters/<char_id>/chapters/audio/"
```

## TTS Audio Pre-Flight Rules

1. **The Ellipses Ceiling ($\le 0.60$ per 300 words):**
   - TTS models parse ellipses as awkward, multi-second silences or pitch drops that disrupt spoken cadence.
   - If `uv run sr6 lint` reports an ellipses ratio $> 0.60$, replace trailing ellipses with commas, em-dashes, or complete affirmative sentences.
2. **Markdown Normalization for Spoken Voice:**
   - The narration engine (`clean_markdown_for_tts`) automatically filters markdown links, image tags, callout boxes (`::: {.callout-note}`), and code blocks.
   - Prose must not rely on typography gimmicks (e.g. ALL CAPS screaming, bracketed `[ERROR]` logs, or raw URLs) that sound unnatural when read aloud.
3. **Mindspeech & Dialogue Cadence:**
   - Pure non-acoustic mindspeech (`*...*`) is automatically converted to spoken cadence during TTS synthesis.
   - Ensure mindspeech sentences end with standard punctuation (`.`, `?`, `!`) inside the asterisks so speech engines do not elide sentences together.
4. **Pronunciation Management (`reference/pronunciations.yaml`):**
   - Verify phonetics for Sixth World jargon and character handles:
     - `nuyen`: *new-yen*
     - `mitsuhama`: *meet-soo-hah-mah*
     - `aztechnology`: *az-tek-nahl-oh-jee*
     - `r31k0`: *ray-koh*
     - `dronomancy`: *droh-noh-man-see*

## Narration Pre-Flight Checklist

- [ ] `uv run sr6 lint <chapter>` passes with ellipses ratio $\le 0.60$.
- [ ] No unexpanded technical acronyms or raw table markup in spoken sections.
- [ ] New syndicate/corp proper nouns added to `reference/pronunciations.yaml`.
- [ ] Narration generated to `chapters/audio/<chapter>.mp3` with clean title/artist MP3 tags.
