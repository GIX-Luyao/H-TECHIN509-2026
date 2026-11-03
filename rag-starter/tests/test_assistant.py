"""Week 9: tests for the terminal assistant loop. Offline; input() is scripted."""

import pytest

from ribot import assistant
from ribot.memory import load_memory


@pytest.fixture(autouse=True)
def offline(monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.delenv("RIBOT_LLM", raising=False)


def _run(monkeypatch, tmp_path, lines):
    feed = iter(lines)
    monkeypatch.setattr("builtins.input", lambda prompt="": next(feed))
    memory = tmp_path / "assistant_memory.md"
    memory.write_text("## Preferences\n- Tone: plain\n", encoding="utf-8")
    assistant.main(memory_path=memory, drafts_dir=tmp_path / "drafts")
    return memory


def test_answers_with_a_citation_then_exits(monkeypatch, tmp_path, capsys):
    _run(monkeypatch, tmp_path, ["How do I reset my password?", "/exit"])
    out = capsys.readouterr().out
    assert "bot > " in out and "[source: help_center.md]" in out


def test_trace_shows_which_tool_ran(monkeypatch, tmp_path, capsys):
    _run(monkeypatch, tmp_path, ["/trace", "How do I reset my password?", "/exit"])
    assert "search_docs" in capsys.readouterr().out


def test_follow_up_is_rewritten_before_searching(monkeypatch, tmp_path, capsys):
    _run(
        monkeypatch,
        tmp_path,
        [
            "/trace",
            "What is the vacation carryover limit?",
            "Can those roll over?",
            "/exit",
        ],
    )
    out = capsys.readouterr().out
    assert "vacation carryover limit? Can those roll over?" in out


def test_remember_command_writes_memory(monkeypatch, tmp_path, capsys):
    memory = _run(monkeypatch, tmp_path, ["/remember prefers bullet points", "/exit"])
    assert "prefers bullet points" in load_memory(memory)
    assert "Saved" in capsys.readouterr().out


def test_remember_command_rejects_personal_data(monkeypatch, tmp_path, capsys):
    memory = _run(monkeypatch, tmp_path, ["/remember jane@example.com", "/exit"])
    assert "jane" not in load_memory(memory)
    assert "Not saved" in capsys.readouterr().out


def test_ctrl_d_exits_cleanly(monkeypatch, tmp_path):
    def eof(prompt=""):
        raise EOFError

    monkeypatch.setattr("builtins.input", eof)
    assistant.main(memory_path=tmp_path / "m.md", drafts_dir=tmp_path / "d")


def test_backend_errors_are_reported_not_fatal(monkeypatch, tmp_path, capsys):
    def broken(*args, **kwargs):
        raise RuntimeError("Ollama not reachable")

    monkeypatch.setattr(assistant, "run_harness_turn", broken)
    _run(monkeypatch, tmp_path, ["hello", "/exit"])
    assert "Ollama not reachable" in capsys.readouterr().out


def test_source_has_the_week9_self_check_parts():
    # The Module 9 assignment notebook greps for these.
    src = assistant.__file__ and open(assistant.__file__, encoding="utf-8").read()
    for part in ("input(", "/exit", "standalone_query", ".append(", "run_harness"):
        assert part in src
