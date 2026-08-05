"""
Unified RAGEngine coordinator for SR6 rules search and AI assistance.
"""

import os
from typing import Dict, Any, List, Optional

from sr6core.rules_db import DEFAULT_DB_PATH
from sr6core.rag.search import search_rules_db, deduplicate_and_resolve_conflicts, format_context_for_llm
from sr6core.rag.llm import query_gemini, RAGChatSession


class RAGEngine:
    def __init__(self, db_path: Optional[str] = None, model_name: str = "flash-latest", effort_level: Optional[str] = "medium"):
        if db_path and os.path.exists(db_path):
            self.db_path = db_path
        elif os.path.exists(DEFAULT_DB_PATH):
            self.db_path = DEFAULT_DB_PATH
        elif os.path.exists(LOCAL_CORE_DB_PATH):
            self.db_path = LOCAL_CORE_DB_PATH
        else:
            self.db_path = DEFAULT_DB_PATH
        self.session = RAGChatSession(model_name=model_name, effort_level=effort_level)

    def search(self, query: str, limit: int = 15) -> List[Dict[str, Any]]:
        raw = search_rules_db(self.db_path, query, limit=limit)
        return deduplicate_and_resolve_conflicts(raw)

    def query(
        self,
        user_query: str,
        limit: int = 10,
        use_ai: bool = True,
        model_name: Optional[str] = None,
        effort_level: Optional[str] = None,
        use_session: bool = False
    ) -> Dict[str, Any]:
        rules = self.search(user_query, limit=limit)
        context_str = format_context_for_llm(rules)

        ai_response = None
        error = None

        if model_name:
            self.session.set_model(model_name)
        if effort_level is not None:
            self.session.set_effort(effort_level)

        if use_ai:
            if use_session:
                ai_response, error = self.session.send_query(user_query, context_str)
            else:
                target_model = model_name or self.session.model_name
                target_effort = effort_level if effort_level is not None else self.session.effort_level
                ai_response, error = query_gemini(
                    user_query,
                    context_str,
                    model_name=target_model,
                    effort_level=target_effort
                )

        return {
            "query": user_query,
            "rules": rules,
            "context": context_str,
            "ai_response": ai_response,
            "error": error,
            "model_name": self.session.model_name,
            "effort_level": self.session.effort_level
        }

