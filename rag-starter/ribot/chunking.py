"""Week 6: split a long document into overlapping chunks.

Overlap matters: if a sentence straddles a boundary, the overlap keeps the idea whole
in at least one chunk.
"""

from __future__ import annotations


def chunk_text(text: str, size: int = 300, overlap: int = 50) -> list[str]:
    """Slice text into chunks of `size` chars that overlap by `overlap` chars.

    >>> chunks = chunk_text("abcdefghij", size=4, overlap=1)
    >>> chunks
    ['abcd', 'defg', 'ghij', 'j']
    """
    if size <= 0:
        raise ValueError("size must be positive")
    if overlap >= size:
        raise ValueError("overlap must be smaller than size")

    step = size - overlap
    chunks: list[str] = []
    for start in range(0, len(text), step):
        chunk = text[start : start + size]
        if chunk:
            chunks.append(chunk)
    return chunks


if __name__ == "__main__":  # `python -m ribot.chunking`
    sample = "The quick brown fox jumps over the lazy dog. " * 5
    pieces = chunk_text(sample, size=60, overlap=10)
    print(f"{len(pieces)} chunks; first = {pieces[0]!r}")
