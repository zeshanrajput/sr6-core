"""
Canonical SRM / CMP / SMH Missions Registry.
Loads and resolves mission metadata from reference/missions.yaml.
"""

import os
from pathlib import Path
from typing import Dict, Any, Optional
import yaml

_MISSIONS_REGISTRY: Optional[Dict[str, Dict[str, Any]]] = None


def _find_missions_file() -> Optional[Path]:
    candidates = [
        Path(__file__).resolve().parents[2] / "reference" / "missions.yaml",
        Path(__file__).resolve().parents[1] / "reference" / "missions.yaml",
        Path.cwd() / "reference" / "missions.yaml",
        Path.cwd().parent / "reference" / "missions.yaml",
        Path.cwd().parents[1] / "reference" / "missions.yaml",
    ]
    for c in candidates:
        if c.exists():
            return c
    return None


def get_missions_registry() -> Dict[str, Dict[str, Any]]:
    global _MISSIONS_REGISTRY
    if _MISSIONS_REGISTRY is not None:
        return _MISSIONS_REGISTRY

    fpath = _find_missions_file()
    if fpath and fpath.exists():
        try:
            with open(fpath, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f)
                if isinstance(data, dict):
                    _MISSIONS_REGISTRY = data
                    return _MISSIONS_REGISTRY
        except Exception:
            pass

    _MISSIONS_REGISTRY = {}
    return _MISSIONS_REGISTRY


def normalize_mission_code(code_or_title: str) -> str:
    """
    Normalizes variations like 'SRM 2081-01' -> 'SRM.2081.01',
    'CMP 2081-09' -> 'CMP.2081.09', 'SMH 2083-02' -> 'SMH.2083.02'.
    """
    s = code_or_title.strip()
    s_clean = s.replace(" ", ".").replace("-", ".")
    parts = [p for p in s_clean.split(".") if p]
    if len(parts) >= 3 and parts[0].upper() in ["SRM", "CMP", "SMH"]:
        return f"{parts[0].upper()}.{parts[1]}.{parts[2]}"
    if s.lower().startswith("cmp first taste"):
        return "CMP.2081.FT"
    if s.lower() == "build-a-runner":
        return "Build-A-Runner"
    return s


def get_mission(code_or_title: str) -> Optional[Dict[str, Any]]:
    """
    Resolves mission by code (SRM.2081.01, SRM 2081-01), or by title.
    """
    registry = get_missions_registry()
    if not registry:
        return None

    norm = normalize_mission_code(code_or_title)
    if norm in registry:
        return registry[norm]

    # Try case-insensitive key search
    norm_lower = norm.lower()
    for k, v in registry.items():
        if k.lower() == norm_lower:
            return v

    # Try matching title
    title_lower = code_or_title.strip().lower()
    for k, v in registry.items():
        if v.get("title", "").lower() == title_lower:
            return v
        if title_lower in v.get("title", "").lower():
            return v

    return None
