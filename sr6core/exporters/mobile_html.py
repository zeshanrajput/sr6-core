"""
Mobile HTML Application Exporter for SR6 Characters.
Generates an ultra-responsive, standalone, offline-ready mobile web application (PWA)
compiled with Vite + TypeScript, featuring dynamic wound penalty recalculation,
interactive condition monitors, one-tap ammo tracking, tactile cyberpunk dice roller,
and universal drill-down rule drawers.
"""

import os
import json
from pathlib import Path
from typing import Dict, Any, Optional

from sr6core.exporters.mobile_json import export_mobile_json


def get_mobile_html_template(character_data_bundle: Dict[str, Any], initial_char_id: str = "reiko") -> str:
    """
    Renders the complete self-contained HTML/CSS/JS mobile application
    with embedded character bundle data.
    """
    bundle_json_str = json.dumps(character_data_bundle, indent=2, ensure_ascii=False)

    # Path to compiled Vite singlefile distribution
    base_dir = Path(__file__).resolve().parent.parent.parent
    dist_html_path = base_dir / "app" / "index.html"

    if dist_html_path.exists():
        template = dist_html_path.read_text(encoding="utf-8")
        # Inject global state variables before the first script tag or </head>
        injection = f"""
  <script>
    window.__SR6_DATA_BUNDLE__ = {bundle_json_str};
    window.__SR6_INITIAL_CHAR__ = "{initial_char_id}";
  </script>
"""
        if "</head>" in template:
            return template.replace("</head>", f"{injection}\n</head>", 1)
        elif "<body>" in template:
            return template.replace("<body>", f"<body>\n{injection}", 1)
        else:
            return f"{injection}\n{template}"

    # Fallback minimal standalone shell if compiled template not present
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>SR6 Tactical Character Dossier</title>
  <script>
    window.__SR6_DATA_BUNDLE__ = {bundle_json_str};
    window.__SR6_INITIAL_CHAR__ = "{initial_char_id}";
  </script>
</head>
<body>
  <div id="app">
    <h1>SR6 Tactical Character Dossier</h1>
    <pre>{bundle_json_str}</pre>
  </div>
</body>
</html>
"""


def export_mobile_html(char_data: Dict[str, Any], char_id: str = "reiko", char_repo_path: Optional[str] = None) -> str:
    """
    Exports a standalone single-character mobile HTML application.
    """
    char_json = export_mobile_json(char_data, char_repo_path=char_repo_path)
    bundle = {char_id: char_json}
    return get_mobile_html_template(bundle, initial_char_id=char_id)
