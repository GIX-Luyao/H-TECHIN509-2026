# memory-bot

A terminal bot whose memory is a list of dicts.

```text
memory-bot/
├── bot.py        # the while loop and the commands /show, /reset, /exit
├── memory.py     # new_history(), add_turn(), request_messages()
├── backend.py    # reply(messages): an offline stand-in for a model that remembers a name
├── tests/        # python -m pytest
└── docs/         # filled in during the session
    ├── TRACE.md
    └── MEMORY_POLICY.md
```

## Run it

```text
python bot.py
python -m pytest
```

Expect **5 passed, 4 failed** before any fix. If `pytest` is missing: `uv pip install pytest`.

## Open issues

Fix each one on its own branch, through a pull request your partner reviews.

**Issue 1. The bot forgets my name.**
A user typed `My name is Ada`, then `What is my name?`, and got "I do not know your name yet."
`/show` proves the name is stored. Compare the stored list with the list `reply()` receives.
Red tests: `test_backend_receives_the_whole_history`, `test_bot_recalls_a_name_from_an_earlier_turn`.

**Issue 2. A command with a trailing space is treated as a message.**
Typing `/show ` adds a user turn and gets a "Noted" reply instead of showing the history.
Red test: `test_command_with_trailing_space_still_works`.

**Issue 3. `/reset` deletes the system message.**
After `/reset` the history is empty instead of holding the system message.
Red test: `test_reset_keeps_the_system_message`.

## Rules

- Keep the existing tests unchanged. Add new tests below them. Please work with your agent when preparing new tests as unit test is not covered in class yet.
- Smallest change that makes the red test green. Do not rewrite files.
- AI can be used for coding assistance and explaining errors.
