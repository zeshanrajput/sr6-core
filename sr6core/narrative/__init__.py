"""
Narrative subpackage for SR6 Core.
Provides prose linting (29 anti-slop rules, braid ratio, ellipses ceiling),
campaign story continuity tracking, and Kokoro TTS narration generation.
"""

from sr6core.narrative.linter import (
    analyze_prose,
    print_prose_report,
    run_markdownlint,
    BANNED_BUZZWORDS,
)
from sr6core.narrative.continuity import (
    build_continuity_report,
    print_continuity_report,
)
from sr6core.narrative.narration import (
    generate_narration,
    batch_generate_narrations,
    clean_markdown_for_tts,
    clean_pronunciation,
    extract_chapter_metadata,
    list_narratives,
    retag_narratives,
)

from sr6core.narrative.sync import (
    sync_narrative_context,
    print_sync_report,
)
from sr6core.narrative.packet import build_story_packet
from sr6core.narrative.prep_audio import (
    scan_audio_prep,
    print_audio_prep_report,
)

__all__ = [
    "analyze_prose",
    "print_prose_report",
    "run_markdownlint",
    "BANNED_BUZZWORDS",
    "build_continuity_report",
    "print_continuity_report",
    "generate_narration",
    "batch_generate_narrations",
    "clean_markdown_for_tts",
    "clean_pronunciation",
    "extract_chapter_metadata",
    "list_narratives",
    "retag_narratives",
    "sync_narrative_context",
    "print_sync_report",
    "build_story_packet",
    "scan_audio_prep",
    "print_audio_prep_report",
]
