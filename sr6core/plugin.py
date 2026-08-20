"""
Plugin management utilities for SR6 Core Antigravity Agent Plugin.
Handles global installation, status inspection, and repository workspace configuration.
"""

import os
import sys
import shutil
import json
from pathlib import Path
from typing import Dict, Any, Tuple, Optional


def get_plugin_source_dir() -> Path:
    """Returns the path to the sr6-narrative plugin source directory inside sr6-core."""
    current_file = Path(__file__).resolve()
    # Path is sr6-core/sr6core/plugin.py -> parent is sr6core -> parent is sr6-core
    sr6_core_root = current_file.parent.parent
    plugin_dir = sr6_core_root / ".agents" / "plugins" / "sr6-narrative"
    return plugin_dir


def get_global_plugins_dir() -> Path:
    """Returns the global ~/.gemini/config/plugins directory."""
    home = Path.home()
    return home / ".gemini" / "config" / "plugins"


def get_global_sr6_plugin_dir() -> Path:
    """Returns the global ~/.gemini/config/plugins/sr6-narrative directory."""
    return get_global_plugins_dir() / "sr6-narrative"


def get_plugin_manifest(plugin_path: Path) -> Optional[Dict[str, Any]]:
    """Reads and parses plugin.json if it exists."""
    manifest_file = plugin_path / "plugin.json"
    if not manifest_file.exists():
        return None
    try:
        with open(manifest_file, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return None


def get_plugin_status() -> Dict[str, Any]:
    """Inspects local and global plugin installation status."""
    source_dir = get_plugin_source_dir()
    source_manifest = get_plugin_manifest(source_dir)

    global_dir = get_global_sr6_plugin_dir()
    global_installed = global_dir.exists()
    global_manifest = get_plugin_manifest(global_dir) if global_installed else None
    is_symlink = global_dir.is_symlink() if global_installed else False

    # Count skills in source
    skills_dir = source_dir / "skills"
    skills_count = len([d for d in skills_dir.iterdir() if d.is_dir()]) if skills_dir.exists() else 0

    return {
        "source_path": str(source_dir),
        "source_exists": source_dir.exists(),
        "source_version": source_manifest.get("version", "unknown") if source_manifest else None,
        "skills_count": skills_count,
        "global_path": str(global_dir),
        "global_installed": global_installed,
        "global_is_symlink": is_symlink,
        "global_version": global_manifest.get("version", "unknown") if global_manifest else None,
    }


def install_global_plugin(symlink: bool = False, force: bool = True) -> Tuple[bool, str]:
    """Installs the sr6-narrative plugin to ~/.gemini/config/plugins/sr6-narrative."""
    source_dir = get_plugin_source_dir()
    if not source_dir.exists():
        return False, f"Source plugin directory does not exist at {source_dir}"

    global_plugins_dir = get_global_plugins_dir()
    global_plugins_dir.mkdir(parents=True, exist_ok=True)

    target_dir = get_global_sr6_plugin_dir()

    if target_dir.exists() or target_dir.is_symlink():
        if not force:
            return False, f"Plugin already installed at {target_dir}. Use force=True to overwrite."
        if target_dir.is_symlink():
            target_dir.unlink()
        else:
            shutil.rmtree(target_dir)

    if symlink:
        try:
            # Create symlink or junction
            target_dir.symlink_to(source_dir, target_is_directory=True)
            return True, f"Symlinked {source_dir} -> {target_dir}"
        except OSError:
            # Fall back to copy if symlink privileges are not available
            shutil.copytree(source_dir, target_dir)
            return True, f"Copied {source_dir} -> {target_dir} (symlink fallback)"
    else:
        shutil.copytree(source_dir, target_dir)
        return True, f"Copied {source_dir} -> {target_dir}"


def configure_repo_plugin_inheritance(repo_path: str) -> Tuple[bool, str]:
    """Creates or updates .agents/plugins.json in a character repository."""
    target_repo = Path(repo_path).resolve()
    if not target_repo.exists():
        return False, f"Target directory does not exist: {target_repo}"

    agents_dir = target_repo / ".agents"
    agents_dir.mkdir(parents=True, exist_ok=True)

    plugins_json_path = agents_dir / "plugins.json"

    # Compute relative path from target .agents dir to sr6-core plugin dir
    source_dir = get_plugin_source_dir()
    try:
        rel_path = os.path.relpath(source_dir, start=target_repo).replace("\\", "/")
    except ValueError:
        rel_path = str(source_dir).replace("\\", "/")

    config = {
        "inherits": [
            {
                "path": rel_path
            }
        ]
    }

    with open(plugins_json_path, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=2)

    return True, f"Wrote {plugins_json_path} inheriting from '{rel_path}'"


def print_plugin_status_rich():
    """Prints a styled Rich status report for the plugin."""
    try:
        from rich.console import Console
        from rich.panel import Panel
        from rich.table import Table

        console = Console()
        status = get_plugin_status()

        table = Table(show_header=False, box=None)
        table.add_column("Key", style="bold cyan")
        table.add_column("Value", style="white")

        table.add_row("Plugin Name", "sr6-narrative-suite")
        table.add_row("Source Path", status["source_path"])
        table.add_row("Source Version", str(status["source_version"]))
        table.add_row("Skills Included", f"{status['skills_count']} skills")
        table.add_row("Global Install Path", status["global_path"])

        g_status = "[green]INSTALLED[/green]" if status["global_installed"] else "[yellow]NOT INSTALLED[/yellow]"
        if status["global_installed"]:
            g_type = " (Symlink)" if status["global_is_symlink"] else " (Copy)"
            g_status += g_type
        table.add_row("Global Status", g_status)

        panel = Panel(table, title="🤖 Antigravity Plugin Status: sr6-narrative-suite", border_style="blue")
        console.print(panel)
    except ImportError:
        status = get_plugin_status()
        print("\n=== Antigravity Plugin Status: sr6-narrative-suite ===")
        for k, v in status.items():
            print(f" {k:<20}: {v}")
        print()
