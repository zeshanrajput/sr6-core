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
from sr6core.narration import generate_narration, retag_narratives, list_narratives
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

        for fmt, ext in [("roll20", ".json"), ("vtt", ".txt"), ("xml", ".xml"), ("cards", "_cards.md")]:
            try:
                content = cm.export_character(cid, fmt=fmt)
                target_file = os.path.join(out_dir, f"{cid}_sheet{ext}" if fmt != "cards" else f"{cid}_cards.md")
                with open(target_file, "w", encoding="utf-8") as f:
                    f.write(content)
            except Exception as e:
                print(f"         +-- Export {fmt.upper()} error: {e}")

        try:
            from sr6core.cards import export_character_card_deck
            _, html_deck = export_character_card_deck(cid)
            with open(os.path.join(out_dir, f"{cid}_cards.html"), "w", encoding="utf-8") as f:
                f.write(html_deck)
        except Exception as e:
            print(f"         +-- Export Cards HTML error: {e}")

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
    card_parser.add_argument("category", type=str, help="Item category (quality, spell, complex_form, weapon, cyberware, vehicle, program, gear)")
    card_parser.add_argument("item_id", type=str, help="Item reference ID or name")

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
    export_parser = subparsers.add_parser("export", help="Export character to Roll20 JSON, VTT Text, Genesis XML, or Cards Deck")
    export_parser.add_argument("char_id", type=str, help="Character ID (yuriko, velvet, union)")
    export_parser.add_argument("--format", type=str, choices=["roll20", "vtt", "xml", "cards"], default="roll20", help="Export format")

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
    narrate_parser.add_argument("--char", type=str, default=None, help="Character identifier (e.g. velvet, yuriko, union)")
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
    rag_query_parser.add_argument("--char", type=str, default=None, help="Active character dossier context ID (yuriko, velvet, union)")
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

    elif args.command == "card":
        from sr6core.cards import get_item_card
        card_info = get_item_card(args.category, args.item_id)
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
            out_file, err = generate_narration(args.target, pacing=args.pacing, voice=args.voice, char_id=args.char)
            if err:
                print(f"[Notice] {err}")
            else:
                print(f"[OK] Audio narration output target: {out_file}")

    elif args.command == "rag":
        from sr6core.rag import print_search_results_rich, render_rag_result_rich
        rag_engine = RAGEngine()

        if args.subcommand == "search" or (not args.subcommand and hasattr(args, "query")):
            q = getattr(args, "query", "")
            results = rag_engine.search(q, limit=10)
            print_search_results_rich(q, results)

        elif args.subcommand == "query" or hasattr(args, "prompt"):
            prompt = getattr(args, "prompt", "")
            use_ai = not getattr(args, "no_ai", False)
            provider_choice = getattr(args, "provider", "gemini")
            model_choice = getattr(args, "model", "gemini-flash-latest")
            llama_url = getattr(args, "url", None)
            char_choice = getattr(args, "char", None)
            effort_choice = getattr(args, "effort", None)

            res = rag_engine.query(
                prompt,
                use_ai=use_ai,
                provider_name=provider_choice,
                model_name=model_choice,
                llama_url=llama_url,
                char_id=char_choice,
                effort_level=effort_choice
            )
            render_rag_result_rich(res, show_context=True)


if __name__ == "__main__":
    main()
