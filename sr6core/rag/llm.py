"""
LLM Client and System Instructions for SR6 RAG Vault.
Enforces 4-Level Authority Hierarchy and exact [Book, Page] source citations.
"""

import os
from typing import Optional, Tuple, Any, List, Dict
from dotenv import load_dotenv

SYSTEM_INSTRUCTION = """ROLE: Table-side Rules Reference Assistant for Shadowrun Missions (SRM) campaigns.

---

### 1. THE FOUR-LEVEL AUTHORITY ORDER
When resolving rules questions or identifying conflicting text, evaluate metadata priority using this strict model:

*   **[LEVEL 1] SRM Campaign Specific Exception**: Contained in documents like 'SRM 6E Missions FAQ' or 'SRM 6E Guidebook'. Directives here override standard publisher material.
*   **[LEVEL 2] Core Rulebook Expansions & Companions**: Contained in supplements (such as 'Hack and Slash' or 'Companion Sourcebook'). These explain, expand, and override standard core rules.
*   **[LEVEL 3] Standard Core Rulebook**: Baseline standard regulations from 'SR6 Core Rulebook'.
*   **[LEVEL 4] Unofficial House Rules / Homebrew**: Fan-made or custom local GM notes.
    ⚠️ *CRITICAL MANDATE*: You are permitted to reference Level 4 content, but MUST include explicit notice:
    "⚠️ UNSANCTIONED CONTENT WARNING: This reference utilizes Level 4 (Unofficial) homebrew material which is strictly prohibited in official Shadowrun Missions play."

---

### 2. EXACT SOURCE CITATIONS (NO SYMBOLIC FOOTNOTES)
Every response statement or cost breakdown must be verified back to physical page numbers. Citations must follow the explicit format:
`[Book Name, Page Number]`
*Example*:
"Raising your Agility costs 45 Karma total [SRM 6E Guidebook, Page 14]."
"""


MODEL_ALIASES = {
    "flash-latest": "gemini-flash-latest",
    "flash-light-latest": "gemini-flash-lite-latest",
    "flash-lite-latest": "gemini-flash-lite-latest",
    "flash-light": "gemini-flash-lite-latest",
    "flash": "gemini-flash-latest",
    "pro": "gemini-2.5-pro",
}

EFFORT_BUDGETS = {
    "high": 2048,
    "medium": 1024,
    "low": 512,
}


def resolve_model_name(model_name: str) -> str:
    """Normalizes model names and aliases."""
    normalized = model_name.strip().lower()
    return MODEL_ALIASES.get(normalized, model_name)


def load_environment():
    """Loads GEMINI_API_KEY from environment or .env file across standard project locations."""
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    search_paths = [
        os.path.join(base_dir, ".env"),
        os.path.join(os.path.dirname(base_dir), "sr6yuriko", ".env"),
        "C:\\GitHub\\sr6-core\\.env",
        "C:\\GitHub\\sr6yuriko\\.env",
        "C:\\GitHub\\.env",
        os.path.join(os.getcwd(), ".env"),
        os.path.expanduser("~\\.env")
    ]
    for path in search_paths:
        if os.path.exists(path):
            load_dotenv(path, override=True)
            key = os.getenv("GEMINI_API_KEY")
            if key and key.strip():
                os.environ["GEMINI_API_KEY"] = key.strip().strip('"').strip("'")
                return

    if not os.getenv("GEMINI_API_KEY"):
        for path in search_paths:
            if os.path.exists(path):
                try:
                    with open(path, "r", encoding="utf-8") as f:
                        for line in f:
                            line = line.strip()
                            if line and not line.startswith("#") and "GEMINI_API_KEY" in line:
                                parts = line.split("=", 1)
                                val = parts[1].strip().strip('"').strip("'")
                                if val:
                                    os.environ["GEMINI_API_KEY"] = val
                                    return
                except Exception:
                    pass


def query_gemini(
    user_query: str,
    context_str: str,
    model_name: str = "flash-latest",
    effort_level: Optional[str] = None,
    chat_session: Optional[Any] = None
) -> Tuple[Optional[str], Optional[str]]:
    """
    Queries Gemini API with system instructions, retrieved rules context, selected model, and effort level.
    """
    load_environment()
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        return None, "GEMINI_API_KEY not found in environment or .env files."

    try:
        from google import genai
        from google.genai import types
        client = genai.Client(api_key=api_key)
    except ImportError:
        return None, "google-genai library not installed."
    except Exception as e:
        return None, f"Failed to initialize Gemini client: {e}"

    target_model = resolve_model_name(model_name)

    full_prompt = (
        f"{SYSTEM_INSTRUCTION}\n\n"
        f"### RETRIEVED RULES CONTEXT:\n{context_str}\n\n"
        f"### USER QUERY:\n{user_query}"
    )

    config = None
    if effort_level:
        budget = EFFORT_BUDGETS.get(effort_level.lower())
        if budget is not None:
            config = types.GenerateContentConfig(
                thinking_config=types.ThinkingConfig(thinking_budget=budget)
            )

    try:
        if chat_session:
            response = chat_session.send_message(full_prompt, config=config, model=target_model)
        else:
            response = client.models.generate_content(
                model=target_model,
                contents=full_prompt,
                config=config
            )
        return response.text, None
    except Exception as e:
        return None, f"Gemini generation error: {e}"


class RAGChatSession:
    """
    Interactive conversation session manager supporting model switching, effort levels, and thread clearing.
    """
    def __init__(self, model_name: str = "flash-latest", effort_level: Optional[str] = "medium"):
        self.model_name = resolve_model_name(model_name)
        self.effort_level = effort_level
        self.history: List[Dict[str, str]] = []
        self._client = None
        self._chat = None

    def _ensure_client(self):
        load_environment()
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY not found in environment or .env files.")
        from google import genai
        if self._client is None:
            self._client = genai.Client(api_key=api_key)
        if not self._chat:
            self._chat = self._client.chats.create(model=self.model_name)

    def set_model(self, model_name: str):
        normalized = resolve_model_name(model_name)
        if normalized != self.model_name:
            self.model_name = normalized
            self._chat = None

    def set_effort(self, effort_level: Optional[str]):
        if effort_level and effort_level.lower() in EFFORT_BUDGETS:
            self.effort_level = effort_level.lower()
        elif not effort_level or effort_level.lower() in ["none", "off"]:
            self.effort_level = None

    def clear_history(self):
        self.history.clear()
        self._chat = None

    def send_query(self, user_query: str, context_str: str) -> Tuple[Optional[str], Optional[str]]:
        try:
            self._ensure_client()
        except Exception as e:
            return None, f"Gemini client initialization error: {e}"

        from google.genai import types

        target_model = resolve_model_name(self.model_name)
        prompt = (
            f"{SYSTEM_INSTRUCTION}\n\n"
            f"### RETRIEVED RULES CONTEXT:\n{context_str}\n\n"
            f"### USER QUERY:\n{user_query}"
        )

        config = None
        if self.effort_level:
            budget = EFFORT_BUDGETS.get(self.effort_level.lower())
            if budget is not None:
                config = types.GenerateContentConfig(
                    thinking_config=types.ThinkingConfig(thinking_budget=budget)
                )

        try:
            if not self._chat:
                self._chat = self._client.chats.create(model=target_model)
            res = self._chat.send_message(prompt, config=config)
            text = res.text
            self.history.append({"user": user_query, "assistant": text})
            return text, None
        except Exception as e:
            err_msg = str(e)
            if "client has been closed" in err_msg.lower() or "closed" in err_msg.lower():
                self._client = None
                self._chat = None
            return None, f"Gemini chat error: {e}"


