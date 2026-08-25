"""
Gemini File Search Store Inspector and Failure Diagnostics.
"""

import os
from typing import Dict, Any, List, Optional
from dotenv import load_dotenv
from google import genai


def get_gemini_client() -> genai.Client:
    from sr6core.rag.llm import load_environment
    load_environment()
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY environment variable not found.")
    return genai.Client(api_key=api_key)


def list_stores_summary() -> List[Dict[str, Any]]:
    """Lists all active File Search Stores with document counts."""
    client = get_gemini_client()
    stores = list(client.file_search_stores.list())
    summary = []
    for s in stores:
        summary.append({
            "name": s.name,
            "display_name": getattr(s, "display_name", "N/A"),
            "active_documents_count": getattr(s, "active_documents_count", 0),
            "pending_documents_count": getattr(s, "pending_documents_count", 0),
            "failed_documents_count": getattr(s, "failed_documents_count", 0)
        })
    return summary


def list_store_failures(store_name: str) -> List[Dict[str, Any]]:
    """Inspects a File Search Store and lists documents in 'failed' state."""
    client = get_gemini_client()
    docs = client.file_search_stores.documents.list(parent=store_name)
    failures = []
    for doc in docs:
        if getattr(doc, "state", "").lower() == "failed":
            failures.append({
                "name": doc.name,
                "display_name": getattr(doc, "display_name", "N/A"),
                "error": getattr(doc, "error", "Unknown error")
            })
    return failures
