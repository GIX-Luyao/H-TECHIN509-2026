# AI Coding Agent Arena

Repair a small document-search program. It uses synthetic data and needs only Python 3.10+. Note that the repo is intentionally broken, and if you encounter them, fix it with your team.

## Run the starting checks

Open a terminal in this `arena` folder:

```text
python -m unittest -v
python search.py
```

Use `python3` or `py` if that is your Python command. Expect **2 passing and 5 failing tests** at the start. Save the output.

## Your task

Edit `search.py`. `Library(path)` loads a JSON list of documents with `source` and `text`. `search(query, limit=3)` should:

- Match a substring of the text, ignoring case.
- Trim spaces around the query.
- Return `[]` for blank queries or no matches.
- Return at most `limit` documents; return `[]` for a zero limit.
- Preserve each result's text and source.

Keep the supplied data and tests unchanged. Add checks in a separate `test_*.py` file. Do not hard-code answers or add a model/API dependency.

## Verify your work

1. Follow your assigned workflow in the [session instructions](../README.md).
2. Read [the additional requirement](REVEAL.md), rotate roles, and update your checks.
3. Review the diff, rerun all checks, and test an additional case.
4. Complete the [Arena record](../templates/ARENA_RECORD.md). Explain the data flow: JSON → library → query → matching text and source.

If blocked, record the command, expected and observed result, likely cause, and next check. A supported diagnosis is an acceptable outcome.
