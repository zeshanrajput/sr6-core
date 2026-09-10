"""
Rules subpackage for SR6 Core.
Provides SQLite database access, stat cards, situational modifiers,
gameplay tables, rules cheatsheets, PACKs catalog, and sourcebook searching.
"""

from sr6core.rules.db import (
    RulesDB,
    DEFAULT_DB_PATH,
    execute_db_query,
    get_db_schema,
    format_query_results,
    format_db_schema,
)
from sr6core.rules.cards import (
    get_item_card,
    format_card,
)
from sr6core.rules.modifiers import (
    ModifierEngine,
    PoolModifier,
    PoolComponent,
    PoolOptimization,
)
from sr6core.rules.cheatsheets import (
    get_cheatsheet,
    list_cheatsheets,
    format_cheatsheets_index,
)
from sr6core.rules.catalog import (
    get_pack,
    parse_6wc_packs,
    format_pack_card,
)
from sr6core.rules.source_explorer import (
    resolve_book_file,
    search_source_book,
    format_source_results,
)

__all__ = [
    "RulesDB",
    "DEFAULT_DB_PATH",
    "execute_db_query",
    "get_db_schema",
    "format_query_results",
    "format_db_schema",
    "get_item_card",
    "format_card",
    "ModifierEngine",
    "PoolModifier",
    "PoolComponent",
    "PoolOptimization",
    "get_cheatsheet",
    "list_cheatsheets",
    "format_cheatsheets_index",
    "get_pack",
    "parse_6wc_packs",
    "format_pack_card",
    "resolve_book_file",
    "search_source_book",
    "format_source_results",
]
