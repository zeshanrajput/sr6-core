"""
Interactive Terminal Menu System for SR6 Core Master Project.
"""

import sys
import os
from typing import Dict, Any, Optional

from sr6core.character_manager import CharacterManager
from sr6core.rules_db import RulesDB
from sr6core.rag import RAGEngine
from sr6core.linter import analyze_prose, print_prose_report
from sr6core.continuity_engine import build_continuity_report, print_continuity_report
from sr6core.narration import generate_narration
from sr6core.dataset_compiler import compile_commlink_datasets, get_dataset_info, find_latest_commlink_jar
from sr6core.creation.deep_audit import deep_audit_character
from sr6core.advancement import search_catalog, purchase_item_for_character
from sr6core.quarto_enricher import generate_character_dossier_appendix


def print_banner():
    print("\n" + "=" * 60)
    print("      SR6 CORE - MASTER PORTFOLIO & RULES ENGINE CLI")
    print("=" * 60)


def manage_characters_menu(cm: CharacterManager):
    while True:
        chars = cm.list_characters()
        print("\n--- SELECT CHARACTER PORTFOLIO ---")
        for idx, char in enumerate(chars, 1):
            status = "EXISTS" if char["exists"] else "MISSING"
            print(f" [{idx}] {char['name']} ({char['id']}) | {char['metatype']} | {char['role']} [{status}]")
        print(" [B] Back to Main Menu")

        choice = input("\nEnter choice: ").strip()
        if choice.lower() == 'b':
            break

        try:
            char_idx = int(choice) - 1
            if 0 <= char_idx < len(chars):
                selected_char = chars[char_idx]
                character_actions_menu(cm, selected_char["id"])
            else:
                print("Invalid character selection.")
        except ValueError:
            print("Please enter a valid number or 'B'.")


def character_actions_menu(cm: CharacterManager, char_id: str):
    data = cm.get_character_data(char_id)
    if not data:
        print(f"\n[Error] Character file for '{char_id}' not found.")
        return

    identity = data.get("identity", {})
    attrs = data.get("attributes", {})

    while True:
        print(f"\n=== CHARACTER PORTFOLIO: {identity.get('handle', char_id.title())} ===")
        print(f"Real Name: {identity.get('real_name', 'N/A')} | Metatype: {identity.get('metatype', 'Human')}")
        print("------------------------------------------------------------")
        print(" [1] View Sheet Summary & Attributes")
        print(" [2] Deep Audit (Item-by-Item & Transaction Pricing)")
        print(" [3] Advance / Shop for Gear, Qualities & Spells")
        print(" [4] Export Roll20 JSON")
        print(" [5] Export Plain-Text VTT")
        print(" [6] Export Genesis / CommLink6 Compliant XML")
        print(" [B] Back to Character Selection")

        choice = input("\nAction choice: ").strip()
        if choice.lower() == 'b':
            break

        if choice == '1':
            print(f"\n--- {identity.get('handle', char_id)} Attributes ---")
            for k, v in attrs.items():
                print(f"  {k.upper():<12}: {v}")
            print(f"  Skills Count: {len(data.get('skills', []))}")
            print(f"  Qualities   : +{len(data.get('qualities', {}).get('positive', []))} / -{len(data.get('qualities', {}).get('negative', []))}")

        elif choice == '2':
            report = deep_audit_character(char_id)
            print(f"\n--- Deep Audit Report for '{char_id}' ---")
            print(f"  Overall Compliance : {'PASS' if report['valid'] else 'WARNINGS'}")
            print(f"  Positive Karma Total: {report['total_pos_karma']}")
            print(f"  Negative Karma Total: {report['total_neg_karma']}")
            if report.get("warnings"):
                print("  Warnings:")
                for w in report["warnings"]:
                    print(f"   - {w}")
            if report.get("gear_audits"):
                print("\n  Gear & Vehicle Transaction Pricing Audits:")
                for g in report["gear_audits"]:
                    print(f"   - {g['name']} ({g['ref']}): Base {g['base_cost']}¥ -> Actual {g['transaction_cost']}¥ [{g['pricing_note']}]")

        elif choice == '3':
            q = input("\nEnter item or quality search term (e.g. cyberjack, hooder, acclimation): ").strip()
            if q:
                results = search_catalog(q)
                if not results:
                    print("No matching items found.")
                else:
                    print(f"\n--- Catalog Search Results for '{q}' ---")
                    for idx, res in enumerate(results, 1):
                        print(f" [{idx}] {res['name']} ({res['id']}) | Type: {res['category'].upper()}")
                    sel = input("\nEnter number to purchase (or ENTER to cancel): ").strip()
                    if sel.isdigit() and 1 <= int(sel) <= len(results):
                        chosen = results[int(sel) - 1]
                        ok, msg = purchase_item_for_character(char_id, chosen["id"])
                        print(f"\n{msg}")

        elif choice == '4':
            out = cm.export_character(char_id, fmt="roll20")
            print(f"\n--- Roll20 JSON Export ({char_id}) ---")
            print(out)

        elif choice == '5':
            out = cm.export_character(char_id, fmt="vtt")
            print(f"\n--- Plain-Text VTT Export ({char_id}) ---")
            print(out)

        elif choice == '6':
            out = cm.export_character(char_id, fmt="xml")
            print(f"\n--- CommLink6 Compliant XML Export ({char_id}) ---")
            print(out)

        else:
            print("Invalid option.")


def rules_search_menu(db: RulesDB):
    query = input("\nEnter rules search query (e.g. matrix, fading, drones): ").strip()
    if not query:
        return
    results = db.search_rules(query, limit=10)
    print(f"\n--- Rules Search Results for '{query}' ---")
    if not results:
        print("No matching rules found in rules vault.")
        return
    for r in results:
        print(f"- [{r.get('id')}] {r.get('topic', 'N/A')} ({r.get('source', 'SR6')} p.{r.get('page', '')})")


def rules_rag_menu(rag_engine: RAGEngine):
    print("\n=== RULES RAG AI ASSISTANT INTERACTIVE SESSION ===")
    print("Available commands:")
    print("  /clear       : Clear current conversation thread history")
    print("  /model <m>   : Set model (e.g. flash-latest, flash-light-latest)")
    print("  /effort <e>  : Set effort level (high, medium, low)")
    print("  /help        : Show slash command help")
    print("  /exit or B   : Return to main menu")

    while True:
        status_line = f"[Model: {rag_engine.session.model_name} | Effort: {rag_engine.session.effort_level or 'default'}]"
        prompt = input(f"\n{status_line} RAG Prompt > ").strip()
        if not prompt:
            continue

        if prompt.lower() in ['b', '/exit', '/quit', '/back']:
            break

        if prompt.lower() == '/clear':
            rag_engine.session.clear_history()
            print("[+] Conversation thread history cleared.")
            continue

        if prompt.lower() in ['/help', '?']:
            print("\nSlash Commands:")
            print("  /clear                 : Reset active chat memory")
            print("  /model flash-latest    : Switch to Gemini Flash Latest")
            print("  /model flash-light-latest : Switch to Gemini Flash Lite Latest")
            print("  /effort high|medium|low: Adjust thinking budget")
            print("  /exit                  : Back to main menu")
            continue

        if prompt.lower().startswith('/model'):
            parts = prompt.split(maxsplit=1)
            if len(parts) > 1:
                new_model = parts[1].strip()
                rag_engine.session.set_model(new_model)
                print(f"[+] Model updated to '{rag_engine.session.model_name}'.")
            else:
                print(f"Current model: {rag_engine.session.model_name}")
            continue

        if prompt.lower().startswith('/effort'):
            parts = prompt.split(maxsplit=1)
            if len(parts) > 1:
                new_effort = parts[1].strip()
                rag_engine.session.set_effort(new_effort)
                print(f"[+] Effort level updated to '{rag_engine.session.effort_level}'.")
            else:
                print(f"Current effort level: {rag_engine.session.effort_level}")
            continue

        print(f"\nProcessing RAG query: '{prompt}'...")
        res = rag_engine.query(prompt, use_ai=True, use_session=True)

        if res.get("ai_response"):
            print("\n=== RAG AI Assistant Answer ===")
            print(res["ai_response"])
        else:
            if res.get("error"):
                print(f"\n[AI Notice] {res['error']}")
            print("\n=== Retrieved Vault Context ===")
            print(res["context"])



def lint_prose_menu():
    target = input("\nEnter chapter file path to lint (e.g. C:\\GitHub\\sr6yuriko\\chapters\\character_log.qmd): ").strip()
    if not target:
        return
    report, err = analyze_prose(target)
    if err:
        print(f"\n[Error] {err}")
    else:
        print()
        print_prose_report(report)


def continuity_menu():
    target = input("\nEnter repository path for campaign continuity audit (e.g. C:\\GitHub\\sr6yuriko): ").strip()
    if not target:
        return
    report, err = build_continuity_report(target)
    if err:
        print(f"\n[Error] {err}")
    else:
        print()
        print_continuity_report(report)


def narration_menu():
    target = input("\nEnter chapter file path to narrate (e.g. C:\\GitHub\\sr6yuriko\\chapters\\character_log.qmd): ").strip()
    if not target:
        return
    out_file, err = generate_narration(target)
    if err:
        print(f"\n[Notice] {err}")
    else:
        print(f"\n[OK] TTS Narration target: {out_file}")


def commlink_import_menu():
    print("\n--- COMMLINK6 DATASET IMPORT ---")
    latest_jar = find_latest_commlink_jar()
    print(f"Auto-detected latest JAR: {latest_jar or 'None'}")
    jar_input = input("Press ENTER to import from latest JAR (or enter custom JAR path): ").strip()
    target_jar = jar_input if jar_input else latest_jar

    print(f"\nProcessing CommLink6 dataset import from '{target_jar}'...")
    ok, msg = compile_commlink_datasets(jar_path=target_jar)
    print(f"\n{msg}")


def vault_compile_menu(db: RulesDB):
    print("\n--- RE-INDEX SHADOWRUN RULES VAULT ---")
    print(f"Vault Directory: {db.vault_dir}")
    confirm = input("Re-index all vault markdown files into SQLite? [Y/n]: ").strip()
    if confirm.lower() in ['', 'y', 'yes']:
        count, msg = db.compile_vault(force=True)
        print(f"\n{msg}")


def show_config_info(cm: CharacterManager):
    chars = cm.list_characters()
    info = get_dataset_info()
    print("\n--- WORKSPACE & PORTFOLIO CONFIGURATION ---")
    print(f"Config path   : {cm.config_path or 'Default (characters.yaml)'}")
    print(f"GitHub root   : {cm.github_root}")
    print(f"CommLink6 JAR : {info.get('commlink_jar', 'Not imported yet')}")
    print("\nConfigured Characters:")
    for c in chars:
        print(f"- {c['id']:<10} | Name: {c['name']:<15} | Path: {c['path']}")


def run_interactive_menu():
    cm = CharacterManager()
    db = RulesDB()
    rag_engine = RAGEngine()

    from sr6core.cli import run_sync_all

    while True:
        print_banner()
        print(" [1] Manage Character Portfolios (Yuriko, Velvet, Union)")
        print(" [2] Quick Rules Search (FTS5 Keyword Search)")
        print(" [3] Rules RAG AI Reference Assistant (Gemini / Context)")
        print(" [4] View Portfolio & Database Configuration Info")
        print(" [5] Lint Quarto Chapter Prose (Anti-Slop Audit)")
        print(" [6] Check Campaign Story Continuity")
        print(" [7] Generate Audio TTS Narration")
        print(" [8] Run Full Ecosystem Sync (sync-all)")
        print(" [9] Import / Update CommLink6 Datasets")
        print(" [10] Re-index Shadowrun Rules Vault Markdown Files")
        print(" [11] Exit")

        choice = input("\nSelect menu option [1-11]: ").strip()

        if choice == '1':
            manage_characters_menu(cm)
        elif choice == '2':
            rules_search_menu(db)
        elif choice == '3':
            rules_rag_menu(rag_engine)
        elif choice == '4':
            show_config_info(cm)
        elif choice == '5':
            lint_prose_menu()
        elif choice == '6':
            continuity_menu()
        elif choice == '7':
            narration_menu()
        elif choice == '8':
            run_sync_all()
        elif choice == '9':
            commlink_import_menu()
        elif choice == '10':
            vault_compile_menu(db)
        elif choice == '11' or choice.lower() == 'q':
            print("\nExiting SR6 Core CLI. Good chummer!")
            sys.exit(0)
        else:
            print("Invalid choice. Please select [1-11].")
