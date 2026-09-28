"""Week 6: build the document index end-to-end.

load files -> chunk -> embed -> store -> (optional) query.
Run it:  python -m ribot.build_index
"""

from __future__ import annotations

from pathlib import Path

from .chunking import chunk_text
from .embeddings import get_embedder
from .retriever import Retriever
from .vectorstore import get_store

SAMPLE_DIR = Path(__file__).resolve().parent.parent / "data" / "sample_docs"


def load_docs(folder: Path) -> list[tuple[str, str]]:
    """Return (filename, text) for every .md/.txt file in a folder."""
    docs: list[tuple[str, str]] = []
    for path in sorted(folder.glob("*")):
        if path.suffix.lower() in {".md", ".txt"}:
            try:
                docs.append((path.name, path.read_text(encoding="utf-8")))
            except OSError as err:  # missing-file / permission handling
                print(f"skip {path.name}: {err}")
    return docs


def build_index(
    folder: Path = SAMPLE_DIR,
    persist: bool = False,
    size: int = 300,
    overlap: int = 50,
    quiet: bool = False,
):
    """Build and return a Retriever over the documents in `folder`.

    `size` and `overlap` are the Week-6 chunking knobs, exposed here so Week 9 can sweep
    them and measure what changes. The defaults are exactly what Weeks 6-8 have always
    used, so existing calls behave identically.
    """
    embed = get_embedder()
    store = get_store(persist=persist)

    ids, documents, embeddings = [], [], []
    for name, text in load_docs(folder):
        for i, chunk in enumerate(chunk_text(text, size=size, overlap=overlap)):
            ids.append(f"{name}:{i}")
            documents.append(chunk)
            embeddings.append(embed(chunk))

    store.add(ids=ids, documents=documents, embeddings=embeddings)
    if not quiet:
        print(f"indexed {store.count()} chunks from {folder}")
    return Retriever(store, embed_fn=embed)


if __name__ == "__main__":
    retriever = build_index()
    question = "How do I reset my password?"
    print(f"\nQ: {question}")
    for chunk, score in retriever.search(question, k=2):
        print(f"  [{score:.3f}] {chunk[:80]}...")
