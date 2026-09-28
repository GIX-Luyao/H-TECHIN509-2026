"""Central settings. Loads the API key from a local .env file (never committed)."""

from __future__ import annotations

import os
from dataclasses import dataclass

try:  # python-dotenv is optional for the offline path
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:  # pragma: no cover - offline machines may not have it yet
    pass


@dataclass(frozen=True)
class Settings:
    """Immutable view of the environment configuration."""

    api_key: str | None
    chat_model: str
    embed_model: str
    base_url: str | None
    llm_backend: str
    embed_backend: str
    ollama_model: str
    ollama_embed_model: str
    ollama_host: str

    @property
    def has_key(self) -> bool:
        """True when a real API key is configured (otherwise we run offline)."""
        return bool(self.api_key and self.api_key.strip())


def get_settings() -> Settings:
    """Read settings from the environment each call (cheap, and easy to reason about)."""
    return Settings(
        api_key=os.environ.get("OPENAI_API_KEY"),
        chat_model=os.environ.get("CHAT_MODEL", "gpt-4o-mini"),
        embed_model=os.environ.get("EMBED_MODEL", "text-embedding-3-small"),
        base_url=os.environ.get("OPENAI_BASE_URL") or None,
        # Week 10 (optional): set RIBOT_LLM=ollama to point chat() at a local model.
        llm_backend=os.environ.get("RIBOT_LLM", "").strip().lower(),
        # Week 10 stretch (optional): set RIBOT_EMBED=ollama to embed locally too.
        embed_backend=os.environ.get("RIBOT_EMBED", "").strip().lower(),
        ollama_model=os.environ.get("OLLAMA_MODEL", "llama3.2"),
        ollama_embed_model=os.environ.get("OLLAMA_EMBED_MODEL", "nomic-embed-text"),
        ollama_host=os.environ.get("OLLAMA_HOST", "http://localhost:11434"),
    )
