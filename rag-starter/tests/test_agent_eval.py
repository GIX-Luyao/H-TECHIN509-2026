"""Weeks 8-10: tests for the agent behavior evaluation. Offline."""

import json

import pytest

from ribot.agent_eval import (
    AgentCase,
    check_turn,
    evaluate_agent,
    is_refusal,
    load_cases,
)
from ribot.agent_loop import AgentTurn, ToolStep
from ribot.build_index import build_index
from ribot.toolbox import deny_all, make_assistant_tools


@pytest.fixture(autouse=True)
def offline(monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.delenv("RIBOT_LLM", raising=False)


def _turn(answer, *names):
    return AgentTurn(answer, tuple(ToolStep(n, {}, "r") for n in names), False)


def test_shipped_cases_load_and_cover_routing_refusal_and_no_tool():
    cases = load_cases()
    assert len(cases) >= 8
    assert any(c.expect_refusal for c in cases)
    assert any(c.expect_tool == "none" for c in cases)
    assert any(c.expect_tool == "list_sources" for c in cases)


def test_load_cases_rejects_malformed_file(tmp_path):
    bad = tmp_path / "cases.json"
    bad.write_text(
        json.dumps({"cases": [{"expect_tool": "search_docs"}]}), encoding="utf-8"
    )
    with pytest.raises(ValueError, match="question"):
        load_cases(bad)


def test_is_refusal():
    assert is_refusal("I don't know based on the documents I have.")
    assert is_refusal("I couldn't find that in your documents.")
    assert not is_refusal("Based on the documents: reset via the link.")


def test_check_turn_reports_each_failure():
    case = AgentCase("q", expect_tool="search_docs", expect_refusal=True)
    assert check_turn(case, _turn("I don't know.", "search_docs")) == ()
    reasons = check_turn(case, _turn("Here you go", "list_sources"))
    assert len(reasons) == 2
    no_tool = AgentCase("hi", expect_tool="none")
    assert check_turn(no_tool, _turn("Hello!")) == ()
    assert check_turn(no_tool, _turn("Hello!", "search_docs"))


def test_offline_run_passes_every_case_it_does_not_skip(tmp_path):
    tools = make_assistant_tools(
        build_index(quiet=True),
        confirm=deny_all,
        memory_path=tmp_path / "m.md",
        drafts_dir=tmp_path / "drafts",
    )
    results = evaluate_agent(tools, load_cases())
    ran = [r for r in results if not r.skipped]
    assert ran and all(r.passed for r in ran), [r.reasons for r in ran if not r.passed]
    assert any(r.skipped for r in results)  # real-model-only cases are skipped offline
