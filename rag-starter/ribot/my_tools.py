"""YOUR tools — the one file you edit to give the assistant a new ability.

A tool is two things glued together:
  1. a plain Python function that returns a string, and
  2. a `Tool(...)` entry describing it, so the model knows when and how to call it.

Add your entry to `MY_TOOLS` and the assistant picks it up automatically: no loop
changes. `current_date` below is a complete working example. It exists because a model
genuinely cannot know today's date, which is the whole reason tools exist: to give the
model facts or abilities it does not have on its own.

Rules of thumb:
- Return a short string. That string is all the model sees.
- Write the `description` for the model: say WHEN to use the tool, not just what it does.
- Read-only tools are safe. A tool that changes something (writes a file, sends a
  message) belongs behind a confirmation. See `gated()` in ribot/toolbox.py.

Offline note: the scripted FakeToolLLM only ever picks `search_docs` or `list_sources`,
so test your function directly with pytest. With a real model (class key or Ollama),
run `python -m ribot.agent_eval` to see whether it actually picks your tool.
"""

from __future__ import annotations

from datetime import date

from .harness import Tool


def current_date() -> str:
    """Today's date as YYYY-MM-DD."""
    return date.today().isoformat()


MY_TOOLS: list[Tool] = [
    Tool(
        name="current_date",
        description=(
            "Get today's date (YYYY-MM-DD). Use it whenever the user asks about today, "
            "deadlines, or how many days until something."
        ),
        input_schema={"type": "object", "properties": {}},
        run=current_date,
    ),
    # TODO (Week 8): add ONE tool for your own workflow. Template:
    #
    # Tool(
    #     name="word_count",
    #     description="Count the words in a piece of text. Use it when the user asks "
    #                 "how long a draft is.",
    #     input_schema={
    #         "type": "object",
    #         "properties": {"text": {"type": "string", "description": "The text"}},
    #         "required": ["text"],
    #     },
    #     run=lambda text: f"{len(text.split())} words",
    # ),
]
