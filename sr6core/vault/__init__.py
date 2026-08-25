"""
SR6 Vault Subsystem.
Manages rulebook PDF conversion, atomic markdown chunking, vault integrity auditing,
stat block parsing into Pydantic models, and Google Gemini File Search Store vector synchronization.
"""

from sr6core.vault.atomizer import atomize_vault, FILE_MAP
from sr6core.vault.auditor import audit_vault
from sr6core.vault.gemini_sync import sync_gemini_store
from sr6core.vault.store_inspector import list_stores_summary, list_store_failures
from sr6core.vault.web_importer import import_web_faq
from sr6core.vault.pdf_converter import (
    clean_markdown_artifacts,
    clean_shadowrun_markdown,
    is_cuda_available,
    convert_pdf_to_md,
    batch_convert_pdfs,
)
from sr6core.vault.statblock_parser import (
    parse_markdown_table_rows,
    parse_weapon_table,
    parse_armor_table,
    parse_vehicle_table,
    parse_spell_table,
    parse_complex_form_table,
    parse_sprite_table,
    parse_spirit_table,
    parse_npc_statblock,
    parse_ai_statblock,
    calculate_modified_weapon,
    format_weapon_card,
    format_statblock_markdown,
    format_statblock_plaintext,
)

__all__ = [
    "atomize_vault",
    "FILE_MAP",
    "audit_vault",
    "sync_gemini_store",
    "list_stores_summary",
    "list_store_failures",
    "import_web_faq",
    "clean_markdown_artifacts",
    "clean_shadowrun_markdown",
    "is_cuda_available",
    "convert_pdf_to_md",
    "batch_convert_pdfs",
    "parse_markdown_table_rows",
    "parse_weapon_table",
    "parse_armor_table",
    "parse_vehicle_table",
    "parse_spell_table",
    "parse_complex_form_table",
    "parse_sprite_table",
    "parse_spirit_table",
    "parse_npc_statblock",
    "parse_ai_statblock",
    "calculate_modified_weapon",
    "format_weapon_card",
    "format_statblock_markdown",
    "format_statblock_plaintext",
]
