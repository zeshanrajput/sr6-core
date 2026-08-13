"""
LLM Client and System Instructions for SR6 RAG Vault.
Enforces 4-Level Authority Hierarchy and exact [Book, Page] source citations.
Supports both Google Gemini API and local llama.cpp / Gemma endpoints.
"""

import os
import json
import shutil
import glob
import time
import subprocess
import urllib.request
import urllib.error
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


DEFAULT_MODEL = os.environ.get("SR6_DEFAULT_MODEL", "gemini-flash-latest")

MODEL_ALIASES = {
    "flash-latest": "gemini-flash-latest",
    "gemini-flash-latest": "gemini-flash-latest",
    "flash-light-latest": "gemini-flash-lite-latest",
    "flash-lite-latest": "gemini-flash-lite-latest",
    "flash-light": "gemini-flash-lite-latest",
    "flash": "gemini-flash-latest",
    "3.7-flash": "gemini-flash-latest",
    "3.7": "gemini-flash-latest",
    "gemini-3.7-flash": "gemini-flash-latest",
    "pro": "gemini-2.5-pro",
    "gemma": "gemma-2-9b-it",
    "llama": "gemma-2-9b-it",
}

EFFORT_BUDGETS = {
    "high": 2048,
    "medium": 1024,
    "low": 512,
}

DEFAULT_LLAMA_URL = os.environ.get("SR6_LLAMA_URL", "http://localhost:8080/v1")


def resolve_model_name(model_name: str) -> str:
    """Normalizes model names and aliases."""
    normalized = model_name.strip().lower()
    return MODEL_ALIASES.get(normalized, model_name)


def load_environment():
    """Loads GEMINI_API_KEY and SR6_LLAMA config from environment or .env file across standard project locations."""
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    search_paths = [
        os.path.join(base_dir, ".env"),
        os.path.join(os.path.dirname(base_dir), "sr6yuriko", ".env"),
        "C:\\GitHub\\sr6-core\\.env",
        "C:\\GitHub\\sr6yuriko\\.env",
        "C:\\GitHub\\.env",
        os.path.join(os.getcwd(), ".env"),
        os.path.join(os.path.expanduser("~"), ".env")
    ]
    for path in search_paths:
        if os.path.exists(path):
            load_dotenv(path, override=True)


def find_llama_bin() -> Optional[str]:
    load_environment()
    env_bin = os.getenv("SR6_LLAMA_BIN")
    if env_bin and os.path.exists(env_bin):
        return env_bin
    
    for name in ["llama-server", "server", "llama-cli", "main"]:
        found = shutil.which(name)
        if found:
            return found
            
    search_dirs = [
        r"C:\Users\zesha\llama.cpp",
        os.path.expanduser(r"~\llama.cpp"),
        os.path.expanduser(r"~\bin"),
        os.path.expanduser(r"~\Downloads"),
        r"C:\llama.cpp",
        r"C:\tools\llama.cpp",
        r"C:\tools"
    ]
    for d in search_dirs:
        if os.path.exists(d):
            for exe in ["llama-server.exe", "server.exe", "main.exe", "llama-server"]:
                p = os.path.join(d, exe)
                if os.path.exists(p):
                    return p
    return None


def find_llama_model() -> Optional[str]:
    load_environment()
    env_model = os.getenv("SR6_LLAMA_MODEL_PATH")
    if env_model and os.path.exists(env_model) and env_model.lower().endswith(".gguf"):
        return env_model
        
    search_dirs = [
        r"C:\Users\zesha\models",
        os.path.expanduser(r"~\models"),
        os.path.expanduser(r"~\Downloads"),
        os.path.expanduser(r"~\.cache\lm-studio\models"),
        os.path.expanduser(r"~\.cache\huggingface"),
        os.path.expanduser(r"~\.ollama\models"),
        r"C:\models",
        r"D:\models",
        r"E:\models",
        r"C:\llama.cpp"
    ]
    for d in search_dirs:
        if os.path.exists(d):
            try:
                ggufs = glob.glob(os.path.join(d, "*.gguf")) + glob.glob(os.path.join(d, "**", "*.gguf"), recursive=True)
                if ggufs:
                    gemma_models = [g for g in ggufs if "gemma" in os.path.basename(g).lower()]
                    return gemma_models[0] if gemma_models else ggufs[0]
            except Exception:
                pass
    return None


def auto_launch_llama_server(base_url: str, model_name: str) -> Tuple[bool, Optional[str]]:
    endpoint = f"{base_url.rstrip('/')}/models"
    try:
        req = urllib.request.Request(endpoint)
        with urllib.request.urlopen(req, timeout=1.5) as resp:
            if resp.status == 200:
                return True, None
    except Exception:
        pass

    bin_path = find_llama_bin()
    model_path = find_llama_model()
    env_model = os.getenv("SR6_LLAMA_MODEL_PATH")

    if env_model and env_model.lower().endswith(".litertlm"):
        err_msg = (
            f"Local llama.cpp server is not active at {base_url}.\n"
            f"Note: '{env_model}' is in LiteRT-LM format. llama-server requires a GGUF model file (.gguf).\n"
            f"Please download a GGUF format model (e.g. gemma-2-9b-it.gguf) and set SR6_LLAMA_MODEL_PATH in .env, or start your server manually."
        )
        return False, err_msg

    if not bin_path or not model_path:
        missing = []
        if not bin_path:
            missing.append("llama-server executable (set SR6_LLAMA_BIN in .env)")
        if not model_path:
            missing.append("GGUF model file (.gguf) (set SR6_LLAMA_MODEL_PATH in .env)")
        err_msg = (
            f"Local llama.cpp server is not active at {base_url}.\n"
            f"Could not auto-launch server because missing: {', '.join(missing)}."
        )
        return False, err_msg

    port = "8080"
    if ":" in base_url:
        parts = base_url.split(":")
        if len(parts) >= 3:
            port = parts[2].split("/")[0]

    cmd = [
        bin_path,
        "-m", model_path,
        "--port", port,
        "-c", "8192",
        "--alias", model_name
    ]

    try:
        proc = subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        print(f"[+] Auto-launched local llama-server (PID: {proc.pid}) using model: {os.path.basename(model_path)}...")
        
        for _ in range(20):
            time.sleep(0.5)
            try:
                with urllib.request.urlopen(endpoint, timeout=1.0) as resp:
                    if resp.status == 200:
                        return True, None
            except Exception:
                pass
        return True, None
    except Exception as e:
        return False, f"Failed to auto-launch llama-server: {e}"


class BaseLLMProvider:
    """Abstract Base Class for RAG LLM Providers."""
    def generate(self, prompt: str, system_instruction: str = SYSTEM_INSTRUCTION) -> Tuple[Optional[str], Optional[str]]:
        raise NotImplementedError

    def chat_message(self, prompt: str, history: List[Dict[str, str]], system_instruction: str = SYSTEM_INSTRUCTION) -> Tuple[Optional[str], Optional[str]]:
        raise NotImplementedError


class GeminiProvider(BaseLLMProvider):
    """Google Gemini Client Provider."""
    def __init__(self, model_name: str = DEFAULT_MODEL, effort_level: Optional[str] = None):
        self.model_name = resolve_model_name(model_name)
        self.effort_level = effort_level
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
        if self._chat is None:
            self._chat = self._client.chats.create(model=self.model_name)

    def generate(self, prompt: str, system_instruction: str = SYSTEM_INSTRUCTION) -> Tuple[Optional[str], Optional[str]]:
        try:
            self._ensure_client()
            from google.genai import types
            full_prompt = f"{system_instruction}\n\n{prompt}"
            config = None
            if self.effort_level:
                budget = EFFORT_BUDGETS.get(self.effort_level.lower())
                if budget is not None:
                    config = types.GenerateContentConfig(
                        thinking_config=types.ThinkingConfig(thinking_budget=budget)
                    )
            response = self._client.models.generate_content(
                model=self.model_name,
                contents=full_prompt,
                config=config
            )
            return response.text, None
        except Exception as e:
            return None, f"Gemini generation error: {e}"

    def chat_message(self, prompt: str, history: List[Dict[str, str]], system_instruction: str = SYSTEM_INSTRUCTION) -> Tuple[Optional[str], Optional[str]]:
        try:
            self._ensure_client()
            from google.genai import types
            full_prompt = f"{system_instruction}\n\n{prompt}"
            config = None
            if self.effort_level:
                budget = EFFORT_BUDGETS.get(self.effort_level.lower())
                if budget is not None:
                    config = types.GenerateContentConfig(
                        thinking_config=types.ThinkingConfig(thinking_budget=budget)
                    )
            response = self._chat.send_message(full_prompt, config=config)
            return response.text, None
        except Exception as e:
            return None, f"Gemini chat error: {e}"


class LlamaCppProvider(BaseLLMProvider):
    """Local llama.cpp HTTP server provider (OpenAI-compatible endpoint with Gemma optimization)."""
    def __init__(self, model_name: str = "gemma-2-9b-it", base_url: str = DEFAULT_LLAMA_URL):
        self.model_name = resolve_model_name(model_name)
        self.base_url = base_url.rstrip('/')

    def generate(self, prompt: str, system_instruction: str = SYSTEM_INSTRUCTION) -> Tuple[Optional[str], Optional[str]]:
        return self.chat_message(prompt=prompt, history=[], system_instruction=system_instruction)

    def chat_message(self, prompt: str, history: List[Dict[str, str]], system_instruction: str = SYSTEM_INSTRUCTION) -> Tuple[Optional[str], Optional[str]]:
        ok, launch_err = auto_launch_llama_server(self.base_url, self.model_name)
        if not ok:
            return None, launch_err

        endpoint = f"{self.base_url}/chat/completions"
        
        # Build messages payload
        messages = [{"role": "system", "content": system_instruction}]
        for h in history:
            if "user" in h:
                messages.append({"role": "user", "content": h["user"]})
            if "assistant" in h:
                messages.append({"role": "assistant", "content": h["assistant"]})
        messages.append({"role": "user", "content": prompt})

        payload = {
            "messages": messages,
            "temperature": 0.3,
            "max_tokens": 1024,
        }

        def send_req(body_dict: dict) -> Tuple[Optional[str], Optional[str]]:
            data = json.dumps(body_dict).encode("utf-8")
            req = urllib.request.Request(
                endpoint,
                data=data,
                headers={"Content-Type": "application/json"}
            )
            try:
                with urllib.request.urlopen(req, timeout=60) as resp:
                    result = json.loads(resp.read().decode("utf-8"))
                    content = result["choices"][0]["message"]["content"]
                    return content, None
            except urllib.error.HTTPError as e:
                body = e.read().decode("utf-8", errors="ignore") if hasattr(e, "read") else ""
                return None, f"HTTP Error {e.code}: {body or e.reason}"
            except urllib.error.URLError as e:
                return None, f"Connection error at {endpoint}: {e}."
            except Exception as e:
                return None, f"llama.cpp generation error: {e}"

        res, err = send_req(payload)
        if err and "400" in err:
            # Fallback: combine system prompt into single user message if llama-server rejects system role
            combined_prompt = f"{system_instruction}\n\n"
            for h in history:
                if "user" in h:
                    combined_prompt += f"User: {h['user']}\n"
                if "assistant" in h:
                    combined_prompt += f"Assistant: {h['assistant']}\n"
            combined_prompt += f"User: {prompt}"

            fallback_payload = {
                "messages": [{"role": "user", "content": combined_prompt}],
                "temperature": 0.3,
                "max_tokens": 1024
            }
            res, err = send_req(fallback_payload)

        return res, err


def get_llm_provider(
    provider_name: str = "gemini",
    model_name: str = DEFAULT_MODEL,
    effort_level: Optional[str] = None,
    llama_url: str = DEFAULT_LLAMA_URL
) -> BaseLLMProvider:
    p_norm = provider_name.strip().lower()
    m_norm = model_name.strip().lower()

    # Auto-detect local llama provider if provider is llama/local OR if model is gemma/llama/gguf
    if p_norm in ["llama", "llamacpp", "gemma", "local"] or any(k in m_norm for k in ["gemma", "llama", "gguf"]):
        return LlamaCppProvider(model_name=model_name, base_url=llama_url)
    return GeminiProvider(model_name=model_name, effort_level=effort_level)


def query_gemini(
    user_query: str,
    context_str: str,
    model_name: str = DEFAULT_MODEL,
    effort_level: Optional[str] = None,
    chat_session: Optional[Any] = None,
    provider_name: str = "gemini",
    llama_url: str = DEFAULT_LLAMA_URL
) -> Tuple[Optional[str], Optional[str]]:
    """
    Queries LLM (Gemini or Local llama.cpp) with system instructions and retrieved context.
    """
    provider = get_llm_provider(
        provider_name=provider_name,
        model_name=model_name,
        effort_level=effort_level,
        llama_url=llama_url
    )
    prompt = f"### RETRIEVED RULES CONTEXT:\n{context_str}\n\n### USER QUERY:\n{user_query}"
    return provider.generate(prompt)


class RAGChatSession:
    """
    Interactive conversation session manager supporting provider selection, model switching, and thread history.
    """
    def __init__(
        self,
        model_name: str = DEFAULT_MODEL,
        effort_level: Optional[str] = "medium",
        provider_name: str = "gemini",
        llama_url: str = DEFAULT_LLAMA_URL
    ):
        self.model_name = resolve_model_name(model_name)
        self.effort_level = effort_level
        self.provider_name = provider_name
        self.llama_url = llama_url
        self.history: List[Dict[str, str]] = []
        self._provider: Optional[BaseLLMProvider] = None

    def _get_provider(self) -> BaseLLMProvider:
        if self._provider is None:
            self._provider = get_llm_provider(
                provider_name=self.provider_name,
                model_name=self.model_name,
                effort_level=self.effort_level,
                llama_url=self.llama_url
            )
        return self._provider

    def set_provider(self, provider_name: str):
        if provider_name != self.provider_name:
            self.provider_name = provider_name
            self._provider = None

    def set_model(self, model_name: str):
        norm = resolve_model_name(model_name)
        if norm != self.model_name:
            self.model_name = norm
            if any(k in norm.lower() for k in ["gemma", "llama", "gguf"]):
                self.provider_name = "llama"
            self._provider = None

    def set_effort(self, effort_level: Optional[str]):
        if effort_level and effort_level.lower() in EFFORT_BUDGETS:
            self.effort_level = effort_level.lower()
        elif not effort_level or effort_level.lower() in ["none", "off"]:
            self.effort_level = None

    def clear_history(self):
        self.history.clear()
        self._provider = None

    def send_query(self, user_query: str, context_str: str) -> Tuple[Optional[str], Optional[str]]:
        provider = self._get_provider()
        prompt = f"### RETRIEVED RULES CONTEXT:\n{context_str}\n\n### USER QUERY:\n{user_query}"
        text, error = provider.chat_message(prompt, history=self.history)
        if text:
            self.history.append({"user": user_query, "assistant": text})
        return text, error



