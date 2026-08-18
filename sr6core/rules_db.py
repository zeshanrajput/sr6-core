"""
Compact SQLite Rules Vault Engine for Shadowrun 6th Edition.
Provides rules search and cross-referencing between CommLink6 XML datasets, SRM contacts, and Rules Vault text.
"""

import os
import re
import sqlite3
from typing import Dict, Any, List, Optional, Tuple

DEFAULT_DB_PATH = os.path.join(os.path.expanduser("~"), ".sr6", "rules_index.db")
DEFAULT_VAULT_DIR = os.path.join(os.path.expanduser("~"), "OneDrive", "Desktop", "SR6", "ebooks", "shadowrun_rules_vault")


class RulesDB:
    def __init__(self, db_path: str = DEFAULT_DB_PATH, vault_dir: str = DEFAULT_VAULT_DIR):
        self.db_path = os.environ.get("SR6_RULES_DB_PATH", db_path)
        self.vault_dir = os.environ.get("SR6_RULES_VAULT_DIR", vault_dir)
        dirname = os.path.dirname(self.db_path)
        if dirname:
            os.makedirs(dirname, exist_ok=True)
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row
        self._init_db()

    def _get_rules_columns(self) -> List[str]:
        cursor = self.conn.cursor()
        try:
            return [row[1] for row in cursor.execute("PRAGMA table_info(rules)").fetchall()]
        except Exception:
            return ["id", "topic", "chapter", "source", "content"]

    def _init_db(self):
        with self.conn:
            self.conn.execute("""
                CREATE TABLE IF NOT EXISTS rules (
                    id TEXT PRIMARY KEY,
                    topic TEXT,
                    chapter TEXT,
                    source TEXT,
                    page TEXT,
                    authority_level INTEGER DEFAULT 3,
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

            cols = [row[1] for row in self.conn.execute("PRAGMA table_info(rules)").fetchall()]
            if "page" not in cols:
                try:
                    self.conn.execute("ALTER TABLE rules ADD COLUMN page TEXT")
                except Exception:
                    pass
            if "authority_level" not in cols:
                try:
                    self.conn.execute("ALTER TABLE rules ADD COLUMN authority_level INTEGER DEFAULT 3")
                except Exception:
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

        cols = self._get_rules_columns()
        has_page = "page" in cols
        has_auth = "authority_level" in cols

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
            auth_level = int(fm.get("authority_level", 3)) if str(fm.get("authority_level", "")).isdigit() else 3
            tags = ",".join(fm.get("tags", [])) if isinstance(fm.get("tags"), list) else str(fm.get("tags", ""))

            if has_page and has_auth:
                cursor.execute(
                    "INSERT OR REPLACE INTO rules (id, topic, chapter, source, page, authority_level, tags, content) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                    (rule_id, topic, chapter, source, page, auth_level, tags, content)
                )
            elif has_auth:
                cursor.execute(
                    "INSERT OR REPLACE INTO rules (id, topic, chapter, source, authority_level, tags, content) VALUES (?, ?, ?, ?, ?, ?, ?)",
                    (rule_id, topic, chapter, source, auth_level, tags, content)
                )
            else:
                cursor.execute(
                    "INSERT OR REPLACE INTO rules (id, topic, chapter, source, tags, content) VALUES (?, ?, ?, ?, ?, ?)",
                    (rule_id, topic, chapter, source, tags, content)
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

        # Re-populate official SRM contacts table
        from sr6core.srm_contacts import populate_srm_contacts_table
        populate_srm_contacts_table(self.db_path)

        return indexed_count, f"Successfully compiled {indexed_count} rules from '{self.vault_dir}' into SQLite."

    def query_rule(self, rule_id: str) -> Optional[Dict[str, Any]]:
        """Fast O(1) lookup of a rule by ID."""
        cursor = self.conn.cursor()
        row = cursor.execute("SELECT * FROM rules WHERE id = ? OR lower(id) = ?", (rule_id, rule_id.lower())).fetchone()
        if row:
            return dict(row)
        return None

    def search_rules(self, query: str, limit: int = 10, category: Optional[str] = None) -> List[Dict[str, Any]]:
        """Full-text search across rules vault with topic ranking, category awareness, and TOC filtering."""
        if not query or not query.strip():
            return []
            
        clean_q = query.strip()
        norm_q = clean_q.lower()
        norm_no_hyphen = norm_q.replace("-", " ")

        cols = self._get_rules_columns()
        select_clause = ", ".join([c for c in cols if c in ["id", "topic", "chapter", "source", "page", "authority_level", "content"]])
        if not select_clause:
            select_clause = "*"

        cursor = self.conn.cursor()

        ignore_clause = """
            lower(topic) NOT LIKE '%content%' 
            AND lower(topic) NOT LIKE 'index%' 
            AND lower(topic) NOT LIKE '%game concepts%'
            AND lower(topic) NOT LIKE '%credits%'
        """

        # 1. Exact topic match (with or without hyphens)
        rows = cursor.execute(
            f"SELECT {select_clause} FROM rules WHERE (lower(topic) = ? OR lower(topic) = ?) AND {ignore_clause} LIMIT ?",
            (norm_q, norm_no_hyphen, limit)
        ).fetchall()
        if rows:
            return [dict(r) for r in rows]

        # 2. Topic prefix / title containment match
        rows = cursor.execute(
            f"SELECT {select_clause} FROM rules WHERE (lower(topic) LIKE ? OR lower(topic) LIKE ? OR lower(topic) LIKE ? OR lower(topic) LIKE ?) AND {ignore_clause} LIMIT ?",
            (f"{norm_q}%", f"anthro - {norm_q}%", f"% {norm_q}%", f"%{norm_q}%", limit)
        ).fetchall()
        if rows:
            return [dict(r) for r in rows]

        # 3. Individual significant words in topic
        words = [w.strip() for w in re.split(r"[\s\-_]+", norm_q) if len(w.strip()) >= 4 and w.strip() not in ["array", "drone", "heavy", "light", "medium", "small"]]
        if words:
            for w in words:
                rows = cursor.execute(
                    f"SELECT {select_clause} FROM rules WHERE lower(topic) LIKE ? AND {ignore_clause} LIMIT ?",
                    (f"%{w}%", limit)
                ).fetchall()
                if rows:
                    return [dict(r) for r in rows]

        # 4. FTS search excluding TOC/Index
        try:
            fts_term = re.sub(r"[^\w\s]", " ", query).strip()
            if fts_term:
                fts_q = f'"{fts_term}"'
                rows = cursor.execute(
                    f"""
                    SELECT {select_clause} 
                    FROM rules r 
                    JOIN rules_fts fts ON r.id = fts.id 
                    WHERE rules_fts MATCH ? 
                    AND {ignore_clause}
                    LIMIT ?
                    """,
                    (fts_q, limit)
                ).fetchall()
                if rows:
                    return [dict(r) for r in rows]
        except Exception:
            pass

        # 5. Fallback content/topic LIKE query
        fallback_term = re.sub(r"[^\w\s]", " ", query).strip()
        rows = cursor.execute(
            f"SELECT {select_clause} FROM rules WHERE (topic LIKE ? OR content LIKE ?) AND {ignore_clause} LIMIT ?",
            (f"%{fallback_term}%", f"%{fallback_term}%", limit)
        ).fetchall()
        return [dict(r) for r in rows]

    def get_enriched_item(self, target: str) -> Optional[Dict[str, Any]]:
        """
        Cross-references CommLink6 XML dataset tables and official SRM contacts with Rules Vault text.
        """
        if not target or not target.strip():
            return None

        clean_target = target.strip()
        norm_target = clean_target.lower().replace(" ", "_")

        cursor = self.conn.cursor()
        dataset_info = None
        item_type = "unknown"

        tables = [
            ("ref_contacts", "srm_contact"),
            ("ref_qualities", "quality"),
            ("ref_spells", "spell"),
            ("ref_complex_forms", "complex_form"),
            ("ref_gear", "gear"),
            ("ref_metatypes", "metatype")
        ]

        for tbl, t_label in tables:
            try:
                row = cursor.execute(
                    f"SELECT * FROM {tbl} WHERE id = ? OR lower(id) = ? OR lower(name) = ?",
                    (clean_target, norm_target, clean_target.lower())
                ).fetchone()
                if row:
                    dataset_info = dict(row)
                    item_type = t_label
                    break
            except Exception:
                pass

        vault_rule = self.query_rule(norm_target) or self.query_rule(clean_target)
        if not vault_rule:
            matches = self.search_rules(clean_target, limit=5)
            for m in matches:
                if m.get("topic", "").lower() == clean_target.lower() or m.get("id", "").lower() == norm_target:
                    vault_rule = self.query_rule(m["id"])
                    break

        if not dataset_info and not vault_rule:
            return None

        name = (dataset_info.get("name") if dataset_info else None) or (vault_rule.get("topic") if vault_rule else clean_target.title())
        item_id = (dataset_info.get("id") if dataset_info else None) or (vault_rule.get("id") if vault_rule else norm_target)

        return {
            "id": item_id,
            "name": name,
            "item_type": item_type,
            "commlink_data": dataset_info,
            "rules_vault": vault_rule
        }

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
