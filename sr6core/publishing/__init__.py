"""
Publishing subpackage for SR6 Core.
Provides official fillable PDF character sheets, Quarto enrichment and appendix dossiers,
Roll20 JSON/macros, CommLink 6 XML, and derived character JSON bundles.
"""

from sr6core.publishing.enricher import (
    expand_quarto_shortcodes,
    generate_character_dossier_appendix,
    inject_chapter_audio_players,
)
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
from sr6core.publishing.fillable_pdf import (
    build_pdf_field_map,
    export_fillable_pdf,
)

__all__ = [
    "expand_quarto_shortcodes",
    "generate_character_dossier_appendix",
    "inject_chapter_audio_players",
    "export_mobile_json",
    "build_roll20_payload",
    "export_roll20_json",
    "export_commlink_xml",
    "export_to_commlink",
    "scan_commlink_player_saves",
    "generate_commlink_metadata",
    "render_campaign_roadmap",
    "build_pdf_field_map",
    "export_fillable_pdf",
]
