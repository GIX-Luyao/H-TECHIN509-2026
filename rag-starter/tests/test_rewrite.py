"""Week 9: tests for turning a follow-up into a standalone question. All offline."""

import pytest

from ribot.rewrite import needs_rewrite, standalone_query

HISTORY = [
    {"role": "user", "content": "What is the vacation carryover limit?"},
    {"role": "assistant", "content": "Up to 5 unused days roll over."},
]


@pytest.mark.parametrize(
    "question",
    [
        "Can those roll over?",
        "How many after that?",
        "What about them?",
        "For how long?",
    ],
)
def test_pronoun_questions_need_a_rewrite(question):
    assert needs_rewrite(question) is True


@pytest.mark.parametrize(
    "question",
    [
        "What is the vacation carryover limit?",
        "What is 2FA?",  # short, but complete on its own — must NOT be dragged into history
        "What torque does WI-204 specify?",
    ],
)
def test_complete_questions_are_left_alone(question):
    assert needs_rewrite(question) is False
    assert standalone_query(HISTORY, question) == question


def test_rewrite_borrows_the_previous_user_turn():
    rewritten = standalone_query(HISTORY, "Can those roll over?")
    assert "vacation carryover limit" in rewritten
    assert "Can those roll over?" in rewritten


def test_assistant_turns_are_not_borrowed():
    # The bot's own words are not the subject the user is following up on.
    rewritten = standalone_query(HISTORY, "Can those roll over?")
    assert "Up to 5 unused days" not in rewritten


def test_no_history_means_no_rewrite():
    # Nothing to borrow from: return the question untouched rather than inventing context.
    assert standalone_query([], "Can those roll over?") == "Can those roll over?"


def test_plain_string_history_is_accepted():
    # Some students keep history as a list of question strings; both shapes must work.
    rewritten = standalone_query(
        ["What is the carryover limit?"], "Can those roll over?"
    )
    assert "carryover limit" in rewritten


def test_empty_question_is_not_rewritten():
    assert needs_rewrite("") is False
    assert standalone_query(HISTORY, "") == ""


def test_llm_path_works_offline_through_fakellm(monkeypatch):
    # No key -> FakeLLM answers the rewrite protocol, so the plumbing is testable offline.
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.delenv("RIBOT_LLM", raising=False)
    rewritten = standalone_query(HISTORY, "Can those roll over?", use_llm=True)
    assert "vacation carryover limit" in rewritten
    assert "Can those roll over?" in rewritten
