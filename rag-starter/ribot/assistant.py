"""Week 9: the terminal assistant — your Demo Day front door.

Every part is something you already wrote:

    (A) build_index()        your Week 6 retriever, built ONCE before the loop
    (B) history = []         your Week 3 list of {role, content} dicts
    (C) while True / /exit   your Week 3 command loop
    (D) input("you > ")      the chat box is just input()
    (E) standalone_query()   Week 9: turn "Can those roll over?" into a searchable question
    (F) run_harness_turn()   your Week 8 agent loop, now with history, memory and a trace

Commands: /trace shows which tools the agent called, /remember <note> saves a note to
assistant_memory.md, /exit quits. When the agent wants to take an action (save a draft,
save a memory), you are asked to confirm first.

No agent? Swap line (F) for your Week 7 `ChatBot().reply_grounded(query, retriever)`.
Both count fully on Demo Day.
"""

from __future__ import annotations

from pathlib import Path

from .agent_loop import AgentTurn, run_harness_turn
from .build_index import build_index
from .memory import MEMORY_PATH, load_memory, save_note
from .rewrite import standalone_query
from .toolbox import DRAFTS_DIR, make_assistant_tools

GREETING = (
    "ribot — ask my documents.\n"
    "Commands: /trace (show tool calls)  /remember <note>  /exit\n"
)
TRACE_PREVIEW_CHARS = 100


def ask_user(description: str) -> bool:
    """The confirmation gate: the agent may only act after a human types 'y'."""
    answer = input(f"  ! the assistant wants to {description}. Allow? [y/N] ")
    return answer.strip().lower() in {"y", "yes"}


def remember_command(note: str, memory_path: Path) -> str:
    try:
        return f"Saved to memory: {save_note(note, memory_path)}"
    except ValueError as err:
        return f"Not saved: {err}."


def format_trace(query: str, turn: AgentTurn) -> str:
    lines = [f"  · searched as: {query!r}"]
    for step in turn.steps:
        preview = step.result[:TRACE_PREVIEW_CHARS].replace("\n", " ")
        lines.append(f"  · tool {step.name}({step.input}) -> {preview!r}")
    if not turn.steps:
        lines.append("  · no tool called")
    return "\n".join(lines)


def main(memory_path: Path = MEMORY_PATH, drafts_dir: Path = DRAFTS_DIR) -> None:
    retriever = build_index(quiet=True)  # (A)
    tools = make_assistant_tools(
        retriever, confirm=ask_user, memory_path=memory_path, drafts_dir=drafts_dir
    )
    history = []  # (B)
    show_trace = False
    print(GREETING)
    while True:  # (C)
        try:
            question = input("you > ").strip()  # (D)
        except (EOFError, KeyboardInterrupt):
            break
        if question == "/exit":
            break
        if not question:
            continue
        if question == "/trace":
            show_trace = not show_trace
            print(f"  trace {'on' if show_trace else 'off'}\n")
            continue
        if question.startswith("/remember"):
            print(f"  {remember_command(question[len('/remember'):], memory_path)}\n")
            continue

        query = standalone_query(history, question)  # (E)
        try:
            turn = run_harness_turn(  # (F)
                query, tools, history=history, memory=load_memory(memory_path)
            )
        except RuntimeError as err:  # e.g. Ollama not running, API outage
            print(f"  [error] {err}\n")
            continue
        if show_trace:
            print(format_trace(query, turn))
        print(f"bot > {turn.answer}\n")
        history.append({"role": "user", "content": question})
        history.append({"role": "assistant", "content": turn.answer})
    print("bye!")


if __name__ == "__main__":  # `python -m ribot.assistant`
    main()
