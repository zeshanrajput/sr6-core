"""
Character subpackage for SR6 Core.
Provides character data models, authoritative Character entity,
Markdown Trio compilation, ledger tracking, purchases syncing, and auditing.
"""

from sr6core.character.model import (
    Character,
    load_character,
    list_characters,
    AttributeBlock,
    LivingPersona,
    LivingPersonaASDF,
    Skill,
    Quality,
    ComplexForm,
    MetaEcho,
    Contact,
    Drone,
    CreationBudget,
    WeaponStatBlock,
    ArmorStatBlock,
    VehicleStatBlock,
    SpellStatBlock,
    AdeptPowerStatBlock,
    QualityStatBlock,
    CyberwareStatBlock,
    NPCStatBlock,
    ComplexFormStatBlock,
    SpriteStatBlock,
    SpiritStatBlock,
    AIStatBlock,
    CharacterSchema,
)
from sr6core.character.manager import CharacterManager, get_character_manager
from sr6core.character.compiler import compile_character, rebuild_character_yaml
from sr6core.character.ledger import (
    get_log_totals,
    process_character_log,
)
from sr6core.character.purchases import PurchasesSyncEngine
from sr6core.character.audit import deep_audit_character, calculate_transaction_price
from sr6core.character.contacts import (
    normalize_contacts_list,
    calculate_total_karma_invested,
    get_canonical_contact,
    is_canonical_contact,
)

__all__ = [
    "Character",
    "load_character",
    "list_characters",
    "CharacterManager",
    "get_character_manager",
    "compile_character",
    "rebuild_character_yaml",
    "get_log_totals",
    "process_character_log",
    "PurchasesSyncEngine",
    "deep_audit_character",
    "calculate_transaction_price",
    "normalize_contacts_list",
    "calculate_total_karma_invested",
    "get_canonical_contact",
    "is_canonical_contact",
    "AttributeBlock",
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
    "ComplexFormStatBlock",
    "SpriteStatBlock",
    "SpiritStatBlock",
    "AIStatBlock",
    "CharacterSchema",
]
