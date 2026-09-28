"""Week 6: a place to store chunk vectors and search them.

Two backends, one interface:
- `InMemoryStore` — pure Python, no install, great for class and tests.
- `ChromaStore`   — persistent on disk via chromadb (the 'real' path).

`get_store()` returns Chroma if it's installed, otherwise the in-memory store.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from .similarity import cosine_similarity


@dataclass
class InMemoryStore:
    """A tiny vector store: keeps chunks + vectors in lists and ranks by cosine."""

    ids: list[str] = field(default_factory=list)
    documents: list[str] = field(default_factory=list)
    embeddings: list[list[float]] = field(default_factory=list)

    def add(self, ids: list[str], documents: list[str], embeddings: list[list[float]]) -> None:
        self.ids.extend(ids)
        self.documents.extend(documents)
        self.embeddings.extend(embeddings)

    def count(self) -> int:
        return len(self.ids)

    def query(self, embedding: list[float], n_results: int = 3) -> list[tuple[str, float]]:
        scored = [
            (doc, cosine_similarity(embedding, vec))
            for doc, vec in zip(self.documents, self.embeddings)
        ]
        scored.sort(key=lambda pair: pair[1], reverse=True)
        return scored[:n_results]


class ChromaStore:
    """Persistent store backed by chromadb, exposing the same small interface."""

    def __init__(self, path: str = ".chroma", name: str = "docs") -> None:
        import chromadb

        self._client = chromadb.PersistentClient(path=path)
        self._collection = self._client.get_or_create_collection(name)

    def add(self, ids: list[str], documents: list[str], embeddings: list[list[float]]) -> None:
        self._collection.add(ids=ids, documents=documents, embeddings=embeddings)

    def count(self) -> int:
        return self._collection.count()

    def query(self, embedding: list[float], n_results: int = 3) -> list[tuple[str, float]]:
        res = self._collection.query(query_embeddings=[embedding], n_results=n_results)
        docs = res.get("documents", [[]])[0]
        dists = res.get("distances", [[]])[0] or [0.0] * len(docs)
        # chroma returns distance (lower = closer); convert to a similarity-ish score.
        return [(doc, 1.0 - dist) for doc, dist in zip(docs, dists)]


def get_store(persist: bool = False, path: str = ".chroma", name: str = "docs"):
    """Return a Chroma store if available and requested, else an in-memory store."""
    if persist:
        try:
            return ChromaStore(path=path, name=name)
        except ImportError:
            print("chromadb not installed — using in-memory store instead.")
    return InMemoryStore()
