"""Regenerate data/embeddings_fixture.json from the sample docs using fallback_embed.

The fixture lets Week 5/6 exercises run with consistent, offline vectors.

    python scripts/build_fixture.py
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from ribot.chunking import chunk_text          # noqa: E402
from ribot.embeddings import fallback_embed     # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
SAMPLE_DIR = ROOT / "data" / "sample_docs"
OUT = ROOT / "data" / "embeddings_fixture.json"


def main() -> None:
    fixture: dict[str, list[float]] = {}
    for path in sorted(SAMPLE_DIR.glob("*.md")):
        for i, chunk in enumerate(chunk_text(path.read_text(encoding="utf-8"))):
            fixture[f"{path.name}:{i}"] = fallback_embed(chunk)
    OUT.write_text(json.dumps(fixture, indent=2), encoding="utf-8")
    print(f"wrote {len(fixture)} vectors to {OUT}")


if __name__ == "__main__":
    main()
