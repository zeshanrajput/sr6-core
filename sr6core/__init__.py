"""
SR6 Core Package: The Tabletop Companion and Narrative Engine for Shadowrun 6th Edition.

Provides:
- character: Authoritative Character entity, Markdown Trio compilation, and ledger.
- rules: Offline SQLite rules vault, modifiers, gameplay tables, and card generator.
- narrative: Editorial linter, story continuity tracker, and audio narration.
- publishing: Official fillable PDF character sheets, Quarto enrichers, and Roll20/XML exporters.

Usage Example:
    >>> import sr6core
    >>> char = sr6core.load_character("reiko")
    >>> print(f"{char.name}: {char.nuyen}¥, {char.karma} Karma")
    >>> pdf_path = char.export_fillable_pdf()
"""

from sr6core.character import (
    Character,
    load_character,
    list_characters,
    CharacterManager,
    get_character_manager,
    compile_character,
    rebuild_character_yaml,
    deep_audit_character,
    AttributeBlock,
    LivingPersona,
    Skill,
    Quality,
    Contact,
    Drone,
    WeaponStatBlock,
    ArmorStatBlock,
    VehicleStatBlock,
    SpellStatBlock,
    AdeptPowerStatBlock,
    QualityStatBlock,
    CyberwareStatBlock,
    NPCStatBlock,
    CharacterSchema,
)

from sr6core.rules import (
    RulesDB,
    DEFAULT_DB_PATH,
    execute_db_query,
    get_db_schema,
    get_item_card,
    format_card,
    ModifierEngine,
    PoolModifier,
    PoolComponent,
    PoolOptimization,
    get_cheatsheet,
    list_cheatsheets,
    get_pack,
    parse_6wc_packs,
    resolve_book_file,
    search_source_book,
)

from sr6core.narrative import (
    analyze_prose,
    print_prose_report,
    run_markdownlint,
    BANNED_BUZZWORDS,
    build_continuity_report,
    print_continuity_report,
    generate_narration,
)

from sr6core.publishing import (
    expand_quarto_shortcodes,
    generate_character_dossier_appendix,
    export_mobile_json,
    export_fillable_pdf,
)

from sr6core import character
from sr6core import rules
from sr6core import narrative
from sr6core import publishing
from sr6core import ledger

__version__ = "0.2.0"

__all__ = [
    # Top-Level Facade
    "Character",
    "load_character",
    "list_characters",
    "CharacterManager",
    "get_character_manager",
    "compile_character",
    "rebuild_character_yaml",
    "deep_audit_character",
    "RulesDB",
    "DEFAULT_DB_PATH",
    "execute_db_query",
    "get_db_schema",
    "get_item_card",
    "format_card",
    "ModifierEngine",
    "PoolModifier",
    "PoolComponent",
    "PoolOptimization",
    "get_cheatsheet",
    "list_cheatsheets",
    "get_pack",
    "parse_6wc_packs",
    "resolve_book_file",
    "search_source_book",
    "analyze_prose",
    "print_prose_report",
    "run_markdownlint",
    "BANNED_BUZZWORDS",
    "build_continuity_report",
    "print_continuity_report",
    "generate_narration",
    "expand_quarto_shortcodes",
    "generate_character_dossier_appendix",
    "export_mobile_json",
    "export_fillable_pdf",
    # Data Models
    "AttributeBlock",
    "LivingPersona",
    "Skill",
    "Quality",
    "Contact",
    "Drone",
    "WeaponStatBlock",
    "ArmorStatBlock",
    "VehicleStatBlock",
    "SpellStatBlock",
    "AdeptPowerStatBlock",
    "QualityStatBlock",
    "CyberwareStatBlock",
    "NPCStatBlock",
    "CharacterSchema",
    # Subpackages
    "character",
    "rules",
    "narrative",
    "publishing",
]
