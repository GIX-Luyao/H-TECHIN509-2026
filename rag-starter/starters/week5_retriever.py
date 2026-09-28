"""Week 5 faded exercise: cosine similarity + return the nearest chunk.

Fill in each # TODO. Reference: ribot/similarity.py, ribot/build_index.py
Run:  python starters/week5_retriever.py
"""

from __future__ import annotations

import math

from ribot.embeddings import get_embedder

embed = get_embedder()


def cosine_similarity(a: list[float], b: list[float]) -> float:
    # TODO 1: dot product of a and b (sum of a[i]*b[i])
    dot = 0.0  # replace
    # TODO 2: magnitude of a, and magnitude of b
    mag_a = 0.0  # replace with sqrt(sum of squares)
    mag_b = 0.0  # replace
    if mag_a * mag_b == 0:
        return 0.0
    # TODO 3: return dot / (mag_a * mag_b)
    return 0.0


def nearest_chunk(query: str, chunks: list[str]) -> str:
    query_vec = embed(query)
    best_chunk, best_score = "", -1.0
    for chunk in chunks:
        score = cosine_similarity(query_vec, embed(chunk))
        # TODO 4: if this score is the best so far, remember this chunk and score
    return best_chunk


if __name__ == "__main__":
    library = [
        "Click 'Forgot password' to reset your password.",
        "Full-time employees get 15 vacation days per year.",
        "The Team plan costs 8 dollars per user per month.",
    ]
    print(nearest_chunk("how do I change my password?", library))
