"""
CommLink6 Player Save Scanner & Automated Roundtrip Sync Engine for SR6 Core.
Scans CommLink6 player character folders and enables two-way automated syncing between CommLink6 GUI and sr6-core.
"""

import os
import glob
import sqlite3
import xml.etree.ElementTree as ET
from typing import Dict, Any, List, Optional, Tuple

from sr6core.config import DEFAULT_COMMLINK_PLAYER_DIR, get_character_configs
from sr6core.character_manager import CharacterManager
from sr6core.exporters.genesis_xml import export_genesis_xml, patch_genesis_xml


def scan_commlink_player_saves(player_dir: Optional[str] = None) -> Dict[str, Dict[str, str]]:
    """
    Scans CommLink6 player directory for character folders and returns mapping of
    character IDs (yuriko, velvet, union, etc.) to XML file paths.
    """
    target_dir = player_dir or DEFAULT_COMMLINK_PLAYER_DIR
    if not os.path.exists(target_dir):
        return {}

    saves = {}
    subdirs = [os.path.join(target_dir, d) for d in os.listdir(target_dir) if os.path.isdir(os.path.join(target_dir, d))]

    # Load configured character aliases from characters.yaml
    configured_chars = get_character_configs()
    known_aliases = {}
    for cid, cfg in configured_chars.items():
        known_aliases[cid.lower()] = cid
        cname = cfg.get("name", "").lower()
        if cname:
            known_aliases[cname] = cid

    for sdir in subdirs:
        xml_files = glob.glob(os.path.join(sdir, "*.xml"))
        for xml_path in xml_files:
            filename = os.path.basename(xml_path)
            norm_name = filename.replace(".xml", "").lower().strip()

            cid = None
            for alias, target_cid in known_aliases.items():
                if alias in norm_name:
                    cid = target_cid
                    break

            if not cid:
                cid = norm_name.replace(" ", "_")

            saves[cid] = {
                "char_id": cid,
                "xml_filename": filename,
                "folder_path": sdir,
                "xml_path": xml_path
            }

    return saves


def push_to_commlink(char_id: str, player_dir: Optional[str] = None) -> Tuple[bool, str]:
    """
    Export character sheet from sr6-core and overwrite the character save XML directly
    in CommLink6's player save directory, including session logs and contacts.
    """
    target_dir = player_dir or DEFAULT_COMMLINK_PLAYER_DIR
    saves = scan_commlink_player_saves(target_dir)

    if char_id not in saves:
        return False, f"Character save for '{char_id}' not found in CommLink player directory '{target_dir}'."

    save_info = saves[char_id]
    xml_path = save_info["xml_path"]

    cm = CharacterManager()
    char = cm.get_character(char_id)
    if not char or not char.get("data"):
        return False, f"Character data for '{char_id}' not found in master workspace."

    repo_path = char.get("config", {}).get("repo_path") or os.path.dirname(char.get("path", ""))

    success = patch_genesis_xml(
        input_xml_path=xml_path,
        char_data=char["data"],
        output_xml_path=xml_path,
        char_repo_path=repo_path
    )

    if success:
        return True, f"Successfully patched CommLink6 save at '{xml_path}'."
    else:
        return False, f"Failed to patch CommLink6 save at '{xml_path}'."


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
