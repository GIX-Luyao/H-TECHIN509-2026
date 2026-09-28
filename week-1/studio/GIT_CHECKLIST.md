# Week 1 repository release checklist

Work in your **own copy of `rag-starter`**, not the instructor's course repository. Copy the complete `rag-starter` folder from the course checkout, including `.gitignore`. Do not create a nested Git repository inside a course clone; place your personal project outside that clone.

## Inspect before staging

```text
git status
```

If this says “not a git repository,” initialize **your project folder**:

```text
git init -b main
```

If it already is a repository, check `git branch --show-current` and use that branch in the push command below. Do not rename an existing branch just to match this example.

```text
git check-ignore .env
git ls-files .env
git status --short
```

The first command must print `.env`; the second must print nothing. The starter already includes the ignore rule. No real key is needed to check it. If `.env` is tracked, stop and ask for help before pushing; an ignore rule cannot remove a secret from history. Review any existing history locally with `git log -p`; do not paste sensitive output into an agent or submission.

Stage only reviewed files. For a newly copied starter, this includes the code needed to reproduce your environment:

```text
git add .gitignore README.md SECURITY.md SETUP_TROUBLESHOOTING.md pyproject.toml requirements.txt uv.lock ribot scripts tests data docs
```

If you saved Arena code locally, also run `git add exercises/week1-arena`. Do not stage private source documents; use only the supplied synthetic fixtures or your approved safe data.

```text
git diff --cached --stat
git diff --cached
git status --short
git commit -m "Prepare Week 1 project scope and studio evidence"
```

Read the staged diff before committing. It must contain no `.env`, keys, personal/confidential material, or virtual-environment files.

## Connect and push

Create an **empty** GitHub repository (without a generated README). Choose public or private; for private, invite the instructor through repository access settings.

```text
git remote -v
```

If there is no `origin`, run `git remote add origin YOUR_REPOSITORY_URL`, replacing the placeholder with your own URL. If `origin` points at the course repository, verify your personal URL before using `git remote set-url origin YOUR_REPOSITORY_URL`. Do not push to the instructor's repository or use force-push.

For a new repository on `main`:

```text
git push -u origin main
```

For an existing branch, substitute its actual name. If authentication or permissions fail, record the exact error without tokens and get help.

## Partner verification

Refresh GitHub. Verify the URL and branch, `ribot/`, `scripts/check_env.py`, `.gitignore`, and your `docs/` files. Confirm `.env` and `.venv` are absent. A private repository must have an instructor invitation/access arranged; your partner can verify on your screen without making it public. After the peer-review revision, commit and push again and verify that final commit on GitHub.
