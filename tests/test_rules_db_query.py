"""
Unit tests for Rules DB SQL query engine, schema inspector, and CLI commands.
"""

import json
import pytest
from sr6core.rules_db import (
    execute_db_query,
    get_db_schema,
    format_query_results,
    format_db_schema,
)


def test_execute_db_query_basic():
    columns, rows = execute_db_query("SELECT id, name, cost FROM ref_cyberware LIMIT 3")
    assert columns == ["id", "name", "cost"]
    assert len(rows) in (2, 3)
    assert all(isinstance(r[2], (int, type(None))) for r in rows)


def test_execute_db_query_readonly_enforcement():
    with pytest.raises(ValueError, match="Only read-only queries"):
        execute_db_query("INSERT INTO ref_cyberware (id, name) VALUES ('hack', 'Hack')")

    with pytest.raises(ValueError, match="Destructive SQL operations"):
        execute_db_query("SELECT * FROM ref_cyberware; DROP TABLE ref_cyberware;")

    with pytest.raises(ValueError, match="Only read-only queries"):
        execute_db_query("DELETE FROM ref_weapons")


def test_get_db_schema_all_tables():
    info = get_db_schema()
    assert "tables" in info
    names = [t["name"] for t in info["tables"]]
    assert "ref_cyberware" in names
    assert "ref_weapons" in names
    assert "rules" in names
    assert "dataset_meta" in names


def test_get_db_schema_single_table():
    info = get_db_schema("ref_cyberware")
    assert info["table"] == "ref_cyberware"
    assert info["row_count"] > 0
    col_names = [c["name"] for c in info["columns"]]
    assert "id" in col_names
    assert "name" in col_names
    assert "cost" in col_names
    assert "essence" in col_names
    assert "sample" in info
    assert info["sample"]["id"] != ""


def test_format_query_results_markdown():
    cols = ["name", "cost"]
    rows = [("Cyberarm", 20000), ("Wired Reflexes", 40000)]
    md = format_query_results(cols, rows, fmt="markdown")
    assert "| name | cost |" in md
    assert "| Cyberarm | 20000 |" in md
    assert "*(2 rows returned)*" in md


def test_format_query_results_json():
    cols = ["name", "cost"]
    rows = [("Cyberarm", 20000)]
    j = format_query_results(cols, rows, fmt="json")
    parsed = json.loads(j)
    assert isinstance(parsed, list)
    assert parsed[0]["name"] == "Cyberarm"
    assert parsed[0]["cost"] == 20000


def test_format_query_results_csv():
    cols = ["name", "cost"]
    rows = [("Cyberarm", 20000)]
    c = format_query_results(cols, rows, fmt="csv")
    assert "name,cost" in c
    assert "Cyberarm,20000" in c


def test_format_db_schema():
    info = get_db_schema("ref_qualities")
    formatted = format_db_schema(info, fmt="markdown")
    assert "=== Schema for Table: ref_qualities" in formatted
    assert "karma" in formatted
