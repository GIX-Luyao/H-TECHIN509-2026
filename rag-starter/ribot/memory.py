"""Week 10: the assistant's long-term memory — a markdown file you can read and audit.

`assistant_memory.md` holds durable notes: your preferences, recurring workflows, project
vocabulary. This module does three small things with it:

- `load_memory()` reads the file and keeps only the lines you actually filled in,
- `memory_block()` frames that text for the system prompt, clearly marked as NOT evidence,
- `save_note()` appends one dated note — after checking it is short and not a secret or
  personal data, because anything in this file is sent to the model on every turn.

Memory is plain text you own. Open the file, read it, delete a line — that is the audit.
"""

from __future__ import annotations

import re
from datetime import date
from pathlib import Path

MEMORY_PATH = Path(__file__).resolve().parent.parent / "assistant_memory.md"

# Memory rides along on EVERY request, so it costs tokens every turn: keep it small.
MAX_MEMORY_CHARS = 2000
MAX_NOTE_CHARS = 200
NOTES_HEADING = "## Notes From Conversations"

# Sections written for the human auditor, not for the model.
_HUMAN_ONLY_SECTIONS = {"audit notes"}

# Things that must never land in a file the model reads on every turn.
_BLOCKED_PATTERNS = {
    "an API key": re.compile(r"\bsk-[A-Za-z0-9_-]{8,}"),
    "a password": re.compile(r"\bpassword\s*[:=]", re.IGNORECASE),
    "an email address": re.compile(r"[\w.+-]+@[\w-]+\.[\w.]+"),
    "a phone number": re.compile(r"\b\d{3}[-.\s]\d{3}[-.\s]\d{4}\b"),
}


def _is_filled(line: str) -> bool:
    """A template field like '- Tone:' is blank; '- Tone: plain' is filled."""
    stripped = line.strip()
    return bool(stripped) and not stripped.endswith(":")


def load_memory(path: Path = MEMORY_PATH) -> str:
    """Return the filled-in parts of the memory file ('' if there is no file).

    Keeps a heading only when something under it is filled in, skips the intro paragraph
    above the first heading, and skips human-only sections such as 'Audit Notes'.
    """
    try:
        text = Path(path).read_text(encoding="utf-8")
    except FileNotFoundError:
        return ""

    kept: list[str] = []
    heading: str | None = None
    heading_used = False
    skipping = True  # everything before the first '## ' heading is the intro
    for line in text.splitlines():
        if line.startswith("## "):
            heading = line.strip()
            heading_used = False
            skipping = heading[3:].strip().lower() in _HUMAN_ONLY_SECTIONS
            continue
        if skipping or line.startswith("#") or not _is_filled(line):
            continue
        if not heading_used and heading:
            kept.append(heading)
            heading_used = True
        kept.append(line.rstrip())
    return "\n".join(kept)


def memory_block(memory: str) -> str:
    """Frame memory for the system prompt — useful context, never a citable source."""
    if not memory.strip():
        return ""
    if len(memory) > MAX_MEMORY_CHARS:
        memory = memory[:MAX_MEMORY_CHARS] + "\n[memory truncated]"
    return (
        "Long-term memory about this user (preferences and working notes). Use it to "
        "shape tone and format. It is NOT evidence: never cite it as a source.\n"
        f"{memory}"
    )


def check_note(note: str) -> str:
    """Return the cleaned note, or raise ValueError saying why it can't be stored."""
    cleaned = " ".join(str(note).split())
    if not cleaned:
        raise ValueError("the note is empty")
    if len(cleaned) > MAX_NOTE_CHARS:
        raise ValueError(f"the note is longer than {MAX_NOTE_CHARS} characters")
    for label, pattern in _BLOCKED_PATTERNS.items():
        if pattern.search(cleaned):
            raise ValueError(f"the note looks like it contains {label}")
    return cleaned


def add_note(text: str, note: str, today: date) -> str:
    """Return a NEW memory text with one dated bullet under the notes heading.

    Pure function: the input text is never modified, which makes it easy to test.
    """
    bullet = f"- {today.isoformat()}: {note}"
    lines = text.rstrip("\n").splitlines()
    if NOTES_HEADING not in lines:
        return "\n".join([*lines, "", NOTES_HEADING, "", bullet]) + "\n"

    start = lines.index(NOTES_HEADING) + 1
    end = next(
        (i for i in range(start, len(lines)) if lines[i].startswith("## ")), len(lines)
    )
    # Insert right after the section's last non-blank line.
    insert_at = end
    while insert_at > start and not lines[insert_at - 1].strip():
        insert_at -= 1
    if insert_at == start:
        new_lines = [*lines[:start], "", bullet, *lines[start:]]
    else:
        new_lines = [*lines[:insert_at], bullet, *lines[insert_at:]]
    return "\n".join(new_lines) + "\n"


def save_note(note: str, path: Path = MEMORY_PATH, today: date | None = None) -> str:
    """Check the note, append it to the memory file, and return the cleaned note."""
    cleaned = check_note(note)
    path = Path(path)
    current = (
        path.read_text(encoding="utf-8") if path.exists() else "# Assistant Memory\n"
    )
    path.write_text(add_note(current, cleaned, today or date.today()), encoding="utf-8")
    return cleaned
