"""
Model Context Protocol (MCP) Server for SR6 Core.
Provides native Agent tools, resources, and prompts over stdio for Shadowrun 6e rules lookups,
Gemini RAG queries, character auditing, prose linting, multi-axis evaluations, and campaign state tracking.
"""

import sys
import os
import json
import traceback
from pathlib import Path
from typing import Dict, Any, List, Optional
from sr6core.character_manager import CharacterManager
from sr6core.evaluator import evaluate_chapter_draft, format_scorecard_markdown
from sr6core.ledger_parser import parse_combat_ledger_prose, format_ledger_patch_markdown


TOOLS_DEFINITIONS: List[Dict[str, Any]] = [
    {
        "name": "sr6_search_rules",
        "description": "Searches Shadowrun 6e rules, spells, qualities, cyberware, weapons, and gear. Returns enriched stat blocks with official book and page citations [Book, Page].",
        "inputSchema": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Item name, quality, spell, weapon, or rule topic to look up (e.g. 'fading', 'ambidextrous', 'ares predator vi', 'skinlink')."
                }
            },
            "required": ["query"]
        }
    },
    {
        "name": "sr6_query_rag",
        "description": "Queries the Shadowrun 6e AI Rules Assistant with SRM 4-Level Authority ranking, book citations, and optional runner dossier context.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "prompt": {
                    "type": "string",
                    "description": "The rules question or mechanics query (e.g. 'How does Matrix technomancer submersion work?')."
                },
                "char_id": {
                    "type": "string",
                    "description": "Optional active character ID ('yuriko', 'velvet', 'union') to inject runner attributes and active gear into context."
                },
                "no_ai": {
                    "type": "boolean",
                    "description": "If true, retrieves only authoritative context passages without invoking the Gemini generative model."
                }
            },
            "required": ["prompt"]
        }
    },
    {
        "name": "sr6_lint_prose",
        "description": "Lints a narrative chapter (.qmd) for ellipses density ceiling (<= 0.6 per 300 words), forbidden AI slop buzzwords, cognitive buffer verbs, and markdown style issues.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "file_path": {
                    "type": "string",
                    "description": "Path to the target chapter markdown file (e.g. 'chapters/character_log.qmd')."
                }
            },
            "required": ["file_path"]
        }
    },
    {
        "name": "sr6_evaluate_draft",
        "description": "Performs unified 7-axis evaluation (voice, pacing, agency, worldbuilding, no-ai-slop, continuity, rules) with tier-calibrated scoring (Tier 1: 9.0, Tier 2: 8.5, Tier 3: 8.0) and generates a Markdown scorecard.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "text_or_path": {
                    "type": "string",
                    "description": "Raw draft text or file path to target .qmd chapter."
                },
                "tier": {
                    "type": "integer",
                    "enum": [1, 2, 3],
                    "default": 2,
                    "description": "Chapter Tier (1=Keystone 9.0 min, 2=Narrative Evolution 8.5 min, 3=Atmospheric Bridge 8.0 min)."
                },
                "char_id": {
                    "type": "string",
                    "description": "Optional character ID ('yuriko', 'velvet', 'union') for voice spec calibration."
                }
            },
            "required": ["text_or_path"]
        }
    },
    {
        "name": "sr6_parse_combat_ledger",
        "description": "Scans chapter prose and Quarto cells for fired ammo, physical/stun damage taken, drain/fading suffered, and rewards, generating a proposed YAML patch for character_master.yaml.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "text_or_path": {
                    "type": "string",
                    "description": "Raw chapter text or file path to target .qmd file."
                }
            },
            "required": ["text_or_path"]
        }
    },
    {
        "name": "sr6_audit_character",
        "description": "Performs deep item-by-item creation & tabletop validation on a character dossier. Validates Karma math, positive/negative qualities balance, and attribute caps.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "char_id": {
                    "type": "string",
                    "description": "Character ID (e.g. 'yuriko', 'velvet', 'union') or path to master YAML file."
                }
            },
            "required": ["char_id"]
        }
    },
    {
        "name": "sr6_check_continuity",
        "description": "Audits campaign narrative logs for Karma/Nuyen lifetime totals, active sprite lifespans, damage tracks, and contact loyalty changes.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "repo_path": {
                    "type": "string",
                    "description": "Path to the character repository (defaults to current directory '.')."
                }
            }
        }
    },
    {
        "name": "sr6_get_item_card",
        "description": "Retrieves the complete markdown item reference card for a specific quality, weapon, spell, cyberware, vehicle, or program.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "category": {
                    "type": "string",
                    "enum": ["quality", "weapon", "spell", "cyberware", "vehicle", "program", "armor", "gear"],
                    "description": "Category of the item."
                },
                "item_id": {
                    "type": "string",
                    "description": "The exact ID or name of the item (e.g. 'ambidextrous', 'fireball', 'wired_reflexes_1')."
                }
            },
            "required": ["category", "item_id"]
        }
    }
]

RESOURCES_DEFINITIONS: List[Dict[str, Any]] = [
    {
        "uri": "sr6://characters/yuriko/master",
        "name": "Yuriko Master Character Dossier",
        "description": "Full YAML dossier for Yuriko Star (Technoshaman/Rigger).",
        "mimeType": "application/x-yaml"
    },
    {
        "uri": "sr6://characters/velvet/master",
        "name": "Velvet Master Character Dossier",
        "description": "Full YAML dossier for Velvet (Social Infiltrator/Combat Adept).",
        "mimeType": "application/x-yaml"
    },
    {
        "uri": "sr6://characters/union/master",
        "name": "Union Master Character Dossier",
        "description": "Full YAML dossier for Union (Street Sam/Decker).",
        "mimeType": "application/x-yaml"
    },
    {
        "uri": "sr6://campaign/contacts",
        "name": "Official SRM & Active Campaign Contacts",
        "description": "Active campaign contacts across portfolios with Connection/Loyalty ratings.",
        "mimeType": "application/json"
    },
    {
        "uri": "sr6://rules/summary",
        "name": "SR6 Rules Database & Dataset Status",
        "description": "Summary of indexed books, record counts, and authority levels.",
        "mimeType": "application/json"
    }
]

PROMPTS_DEFINITIONS: List[Dict[str, Any]] = [
    {
        "name": "sr6_audit_chapter",
        "description": "Runs a full 7-axis narrative audit on a chapter file with tier-calibrated scoring.",
        "arguments": [
            {
                "name": "file_path",
                "description": "Path to the .qmd chapter file.",
                "required": True
            },
            {
                "name": "tier",
                "description": "Target tier (1=Keystone, 2=Narrative Evolution, 3=Atmospheric Bridge).",
                "required": False
            }
        ]
    },
    {
        "name": "sr6_draft_scene",
        "description": "Generates a scene draft following narrative director 4-beat structure and anti-slop rules.",
        "arguments": [
            {
                "name": "prompt",
                "description": "Scene beat sheet, friction point, or narrative objective.",
                "required": True
            },
            {
                "name": "char_id",
                "description": "Target character ID (yuriko, velvet, union).",
                "required": True
            },
            {
                "name": "tier",
                "description": "Scene tier (1, 2, or 3).",
                "required": False
            }
        ]
    },
    {
        "name": "sr6_sync_portfolio",
        "description": "Performs deep audit, regenerates multi-format sheets, and syncs CommLink6 saves.",
        "arguments": [
            {
                "name": "char_id",
                "description": "Optional specific character ID to sync (defaults to all).",
                "required": False
            }
        ]
    }
]


def handle_search_rules(arguments: Dict[str, Any]) -> str:
    from sr6core.rules_db import RulesDB
    query = arguments.get("query", "").strip()
    if not query:
        return "Error: query parameter is required."

    db = RulesDB()
    enriched = db.get_enriched_item(query)
    if enriched:
        output = [
            f"# Enriched Rule & Item Card: {enriched['name']}",
            f"- **ID**: `{enriched['id']}`",
            f"- **Category**: {enriched['item_type'].upper()}"
        ]
        if enriched.get("commlink_data"):
            cdata = enriched["commlink_data"]
            stats = [f"**{k}**: {v}" for k, v in cdata.items() if k not in ["raw_xml"] and v is not None]
            output.append(f"- **CommLink6 Stats**: {', '.join(stats)}")
        if enriched.get("rules_vault"):
            v = enriched["rules_vault"]
            output.append(f"- **Rulebook Citation**: *{v.get('source', 'SR6')}* (Page {v.get('page', 'N/A')}) [Authority Level {v.get('authority_level', 3)}]")
            if v.get("content"):
                output.append(f"\n### Rules Text\n{v['content']}")
        return "\n".join(output)

    results = db.search_rules(query)
    if not results:
        return f"No rules or dataset entries found for '{query}'."

    output = [f"### Rules Search Results for '{query}' ({len(results)} matches):"]
    for r in results[:10]:
        output.append(f"- **[{r.get('id')}] {r.get('topic')}** (*{r.get('source', 'SR6')}* p.{r.get('page', 'N/A')}) [Auth Level {r.get('authority_level', 3)}]")
    return "\n".join(output)


def handle_query_rag(arguments: Dict[str, Any]) -> str:
    from sr6core.rag import RAGEngine
    prompt = arguments.get("prompt", "").strip()
    char_id = arguments.get("char_id")
    no_ai = arguments.get("no_ai", False)

    if not prompt:
        return "Error: prompt parameter is required."

    rag = RAGEngine()
    res = rag.query(prompt, char_id=char_id, use_ai=not no_ai)

    output = []
    if res.get("ai_response"):
        output.append(f"### Rules AI Assistant Response\n{res['ai_response']}\n")

    output.append(f"### Authoritative Rules Context ({len(res.get('contexts', []))} sources cited):")
    for i, c in enumerate(res.get("contexts", [])[:5], 1):
        output.append(f"**[{i}] {c.get('topic', 'Rule')}** (*{c.get('source', 'SR6')}* p.{c.get('page', 'N/A')}) [Authority Level {c.get('authority_level', 3)}]")
        text_preview = c.get('text', '').strip().replace('\n', ' ')
        if len(text_preview) > 200:
            text_preview = text_preview[:200] + "..."
        output.append(f"> {text_preview}\n")

    return "\n".join(output)


def handle_lint_prose(arguments: Dict[str, Any]) -> str:
    from sr6core.linter import analyze_prose
    file_path = arguments.get("file_path", "").strip()
    if not file_path:
        return "Error: file_path parameter is required."

    report, err = analyze_prose(file_path)
    if err:
        return f"Error analyzing prose: {err}"

    output = [
        f"### Prose Lint Report: `{file_path}`",
        f"- **Word Count**: {report.get('word_count', 0):,} words",
        f"- **Ellipses Count**: {report.get('ellipses_count', 0)} (Density: {report.get('ellipses_per_300', 0.0):.2f} / 300 words, Budget: <= 0.60)",
        f"- **Ellipses Status**: {'[PASS]' if report.get('ellipses_valid') else '[FAIL - EXCEEDS BUDGET]'}",
        f"- **Forbidden Buzzwords**: {len(report.get('buzzwords_found', []))} violations",
        f"- **Cognitive Buffer Verbs**: {len(report.get('cognitive_buffers_found', []))} occurrences"
    ]

    if report.get("buzzwords_found"):
        output.append("\n#### Forbidden Buzzwords Detected:")
        for b in report["buzzwords_found"][:10]:
            output.append(f"- Line {b.get('line')}: `{b.get('word')}` -> {b.get('snippet')}")

    if report.get("redlines"):
        output.append("\n#### Prose Redlines & Suggestions:")
        for r in report["redlines"][:10]:
            output.append(f"- {r}")

    return "\n".join(output)


def handle_evaluate_draft(arguments: Dict[str, Any]) -> str:
    text_or_path = arguments.get("text_or_path", "").strip()
    tier = int(arguments.get("tier", 2))
    char_id = arguments.get("char_id")

    if not text_or_path:
        return "Error: text_or_path parameter is required."

    report = evaluate_chapter_draft(text_or_path, tier=tier, char_id=char_id)
    return format_scorecard_markdown(report)


def handle_parse_combat_ledger(arguments: Dict[str, Any]) -> str:
    text_or_path = arguments.get("text_or_path", "").strip()
    if not text_or_path:
        return "Error: text_or_path parameter is required."

    report = parse_combat_ledger_prose(text_or_path)
    return format_ledger_patch_markdown(report)


def handle_audit_character(arguments: Dict[str, Any]) -> str:
    from sr6core.creation.deep_audit import deep_audit_character
    char_id = arguments.get("char_id", "").strip()
    if not char_id:
        return "Error: char_id parameter is required."

    report = deep_audit_character(char_id)
    output = [
        f"### Deep Character Audit: `{char_id}`",
        f"- **Validation Status**: {'[PASS]' if report.get('valid') else '[WARNINGS DETECTED]'}",
        f"- **Positive Qualities Karma**: {report.get('total_pos_karma', 0)}",
        f"- **Negative Qualities Karma**: {report.get('total_neg_karma', 0)}"
    ]

    if report.get("warnings"):
        output.append(f"\n#### Audit Warnings ({len(report['warnings'])}):")
        for w in report["warnings"]:
            output.append(f"- {w}")

    return "\n".join(output)


def handle_check_continuity(arguments: Dict[str, Any]) -> str:
    from sr6core.continuity_engine import build_continuity_report
    repo_path = arguments.get("repo_path", ".").strip() or "."

    report, err = build_continuity_report(repo_path)
    if err:
        return f"Error checking continuity: {err}"

    output = [
        f"### Campaign Continuity Report: `{repo_path}`",
        f"- **Chapters Scanned**: {len(report.get('chapters', []))}",
        f"- **Net Karma Total**: {report.get('net_karma', 0)}",
        f"- **Net Nuyen Total**: ¥{report.get('net_nuyen', 0):,}",
        f"- **Active Sprites**: {len(report.get('active_sprites', []))}"
    ]

    if report.get("contacts"):
        output.append(f"\n#### Active Contacts ({len(report['contacts'])}):")
        for cname, cinfo in report["contacts"].items():
            output.append(f"- **{cname}**: Loyalty {cinfo.get('loyalty', 1)}, Connection {cinfo.get('connection', 1)}")

    return "\n".join(output)


def handle_get_item_card(arguments: Dict[str, Any]) -> str:
    from sr6core.cards import get_item_card
    category = arguments.get("category", "").strip()
    item_id = arguments.get("item_id", "").strip()

    if not category or not item_id:
        return "Error: category and item_id parameters are required."

    card = get_item_card(category, item_id)
    if not card or not card.get("markdown"):
        return f"No item card found for category '{category}' and ID '{item_id}'."

    return card["markdown"]


TOOL_HANDLERS = {
    "sr6_search_rules": handle_search_rules,
    "sr6_query_rag": handle_query_rag,
    "sr6_lint_prose": handle_lint_prose,
    "sr6_evaluate_draft": handle_evaluate_draft,
    "sr6_parse_combat_ledger": handle_parse_combat_ledger,
    "sr6_audit_character": handle_audit_character,
    "sr6_check_continuity": handle_check_continuity,
    "sr6_get_item_card": handle_get_item_card,
}


def handle_read_resource(uri: str) -> Optional[Dict[str, Any]]:
    """Resolves and returns contents for an sr6:// resource URI."""
    cm = CharacterManager()

    if uri.startswith("sr6://characters/"):
        parts = uri.replace("sr6://characters/", "").split("/")
        cid = parts[0]
        res_type = parts[1] if len(parts) > 1 else "master"

        char_info = cm.get_character(cid)
        if not char_info:
            return None

        if res_type == "master":
            yaml_path = char_info.get("path")
            if yaml_path and os.path.exists(yaml_path):
                with open(yaml_path, "r", encoding="utf-8") as f:
                    return {"uri": uri, "mimeType": "application/x-yaml", "text": f.read()}
        elif res_type == "voice_spec":
            repo_dir = char_info.get("repo_path")
            voice_path = os.path.join(repo_dir, "reference", "voice_spec.md")
            if os.path.exists(voice_path):
                with open(voice_path, "r", encoding="utf-8") as f:
                    return {"uri": uri, "mimeType": "text/markdown", "text": f.read()}

    elif uri == "sr6://campaign/contacts":
        from sr6core.contacts import CANONICAL_CONTACTS
        return {
            "uri": uri,
            "mimeType": "application/json",
            "text": json.dumps(CANONICAL_CONTACTS, indent=2)
        }

    elif uri == "sr6://rules/summary":
        from sr6core.dataset_compiler import get_dataset_info
        info = get_dataset_info()
        return {
            "uri": uri,
            "mimeType": "application/json",
            "text": json.dumps(info, indent=2)
        }

    return None


def handle_get_prompt(prompt_name: str, arguments: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Returns pre-engineered prompt messages for MCP prompts/get."""
    if prompt_name == "sr6_audit_chapter":
        fpath = arguments.get("file_path", "chapters/character_log.qmd")
        tier = arguments.get("tier", "2")
        return {
            "description": f"Audit chapter {fpath} across 7 dimensions (Tier {tier})",
            "messages": [
                {
                    "role": "user",
                    "content": {
                        "type": "text",
                        "text": f"Please evaluate the chapter at `{fpath}` against all 7 sub-agent audit dimensions (voice, pacing, agency, worldbuilding, no-ai-slop, continuity, rules) for Chapter Tier {tier}. Run `sr6_evaluate_draft` and provide the complete Markdown scorecard."
                    }
                }
            ]
        }
    elif prompt_name == "sr6_draft_scene":
        prompt_text = arguments.get("prompt", "Infiltrate the warehouse")
        char_id = arguments.get("char_id", "yuriko")
        tier = arguments.get("tier", "2")
        return {
            "description": f"Draft scene for {char_id} (Tier {tier})",
            "messages": [
                {
                    "role": "user",
                    "content": {
                        "type": "text",
                        "text": f"Draft a 4-beat narrative scene (Inciting Friction -> Escalation -> Climax -> Aftermath) for `{char_id}` adhering strictly to the active voice spec and anti-slop rules (Tier {tier} threshold).\n\nScene Prompt: {prompt_text}"
                    }
                }
            ]
        }
    elif prompt_name == "sr6_sync_portfolio":
        char_id = arguments.get("char_id", "")
        target_str = f" for '{char_id}'" if char_id else " across all portfolios"
        return {
            "description": f"Run full sync{target_str}",
            "messages": [
                {
                    "role": "user",
                    "content": {
                        "type": "text",
                        "text": f"Please run a deep character audit, regenerate modular sheets/exports, and sync CommLink6 player saves{target_str}."
                    }
                }
            ]
        }
    return None


def send_response(response: Dict[str, Any]):
    """Sends a JSON-RPC response message to stdout with newline framing."""
    body = json.dumps(response)
    sys.stdout.write(body + "\n")
    sys.stdout.flush()


def run_mcp_server():
    """Main JSON-RPC stdio loop for Antigravity MCP protocol."""
    # Ensure stdout is in UTF-8 mode
    if sys.stdout.encoding.lower() != "utf-8":
        import io
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

    while True:
        line = sys.stdin.readline()
        if not line:
            break

        line = line.strip()
        if not line:
            continue

        # Support Content-Length header if client uses HTTP/LSP framing
        if line.lower().startswith("content-length:"):
            try:
                length = int(line.split(":")[1].strip())
                while True:
                    header = sys.stdin.readline().strip()
                    if not header:
                        break
                payload = sys.stdin.read(length)
                req = json.loads(payload)
            except Exception:
                continue
        else:
            try:
                req = json.loads(line)
            except Exception:
                continue

        req_id = req.get("id")
        method = req.get("method", "")
        params = req.get("params", {})

        if method == "initialize":
            send_response({
                "jsonrpc": "2.0",
                "id": req_id,
                "result": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {
                        "tools": {},
                        "resources": {},
                        "prompts": {}
                    },
                    "serverInfo": {
                        "name": "sr6-tools",
                        "version": "1.0.0"
                    }
                }
            })

        elif method == "notifications/initialized" or method == "initialized":
            pass

        elif method == "tools/list":
            send_response({
                "jsonrpc": "2.0",
                "id": req_id,
                "result": {
                    "tools": TOOLS_DEFINITIONS
                }
            })

        elif method == "tools/call":
            tool_name = params.get("name", "")
            args = params.get("arguments", {})
            handler = TOOL_HANDLERS.get(tool_name)

            if handler:
                try:
                    result_text = handler(args)
                    send_response({
                        "jsonrpc": "2.0",
                        "id": req_id,
                        "result": {
                            "content": [
                                {
                                    "type": "text",
                                    "text": result_text
                                }
                            ]
                        }
                    })
                except Exception as e:
                    send_response({
                        "jsonrpc": "2.0",
                        "id": req_id,
                        "result": {
                            "isError": True,
                            "content": [
                                {
                                    "type": "text",
                                    "text": f"Error executing {tool_name}: {str(e)}\n{traceback.format_exc()}"
                                }
                            ]
                        }
                    })
            else:
                send_response({
                    "jsonrpc": "2.0",
                    "id": req_id,
                    "error": {
                        "code": -32601,
                        "message": f"Unknown tool: {tool_name}"
                    }
                })

        elif method == "resources/list":
            send_response({
                "jsonrpc": "2.0",
                "id": req_id,
                "result": {
                    "resources": RESOURCES_DEFINITIONS
                }
            })

        elif method == "resources/read":
            uri = params.get("uri", "")
            res = handle_read_resource(uri)
            if res:
                send_response({
                    "jsonrpc": "2.0",
                    "id": req_id,
                    "result": {
                        "contents": [res]
                    }
                })
            else:
                send_response({
                    "jsonrpc": "2.0",
                    "id": req_id,
                    "error": {
                        "code": -32002,
                        "message": f"Resource not found: {uri}"
                    }
                })

        elif method == "prompts/list":
            send_response({
                "jsonrpc": "2.0",
                "id": req_id,
                "result": {
                    "prompts": PROMPTS_DEFINITIONS
                }
            })

        elif method == "prompts/get":
            prompt_name = params.get("name", "")
            p_args = params.get("arguments", {})
            p_res = handle_get_prompt(prompt_name, p_args)
            if p_res:
                send_response({
                    "jsonrpc": "2.0",
                    "id": req_id,
                    "result": p_res
                })
            else:
                send_response({
                    "jsonrpc": "2.0",
                    "id": req_id,
                    "error": {
                        "code": -32602,
                        "message": f"Prompt not found: {prompt_name}"
                    }
                })

        elif method == "ping":
            send_response({
                "jsonrpc": "2.0",
                "id": req_id,
                "result": {}
            })

        elif req_id is not None:
            send_response({
                "jsonrpc": "2.0",
                "id": req_id,
                "error": {
                    "code": -32601,
                    "message": f"Method not found: {method}"
                }
            })


if __name__ == "__main__":
    run_mcp_server()
