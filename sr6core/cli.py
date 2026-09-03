"""
Command-Line Interface for SR6 Core Master Project.
Supports non-interactive script subcommands, ecosystem sync-all, and interactive console menu interface.
"""

import os
import sys
import argparse
from sr6core.rules_db import RulesDB
from sr6core.character_manager import CharacterManager
from sr6core.rag import RAGEngine
from sr6core.menu import run_interactive_menu
from sr6core.linter import analyze_prose, print_prose_report
from sr6core.continuity_engine import build_continuity_report, print_continuity_report
from sr6core.narration import generate_narration, batch_generate_narrations, retag_narratives, list_narratives
from sr6core.dataset_compiler import compile_commlink_datasets, get_dataset_info, find_latest_commlink_jar
from sr6core.creation.deep_audit import deep_audit_character
from sr6core.advancement import search_catalog, purchase_item_for_character
from sr6core.quarto_enricher import generate_character_dossier_appendix, expand_quarto_shortcodes
from sr6core.commlink_sync import push_to_commlink, push_all_to_commlink, scan_commlink_player_saves


def run_sync_all():
    print("\n============================================================")
    print("      RUNNING FULL SR6 ECOSYSTEM SYNC (sync-all)")
    print("============================================================\n")

    cm = CharacterManager()
    chars = cm.list_characters()

    for c in chars:
        cid = c["id"]
        cname = c["name"]
        cfile_path = c.get("path")
        if not c.get("exists") or not cfile_path or not os.path.exists(cfile_path):
            continue

        repo_dir = os.path.dirname(cfile_path) if os.path.isfile(cfile_path) else cfile_path
        print(f"--- Processing Portfolio: {cname} ({cid}) ---")


        # 1. Deep Audit
        audit = deep_audit_character(cid)
        warnings_list = audit.get("warnings", [])
        a_status = "PASS" if audit.get("valid", False) else f"WARNINGS ({len(warnings_list)})"
        print(f"  [1/5] Deep Item-by-Item Audit : {a_status}")
        for w in warnings_list:
            print(f"         +-- {w}")

        # 2. Multi-Format Exports into standardized output/ subfolders
        cm.clean_output_directory(repo_dir)
        text_dir = os.path.join(repo_dir, "output", "text")
        vtt_dir = os.path.join(repo_dir, "output", "vtt")
        for d in [text_dir, vtt_dir]:
            os.makedirs(d, exist_ok=True)

        # Modular Text Exports
        try:
            text_sheets = cm.export_character(cid, fmt="text_modular")
            for filename, sheet_content in text_sheets.items():
                with open(os.path.join(text_dir, filename), "w", encoding="utf-8") as f:
                    f.write(sheet_content)
        except Exception as e:
            print(f"         +-- Export Modular Text error: {e}")

        # VTT Exports (Genesis XML + Roll20 JSON)
        try:
            xml_content = cm.export_character(cid, fmt="xml")
            with open(os.path.join(vtt_dir, f"{cid}.xml"), "w", encoding="utf-8") as f:
                f.write(xml_content)
        except Exception as e:
            print(f"         +-- Export XML error: {e}")

        try:
            json_content = cm.export_character(cid, fmt="roll20")
            with open(os.path.join(vtt_dir, f"{cid}.json"), "w", encoding="utf-8") as f:
                f.write(json_content)
        except Exception as e:
            print(f"         +-- Export JSON error: {e}")

        # Mobile HTML App Export
        mobile_dir = os.path.join(repo_dir, "output", "mobile")
        os.makedirs(mobile_dir, exist_ok=True)
        try:
            mobile_html_content = cm.export_character(cid, fmt="mobile_html")
            with open(os.path.join(mobile_dir, "index.html"), "w", encoding="utf-8") as f:
                f.write(mobile_html_content)
            # Copy sw.js and manifest.json if present
            app_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "app")
            for asset in ["sw.js", "manifest.json"]:
                asset_src = os.path.join(app_dir, asset)
                if os.path.exists(asset_src):
                    import shutil
                    shutil.copy2(asset_src, os.path.join(mobile_dir, asset))
        except Exception as e:
            print(f"         +-- Export Mobile App error: {e}")

        print(f"  [2/5] Regenerated Exports     : Saved to {os.path.join(repo_dir, 'output')} (text, vtt, mobile)")

        # 3. CommLink6 GUI Save Sync
        ok, msg = push_to_commlink(cid)
        cl_status = "OK" if ok else "SKIPPED"
        print(f"  [3/5] CommLink6 GUI Save Sync : {cl_status} ({msg})")

        # 4. Generate Appendix Character Dossier (.qmd)
        chap_dir = os.path.join(repo_dir, "chapters")
        appendix_path = os.path.join(chap_dir, "appendix_dossier.qmd")
        try:
            generate_character_dossier_appendix(cid, appendix_path)
            print(f"  [4/5] Appendix Character Dossier: Generated at {appendix_path}")
        except Exception as e:
            print(f"  [4/5] Appendix Character Dossier: Error {e}")

        # 5. Expand Quarto Shortcodes in Chapter Files
        linter_count = 0
        if os.path.exists(chap_dir):
            for f in os.listdir(chap_dir):
                if f.endswith(".qmd") or f.endswith(".md"):
                    linter_count += 1
                    fpath = os.path.join(chap_dir, f)
                    try:
                        with open(fpath, "r", encoding="utf-8") as file:
                            txt = file.read()
                        expanded = expand_quarto_shortcodes(txt)
                        if expanded != txt:
                            with open(fpath, "w", encoding="utf-8") as file:
                                file.write(expanded)
                    except Exception:
                        pass
        print(f"  [5/5] Chapter Shortcodes & Files : Processed {linter_count} chapters in {chap_dir}\n")

    # Build Master Multi-Character PWA at app/index.html
    try:
        from sr6core.exporters.mobile_json import export_mobile_json
        from sr6core.exporters.mobile_html import get_mobile_html_template
        multi_bundle = {}
        for c in chars:
            cid = c["id"]
            if c.get("exists"):
                c_data = cm.get_character_data(cid)
                c_repo = cm.get_character_repo_dir(cid)
                if c_data:
                    multi_bundle[cid] = export_mobile_json(c_data, char_repo_path=c_repo)
        
        if multi_bundle:
            app_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "app")
            os.makedirs(app_dir, exist_ok=True)
            master_html = get_mobile_html_template(multi_bundle, initial_char_id="reiko")
            with open(os.path.join(app_dir, "index.html"), "w", encoding="utf-8") as f:
                f.write(master_html)
            print(f"  [+] Multi-Character Mobile PWA  : Built at {os.path.join(app_dir, 'index.html')} ({len(multi_bundle)} characters)\n")
    except Exception as e:
        print(f"  [!] Master Mobile App Build Error: {e}\n")

    print("============================================================")
    print("      SR6 ECOSYSTEM SYNC COMPLETED SUCCESSFULLY!")
    print("============================================================\n")


def main():
    if hasattr(sys.stdout, "reconfigure"):
        try:
            sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        except Exception:
            pass

    parser = argparse.ArgumentParser(description="SR6 Core Master Project & Portfolio Manager CLI")
    subparsers = parser.add_subparsers(dest="command", help="Sub-command to execute")

    # menu subcommand
    subparsers.add_parser("menu", help="Launch interactive CLI menu")

    # sync-all subcommand
    subparsers.add_parser("sync-all", help="Perform full ecosystem audit, export sync, and Quarto dossier generation")

    # search subcommand
    search_parser = subparsers.add_parser("search", help="Search the rules vault database")
    search_parser.add_argument("query", type=str, help="Search query string")

    # card subcommand
    card_parser = subparsers.add_parser("card", help="Display item reference card")
    card_parser.add_argument("target", type=str, nargs="+", help="Item category and name, or just item name (e.g. 'bioware Cerebellum Booster' or 'Cerebellum Booster')")

    # characters subcommand
    char_parser = subparsers.add_parser("characters", help="Manage character portfolios (reiko, velvet, venn)")
    char_sub = char_parser.add_subparsers(dest="subcommand", help="Action to perform")
    char_sub.add_parser("list", help="List all configured character portfolios")
    audit_parser = char_sub.add_parser("audit", help="Audit character creation compliance")
    audit_parser.add_argument("char_id", type=str, nargs="?", help="Character ID (reiko, velvet, venn)")
    adv_parser = char_sub.add_parser("advance", help="Purchase gear/qualities for character")
    adv_parser.add_argument("char_id", type=str, help="Character ID")
    adv_parser.add_argument("item_ref", type=str, help="CommLink6 item reference ID")

    # export subcommand
    export_parser = subparsers.add_parser("export", help="Export character to Modular Text, Roll20 JSON, or Genesis XML")
    export_parser.add_argument("char_id", type=str, help="Character ID (reiko, velvet, venn)")
    export_parser.add_argument("--format", type=str, choices=["text_modular", "roll20", "vtt", "xml"], default="text_modular", help="Export format")
    export_parser.add_argument("--output", type=str, default=None, help="Custom output filepath")

    # lint subcommand
    lint_parser = subparsers.add_parser("lint", help="Lint Quarto chapter prose for style and AI buzzwords")
    lint_parser.add_argument("target", type=str, help="Path to chapter markdown/qmd file")

    # continuity subcommand
    cont_parser = subparsers.add_parser("continuity", help="Run campaign timeline & story continuity audit")
    cont_parser.add_argument("repo_path", type=str, help="Repository directory path")


    # audit subcommand
    audit_parser = subparsers.add_parser("audit", help="Run AI sub-agent semantic narrative audit on a chapter")
    audit_parser.add_argument("target", type=str, help="Path to chapter markdown/qmd file")
    audit_parser.add_argument("--agent", type=str, default="no-ai-slop", choices=["no-ai-slop", "voice-internality", "pacing-structure", "panel"], help="Target sub-agent evaluator")
    audit_parser.add_argument("--model", type=str, default="gemini-flash-latest", help="LLM Model for evaluation")
    audit_parser.add_argument("--effort", type=str, choices=["high", "medium", "low"], default="medium", help="Thinking effort level")

    # narrate subcommand
    narrate_parser = subparsers.add_parser("narrate", help="Generate or manage TTS audio narration and character metadata tags")
    narrate_parser.add_argument("target", type=str, nargs="?", default=".", help="Path to chapter file, directory, or audio file (default: .)")
    narrate_parser.add_argument("--char", type=str, default=None, help="Character identifier (e.g. velvet, reiko, venn)")
    narrate_parser.add_argument("--retag", action="store_true", help="Update ID3 metadata tags on existing MP3 files without re-synthesizing audio")
    narrate_parser.add_argument("--list", action="store_true", help="List narrative audio files and their character metadata tags")
    narrate_parser.add_argument("--voice", type=str, default="af_heart", help="Kokoro voice model identifier (default: af_heart)")
    narrate_parser.add_argument("--pacing", type=str, choices=["tight", "balanced", "spacious"], default="balanced", help="Pause pacing profile")

    # db subcommand
    db_parser = subparsers.add_parser("db", help="Manage rules database & CommLink6 dataset imports")
    db_sub = db_parser.add_subparsers(dest="subcommand", help="Database action to perform")
    import_parser = db_sub.add_parser("import-commlink", help="Extract and index CommLink6 JAR XML datasets")
    import_parser.add_argument("--jar", type=str, help="Path to CommLink6 JAR file (optional)")
    db_sub.add_parser("compile-vault", help="Re-index Shadowrun Rules Vault markdown files into SQLite")
    db_sub.add_parser("sync-commlink", help="Push XML character sheets directly to CommLink6 GUI player saves")
    db_sub.add_parser("info", help="Display rules database status and CommLink6 dataset statistics")

    # rag subcommand
    rag_parser = subparsers.add_parser("rag", help="Query or search rules using the RAG subsystem")
    rag_sub = rag_parser.add_subparsers(dest="subcommand", help="RAG action to perform")
    rag_query_parser = rag_sub.add_parser("query", help="Query rules AI reference assistant")
    rag_query_parser.add_argument("prompt", type=str, help="Rules question / prompt")
    rag_query_parser.add_argument("--no-ai", action="store_true", help="Retrieve context only without AI response")
    rag_query_parser.add_argument("--provider", type=str, choices=["gemini", "llama"], default="gemini", help="LLM Provider (gemini or llama)")
    rag_query_parser.add_argument("--model", type=str, default="gemini-flash-latest", help="Model choice (gemini-flash-latest, gemma-2-9b-it)")
    rag_query_parser.add_argument("--url", type=str, default=None, help="Local llama.cpp URL")
    rag_query_parser.add_argument("--char", type=str, default=None, help="Active character dossier context ID (reiko, velvet, venn)")
    rag_query_parser.add_argument("--effort", type=str, choices=["high", "medium", "low"], default=None, help="Thinking effort level")
    rag_query_parser.add_argument("--compact", action="store_true", help="Output clean Markdown without ASCII box art")

    rag_search_parser = rag_sub.add_parser("search", help="Perform FTS rules search with authority ranking")
    rag_search_parser.add_argument("query", type=str, help="Search terms")
    rag_search_parser.add_argument("--compact", action="store_true", help="Output clean Markdown without ASCII box art")

    rag_get_parser = rag_sub.add_parser("get", help="Retrieve full rule markdown chunk by ID or topic directly from SQLite")
    rag_get_parser.add_argument("identifier", type=str, help="Rule ID (e.g. BS-005, HnS-0205) or Topic name")
    rag_get_parser.add_argument("--compact", action="store_true", help="Output clean Markdown without ASCII box art")

    # plugin subcommand
    plugin_parser = subparsers.add_parser("plugin", help="Manage SR6 Antigravity Agent Plugin")
    plugin_sub = plugin_parser.add_subparsers(dest="subcommand", help="Plugin action to perform")
    plugin_sub.add_parser("status", help="Show status of SR6 Antigravity Agent Plugin")
    p_install = plugin_sub.add_parser("install", help="Install SR6 plugin to ~/.gemini/config/plugins/")
    p_install.add_argument("--symlink", action="store_true", help="Create symlink/junction instead of directory copy")
    p_install.add_argument("--force", action="store_true", default=True, help="Overwrite existing installation")
    p_init = plugin_sub.add_parser("init-repo", help="Configure .agents/plugins.json inheritance in a character repo")
    p_init.add_argument("path", type=str, help="Path to character repository")

    # evaluate subcommand
    eval_parser = subparsers.add_parser("evaluate", help="Perform unified 7-axis narrative audit with tier-calibrated scoring")
    eval_parser.add_argument("target", type=str, help="Path to chapter .qmd file or prose text")
    eval_parser.add_argument("--tier", type=int, choices=[1, 2, 3], default=2, help="Chapter Tier (1=Keystone 9.0, 2=Narrative Evolution 8.5, 3=Atmospheric Bridge 8.0)")
    eval_parser.add_argument("--char", type=str, default=None, help="Character ID context (reiko, velvet, venn)")

    # ledger subcommand
    ledger_parser = subparsers.add_parser("ledger", help="Tabletop automation & combat ledger parsing")
    ledger_sub = ledger_parser.add_subparsers(dest="subcommand", help="Ledger action")
    l_parse = ledger_sub.add_parser("parse", help="Extract ammo, damage, and financial deltas from chapter prose")
    l_parse.add_argument("target", type=str, help="Path to chapter .qmd file or prose text")

    # vault subcommand
    vault_parser = subparsers.add_parser("vault", help="Manage Shadowrun Rules Vault, atomization, auditing, and Gemini vector search store")
    vault_sub = vault_parser.add_subparsers(dest="subcommand", help="Vault action to perform")
    v_import = vault_sub.add_parser("import-faq", help="Import & atomize official web FAQ into converted_md and vault (Auth Level 2)")
    v_import.add_argument("--url", type=str, default="https://shadowrunsixthworld.com/shadowrun-sixth-world-faq/", help="FAQ URL to fetch")
    v_import.add_argument("--html", type=str, default=None, help="Local HTML file path (optional)")

    v_atomize = vault_sub.add_parser("atomize", help="Atomize converted markdown rulebooks into individual rule chunks")
    v_atomize.add_argument("--single", type=str, default=None, help="Single file in converted_md to atomize")
    v_atomize.add_argument("--clear", action="store_true", help="Clear destination vault directory before atomizing")

    v_audit = vault_sub.add_parser("audit", help="Audit vault markdown chunks for integrity, dangling thoughts, and sizing anomalies")
    v_audit.add_argument("--report", type=str, default=None, help="Path to save markdown audit report")

    v_sync = vault_sub.add_parser("sync-gemini", help="Synchronize local rules vault with Google Gemini File Search Store")
    v_sync.add_argument("--skip-updates", action="store_true", help="Skip updating existing documents with different hashes")
    v_sync.add_argument("--workers", type=int, default=10, help="Concurrent upload worker threads (default: 10)")

    vault_sub.add_parser("status", help="Show summary of local rules vault, SQLite records, and Gemini File Search Store")

    v_pdf = vault_sub.add_parser("convert-pdf", help="Convert PDF rulebooks to clean markdown files in converted_md")
    v_pdf.add_argument("--single", type=str, default=None, help="Single PDF filename in input directory")
    v_pdf.add_argument("--regenerate", action="store_true", help="Force regenerate existing markdown files")
    v_pdf.add_argument("--engine", type=str, choices=["docling", "pymupdf", "auto"], default="auto", help="Conversion engine (docling with GPU/CUDA or pymupdf)")
    v_pdf.add_argument("--cuda", action="store_true", default=True, help="Enable CUDA acceleration for Docling (default: True)")
    v_pdf.add_argument("--cpu", dest="cuda", action="store_false", help="Disable CUDA and force CPU for Docling")
    v_pdf.add_argument("--curated-core", action="store_true", help="Curate core rulebooks: prioritize Hong Kong edition and skip redundant older core revisions")
    v_pdf.add_argument("--no-post-process", dest="post_process", action="store_false", default=True, help="Disable Shadowrun domain post-processing")
    v_pdf.add_argument("--input-dir", type=str, default=None, help="Input directory containing PDFs")
    v_pdf.add_argument("--output-dir", type=str, default=None, help="Output directory for markdown files")

    # roll subcommand
    roll_parser = subparsers.add_parser("roll", help="Roll an SR6 dice pool with exploding 6s (Rule of Six) or bought hits")
    roll_parser.add_argument("pool", type=str, help="Dice pool size or formula (e.g. '14', '12d6', '12+2')")
    roll_parser.add_argument("-x", "--exploding", action="store_true", help="Enable Rule of Six exploding dice")
    roll_parser.add_argument("-b", "--buy", action="store_true", help="Buy hits automatically (1 hit per 4 dice)")
    roll_parser.add_argument("--desc", type=str, default="Dice Test", help="Label or description for the test")

    # combat subcommand
    combat_parser = subparsers.add_parser("combat", help="Simulate SR6 combat exchanges and opposed tests")
    combat_sub = combat_parser.add_subparsers(dest="subcommand", help="Combat action to perform")
    c_att = combat_sub.add_parser("attack", help="Resolve an opposed ranged or melee attack test")
    c_att.add_argument("--char", type=str, default=None, help="Attacker character ID (reiko, velvet, venn)")
    c_att.add_argument("--weapon", type=str, default=None, help="Weapon name or ID")
    c_att.add_argument("--pool", type=int, default=12, help="Attacker attack pool if no character specified")
    c_att.add_argument("--base-dv", type=int, default=4, help="Base weapon damage value")
    c_att.add_argument("--ar", type=int, default=10, help="Attacker Attack Rating (AR)")
    c_att.add_argument("--defender", type=str, default="Target", help="Defender name")
    c_att.add_argument("--def-pool", type=int, default=8, help="Defender defense pool")
    c_att.add_argument("--def-dr", type=int, default=8, help="Defender Defense Rating (DR)")
    c_att.add_argument("--def-soak", type=int, default=8, help="Defender soak pool")
    # serve subcommand
    serve_parser = subparsers.add_parser("serve", help="Launch local live-sync server & web tactical PWA")
    serve_parser.add_argument("--port", type=int, default=8080, help="HTTP port (default: 8080)")
    serve_parser.add_argument("--host", type=str, default="0.0.0.0", help="HTTP host (default: 0.0.0.0)")

    # build subcommand (single-source build)
    build_parser = subparsers.add_parser("build", help="Rebuild master YAMLs from Markdown Trio, sync purchases, and build single-file offline PWA app/index.html")
    build_parser.add_argument("--rebuild-yaml", action="store_true", help="Recompile master YAML files completely from Markdown Trio (single source of truth)")
    build_parser.add_argument("--skip-npm", action="store_true", help="Skip npm build step")

    args = parser.parse_args()
    cm = CharacterManager()

    if args.command == "menu" or len(sys.argv) == 1:
        run_interactive_menu()

    elif args.command == "build":
        from sr6core.ledger.purchases_sync import PurchasesSyncEngine
        from sr6core.exporters.mobile_json import export_mobile_json
        import json
        import subprocess
        from rich.console import Console
        console = Console()

        console.print("\n[bold cyan]============================================================[/bold cyan]")
        console.print("[bold cyan]       SR6 CORE UNIFIED BUILD PIPELINE (Single-Source)      [/bold cyan]")
        console.print("[bold cyan]============================================================[/bold cyan]\n")

        # 1. Rebuild Master YAMLs from Markdown Trio if requested
        if getattr(args, "rebuild_yaml", False):
            from sr6core.compiler import rebuild_character_yaml
            console.print("[bold green][1/4] Recompiling master YAML dossiers from Markdown Trio...[/bold green]")
            for c in cm.list_characters():
                cid = c["id"]
                if c.get("exists"):
                    try:
                        ypath = rebuild_character_yaml(cid)
                        console.print(f"  • [{cid}] Rebuilt: {ypath}")
                    except Exception as ex:
                        console.print(f"  • [{cid}] Rebuild error: {ex}")

        # 2. Sync Purchases
        console.print("[bold green][2/4] Syncing purchases from character_purchases.qmd -> *_master.yaml...[/bold green]")
        sync_results = PurchasesSyncEngine.sync_all()
        for r in sync_results:
            if r.get("status") == "success":
                c_cnt = r.get("changes_count", 0)
                msg = f"  • [{r['char_id']}] Synced successfully ({c_cnt} changes applied)"
                console.print(f"[green]{msg}[/green]")
                for ch in r.get("changes", []):
                    console.print(f"     +-- {ch}")
            else:
                console.print(f"  • [{r.get('char_id', 'Unknown')}] {r.get('message', 'Skipped')}")

        # 3. Ingest characters & bake defaultBundle.ts
        console.print("\n[bold green][3/4] Exporting mobile JSON bundles & regenerating defaultBundle.ts...[/bold green]")
        bundle = {}
        for c in cm.list_characters():
            cid = c["id"]
            if c.get("exists"):
                c_data = cm.get_character_data(cid)
                repo_dir = cm.get_character_repo_dir(cid)
                if c_data:
                    bundle[cid] = export_mobile_json(c_data, char_repo_path=repo_dir)

        bundle_dir = os.path.join(os.path.dirname(__file__), "..", "web", "src", "data")
        os.makedirs(bundle_dir, exist_ok=True)
        bundle_path = os.path.join(bundle_dir, "defaultBundle.ts")
        with open(bundle_path, "w", encoding="utf-8") as f:
            f.write("export const defaultBundle: any = " + json.dumps(bundle, indent=2, ensure_ascii=False) + ";\n")
        console.print(f"[green]  • Inlined {len(bundle)} character portfolios into {bundle_path}[/green]")

        # Also emit standalone mobile app HTML directly into app/index.html
        from sr6core.exporters.mobile_html import get_mobile_html_template
        app_html_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "app", "index.html"))
        os.makedirs(os.path.dirname(app_html_path), exist_ok=True)
        with open(app_html_path, "w", encoding="utf-8") as f:
            f.write(get_mobile_html_template(bundle, initial_char_id="velvet"))
        console.print(f"[green]  • Standalone mobile PWA refreshed: {app_html_path}[/green]")

        # 3. Build single-file Vite PWA (if npm is available and not skipped)
        if not getattr(args, "skip_npm", False):
            console.print("\n[bold green][3/3] Compiling single-file offline PWA (app/index.html)...[/bold green]")
            web_dir = os.path.join(os.path.dirname(__file__), "..", "web")
            try:
                res = subprocess.run(["npm", "run", "build"], cwd=web_dir, capture_output=True, text=True, check=True, shell=True)
                out_html = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "app", "index.html"))
                console.print(f"[bold green][OK] Single-file mobile PWA successfully built: {out_html}[/bold green]\n")
            except subprocess.CalledProcessError as e:
                console.print(f"[bold red][Error] npm run build failed: {e.stderr}[/bold red]\n")

    elif args.command == "sync-all":
        run_sync_all()

    elif args.command == "search":
        db = RulesDB()
        enriched = db.get_enriched_item(args.query)
        if enriched:
            print(f"\n=== ENRICHED RULE & DATASET CARD: '{enriched['name']}' ===")
            print(f" ID        : {enriched['id']}")
            print(f" Type      : {enriched['item_type'].upper()}")
            if enriched.get("commlink_data"):
                cdata = enriched["commlink_data"]
                stats = [f"{k}={v}" for k, v in cdata.items() if k not in ["raw_xml"] and v is not None]
                print(f" CommLink6 : {', '.join(stats)}")
            if enriched.get("rules_vault"):
                v = enriched["rules_vault"]
                print(f" Rulebook  : {v.get('source', 'SR6')} (Page: {v.get('page', 'N/A')}) [Auth Level {v.get('authority_level', 3)}]")
            print()
        else:
            results = db.search_rules(args.query)
            print(f"Rules search results for '{args.query}':")
            for r in results:
                print(f"- [{r.get('id')}] {r.get('topic')} ({r.get('source')} p.{r.get('page')})")

    elif args.command == "card":
        from sr6core.cards import get_item_card
        known_cats = {"quality", "qualities", "spell", "spells", "complex_form", "complexform", "weapon", "weapons", "cyberware", "bioware", "vehicle", "drone", "gear", "program", "contact", "contacts", "echo", "meta_echo"}
        if len(args.target) == 1:
            cat, item_name = "auto", args.target[0]
        else:
            first = args.target[0].lower().strip()
            if first in known_cats:
                cat = first
                item_name = " ".join(args.target[1:])
            else:
                cat = "auto"
                item_name = " ".join(args.target)
        card_info = get_item_card(cat, item_name)
        print(f"\n{card_info['markdown']}\n")

    elif args.command == "characters":
        if args.subcommand == "list" or not args.subcommand:
            print("\n=== Configured SR6 Character Portfolios ===")
            for char in cm.list_characters():
                status_str = "EXISTS" if char["exists"] else "MISSING"
                print(f"- [{char['id']}] {char['name']} | Metatype: {char['metatype']} | Role: {char['role']} | Status: {status_str}")
            print()

        elif args.subcommand == "audit":
            char_ids = [args.char_id] if args.char_id else [c["id"] for c in cm.list_characters()]
            for cid in char_ids:
                report = deep_audit_character(cid)
                print(f"\n--- Deep Audit Report for '{cid}' ---")
                print(f"  Overall Valid      : {'PASS' if report['valid'] else 'WARNINGS'}")
                print(f"  Positive Karma     : {report['total_pos_karma']}")
                print(f"  Negative Karma     : {report['total_neg_karma']}")
                if report.get("warnings"):
                    print("  Warnings:")
                    for w in report["warnings"]:
                        print(f"   - {w}")
            print()

        elif args.subcommand == "advance":
            ok, msg = purchase_item_for_character(args.char_id, args.item_ref)
            print(f"\n{msg}\n")

    elif args.command == "export":
        try:
            output = cm.export_character(
                args.char_id,
                fmt=args.format,
                output_path=getattr(args, "output", None)
            )
            print(f"\n--- Export for '{args.char_id}' ({args.format.upper()}) ---")
            if isinstance(output, dict):
                for fname, content in output.items():
                    print(f"\n>>> {fname}:\n{content[:300]}...\n")
            else:
                print(output)
        except Exception as e:
            print(f"Export failed: {e}")

    elif args.command == "db":
        if args.subcommand == "import-commlink":
            jar_path = getattr(args, "jar", None) or find_latest_commlink_jar()
            print(f"Importing CommLink6 datasets from '{jar_path}'...")
            ok, msg = compile_commlink_datasets(jar_path=jar_path)
            print(msg)
        elif args.subcommand == "compile-vault":
            print(f"Re-indexing rules vault from 'C:\\Users\\zesha\\OneDrive\\Desktop\\SR6\\ebooks\\shadowrun_rules_vault'...")
            db = RulesDB()
            count, msg = db.compile_vault(force=True)
            print(f"\n{msg}\n")
        elif args.subcommand == "sync-commlink":
            print("Syncing character sheets directly to CommLink6 GUI player saves...")
            res = push_all_to_commlink()
            for cid, ok, msg in res:
                print(f" - [{cid}]: {msg}")
            print()
        elif args.subcommand == "info" or not args.subcommand:
            info = get_dataset_info()
            print("\n=== Rules Database Status & CommLink6 Datasets ===")
            print(f" Database Exists : {info.get('exists')}")
            print(f" CommLink6 JAR   : {info.get('commlink_jar', 'Not imported yet')}")
            print(f" Import Date     : {info.get('import_date', 'N/A')}")
            if "counts" in info:
                print("\n Dataset Record Counts:")
                for tbl, cnt in info["counts"].items():
                    print(f"  - {tbl:<20}: {cnt:,}")
            print()

    elif args.command == "lint":
        report, err = analyze_prose(args.target)
        if err:
            print(f"[Error] {err}")
        else:
            print_prose_report(report)

    elif args.command == "continuity":
        report, err = build_continuity_report(args.repo_path)
        if err:
            print(f"[Error] {err}")
        else:
            print_continuity_report(report)


    elif args.command == "audit":
        from sr6core.audit import run_semantic_audit, print_audit_report
        res = run_semantic_audit(args.target, agent=args.agent, model=args.model, effort=args.effort)
        print_audit_report(res)

    elif args.command == "narrate":
        if args.list or args.target == "list":
            target = "." if args.target == "list" else args.target
            items = list_narratives(target, char_id=args.char)
            if not items:
                print(f"[Notice] No narrative MP3 files found in '{target}'" + (f" for character '{args.char}'" if args.char else ""))
            else:
                from rich.console import Console
                from rich.table import Table
                console = Console()
                char_heading = f" (Character: {args.char.upper()})" if args.char else ""
                table = Table(title=f"🎙️ Shadowrun 6e Audio Narratives ({len(items)} tracks){char_heading}")
                table.add_column("Trk", justify="right", style="cyan")
                table.add_column("Character", style="magenta")
                table.add_column("Title", style="bold white")
                table.add_column("Artist / Lead", style="green")
                table.add_column("Album / Source", style="dim")
                table.add_column("File", style="blue")

                for it in items:
                    table.add_row(
                        it.get("track") or "-",
                        it.get("character_id") or it.get("handle") or "-",
                        it.get("title") or it.get("filename") or "-",
                        it.get("artist") or "-",
                        it.get("album") or "-",
                        it.get("filename") or "-"
                    )
                console.print(table)

        elif args.retag:
            tagged = retag_narratives(args.target, char_id=args.char)
            if not tagged:
                print(f"[Notice] No audio files found to retag in '{args.target}'.")
            else:
                print(f"[OK] Successfully updated ID3 metadata tags on {len(tagged)} audio files:")
                for t in tagged:
                    print(f"  • [{t.get('character_id', 'Unknown')}] Track {t.get('track_num', '-')}: {t.get('title', 'Chapter')} -> {t.get('artist', '')} ({t.get('album', '')})")

        else:
            abs_t = os.path.abspath(args.target)
            if os.path.isdir(abs_t):
                results = batch_generate_narrations(args.target, pacing=args.pacing, voice=args.voice, char_id=args.char)
                success_cnt = sum(1 for p, err in results if not err)
                print(f"\n[OK] Batch narration complete: {success_cnt}/{len(results)} chapters generated successfully.")
            else:
                out_file, err = generate_narration(args.target, pacing=args.pacing, voice=args.voice, char_id=args.char)
                if err:
                    print(f"[Notice] {err}")
                else:
                    print(f"[OK] Audio narration output target: {out_file}")

    elif args.command == "rag":
        from sr6core.rag import print_search_results_rich, render_rag_result_rich
        from sr6core.rag.ui import render_rule_chunk_markdown
        rag_engine = RAGEngine()

        if args.subcommand == "get":
            ident = getattr(args, "identifier", "")
            rule = rag_engine.get_rule(ident)
            render_rule_chunk_markdown(rule, compact=getattr(args, "compact", False))

        elif args.subcommand == "search" or (not args.subcommand and hasattr(args, "query")):
            q = getattr(args, "query", "")
            compact = getattr(args, "compact", False)
            results = rag_engine.search(q, limit=10)
            print_search_results_rich(q, results, compact=compact)

        elif args.subcommand == "query" or hasattr(args, "prompt"):
            prompt = getattr(args, "prompt", "")
            use_ai = not getattr(args, "no_ai", False)
            provider_choice = getattr(args, "provider", "gemini")
            model_choice = getattr(args, "model", "gemini-flash-latest")
            llama_url = getattr(args, "url", None)
            char_choice = getattr(args, "char", None)
            effort_choice = getattr(args, "effort", None)
            compact = getattr(args, "compact", False)

            res = rag_engine.query(
                prompt,
                use_ai=use_ai,
                provider_name=provider_choice,
                model_name=model_choice,
                llama_url=llama_url,
                char_id=char_choice,
                effort_level=effort_choice
            )
            render_rag_result_rich(res, show_context=True, compact=compact)

    elif args.command == "plugin":
        from sr6core.plugin import print_plugin_status_rich, install_global_plugin, configure_repo_plugin_inheritance
        if args.subcommand == "install":
            ok, msg = install_global_plugin(symlink=args.symlink, force=args.force)
            if ok:
                print(f"[OK] {msg}")
            else:
                print(f"[Error] {msg}")
        elif args.subcommand == "init-repo":
            ok, msg = configure_repo_plugin_inheritance(args.path)
            if ok:
                print(f"[OK] {msg}")
            else:
                print(f"[Error] {msg}")
        else:
            print_plugin_status_rich()

    elif args.command == "evaluate":
        from sr6core.evaluator import evaluate_chapter_draft, print_scorecard_rich
        report = evaluate_chapter_draft(args.target, tier=args.tier, char_id=args.char)
        print_scorecard_rich(report)

    elif args.command == "ledger":
        from sr6core.ledger_parser import parse_combat_ledger_prose, format_ledger_patch_markdown
        if args.subcommand == "parse" or not args.subcommand:
            report = parse_combat_ledger_prose(args.target)
            print(f"\n{format_ledger_patch_markdown(report)}\n")

    elif args.command == "vault":
        from sr6core.vault import (
            atomize_vault,
            audit_vault,
            sync_gemini_store,
            list_stores_summary,
            import_web_faq,
        )
        from sr6core.vault.pdf_converter import batch_convert_pdfs, convert_pdf_to_md
        from sr6core.rules_db import DEFAULT_VAULT_DIR, DEFAULT_CONVERTED_DIR, DEFAULT_DB_PATH, DEFAULT_PDF_DIR

        if args.subcommand == "import-faq":
            print(f"Importing FAQ from '{args.url}' (or local source: {args.html})...")
            try:
                cnt, full_md, vault_d = import_web_faq(url=args.url, html_source=args.html)
                print(f"[OK] Ingested & atomized {cnt} FAQ rules into '{vault_d}'")
                print(f"     Full document saved: '{full_md}'")
            except Exception as e:
                print(f"[Error] FAQ import failed: {e}")

        elif args.subcommand == "atomize":
            print(f"Atomizing rulebooks from '{DEFAULT_CONVERTED_DIR}' to '{DEFAULT_VAULT_DIR}'...")
            n_files, n_chunks = atomize_vault(single_file=args.single, clear_output=args.clear)
            print(f"[OK] Processed {n_files} files, generated {n_chunks} atomic rules.")

        elif args.subcommand == "audit":
            print(f"Auditing vault at '{DEFAULT_VAULT_DIR}'...")
            res = audit_vault(report_path=args.report)
            print(f"\n=== Vault Audit Results ===")
            print(f"  Valid Status        : {'PASS' if res['valid'] else 'FAIL'}")
            print(f"  Total Chunks        : {res['total_files']}")
            print(f"  Dangling Thoughts   : {res['dangling_thoughts_count']}")
            print(f"  Dangling Hyphens    : {res['dangling_hyphens_count']}")
            print(f"  Header-Only Chunks  : {res['header_only_count']}")
            print(f"  Isolated Entities   : {res['isolated_entities_count']}")
            print(f"  Micro Chunks (<100) : {res['micro_chunks_count']}")
            print(f"  Monolith Chunks     : {res['monolith_chunks_count']}")
            if args.report:
                print(f"  Report Written To   : {args.report}")
            print()

        elif args.subcommand == "sync-gemini":
            print(f"Synchronizing vault at '{DEFAULT_VAULT_DIR}' to Gemini File Search Store...")
            res = sync_gemini_store(skip_updates=args.skip_updates, max_workers=args.workers)
            if res.get("success"):
                print(f"\n[OK] Synchronization Complete!")
                print(f"  Store Name  : {res['store_name']}")
                print(f"  Uploaded    : {res['uploaded']}")
                print(f"  Updated     : {res['updated']}")
                print(f"  Deleted     : {res['deleted']}")
                print(f"  Local Vault : {res['total_local']} files")
            else:
                print(f"[Error] Synchronization failed: {res.get('error')}")

        elif args.subcommand == "convert-pdf":
            in_dir = args.input_dir or DEFAULT_PDF_DIR
            out_dir = args.output_dir or DEFAULT_CONVERTED_DIR
            if args.single:
                pdf_p = os.path.join(in_dir, args.single)
                md_p = os.path.join(out_dir, os.path.splitext(args.single)[0] + ".md")
                ok, err = convert_pdf_to_md(
                    pdf_p,
                    md_p,
                    engine=args.engine,
                    use_cuda=args.cuda,
                    post_process=args.post_process
                )
                if ok:
                    print(f"[OK] Converted {args.single} -> {md_p} (engine: {args.engine}, cuda: {args.cuda})")
                else:
                    print(f"[Error] {err}")
            else:
                print(f"Converting PDFs from '{in_dir}' to '{out_dir}' (engine: {args.engine}, cuda: {args.cuda})...")
                succ, tot, errs = batch_convert_pdfs(
                    in_dir,
                    out_dir,
                    regenerate=args.regenerate,
                    engine=args.engine,
                    use_cuda=args.cuda,
                    curated_core_only=args.curated_core
                )
                print(f"[OK] Converted {succ}/{tot} PDF files.")
                for err in errs:
                    print(f"  - {err}")

        elif args.subcommand == "status" or not args.subcommand:
            import glob
            local_vault_count = len(glob.glob(os.path.join(DEFAULT_VAULT_DIR, "*.md"))) if os.path.exists(DEFAULT_VAULT_DIR) else 0
            local_conv_count = len(glob.glob(os.path.join(DEFAULT_CONVERTED_DIR, "*.md"))) if os.path.exists(DEFAULT_CONVERTED_DIR) else 0

            print("\n=== Shadowrun Rules Vault & Gemini Vector Store Status ===")
            print(f" Local Vault Path     : {DEFAULT_VAULT_DIR} ({local_vault_count:,} chunks)")
            print(f" Converted MD Path    : {DEFAULT_CONVERTED_DIR} ({local_conv_count:,} sourcebooks)")
            print(f" SQLite Index DB Path : {DEFAULT_DB_PATH} ({'EXISTS' if os.path.exists(DEFAULT_DB_PATH) else 'MISSING'})")

            try:
                stores = list_stores_summary()
                print("\n Active Gemini File Search Stores:")
                for s in stores:
                    print(f"  - {s['display_name']} ({s['name']}): {s['active_documents_count']} active, {s['pending_documents_count']} pending, {s['failed_documents_count']} failed")
            except Exception as e:
                print(f"\n Gemini API Store Status: [Unavailable / {e}]")
            print()

    elif args.command == "roll":
        from sr6core.simulation.dice import roll_pool
        from rich.console import Console
        console = Console()

        # Parse pool expression (e.g. "14", "12d6", "10+2-1")
        pool_str = args.pool.lower().replace("d6", "").replace("d", "").strip()
        try:
            pool_val = int(eval(pool_str, {"__builtins__": None}, {}))
        except Exception:
            pool_val = 12

        res = roll_pool(
            pool=max(1, pool_val),
            description=args.desc,
            is_exploding=args.exploding,
            buy_hits=args.buy,
        )
        console.print(res.format_terminal())

    elif args.command == "combat":
        from sr6core.simulation.combat import CombatResolver
        from rich.console import Console
        console = Console()

        if args.subcommand == "attack" or not args.subcommand:
            attacker_name = "Attacker"
            weapon_name = args.weapon or "Colt Manhunter"
            attack_pool = args.pool
            base_dv = args.base_dv
            attack_ar = args.ar

            if args.char:
                cm = CharacterManager()
                c_data = cm.get_character_data(args.char)
                if c_data:
                    attacker_name = c_data.get("identity", {}).get("handle", args.char.title())

            res = CombatResolver.resolve_attack(
                attacker_pool=attack_pool,
                defender_pool=args.def_pool,
                base_dv=base_dv,
                soak_pool=args.def_soak,
                attacker_name=attacker_name,
                defender_name=args.defender,
                weapon_name=weapon_name,
                attacker_ar=attack_ar,
                defender_dr=args.def_dr,
                is_exploding=args.exploding,
            )
            console.print(res.format_terminal())

    elif args.command == "serve":
        from sr6core.server import run_server
        run_server(port=args.port, host=args.host)



if __name__ == "__main__":
    main()
