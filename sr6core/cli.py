"""
Command-Line Interface for SR6 Core.
"""

import sys
import argparse
from sr6core.rules_db import RulesDB
from sr6core.web.app import create_app


def main():
    parser = argparse.ArgumentParser(description="SR6 Core Utility & Dashboard CLI")
    subparsers = parser.add_subparsers(dest="command", help="Sub-command to execute")

    # dashboard subcommand
    subparsers.add_parser("dashboard", help="Launch the FastHTML multi-character dashboard")

    # search subcommand
    search_parser = subparsers.add_parser("search", help="Search the rules vault database")
    search_parser.add_argument("query", type=str, help="Search query string")

    args = parser.parse_args()

    if args.command == "dashboard" or len(sys.argv) == 1:
        print("Launching SR6 Multi-Character Dashboard...")
        app = create_app()
        app.run()
    elif args.command == "search":
        db = RulesDB()
        results = db.search_rules(args.query)
        print(f"Rules search results for '{args.query}':")
        for r in results:
            print(f"- [{r.get('id')}] {r.get('topic')} ({r.get('source')} p.{r.get('page')})")


if __name__ == "__main__":
    main()
