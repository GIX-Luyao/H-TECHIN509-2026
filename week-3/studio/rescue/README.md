# Helpdesk assistant — inherited handoff

> Exercise artifact: this handoff is out of date. Compare its claims with the current incident contract and running code.

Run `python assistant.py`. No installation is needed.

The assistant remembers earlier project details. `/show` displays the same context used to produce the last reply. `/reset` starts a new conversation. `/exit` quits.

History automatically keeps the most recent six messages, so request size is bounded. The backend is a local deterministic stand-in; this repository has no network client.

Files: `assistant.py` handles the terminal, `memory.py` prepares conversation context, and `backend.py` produces replies. Run checks with `python -m unittest -v`.
