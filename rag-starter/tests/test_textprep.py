"""Week 7: example tests for the Week 4 text-prep functions."""

import pytest

from ribot.textprep import build_conv, clean_message, safe_clean


def test_clean_message_strips_and_lowercases():
    assert clean_message("  Hello,   WORLD!! ") == "hello world"


def test_clean_message_empty():
    # edge case: empty input should not crash
    assert clean_message("   ") == ""


def test_build_conv_pairs_records():
    conv = build_conv(["Q one?"], ["A one."])
    assert conv == [{"user": "q one", "bot": "a one"}]


def test_safe_clean_handles_bad_input():
    # expected-failure case: a non-string must not raise
    assert safe_clean(None) == ""


@pytest.mark.parametrize("raw,expected", [("A B", "a b"), ("x!", "x"), ("  z ", "z")])
def test_clean_message_parametrized(raw, expected):
    assert clean_message(raw) == expected
