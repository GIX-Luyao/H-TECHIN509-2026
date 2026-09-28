"""Week 7: example tests for cosine similarity."""

from ribot.similarity import cosine_similarity


def test_identical_vectors_are_similarity_one():
    assert cosine_similarity([1.0, 2.0, 3.0], [1.0, 2.0, 3.0]) == 1.0


def test_orthogonal_vectors_are_zero():
    assert cosine_similarity([1.0, 0.0], [0.0, 1.0]) == 0.0


def test_zero_vector_is_safe():
    # edge case: must not divide by zero
    assert cosine_similarity([0.0, 0.0], [1.0, 1.0]) == 0.0


def test_related_phrases_more_similar_than_unrelated():
    from ribot.embeddings import fallback_embed

    related = cosine_similarity(fallback_embed("reset password"), fallback_embed("forgot password"))
    unrelated = cosine_similarity(fallback_embed("reset password"), fallback_embed("pizza recipe"))
    assert related > unrelated
