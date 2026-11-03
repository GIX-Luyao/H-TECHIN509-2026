"""Weeks 8-10: tests for the multi-turn agent loop. Offline; scripted fakes only."""

import pytest

from ribot.agent_loop import AgentTurn, build_messages, run_harness_turn
from ribot.build_index import build_index
from ribot.harness import Tool
from ribot.toolbox import deny_all, make_assistant_tools


@pytest.fixture(scope="module")
def tools(tmp_path_factory):
    folder = tmp_path_factory.mktemp("agent")
    return make_assistant_tools(
        build_index(quiet=True),
        confirm=deny_all,
        memory_path=folder / "assistant_memory.md",
        drafts_dir=folder / "drafts",
    )


@pytest.fixture(autouse=True)
def offline(monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.delenv("RIBOT_LLM", raising=False)


def test_offline_turn_is_grounded_cited_and_traced(tools):
    turn = run_harness_turn("How do I reset my password?", tools)
    assert isinstance(turn, AgentTurn)
    assert "[source: help_center.md]" in turn.answer
    assert [step.name for step in turn.steps] == ["search_docs"]
    assert not turn.hit_cap


def test_out_of_corpus_question_is_refused(tools):
    turn = run_harness_turn("Recommend a good pizza recipe", tools)
    assert "don't know" in turn.answer.lower()


def test_build_messages_includes_memory_and_recent_text_history():
    history = [{"role": "user", "content": f"q{i}"} for i in range(20)]
    history.append({"role": "assistant", "content": [{"type": "text", "text": "x"}]})
    messages = build_messages("now?", history, memory="## Preferences\n- Tone: plain")
    assert messages[0]["role"] == "system"
    assert "- Tone: plain" in messages[0]["content"]
    assert messages[-1] == {"role": "user", "content": "now?"}
    middle = messages[1:-1]
    assert 0 < len(middle) <= 6 and all(isinstance(m["content"], str) for m in middle)
    assert middle[-1]["content"] == "q19"


def _scripted(replies):
    """A fake chat function that returns canned assistant messages in order."""
    queue = list(replies)

    def chat_fn(messages, declarations):
        return queue.pop(0)

    return chat_fn


def _tool_use(name, args, n=1):
    return {
        "role": "assistant",
        "content": [{"type": "tool_use", "id": f"t{n}", "name": name, "input": args}],
    }


def test_loop_stops_at_the_cap():
    echo = Tool("echo", "echo", {"type": "object", "properties": {}}, lambda: "again")
    forever = _scripted([_tool_use("echo", {}, n) for n in range(10)])
    turn = run_harness_turn("loop?", [echo], max_iters=3, chat_fn=forever)
    assert turn.hit_cap and len(turn.steps) == 3
    assert "step limit" in turn.answer


def test_unknown_tool_is_recovered_not_crashed():
    replies = _scripted(
        [
            _tool_use("no_such_tool", {}),
            {"role": "assistant", "content": [{"type": "text", "text": "ok"}]},
        ]
    )
    turn = run_harness_turn("x", [], chat_fn=replies)
    assert turn.answer == "ok"
    assert "Unknown tool" in turn.steps[0].result


def test_tool_crash_becomes_readable_result():
    def boom(**_):
        raise RuntimeError("disk full")

    broken = Tool("broken", "fails", {"type": "object", "properties": {}}, boom)
    replies = _scripted(
        [
            _tool_use("broken", {}),
            {"role": "assistant", "content": [{"type": "text", "text": "sorry"}]},
        ]
    )
    turn = run_harness_turn("x", [broken], chat_fn=replies)
    assert "disk full" in turn.steps[0].result and turn.answer == "sorry"
