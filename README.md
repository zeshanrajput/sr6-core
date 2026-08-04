# SR6 Core (`sr6-core`)

The shared engine for Shadowrun 6th Edition character portfolios, creation auditing, rules database search, multi-format exporters, and interactive FastHTML multi-character dashboarding.

## Features

- **Pydantic Data Models**: Standardized schemas for Shadowrun 6e attributes, living personas, skills, qualities, complex forms, echoes, contacts, and drones (`sr6core.models`).
- **Rules Vault DB**: High-performance SQLite and text rules search engine (`sr6core.rules_db`).
- **Creation Audit**: Validation engines for Priority, Point-Buy, Sum-to-Ten, and Lifepath character builds (`sr6core.creation`).
- **Multi-Format Exporters**: Roll20 JSON, Plain-Text VTT character sheet, and Genesis XML generation (`sr6core.exporters`).
- **Multi-Character Web Dashboard**: FastHTML interactive dashboard for scanning and auditing character portfolios across `C:\github\` (`sr6core.web`).
- **Unified CLI**: Command-line interface (`sr6`) for rules querying, character auditing, export generation, and dashboard launching.

## Installation

As an editable dependency in portfolio projects (e.g. `sr6yuriko`, `sr6velvet`, `sr6union`):

```toml
[tool.uv.sources]
sr6-core = { path = "../sr6-core", editable = true }
```

Then run `uv sync`.

## Running the Dashboard

Launch the FastHTML multi-character dashboard:

```bash
uv run python -m sr6core.web.app
```

Or via CLI:

```bash
sr6 dashboard
```
