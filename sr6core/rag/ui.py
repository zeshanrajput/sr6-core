"""
Rich Terminal User Interface for SR6 RAG Rules Engine.
Provides beautiful, colorized Markdown rendering, authority-level badges, citation tables, and interactive slash command sessions.
"""

from typing import Dict, Any, List, Optional

try:
    from rich.console import Console
    from rich.panel import Panel
    from rich.markdown import Markdown
    from rich.table import Table
    from rich.text import Text
    from rich.box import ROUNDED, DOUBLE_EDGE
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False


AUTH_LEVEL_STYLES = {
    1: ("bold magenta", "Level 1: SRM Exception"),
    2: ("bold cyan", "Level 2: Supplement"),
    3: ("bold green", "Level 3: Core Rulebook"),
    4: ("bold yellow", "Level 4: Homebrew / Unofficial"),
}


def get_auth_badge(level: int) -> str:
    style, label = AUTH_LEVEL_STYLES.get(level, ("white", f"Level {level}"))
    return f"[{style}][{label}][/{style}]"


def print_search_results_rich(query: str, results: List[Dict[str, Any]]):
    """Prints a styled Rich table of rules vault search results."""
    if not RICH_AVAILABLE:
        print(f"\n=== Rules Vault Search Results for '{query}' ===")
        for r in results:
            print(f"- [{r.get('id')}] {r.get('topic', 'N/A')} ({r.get('source', 'SR6')} p.{r.get('page', '')}) [Auth Level {r.get('authority_level', 3)}]")
        return

    console = Console()
    table = Table(title=f"Shadowrun 6e Rules Vault Search: '{query}'", box=ROUNDED, header_style="bold cyan")
    table.add_column("Authority Level", justify="left", style="bold")
    table.add_column("Topic / Rule", style="bold white")
    table.add_column("Source", style="green")
    table.add_column("Page", justify="right", style="yellow")
    table.add_column("CommLink6 Dataset", style="dim cyan")

    for r in results:
        auth_lvl = r.get("authority_level", 3)
        style, label = AUTH_LEVEL_STYLES.get(auth_lvl, ("white", f"Level {auth_lvl}"))
        auth_cell = Text(label, style=style)
        
        topic = r.get("topic", r.get("id", "N/A"))
        source = r.get("source", "SR6 Core")
        page = str(r.get("page", "N/A"))
        
        cdata = r.get("commlink_data")
        cdata_str = f"{cdata.get('name', '')} ({cdata.get('category', '')})" if cdata else "-"
        
        table.add_row(auth_cell, topic, source, page, cdata_str)

    console.print()
    console.print(table)
    console.print()


def render_rag_result_rich(res: Dict[str, Any], show_context: bool = False):
    """Renders a complete RAG query answer with Rich header panel, Markdown body, and citation table."""
    if not RICH_AVAILABLE:
        prompt = res.get("query", "")
        print(f"\n=== RAG AI Assistant Answer for '{prompt}' ===")
        if res.get("ai_response"):
            print(res["ai_response"])
        elif res.get("error"):
            print(f"[AI Notice] {res['error']}")
            print("\n=== Retrieved Context ===")
            print(res.get("context", ""))
        return

    console = Console()
    prompt = res.get("query", "")
    provider = res.get("provider_name", "gemini").upper()
    model = res.get("model_name", "flash-latest")
    effort = res.get("effort_level") or "default"
    char_id = res.get("char_id")
    char_str = f" | Runner: [bold gold1]{char_id.upper()}[/bold gold1]" if char_id else ""

    header_text = f"[bold cyan]Provider:[/bold cyan] {provider} | [bold cyan]Model:[/bold cyan] {model} | [bold cyan]Thinking Effort:[/bold cyan] {effort}{char_str}"
    console.print()
    console.print(Panel(f"[bold white]{prompt}[/bold white]\n\n{header_text}", title="[bold magenta]SR6 RAG RULES VAULT QUERY[/bold magenta]", box=ROUNDED, border_style="cyan"))

    ai_response = res.get("ai_response")
    error = res.get("error")

    if ai_response:
        console.print()
        console.print(Panel(Markdown(ai_response), title="[bold green]AUTHORITATIVE RULES ANSWER[/bold green]", box=ROUNDED, border_style="green"))
    elif error:
        console.print()
        console.print(Panel(f"[bold red]AI Engine Notice:[/bold red] {error}", title="[bold red]NOTICE[/bold red]", box=ROUNDED, border_style="red"))

    rules = res.get("rules", [])
    if rules or show_context:
        table = Table(title="Retrieved Rules Vault Citations & Authority Matrix", box=ROUNDED, header_style="bold magenta")
        table.add_column("Authority Hierarchy", justify="left")
        table.add_column("Topic / Rule Section", style="bold white")
        table.add_column("Source Book", style="cyan")
        table.add_column("Page", justify="right", style="yellow")

        for r in rules:
            auth_lvl = r.get("authority_level", 3)
            style, label = AUTH_LEVEL_STYLES.get(auth_lvl, ("white", f"Level {auth_lvl}"))
            auth_cell = Text(label, style=style)

            topic = r.get("topic", r.get("id", "N/A"))
            source = r.get("source", "SR6 Core")
            page = str(r.get("page", "N/A"))
            table.add_row(auth_cell, topic, source, page)

        console.print()
        console.print(table)

    console.print()


def run_interactive_rag_session_rich(rag_engine: Any):
    """Runs a rich interactive RAG session with live status spinners and slash commands."""
    if not RICH_AVAILABLE:
        from sr6core.menu import rules_rag_menu
        rules_rag_menu(rag_engine)
        return

    console = Console()
    active_char = None

    console.print()
    console.print(Panel(
        "[bold white]SHADOWRUN 6TH EDITION RAG RULES AI ASSISTANT[/bold white]\n"
        "[dim]Interactive Rules Reference & Character Dossier Engine[/dim]\n\n"
        "[bold yellow]Slash Commands:[/bold yellow]\n"
        "  [cyan]/provider <gemini|llama>[/cyan] : Switch LLM Provider\n"
        "  [cyan]/model <name>[/cyan]          : Switch Model (e.g. flash-latest, gemma-2-9b-it)\n"
        "  [cyan]/url <endpoint>[/cyan]        : Set local llama.cpp endpoint URL\n"
        "  [cyan]/char <yuriko|velvet|union|off>[/cyan] : Bind active runner dossier context\n"
        "  [cyan]/effort <high|medium|low>[/cyan] : Set thinking effort budget\n"
        "  [cyan]/clear[/cyan]                 : Reset conversation thread memory\n"
        "  [cyan]/search <query>[/cyan]        : Perform raw FTS rules vault search\n"
        "  [cyan]/help[/cyan]                  : Show slash command menu\n"
        "  [cyan]/exit or B[/cyan]            : Return to main menu",
        title="[bold magenta]SR6 RAG SESSION[/bold magenta]",
        box=DOUBLE_EDGE,
        border_style="magenta"
    ))

    while True:
        prov = rag_engine.session.provider_name.upper()
        mod = rag_engine.session.model_name
        eff = rag_engine.session.effort_level or 'default'
        char_lbl = f" | Runner: [gold1]{active_char.upper()}[/gold1]" if active_char else ""
        prompt_status = f"[bold cyan][{prov} | {mod} | Effort: {eff}{char_lbl}][/bold cyan] RAG Prompt > "

        try:
            prompt = console.input(f"\n{prompt_status}").strip()
        except (KeyboardInterrupt, EOFError):
            console.print("\n[dim]Exiting RAG session...[/dim]")
            break

        if not prompt:
            continue

        if prompt.lower() in ['b', '/exit', '/quit', '/back']:
            console.print("[green]Returning to main menu.[/green]")
            break

        if prompt.lower() == '/clear':
            rag_engine.session.clear_history()
            console.print("[bold green][+] Conversation thread memory cleared.[/bold green]")
            continue

        if prompt.lower() in ['/help', '?']:
            console.print("\n[bold yellow]Available Slash Commands:[/bold yellow]")
            console.print("  /provider gemini|llama  : Switch LLM provider")
            console.print("  /model <name>          : Switch model name (e.g. flash-latest, pro, gemma)")
            console.print("  /url <endpoint>        : Set local llama.cpp endpoint URL")
            console.print("  /char yuriko|velvet|union|off : Bind active runner dossier context")
            console.print("  /effort high|medium|low: Adjust thinking budget")
            console.print("  /search <term>         : Search rules vault directly without AI")
            console.print("  /clear                 : Reset active conversation memory")
            console.print("  /exit                  : Back to main menu")
            continue

        if prompt.lower().startswith('/provider'):
            parts = prompt.split(maxsplit=1)
            if len(parts) > 1:
                new_prov = parts[1].strip()
                rag_engine.session.set_provider(new_prov)
                console.print(f"[bold green][+] Provider set to '{rag_engine.session.provider_name}'.[/bold green]")
            else:
                console.print(f"Current provider: [cyan]{rag_engine.session.provider_name}[/cyan]")
            continue

        if prompt.lower().startswith('/url'):
            parts = prompt.split(maxsplit=1)
            if len(parts) > 1:
                rag_engine.session.llama_url = parts[1].strip()
                console.print(f"[bold green][+] Local llama.cpp URL set to '{rag_engine.session.llama_url}'.[/bold green]")
            else:
                console.print(f"Current llama URL: [cyan]{rag_engine.session.llama_url}[/cyan]")
            continue

        if prompt.lower().startswith('/char'):
            parts = prompt.split(maxsplit=1)
            if len(parts) > 1:
                c_val = parts[1].strip().lower()
                active_char = None if c_val in ['off', 'none', 'clear'] else c_val
                console.print(f"[bold green][+] Active runner context: '{active_char or 'None'}'.[/bold green]")
            else:
                console.print(f"Current runner context: [cyan]{active_char or 'None'}[/cyan]")
            continue

        if prompt.lower().startswith('/model'):
            parts = prompt.split(maxsplit=1)
            if len(parts) > 1:
                new_model = parts[1].strip()
                rag_engine.session.set_model(new_model)
                console.print(f"[bold green][+] Model updated to '{rag_engine.session.model_name}'.[/bold green]")
            else:
                console.print(f"Current model: [cyan]{rag_engine.session.model_name}[/cyan]")
            continue

        if prompt.lower().startswith('/effort'):
            parts = prompt.split(maxsplit=1)
            if len(parts) > 1:
                new_effort = parts[1].strip()
                rag_engine.session.set_effort(new_effort)
                console.print(f"[bold green][+] Effort level updated to '{rag_engine.session.effort_level}'.[/bold green]")
            else:
                console.print(f"Current effort level: [cyan]{rag_engine.session.effort_level}[/cyan]")
            continue

        if prompt.lower().startswith('/search'):
            parts = prompt.split(maxsplit=1)
            if len(parts) > 1:
                sq = parts[1].strip()
                results = rag_engine.search(sq, limit=10)
                print_search_results_rich(sq, results)
            else:
                console.print("[yellow]Usage: /search <term>[/yellow]")
            continue

        ctx_msg = f" (Runner: {active_char.upper()})" if active_char else ""
        with console.status(f"[bold cyan]Consulting Shadowrun Rules Vault & LLM Engine{ctx_msg}...[/bold cyan]", spinner="dots"):
            res = rag_engine.query(
                prompt,
                use_ai=True,
                use_session=True,
                char_id=active_char
            )

        render_rag_result_rich(res, show_context=True)
