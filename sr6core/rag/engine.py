"""
Unified RAGEngine coordinator for SR6 rules search and AI assistance.
Supports provider switching (Gemini / llama.cpp Gemma) and character-specific dossier context binding.
"""

import os
from typing import Dict, Any, List, Optional

from sr6core.rules_db import DEFAULT_DB_PATH
from sr6core.rag.search import search_rules_db, deduplicate_and_resolve_conflicts, format_context_for_llm
from sr6core.rag.llm import query_gemini, RAGChatSession, DEFAULT_LLAMA_URL
from sr6core.character_manager import CharacterManager


class RAGEngine:
    def __init__(
        self,
        db_path: Optional[str] = None,
        model_name: str = "flash-latest",
        effort_level: Optional[str] = "medium",
        provider_name: str = "gemini",
        llama_url: str = DEFAULT_LLAMA_URL
    ):
        if db_path and os.path.exists(db_path):
            self.db_path = db_path
        elif os.path.exists(DEFAULT_DB_PATH):
            self.db_path = DEFAULT_DB_PATH
        else:
            self.db_path = DEFAULT_DB_PATH

        self.session = RAGChatSession(
            model_name=model_name,
            effort_level=effort_level,
            provider_name=provider_name,
            llama_url=llama_url
        )

    def _build_char_context(self, char_id: str) -> str:
        try:
            cm = CharacterManager()
            char = cm.load_character(char_id)
            if not char or "data" not in char:
                return ""
            data = char["data"]
            identity = data.get("identity", {})
            name = identity.get("handle", data.get("name", char_id.title()))
            archetype = data.get("archetype", identity.get("role", "Shadowrunner"))
            metatype = identity.get("metatype", data.get("metatype", "Human"))
            stream = identity.get("stream") or identity.get("tradition")

            attrs = data.get("attributes", {})
            skills_raw = data.get("skills", [])
            if isinstance(skills_raw, list):
                skills = [s.get("name", s.get("id", str(s))) for s in skills_raw if isinstance(s, dict)]
            elif isinstance(skills_raw, dict):
                skills = list(skills_raw.keys())
            else:
                skills = []

            # Qualities
            pos_q = data.get("qualities", {}).get("positive", []) if isinstance(data.get("qualities"), dict) else data.get("qualities", [])
            neg_q = data.get("qualities", {}).get("negative", []) if isinstance(data.get("qualities"), dict) else []
            qualities = []
            for q in pos_q + neg_q:
                qualities.append(q.get("name", q.get("id", str(q))) if isinstance(q, dict) else str(q))

            # Echoes / Metamagics
            echoes_raw = data.get("meta_echoes", []) or data.get("echoes", []) or data.get("metamagics", [])
            echoes = [e.get("name", e.get("id", str(e))) if isinstance(e, dict) else str(e) for e in echoes_raw]

            # Complex Forms / Spells
            cf_raw = data.get("complex_forms", [])
            complex_forms = [cf.get("name", cf.get("id", str(cf))) if isinstance(cf, dict) else str(cf) for cf in cf_raw]

            spells_raw = data.get("spells", [])
            spells = [s.get("name", s.get("id", str(s))) if isinstance(s, dict) else str(s) for s in spells_raw]

            # Cyberware / Drones
            cyber_raw = data.get("cyberware", [])
            cyberware = [c.get("name", c.get("id", str(c))) if isinstance(c, dict) else str(c) for c in cyber_raw]

            drones_raw = data.get("drones", [])
            drones = [d.get("name", d.get("id", str(d))) if isinstance(d, dict) else str(d) for d in drones_raw]

            attr_str = ", ".join([f"{k.upper()}: {v}" for k, v in attrs.items() if isinstance(v, (int, float))])
            skill_str = ", ".join(skills[:12])
            qual_str = ", ".join(qualities[:12])

            lines = [
                f"### ACTIVE RUNNER DOSSIER: {name} ({archetype}, {metatype})",
                f"- Attributes: {attr_str}"
            ]
            if stream:
                lines.append(f"- Stream / Tradition: {stream}")
            if skill_str:
                lines.append(f"- Key Skills: {skill_str}")
            if qual_str:
                lines.append(f"- Active Qualities: {qual_str}")
            if echoes:
                lines.append(f"- Possessed Submersion Echoes / Metamagics: {', '.join(echoes)}")
            if complex_forms:
                lines.append(f"- Known Complex Forms: {', '.join(complex_forms)}")
            if spells:
                lines.append(f"- Known Spells: {', '.join(spells)}")
            if cyberware:
                lines.append(f"- Installed Cyberware: {', '.join(cyberware)}")
            if drones:
                lines.append(f"- Active Drones: {', '.join(drones)}")

            return "\n".join(lines) + "\n\n"
        except Exception:
            return ""

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
        provider_name: Optional[str] = None,
        llama_url: Optional[str] = None,
        char_id: Optional[str] = None,
        use_session: bool = False
    ) -> Dict[str, Any]:
        rules = self.search(user_query, limit=limit)
        rules_context = format_context_for_llm(rules)

        char_context = self._build_char_context(char_id) if char_id else ""
        context_str = f"{char_context}{rules_context}"

        ai_response = None
        error = None

        if provider_name:
            self.session.set_provider(provider_name)
        if model_name:
            self.session.set_model(model_name)
        if effort_level is not None:
            self.session.set_effort(effort_level)
        if llama_url:
            self.session.llama_url = llama_url

        if use_ai:
            if use_session:
                ai_response, error = self.session.send_query(user_query, context_str)
            else:
                target_model = model_name or self.session.model_name
                target_effort = effort_level if effort_level is not None else self.session.effort_level
                target_provider = provider_name or self.session.provider_name
                target_url = llama_url or self.session.llama_url

                ai_response, error = query_gemini(
                    user_query,
                    context_str,
                    model_name=target_model,
                    effort_level=target_effort,
                    provider_name=target_provider,
                    llama_url=target_url
                )

        return {
            "query": user_query,
            "char_id": char_id,
            "rules": rules,
            "context": context_str,
            "ai_response": ai_response,
            "error": error,
            "provider_name": self.session.provider_name,
            "model_name": self.session.model_name,
            "effort_level": self.session.effort_level
        }


