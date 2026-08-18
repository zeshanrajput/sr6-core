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
        print(" [4] Export Printable PDF Reference Card Stack (Postcards / Index Cards)")
        print(" [5] Export Printable PDF 1-2 Page Base Sheet")
        print(" [6] Export Modular Plain-Text Sheets (Base, Contacts, Combat, etc.)")
        print(" [7] Export Roll20 JSON")
        print(" [8] Export Genesis / CommLink6 Compliant XML")
        print(" [9] Export Reference Cards Deck (Markdown)")
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
            csize = input("Select Card Size (1: Postcard 4.25x5.5, 2: Index 4x6, 3: Index 3x5) [1]: ").strip()
            size_map = {"1": "postcard_4x5.5", "2": "index_4x6", "3": "index_3x5"}
            card_size = size_map.get(csize, "postcard_4x5.5")
            repo_dir = cm.get_character_repo_dir(char_id) or "."
            pdf_path = os.path.join(repo_dir, "output", "pdf", f"{char_id}_cards_deck.pdf")
            out_file = cm.export_character(char_id, fmt="pdf_deck", output_path=pdf_path, card_size=card_size)
            print(f"\n[OK] Generated Printable PDF Card Deck: {out_file}\n")

        elif choice == '5':
            repo_dir = cm.get_character_repo_dir(char_id) or "."
            pdf_path = os.path.join(repo_dir, "output", "pdf", f"{char_id}_base_sheet.pdf")
            out_file = cm.export_character(char_id, fmt="pdf_base", output_path=pdf_path)
            print(f"\n[OK] Generated Printable PDF Base Sheet: {out_file}\n")

        elif choice == '6':
            sheets = cm.export_character(char_id, fmt="text_modular")
            repo_dir = cm.get_character_repo_dir(char_id) or "."
            txt_dir = os.path.join(repo_dir, "output", "text")
            os.makedirs(txt_dir, exist_ok=True)
            for fname, content in sheets.items():
                target = os.path.join(txt_dir, fname)
                with open(target, "w", encoding="utf-8") as f:
                    f.write(content)
            print(f"\n[OK] Generated {len(sheets)} Modular Text Sheets in {txt_dir}\n")

        elif choice == '7':
            out = cm.export_character(char_id, fmt="roll20")
            print(f"\n--- Roll20 JSON Export ({char_id}) ---")
            print(out)

        elif choice == '8':
            out = cm.export_character(char_id, fmt="xml")
            print(f"\n--- CommLink6 Compliant XML Export ({char_id}) ---")
            print(out)

        elif choice == '9':
            out = cm.export_character(char_id, fmt="cards")
            print(f"\n--- Reference Cards Deck Export ({char_id}) ---")
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


def card_lookup_menu():
    cat = input("\nEnter category (quality, spell, complex_form, weapon, cyberware, vehicle, program, gear): ").strip()
    if not cat:
        return
    item_id = input("Enter item ID or name (e.g. ambidextrous, ares_predator_vi, heal): ").strip()
    if not item_id:
        return
    from sr6core.cards import get_item_card
    card = get_item_card(cat, item_id)
    print(f"\n{card['markdown']}\n")


def rules_rag_menu(rag_engine: RAGEngine):
    from sr6core.rag import run_interactive_rag_session_rich
    run_interactive_rag_session_rich(rag_engine)


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
        print(" [3] Rules RAG AI Reference Assistant (Gemini / llama.cpp)")
        print(" [4] Inspect Reference Item Card (Quality, Weapon, Spell, Cyberware)")
        print(" [5] View Portfolio & Database Configuration Info")
        print(" [6] Lint Quarto Chapter Prose (Anti-Slop Audit)")
        print(" [7] Check Campaign Story Continuity")
        print(" [8] Generate Audio TTS Narration")
        print(" [9] Run Full Ecosystem Sync (sync-all)")
        print(" [10] Import / Update CommLink6 Datasets")
        print(" [11] Re-index Shadowrun Rules Vault Markdown Files")
        print(" [12] Exit")

        choice = input("\nSelect menu option [1-12]: ").strip()

        if choice == '1':
            manage_characters_menu(cm)
        elif choice == '2':
            rules_search_menu(db)
        elif choice == '3':
            rules_rag_menu(rag_engine)
        elif choice == '4':
            card_lookup_menu()
        elif choice == '5':
            show_config_info(cm)
        elif choice == '6':
            lint_prose_menu()
        elif choice == '7':
            continuity_menu()
        elif choice == '8':
            narration_menu()
        elif choice == '9':
            run_sync_all()
        elif choice == '10':
            commlink_import_menu()
        elif choice == '11':
            vault_compile_menu(db)
        elif choice == '12' or choice.lower() == 'q':
            print("\nExiting SR6 Core CLI. Good chummer!")
            sys.exit(0)
        else:
            print("Invalid choice. Please select [1-12].")
