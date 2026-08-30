"""
Configuration loader module for SR6 Core master project.
Manages supported character portfolios, workspace paths, and CommLink user directories.
Enables cross-platform environment variable overrides for custom home folders and character rosters.
"""

import os
import yaml
from pathlib import Path
from typing import Dict, Any, Optional

DEFAULT_CONFIG_FILENAME = "characters.yaml"

# Default workspace root (e.g. C:\GitHub or user's code root)
def get_default_workspace_root() -> str:
    env_root = os.getenv("SR6_WORKSPACE_ROOT") or os.getenv("GITHUB_ROOT")
    if env_root and os.path.exists(env_root):
        return env_root

    # Check if parent of sr6-core directory exists
    parent_dir = Path(__file__).resolve().parent.parent.parent
    if parent_dir.exists() and (parent_dir / "sr6-core").exists():
        return str(parent_dir)

    # Check parent of current working directory if sibling repos exist
    cwd_parent = Path.cwd().parent
    if cwd_parent.exists() and any((cwd_parent / d).exists() for d in ["sr6-core", "sr6velvet", "sr6reiko", "sr6venn", "sr6yuriko", "sr6union"]):
        return str(cwd_parent)

    # Check current working directory
    if Path.cwd().exists() and (Path.cwd() / "sr6-core").exists():
        return str(Path.cwd())

    if os.path.exists(r"C:\GitHub"):
        return r"C:\GitHub"

    return str(Path.cwd())



# Default CommLink6 player saves directory (e.g. C:\Users\<user>\CommLink6\player\myself\shadowrun6)
def get_default_commlink_dir() -> str:
    env_commlink = os.getenv("COMMLINK_PLAYER_DIR") or os.getenv("SR6_COMMLINK_DIR")
    if env_commlink and os.path.exists(env_commlink):
        return env_commlink

    user_home = Path.home()
    default_user_dir = user_home / "CommLink6" / "player" / "myself" / "shadowrun6"
    if default_user_dir.exists():
        return str(default_user_dir)

    # Legacy fallback
    fallback = r"C:\Users\zesha\CommLink6\player\myself\shadowrun6"
    if os.path.exists(fallback):
        return fallback

    return str(default_user_dir)


DEFAULT_GITHUB_ROOT = get_default_workspace_root()
DEFAULT_COMMLINK_PLAYER_DIR = get_default_commlink_dir()


def get_default_config_path() -> Path:
    cwd_path = Path.cwd() / DEFAULT_CONFIG_FILENAME
    if cwd_path.exists():
        return cwd_path

    module_dir = Path(__file__).resolve().parent.parent / DEFAULT_CONFIG_FILENAME
    if module_dir.exists():
        return module_dir

    return Path(get_default_workspace_root()) / "sr6-core" / DEFAULT_CONFIG_FILENAME


def load_config(config_path: Optional[str] = None) -> Dict[str, Any]:
    """
    Load character configuration from YAML file.
    """
    target_path = Path(config_path) if config_path else get_default_config_path()

    if not target_path.exists():
        return {"characters": {}}

    try:
        with open(target_path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}
            return data
    except Exception as e:
        print(f"[Warning] Failed to read configuration from {target_path}: {e}")
        return {"characters": {}}


def get_character_configs(config_path: Optional[str] = None) -> Dict[str, Dict[str, Any]]:
    """
    Returns dictionary of configured character entries.
    """
    cfg = load_config(config_path)
    return cfg.get("characters", {})


def get_character_config(char_id: str, config_path: Optional[str] = None) -> Optional[Dict[str, Any]]:
    """
    Returns specific character configuration dictionary by ID.
    """
    chars = get_character_configs(config_path)
    return chars.get(char_id)
