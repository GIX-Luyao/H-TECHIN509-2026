"""Week 6: tie embeddings + the vector store together into a Retriever.

A Retriever answers one question: 'which stored chunks are most relevant to this query?'

Week 9 adds a second way to answer it — `search_hybrid` — without touching `search`.
Everything Weeks 6, 7 and 8 built keeps calling `search` and keeps behaving identically.
"""

from __future__ import annotations

from typing import Callable

from .embeddings import get_embedder
from .rerank import rerank


class Retriever:
    """Embeds a query and returns the nearest stored chunks."""

    def __init__(
        self, store, embed_fn: Callable[[str], list[float]] | None = None
    ) -> None:
        self._store = store
        self._embed = embed_fn or get_embedder()

    def search(self, query: str, k: int = 3) -> list[tuple[str, float]]:
        """Return up to k (chunk, score) pairs, best first."""
        query_vec = self._embed(query)
        return self._store.query(query_vec, n_results=k)

    def search_hybrid(
        self,
        query: str,
        k: int = 3,
        alpha: float = 0.5,
        pool: int | None = None,
    ) -> list[tuple[str, float]]:
        """Week 9: retrieve a WIDE pool by meaning, then rerank it by meaning + words.

        Two stages, and the order matters:
          1. `search` fetches `pool` candidates using the Week-5 cosine score.
          2. `rerank` re-orders that pool by blending in an exact-word score.

        Stage 2 can only reorder what stage 1 found, so the pool is deliberately wider
        than `k` — that is what gives reranking something to fix. A pool as wide as your
        whole index is the most thorough option and, on a small corpus, entirely affordable.

        Args:
            query: the question to search for (rewrite follow-ups FIRST — see ribot.rewrite).
            k: how many chunks to return.
            alpha: 1.0 = pure semantic (identical to `search`), 0.0 = pure keyword.
            pool: candidates to rerank. Defaults to 5x k, at least 20.
        """
        if k <= 0:
            raise ValueError(f"k must be positive, got {k}")
        candidate_pool = pool if pool is not None else max(5 * k, 20)
        candidates = self.search(query, k=candidate_pool)
        return rerank(query, candidates, alpha=alpha)[:k]

    def search_text(self, query: str, k: int = 3) -> str:
        """Return the top chunks joined into one string (handy for prompts/tools)."""
        hits = self.search(query, k=k)
        if not hits:
            return ""
        return "\n---\n".join(doc for doc, _ in hits)

    def sources(self) -> list[str]:
        """Every distinct source file in the index, sorted (Week 8's second tool).

        Works with the in-memory store, which keeps ids like 'notes.md:4' as a plain
        list; a Chroma-backed store doesn't expose them, so we return [] honestly.
        """
        ids = getattr(self._store, "ids", None)
        if not ids:
            return []
        return sorted({chunk_id.split(":")[0] for chunk_id in ids})

    def source_of(self, chunk: str) -> str:
        """Which file did this chunk come from? Ids look like 'notes.md:4' (Week 6).

        Works with the in-memory store, which keeps ids and documents as parallel
        lists; a Chroma-backed store doesn't expose them, so we say so honestly.
        """
        documents = getattr(self._store, "documents", None)
        if documents and chunk in documents:
            chunk_id = self._store.ids[documents.index(chunk)]
            return chunk_id.split(":")[0]
        return "unknown source"
