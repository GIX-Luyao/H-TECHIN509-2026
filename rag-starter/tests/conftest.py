"""Make the `ribot` package importable when running `pytest` from the repo root."""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

# A student's .env may switch on a real model (Week 8: RIBOT_LLM=ollama). Tests must stay
# deterministic and offline, so every test starts with those switches cleared. A test that
# needs one sets it again with monkeypatch.setenv.
_MODEL_SWITCHES = ("OPENAI_API_KEY", "RIBOT_LLM", "RIBOT_EMBED", "OLLAMA_THINK")


@pytest.fixture(autouse=True)
def _offline_by_default(monkeypatch):
    for name in _MODEL_SWITCHES:
        monkeypatch.delenv(name, raising=False)
