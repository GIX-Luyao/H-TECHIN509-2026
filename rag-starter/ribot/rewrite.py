"""Week 9: make a follow-up question searchable on its own.

Week 3 gave the assistant a history. Week 6 gave it a retriever. Nobody ever joined
them — so the retriever still sees only the latest question:

    "What is the vacation carryover limit?"   -> retrieval works
    "Can those roll over?"                    -> two words survive, retrieval misses

`standalone_query(history, question)` closes that gap: it rewrites a follow-up into a
question that stands on its own, *then* you search with the rewrite.

Two paths, on purpose:
  - the **heuristic** (default): free, instant, deterministic, and testable.
  - the **LLM rewrite** (`use_llm=True`): smarter, and costs one extra model call, extra
    latency, and a brand-new failure mode — a rewrite that changes what you asked.
Which one wins is a measurement, not an opinion. Week 9's ablation is where you settle it.
"""

from __future__ import annotations

from typing import Sequence

from .embeddings import _tokens
from .llm import REWRITE_PROTOCOL_MARKER, chat

Turn = dict[str, str]

# Openers that almost always lean on the turn before them. Heuristics, not laws —
# `needs_rewrite` is deliberately easy to read, argue with, and change.
FOLLOWUP_STARTS = (
    "what about",
    "how about",
    "and what",
    "and how",
    "and for",
    "what else",
    "what if",
    "why not",
    "is it",
    "are they",
    "does it",
    "do they",
    "can those",
    "for how long",
)

# A question carrying this few content words has almost nothing left to embed after
# stopwords are stripped. One is a judgement call, and it is deliberately CAUTIOUS: at 2,
# "What is 2FA?" gets flagged as a follow-up and dragged toward whatever came before it.
# Raising this makes the rewrite fire more often, which helps follow-ups and hurts plain
# questions. Change it and re-run the Week 9 ablation — that is the whole point.
MIN_CONTENT_WORDS = 1

_REWRITE_SYSTEM = (
    "You rewrite a follow-up question so it can be understood on its own, with no "
    "conversation history. Keep the user's meaning and wording where you can. Add only "
    "the subject the follow-up is leaning on. Do not answer the question. "
    f"{REWRITE_PROTOCOL_MARKER}"
)


def _user_turns(history: Sequence[Turn | str]) -> list[str]:
    """Pull the user's messages out of a history, tolerating both shapes we hand out.

    The course's canonical history is a list of {"role", "content"} dicts (Week 3). Some
    students keep a plain list of question strings instead; both are accepted here rather
    than crashing on someone's perfectly reasonable variation.
    """
    turns: list[str] = []
    for item in history or []:
        if isinstance(item, str):
            turns.append(item)
        elif isinstance(item, dict) and item.get("role") == "user":
            turns.append(str(item.get("content", "")))
    return [t for t in turns if t.strip()]


def needs_rewrite(question: str) -> bool:
    """True when this question probably cannot be searched on its own.

    Two cheap signals: it opens like a follow-up, or almost nothing survives stopword
    stripping. `_tokens` is the same tokenizer `fallback_embed` uses, so this asks the
    honest question — *is there anything here for the embedder to work with?*

    >>> needs_rewrite("What is the vacation carryover limit?")
    False
    >>> needs_rewrite("What is 2FA?")
    False
    >>> needs_rewrite("Can those roll over?")
    True
    >>> needs_rewrite("How many after that?")
    True
    """
    text = question.strip().lower()
    if not text:
        return False
    if text.startswith(FOLLOWUP_STARTS):
        return True
    return len(_tokens(text)) <= MIN_CONTENT_WORDS


def _llm_rewrite(previous: str, question: str) -> str:
    """Ask the model to spell the follow-up out. One extra call, so one extra failure mode."""
    messages = [
        {"role": "system", "content": _REWRITE_SYSTEM},
        {
            "role": "user",
            "content": (
                f"Earlier question: {previous}\n"
                f"Follow-up question: {question}\n"
                "Rewrite the follow-up as a standalone question."
            ),
        },
    ]
    rewritten = chat(messages).strip()
    # If the model returns nothing usable, fall back rather than searching for "".
    return rewritten or f"{previous} {question}"


def standalone_query(
    history: Sequence[Turn | str],
    question: str,
    use_llm: bool = False,
) -> str:
    """Return a question that can be searched without the conversation around it.

    Leaves the question untouched when there is no history to borrow from, or when it
    already stands on its own — the common case, and the one you must not make worse.

    >>> standalone_query([{"role": "user", "content": "What is the carryover limit?"}],
    ...                  "Can those roll over?")
    'What is the carryover limit? Can those roll over?'
    """
    previous_turns = _user_turns(history)
    if not previous_turns or not needs_rewrite(question):
        return question
    previous = previous_turns[-1]
    if use_llm:
        return _llm_rewrite(previous, question)
    # The heuristic: hand the retriever both turns and let the embedder see the subject.
    return f"{previous} {question}"


if __name__ == "__main__":  # `python -m ribot.rewrite`
    history = [{"role": "user", "content": "What is the vacation carryover limit?"}]
    for follow_up in (
        "Can those roll over?",
        "How many after that?",
        "What about the Business plan?",
        "What is 2FA?",
    ):
        print(
            f"{follow_up!r:28} needs_rewrite={needs_rewrite(follow_up)!s:5} "
            f"-> {standalone_query(history, follow_up)!r}"
        )
