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
from sr6core.narration import generate_narration
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
        cfile_path = c["path"]
        repo_dir = os.path.dirname(cfile_path) if os.path.isfile(cfile_path) else cfile_path
        print(f"--- Processing Portfolio: {cname} ({cid}) ---")

        # 1. Deep Audit
        audit = deep_audit_character(cid)
        a_status = "PASS" if audit["valid"] else f"WARNINGS ({len(audit['warnings'])})"
        print(f"  [1/5] Deep Item-by-Item Audit : {a_status}")
        for w in audit.get("warnings", []):
            print(f"         +-- {w}")

        # 2. Multi-Format Exports into output/ folder
        out_dir = os.path.join(repo_dir, "output")
        os.makedirs(out_dir, exist_ok=True)

        for fmt, ext in [("roll20", ".json"), ("vtt", ".txt"), ("xml", ".xml")]:
            try:
                content = cm.export_character(cid, fmt=fmt)
                target_file = os.path.join(out_dir, f"{cid}_sheet{ext}")
                with open(target_file, "w", encoding="utf-8") as f:
                    f.write(content)
            except Exception as e:
                print(f"         +-- Export {fmt.upper()} error: {e}")
        print(f"  [2/5] Regenerated Exports     : Saved to {out_dir}")

        # 3. CommLink6 GUI Save Sync
        ok, msg = push_to_commlink(cid)
        cl_status = "OK" if ok else "SKIPPED"
        print(f"  [3/5] CommLink6 GUI Save Sync : {cl_status} ({msg})")

        # 4. Expand Quarto Shortcodes in Chapter Files
        chap_dir = os.path.join(repo_dir, "chapters")
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

    print("============================================================")
    print("      SR6 ECOSYSTEM SYNC COMPLETED SUCCESSFULLY!")
    print("============================================================\n")


def main():
    parser = argparse.ArgumentParser(description="SR6 Core Master Project & Portfolio Manager CLI")
    subparsers = parser.add_subparsers(dest="command", help="Sub-command to execute")

    # menu subcommand
    subparsers.add_parser("menu", help="Launch interactive CLI menu")

    # sync-all subcommand
    subparsers.add_parser("sync-all", help="Perform full ecosystem audit, export sync, and Quarto dossier generation")

    # search subcommand
    search_parser = subparsers.add_parser("search", help="Search the rules vault database")
    search_parser.add_argument("query", type=str, help="Search query string")

    # characters subcommand
    char_parser = subparsers.add_parser("characters", help="Manage character portfolios (yuriko, velvet, union)")
    char_sub = char_parser.add_subparsers(dest="subcommand", help="Action to perform")
    char_sub.add_parser("list", help="List all configured character portfolios")
    audit_parser = char_sub.add_parser("audit", help="Audit character creation compliance")
    audit_parser.add_argument("char_id", type=str, nargs="?", help="Character ID (yuriko, velvet, union)")
    adv_parser = char_sub.add_parser("advance", help="Purchase gear/qualities for character")
    adv_parser.add_argument("char_id", type=str, help="Character ID")
    adv_parser.add_argument("item_ref", type=str, help="CommLink6 item reference ID")

    # export subcommand
    export_parser = subparsers.add_parser("export", help="Export character to Roll20 JSON, VTT Text, or Genesis XML")
    export_parser.add_argument("char_id", type=str, help="Character ID (yuriko, velvet, union)")
    export_parser.add_argument("--format", type=str, choices=["roll20", "vtt", "xml"], default="roll20", help="Export format")

    # lint subcommand
    lint_parser = subparsers.add_parser("lint", help="Lint Quarto chapter prose for style and AI buzzwords")
    lint_parser.add_argument("target", type=str, help="Path to chapter markdown/qmd file")

    # continuity subcommand
    cont_parser = subparsers.add_parser("continuity", help="Run campaign timeline & story continuity audit")
    cont_parser.add_argument("repo_path", type=str, help="Repository directory path")

    # narrate subcommand
    narrate_parser = subparsers.add_parser("narrate", help="Generate TTS audio narration for campaign chapter")
    narrate_parser.add_argument("target", type=str, help="Path to chapter markdown/qmd file")

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
    rag_query_parser.add_argument("--model", type=str, default="flash-latest", help="Model choice (flash-latest, flash-light-latest, gemini-2.5-flash)")
    rag_query_parser.add_argument("--effort", type=str, choices=["high", "medium", "low"], default=None, help="Thinking effort level")
    rag_search_parser = rag_sub.add_parser("search", help="Perform FTS rules search with authority ranking")
    rag_search_parser.add_argument("query", type=str, help="Search terms")

    args = parser.parse_args()
    cm = CharacterManager()

    if args.command == "menu" or len(sys.argv) == 1:
        run_interactive_menu()

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
            output = cm.export_character(args.char_id, fmt=args.format)
            print(f"\n--- Export for '{args.char_id}' ({args.format.upper()}) ---")
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

    elif args.command == "narrate":
        out_file, err = generate_narration(args.target)
        if err:
            print(f"[Notice] {err}")
        else:
            print(f"[OK] Audio narration output target: {out_file}")

    elif args.command == "rag":
        rag_engine = RAGEngine()

        if args.subcommand == "search" or (not args.subcommand and hasattr(args, "query")):
            q = getattr(args, "query", "")
            results = rag_engine.search(q, limit=10)
            print(f"\n=== RAG Rules Vault Search Results for '{q}' ===")
            for r in results:
                ds_label = f" [CommLink6: {r['commlink_data']['name']}]" if r.get("commlink_data") else ""
                print(f"- [{r['id']}] {r.get('topic', 'N/A')} ({r.get('source', 'SR6')} p.{r.get('page', '')}) [Auth Level {r.get('authority_level', 3)}]{ds_label}")
            print()

        elif args.subcommand == "query" or hasattr(args, "prompt"):
            prompt = getattr(args, "prompt", "")
            use_ai = not getattr(args, "no_ai", False)
            model_choice = getattr(args, "model", "flash-latest")
            effort_choice = getattr(args, "effort", None)
            print(f"\nProcessing RAG query: '{prompt}' (Model: {model_choice}, Effort: {effort_choice or 'default'})...")
            res = rag_engine.query(prompt, use_ai=use_ai, model_name=model_choice, effort_level=effort_choice)
            
            if res.get("ai_response"):
                print("\n=== RAG AI Assistant Answer ===")
                print(res["ai_response"])
            elif res.get("error"):
                print(f"\n[AI Notice] {res['error']}")
                print("\n=== Retrieved Context ===")
                print(res["context"])
            else:
                print("\n=== Retrieved Context ===")
                print(res["context"])
            print()



if __name__ == "__main__":
    main()
