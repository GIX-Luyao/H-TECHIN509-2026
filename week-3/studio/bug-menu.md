# Bug menu for the cross-pair hunt

Pick **one**. Plant it on a branch in the other pair's repo and open a pull request titled
`memory change`. Do not say which bug. Keep the diff to one or two lines.

| Bug | Where | The change |
|---|---|---|
| A | `memory.py` `add_turn` | Swap the two values: `{"role": content, "content": role}` |
| B | `bot.py` `respond` | Move `add_turn(history, "user", text)` to after the `reply(...)` line |
| C | `bot.py` `respond` | Replace `history.clear()` with `history.pop()` |
| D | `backend.py` `reply` | Remove `.lower()` from the `latest = ...` line |
| E | `bot.py` `show` | Add `if message["role"] == "user":` above the `lines.append(...)` line |

The reviewing pair runs `python -m pytest` on the branch, reads the diff, and writes one review
comment: the bug, the symptom a user would see, and the test that catches it. If no test
catches it, the comment names the test you would add. Request changes; do not merge.
