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
from sr6core.publishing.roll20_json import (
    build_roll20_payload,
    export_roll20_json,
)
from sr6core.publishing.commlink_xml import (
    export_commlink_xml,
    export_to_commlink,
    scan_commlink_player_saves,
    generate_commlink_metadata,
)
from sr6core.publishing.campaign_roadmap import render_campaign_roadmap

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
    "build_roll20_payload",
    "export_roll20_json",
    "export_commlink_xml",
    "export_to_commlink",
    "scan_commlink_player_saves",
    "generate_commlink_metadata",
    "render_campaign_roadmap",
]
