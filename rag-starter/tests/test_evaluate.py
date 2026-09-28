"""Week 9: tests for the shared evaluation harness. All offline."""

import pytest

from ribot.evaluate import (
    ablation,
    evaluate,
    format_table,
    load_golden_set,
    regressions,
)

# A tiny fake index: three "chunks" and a source lookup, so these tests measure the
# HARNESS rather than the retriever.
CHUNKS = {
    "PTO rolls over up to a maximum of 5 unused days.": "hr_policy.md",
    "Reset links are valid for 30 minutes.": "help_center.md",
    "The Team plan is 8 dollars per user.": "product_faq.md",
}
GOLDEN = [
    {
        "id": "g1",
        "kind": "plain",
        "history": [],
        "question": "carryover",
        "expected_source": "hr_policy.md",
        "expected_snippet": "maximum of 5 unused days",
    },
    {
        "id": "g2",
        "kind": "plain",
        "history": [],
        "question": "reset",
        "expected_source": "help_center.md",
        "expected_snippet": "valid for 30 minutes",
    },
    {
        "id": "oob",
        "kind": "out-of-corpus",
        "history": [],
        "question": "parental leave",
        "expected_source": None,
        "expected_snippet": None,
    },
]


def source_of(chunk):
    return CHUNKS.get(chunk, "unknown source")


def perfect_search(question, history):
    """Returns the right chunk first for both scorable questions."""
    wanted = "PTO" if question == "carryover" else "Reset"
    ordered = sorted(CHUNKS, key=lambda c: not c.startswith(wanted))
    return [(chunk, 1.0) for chunk in ordered]


def useless_search(question, history):
    """Always returns the same wrong chunk."""
    return [("The Team plan is 8 dollars per user.", 1.0)]


def test_a_perfect_retriever_scores_one_on_both_metrics():
    result = evaluate(GOLDEN, perfect_search, source_of, k=3)
    assert result["hits_at_k"] == 1.0
    assert result["answerable_at_k"] == 1.0


def test_out_of_corpus_questions_are_skipped_not_scored():
    # Scoring "the right file came back" is meaningless when no file is right.
    result = evaluate(GOLDEN, perfect_search, source_of, k=3)
    assert result["scored"] == 2
    assert result["unanswerable_skipped"] == 1
    assert [row["id"] for row in result["per_question"]] == ["g1", "g2"]


def test_a_useless_retriever_scores_zero_without_crashing():
    result = evaluate(GOLDEN, useless_search, source_of, k=3)
    assert result["hits_at_k"] == 0.0
    assert result["answerable_at_k"] == 0.0


def test_k_truncates_the_result_list():
    # k=1 sees only the top chunk, so the second question's answer is out of reach.
    at_one = evaluate(GOLDEN, useless_search, source_of, k=1)
    assert at_one["k"] == 1
    assert at_one["hits"] == 0


def test_right_file_can_hit_while_the_answer_is_still_missing():
    # The whole reason Week 9 adds answerable@k: the file is right, the paragraph is not.
    golden = [
        {
            "id": "coarse",
            "kind": "plain",
            "history": [],
            "question": "carryover",
            "expected_source": "hr_policy.md",
            "expected_snippet": "text that is nowhere in the chunk",
        }
    ]
    result = evaluate(golden, perfect_search, source_of, k=3)
    assert result["hits_at_k"] == 1.0
    assert result["answerable_at_k"] == 0.0


def test_evaluate_does_not_mutate_the_golden_set():
    before = [dict(item) for item in GOLDEN]
    evaluate(GOLDEN, perfect_search, source_of, k=3)
    assert GOLDEN == before


def test_ablation_scores_every_variant_over_the_same_questions():
    results = ablation(
        {"good": perfect_search, "bad": useless_search}, GOLDEN, source_of, k=3
    )
    assert list(results) == ["good", "bad"]
    assert results["good"]["answerable"] == 2
    assert results["bad"]["answerable"] == 0


def test_regressions_lists_what_a_change_broke():
    good = evaluate(GOLDEN, perfect_search, source_of, k=3)
    bad = evaluate(GOLDEN, useless_search, source_of, k=3)
    broke = regressions(good, bad)
    assert {row["id"] for row in broke} == {"g1", "g2"}
    # And nothing "regressed" when the change was an improvement.
    assert regressions(bad, good) == []


def test_format_table_reports_both_metrics_and_the_skipped_count():
    results = ablation({"good": perfect_search}, GOLDEN, source_of, k=3)
    table = format_table(results)
    assert "hits@k" in table and "answerable@k" in table
    assert "out-of-corpus" in table


def test_the_shipped_golden_set_loads_and_is_well_formed():
    everything = load_golden_set()
    assert len(everything) >= 12
    for item in everything:
        assert {"id", "corpus", "question", "expected_source", "kind"} <= set(item)
        # An answerable question needs a snippet to check; an unanswerable one must not
        # have one, or the harness would score a question that has no right answer.
        assert bool(item["expected_source"]) == bool(item["expected_snippet"])


def test_golden_set_can_be_filtered_to_one_corpus():
    engineering = load_golden_set("sample_docs_engineering")
    assert engineering
    assert {item["corpus"] for item in engineering} == {"sample_docs_engineering"}


def test_a_missing_golden_set_says_what_to_do(tmp_path):
    with pytest.raises(FileNotFoundError, match="No golden set at"):
        load_golden_set(path=tmp_path / "nope.json")
