"""
Advanced Search & Context Engine for SR6 RAG Vault.
Includes FTS5 AND/OR query parsing, stop-word filtering, authority hierarchy ordering, and enriched context formatting.
"""

import os
import re
import sqlite3
from typing import Dict, Any, List, Optional

STOP_WORDS = {
    "a", "about", "above", "after", "again", "against", "all", "am", "an", "and", "any", "are", "arent",
    "as", "at", "be", "because", "been", "before", "being", "below", "between", "both", "but", "by",
    "can", "cant", "cannot", "could", "couldnt", "did", "didnt", "do", "does", "doesnt", "doing", "dont",
    "down", "during", "each", "few", "for", "from", "further", "had", "hadnt", "has", "hasnt", "have",
    "havent", "having", "he", "hed", "hell", "hes", "her", "here", "heres", "hers", "herself", "him",
    "himself", "his", "how", "hows", "i", "id", "ill", "im", "ive", "if", "in", "into", "is", "isnt",
    "it", "its", "itself", "lets", "me", "more", "most", "mustnt", "my", "myself", "no", "nor", "not",
    "of", "off", "on", "once", "only", "or", "other", "ought", "our", "ours", "ourselves", "out", "over",
    "own", "same", "shant", "she", "shed", "shell", "shes", "should", "shouldnt", "so", "some", "such",
    "than", "that", "thats", "the", "their", "theirs", "them", "themselves", "then", "there", "theres",
    "these", "they", "theyd", "theyll", "theyre", "theyve", "this", "those", "through", "to", "too",
    "under", "until", "up", "very", "was", "wasnt", "we", "wed", "well", "were", "weve", "werent",
    "what", "whats", "when", "whens", "where", "wheres", "which", "while", "who", "whos", "whom",
    "why", "whys", "with", "wont", "would", "wouldnt", "you", "youd", "youll", "youre", "youve",
    "your", "yours", "yourself", "yourselves", "rules", "rule", "game", "shadowrun",
    "given", "current", "capabilities", "capability", "valuable", "value", "next", "take",
    "good", "best", "recommend", "recommendation", "option", "options", "choice", "choices",
    "character", "characters", "char", "runner"
}


def clean_query_terms(query_str: str) -> List[str]:
    """Extracts alphanumeric terms filtering stop words."""
    words = re.findall(r'\b\w+\b', query_str.lower())
    return [w for w in words if w not in STOP_WORDS and len(w) > 1]


def construct_fts5_query(terms: List[str], mode: str = "AND") -> str:
    """Constructs a syntax-safe FTS5 query string using prefix matching."""
    if not terms:
        return ""
    formatted_terms = [f'"{term}"*' for term in terms]
    return f" {mode} ".join(formatted_terms)


def search_rules_db(db_path: str, user_query: str, limit: int = 15) -> List[Dict[str, Any]]:
    """
    Searches the rules database using unified 5-stage hybrid search (O(1) exact, multi-word containment,
    topic prefix, BM25 weighted FTS5 with column boosts, and fallback) enriched with CommLink6 dataset stat blocks.
    """
    if not os.path.exists(db_path):
        return []

    from sr6core.rules_db import RulesDB
    db = RulesDB(db_path=db_path)
    results = db.search_rules(user_query, limit=limit, consolidate_editions=False, attach_statblocks=True)

    # Enrich rules with CommLink6 dataset stat blocks if matching
    conn = db.conn
    cursor = conn.cursor()
    for r in results:
        r_id = r.get("id", "")
        r_topic = r.get("topic", "")
        if not r.get("authority_level"):
            r["authority_level"] = 3

        dataset_match = None
        for tbl in ["ref_qualities", "ref_spells", "ref_complex_forms", "ref_gear", "ref_metatypes"]:
            try:
                row = cursor.execute(
                    f"SELECT * FROM {tbl} WHERE lower(id)=? OR lower(name)=?",
                    (r_id.lower(), r_topic.lower())
                ).fetchone()
                if row:
                    dataset_match = dict(row)
                    break
            except Exception:
                pass
        r["commlink_data"] = dataset_match

    return results


def deduplicate_and_resolve_conflicts(rules: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Consolidates duplicate topic entries across regional editions (Hong Kong, Seattle, Berlin)
    and supplements, prioritizing higher authority levels and canonical Hong Kong Core Rulebook.
    """
    from sr6core.rules_db import consolidate_edition_matches
    return consolidate_edition_matches(rules)


def format_authority_label(level: int) -> str:
    labels = {
        1: "Level 1 (Highest Authority - Shadowrun Missions Guide / Core Errata)",
        2: "Level 2 (High Authority - Supplemental Sourcebooks)",
        3: "Level 3 (Medium Authority - Core Rulebook)",
        4: "Level 4 (Lowest Authority - FAQs, GM Primers, Conversion Guides)"
    }
    return labels.get(level, f"Level {level}")


def format_context_for_llm(rules: List[Dict[str, Any]], max_chars: int = 12000) -> str:
    if not rules:
        return "No relevant rules retrieved from the vault."

    context_blocks = []
    total_len = 0

    for r in rules:
        dataset_str = ""
        cdata = r.get("commlink_data")
        if cdata:
            stats = []
            for k, v in cdata.items():
                if k not in ["raw_xml"] and v is not None:
                    stats.append(f"{k}: {v}")
            dataset_str = f"COMMLINK6 STAT BLOCK: {', '.join(stats)}\n"

        cross_refs_str = ""
        if r.get("cross_references"):
            cross_refs_str = f"CROSS REFERENCES: {', '.join(r['cross_references'])}\n"

        content_body = r.get("content", "")
        # Remove yaml frontmatter if present
        if content_body.startswith("---"):
            parts = content_body.split("---", 2)
            if len(parts) >= 3:
                content_body = parts[2].strip()

        block = (
            f"---\n"
            f"RULE ID: {r['id']}\n"
            f"SOURCE: {r.get('source', 'SR6')} (Page: {r.get('page', 'N/A')})\n"
            f"CHAPTER: {r.get('chapter', 'General')}\n"
            f"TOPIC: {r.get('topic', 'Rules Topic')}\n"
            f"AUTHORITY: {format_authority_label(r.get('authority_level', 3))}\n"
            f"{cross_refs_str}"
            f"{dataset_str}"
            f"CONTENT:\n"
            f"{content_body}\n"
            f"---"
        )

        if total_len + len(block) > max_chars and context_blocks:
            break

        context_blocks.append(block)
        total_len += len(block)

    return "\n\n".join(context_blocks)
