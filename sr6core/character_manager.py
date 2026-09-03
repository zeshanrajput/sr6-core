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
        Loads configured character portfolios, falling back to auto-discovery in github_root,
        CWD, and parent workspace directories.
        """
        characters = {}

        # 1. Configured characters with multi-candidate search
        legacy_aliases = {"reiko": ["yuriko", "sr6yuriko"], "venn": ["union", "sr6union"]}
        for char_id, cfg in self._character_configs.items():
            repo_name = cfg.get("repo", f"sr6{char_id}")
            master_file = cfg.get("master_yaml") or f"{char_id}_master.yaml"

            candidates = []
            if cfg.get("repo_path"):
                candidates.append(cfg.get("repo_path"))
            
            # Monorepo characters/ folder support (highest priority)
            candidates.append(os.path.join(os.path.dirname(os.path.dirname(__file__)), "characters", char_id))
            candidates.append(os.path.join(os.getcwd(), "characters", char_id))
            if self.github_root:
                candidates.append(os.path.join(self.github_root, "sr6-core", "characters", char_id))

            # Sibling and CWD candidates
            candidates.append(os.path.join(os.path.dirname(os.path.dirname(__file__)), repo_name))
            candidates.append(os.path.join(os.getcwd(), repo_name))
            if self.github_root:
                candidates.append(os.path.join(self.github_root, repo_name))
                candidates.append(os.path.join(self.github_root, char_id))

            # Workspace and CWD relative candidates
            cwd = os.getcwd()
            candidates.append(cwd)
            candidates.append(os.path.join(cwd, repo_name))
            candidates.append(os.path.join(cwd, "..", repo_name))
            candidates.append(os.path.join(cwd, "..", char_id))

            # Also check legacy alias candidate directories
            for alias in legacy_aliases.get(char_id, []):
                candidates.append(os.path.join(os.path.dirname(os.path.dirname(__file__)), "characters", alias))
                if self.github_root:
                    candidates.append(os.path.join(self.github_root, alias))
                    candidates.append(os.path.join(self.github_root, f"sr6{alias}"))
                candidates.append(os.path.join(cwd, "..", alias))
                candidates.append(os.path.join(cwd, "..", f"sr6{alias}"))

            matched_file = None
            resolved_repo_dir = None
            data = None

            for cand_dir in candidates:
                if not cand_dir or not os.path.exists(cand_dir):
                    continue
                cand_dir_abs = os.path.abspath(cand_dir)
                direct_file = os.path.join(cand_dir_abs, master_file)
                if os.path.isfile(direct_file):
                    matched_file = direct_file
                    resolved_repo_dir = cand_dir_abs
                    break

                # Glob search in candidate directory
                glob_matches = glob.glob(os.path.join(cand_dir_abs, f"*{char_id}*_master.yaml"))
                if not glob_matches and (os.path.basename(cand_dir_abs) in [repo_name, char_id]):
                    glob_matches = glob.glob(os.path.join(cand_dir_abs, "*_master.yaml"))

                if glob_matches:
                    matched_file = glob_matches[0]
                    resolved_repo_dir = cand_dir_abs
                    break

            if matched_file and os.path.exists(matched_file):
                try:
                    with open(matched_file, "r", encoding="utf-8") as f:
                        data = yaml.safe_load(f)
                except Exception as e:
                    print(f"[Warning] Error parsing YAML for {char_id} at {matched_file}: {e}")

            # Also load exceptions if available in rules/exceptions.yaml
            if data and resolved_repo_dir:
                try:
                    from sr6core.creation.exceptions_parser import ExceptionsRegistry
                    data["exceptions"] = ExceptionsRegistry.get_character_exceptions(char_id, repo_dir=resolved_repo_dir)
                except Exception:
                    pass

                # Ingest declared modifiers and collections from character_build.qmd / character_log.qmd / character_purchases.qmd
                try:
                    from sr6core.log_engine import get_log_totals
                    totals = get_log_totals(resolved_repo_dir)
                    if totals:
                        if "Modifiers" in totals and totals["Modifiers"]:
                            data.setdefault("modifiers", [])
                            existing_ids = {m.get("id") for m in data["modifiers"] if isinstance(m, dict)}
                            for dm in totals["Modifiers"]:
                                if dm.get("id") not in existing_ids:
                                    data["modifiers"].append(dm)
                                    existing_ids.add(dm.get("id"))

                        for field_key in ["Spells", "Complex_Forms", "Adept_Powers", "Metamagic", "Echoes", "Knowledge_Skills"]:
                            if field_key in totals and totals[field_key]:
                                yaml_key = field_key.lower()
                                data.setdefault(yaml_key, [])
                                existing_names = {x.get("name", "").lower() for x in data[yaml_key] if isinstance(x, dict)}
                                for item in totals[field_key]:
                                    if item.get("name", "").lower() not in existing_names:
                                        data[yaml_key].append(item)
                                        existing_names.add(item.get("name", "").lower())
                        # Sync dynamic runtime balances (Karma, Nuyen, Contacts) from single source of truth log
                        data.setdefault("identity", {})
                        if "Karma" in totals:
                            data["identity"]["karma"] = totals["Karma"]
                        if "Nuyen" in totals:
                            data["identity"]["nuyen"] = totals["Nuyen"]
                        if "Contacts" in totals and totals["Contacts"]:
                            data.setdefault("contacts", [])
                            existing_contact_names = {c.get("name", "").lower() for c in data["contacts"] if isinstance(c, dict)}
                            for c in totals["Contacts"]:
                                if c.get("name", "").lower() not in existing_contact_names:
                                    data["contacts"].append(c)
                                    existing_contact_names.add(c.get("name", "").lower())
                except Exception:
                    pass

            full_path = matched_file or os.path.join(self.github_root, repo_name, master_file)
            name = cfg.get("name") or (data.get("identity", {}).get("handle") if data else char_id.title())
            characters[char_id] = {
                "id": char_id,
                "name": name,
                "path": full_path,
                "repo_dir": resolved_repo_dir or (os.path.dirname(full_path) if os.path.isfile(full_path) else full_path),
                "exists": data is not None,
                "data": data or {},
                "config": cfg
            }

        # 2. Fallback auto-discovery for unconfigured or missing sr6 repos
        search_roots = [self.github_root]
        cwd_parent = os.path.abspath(os.path.join(os.getcwd(), ".."))
        if cwd_parent not in search_roots and os.path.exists(cwd_parent):
            search_roots.append(cwd_parent)

        alias_map = {"yuriko": "reiko", "union": "venn"}
        ignored_repos = {"sr6-core", "sr6narrator", "sr6lglass"}

        for root in search_roots:
            if not root or not os.path.exists(root):
                continue
            for entry in os.listdir(root):
                repo_path = os.path.join(root, entry)
                if os.path.isdir(repo_path) and entry.startswith("sr6") and entry not in ignored_repos:
                    raw_id = entry.replace("sr6", "").lower()
                    canonical_id = alias_map.get(raw_id, raw_id)
                    # If this character or its canonical alias is already loaded, skip it to avoid duplicates
                    if canonical_id in characters and characters[canonical_id].get("exists"):
                        continue
                    if raw_id not in characters or not characters[raw_id].get("exists"):
                        yaml_files = glob.glob(os.path.join(repo_path, "*_master.yaml"))
                        for yf in yaml_files:
                            try:
                                with open(yf, "r", encoding="utf-8") as f:
                                    data = yaml.safe_load(f)
                                name = data.get("identity", {}).get("handle", canonical_id.title())
                                characters[canonical_id] = {
                                    "id": canonical_id,
                                    "name": name,
                                    "path": yf,
                                    "repo_dir": repo_path,
                                    "exists": True,
                                    "data": data,
                                    "config": {"repo": entry, "repo_path": repo_path}
                                }
                                break
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
        if char_id in chars:
            return chars[char_id]
        # Backward compatibility alias map
        alias_map = {"yuriko": "reiko", "union": "venn"}
        if char_id.lower() in alias_map:
            return chars.get(alias_map[char_id.lower()])
        return None

    def get_character_data(self, char_id: str) -> Optional[Dict[str, Any]]:
        info = self.get_character(char_id)
        return info.get("data") if info else None

    def get_character_repo_dir(self, char_id: str) -> Optional[str]:
        info = self.get_character(char_id)
        if not info:
            return None
        return info.get("repo_dir") or (os.path.dirname(info["path"]) if info.get("path") and os.path.isfile(info["path"]) else info.get("path"))


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

    def clean_output_directory(self, repo_path: str):
        """Prunes legacy or unorganized files from the root of output/ folder."""
        out_dir = os.path.join(repo_path, "output")
        if not os.path.exists(out_dir):
            return

        # Legacy file patterns and obsolete export folders to clean from output root
        for entry in os.listdir(out_dir):
            entry_path = os.path.join(out_dir, entry)
            if os.path.isfile(entry_path):
                # If it is a root loose file, remove it so output is cleanly grouped in subfolders
                try:
                    os.remove(entry_path)
                except Exception:
                    pass
            elif entry in ["xml", "pdf", "cards"] and os.path.isdir(entry_path):
                import shutil
                try:
                    shutil.rmtree(entry_path)
                except Exception:
                    pass

    def export_character(self, char_id: str, fmt: str = "xml", output_path: Optional[str] = None) -> Any:
        data = self.get_character_data(char_id)
        if not data:
            raise ValueError(f"Character data for '{char_id}' not found.")

        repo_path = self.get_character_repo_dir(char_id)
        fmt = fmt.lower()
        if fmt in ["roll20", "json"]:
            return export_roll20_json(data, char_repo_path=repo_path)
        elif fmt in ["vtt", "txt", "base"]:
            return export_vtt_text(data)
        elif fmt == "text_modular":
            from sr6core.exporters.vtt_text import export_modular_text_sheets
            return export_modular_text_sheets(data, char_id, char_repo_path=repo_path)
        elif fmt in ["xml", "genesis"]:
            return export_genesis_xml(data, char_repo_path=repo_path)
        elif fmt in ["mobile", "mobile_html", "html"]:
            from sr6core.exporters.mobile_html import export_mobile_html
            return export_mobile_html(data, char_id=char_id, char_repo_path=repo_path)
        elif fmt in ["mobile_json"]:
            from sr6core.exporters.mobile_json import export_mobile_json
            return export_mobile_json(data, char_repo_path=repo_path)
        else:
            raise ValueError(f"Unsupported export format '{fmt}'.")

