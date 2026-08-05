"""
LLM Client and System Instructions for SR6 RAG Vault.
Enforces 4-Level Authority Hierarchy and exact [Book, Page] source citations.
"""

import os
from typing import Optional, Tuple
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


def load_environment():
    """Loads GEMINI_API_KEY from environment or .env file."""
    search_paths = [
        os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), ".env"),
        "C:\\GitHub\\.env",
        ".env",
        os.path.expanduser("~\\.env")
    ]
    for path in search_paths:
        if os.path.exists(path):
            load_dotenv(path, override=False)

    if not os.getenv("GEMINI_API_KEY"):
        for path in search_paths:
            if os.path.exists(path):
                try:
                    with open(path, "r", encoding="utf-8") as f:
                        for line in f:
                            line = line.strip()
                            if line and not line.startswith("#") and "GEMINI_API_KEY" in line:
                                parts = line.split("=", 1)
                                os.environ["GEMINI_API_KEY"] = parts[1].strip().strip('"').strip("'")
                                break
                except Exception:
                    pass


def query_gemini(user_query: str, context_str: str, model_name: str = "gemini-2.5-flash") -> Tuple[Optional[str], Optional[str]]:
    """
    Queries Gemini API with system instructions and retrieved rules context.
    """
    load_environment()
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        return None, "GEMINI_API_KEY not found in environment or .env files."

    try:
        from google import genai
        client = genai.Client(api_key=api_key)
    except ImportError:
        return None, "google-genai library not installed."
    except Exception as e:
        return None, f"Failed to initialize Gemini client: {e}"

    full_prompt = (
        f"{SYSTEM_INSTRUCTION}\n\n"
        f"### RETRIEVED RULES CONTEXT:\n{context_str}\n\n"
        f"### USER QUERY:\n{user_query}"
    )

    try:
        response = client.models.generate_content(
            model=model_name,
            contents=full_prompt
        )
        return response.text, None
    except Exception as e:
        return None, f"Gemini generation error: {e}"
