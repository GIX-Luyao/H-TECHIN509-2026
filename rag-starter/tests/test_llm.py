"""Week 10: tests for the LLM backends. Everything here runs offline — no key, no Ollama."""

import io
import json
import urllib.error
from unittest.mock import patch

import pytest

from ribot.llm import JSON_PROTOCOL_MARKER, REWRITE_PROTOCOL_MARKER, OllamaLLM, chat

MESSAGES = [
    {"role": "system", "content": "You are a test bot."},
    {"role": "user", "content": "hello"},
]


def test_default_backend_is_still_fakellm(monkeypatch):
    # NO env opt-in and NO key -> chat() must keep using the offline FakeLLM.
    monkeypatch.delenv("RIBOT_LLM", raising=False)
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    answer = chat(MESSAGES)
    assert "offline demo reply" in answer


def test_ollama_unreachable_gives_actionable_error():
    # No Ollama needed: we mock the network call failing, as it would on a fresh laptop.
    llm = OllamaLLM(model="llama3.2", host="http://localhost:11434")
    with patch(
        "ribot.llm.urllib.request.urlopen",
        side_effect=urllib.error.URLError("connection refused"),
    ):
        with pytest.raises(RuntimeError) as excinfo:
            llm.chat(MESSAGES)
    message = str(excinfo.value)
    assert "Ollama not reachable at http://localhost:11434" in message
    assert "ollama.com" in message
    assert "ollama pull llama3.2" in message


def test_ollama_parses_a_successful_reply():
    # Mock a healthy Ollama server so the request/response plumbing is exercised.
    fake_body = json.dumps({"message": {"role": "assistant", "content": "local hi"}})

    class FakeResponse(io.BytesIO):
        def __enter__(self):
            return self

        def __exit__(self, *args):
            self.close()

    with patch(
        "ribot.llm.urllib.request.urlopen",
        return_value=FakeResponse(fake_body.encode("utf-8")),
    ) as mock_urlopen:
        answer = OllamaLLM(model="llama3.2").chat(MESSAGES)

    assert answer == "local hi"
    request = mock_urlopen.call_args.args[0]
    assert request.full_url == "http://localhost:11434/api/chat"
    sent = json.loads(request.data.decode("utf-8"))
    assert sent["model"] == "llama3.2"
    assert sent["messages"] == MESSAGES
    assert sent["stream"] is False


def test_env_var_routes_chat_to_ollama(monkeypatch):
    # RIBOT_LLM=ollama is the opt-in switch; confirm chat() honors it (still mocked).
    monkeypatch.setenv("RIBOT_LLM", "ollama")
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    with patch(
        "ribot.llm.urllib.request.urlopen",
        side_effect=urllib.error.URLError("connection refused"),
    ):
        with pytest.raises(RuntimeError, match="Ollama not reachable"):
            chat(MESSAGES)


# --- Week 4: structured output from the offline FakeLLM ---------------------------


def test_json_marker_makes_fakellm_return_parseable_json(monkeypatch):
    """The Week-4 lesson needs the offline model to emit JSON, not prose."""
    monkeypatch.delenv("RIBOT_LLM", raising=False)
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    messages = [
        {"role": "system", "content": f"Extract the fields. {JSON_PROTOCOL_MARKER}."},
        {"role": "user", "content": "How many vacation days do I get?"},
    ]
    reply = chat(messages)

    # It arrives FENCED, exactly like a real model's — that is the whole teaching point,
    # so json.loads must fail on the raw reply and succeed once the fence is stripped.
    with pytest.raises(json.JSONDecodeError):
        json.loads(reply)

    assert reply.startswith("```json")
    stripped = reply.removeprefix("```json").removesuffix("```").strip()
    parsed = json.loads(stripped)
    assert parsed["question"] == "How many vacation days do I get?"
    assert parsed["needs_human"] is False


def test_no_json_marker_still_returns_prose(monkeypatch):
    """The marker must be opt-in — Weeks 1-3 must be completely unaffected."""
    monkeypatch.delenv("RIBOT_LLM", raising=False)
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    reply = chat(MESSAGES)
    assert "offline demo reply" in reply
    assert "```json" not in reply


def test_rewrite_marker_makes_fakellm_stitch_the_two_turns(monkeypatch):
    """The Week-9 lesson needs the offline model to answer a rewrite request."""
    monkeypatch.delenv("RIBOT_LLM", raising=False)
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    messages = [
        {"role": "system", "content": f"Rewrite it. {REWRITE_PROTOCOL_MARKER}"},
        {
            "role": "user",
            "content": (
                "Earlier question: What is the vacation carryover limit?\n"
                "Follow-up question: Can those roll over?\n"
                "Rewrite the follow-up as a standalone question."
            ),
        },
    ]
    reply = chat(messages)

    # Offline, the "rewrite" is the two turns stitched together — the wiring works, and
    # the lesson says plainly that a real model is the part that gets smarter.
    assert reply == "What is the vacation carryover limit? Can those roll over?"


def test_no_rewrite_marker_still_returns_prose(monkeypatch):
    """The marker must be opt-in — Weeks 1-8 must be completely unaffected."""
    monkeypatch.delenv("RIBOT_LLM", raising=False)
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    reply = chat(MESSAGES)
    assert "offline demo reply" in reply
    assert "Earlier question" not in reply
