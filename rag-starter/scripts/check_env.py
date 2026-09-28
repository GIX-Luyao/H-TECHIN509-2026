"""Week 1 offline health check: python scripts/check_env.py.

Never calls a model service, even if the shell or .env configures one.
"""
from __future__ import annotations

import importlib.util
import math
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))


def main() -> None:
    if sys.version_info < (3, 10):
        raise RuntimeError("Python 3.10 or newer is required.")
    print("Python:", sys.version.split()[0])
    # Load dotenv first, then temporarily override provider choices for this check.
    from ribot.config import get_settings
    from ribot.chatbot import ChatBot
    from ribot.embeddings import get_embedder
    from ribot.similarity import cosine_similarity

    names = ("OPENAI_API_KEY", "RIBOT_LLM", "RIBOT_EMBED")
    saved = {name: os.environ.get(name) for name in names}
    try:
        for name in names:
            os.environ[name] = ""
        if get_settings().has_key:
            raise RuntimeError("Could not select offline mode.")
        print("LLM: offline (FakeLLM)")
        bot = ChatBot()
        answer = bot.reply("My name is Sam.")
        if not answer or "Sam" not in bot.reply("What's my name?"):
            raise RuntimeError("Chat round-trip or conversation memory failed.")
        print("Chat round-trip: ok")
        embed = get_embedder()
        a, b = embed("reset password"), embed("forgot my password")
        score = cosine_similarity(a, b)
        if not a or len(a) != len(b) or not math.isfinite(score):
            raise RuntimeError("Embedding / cosine check failed.")
        print(f"Embedding + cosine: ok (similarity = {score:.2f})")
        for name in ("numpy", "chromadb", "streamlit", "openai"):
            found = importlib.util.find_spec(name) is not None
            print(f"optional '{name}': " + ("available (not imported)" if found else "not installed (fine until needed)"))
        print("\nAll core checks passed. You're ready!")
    finally:
        for name, value in saved.items():
            if value is None:
                os.environ.pop(name, None)
            else:
                os.environ[name] = value


if __name__ == "__main__":
    main()
