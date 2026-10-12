# Memory policy

The model has a limited context window, so a long conversation cannot be sent whole.
Decide what `request_messages()` sends when the history gets long.

- Policy (one sentence, e.g. "the system message plus the last 4 turns"):
- What is dropped first, and why:
- A question the bot will then get wrong. Write the exact conversation:
- Implemented or proposed only:

## The test that encodes the policy

Copy this into `tests/test_memory.py`, replace the TODOs, and run `python -m pytest`.
It is fine if it is red when you leave; the policy is the deliverable.

```python
def test_request_keeps_system_message_and_recent_turns():
    history = new_history()
    for number in range(10):
        add_turn(history, "user", f"message {number}")
        add_turn(history, "assistant", f"reply {number}")
    sent = request_messages(history)
    assert sent[0]["role"] == "system"
    assert len(sent) <= TODO            # system message + how many recent messages?
    assert sent[-1] == history[-1]      # the newest message is always sent
```
