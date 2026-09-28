"""Week 8: a structured tool-calling harness — `ribot/agent.py` in the production envelope.

`agent.py` teaches the loop with a text protocol: the model replies `SEARCH: ...` and we
parse the string. This module is the SAME loop wearing the grown-up envelope:

- each tool is DECLARED as a JSON schema (name, description, typed arguments),
- the model's request arrives as a typed `tool_use` block, not a magic string,
- the result goes back as a `tool_result` turn tied to that block's id,
- a registry maps tool names to your Python functions, so adding a tool is one entry.

These are exactly the shapes shipped in `data/tool_call_transcript.json` — now run by
code instead of read as data. Offline, `chat_tools` answers via the deterministic
`FakeToolLLM` (scripted, honestly: you study the loop, not model agency); with a real
key the tool choice is genuinely the model's. The loop below never changes.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

from .build_index import build_index
from .llm import ToolMessage, chat_tools
from .retriever import Retriever

HARNESS_SYSTEM = (
    "You are a research assistant for the user's document library. Use the provided "
    "tools when you need facts. Answer ONLY from tool results and cite them. If the "
    "results are empty or irrelevant, say you don't know based on the available "
    "documents."
)


@dataclass(frozen=True)
class Tool:
    """One tool = a schema the model sees + the Python function your loop runs."""

    name: str
    description: str
    input_schema: dict
    run: Callable[..., str]

    def declaration(self) -> dict:
        """The schema-only view sent to the model (it never sees `run`)."""
        return {
            "name": self.name,
            "description": self.description,
            "input_schema": self.input_schema,
        }


def make_tools(retriever: Retriever) -> list[Tool]:
    """The two-tool starter kit: search the docs, or list what's indexed.

    Your assignment adds a tool of YOUR own here — one entry, no loop changes.
    """
    return [
        Tool(
            name="search_docs",
            description=(
                "Search the indexed documents. Returns the top-k most relevant "
                "chunks with their source filenames."
            ),
            input_schema={
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "What to look up"},
                    "k": {"type": "integer", "description": "How many chunks to return"},
                },
                "required": ["query"],
            },
            run=lambda query, k=3: retriever.search_text(query, k=k),
        ),
        Tool(
            name="list_sources",
            description=(
                "List the source files currently in the document index. Takes no "
                "arguments. Use it when the user asks what the library contains."
            ),
            input_schema={"type": "object", "properties": {}},
            run=lambda: ", ".join(retriever.sources())
            or "The index has no listable sources.",
        ),
    ]


def run_harness(question: str, tools: list[Tool], max_iters: int = 4) -> str:
    """The bounded dispatch loop: ask -> maybe run a tool -> feed result back -> repeat.

    Same skeleton as `run_agent` in agent.py; only the envelope changed. Note what the
    registry buys you over `startswith("SEARCH:")`: an unknown tool name or malformed
    arguments become a clean tool_result the model can recover from, not a crash.
    """
    registry = {tool.name: tool for tool in tools}
    declarations = [tool.declaration() for tool in tools]
    messages: list[ToolMessage] = [
        {"role": "system", "content": HARNESS_SYSTEM},
        {"role": "user", "content": question},
    ]

    for _ in range(max_iters):  # the cap guarantees the loop always ends
        reply = chat_tools(messages, declarations)
        block = _first_tool_use(reply)
        if block is None:
            return _text_of(reply)

        messages.append(reply)
        messages.append(
            {
                "role": "user",
                "content": [
                    {
                        "type": "tool_result",
                        "tool_use_id": block["id"],
                        "content": _dispatch(registry, block),
                    }
                ],
            }
        )

    return "I couldn't finish within the step limit."


def _dispatch(registry: dict[str, Tool], block: dict) -> str:
    """Run the requested tool; turn every failure into text the model can read."""
    tool = registry.get(block["name"])
    if tool is None:
        return f"Unknown tool {block['name']!r}. Available tools: {sorted(registry)}."
    try:
        return tool.run(**block.get("input", {}))
    except TypeError as err:
        return f"Bad arguments for {block['name']!r}: {err}"


def _first_tool_use(reply: ToolMessage) -> dict | None:
    """The reply's tool_use block, or None when the model answered with text."""
    content = reply.get("content")
    blocks = content if isinstance(content, list) else []
    for block in blocks:
        if isinstance(block, dict) and block.get("type") == "tool_use":
            return block
    return None


def _text_of(reply: ToolMessage) -> str:
    """The reply's text, whichever shape it arrived in."""
    content = reply.get("content")
    if isinstance(content, str):
        return content
    blocks = content if isinstance(content, list) else []
    return " ".join(
        str(block.get("text", ""))
        for block in blocks
        if isinstance(block, dict) and block.get("type") == "text"
    ).strip()


def main() -> None:
    retriever = build_index()
    tools = make_tools(retriever)
    for question in ("How do I reset my password?", "Which documents do you have?"):
        print(f"Q: {question}\nA: {run_harness(question, tools)}\n")


if __name__ == "__main__":  # `python -m ribot.harness`
    main()
