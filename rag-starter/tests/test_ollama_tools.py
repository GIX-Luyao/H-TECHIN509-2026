"""Week 10: tests for local (Ollama) tool calling. No Ollama needed — HTTP is faked."""

import io
import json
import urllib.error

import pytest

from ribot import ollama_tools
from ribot.ollama_tools import (
    OllamaToolLLM,
    chat_tools_routed,
    from_ollama_reply,
    to_ollama_messages,
)

TOOLS = [
    {
        "name": "search_docs",
        "description": "Search",
        "input_schema": {"type": "object", "properties": {"query": {"type": "string"}}},
    }
]


def test_to_ollama_messages_converts_blocks_and_names_tool_results():
    messages = [
        {"role": "system", "content": "sys"},
        {"role": "user", "content": "q"},
        {
            "role": "assistant",
            "content": [
                {
                    "type": "tool_use",
                    "id": "a1",
                    "name": "search_docs",
                    "input": {"query": "q"},
                }
            ],
        },
        {
            "role": "user",
            "content": [
                {"type": "tool_result", "tool_use_id": "a1", "content": "found"}
            ],
        },
    ]
    converted = to_ollama_messages(messages)
    assert converted[0] == {"role": "system", "content": "sys"}
    assert converted[2]["tool_calls"][0]["function"] == {
        "name": "search_docs",
        "arguments": {"query": "q"},
    }
    assert converted[3] == {
        "role": "tool",
        "content": "found",
        "tool_name": "search_docs",
    }


@pytest.mark.parametrize("arguments", [{"query": "pw"}, '{"query": "pw"}'])
def test_from_ollama_reply_tool_call(arguments):
    body = {
        "message": {
            "content": "",
            "tool_calls": [
                {"function": {"name": "search_docs", "arguments": arguments}}
            ],
        }
    }
    reply = from_ollama_reply(body, turn=2)
    block = reply["content"][0]
    assert reply["stop_reason"] == "tool_use"
    assert block["name"] == "search_docs" and block["input"] == {"query": "pw"}
    assert block["id"] == "toolu_ollama_002"


def test_from_ollama_reply_text():
    reply = from_ollama_reply({"message": {"content": "hi"}}, turn=0)
    assert reply["stop_reason"] == "end_turn"
    assert reply["content"] == [{"type": "text", "text": "hi"}]


class _FakeResponse(io.BytesIO):
    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return False


def test_chat_tools_posts_declared_tools(monkeypatch):
    sent = {}

    def fake_urlopen(request, timeout):
        sent["body"] = json.loads(request.data)
        return _FakeResponse(json.dumps({"message": {"content": "done"}}).encode())

    monkeypatch.setattr(ollama_tools.urllib.request, "urlopen", fake_urlopen)
    reply = OllamaToolLLM(model="qwen3").chat_tools(
        [{"role": "user", "content": "q"}], TOOLS
    )
    assert reply["content"][0]["text"] == "done"
    assert sent["body"]["tools"][0]["function"]["name"] == "search_docs"
    assert sent["body"]["model"] == "qwen3" and sent["body"]["stream"] is False


def test_model_without_tool_support_gets_a_clear_error(monkeypatch):
    def fake_urlopen(request, timeout):
        raise urllib.error.HTTPError(
            request.full_url,
            400,
            "Bad Request",
            {},
            io.BytesIO(b"does not support tools"),
        )

    monkeypatch.setattr(ollama_tools.urllib.request, "urlopen", fake_urlopen)
    with pytest.raises(RuntimeError, match="tool"):
        OllamaToolLLM(model="gemma3:1b").chat_tools(
            [{"role": "user", "content": "q"}], TOOLS
        )


def test_unreachable_ollama_gets_a_clear_error(monkeypatch):
    def fake_urlopen(request, timeout):
        raise urllib.error.URLError("connection refused")

    monkeypatch.setattr(ollama_tools.urllib.request, "urlopen", fake_urlopen)
    with pytest.raises(RuntimeError, match="not reachable"):
        OllamaToolLLM().chat_tools([{"role": "user", "content": "q"}], TOOLS)


def test_router_uses_ollama_only_when_opted_in(monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.delenv("RIBOT_LLM", raising=False)
    offline = chat_tools_routed([{"role": "user", "content": "q"}], TOOLS)
    assert offline["content"][0]["id"].startswith("toolu_offline")

    monkeypatch.setenv("RIBOT_LLM", "ollama")
    monkeypatch.setattr(
        OllamaToolLLM,
        "chat_tools",
        lambda self, m, t: {"role": "assistant", "content": "local"},
    )
    assert (
        chat_tools_routed([{"role": "user", "content": "q"}], TOOLS)["content"]
        == "local"
    )
