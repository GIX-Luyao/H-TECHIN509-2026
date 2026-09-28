"""Week 10 stretch: tests for the embedding backends. Everything here runs offline."""

import io
import json
import urllib.error
from unittest.mock import patch

import pytest

from ribot.embeddings import OllamaEmbedder, fallback_embed, get_embedder


def test_default_embedder_is_still_fallback(monkeypatch):
    # NO env opt-in and NO key -> get_embedder() must keep using the offline fallback.
    monkeypatch.delenv("RIBOT_EMBED", raising=False)
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    assert get_embedder() is fallback_embed


def test_ollama_unreachable_gives_actionable_error():
    # No Ollama needed: we mock the network call failing, as it would on a fresh laptop.
    embedder = OllamaEmbedder(model="nomic-embed-text", host="http://localhost:11434")
    with patch(
        "ribot.embeddings.urllib.request.urlopen",
        side_effect=urllib.error.URLError("connection refused"),
    ):
        with pytest.raises(RuntimeError) as excinfo:
            embedder.embed("reset my password")
    message = str(excinfo.value)
    assert "Ollama not reachable at http://localhost:11434" in message
    assert "ollama.com" in message
    assert "ollama pull nomic-embed-text" in message


def test_ollama_parses_a_successful_embedding():
    # Mock a healthy Ollama server so the request/response plumbing is exercised.
    fake_body = json.dumps({"embedding": [0.1, 0.2, 0.3]})

    class FakeResponse(io.BytesIO):
        def __enter__(self):
            return self

        def __exit__(self, *args):
            self.close()

    with patch(
        "ribot.embeddings.urllib.request.urlopen",
        return_value=FakeResponse(fake_body.encode("utf-8")),
    ) as mock_urlopen:
        vector = OllamaEmbedder(model="nomic-embed-text").embed("hello")

    assert vector == [0.1, 0.2, 0.3]
    request = mock_urlopen.call_args.args[0]
    assert request.full_url == "http://localhost:11434/api/embeddings"
    sent = json.loads(request.data.decode("utf-8"))
    assert sent["model"] == "nomic-embed-text"
    assert sent["prompt"] == "hello"


def test_env_var_routes_embedding_to_ollama(monkeypatch):
    # RIBOT_EMBED=ollama is the opt-in switch; confirm get_embedder() honors it (mocked).
    monkeypatch.setenv("RIBOT_EMBED", "ollama")
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    embed_fn = get_embedder()
    with patch(
        "ribot.embeddings.urllib.request.urlopen",
        side_effect=urllib.error.URLError("connection refused"),
    ):
        with pytest.raises(RuntimeError, match="Ollama not reachable"):
            embed_fn("hello")
