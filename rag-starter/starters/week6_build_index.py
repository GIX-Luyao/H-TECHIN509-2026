"""Week 6 faded exercise: load -> chunk -> embed -> store -> query.

Fill in each # TODO. Reference: ribot/build_index.py
Run:  python starters/week6_build_index.py
"""

from __future__ import annotations

from pathlib import Path

from ribot.chunking import chunk_text
from ribot.embeddings import get_embedder
from ribot.vectorstore import InMemoryStore

embed = get_embedder()
SAMPLE_DIR = Path(__file__).resolve().parent.parent / "data" / "sample_docs"


def build() -> InMemoryStore:
    store = InMemoryStore()
    for path in sorted(SAMPLE_DIR.glob("*.md")):
        text = path.read_text(encoding="utf-8")
        # TODO 1: chunk the text with chunk_text(text)
        chunks: list[str] = []  # replace
        for i, chunk in enumerate(chunks):
            # TODO 2: add one item: ids=[f"{path.name}:{i}"], documents=[chunk],
            #         embeddings=[embed(chunk)]
            pass
    print("stored", store.count(), "chunks")
    return store


def ask(store: InMemoryStore, question: str) -> None:
    # TODO 3: embed the question, then call store.query(vector, n_results=2)
    print("(fill in TODO 3 to see results for:", question, ")")


if __name__ == "__main__":
    s = build()
    ask(s, "how do I reset my password?")
