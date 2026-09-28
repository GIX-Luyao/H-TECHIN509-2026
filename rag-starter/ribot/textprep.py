"""Week 4: reusable functions + error handling + JSON.

These turn messy text into clean, structured records the rest of the app depends on.
"""

from __future__ import annotations

import json
import re


def clean_message(text: str) -> str:
    """Strip, lowercase, collapse runs of whitespace, and drop stray punctuation.

    >>> clean_message("  Hello,   WORLD!! ")
    'hello world'
    """
    text = text.strip().lower()
    text = re.sub(r"[^\w\s]", "", text)   # remove punctuation
    text = re.sub(r"\s+", " ", text)       # collapse whitespace
    return text


def build_conv(questions: list[str], answers: list[str]) -> list[dict[str, str]]:
    """Pair questions with answers into a list of {'user', 'bot'} dicts.

    Reuses clean_message so every record is normalized the same way.
    """
    return [
        {"user": clean_message(q), "bot": clean_message(a)}
        for q, a in zip(questions, answers)
    ]


def safe_clean(text: str) -> str:
    """Clean text but never crash on bad input (Week 4 try/except floor)."""
    try:
        return clean_message(text)
    except (TypeError, AttributeError):
        return ""


def export_to_json(data: object, filename: str) -> None:
    """Write any JSON-serializable object to a readable file."""
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


if __name__ == "__main__":  # `python -m ribot.textprep`
    conv = build_conv(
        questions=["  How do I RESET my password? ", "Where are the DOCS?"],
        answers=["Use the 'Forgot password' link.", "In the help center."],
    )
    print(conv)
    export_to_json(conv, "conv_example.json")
    print("wrote conv_example.json")
