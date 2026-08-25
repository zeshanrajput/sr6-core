"""
Compact SQLite Rules Vault Engine for Shadowrun 6th Edition.
Provides rules search and cross-referencing between CommLink6 XML datasets, SRM contacts, and Rules Vault text.
"""

import os
import re
import sqlite3
from typing import Dict, Any, List, Optional, Tuple

from pathlib import Path

DEFAULT_DB_PATH = os.environ.get(
    "SR6_RULES_DB_PATH",
    os.path.join(os.path.expanduser("~"), ".sr6", "rules_index.db")
)


def get_default_vault_dir() -> str:
    env_vault = os.getenv("SR6_RULES_VAULT_DIR")
    if env_vault and os.path.exists(env_vault):
        return env_vault

    local_repo_vault = Path(__file__).resolve().parent.parent / "shadowrun_rules_vault"
    if local_repo_vault.exists():
        return str(local_repo_vault)

    onedrive_vault = os.path.join(os.path.expanduser("~"), "OneDrive", "Desktop", "SR6", "ebooks", "shadowrun_rules_vault")
    if os.path.exists(onedrive_vault):
        return onedrive_vault

    return str(local_repo_vault)


def get_default_converted_dir() -> str:
    env_converted = os.getenv("SR6_CONVERTED_MD_DIR")
    if env_converted and os.path.exists(env_converted):
        return env_converted

    local_repo_converted = Path(__file__).resolve().parent.parent / "converted_md"
    if local_repo_converted.exists():
        return str(local_repo_converted)

    onedrive_converted = os.path.join(os.path.expanduser("~"), "OneDrive", "Desktop", "SR6", "ebooks", "converted_md")
    if os.path.exists(onedrive_converted):
        return onedrive_converted

def get_default_pdf_dir() -> str:
    env_pdf = os.getenv("SR6_EBOOKS_DIR")
    if env_pdf and os.path.exists(env_pdf):
        return env_pdf

    onedrive_pdf = os.path.join(os.path.expanduser("~"), "OneDrive", "Desktop", "SR6", "ebooks")
    if os.path.exists(onedrive_pdf):
        return onedrive_pdf

    local_repo_pdf = Path(__file__).resolve().parent.parent / "ebooks"
    return str(local_repo_pdf)


DEFAULT_VAULT_DIR = get_default_vault_dir()
DEFAULT_CONVERTED_DIR = get_default_converted_dir()
DEFAULT_PDF_DIR = get_default_pdf_dir()


def consolidate_edition_matches(rules: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Consolidates duplicate topic entries across regional editions (Hong Kong, Seattle, Berlin)
    and supplements, prioritizing higher authority levels and canonical Hong Kong Core Rulebook.
    """
    if not rules:
        return []

    grouped: Dict[str, List[Dict[str, Any]]] = {}
    for r in rules:
        topic_key = re.sub(r'[^a-zA-Z0-9]', '', (r.get("topic") or "").lower())
        if not topic_key:
            topic_key = r.get("id", "")
        grouped.setdefault(topic_key, []).append(r)

    consolidated = []
    for topic_key, entries in grouped.items():
        # Sort by authority level ascending (Level 1 > Level 2 > Level 3), then prefer Hong Kong (SR6H) over Seattle (6WS)/Berlin (6WB)
        def sort_key(item: Dict[str, Any]) -> Tuple[int, int, str]:
            auth = item.get("authority_level", 3)
            item_id = item.get("id", "")
            # Prioritize SR6H (Hong Kong) if same authority level
            pref = 0 if item_id.startswith("SR6H") else (1 if item_id.startswith("FS") else 2)
            return (auth, pref, item_id)

        sorted_entries = sorted(entries, key=sort_key)
        primary = sorted_entries[0]

        # Gather cross references from remaining entries
        cross_refs = []
        for other in sorted_entries[1:]:
            src = other.get("source", "SR6")
            pg = other.get("page")
            ref_str = f"{src} (p. {pg})" if pg else src
            if ref_str not in cross_refs and ref_str != primary.get("source"):
                cross_refs.append(ref_str)

        if cross_refs:
            primary["cross_references"] = cross_refs

        consolidated.append(primary)

    return consolidated


def attach_rule_statblocks(rule: Dict[str, Any]) -> Dict[str, Any]:
    """Extracts and attaches typed Pydantic stat blocks from rule content if present."""
    try:
        from sr6core.vault.statblock_parser import extract_statblocks_from_rule
        content = rule.get("content", "")
        statblocks = extract_statblocks_from_rule(content)
        if statblocks:
            rule["statblocks"] = statblocks
            rule["statblock"] = statblocks[0]
    except Exception:
        pass
    return rule


class RulesDB:
    def __init__(self, db_path: Optional[str] = None, vault_dir: Optional[str] = None):
        self.db_path = db_path or os.environ.get("SR6_RULES_DB_PATH", DEFAULT_DB_PATH)
        self.vault_dir = vault_dir or os.environ.get("SR6_RULES_VAULT_DIR", get_default_vault_dir())
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

    def search_rules(
        self,
        query: str,
        limit: int = 10,
        category: Optional[str] = None,
        consolidate_editions: bool = True,
        attach_statblocks: bool = True
    ) -> List[Dict[str, Any]]:
        """
        Unified 5-stage hybrid search across rules vault:
        1. Exact topic / name match (O(1))
        2. Multi-word topic containment (all words in topic)
        3. Topic prefix / title containment
        4. FTS5 BM25 weighted search with snippets (Topic x5.0, Tags x3.0, Content x1.0)
        5. Fallback LIKE search
        Followed by canonical edition deduplication and Pydantic stat block attachment.
        """
        if not query or not query.strip():
            return []

        clean_q = query.strip()
        norm_q = clean_q.lower()
        norm_no_hyphen = norm_q.replace("-", " ")

        cols = self._get_rules_columns()
        select_cols = [c for c in cols if c in ["id", "topic", "chapter", "source", "page", "authority_level", "content"]]
        select_clause = ", ".join(select_cols) if select_cols else "*"

        cursor = self.conn.cursor()

        ignore_clause = """
            lower(topic) NOT LIKE '%content%' 
            AND lower(topic) NOT LIKE 'index%' 
            AND lower(topic) NOT LIKE '%game concepts%'
            AND lower(topic) NOT LIKE '%credits%'
        """

        raw_results = []

        # 1. Exact topic match
        rows = cursor.execute(
            f"SELECT {select_clause} FROM rules WHERE (lower(topic) = ? OR lower(topic) = ?) AND {ignore_clause} ORDER BY authority_level ASC, id ASC LIMIT ?",
            (norm_q, norm_no_hyphen, limit * 2)
        ).fetchall()
        if rows:
            raw_results.extend([dict(r) for r in rows])

        # 2. Multi-word topic containment match (ALL words matching in topic)
        if len(raw_results) < limit:
            words = [w.strip() for w in re.split(r"[\s\-_]+", norm_q) if len(w.strip()) >= 3 and w.strip() not in ["array", "drone", "heavy", "light", "medium", "small"]]
            if len(words) > 1:
                like_clauses = " AND ".join(["lower(topic) LIKE ?" for _ in words])
                params = [f"%{w}%" for w in words]
                rows = cursor.execute(
                    f"SELECT {select_clause} FROM rules WHERE ({like_clauses}) AND {ignore_clause} ORDER BY authority_level ASC, id ASC LIMIT ?",
                    (*params, limit * 2)
                ).fetchall()
                if rows:
                    seen = {r["id"] for r in raw_results}
                    for r in rows:
                        d = dict(r)
                        if d["id"] not in seen:
                            raw_results.append(d)
                            seen.add(d["id"])

        # 3. Topic prefix / title containment match
        if len(raw_results) < limit:
            rows = cursor.execute(
                f"SELECT {select_clause} FROM rules WHERE (lower(topic) LIKE ? OR lower(topic) LIKE ? OR lower(topic) LIKE ? OR lower(topic) LIKE ?) AND {ignore_clause} ORDER BY authority_level ASC, id ASC LIMIT ?",
                (f"{norm_q}%", f"anthro - {norm_q}%", f"% {norm_q}%", f"%{norm_q}%", limit * 2)
            ).fetchall()
            if rows:
                seen = {r["id"] for r in raw_results}
                for r in rows:
                    d = dict(r)
                    if d["id"] not in seen:
                        raw_results.append(d)
                        seen.add(d["id"])

        # 4. FTS5 BM25 Weighted Search with Snippet Extraction
        if len(raw_results) < limit:
            try:
                fts_term = re.sub(r"[^\w\s]", " ", query).strip()
                if fts_term:
                    fts_words = fts_term.split()
                    # Safe FTS query with prefix wildcard
                    fts_q = " AND ".join([f'"{w}"*' for w in fts_words]) if len(fts_words) > 1 else f'"{fts_term}"*'
                    
                    fts_select = ", ".join([f"r.{c}" for c in select_cols]) if select_cols else "r.*"
                    rows = cursor.execute(
                        f"""
                        SELECT {fts_select}, 
                               bm25(rules_fts, 10.0, 5.0, 2.0, 3.0, 1.0) AS fts_score,
                               snippet(rules_fts, 4, '[bold cyan]', '[/bold cyan]', '...', 25) AS snippet
                        FROM rules r 
                        JOIN rules_fts fts ON r.id = fts.id 
                        WHERE rules_fts MATCH ? 
                        AND {ignore_clause}
                        ORDER BY r.authority_level ASC, fts_score ASC
                        LIMIT ?
                        """,
                        (fts_q, limit * 3)
                    ).fetchall()
                    if rows:
                        seen = {r["id"] for r in raw_results}
                        for r in rows:
                            d = dict(r)
                            if d["id"] not in seen:
                                raw_results.append(d)
                                seen.add(d["id"])
            except Exception:
                pass

        # 5. Fallback content/topic LIKE query
        if len(raw_results) < limit:
            fallback_term = re.sub(r"[^\w\s]", " ", query).strip()
            rows = cursor.execute(
                f"SELECT {select_clause} FROM rules WHERE (topic LIKE ? OR content LIKE ?) AND {ignore_clause} ORDER BY authority_level ASC, id ASC LIMIT ?",
                (f"%{fallback_term}%", f"%{fallback_term}%", limit)
            ).fetchall()
            seen = {r["id"] for r in raw_results}
            for r in rows:
                d = dict(r)
                if d["id"] not in seen:
                    raw_results.append(d)
                    seen.add(d["id"])

        # Consolidate editions across regional versions if requested
        if consolidate_editions:
            results = consolidate_edition_matches(raw_results)[:limit]
        else:
            results = raw_results[:limit]

        # Attach Pydantic stat blocks if present
        if attach_statblocks:
            for r in results:
                attach_rule_statblocks(r)

        return results

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
