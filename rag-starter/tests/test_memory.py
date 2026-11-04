"""Week 10: tests for the markdown assistant memory. Fully offline."""

from datetime import date

import pytest

from ribot.memory import (
    MAX_MEMORY_CHARS,
    NOTES_HEADING,
    add_note,
    check_note,
    load_memory,
    memory_block,
    save_note,
)

TEMPLATE = """# Assistant Memory

Intro paragraph that explains the file to a human.

## Preferences

- Tone: plain and direct
- Formatting:

## Glossary

- Term:
  - Meaning:

## Audit Notes

- Memory claim checked: tone
"""


def test_load_memory_keeps_only_filled_lines(tmp_path):
    path = tmp_path / "assistant_memory.md"
    path.write_text(TEMPLATE, encoding="utf-8")
    memory = load_memory(path)
    assert "- Tone: plain and direct" in memory
    assert "## Preferences" in memory
    # Blank template fields, empty sections, the intro, and audit notes are dropped.
    assert "Formatting" not in memory
    assert "## Glossary" not in memory
    assert "Intro paragraph" not in memory
    assert "Audit" not in memory


def test_load_memory_missing_file_is_empty(tmp_path):
    assert load_memory(tmp_path / "nope.md") == ""


def test_memory_block_frames_memory_as_not_evidence():
    block = memory_block("## Preferences\n- Tone: plain")
    assert "- Tone: plain" in block
    assert "not evidence" in block.lower()


def test_memory_block_empty_and_capped():
    assert memory_block("") == ""
    huge = "## Notes\n" + "- x\n" * MAX_MEMORY_CHARS
    assert len(memory_block(huge)) < MAX_MEMORY_CHARS + 400


@pytest.mark.parametrize(
    "bad",
    [
        "",
        "   ",
        "x" * 500,
        "my key is sk-abcdefghijklmnop",
        "email me at jane.doe@example.com",
        "call 206-555-0142",
    ],
)
def test_check_note_rejects_empty_long_secret_or_personal(bad):
    with pytest.raises(ValueError):
        check_note(bad)


def test_check_note_collapses_whitespace():
    assert check_note("  prefers   bullet\npoints ") == "prefers bullet points"


def test_add_note_is_pure_and_creates_section():
    original = "## Preferences\n- Tone: plain\n"
    updated = add_note(original, "prefers bullet points", date(2026, 11, 2))
    assert original == "## Preferences\n- Tone: plain\n"  # unchanged
    assert NOTES_HEADING in updated
    assert "- 2026-11-02: prefers bullet points" in updated


def test_add_note_appends_inside_existing_section():
    text = f"{NOTES_HEADING}\n\n- 2026-11-01: first\n\n## Later\n- other: x\n"
    updated = add_note(text, "second", date(2026, 11, 2))
    notes_part = updated.split("## Later")[0]
    assert "- 2026-11-01: first" in notes_part
    assert "- 2026-11-02: second" in notes_part


def test_save_note_writes_and_round_trips(tmp_path):
    path = tmp_path / "assistant_memory.md"
    path.write_text(TEMPLATE, encoding="utf-8")
    saved = save_note("prefers  bullet points", path, today=date(2026, 11, 2))
    assert saved == "prefers bullet points"
    assert "- 2026-11-02: prefers bullet points" in load_memory(path)


def test_save_note_rejects_without_writing(tmp_path):
    path = tmp_path / "assistant_memory.md"
    path.write_text(TEMPLATE, encoding="utf-8")
    with pytest.raises(ValueError):
        save_note("jane.doe@example.com", path)
    assert path.read_text(encoding="utf-8") == TEMPLATE
