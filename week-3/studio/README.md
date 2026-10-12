# Week 3 in-person session — Fix the Forgetful Bot, by Pull Request

You work in pairs on one shared GitHub repository, each on your own laptop. Everything you
need is Week 1 Git, Week 2 strings, and Week 3 lists of dicts. No API key. Synthetic data only.

Bring: your laptop, GitHub login, and the `rag-starter` environment that ran `python -m ribot.chatbot`.

## Session order

1. Clinic and setup
2. Trace the incident
3. Fix issues by pull request
4. Cross-pair bug hunt
5. Memory policy
6. Demos and live check
7. Push and log

## 1. Clinic and setup

Form pairs. Then **one partner**:

1. Creates a new GitHub repository named `week3-memory-bot` (private is fine).
2. Copies the [memory-bot](memory-bot/) folder into it, commits, pushes.
3. Adds the partner as a collaborator (Settings → Collaborators).

**Both partners** clone it, then from the `memory-bot` folder run:

```text
python bot.py
python -m pytest
```

Expect **5 passed, 4 failed**. Read [memory-bot/README.md](memory-bot/README.md) together.

## 2. Trace the incident

Partner A runs `python bot.py` and types the four lines in [docs/TRACE.md](memory-bot/docs/TRACE.md).
Partner B runs `python -m pytest` and reads the first failing test, top to bottom.

Fill in `docs/TRACE.md` together: predict the history after each line, then check with `/show`.
Find the one line of code that explains why the name is stored but not recalled. Commit the
trace to `main`.

## 3. Fix issues by pull request

For each of the three issues in the memory-bot README, one partner fixes, the other reviews.
Swap roles after each issue.

**Fixer**: Make the smallest change. Run `python -m pytest`. Commit, push, open a pull request on GitHub.

**Reviewer** reviews on your own laptop.
Read the diff on GitHub. Approve if the red test is green and nothing else broke; otherwise
request changes and say what to change. Merge. Both partners `git checkout main` and `git pull`.

Do not edit the supplied tests. You may ask agent to explain 
an error message.

## 4 (Optional). Cross-pair bug hunt

Swap with another pair. Each pair clones the other pair's repository and follows
[bug-menu.md](bug-menu.md): plant one bug on a branch, open a pull request titled `memory change`. You may need to be added as a collaborator to the repo.

Review the pull request you receive: run the tests on the branch, read the diff, and write
one review comment naming the bug, the symptom a user would see, and the test that catches it
(or the test you would add). Request changes. Do not merge.

## 5. Memory policy

Back in your own pair repository, open [docs/MEMORY_POLICY.md](memory-bot/docs/MEMORY_POLICY.md).

One partner writes the policy: what `request_messages()` sends when the conversation is long,
and the exact conversation that will then go wrong. The other partner copies the test template
into `tests/test_memory.py` and fills in the number.

Floor: the policy written and the test committed, red or green.

## 6. Push and log

Complete the Week 3 entry from [templates/AGENT_ENGINEERING_LOG.md](templates/AGENT_ENGINEERING_LOG.md)
to `docs/AGENT_ENGINEERING_LOG.md`, including the pair repository URL. Push your repo to remote. **If your repo is private, please add your instructor to it for access.**

## Before you leave

The pair repository contains:

- Issues 1 to 3 merged through pull requests, `python -m pytest` green on `main`.
- `docs/TRACE.md` filled in.
- (Optional). One review comment on another pair's `memory change` pull request.
- `docs/MEMORY_POLICY.md` plus the policy test.
