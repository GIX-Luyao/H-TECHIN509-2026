# Week 1 in-person session

Bring your laptop, course repository, and your preferred coding agent. Use only synthetic or sanitized data.

## 1. Check your setup

From your `rag-starter` folder, run:

```text
python scripts/check_env.py
```

No API key or extra packages are needed for this check or the Arena. If blocked, record the error and work with a partner.

## 2. Complete the AI Coding Agent Arena

1. Open the [Arena task and code](arena/README.md). Work in pairs or a small team; choose a human lead, agent operator, and reviewer. In a pair, the lead also reviews.
2. Run the starting checks and save the results.
3. Use your one of the workflows below. If you prefer a different workflow, articulate it and use it. However, after your role rotation within team, you should pick a different workflow.
   - **Vibe:** ask the agent for an approach, then agree on the task and checks before approving edits.
   - **Specification-first:** write the requirements and acceptance checks before asking for code.
   - **Verification-first:** inspect the checks and add a case before asking for code.
4. Open the [additional requirement](arena/REVEAL.md), rotate roles, and revise your approach.
5. Review the diff, run the checks, and test one additional case. Record a working change or explain what remains broken.
6. Compare results with other teams. Complete the [Arena record](templates/ARENA_RECORD.md) and save it as `docs/ARENA_RECORD.md`.

Keep your Arena code and checks in `exercises/week1-arena/` for submission.

## 3. Scope your chatbot

Follow [Build Your Bot Circle](build-your-bot-circle.md). Use the [scope template](templates/SCOPING.md) to write `docs/SCOPING.md`. See the [example](SCOPING_EXAMPLE.md) if needed.

Explain your user, problem, smallest useful version, safe document sources, and a measurable success criterion. Ask a partner to challenge your idea, then record your revision.

## 4. Review and push

1. Explain your scope and answer classmates' questions without AI.
2. Complete your [Agent Engineering Log](templates/AGENT_ENGINEERING_LOG.md) in `docs/AGENT_ENGINEERING_LOG.md`.
3. Follow the [Git checklist](GIT_CHECKLIST.md). Commit and push your code and documents.
5. Record `shipped: <repository URL>` or `blocked: <specific blocker>` in your engineering log.

## Before you leave

Your GitHub repository should contain:

- Arena code/checks or a supported diagnosis, plus `docs/ARENA_RECORD.md`.
- `docs/SCOPING.md`, including one peer-review revision.
- `docs/AGENT_ENGINEERING_LOG.md` with verification results and your shipped/blocked line.

**AI use:** agent-generated code is allowed in the Arena. For scoping, use AI for questions and critique, then write your own brief. Defend your scope without AI. Independent assignments retain their explain/debug-only policy.
