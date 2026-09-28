"""Week 9: tests for the lexical scorer and the hybrid blend. All offline."""

import pytest

from ribot.build_index import build_index, SAMPLE_DIR
from ribot.rerank import fuse, lexical_score, normalize, rerank

ENGINEERING_DIR = SAMPLE_DIR.parent / "sample_docs_engineering"


def test_lexical_score_is_query_word_coverage():
    assert lexical_score("torque limit", "the torque limit is 12 N-m") == 1.0
    assert lexical_score("torque limit", "the torque is high") == 0.5
    assert lexical_score("torque limit", "nothing relevant") == 0.0


def test_lexical_score_of_an_all_stopword_query_is_zero_not_a_crash():
    # "how do I do it" leaves no content words. Must not divide by zero.
    assert lexical_score("how do I do it", "any chunk at all") == 0.0


def test_normalize_puts_the_best_score_at_one():
    assert normalize([("a", 0.4), ("b", 0.2)]) == [("a", 1.0), ("b", 0.5)]


def test_normalize_survives_all_zero_scores():
    assert normalize([("a", 0.0), ("b", 0.0)]) == [("a", 0.0), ("b", 0.0)]


def test_normalize_returns_a_new_list():
    original = [("a", 0.4)]
    assert normalize(original) is not original
    assert original == [("a", 0.4)]


def test_fuse_lets_a_strong_lexical_match_overtake_a_stronger_vector_match():
    fused = fuse([("a", 1.0), ("b", 0.5)], [("b", 1.0), ("a", 0.0)], alpha=0.5)
    assert fused[0][0] == "b"


def test_alpha_one_is_pure_vector_ranking():
    fused = fuse([("a", 1.0), ("b", 0.5)], [("b", 1.0), ("a", 0.0)], alpha=1.0)
    assert [chunk for chunk, _ in fused] == ["a", "b"]


def test_alpha_zero_is_pure_lexical_ranking():
    fused = fuse([("a", 1.0), ("b", 0.5)], [("b", 1.0), ("a", 0.0)], alpha=0.0)
    assert [chunk for chunk, _ in fused] == ["b", "a"]


@pytest.mark.parametrize("alpha", [-0.1, 1.1])
def test_alpha_outside_zero_to_one_is_rejected(alpha):
    with pytest.raises(ValueError, match="alpha must be between 0 and 1"):
        fuse([("a", 1.0)], [("a", 1.0)], alpha=alpha)


def test_rerank_finds_the_chunk_that_contains_the_identifier():
    # The vector scorer prefers the chunk that TALKS about NCRs; the lexical scorer knows
    # which chunk actually CONTAINS NCR-2031. This is the failure hybrid retrieval fixes.
    talks_about = (
        "Any departure is documented as a nonconformance report (NCR) per QP-09.",
        0.35,
    )
    contains_it = (
        "## NCR-2031 - Finding: shaft binding, breakaway torque 0.9 N-m.",
        0.34,
    )
    reranked = rerank("NCR-2031", [talks_about, contains_it], alpha=0.5)
    assert reranked[0][0] == contains_it[0]


def test_search_hybrid_with_alpha_one_matches_plain_search():
    # The safety guarantee: hybrid retrieval is ADDITIVE. At alpha=1.0 it must reproduce
    # the Week 6 behavior exactly, so nothing Weeks 6-8 built can be silently changed.
    retriever = build_index(ENGINEERING_DIR, quiet=True)
    query = "What torque does WI-204 specify?"
    plain = [chunk for chunk, _ in retriever.search(query, k=3)]
    hybrid = [chunk for chunk, _ in retriever.search_hybrid(query, k=3, alpha=1.0)]
    assert plain == hybrid


def test_search_hybrid_rejects_a_nonpositive_k():
    retriever = build_index(ENGINEERING_DIR, quiet=True)
    with pytest.raises(ValueError, match="k must be positive"):
        retriever.search_hybrid("anything", k=0)
