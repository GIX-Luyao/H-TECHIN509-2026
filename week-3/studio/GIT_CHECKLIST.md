# Week 3 rescue handoff checklist

Work in your own project repository. For initial GitHub setup, use the [Week 1 checklist](../../Module%201/Studio/GIT_CHECKLIST.md). Keep the inherited case in `exercises/week3-rescue/` without a nested repository.

## Verify and review

From `exercises/week3-rescue/`, run `python -m unittest -v` and replay the incident. Record actual results, including remaining failures. Then return to your repository root:

```text
git status --short
git diff
git check-ignore .env
git ls-files .env
```

The ignore check should print `.env`; the tracked-file check should print nothing. Read new untracked files separately. If secrets or unapproved originals were tracked, get help before pushing; deleting a current file does not remove history.

Confirm your packet includes the architecture sketch, diagnostic record, minimal fix or diagnosis, memory policy, all boundary cases, peer-review evidence, demo note, and Week 3 Agent Engineering Log entry. Exclude `__pycache__`, virtual environments, private originals, and credentials.

## Stage and push

Stage only reviewed files; 

Verify the remote is your own repository. Use `git push` if the branch already tracks it; otherwise use `git push -u origin YOUR_BRANCH`, replacing `YOUR_BRANCH` with its actual name.

Refresh GitHub with your partner and confirm the branch, commit, code and records. Arrange instructor access for a private repository. Record the shipped/blocked line and post the required cohort check-in before next week's Zoom.
