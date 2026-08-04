"""
FastHTML Dashboard Application for Multi-Character SR6 Ecosystem.
"""

import os
import sys
import glob
import yaml
from fasthtml.common import *

from sr6core.rules_db import RulesDB
from sr6core.creation.priority import audit_priority_build
from sr6core.creation.point_buy import audit_point_buy
from sr6core.exporters.roll20_json import export_roll20_json
from sr6core.exporters.vtt_text import export_vtt_text


def find_characters(github_root="C:\\GitHub"):
    characters = {}
    if not os.path.exists(github_root):
        return characters

    for repo in os.listdir(github_root):
        repo_path = os.path.join(github_root, repo)
        if os.path.isdir(repo_path) and repo.startswith("sr6"):
            yaml_files = glob.glob(os.path.join(repo_path, "*_master.yaml"))
            for yf in yaml_files:
                try:
                    with open(yf, "r", encoding="utf-8") as f:
                        data = yaml.safe_load(f)
                    name = data.get("identity", {}).get("handle", repo)
                    characters[repo] = {"path": yf, "data": data, "name": name}
                except Exception:
                    pass
    return characters


def create_app():
    app, rt = fast_app(
        hdrs=(
            Style("""
                body { font-family: system-ui, -apple-system, sans-serif; background: #0f172a; color: #f8fafc; padding: 2rem; }
                .card { background: #1e293b; border: 1px solid #334155; border-radius: 8px; padding: 1.5rem; margin-bottom: 1.5rem; }
                .btn { background: #0284c7; color: white; border: none; padding: 0.5rem 1rem; border-radius: 4px; cursor: pointer; text-decoration: none; display: inline-block; margin-right: 0.5rem; }
                .btn:hover { background: #0369a1; }
                .badge { background: #10b981; color: white; padding: 0.2rem 0.5rem; border-radius: 4px; font-size: 0.8rem; }
                .warning { background: #f59e0b; color: white; padding: 0.2rem 0.5rem; border-radius: 4px; font-size: 0.8rem; }
                table { width: 100%; border-collapse: collapse; margin-top: 1rem; }
                th, td { padding: 0.5rem; text-align: left; border-bottom: 1px solid #334155; }
            """),
        )
    )

    rules_db = RulesDB()

    @rt("/")
    def get(selected: str = None):
        chars = find_characters()
        if not selected and chars:
            selected = list(chars.keys())[0]

        char_options = [Option(f"{info['name']} ({repo})", value=repo, selected=(repo == selected)) for repo, info in chars.items()]
        
        selected_info = chars.get(selected, {})
        char_data = selected_info.get("data", {})
        identity = char_data.get("identity", {})

        # Creation audit
        is_priority_valid, priority_warnings = audit_priority_build(char_data.get("creation_budget", {}))
        is_pointbuy_valid, pointbuy_warnings = audit_point_buy(char_data)

        return Titled(
            "SR6 Multi-Character Dashboard",
            Div(
                Form(
                    Label("Select Character Portfolio: ", For="selected"),
                    Select(*char_options, name="selected", id="selected", onchange="this.form.submit()"),
                    action="/", method="get"
                ),
                Class="card"
            ),
            Div(
                H2(identity.get("handle", "Unknown Character")),
                P(f"Real Name: {identity.get('real_name', 'N/A')} | Metatype: {identity.get('metatype', 'Human')} | Stream: {identity.get('stream', 'N/A')}"),
                Div(
                    A("Export Roll20 JSON", href=f"/export/roll20?char={selected}", target="_blank", Class="btn"),
                    A("Export VTT Text", href=f"/export/vtt?char={selected}", target="_blank", Class="btn"),
                ),
                Class="card"
            ),
            Div(
                H3("Character Creation Auditing"),
                P(Span("Priority Build: OK", Class="badge") if is_priority_valid else Span(f"Priority Warnings: {', '.join(priority_warnings)}", Class="warning")),
                P(Span("Point-Buy Build: OK", Class="badge") if is_pointbuy_valid else Span(f"Point-Buy Warnings: {', '.join(pointbuy_warnings)}", Class="warning")),
                Class="card"
            ),
            Div(
                H3("Rules Vault Quick Search"),
                Form(
                    Input(type="text", name="q", placeholder="Search rules (e.g. matrix, fading, drones)..."),
                    Button("Search", type="submit", Class="btn"),
                    action="/rules/search", method="get"
                ),
                Class="card"
            )
        )

    @rt("/export/roll20")
    def get_roll20(char: str):
        chars = find_characters()
        info = chars.get(char, {})
        json_data = export_roll20_json(info.get("data", {}))
        return Response(json_data, headers={"Content-Type": "application/json"})

    @rt("/export/vtt")
    def get_vtt(char: str):
        chars = find_characters()
        info = chars.get(char, {})
        txt_data = export_vtt_text(info.get("data", {}))
        return Response(txt_data, headers={"Content-Type": "text/plain"})

    @rt("/rules/search")
    def search_rules(q: str = ""):
        if not q or not q.strip():
            return Titled(
                "Rules Search Results",
                P("Please enter a search term."),
                Br(),
                A("Back to Dashboard", href="/", Class="btn")
            )

        results = rules_db.search_rules(q, limit=15)
        if not results:
            return Titled(
                f"Rules Search Results for '{q}'",
                P(f"No matching rules found for '{q}' in rules vault."),
                Br(),
                A("Back to Dashboard", href="/", Class="btn")
            )

        items = []
        for r in results:
            rule_id = r.get("id", "N/A")
            topic = r.get("topic") or "General Rule"
            source = r.get("source") or "SR6"
            page = r.get("page") or ""
            page_str = f" p.{page}" if page else ""
            items.append(Li(f"[{rule_id}] {topic} ({source}{page_str})"))

        return Titled(
            f"Rules Search Results for '{q}'",
            Ul(*items),
            Br(),
            A("Back to Dashboard", href="/", Class="btn")
        )

    return app


if __name__ == "__main__":
    app = create_app()
    app.run()
