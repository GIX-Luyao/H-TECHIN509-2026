"""Week 9 faded exercise: make a follow-up question searchable on its own.

Fill in each # TODO, then check your work by running the real tests:

    python starters/week9_rewrite.py     # your own quick look
    pytest tests/test_rewrite.py         # the same tests that grade ribot/rewrite.py

Reference (read it AFTER you try): ribot/rewrite.py
"""

from __future__ import annotations

import sys
from pathlib import Path

# Make `ribot` importable when this file is run directly from the repo root.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

# The same tokenizer fallback_embed uses. Imported after the path fix, on purpose.
from ribot.embeddings import _tokens  # noqa: E402

FOLLOWUP_STARTS = ("what about", "how about", "and what", "for how long", "can those")


def last_user_question(history: list[dict]) -> str:
    """Return the most recent USER message in the history, or "" if there is none.

    History is the Week-3 list of dicts: [{"role": "user", "content": "..."}, ...].
    Careful: the assistant's replies are in there too, and you do not want those.
    """
    # TODO 1: walk the history, keep only role == "user", return the LAST one's content.
    return ""  # replace


def needs_rewrite(question: str) -> bool:
    """True when this question probably cannot be searched on its own."""
    text = question.strip().lower()
    if not text:
        return False
    # TODO 2: return True if `text` starts with any of FOLLOWUP_STARTS.
    #         Hint: str.startswith accepts a tuple.

    # TODO 3: return True if one content word or fewer survives stopword stripping.
    #         Hint: len(_tokens(text)) <= 1
    return False  # replace


def standalone_query(history: list[dict], question: str) -> str:
    """Return a question that can be searched without the conversation around it."""
    previous = last_user_question(history)
    # TODO 4: if there is no previous question, or this question does not need a rewrite,
    #         return `question` unchanged. Otherwise return the two joined by a space.
    return question  # replace


if __name__ == "__main__":
    history = [
        {"role": "user", "content": "What is the vacation carryover limit?"},
        {"role": "assistant", "content": "Up to 5 unused days roll over."},
    ]
    checks = [
        (
            "Can those roll over?",
            True,
            "What is the vacation carryover limit? Can those roll over?",
        ),
        ("What is 2FA?", False, "What is 2FA?"),
    ]
    for question, should_rewrite, expected in checks:
        flagged = needs_rewrite(question)
        rewritten = standalone_query(history, question)
        ok = flagged == should_rewrite and rewritten == expected
        print(f"[{'OK ' if ok else 'XX '}] {question!r}")
        print(f"        needs_rewrite -> {flagged} (want {should_rewrite})")
        print(f"        rewrite       -> {rewritten!r}")
    print("\nAll OK? Now run: pytest tests/test_rewrite.py")
