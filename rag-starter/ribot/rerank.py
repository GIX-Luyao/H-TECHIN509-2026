"""Week 9: reorder retrieved chunks by mixing two different kinds of evidence.

Week 5 built one scorer: cosine similarity between embeddings. It scores *meaning*, which
is exactly what makes semantic search feel smart — and exactly what makes it fumble an
exact string. Ask `fallback_embed` for "NCR-2031" and it does not look for that text; it
hashes "ncr" and "2031" into buckets and adds up overlap, so a document that merely talks
about NCRs a lot can outrank the one document that actually contains NCR-2031.

So we add a second, dumber scorer that only knows about exact words, and combine them:

    vector score   — "does this chunk MEAN the same thing?"   (Week 5 cosine)
    lexical score  — "does this chunk CONTAIN these words?"   (this module)
    fused score    — a weighted blend of the two, controlled by `alpha`

That blend is called **hybrid retrieval**, and the reorder step is called **reranking**.
Both are standard practice, and neither is guaranteed to help *your* corpus — which is why
Week 9 makes you measure it before you keep it.
"""

from __future__ import annotations

from typing import Sequence

from .embeddings import _tokens

Hit = tuple[str, float]


def lexical_score(query: str, chunk: str) -> float:
    """Fraction of the query's content words that literally appear in this chunk.

    No embeddings, no model, no magic: set overlap on the same tokenizer `fallback_embed`
    uses. 1.0 means every content word in the query is present somewhere in the chunk.

    Its weakness is the flip side of its strength: exact means exact. There is no stemming
    here, so "disposition" does not match "dispositions" — a real limitation of keyword
    matching, and half the reason you blend it with the vector score instead of replacing it.

    >>> round(lexical_score("NCR-2031 disposition", "NCR-2031 was reworked"), 3)
    0.667
    >>> lexical_score("NCR-2031 disposition", "Dispositions: use-as-is, rework")
    0.0
    >>> lexical_score("torque limit", "no matching words here")
    0.0
    """
    query_tokens = set(_tokens(query))
    if not query_tokens:
        return 0.0
    chunk_tokens = set(_tokens(chunk))
    return len(query_tokens & chunk_tokens) / len(query_tokens)


def normalize(hits: Sequence[Hit]) -> list[Hit]:
    """Rescale scores onto 0..1 by dividing by the best one. Returns a NEW list.

    Needed because the two scorers do not live on the same scale: offline cosine scores
    cluster around 0.1-0.5, while `lexical_score` happily returns 1.0. Adding them raw
    would quietly let the lexical score dominate, and you would never see it happen.

    >>> normalize([("a", 0.4), ("b", 0.2)])
    [('a', 1.0), ('b', 0.5)]
    >>> normalize([("a", 0.0), ("b", 0.0)])
    [('a', 0.0), ('b', 0.0)]
    """
    best = max((score for _, score in hits), default=0.0)
    if best <= 0:
        return [(chunk, 0.0) for chunk, _ in hits]
    return [(chunk, score / best) for chunk, score in hits]


def fuse(
    vector_hits: Sequence[Hit],
    lexical_hits: Sequence[Hit],
    alpha: float = 0.5,
) -> list[Hit]:
    """Blend two scored lists into one ranking. Returns a NEW list, best first.

    `alpha` is the dial: 1.0 is pure semantic search (Week 6 behavior, unchanged), 0.0 is
    pure keyword matching, 0.5 splits the difference. A chunk missing from one list scores
    0.0 there rather than being dropped.

    Chunk "b" wins here despite a weaker vector score, because the lexical scorer is
    certain about it. That reordering is the whole point of the module.

    >>> fuse([("a", 1.0), ("b", 0.5)], [("b", 1.0), ("a", 0.0)], alpha=0.5)
    [('b', 0.75), ('a', 0.5)]
    """
    if not 0.0 <= alpha <= 1.0:
        raise ValueError(f"alpha must be between 0 and 1, got {alpha}")

    vector_scores = dict(normalize(vector_hits))
    lexical_scores = dict(normalize(lexical_hits))

    fused = [
        (
            chunk,
            alpha * vector_scores.get(chunk, 0.0)
            + (1 - alpha) * lexical_scores.get(chunk, 0.0),
        )
        for chunk in {**vector_scores, **lexical_scores}
    ]
    fused.sort(key=lambda pair: pair[1], reverse=True)
    return fused


def rerank(query: str, vector_hits: Sequence[Hit], alpha: float = 0.5) -> list[Hit]:
    """Score the vector hits lexically too, then return them re-ordered by the blend.

    The honest limit, and it matters: reranking can only reorder what the first stage
    already retrieved. If the right chunk is not in `vector_hits`, no amount of clever
    reordering will conjure it — you need a bigger candidate pool (see
    `Retriever.search_hybrid`, which asks for a wide pool before it reranks).
    """
    lexical_hits = [(chunk, lexical_score(query, chunk)) for chunk, _ in vector_hits]
    return fuse(vector_hits, lexical_hits, alpha=alpha)


if __name__ == "__main__":  # `python -m ribot.rerank`
    query = "NCR-2031"
    chunks = [
        (
            "Any departure is documented as a nonconformance report (NCR) per QP-09.",
            0.35,
        ),
        ("## NCR-2031 — Finding: shaft binding, breakaway torque 0.9 N-m.", 0.34),
    ]
    print(f"query: {query!r}\n")
    print("  vector order (Week 6):")
    for chunk, score in sorted(chunks, key=lambda p: p[1], reverse=True):
        print(f"    [{score:.3f}] {chunk[:60]}")
    print("\n  hybrid order (Week 9, alpha=0.5):")
    for chunk, score in rerank(query, chunks, alpha=0.5):
        print(f"    [{score:.3f}] {chunk[:60]}")
