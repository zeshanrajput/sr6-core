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

    return str(local_repo_converted)


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
        from sr6core.migrations.runner import run_migrations
        run_migrations(self.conn)

        # Ensure sub_items are populated if needed
        try:
            self.populate_sub_items()
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

    def get_rule_by_topic_or_id(self, identifier: str) -> Optional[Dict[str, Any]]:
        """Fast lookup of a rule by exact ID, topic name, or best prefix match."""
        if not identifier or not identifier.strip():
            return None
        clean_id = identifier.strip()
        # 1. Exact ID
        res = self.query_rule(clean_id)
        if res:
            return attach_rule_statblocks(res)

        # 2. Exact Topic
        cursor = self.conn.cursor()
        row = cursor.execute(
            "SELECT * FROM rules WHERE lower(topic) = ? OR lower(topic) = ?",
            (clean_id.lower(), clean_id.lower().replace("-", " "))
        ).fetchone()
        if row:
            return attach_rule_statblocks(dict(row))

        # 3. Best search match
        matches = self.search_rules(clean_id, limit=1)
        if matches:
            return matches[0]
        return None

    def search_rules(
        self,
        query: str,
        limit: int = 10,
        category: Optional[str] = None,
        consolidate_editions: bool = True,
        attach_statblocks: bool = True,
        enable_semantic: bool = False
    ) -> List[Dict[str, Any]]:
        """
        Unified 6-stage hybrid search across rules vault:
        1. Exact topic / name match (O(1))
        2. Multi-word topic containment (all words in topic)
        3. Topic prefix / title containment
        4. FTS5 BM25 weighted search with stop-word cleaning (AND + OR fallback)
        5. Fallback LIKE search
        6. Local semantic vector search (sqlite-vec / embeddings) with Reciprocal Rank Fusion
        Followed by canonical edition deduplication and Pydantic stat block attachment.
        """
        if not query or not query.strip():
            return []

        from sr6core.rag.search import clean_query_terms

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
        ignore_clause_fts = """
            lower(r.topic) NOT LIKE '%content%' 
            AND lower(r.topic) NOT LIKE 'index%' 
            AND lower(r.topic) NOT LIKE '%game concepts%'
            AND lower(r.topic) NOT LIKE '%credits%'
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

        # 4. FTS5 BM25 Weighted Search with Stop-Word Cleaning & Fallback OR Ranking
        if len(raw_results) < limit:
            try:
                clean_terms = clean_query_terms(query)
                if clean_terms:
                    fts_select = ", ".join([f"r.{c}" for c in select_cols]) if select_cols else "r.*"
                    seen = {r["id"] for r in raw_results}

                    # 4a. Strict AND search on clean terms
                    fts_and_q = " AND ".join([f'"{w}"*' for w in clean_terms])
                    rows = cursor.execute(
                        f"""
                        SELECT {fts_select}, 
                               bm25(rules_fts, 10.0, 5.0, 2.0, 3.0, 1.0) AS fts_score,
                               snippet(rules_fts, 4, '[bold cyan]', '[/bold cyan]', '...', 25) AS snippet
                        FROM rules r 
                        JOIN rules_fts fts ON r.id = fts.id 
                        WHERE rules_fts MATCH ? 
                        AND {ignore_clause_fts}
                        ORDER BY r.authority_level ASC, fts_score ASC
                        LIMIT ?
                        """,
                        (fts_and_q, limit * 3)
                    ).fetchall()
                    if rows:
                        for r in rows:
                            d = dict(r)
                            if d["id"] not in seen:
                                raw_results.append(d)
                                seen.add(d["id"])

                    # 4b. If still under limit, run OR search on clean terms with BM25 ranking
                    if len(raw_results) < limit and len(clean_terms) > 1:
                        fts_or_q = " OR ".join([f'"{w}"*' for w in clean_terms])
                        rows = cursor.execute(
                            f"""
                            SELECT {fts_select}, 
                                   bm25(rules_fts, 10.0, 5.0, 2.0, 3.0, 1.0) AS fts_score,
                                   snippet(rules_fts, 4, '[bold cyan]', '[/bold cyan]', '...', 25) AS snippet
                            FROM rules r 
                            JOIN rules_fts fts ON r.id = fts.id 
                            WHERE rules_fts MATCH ? 
                            AND {ignore_clause_fts}
                            ORDER BY r.authority_level ASC, fts_score ASC
                            LIMIT ?
                            """,
                            (fts_or_q, limit * 3)
                        ).fetchall()
                        if rows:
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

        # 6. Local Semantic Vector Search (sqlite-vec / embeddings) with RRF
        is_conceptual = any(q_word in norm_q for q_word in [
            "how do", "how to", "how can", "heal", "penalty", "difference", "why", "reduce", "when can", "recoil"
        ])
        if enable_semantic or (is_conceptual and len(raw_results) < limit):
            try:
                from sr6core.rag.embeddings import VectorVault
                vec_hits = VectorVault.search_vector(self.conn, query, limit=limit)
                if vec_hits:
                    vec_rules = []
                    for v in vec_hits:
                        v_rule = self.query_rule(v["id"])
                        if v_rule:
                            v_rule["semantic_score"] = v.get("score", 0.0)
                            vec_rules.append(v_rule)
                    raw_results = VectorVault.reciprocal_rank_fusion(raw_results, vec_rules, limit=limit * 2)
            except Exception:
                pass

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
            ("ref_adept_powers", "adept_power"),
            ("ref_weapons", "weapon"),
            ("ref_vehicles", "vehicle"),
            ("ref_cyberware", "cyberware"),
            ("ref_programs", "program"),
            ("ref_gear", "gear"),
            ("ref_metatypes", "metatype")
        ]

        # Generate normalized candidate identifiers
        candidate_identifiers = [
            clean_target,
            norm_target,
            clean_target.lower(),
            clean_target.lower().replace("-", " "),
            clean_target.lower().replace("-", "_")
        ]
        
        # Also try stripping common manufacturer / brand prefixes (Ares, Shiawase, Renraku, MCT, Federated-Boeing)
        unbranded = re.sub(r'^(?:ares|shiawase|renraku|mct|federated-boeing|erika)\s+', '', clean_target, flags=re.IGNORECASE).strip()
        if unbranded and unbranded.lower() != clean_target.lower():
            candidate_identifiers.extend([
                unbranded,
                unbranded.lower().replace(" ", "_"),
                unbranded.lower().replace("-", " "),
                unbranded.lower().replace("-", "_"),
                unbranded.lower()
            ])

        # 1. Exact match pass (highest precision)
        for tbl, t_label in tables:
            try:
                for cand in candidate_identifiers:
                    row = cursor.execute(
                        f"SELECT * FROM {tbl} WHERE id = ? OR lower(id) = ? OR lower(name) = ?",
                        (cand, cand.lower(), cand.lower())
                    ).fetchone()
                    if row:
                        dataset_info = dict(row)
                        item_type = t_label
                        break
                if dataset_info:
                    break
            except Exception:
                pass

        # 2. Pattern match pass (if no exact match found)
        if not dataset_info:
            for tbl, t_label in tables:
                try:
                    for cand in candidate_identifiers:
                        row = cursor.execute(
                            f"SELECT * FROM {tbl} WHERE lower(id) LIKE ? OR lower(name) LIKE ?",
                            (f"%{cand.lower()}%", f"%{cand.lower()}%")
                        ).fetchone()
                        if row:
                            dataset_info = dict(row)
                            item_type = t_label
                            break
                    if dataset_info:
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

    def get_cyberware_with_grades(self, identifier: str) -> Optional[Dict[str, Any]]:
        """
        Retrieves cyberware record with calculated grades (Standard, Alpha, Beta, Delta, Used)
        from v_cyberware_grades.
        """
        if not identifier or not identifier.strip():
            return None
        clean_id = identifier.strip()
        norm_id = clean_id.lower().replace(" ", "_")
        cursor = self.conn.cursor()
        try:
            row = cursor.execute(
                "SELECT * FROM v_cyberware_grades WHERE id = ? OR lower(id) = ? OR lower(name) = ? OR lower(name) = ?",
                (clean_id, norm_id, clean_id.lower(), norm_id.replace("_", " "))
            ).fetchone()
            if row:
                d = dict(row)
                if d.get("modifiers_json"):
                    import json
                    try:
                        d["modifiers"] = json.loads(d["modifiers_json"])
                    except Exception:
                        d["modifiers"] = []
                d["grades"] = {
                    "standard": {
                        "essence": d.get("standard_essence"),
                        "cost": d.get("standard_cost"),
                        "avail_mod": d.get("standard_avail_mod", 0)
                    },
                    "used": {
                        "essence": d.get("used_essence"),
                        "cost": d.get("used_cost"),
                        "avail_mod": d.get("used_avail_mod", -1)
                    },
                    "omegaware": {
                        "essence": d.get("used_essence"),
                        "cost": d.get("used_cost"),
                        "avail_mod": d.get("used_avail_mod", -1)
                    },
                    "alphaware": {
                        "essence": d.get("alpha_essence"),
                        "cost": d.get("alpha_cost"),
                        "avail_mod": d.get("alpha_avail_mod", 1)
                    },
                    "betaware": {
                        "essence": d.get("beta_essence"),
                        "cost": d.get("beta_cost"),
                        "avail_mod": d.get("beta_avail_mod", 2)
                    },
                    "deltaware": {
                        "essence": d.get("delta_essence"),
                        "cost": d.get("delta_cost"),
                        "avail_mod": d.get("delta_avail_mod", 3)
                    },
                    "exoware": {
                        "essence": d.get("exoware_essence"),
                        "cost": d.get("exoware_cost"),
                        "avail_mod": d.get("exoware_avail_mod", 0)
                    },
                }
                return d
        except Exception:
            pass
        return None

    def get_weapon_mounts_and_accessories(self, identifier: str) -> Optional[Dict[str, Any]]:
        """
        Retrieves weapon slots, available mounts (TOP, BARREL, UNDER, INTERNAL),
        accessory requirements, and embedded accessories.
        """
        if not identifier or not identifier.strip():
            return None
        clean_id = identifier.strip()
        norm_id = clean_id.lower().replace(" ", "_")
        cursor = self.conn.cursor()
        try:
            row = cursor.execute(
                """SELECT id, name, category, damage, ap, attack_rating, modes, ammo, cost, avail,
                          mounts, mount_top, mount_barrel, mount_under, mount_internal,
                          requirements_json, embedded_accessories_json, modifiers_json
                   FROM ref_weapons
                   WHERE id = ? OR lower(id) = ? OR lower(name) = ? OR lower(name) = ?""",
                (clean_id, norm_id, clean_id.lower(), norm_id.replace("_", " "))
            ).fetchone()
            if row:
                d = dict(row)
                import json
                for k in ["requirements_json", "embedded_accessories_json", "modifiers_json"]:
                    if d.get(k):
                        try:
                            d[k.replace("_json", "")] = json.loads(d[k])
                        except Exception:
                            d[k.replace("_json", "")] = []
                    else:
                        d[k.replace("_json", "")] = []
                d["mount_list"] = [m.strip() for m in (d.get("mounts") or "").split(",") if m.strip()]
                d["raw_mounts"] = d.get("mounts", "")
                d["mounts"] = d["mount_list"]
                return d
        except Exception:
            pass
        return None

    def get_item_structured_modifiers(self, table: str, identifier: str, rating: int = 1) -> List[Dict[str, Any]]:
        """
        Retrieves passive mechanical deltas from modifiers_json for a given item,
        evaluating $RATING formulas against the provided rating.
        """
        if not identifier or not identifier.strip() or table not in [
            "ref_cyberware", "ref_qualities", "ref_spells", "ref_adept_powers", "ref_weapons"
        ]:
            return []

        clean_id = identifier.strip()
        norm_id = clean_id.lower().replace(" ", "_")
        cursor = self.conn.cursor()
        try:
            row = cursor.execute(
                f"SELECT id, name, modifiers_json FROM {table} WHERE id = ? OR lower(id) = ? OR lower(name) = ? OR lower(name) = ?",
                (clean_id, norm_id, clean_id.lower(), norm_id.replace("_", " "))
            ).fetchone()
            if not row or not row["modifiers_json"]:
                return []

            import json
            raw_mods = json.loads(row["modifiers_json"])
            evaluated = []
            for m in raw_mods:
                mod_copy = dict(m)
                val_formula = str(mod_copy.get("raw_value", ""))
                if "$RATING" in val_formula:
                    expr = val_formula.replace("$RATING", str(rating)).replace("*", " * ")
                    try:
                        mod_copy["value"] = int(float(eval(expr, {"__builtins__": None}, {})))
                    except Exception:
                        mod_copy["value"] = rating
                elif mod_copy.get("is_rating_multiplier"):
                    mod_copy["value"] = int(mod_copy.get("value", 1)) * rating
                evaluated.append(mod_copy)
            return evaluated
        except Exception:
            return []

    def populate_sub_items(self, force: bool = False) -> int:
        """
        Parses granular sub-items (Submersion Echoes, Metamagics, Matrix Actions,
        Combat Actions, and Special Powers) out of monolithic rules chunks and indexes them
        into sub_items for instant O(1) queryable retrieval.
        """
        cursor = self.conn.cursor()
        if not force:
            try:
                count = cursor.execute("SELECT COUNT(*) FROM sub_items").fetchone()[0]
                if count > 30:
                    return count
            except Exception:
                pass

        CANONICAL_SUBITEMS = [
            # Submersion Echoes
            ("echo_skinlink", "Skinlink", "echoes", "You can connect to a device as if using a direct neural interface (DNI) simply by touching it with bare skin. Eliminates the need for data cables or wireless broadcast."),
            ("echo_living_network", "Living Network", "echoes", "Your living persona can participate in and form a Personal Area Network (PAN) as the master device, slaving physical gear, weapons, and commlinks directly to your Resonance persona."),
            ("echo_machine_mind", "Machine Mind", "echoes", "You gain the subconscious neural interfaces of a Rating 1 Control Rig. When jumped into a drone or vehicle, gain control rig threshold reductions and dice pool bonuses."),
            ("echo_matrix_upgrade", "Matrix Attribute Upgrade", "echoes", "Permanently increase one of your living persona's Matrix Attributes (Attack, Sleaze, Data Processing, or Firewall) by 1. Can be taken twice per attribute."),
            ("echo_neurofilter", "NeuroFilter", "echoes", "Adds a +1 dice pool bonus to resist biofeedback damage from black IC and Matrix attacks. May be taken up to twice for +2 resistance."),
            ("echo_overclocking", "Overclocking", "echoes", "You accelerate your living persona to act at blinding speeds in the Matrix. Gain +1 additional Minor Action and +1D6 Initiative Dice while in hot-sim VR."),
            ("echo_resonance_link", "Resonance Link", "echoes", "Establish an empathic one-way sensory link with another technomancer. You instantly discern their emotional state, trauma, physical danger, and Matrix alarms."),
            ("echo_aura_link", "Aura Link", "echoes", "Requires Skinlink. You can wirelessly link to devices as if touching them, reading digital signatures across the astral-digital threshold."),
            ("echo_mind_over_machine", "Mind Over Machine", "echoes", "Treat your living persona as an installed Rigger Command Console (RCC), allowing you to share autosofts and command multiple slaved drones simultaneously."),
            ("echo_buffer", "Buffer", "echoes", "Creates a protective Resonance cushion that absorbs up to 2 boxes of Matrix or biofeedback damage per encounter before hitting your persona condition monitor."),
            ("echo_data_haven", "Data Haven", "echoes", "Allows you to store encrypted files, stolen paydata, and node images directly inside your living persona's Resonance matrix memory with complete immunity to external trace actions."),
            ("echo_deconstruct", "Deconstruct", "echoes", "Adds +2 DV to Matrix damage inflicted against IC programs and constructs inside host environments."),

            # Metamagics
            ("meta_centering", "Centering", "metamagic", "Use vocal chants, mantras, or physical gestures to reduce negative situational dice pool modifiers and sustaining penalties by your initiate grade."),
            ("meta_adept_centering", "Adept Centering", "metamagic", "Physical adepts channel ki flow to reduce physical penalties to combat tests by their initiate grade."),
            ("meta_cleansing", "Cleansing", "metamagic", "Scrub background counts, astral signatures, and magical pollution from a physical area through ritual cleansing."),
            ("meta_fixation", "Fixation", "metamagic", "Allows an initiate to make a quickened spell permanent without continuous Karma sustaining drain."),
            ("meta_masking", "Masking", "metamagic", "Alter the appearance of your astral aura to appear mundane, conceal your Magic rating, or disguise your initiate grade against assensing."),
            ("meta_extended_masking", "Extended Masking", "metamagic", "Requires Masking. Extend your masking aura to disguise bonded foci, sustained spells, and allied spirits."),
            ("meta_quickening", "Quickening", "metamagic", "Sustain a spell indefinitely by bonding Karma into the spell matrix, freeing your concentration from sustaining penalties."),
            ("meta_shielding", "Shielding", "metamagic", "Channel astral barrier energy into your spell defense pool, increasing counterspelling dice by your initiate grade."),
            ("meta_absorption", "Absorption", "metamagic", "Requires Shielding. Absorb intercepted spell energy to replenish your physical stamina or reduce active drain."),
            ("meta_flexible_signature", "Flexible Signature", "metamagic", "Alter the astral signature left by your spellcasting to mimic another tradition or accelerate signature decay."),
            ("meta_power_point", "Power Point", "metamagic", "Gain 1 additional Power Point for adept powers upon initiation instead of a standard metamagic technique.")
        ]

        inserted = 0
        for iid, name, ns, content in CANONICAL_SUBITEMS:
            cursor.execute(
                "INSERT OR REPLACE INTO sub_items (id, name, namespace, content) VALUES (?, ?, ?, ?)",
                (iid, name, ns, content)
            )
            inserted += 1

        # Also dynamically parse matching bullet items from monolithic rules chunks
        try:
            target_rules = cursor.execute("""
                SELECT id, topic, content FROM rules 
                WHERE topic LIKE '%echo%' OR topic LIKE '%metamagic%' OR topic LIKE '%matrix action%' 
                   OR topic LIKE '%minor action%' OR topic LIKE '%major action%'
            """).fetchall()

            import re
            for r in target_rules:
                rule_id, topic, content = r[0], r[1], r[2]
                if content.startswith("---"):
                    parts = content.split("---", 2)
                    if len(parts) >= 3:
                        content = parts[2].strip()

                top_low = topic.lower()
                if "echo" in top_low:
                    ns = "echoes"
                elif "metamagic" in top_low:
                    ns = "metamagic"
                elif "matrix" in top_low:
                    ns = "matrix_actions"
                else:
                    ns = "combat_actions"

                pattern = r"(?:^|\n)(?:[-*]\s*)?(?:\*\*([^*:\n]+)\*\*|([A-Z][A-Za-z0-9\s/–—\-]{2,35}))\s*:\s*(.*?)(?=\n(?:[-*]\s*)?(?:\*\*[^*:\n]+\*\*|[A-Z][A-Za-z0-9\s/–—\-]{2,35}\s*:)|$)"
                for m in re.finditer(pattern, content, re.DOTALL):
                    name = (m.group(1) or m.group(2) or "").strip()
                    desc = m.group(3).strip()
                    if len(name) >= 3 and len(desc) >= 20 and not name.lower().startswith("note") and not name.lower().startswith("example"):
                        clean_id = f"{rule_id}_{name.lower().replace(' ', '_')}"
                        cursor.execute(
                            "INSERT OR IGNORE INTO sub_items (id, name, namespace, content) VALUES (?, ?, ?, ?)",
                            (clean_id, name, ns, desc)
                        )
                        inserted += 1
        except Exception:
            pass

        self.conn.commit()
        return inserted

    def get_sub_item(self, name_or_id: str, namespace: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """Retrieves a granular sub-item (echo, metamagic, action, quality) from sub_items."""
        if not name_or_id or not name_or_id.strip():
            return None
        clean_target = name_or_id.strip().lower()
        norm_target = clean_target.replace(" ", "_").replace("-", "_")
        cursor = self.conn.cursor()
        if namespace:
            query = """
                SELECT id, name, namespace, content
                FROM sub_items
                WHERE namespace = ? AND (lower(id) = ? OR lower(name) = ? OR lower(id) = ? OR lower(name) = ?)
            """
            row = cursor.execute(query, (namespace, clean_target, clean_target, norm_target, norm_target.replace("_", " "))).fetchone()
        else:
            query = """
                SELECT id, name, namespace, content
                FROM sub_items
                WHERE lower(id) = ? OR lower(name) = ? OR lower(id) = ? OR lower(name) = ?
            """
            row = cursor.execute(query, (clean_target, clean_target, norm_target, norm_target.replace("_", " "))).fetchone()

        if row:
            return dict(row)
        return None

    def get_action(self, identifier: str) -> Optional[Dict[str, Any]]:
        """Retrieves action details from ref_actions by ID or name."""
        if not identifier or not identifier.strip():
            return None
        clean = identifier.strip().lower()
        norm = clean.replace(" ", "_").replace("-", "_")
        cursor = self.conn.cursor()
        row = cursor.execute(
            "SELECT * FROM ref_actions WHERE id = ? OR lower(name) = ? OR lower(id) = ? OR lower(name) = ?",
            (clean, clean, norm, norm.replace("_", " "))
        ).fetchone()
        return dict(row) if row else None

    def get_status_effect(self, identifier: str) -> Optional[Dict[str, Any]]:
        """Retrieves status effect condition details from ref_status_effects."""
        if not identifier or not identifier.strip():
            return None
        clean = identifier.strip().lower()
        norm = clean.replace(" ", "_").replace("-", "_")
        cursor = self.conn.cursor()
        row = cursor.execute(
            "SELECT * FROM ref_status_effects WHERE id = ? OR lower(name) = ? OR lower(id) = ? OR lower(name) = ?",
            (clean, clean, norm, norm.replace("_", " "))
        ).fetchone()
        return dict(row) if row else None

    def get_edge_boost(self, identifier: str) -> Optional[Dict[str, Any]]:
        """Retrieves Edge boost mechanics from ref_edge_boosts."""
        if not identifier or not identifier.strip():
            return None
        clean = identifier.strip().lower()
        norm = clean.replace(" ", "_").replace("-", "_")
        cursor = self.conn.cursor()
        row = cursor.execute(
            "SELECT * FROM ref_edge_boosts WHERE id = ? OR lower(name) = ? OR lower(id) = ? OR lower(name) = ?",
            (clean, clean, norm, norm.replace("_", " "))
        ).fetchone()
        return dict(row) if row else None

    def get_srm_ruling(self, identifier: str) -> Optional[Dict[str, Any]]:
        """Retrieves official SRM FAQ ruling or campaign exception from srm_rulings."""
        if not identifier or not identifier.strip():
            return None
        clean = identifier.strip().lower()
        norm = clean.replace(" ", "_").replace("-", "_")
        cursor = self.conn.cursor()
        row = cursor.execute(
            """SELECT * FROM srm_rulings 
               WHERE id = ? OR lower(topic) = ? OR rule_or_item_id = ? OR lower(id) = ?
                  OR lower(topic) LIKE ? OR lower(ruling) LIKE ?""",
            (clean, clean, norm, norm, f"%{clean}%", f"%{clean}%")
        ).fetchone()
        return dict(row) if row else None


def execute_db_query(
    sql: str, db_path: Optional[str] = None
) -> Tuple[List[str], List[Tuple[Any, ...]]]:
    """
    Executes a read-only SQL query against the rules database (~/.sr6/rules_index.db).
    Returns (columns, rows).
    """
    path = db_path or DEFAULT_DB_PATH
    if not os.path.exists(path):
        raise FileNotFoundError(f"Database not found at '{path}'")

    trimmed = sql.strip().rstrip(";")
    if not trimmed:
        return [], []

    first_word = trimmed.split()[0].upper() if trimmed.split() else ""
    if first_word not in ("SELECT", "PRAGMA", "EXPLAIN", "WITH"):
        raise ValueError(
            f"Only read-only queries (SELECT, PRAGMA, WITH, EXPLAIN) are permitted. Found: '{first_word}'"
        )

    upper_sql = trimmed.upper()
    destructive = ["DROP ", "DELETE ", "INSERT ", "UPDATE ", "ALTER ", "ATTACH ", "DETACH ", "REPLACE ", "TRUNCATE "]
    for d in destructive:
        if d in upper_sql:
            raise ValueError(f"Destructive SQL operations are prohibited ({d.strip()}).")

    conn = sqlite3.connect(path)
    try:
        conn.execute("PRAGMA query_only = ON;")
        cursor = conn.cursor()
        cursor.execute(trimmed)
        columns = [desc[0] for desc in cursor.description] if cursor.description else []
        rows = cursor.fetchall()
        return columns, rows
    finally:
        conn.close()


def get_db_schema(
    table_name: Optional[str] = None, db_path: Optional[str] = None
) -> Dict[str, Any]:
    """
    Returns schema info for a specific table, or a list of all tables with row counts if table_name is None.
    """
    path = db_path or DEFAULT_DB_PATH
    if not os.path.exists(path):
        raise FileNotFoundError(f"Database not found at '{path}'")

    conn = sqlite3.connect(path)
    try:
        cursor = conn.cursor()
        if table_name:
            table_row = cursor.execute(
                "SELECT name FROM sqlite_master WHERE type IN ('table', 'view') AND lower(name) = ?",
                (table_name.lower().strip(),)
            ).fetchone()
            if not table_row:
                raise ValueError(f"Table or view '{table_name}' does not exist in the database.")
            actual_name = table_row[0]
            cols = cursor.execute(f"PRAGMA table_info('{actual_name}')").fetchall()
            row_count = cursor.execute(f"SELECT count(*) FROM '{actual_name}'").fetchone()[0]
            sample_row = cursor.execute(f"SELECT * FROM '{actual_name}' LIMIT 1").fetchone()
            sample_dict = dict(zip([c[1] for c in cols], sample_row)) if sample_row else {}
            return {
                "table": actual_name,
                "row_count": row_count,
                "columns": [
                    {
                        "cid": c[0],
                        "name": c[1],
                        "type": c[2],
                        "notnull": bool(c[3]),
                        "dflt_value": c[4],
                        "pk": bool(c[5])
                    }
                    for c in cols
                ],
                "sample": sample_dict
            }
        else:
            tables = cursor.execute(
                """SELECT name FROM sqlite_master 
                   WHERE type IN ('table', 'view') 
                     AND name NOT LIKE 'sqlite_%' 
                     AND name NOT LIKE 'vec_%' 
                     AND name NOT LIKE '%_data' 
                     AND name NOT LIKE '%_idx' 
                     AND name NOT LIKE '%_content' 
                     AND name NOT LIKE '%_docsize' 
                     AND name NOT LIKE '%_config' 
                   ORDER BY name"""
            ).fetchall()
            table_list = []
            for (tname,) in tables:
                try:
                    cnt = cursor.execute(f"SELECT count(*) FROM '{tname}'").fetchone()[0]
                except Exception:
                    cnt = 0
                cols = cursor.execute(f"PRAGMA table_info('{tname}')").fetchall()
                col_names = [c[1] for c in cols]
                table_list.append({
                    "name": tname,
                    "row_count": cnt,
                    "column_count": len(cols),
                    "columns": col_names
                })
            return {"tables": table_list}
    finally:
        conn.close()


def format_query_results(
    columns: List[str], rows: List[Tuple[Any, ...]], fmt: str = "table"
) -> str:
    """
    Formats SQL query results as a table, clean markdown, json, or csv.
    """
    if fmt == "json":
        import json
        records = [dict(zip(columns, row)) for row in rows]
        return json.dumps(records, indent=2, default=str)

    if fmt == "csv":
        import io
        import csv
        buf = io.StringIO()
        writer = csv.writer(buf)
        writer.writerow(columns)
        writer.writerows(rows)
        return buf.getvalue().rstrip()

    if not columns:
        return "(0 results / No columns returned)"

    # Markdown format (used for --compact or when plain text table is needed)
    if fmt in ("markdown", "compact"):
        lines = []
        lines.append("| " + " | ".join(columns) + " |")
        lines.append("| " + " | ".join(["---"] * len(columns)) + " |")
        for row in rows:
            clean_cells = [str(val).replace("\n", " ").replace("|", "\\|") if val is not None else "" for val in row]
            lines.append("| " + " | ".join(clean_cells) + " |")
        lines.append(f"\n*({len(rows)} rows returned)*")
        return "\n".join(lines)

    # Rich table format
    try:
        from rich.table import Table
        from rich.console import Console
        import io

        table = Table(show_header=True, header_style="bold cyan", border_style="dim")
        for col in columns:
            table.add_column(str(col))
        for row in rows:
            table.add_row(*[str(val) if val is not None else "" for val in row])
        console = Console(file=io.StringIO(), color_system=None, width=120)
        console.print(table)
        console.print(f"({len(rows)} rows returned)")
        return console.file.getvalue().rstrip()
    except Exception:
        return format_query_results(columns, rows, fmt="markdown")


def format_db_schema(schema_info: Dict[str, Any], fmt: str = "table") -> str:
    """
    Formats schema info for display.
    """
    if "tables" in schema_info:
        cols = ["Table Name", "Row Count", "Columns", "Sample Columns"]
        rows = []
        for t in schema_info["tables"]:
            rows.append((
                t["name"],
                f"{t['row_count']:,}",
                t["column_count"],
                ", ".join(t["columns"][:6]) + ("..." if len(t["columns"]) > 6 else "")
            ))
        header = "=== SQLite Rules Database Tables (~/.sr6/rules_index.db) ===\n\n"
        return header + format_query_results(cols, rows, fmt=fmt)
    else:
        tname = schema_info["table"]
        cnt = schema_info["row_count"]
        cols = ["CID", "Column Name", "Type", "Not Null", "PK", "Default"]
        rows = []
        for c in schema_info["columns"]:
            rows.append((
                c["cid"],
                c["name"],
                c["type"],
                "YES" if c["notnull"] else "NO",
                "PRIMARY KEY" if c["pk"] else "",
                str(c["dflt_value"]) if c["dflt_value"] is not None else ""
            ))
        table_rendered = format_query_results(cols, rows, fmt=fmt)
        out = [f"=== Schema for Table: {tname} ({cnt:,} rows) ===\n", table_rendered]
        if schema_info.get("sample"):
            import json
            out.append("\n**Sample Row:**")
            out.append("```json\n" + json.dumps(schema_info["sample"], indent=2, default=str) + "\n```")
        return "\n".join(out)



