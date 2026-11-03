"""Weeks 8-10: tests for the assistant toolbox (cited search + confirm-gated actions)."""

import pytest

from ribot.build_index import build_index
from ribot.memory import load_memory
from ribot.my_tools import MY_TOOLS, current_date
from ribot.toolbox import deny_all, gated, make_assistant_tools, search_cited


@pytest.fixture(scope="module")
def retriever():
    return build_index(quiet=True)


def _tools_by_name(retriever, tmp_path, confirm):
    memory = tmp_path / "assistant_memory.md"
    memory.write_text("## Preferences\n- Tone: plain\n", encoding="utf-8")
    tools = make_assistant_tools(
        retriever, confirm=confirm, memory_path=memory, drafts_dir=tmp_path / "drafts"
    )
    return {tool.name: tool for tool in tools}, memory


def test_search_cited_labels_each_chunk_with_its_source(retriever):
    found = search_cited(retriever, "How do I reset my password?")
    assert found.startswith("[source: help_center.md]")


def test_search_cited_returns_empty_below_the_score_floor(retriever):
    # Nothing in the sample corpus is about pizza: the floor turns weak matches into
    # "no evidence", which is what lets the assistant say "I don't know".
    assert search_cited(retriever, "Recommend a good pizza recipe") == ""


def test_search_cited_clamps_bad_k(retriever):
    assert search_cited(retriever, "reset password", k="lots") != ""
    assert search_cited(retriever, "reset password", k=0) != ""


def test_gated_runs_only_after_a_yes():
    calls = []
    assert "declined" in gated(deny_all, "do it", lambda: calls.append(1) or "done")
    assert calls == []
    assert gated(lambda _: True, "do it", lambda: "done") == "done"


def test_toolbox_has_read_action_and_student_tools(retriever, tmp_path):
    tools, _ = _tools_by_name(retriever, tmp_path, deny_all)
    assert list(tools)[:4] == ["search_docs", "list_sources", "remember", "save_draft"]
    assert "current_date" in tools  # from my_tools.py


def test_list_sources_names_the_files(retriever, tmp_path):
    tools, _ = _tools_by_name(retriever, tmp_path, deny_all)
    assert "hr_policy.md" in tools["list_sources"].run()


def test_remember_writes_only_when_confirmed(retriever, tmp_path):
    tools, memory = _tools_by_name(retriever, tmp_path, deny_all)
    assert "declined" in tools["remember"].run(note="prefers bullet points")
    assert "bullet" not in load_memory(memory)

    tools, memory = _tools_by_name(retriever, tmp_path, lambda _: True)
    assert "Saved" in tools["remember"].run(note="prefers bullet points")
    assert "prefers bullet points" in load_memory(memory)


def test_remember_reports_rejected_notes(retriever, tmp_path):
    tools, _ = _tools_by_name(retriever, tmp_path, lambda _: True)
    assert "Not saved" in tools["remember"].run(note="jane@example.com")


def test_save_draft_writes_file_and_never_overwrites(retriever, tmp_path):
    tools, _ = _tools_by_name(retriever, tmp_path, lambda _: True)
    result = tools["save_draft"].run(title="Reply to Sam!", body="Hello Sam")
    draft = tmp_path / "drafts" / "reply-to-sam.md"
    assert "Saved" in result and draft.read_text(encoding="utf-8").endswith(
        "Hello Sam\n"
    )
    assert "already exists" in tools["save_draft"].run(title="Reply to Sam", body="x")


def test_save_draft_declined_writes_nothing(retriever, tmp_path):
    tools, _ = _tools_by_name(retriever, tmp_path, deny_all)
    assert "declined" in tools["save_draft"].run(title="t", body="b")
    assert not (tmp_path / "drafts").exists()


def test_my_tools_example_runs():
    assert len(current_date()) == 10  # YYYY-MM-DD
    assert all(tool.declaration()["name"] for tool in MY_TOOLS)
