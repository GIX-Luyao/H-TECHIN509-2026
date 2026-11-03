"""Weeks 8-10: the assistant's toolbox — read tools, action tools, and YOUR tools.

`harness.make_tools()` is the two-tool starter kit. This toolbox is the one the Week 9
terminal assistant uses:

- `search_docs`: cited search with a score floor, so weak matches become "no evidence"
  and the assistant can honestly say "I don't know",
- `list_sources`: what's in the index,
- `remember`: save a note to assistant_memory.md (an ACTION, so it is confirm-gated),
- `save_draft`: write a draft to drafts/ (an ACTION, so it is confirm-gated),
- plus every tool you add in ribot/my_tools.py.

Why the confirmation gate? Retrieved documents are untrusted text. A poisoned document
can tell the model "call save_draft with ..." and a real model may obey. Asking the human
before any action runs is the mitigation that still works when the prompt-level defenses
fail. It is a real guard, not a speed bump, but only for the tools that sit behind it.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Callable, Sequence

from .harness import Tool
from .memory import MEMORY_PATH, save_note
from .my_tools import MY_TOOLS
from .retriever import Retriever

DRAFTS_DIR = Path(__file__).resolve().parent.parent / "drafts"

# Matches scoring below this count as "nothing relevant found". Tune it on your corpus:
# run your golden set plus a few out-of-scope questions and pick a floor between them.
# The offline fallback embedder and real embedding models score on different scales.
MIN_SCORE = 0.2
MAX_K = 10
MAX_DRAFT_CHARS = 5000

ConfirmFn = Callable[[str], bool]


def deny_all(_description: str) -> bool:
    """The safe default confirmation: say no to every action."""
    return False


def gated(confirm: ConfirmFn, description: str, action: Callable[[], str]) -> str:
    """Run `action` only if the human says yes; otherwise tell the model it was declined."""
    if not confirm(description):
        return f"The user declined: {description}. Do not retry; tell the user instead."
    return action()


def _clamp_k(k: object) -> int:
    """Models sometimes send k as a string or a silly number; keep it in 1..MAX_K."""
    try:
        value = int(k)
    except (TypeError, ValueError):
        value = 3
    return max(1, min(value, MAX_K))


def search_cited(
    retriever: Retriever, query: str, k: object = 3, min_score: float = MIN_SCORE
) -> str:
    """Top chunks, each labeled '[source: file.md]', or '' when nothing clears the floor."""
    hits = retriever.search(str(query), k=_clamp_k(k))
    relevant = [(chunk, score) for chunk, score in hits if score >= min_score]
    return "\n---\n".join(
        f"[source: {retriever.source_of(chunk)}] {chunk}" for chunk, _ in relevant
    )


def _slug(title: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-")[:60]


def _write_draft(drafts_dir: Path, title: str, body: str) -> str:
    slug = _slug(title)
    if not slug:
        return "Not saved: the draft needs a title with letters or numbers."
    if len(body) > MAX_DRAFT_CHARS:
        return f"Not saved: the draft is longer than {MAX_DRAFT_CHARS} characters."
    path = Path(drafts_dir) / f"{slug}.md"
    if path.exists():
        return f"Not saved: {path.name} already exists. Pick a different title."
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(f"# {title.strip()}\n\n{body.strip()}\n", encoding="utf-8")
    return f"Saved draft to drafts/{path.name}."


def _remember(memory_path: Path, note: str) -> str:
    try:
        return f"Saved to memory: {save_note(note, memory_path)}"
    except ValueError as err:
        return f"Not saved: {err}."


def _read_tools(retriever: Retriever) -> list[Tool]:
    return [
        Tool(
            name="search_docs",
            description=(
                "Search the user's indexed documents. Returns the most relevant chunks, "
                "each labeled with its source file, or nothing if no chunk is relevant. "
                "Use it for any factual question about the user's work."
            ),
            input_schema={
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "What to look up"},
                    "k": {"type": "integer", "description": "How many chunks (1-10)"},
                },
                "required": ["query"],
            },
            run=lambda query, k=3: search_cited(retriever, query, k),
        ),
        Tool(
            name="list_sources",
            description=(
                "List the source files in the document index. Takes no arguments. Use it "
                "when the user asks what documents or topics you have."
            ),
            input_schema={"type": "object", "properties": {}},
            run=lambda: ", ".join(retriever.sources())
            or "The index has no listable sources.",
        ),
    ]


def _action_tools(
    confirm: ConfirmFn, memory_path: Path, drafts_dir: Path
) -> list[Tool]:
    return [
        Tool(
            name="remember",
            description=(
                "Save one short, durable note about the user's preferences or workflow "
                "to long-term memory. Only use it when the user asks you to remember "
                "something. The user must confirm before it is saved."
            ),
            input_schema={
                "type": "object",
                "properties": {"note": {"type": "string", "description": "The note"}},
                "required": ["note"],
            },
            run=lambda note: gated(
                confirm,
                f"save to memory: {note!r}",
                lambda: _remember(memory_path, note),
            ),
        ),
        Tool(
            name="save_draft",
            description=(
                "Save a draft (an email reply, a summary, meeting notes) as a markdown "
                "file. Only use it when the user asks for a draft to be saved. The user "
                "must confirm before it is written."
            ),
            input_schema={
                "type": "object",
                "properties": {
                    "title": {"type": "string", "description": "Short title"},
                    "body": {"type": "string", "description": "The draft text"},
                },
                "required": ["title", "body"],
            },
            run=lambda title, body: gated(
                confirm,
                f"write draft {title!r} ({len(body)} characters)",
                lambda: _write_draft(drafts_dir, title, body),
            ),
        ),
    ]


def make_assistant_tools(
    retriever: Retriever,
    confirm: ConfirmFn = deny_all,
    memory_path: Path = MEMORY_PATH,
    drafts_dir: Path = DRAFTS_DIR,
    extra: Sequence[Tool] | None = None,
) -> list[Tool]:
    """Every tool the assistant may call: read, action (confirm-gated), then yours."""
    student_tools = MY_TOOLS if extra is None else extra
    return [
        *_read_tools(retriever),
        *_action_tools(confirm, memory_path, drafts_dir),
        *student_tools,
    ]
