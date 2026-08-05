"""
SR6 RAG Subsystem Package.
Exposes RAGEngine, search_rules_db, and query_gemini.
"""

from sr6core.rag.search import search_rules_db, format_context_for_llm, deduplicate_and_resolve_conflicts
from sr6core.rag.llm import query_gemini, SYSTEM_INSTRUCTION
from sr6core.rag.engine import RAGEngine

__all__ = [
    "RAGEngine",
    "search_rules_db",
    "format_context_for_llm",
    "deduplicate_and_resolve_conflicts",
    "query_gemini",
    "SYSTEM_INSTRUCTION"
]
