"""Week 8: a tiny single-tool agent.

An 'agent' here is just a for-loop you already know, plus one rule: the model may reply
with a line that starts with `SEARCH:` to look something up. Our code runs the search,
feeds the results back, and loops until the model gives a normal answer.

This protocol works with BOTH the real model and the offline FakeLLM, so no special
function-calling API is required to learn the idea.

This file is the Week 8 ON-RAMP and the fallback: trace it first, then build the same
loop in the production envelope in `ribot/harness.py` (tools as JSON schemas, a
registry, typed `tool_use`/`tool_result` blocks). If you hit the week's time cap, this
single-tool version is still a full pass — see the Module 8 assignment.
"""

from __future__ import annotations

from .build_index import build_index
from .llm import chat
from .retriever import Retriever

AGENT_SYSTEM = (
    "You are a research assistant with ONE tool: a document search.\n"
    "When you need facts from the user's documents, reply with a line that starts with "
    "SEARCH: followed by your query, and nothing else.\n"
    "After you receive a line beginning with 'SEARCH RESULTS:', answer the user's question "
    "using ONLY those results, and cite them. If the results are empty or irrelevant, say "
    "you don't know based on the available documents."
)


def run_agent(question: str, retriever: Retriever, max_iters: int = 3) -> str:
    """Loop: ask the model; if it requests a SEARCH, run it and feed results back."""
    messages = [
        {"role": "system", "content": AGENT_SYSTEM},
        {"role": "user", "content": question},
    ]

    for _ in range(max_iters):  # the cap guarantees the loop always ends
        reply = chat(messages)
        if reply.strip().startswith("SEARCH:"):
            query = reply.split("SEARCH:", 1)[1].strip()
            found = retriever.search_text(query, k=3)
            messages.append({"role": "assistant", "content": reply})
            messages.append({"role": "user", "content": f"SEARCH RESULTS: {found}"})
            continue
        return reply

    return "I couldn't finish within the step limit."


def main() -> None:
    retriever = build_index()
    question = "How do I reset my password?"
    print(f"Q: {question}\nA: {run_agent(question, retriever)}")


if __name__ == "__main__":  # `python -m ribot.agent`
    main()
