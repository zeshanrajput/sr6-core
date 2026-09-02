"""
Local Live-Sync HTTP & WebSocket Server for SR6 Tactical Dossier & Campaign HUD.
Exposes REST endpoints for character state sync, dice rolling, and combat resolution,
and serves the standalone mobile PWA over localhost.
"""

import os
import json
from http.server import HTTPServer, SimpleHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
from pathlib import Path
from typing import Dict, Any

from sr6core.character_manager import CharacterManager
from sr6core.exporters.mobile_json import export_mobile_json
from sr6core.simulation.dice import roll_pool
from sr6core.simulation.combat import CombatResolver
from sr6core.ledger.events import (
    KarmaAwardedEvent,
    KarmaSpentEvent,
    NuyenTransactionEvent,
    DamageAppliedEvent,
    AmmoExpendedEvent,
)
from sr6core.ledger.engine import CampaignEventLedger


class TacticalServerHandler(SimpleHTTPRequestHandler):
    """Custom HTTP handler serving PWA files and API endpoints."""

    def __init__(self, *args, **kwargs):
        base_dir = Path(__file__).resolve().parent.parent
        self.app_dir = base_dir / "app"
        super().__init__(*args, directory=str(self.app_dir), **kwargs)

    def _send_json(self, data: Any, status: int = 200):
        body = json.dumps(data, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

        if path in ("/", "/index.html"):
            cm = CharacterManager()
            bundle = {}
            for cid in ["reiko", "velvet", "venn"]:
                c_data = cm.get_character_data(cid)
                if c_data:
                    c_repo = cm.get_character_repo_dir(cid)
                    bundle[cid] = export_mobile_json(c_data, char_repo_path=c_repo)
            from sr6core.exporters.mobile_html import get_mobile_html_template
            html_content = get_mobile_html_template(bundle, initial_char_id="reiko")
            body = html_content.encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return

        elif path == "/api/characters":
            cm = CharacterManager()
            chars = cm.list_characters()
            return self._send_json({"characters": chars})

        elif path.startswith("/api/character/"):
            char_id = path.replace("/api/character/", "").strip("/")
            cm = CharacterManager()
            c_data = cm.get_character_data(char_id)
            if not c_data:
                return self._send_json({"error": f"Character '{char_id}' not found"}, status=404)
            c_repo = cm.get_character_repo_dir(char_id)
            m_json = export_mobile_json(c_data, char_repo_path=c_repo)
            return self._send_json(m_json)

        elif path == "/api/bundle":
            cm = CharacterManager()
            bundle = {}
            for cid in ["reiko", "velvet", "venn"]:
                c_data = cm.get_character_data(cid)
                if c_data:
                    c_repo = cm.get_character_repo_dir(cid)
                    bundle[cid] = export_mobile_json(c_data, char_repo_path=c_repo)
            return self._send_json({"characters": bundle})

        # Default static file serving from app/
        return super().do_GET()

    def do_POST(self):
        parsed = urlparse(self.path)
        path = parsed.path
        content_length = int(self.headers.get("Content-Length", 0))
        body_bytes = self.rfile.read(content_length)
        body = json.loads(body_bytes.decode("utf-8")) if body_bytes else {}

        if path == "/api/roll":
            pool = int(body.get("pool", 12))
            desc = body.get("description", "Action Test")
            is_exp = bool(body.get("is_exploding", False))
            buy_hits = bool(body.get("buy_hits", False))
            res = roll_pool(pool=pool, description=desc, is_exploding=is_exp, buy_hits=buy_hits)
            return self._send_json(res.model_dump())

        elif path == "/api/combat/attack":
            res = CombatResolver.resolve_attack(
                attacker_pool=int(body.get("attacker_pool", 12)),
                defender_pool=int(body.get("defender_pool", 8)),
                base_dv=int(body.get("base_dv", 4)),
                soak_pool=int(body.get("soak_pool", 0)),
                attacker_name=body.get("attacker_name", "Attacker"),
                defender_name=body.get("defender_name", "Defender"),
                weapon_name=body.get("weapon_name", "Weapon"),
                attacker_ar=int(body.get("attacker_ar", 0)),
                defender_dr=int(body.get("defender_dr", 0)),
                is_exploding=bool(body.get("is_exploding", False)),
            )
            return self._send_json(res.model_dump())

        return self._send_json({"error": "Endpoint not found"}, status=404)


def run_server(port: int = 8080, host: str = "0.0.0.0"):
    """Starts the tactical HTTP server."""
    server_address = (host, port)
    httpd = HTTPServer(server_address, TacticalServerHandler)
    print(f"\n============================================================")
    print(f"   SR6 TACTICAL DOSSIER & LIVE HUD SERVER RUNNING")
    print(f"============================================================")
    print(f"  • Local URL   : http://localhost:{port}")
    print(f"  • Network URL : http://{host}:{port}")
    print(f"  • API Base    : http://localhost:{port}/api/")
    print(f"============================================================\n")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down server...")
        httpd.server_close()
