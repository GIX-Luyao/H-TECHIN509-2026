"""Week 8: tests for the structured tool-calling harness. Fully offline — no key."""

import pytest

from ribot.build_index import build_index
from ribot.harness import Tool, make_tools, run_harness
from ribot.llm import FakeToolLLM


@pytest.fixture(scope="module")
def tools():
    # Offline fixture embeddings + the sample corpus; no key, no network.
    retriever = build_index()
    return make_tools(retriever)


def test_search_question_gets_a_grounded_answer(monkeypatch, tools):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.delenv("RIBOT_LLM", raising=False)
    answer = run_harness("How do I reset my password?", tools)
    assert "Based on the documents:" in answer


def test_library_question_dispatches_the_second_tool(monkeypatch, tools):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    answer = run_harness("Which documents do you have?", tools)
    # list_sources returns filenames, which the fake answers from verbatim.
    assert ".md" in answer


def test_unknown_tool_becomes_a_readable_tool_result(tools):
    fake = FakeToolLLM()
    reply = fake.chat_tools(
        [{"role": "user", "content": "anything"}],
        [{"name": "no_such_tool", "description": "", "input_schema": {}}],
    )
    block = reply["content"][0]
    assert block["type"] == "tool_use"
    # The harness must survive a request for a tool that isn't registered.
    result = run_harness_with_forced_block(tools, block)
    assert result.is_error
    assert "Unknown tool" in result.content


def run_harness_with_forced_block(tools, block):
    """Route one forced tool_use block through the harness's dispatch path."""
    from ribot.harness import _dispatch

    registry = {tool.name: tool for tool in tools}
    return _dispatch(registry, block)


def test_bad_arguments_become_a_readable_tool_result(tools):
    from ribot.harness import _dispatch

    registry = {tool.name: tool for tool in tools}
    bad_block = {"name": "list_sources", "id": "toolu_x", "input": {"bogus": 1}}
    result = _dispatch(registry, bad_block)
    assert result.is_error
    assert "Bad arguments" in result.content


def test_failed_tool_marks_its_result_block_as_an_error():
    from ribot.harness import _tool_result_block
    from ribot.tools import ToolResult

    block = {"id": "toolu_x", "name": "search_docs"}
    failed = _tool_result_block(block, ToolResult("boom", is_error=True))
    worked = _tool_result_block(block, ToolResult("ok"))
    assert failed["is_error"] is True and failed["tool_use_id"] == "toolu_x"
    assert "is_error" not in worked


def test_cap_always_terminates(monkeypatch):
    # A tool that keeps the conversation from ever reaching a text answer would loop
    # forever without the cap — prove the cap wins.
    always_tool = Tool(
        name="noop",
        description="does nothing",
        input_schema={"type": "object", "properties": {}},
        run=lambda: "",
    )

    def always_tool_use(messages, tools, temperature=0.2):
        return {
            "role": "assistant",
            "stop_reason": "tool_use",
            "content": [
                {"type": "tool_use", "id": "toolu_loop", "name": "noop", "input": {}}
            ],
        }

    monkeypatch.setattr("ribot.harness.chat_tools", always_tool_use)
    answer = run_harness("anything", [always_tool], max_iters=3)
    assert answer == "I couldn't finish within the step limit."


def test_tool_result_ties_back_to_the_tool_use_id():
    # The fake's second turn must answer from a result tied by tool_use_id — the same
    # contract data/tool_call_transcript.json documents.
    fake = FakeToolLLM()
    messages = [
        {"role": "user", "content": "How do I reset my password?"},
        {
            "role": "assistant",
            "stop_reason": "tool_use",
            "content": [
                {
                    "type": "tool_use",
                    "id": "toolu_001",
                    "name": "search_docs",
                    "input": {"query": "password reset", "k": 3},
                }
            ],
        },
        {
            "role": "user",
            "content": [
                {
                    "type": "tool_result",
                    "tool_use_id": "toolu_001",
                    "content": "[help_center.md] Open Settings > Reset password.",
                }
            ],
        },
    ]
    reply = fake.chat_tools(messages, [])
    assert reply["stop_reason"] == "end_turn"
    assert "help_center.md" in reply["content"][0]["text"]
