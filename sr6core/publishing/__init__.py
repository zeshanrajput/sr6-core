"""
Publishing subpackage for SR6 Core.
Provides 2-page ASCII quick reference sheets, Quarto enrichment and appendix dossiers,
and standalone offline mobile PWA exporters.
"""

from sr6core.publishing.quick_sheet import (
    export_quick_sheet,
    MAX_WIDTH,
    PAGE_LINE_BUDGET,
    TOTAL_LINE_BUDGET,
)
from sr6core.publishing.enricher import (
    expand_quarto_shortcodes,
    generate_character_dossier_appendix,
    inject_chapter_audio_players,
)
from sr6core.publishing.mobile_html import export_mobile_html
from sr6core.publishing.mobile_json import export_mobile_json

__all__ = [
    "export_quick_sheet",
    "MAX_WIDTH",
    "PAGE_LINE_BUDGET",
    "TOTAL_LINE_BUDGET",
    "expand_quarto_shortcodes",
    "generate_character_dossier_appendix",
    "inject_chapter_audio_players",
    "export_mobile_html",
    "export_mobile_json",
]
