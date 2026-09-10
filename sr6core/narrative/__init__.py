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
]
