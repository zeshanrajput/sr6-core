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
from sr6core.rules.engine import RulesEngine
from sr6core.rules.vehicles import (
    parse_vehicle_modifications,
    calculate_drone_action_pools,
    format_vehicle_mod_tables,
)
from sr6core.rules.matrix_actions import (
    render_matrix_actions_markdown,
    SRM_MATRIX_TAXONOMY,
)
from sr6core.rules.conjuring import (
    calculate_downtime_binding_table,
    render_downtime_binding_markdown,
    render_sprite_stable,
)
from sr6core.rules.nanotech import (
    NANOHIVE_CATALOG,
    NANOHIVE_PRESETS,
)
from sr6core.rules.spirits import (
    SPIRIT_CATALOG,
    get_spirit_channeling_info,
)
from sr6core.rules.calculator import (
    calculate_cyberlimb,
    calculate_ware,
    format_limb_calculation,
    format_ware_calculation,
)
from sr6core.rules.advancement import (
    search_catalog,
    purchase_item_for_character,
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
    "RulesEngine",
    "parse_vehicle_modifications",
    "calculate_drone_action_pools",
    "format_vehicle_mod_tables",
    "render_matrix_actions_markdown",
    "SRM_MATRIX_TAXONOMY",
    "calculate_downtime_binding_table",
    "render_downtime_binding_markdown",
    "render_sprite_stable",
    "NANOHIVE_CATALOG",
    "NANOHIVE_PRESETS",
    "SPIRIT_CATALOG",
    "get_spirit_channeling_info",
    "calculate_cyberlimb",
    "calculate_ware",
    "format_limb_calculation",
    "format_ware_calculation",
    "search_catalog",
    "purchase_item_for_character",
]
