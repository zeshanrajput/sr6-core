"""
Compact SQLite Rules Vault Engine for Shadowrun 6th Edition.
Replaces 500MB+ JSON dumps with a lightweight, indexed ~30-50MB SQLite database.
"""

import os
import re
import sqlite3
from typing import Dict, Any, List, Optional, Tuple

DEFAULT_DB_PATH = os.path.expanduser(r"~\.sr6\rules_index.db")
DEFAULT_VAULT_DIR = os.path.expanduser(r"~\OneDrive\Desktop\SR6\ebooks\shadowrun_rules_vault")


class RulesDB:
    def __init__(self, db_path: str = DEFAULT_DB_PATH, vault_dir: str = DEFAULT_VAULT_DIR):
        self.db_path = os.environ.get("SR6_RULES_DB_PATH", db_path)
        self.vault_dir = os.environ.get("SR6_RULES_VAULT_DIR", vault_dir)
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row
        self._init_db()

    def _init_db(self):
        with self.conn:
            self.conn.execute("""
                CREATE TABLE IF NOT EXISTS rules (
                    id TEXT PRIMARY KEY,
                    topic TEXT,
                    chapter TEXT,
                    source TEXT,
                    page TEXT,
                    tags TEXT,
                    content TEXT
                )
            """)
            self.conn.execute("""
                CREATE TABLE IF NOT EXISTS sub_items (
                    id TEXT,
                    name TEXT,
                    namespace TEXT,
                    content TEXT,
                    PRIMARY KEY (id, name)
                )
            """)
            try:
                self.conn.execute("""
                    CREATE VIRTUAL TABLE IF NOT EXISTS rules_fts USING fts5(
                        id, topic, chapter, tags, content
                    )
                """)
            except sqlite3.OperationalError:
                pass

    def compile_vault(self, force: bool = False) -> Tuple[int, str]:
        """Scans vault markdown files and indexes them into SQLite."""
        if not os.path.exists(self.vault_dir):
            return 0, f"Vault directory not found: {self.vault_dir}"

        cursor = self.conn.cursor()
        if not force:
            count = cursor.execute("SELECT COUNT(*) FROM rules").fetchone()[0]
            if count > 0:
                return count, "Database already compiled"

        cursor.execute("DELETE FROM rules")
        cursor.execute("DELETE FROM sub_items")
        try:
            cursor.execute("DELETE FROM rules_fts")
        except sqlite3.OperationalError:
            pass

        indexed_count = 0
        for filename in os.listdir(self.vault_dir):
            if not filename.endswith(".md"):
                continue

            filepath = os.path.join(self.vault_dir, filename)
            with open(filepath, "r", encoding="utf-8") as f:
                content = f.read()

            fm = self._parse_frontmatter(content)
            if not fm or "id" not in fm:
                continue

            rule_id = str(fm["id"])
            topic = str(fm.get("topic", ""))
            chapter = str(fm.get("chapter", ""))
            source = str(fm.get("source", ""))
            page = str(fm.get("page", ""))
            tags = ",".join(fm.get("tags", [])) if isinstance(fm.get("tags"), list) else str(fm.get("tags", ""))

            cursor.execute(
                "INSERT OR REPLACE INTO rules (id, topic, chapter, source, page, tags, content) VALUES (?, ?, ?, ?, ?, ?, ?)",
                (rule_id, topic, chapter, source, page, tags, content)
            )
            try:
                cursor.execute(
                    "INSERT INTO rules_fts (id, topic, chapter, tags, content) VALUES (?, ?, ?, ?, ?)",
                    (rule_id, topic, chapter, tags, content)
                )
            except sqlite3.OperationalError:
                pass

            indexed_count += 1

        self.conn.commit()
        return indexed_count, f"Successfully compiled {indexed_count} rules into SQLite."

    def query_rule(self, rule_id: str) -> Optional[Dict[str, Any]]:
        """Fast O(1) lookup of a rule by ID."""
        cursor = self.conn.cursor()
        row = cursor.execute("SELECT * FROM rules WHERE id = ? OR lower(id) = ?", (rule_id, rule_id.lower())).fetchone()
        if row:
            return dict(row)
        return None

    def search_rules(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Full-text search across rules vault."""
        if not query or not query.strip():
            return []
            
        clean_q = re.sub(r"[^\w\s]", "", query).strip()
        if not clean_q:
            return []

        cursor = self.conn.cursor()
        try:
            rows = cursor.execute(
                """
                SELECT r.id, r.topic, r.chapter, r.source, r.page 
                FROM rules r 
                JOIN rules_fts fts ON r.id = fts.id 
                WHERE rules_fts MATCH ? 
                LIMIT ?
                """,
                (f'"{clean_q}"', limit)
            ).fetchall()
            if rows:
                return [dict(r) for r in rows]
        except Exception:
            pass

        rows = cursor.execute(
            "SELECT id, topic, chapter, source, page FROM rules WHERE content LIKE ? OR topic LIKE ? LIMIT ?",
            (f"%{clean_q}%", f"%{clean_q}%", limit)
        ).fetchall()
        return [dict(r) for r in rows]

    def _parse_frontmatter(self, content: str) -> Optional[Dict[str, Any]]:
        if not content.startswith("---"):
            return None
        end_idx = content.find("---", 3)
        if end_idx == -1:
            return None
        fm_block = content[3:end_idx]
        fm = {}
        for line in fm_block.split("\n"):
            line_strip = line.strip()
            if ":" in line_strip and not line_strip.startswith("-"):
                parts = line_strip.split(":", 1)
                key = parts[0].strip()
                val = parts[1].strip().strip("'\"")
                fm[key] = val
        return fm
