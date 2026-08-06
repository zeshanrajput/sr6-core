"""
Unified Character Manager for SR6 Core master project.
Handles loading, auditing, and exporting character portfolios.
"""

import os
import glob
import yaml
from pathlib import Path
from typing import Dict, Any, List, Optional

from sr6core.config import get_character_configs, DEFAULT_GITHUB_ROOT
from sr6core.models import Character
from sr6core.creation.priority import audit_priority_build
from sr6core.creation.point_buy import audit_point_buy
from sr6core.exporters.roll20_json import export_roll20_json
from sr6core.exporters.vtt_text import export_vtt_text
from sr6core.exporters.genesis_xml import export_genesis_xml


class CharacterManager:
    def __init__(self, config_path: Optional[str] = None, github_root: str = DEFAULT_GITHUB_ROOT):
        self.config_path = config_path
        self.github_root = github_root
        self._character_configs = get_character_configs(config_path)

    def discover_characters(self) -> Dict[str, Dict[str, Any]]:
        """
        Loads configured character portfolios, falling back to auto-discovery in github_root.
        """
        characters = {}

        # 1. Configured characters
        for char_id, cfg in self._character_configs.items():
            repo_path = cfg.get("repo_path") or os.path.join(self.github_root, cfg.get("repo", f"sr6{char_id}"))
            master_file = cfg.get("master_yaml") or f"{char_id}_master.yaml"
            full_path = os.path.join(repo_path, master_file)

            data = None
            if os.path.exists(full_path):
                try:
                    with open(full_path, "r", encoding="utf-8") as f:
                        data = yaml.safe_load(f)
                except Exception as e:
                    print(f"[Warning] Error parsing YAML for {char_id} at {full_path}: {e}")

            name = cfg.get("name") or (data.get("identity", {}).get("handle") if data else char_id.title())
            characters[char_id] = {
                "id": char_id,
                "name": name,
                "path": full_path,
                "exists": data is not None,
                "data": data or {},
                "config": cfg
            }

        # 2. Fallback auto-discovery for unconfigured sr6 repos
        if os.path.exists(self.github_root):
            for repo in os.listdir(self.github_root):
                repo_path = os.path.join(self.github_root, repo)
                if os.path.isdir(repo_path) and repo.startswith("sr6") and repo != "sr6-core":
                    char_id = repo.replace("sr6", "")
                    if char_id not in characters:
                        yaml_files = glob.glob(os.path.join(repo_path, "*_master.yaml"))
                        for yf in yaml_files:
                            try:
                                with open(yf, "r", encoding="utf-8") as f:
                                    data = yaml.safe_load(f)
                                name = data.get("identity", {}).get("handle", char_id.title())
                                characters[char_id] = {
                                    "id": char_id,
                                    "name": name,
                                    "path": yf,
                                    "exists": True,
                                    "data": data,
                                    "config": {"repo": repo, "repo_path": repo_path}
                                }
                            except Exception:
                                pass

        return characters

    def list_characters(self) -> List[Dict[str, Any]]:
        chars = self.discover_characters()
        summary_list = []
        for char_id, info in chars.items():
            data = info.get("data", {})
            identity = data.get("identity", {})
            cfg = info.get("config", {})
            summary_list.append({
                "id": char_id,
                "name": info.get("name"),
                "metatype": identity.get("metatype") or cfg.get("metatype", "Unknown"),
                "role": cfg.get("role", "N/A"),
                "exists": info.get("exists", False),
                "path": info.get("path")
            })
        return summary_list

    def get_character(self, char_id: str) -> Optional[Dict[str, Any]]:
        chars = self.discover_characters()
        return chars.get(char_id)

    def get_character_data(self, char_id: str) -> Optional[Dict[str, Any]]:
        chars = self.discover_characters()
        info = chars.get(char_id)
        return info.get("data") if info else None

    def get_character_repo_dir(self, char_id: str) -> Optional[str]:
        chars = self.discover_characters()
        info = chars.get(char_id)
        if not info:
            return None
        cpath = info.get("path")
        return os.path.dirname(cpath) if cpath and os.path.isfile(cpath) else cpath

    def audit_character(self, char_id: str) -> Dict[str, Any]:
        data = self.get_character_data(char_id)
        if not data:
            return {"valid": False, "errors": [f"Character '{char_id}' data not found."]}

        cb = data.get("creation_budget", {})
        p_valid, p_warns = audit_priority_build(cb)
        pb_valid, pb_warns = audit_point_buy(data)

        return {
            "valid": p_valid and pb_valid,
            "warnings": p_warns + pb_warns
        }

    def load_character(self, char_id: str) -> Optional[Dict[str, Any]]:
        return self.get_character(char_id)

    def export_character(self, char_id: str, fmt: str = "xml") -> str:
        data = self.get_character_data(char_id)
        if not data:
            raise ValueError(f"Character data for '{char_id}' not found.")

        repo_path = self.get_character_repo_dir(char_id)
        fmt = fmt.lower()
        if fmt == "roll20" or fmt == "json":
            return export_roll20_json(data)
        elif fmt == "vtt" or fmt == "txt":
            return export_vtt_text(data)
        elif fmt == "cards":
            from sr6core.cards import export_character_card_deck
            md_deck, _ = export_character_card_deck(char_id)
            return md_deck
        elif fmt == "xml" or fmt == "genesis":
            return export_genesis_xml(data, char_repo_path=repo_path)
        else:
            raise ValueError(f"Unsupported export format '{fmt}'.")
