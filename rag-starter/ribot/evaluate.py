"""Week 9: score a retrieval setup, so a change can be kept or reverted on evidence.

Week 6 taught you hits@3: for each golden question, does the file that can answer it show
up in the top 3 chunks? Week 9 keeps that number — and adds a stricter one, because on a
three-file corpus hits@3 is *easy*. Guessing gets you a decent score, and a change that
genuinely helps can leave the number untouched.

    hits@k        - did a chunk from the RIGHT FILE come back?      (Week 6, coarse)
    answerable@k  - did a chunk containing the ACTUAL ANSWER come back?  (Week 9, strict)

`answerable@k` is the one that moves when you fix something real, because retrieving the
right file is not the same as retrieving the paragraph that answers the question. Neither
number tells you whether the model's *answer* was faithful to the chunk — that is the
Week 10 citation spot-check, and no metric in this file is a substitute for it.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Callable, Iterable, Sequence

GOLDEN_PATH = Path(__file__).resolve().parent.parent / "data" / "golden_set.json"

# A search variant: (question, history) -> ranked [(chunk, score), ...]
SearchFn = Callable[[str, Sequence], list[tuple[str, float]]]
SourceFn = Callable[[str], str]


def load_golden_set(corpus: str | None = None, path: Path = GOLDEN_PATH) -> list[dict]:
    """Load the shared golden set, optionally filtered to one corpus.

    Raises FileNotFoundError with an actionable message rather than a bare traceback,
    because "where is my golden set" is the most common way this fails.
    """
    if not path.exists():
        raise FileNotFoundError(
            f"No golden set at {path}. It ships with rag-starter — if it is missing, "
            "pull the latest starter repo, or point `path` at your own JSON file with "
            "the same shape (see data/golden_set.json)."
        )
    questions = json.loads(path.read_text(encoding="utf-8"))["questions"]
    if corpus is None:
        return questions
    return [q for q in questions if q["corpus"] == corpus]


def evaluate(
    golden: Iterable[dict],
    search_fn: SearchFn,
    source_of: SourceFn,
    k: int = 3,
) -> dict:
    """Run every scorable golden question through `search_fn` and count both metrics.

    Out-of-corpus questions (expected_source is null) are counted but NOT scored here:
    "the right file came back" is meaningless when no file is right. What they are for is
    the refusal check in Week 10 — a retriever cannot pass them, only a guardrail can.

    Returns a plain dict (nothing is mutated in place) with per-question detail so you can
    look at the failures instead of just the average. Looking at the failures is the job.
    """
    scorable = [q for q in golden if q.get("expected_source")]
    unanswerable = [q for q in golden if not q.get("expected_source")]

    per_question = []
    for item in scorable:
        hits = search_fn(item["question"], item.get("history", []))[:k]
        chunks = [chunk for chunk, _ in hits]
        sources = [source_of(chunk) for chunk in chunks]
        snippet = item.get("expected_snippet") or ""
        per_question.append(
            {
                "id": item["id"],
                "kind": item.get("kind", "plain"),
                "question": item["question"],
                "hit": item["expected_source"] in sources,
                "answerable": bool(snippet)
                and any(snippet in chunk for chunk in chunks),
                "top_source": sources[0] if sources else None,
                "expected_source": item["expected_source"],
            }
        )

    total = len(per_question) or 1  # guard: never divide by zero on an empty golden set
    return {
        "k": k,
        "scored": len(per_question),
        "unanswerable_skipped": len(unanswerable),
        "hits": sum(row["hit"] for row in per_question),
        "answerable": sum(row["answerable"] for row in per_question),
        "hits_at_k": sum(row["hit"] for row in per_question) / total,
        "answerable_at_k": sum(row["answerable"] for row in per_question) / total,
        "per_question": per_question,
    }


def ablation(
    variants: dict[str, SearchFn],
    golden: Iterable[dict],
    source_of: SourceFn,
    k: int = 3,
) -> dict[str, dict]:
    """Score several search variants over the SAME golden set. Order is preserved.

    This is the shape of every honest experiment you will run: change one thing, re-run
    the identical questions, compare. Keep the change if the number moves; revert it if
    it does not. `regressions()` finds the questions a change broke.
    """
    frozen = list(golden)  # evaluate once per variant over identical questions
    return {name: evaluate(frozen, fn, source_of, k=k) for name, fn in variants.items()}


def regressions(
    baseline: dict, candidate: dict, metric: str = "answerable"
) -> list[dict]:
    """Questions the candidate got WRONG that the baseline got right.

    An average can improve while individual questions break. This is the list you read
    out loud before deciding to keep a change — "it went from 9 to 11, and here are the
    two it broke" is an engineering result. "It went up" is a vibe.
    """
    before = {row["id"]: row for row in baseline["per_question"]}
    return [
        {"id": row["id"], "question": row["question"], "kind": row["kind"]}
        for row in candidate["per_question"]
        if before.get(row["id"], {}).get(metric) and not row[metric]
    ]


def format_table(results: dict[str, dict]) -> str:
    """Render ablation results as a table. Formatting only — computes nothing."""
    header = f"{'variant':<22} {'hits@k':>8} {'answerable@k':>14}   detail"
    lines = [header, "-" * len(header)]
    for name, res in results.items():
        lines.append(
            f"{name:<22} {res['hits_at_k']:>7.0%} {res['answerable_at_k']:>14.0%}"
            f"   {res['hits']}/{res['scored']} files, "
            f"{res['answerable']}/{res['scored']} answers  (k={res['k']})"
        )
    skipped = next(iter(results.values()))["unanswerable_skipped"] if results else 0
    if skipped:
        lines.append(
            f"\n({skipped} out-of-corpus question(s) not scored here — they test the "
            "refusal guardrail, not retrieval. See Week 10.)"
        )
    return "\n".join(lines)
