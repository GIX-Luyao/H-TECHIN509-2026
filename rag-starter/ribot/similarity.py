"""Week 5: cosine similarity — first by hand in pure Python, then with NumPy.

Cosine similarity measures the angle between two vectors:
    cos(a, b) = (a . b) / (|a| * |b|)
Values near 1.0 mean "point the same way" = similar meaning.
"""

from __future__ import annotations

import math
from typing import Sequence

Vector = Sequence[float]


def dot(a: Vector, b: Vector) -> float:
    """Dot product: multiply matching elements and add them up."""
    return sum(x * y for x, y in zip(a, b))


def magnitude(a: Vector) -> float:
    """Length of a vector: sqrt of the sum of squares."""
    return math.sqrt(sum(x * x for x in a))


def cosine_similarity(a: Vector, b: Vector) -> float:
    """Pure-Python cosine similarity. Returns 0.0 if either vector is all zeros."""
    denom = magnitude(a) * magnitude(b)
    if denom == 0:
        return 0.0
    return dot(a, b) / denom


def cosine_similarity_numpy(a: Vector, b: Vector) -> float:
    """The same thing with NumPy — the 'real' path you'll use once data gets big.

    Kept side by side so you can see they agree.
    """
    import numpy as np

    va, vb = np.asarray(a, dtype=float), np.asarray(b, dtype=float)
    denom = float(np.linalg.norm(va) * np.linalg.norm(vb))
    if denom == 0:
        return 0.0
    return float(va @ vb / denom)


if __name__ == "__main__":  # `python -m ribot.similarity`
    cat = [1.0, 0.9, 0.1]
    kitten = [0.9, 1.0, 0.0]
    invoice = [0.1, 0.0, 1.0]
    print("cat ~ kitten:", round(cosine_similarity(cat, kitten), 3))
    print("cat ~ invoice:", round(cosine_similarity(cat, invoice), 3))
