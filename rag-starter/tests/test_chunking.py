"""Week 7: example tests for chunk_text."""

import pytest

from ribot.chunking import chunk_text


def test_chunks_cover_text_with_overlap():
    chunks = chunk_text("abcdefghij", size=4, overlap=1)
    assert chunks[0] == "abcd"
    assert chunks[1].startswith("d")  # overlap of 1 char


def test_short_text_is_one_chunk():
    assert chunk_text("hi", size=100, overlap=10) == ["hi"]


def test_overlap_must_be_smaller_than_size():
    with pytest.raises(ValueError):
        chunk_text("abc", size=2, overlap=2)
