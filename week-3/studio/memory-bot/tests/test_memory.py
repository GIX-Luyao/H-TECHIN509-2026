"""Checks for the memory bot. Run from the memory-bot folder: python -m pytest

Each test builds a history, does a few things to it, and asserts what the list
should look like afterwards. That is the same hand-trace you did on Zoom, written down.
"""
from backend import NO_NAME
from bot import respond, show
from memory import SYSTEM, add_turn, new_history, request_messages


def test_new_history_has_only_the_system_message():
    history = new_history()
    assert history == [{"role": "system", "content": SYSTEM}]


def test_add_turn_appends_one_dict():
    history = new_history()
    add_turn(history, "user", "hi")
    assert history[-1] == {"role": "user", "content": "hi"}
    assert len(history) == 2


def test_one_exchange_stores_user_then_assistant():
    history = new_history()
    answer = respond(history, "hi")
    roles = [message["role"] for message in history]
    assert roles == ["system", "user", "assistant"]
    assert history[-1]["content"] == answer


def test_backend_receives_the_whole_history():
    history = new_history()
    add_turn(history, "user", "My name is Ada")
    add_turn(history, "assistant", "Nice to meet you, Ada.")
    assert request_messages(history) == history


def test_bot_recalls_a_name_from_an_earlier_turn():
    history = new_history()
    respond(history, "My name is Ada")
    answer = respond(history, "What is my name?")
    assert answer == "Your name is Ada."


def test_question_before_any_name_gets_no_name_reply():
    history = new_history()
    assert respond(history, "What is my name?") == NO_NAME


def test_show_does_not_change_history():
    history = new_history()
    respond(history, "hi")
    length_before = len(history)
    printed = show(history)
    assert "[user] hi" in printed
    assert len(history) == length_before


def test_command_with_trailing_space_still_works():
    history = new_history()
    respond(history, "hi")
    length_before = len(history)
    respond(history, "/show ")
    assert len(history) == length_before


def test_reset_keeps_the_system_message():
    history = new_history()
    respond(history, "My name is Ada")
    respond(history, "/reset")
    assert history == new_history()
    assert respond(history, "What is my name?") == NO_NAME
