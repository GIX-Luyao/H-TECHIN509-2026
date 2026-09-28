"""Week 5: turn text into a vector (an 'embedding').

- `embed(text)` calls the real embedding API (needs a key).
- `fallback_embed(text)` is a deterministic, pure-Python stand-in so you can build and
  test the whole retrieval pipeline OFFLINE. It hashes words into a fixed-length vector,
  so texts that share words come out 'similar'. It is NOT as good as real embeddings —
  it is a teaching/safety-net tool.
- `get_embedder()` picks the real one if a key exists, else the fallback.
- Week 10 stretch (opt-in): set `RIBOT_EMBED=ollama` to embed with a *local* Ollama model
  instead — same text in, same list-of-floats out, no document leaves your machine.
"""

from __future__ import annotations

import hashlib
import json
import math
import re
import urllib.error
import urllib.request
from pathlib import Path
from typing import Callable

from .config import get_settings

EMBED_DIM = 256
_FIXTURE_PATH = Path(__file__).resolve().parent.parent / "data" / "embeddings_fixture.json"

# Very common words carry little meaning; dropping them sharpens the offline matches.
_STOPWORDS = frozenset(
    """a an the of to in on at for and or but if is are was were be been being
    you your i me my we our they it this that these those how do does did can
    could will would should with as by from up out about into over after""".split()
)


def _tokens(text: str) -> list[str]:
    return [t for t in re.findall(r"[a-z0-9]+", text.lower()) if t not in _STOPWORDS]


def _bucket(token: str) -> int:
    digest = hashlib.md5(token.encode("utf-8")).hexdigest()
    return int(digest, 16) % EMBED_DIM


def fallback_embed(text: str) -> list[float]:
    """Deterministic offline embedding: a hashed bag-of-words, L2-normalized."""
    vec = [0.0] * EMBED_DIM
    for token in _tokens(text):
        vec[_bucket(token)] += 1.0
    norm = math.sqrt(sum(v * v for v in vec))
    if norm == 0:
        return vec
    return [v / norm for v in vec]


def embed(text: str) -> list[float]:
    """Real embedding via the API. Falls back automatically if no key is set."""
    settings = get_settings()
    if not settings.has_key:
        return fallback_embed(text)
    from openai import OpenAI

    client = OpenAI(api_key=settings.api_key, base_url=settings.base_url)
    response = client.embeddings.create(model=settings.embed_model, input=text)
    return list(response.data[0].embedding)


class OllamaEmbedder:
    """Embed text with a *local* model served by Ollama (https://ollama.com).

    Same interface as `embed`/`fallback_embed`: text in, list of floats out. This is the
    Week 10 stretch "go fully local" path — the LLM swap (`RIBOT_LLM=ollama`) alone is
    half-local: your documents still flow through the *embedding* call. Nothing here is
    installed by default and nothing changes unless you opt in with `RIBOT_EMBED=ollama`
    (or construct this class yourself).

    Uses only the standard library (urllib), mirroring `OllamaLLM` in `ribot/llm.py`.
    """

    def __init__(
        self,
        model: str = "nomic-embed-text",
        host: str = "http://localhost:11434",
        timeout: float = 120.0,
    ) -> None:
        self.model = model
        self.host = host.rstrip("/")
        self.timeout = timeout

    def embed(self, text: str) -> list[float]:
        payload = json.dumps({"model": self.model, "prompt": text}).encode("utf-8")
        request = urllib.request.Request(
            f"{self.host}/api/embeddings",
            data=payload,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        try:
            with urllib.request.urlopen(request, timeout=self.timeout) as response:
                body = json.loads(response.read().decode("utf-8"))
        except (urllib.error.URLError, OSError) as err:
            raise RuntimeError(
                f"Ollama not reachable at {self.host} — install it from ollama.com, "
                f"start it, and run `ollama pull {self.model}`. "
                f"(Original error: {err})"
            ) from err
        return [float(v) for v in body.get("embedding", [])]


def get_embedder() -> Callable[[str], list[float]]:
    """Return whichever embedder is usable right now."""
    settings = get_settings()
    # Opt-in local backend (Week 10 stretch): RIBOT_EMBED=ollama. Default is unchanged.
    if settings.embed_backend == "ollama":
        return OllamaEmbedder(
            model=settings.ollama_embed_model, host=settings.ollama_host
        ).embed
    return embed if settings.has_key else fallback_embed


def load_fixture() -> dict[str, list[float]]:
    """Load precomputed fallback vectors for the sample docs (if present)."""
    if _FIXTURE_PATH.exists():
        return json.loads(_FIXTURE_PATH.read_text(encoding="utf-8"))
    return {}


if __name__ == "__main__":  # `python -m ribot.embeddings`
    v = get_embedder()("reset my password")
    print(f"dim={len(v)}  first5={[round(x, 3) for x in v[:5]]}")
