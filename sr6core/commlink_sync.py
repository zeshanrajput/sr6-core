"""
CommLink6 Player Save Scanner & Automated Roundtrip Sync Engine for SR6 Core.
Scans CommLink6 player character folders and enables two-way automated syncing between CommLink6 GUI and sr6-core.
Includes visual diff reporting of updated ledger values, contacts, and session rewards.
"""

import os
import glob
import sqlite3
import xml.etree.ElementTree as ET
from typing import Dict, Any, List, Optional, Tuple

from sr6core.config import DEFAULT_COMMLINK_PLAYER_DIR, get_character_configs
from sr6core.character_manager import CharacterManager
import uuid
from sr6core.config import DEFAULT_COMMLINK_PLAYER_DIR, get_character_configs
from sr6core.character_manager import CharacterManager
from sr6core.exporters.genesis_xml import export_genesis_xml, generate_commlink_metadata

KNOWN_CHAR_ALIASES = {
    "yuriko": "reiko",
    "yuriko_star": "reiko",
    "yuriko star": "reiko",
    "reiko": "reiko",
    "union": "venn",
    "venn": "venn",
    "velvet": "velvet"
}


def scan_commlink_player_saves(player_dir: Optional[str] = None) -> Dict[str, Dict[str, str]]:
    """
    Scans CommLink6 player directory for character folders and returns mapping of
    canonical character IDs (reiko, velvet, venn, etc.) to folder & XML file paths.
    Inspects both metadata.properties and XML filenames.
    """
    target_dir = player_dir or DEFAULT_COMMLINK_PLAYER_DIR
    if not os.path.exists(target_dir):
        return {}

    saves = {}
    subdirs = [os.path.join(target_dir, d) for d in os.listdir(target_dir) if os.path.isdir(os.path.join(target_dir, d))]

    # Load configured character aliases from characters.yaml + built-in aliases
    configured_chars = get_character_configs()
    known_aliases = dict(KNOWN_CHAR_ALIASES)
    for cid, cfg in configured_chars.items():
        known_aliases[cid.lower()] = cid
        cname = cfg.get("name", "").lower()
        if cname:
            known_aliases[cname] = cid
        for al in cfg.get("aliases", []):
            known_aliases[str(al).lower()] = cid

    for sdir in subdirs:
        meta_path = os.path.join(sdir, "metadata.properties")
        meta_name = None
        meta_file = None
        if os.path.exists(meta_path):
            try:
                with open(meta_path, "r", encoding="utf-8", errors="ignore") as mf:
                    for line in mf:
                        line = line.strip()
                        if line.startswith("name="):
                            meta_name = line.split("=", 1)[1].strip()
                        elif ".file=" in line:
                            meta_file = line.split("=", 1)[1].strip()
            except Exception:
                pass

        xml_files = glob.glob(os.path.join(sdir, "*.xml"))
        # If metadata specified a file that exists, prioritize it
        if meta_file and os.path.exists(os.path.join(sdir, meta_file)):
            xml_files = [os.path.join(sdir, meta_file)]

        for xml_path in xml_files:
            filename = os.path.basename(xml_path)
            norm_name = filename.replace(".xml", "").lower().strip()

            cid = None
            # Check meta_name first
            if meta_name:
                mn_lower = meta_name.lower().strip()
                for alias, target_cid in known_aliases.items():
                    if alias in mn_lower or mn_lower in alias:
                        cid = target_cid
                        break

            if not cid:
                for alias, target_cid in known_aliases.items():
                    if alias in norm_name or norm_name in alias:
                        cid = target_cid
                        break

            if not cid:
                cid = norm_name.replace(" ", "_")

            saves[cid] = {
                "char_id": cid,
                "xml_filename": filename,
                "folder_path": sdir,
                "xml_path": xml_path,
                "metadata_path": meta_path if os.path.exists(meta_path) else None
            }

    return saves


def extract_commlink_stats(xml_path: str) -> Dict[str, Any]:
    """Extracts key balance and ledger stats from a CommLink6 XML save file."""
    if not os.path.exists(xml_path):
        return {}
    try:
        tree = ET.parse(xml_path)
        root = tree.getroot()
        contacts_el = root.find("contacts")
        rewards_el = root.find("rewards")
        return {
            "karma_free": root.get("karmaF", "0"),
            "karma_invested": root.get("karmaI", "0"),
            "nuyen": root.get("nuyen", "0"),
            "contacts_count": len(contacts_el.findall("contact")) if contacts_el is not None else 0,
            "rewards_count": len(rewards_el.findall("reward")) if rewards_el is not None else 0,
        }
    except Exception:
        return {}


def push_to_commlink(char_id: str, player_dir: Optional[str] = None, show_diff: bool = True) -> Tuple[bool, str]:
    """
    Export character sheet from sr6-core de novo and write the character save XML directly
    in CommLink6's player save directory, including session logs, contacts, and metadata.properties.
    """
    target_dir = player_dir or DEFAULT_COMMLINK_PLAYER_DIR
    saves = scan_commlink_player_saves(target_dir)

    cm = CharacterManager()
    char = cm.get_character(char_id)
    if not char or not char.get("data"):
        return False, f"Character data for '{char_id}' not found in master workspace."

    repo_path = char.get("config", {}).get("repo_path") or os.path.dirname(char.get("path", ""))
    identity = char["data"].get("identity", {})
    handle = identity.get("handle") or identity.get("name", char_id.title())

    # Generate clean de novo CommLink XML
    try:
        de_novo_xml = export_genesis_xml(
            char_data=char["data"],
            char_repo_path=repo_path
        )
    except Exception as e:
        return False, f"Failed generating de novo XML for '{char_id}': {e}"

    if char_id in saves:
        save_info = saves[char_id]
        xml_path = save_info["xml_path"]
        sdir = save_info["folder_path"]
        meta_path = save_info.get("metadata_path")

        before_stats = extract_commlink_stats(xml_path)

        # Write clean de novo XML
        with open(xml_path, "w", encoding="utf-8") as f:
            f.write(de_novo_xml)

        # Ensure metadata.properties is updated with character handle and file
        if meta_path and os.path.exists(meta_path):
            try:
                with open(meta_path, "r", encoding="utf-8", errors="ignore") as mf:
                    lines = mf.readlines()
                new_lines = []
                for line in lines:
                    if line.startswith("name="):
                        new_lines.append(f"name={handle}\n")
                    else:
                        new_lines.append(line)
                with open(meta_path, "w", encoding="utf-8") as mf:
                    mf.writelines(new_lines)
            except Exception:
                pass

        after_stats = extract_commlink_stats(xml_path)
        if show_diff:
            print_commlink_sync_diff(char_id, before_stats, after_stats)
        return True, f"Successfully synchronized de novo CommLink6 save at '{xml_path}'."

    else:
        # Provision a new save directory in CommLink
        char_uuid = identity.get("uuid") or str(uuid.uuid4())
        sdir = os.path.join(target_dir, char_uuid)
        os.makedirs(sdir, exist_ok=True)

        xml_filename = f"{handle}.xml"
        xml_path = os.path.join(sdir, xml_filename)
        meta_path = os.path.join(sdir, "metadata.properties")

        # Write metadata.properties scaffold
        meta_content = generate_commlink_metadata(
            char_data=char["data"],
            char_uuid=char_uuid,
            xml_filename=xml_filename
        )
        with open(meta_path, "w", encoding="utf-8") as mf:
            mf.write(meta_content)

        # Write de novo XML
        with open(xml_path, "w", encoding="utf-8") as f:
            f.write(de_novo_xml)

        after_stats = extract_commlink_stats(xml_path)
        if show_diff:
            print_commlink_sync_diff(char_id, {}, after_stats)
        return True, f"Provisioned new de novo CommLink6 save at '{xml_path}'."


def print_commlink_sync_diff(char_id: str, before: Dict[str, Any], after: Dict[str, Any]):
    """Renders a styled Rich table showing before/after sync changes."""
    try:
        from rich.console import Console
        from rich.table import Table
        console = Console()

        table = Table(title=f"🔄 CommLink6 GUI Save Sync: {char_id.upper()}", show_header=True)
        table.add_column("Field / Parameter", style="bold cyan")
        table.add_column("Previous XML Value", style="dim")
        table.add_column("Updated Campaign Value", style="bold green")

        table.add_row("Available Karma (karmaF)", str(before.get("karma_free", "N/A")), str(after.get("karma_free", "N/A")))
        table.add_row("Spent Karma (karmaI)", str(before.get("karma_invested", "N/A")), str(after.get("karma_invested", "N/A")))
        table.add_row("Nuyen Balance (nuyen)", f"¥{int(before.get('nuyen', 0)):,}" if str(before.get("nuyen")).isdigit() else str(before.get("nuyen")), f"¥{int(after.get('nuyen', 0)):,}" if str(after.get("nuyen")).isdigit() else str(after.get("nuyen")))
        table.add_row("Contacts Tracked", str(before.get("contacts_count", 0)), str(after.get("contacts_count", 0)))
        table.add_row("Mission Reward Logs", str(before.get("rewards_count", 0)), str(after.get("rewards_count", 0)))

        console.print(table)
    except Exception:
        pass


def sync_all_commlink_saves(player_dir: Optional[str] = None) -> List[Tuple[str, bool, str]]:
    """
    Scans all configured characters and updates matching CommLink GUI save files.
    """
    target_dir = player_dir or DEFAULT_COMMLINK_PLAYER_DIR
    saves = scan_commlink_player_saves(target_dir)
    results = []

    for cid in saves.keys():
        success, msg = push_to_commlink(cid, player_dir=target_dir)
        results.append((cid, success, msg))

    return results


push_all_to_commlink = sync_all_commlink_saves
