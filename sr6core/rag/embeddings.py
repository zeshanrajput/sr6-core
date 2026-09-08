"""
Local Offline Vector Embedding and Semantic Search Engine for Shadowrun 6e Rules.
Integrates sentence embeddings, sqlite-vec extension with NumPy fallback, and Reciprocal Rank Fusion (RRF).
"""

import os
import re
import sqlite3
import numpy as np
from typing import Dict, Any, List, Optional, Tuple

DEFAULT_EMBED_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
EMBEDDING_DIM = 384


class LocalEmbeddingEngine:
    """Manages local sentence embedding generation using transformers/PyTorch with CPU/CUDA support."""
    _instance: Optional["LocalEmbeddingEngine"] = None

    def __init__(self, model_name: str = DEFAULT_EMBED_MODEL):
        self.model_name = model_name
        self.tokenizer = None
        self.model = None
        self.device = "cpu"
        self._initialized = False

    @classmethod
    def get_instance(cls) -> "LocalEmbeddingEngine":
        if cls._instance is None:
            cls._instance = LocalEmbeddingEngine()
        return cls._instance

    def _lazy_init(self):
        if self._initialized:
            return
        try:
            import torch
            from transformers import AutoTokenizer, AutoModel

            self.device = "cuda" if torch.cuda.is_available() else "cpu"
            self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
            self.model = AutoModel.from_pretrained(self.model_name).to(self.device)
            self.model.eval()
            self._initialized = True
        except Exception:
            # Fallback to pseudo-projection if transformers / torch cannot load
            self._initialized = False

    def embed_text(self, text: str) -> np.ndarray:
        """Generates a normalized 384-dimensional dense float32 vector for a text string."""
        return self.embed_batch([text])[0]

    def embed_batch(self, texts: List[str], max_length: int = 256) -> np.ndarray:
        """Batched vector generation with mean pooling and L2 normalization."""
        self._lazy_init()
        if not self._initialized or not self.model or not self.tokenizer:
            # Deterministic hash-based projection fallback (guarantees offline functionality)
            return self._hash_projection_batch(texts)

        import torch
        clean_texts = [re.sub(r"\s+", " ", t).strip()[:1000] for t in texts]
        if not clean_texts:
            return np.zeros((0, EMBEDDING_DIM), dtype=np.float32)

        with torch.no_grad():
            encoded = self.tokenizer(
                clean_texts,
                padding=True,
                truncation=True,
                max_length=max_length,
                return_tensors="pt"
            ).to(self.device)

            output = self.model(**encoded)
            # Mean pooling over attention mask
            token_embeddings = output.last_hidden_state
            attention_mask = encoded["attention_mask"].unsqueeze(-1).expand(token_embeddings.size()).float()
            sum_embeddings = torch.sum(token_embeddings * attention_mask, 1)
            sum_mask = torch.clamp(attention_mask.sum(1), min=1e-9)
            mean_pooled = sum_embeddings / sum_mask

            # L2 normalization
            normalized = torch.nn.functional.normalize(mean_pooled, p=2, dim=1)
            return normalized.cpu().numpy().astype(np.float32)

    def _hash_projection_batch(self, texts: List[str]) -> np.ndarray:
        """Lightweight offline n-gram pseudo-embedding fallback."""
        vectors = np.zeros((len(texts), EMBEDDING_DIM), dtype=np.float32)
        for i, t in enumerate(texts):
            words = re.findall(r"\b\w+\b", t.lower())
            if not words:
                continue
            for w in words:
                h = hash(w) % EMBEDDING_DIM
                vectors[i, h] += 1.0
            norm = np.linalg.norm(vectors[i])
            if norm > 0:
                vectors[i] /= norm
        return vectors


class VectorVault:
    """Manages SQLite vector tables, sqlite-vec virtual tables, and semantic search."""

    @staticmethod
    def load_sqlite_vec(conn: sqlite3.Connection) -> bool:
        """Attempts to load the native sqlite-vec extension into the SQLite connection."""
        try:
            import sqlite_vec
            conn.enable_load_extension(True)
            sqlite_vec.load(conn)
            conn.enable_load_extension(False)
            return True
        except Exception:
            return False

    @classmethod
    def ensure_tables(cls, conn: sqlite3.Connection) -> bool:
        """Initializes both the BLOB vector storage table and the sqlite-vec virtual table if available."""
        with conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS rule_embeddings (
                    id TEXT PRIMARY KEY,
                    topic TEXT,
                    embedding BLOB
                );
            """)

        has_vec = cls.load_sqlite_vec(conn)
        if has_vec:
            try:
                with conn:
                    conn.execute(f"""
                        CREATE VIRTUAL TABLE IF NOT EXISTS vec_rules USING vec0(
                            id TEXT PRIMARY KEY,
                            embedding float[{EMBEDDING_DIM}]
                        );
                    """)
                return True
            except Exception:
                pass
        return False

    @classmethod
    def index_rules_batch(cls, conn: sqlite3.Connection, rules: List[Dict[str, Any]], batch_size: int = 32):
        """Indexes a batch of rules into rule_embeddings and vec_rules."""
        cls.ensure_tables(conn)
        has_vec = cls.load_sqlite_vec(conn)
        engine = LocalEmbeddingEngine.get_instance()

        for i in range(0, len(rules), batch_size):
            chunk = rules[i : i + batch_size]
            texts = []
            for r in chunk:
                topic = r.get("topic", "")
                content = r.get("content", "")[:600]
                texts.append(f"{topic}: {content}")

            embeddings = engine.embed_batch(texts)

            with conn:
                for r, emb in zip(chunk, embeddings):
                    rid = r["id"]
                    topic = r.get("topic", "")
                    raw_blob = emb.tobytes()

                    conn.execute(
                        "INSERT OR REPLACE INTO rule_embeddings (id, topic, embedding) VALUES (?, ?, ?)",
                        (rid, topic, raw_blob)
                    )

                    if has_vec:
                        try:
                            conn.execute(
                                "INSERT OR REPLACE INTO vec_rules (id, embedding) VALUES (?, ?)",
                                (rid, raw_blob)
                            )
                        except Exception:
                            pass

    @classmethod
    def search_vector(
        cls,
        conn: sqlite3.Connection,
        query: str,
        limit: int = 15
    ) -> List[Dict[str, Any]]:
        """
        Executes semantic vector search against sqlite-vec or NumPy cosine fallback.
        Returns [{'id': str, 'score': float, 'distance': float}, ...]
        """
        if not query or not query.strip():
            return []

        cls.ensure_tables(conn)
        has_vec = cls.load_sqlite_vec(conn)
        engine = LocalEmbeddingEngine.get_instance()
        q_emb = engine.embed_text(query)

        # 1. Try native sqlite-vec virtual table query
        if has_vec:
            try:
                cursor = conn.cursor()
                rows = cursor.execute(
                    """
                    SELECT id, distance
                    FROM vec_rules
                    WHERE embedding MATCH ?
                    ORDER BY distance ASC
                    LIMIT ?
                    """,
                    (q_emb.tobytes(), limit)
                ).fetchall()

                if rows:
                    return [{"id": r[0], "distance": float(r[1]), "score": float(1.0 / (1.0 + r[1]))} for r in rows]
            except Exception:
                pass

        # 2. Fast NumPy in-memory dot product fallback
        cursor = conn.cursor()
        rows = cursor.execute("SELECT id, embedding FROM rule_embeddings").fetchall()
        if not rows:
            return []

        ids = [r[0] for r in rows]
        matrix = np.array([np.frombuffer(r[1], dtype=np.float32) for r in rows])

        # Cosine similarity for normalized vectors is simply dot product
        similarities = np.dot(matrix, q_emb)
        top_indices = np.argsort(similarities)[::-1][:limit]

        results = []
        for idx in top_indices:
            score = float(similarities[idx])
            if score > 0.05:  # Relevance floor
                results.append({
                    "id": ids[idx],
                    "score": score,
                    "distance": float(1.0 - score)
                })

        return results

    @staticmethod
    def reciprocal_rank_fusion(
        keyword_results: List[Dict[str, Any]],
        vector_results: List[Dict[str, Any]],
        rrf_k: int = 60,
        limit: int = 15
    ) -> List[Dict[str, Any]]:
        """
        Merges keyword (BM25) and vector (semantic) ranked results using Reciprocal Rank Fusion (RRF).
        RRF Score(d) = SUM(1 / (k + rank(d)))
        """
        scores: Dict[str, float] = {}
        merged_items: Dict[str, Dict[str, Any]] = {}

        for rank, item in enumerate(keyword_results):
            iid = item["id"]
            scores[iid] = scores.get(iid, 0.0) + (1.0 / (rrf_k + rank + 1))
            merged_items[iid] = item

        for rank, item in enumerate(vector_results):
            iid = item["id"]
            scores[iid] = scores.get(iid, 0.0) + (1.0 / (rrf_k + rank + 1))
            if iid not in merged_items:
                merged_items[iid] = item

        sorted_ids = sorted(scores.keys(), key=lambda x: scores[x], reverse=True)[:limit]
        fused = []
        for sid in sorted_ids:
            it = merged_items[sid]
            it["rrf_score"] = scores[sid]
            fused.append(it)

        return fused

    @classmethod
    def index_vault(
        cls,
        conn: sqlite3.Connection,
        batch_size: int = 64,
        progress_callback: Optional[Any] = None
    ) -> int:
        """
        Indexes all rules from the rules table into rule_embeddings and vec_rules.
        Returns total rules indexed.
        """
        cls.ensure_tables(conn)
        cursor = conn.cursor()
        rows = cursor.execute("SELECT id, topic, content FROM rules").fetchall()
        rules = [{"id": r[0], "topic": r[1], "content": r[2]} for r in rows]
        if not rules:
            return 0
        total = len(rules)
        for i in range(0, total, batch_size):
            chunk = rules[i : i + batch_size]
            cls.index_rules_batch(conn, chunk, batch_size=batch_size)
            if progress_callback:
                progress_callback(min(i + batch_size, total), total)
        return total
