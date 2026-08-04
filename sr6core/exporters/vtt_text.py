"""
Plain-Text VTT & Tabletop Printout Exporter for SR6.
"""

from typing import Dict, Any


def export_vtt_text(char_data: Dict[str, Any]) -> str:
    identity = char_data.get("identity", {})
    attrs = char_data.get("attributes", {})
    
    lines = []
    lines.append("=" * 60)
    lines.append(f" CHARACTER DOSSIER: {identity.get('handle', 'Unknown').upper()}")
    lines.append("=" * 60)
    lines.append(f" Real Name: {identity.get('real_name', 'N/A')}")
    lines.append(f" Metatype : {identity.get('metatype', 'Human')} | Stream: {identity.get('stream', 'N/A')}")
    lines.append("-" * 60)
    lines.append(" BASE ATTRIBUTES:")
    lines.append(f"  BOD: {attrs.get('body', 1)} | AGI: {attrs.get('agility', 1)} | REA: {attrs.get('reaction', 1)} | STR: {attrs.get('strength', 1)}")
    lines.append(f"  WIL: {attrs.get('willpower', 1)} | LOG: {attrs.get('logic', 1)} | INT: {attrs.get('intuition', 1)} | CHA: {attrs.get('charisma', 1)}")
    lines.append(f"  EDG: {attrs.get('edge', 1)} | RES: {attrs.get('resonance', 0)}")
    lines.append("=" * 60)
    
    return "\n".join(lines)
