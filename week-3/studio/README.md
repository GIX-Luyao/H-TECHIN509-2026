# Week 3 — Brownfield Rescue Mission

**Understand, diagnose, and safely fix unfamiliar assistant code.**

You have inherited an assistant. Its original engineer has left, a user reports an incorrect response, and its README is out of date. Your job is to understand the system before changing it, then produce a small, defensible repair.


## Session route

| Time | Activity | Evidence |
|---|---|---|
| 0:00–0:10 | Read the [incident brief](rescue/INCIDENT.md), assign roles, define success | Expected behavior and initial prediction |
| 0:10–0:30 | Understand: inspect the inherited files without editing | Architecture/data-flow sketch |
| 0:30–0:55 | Diagnose: reproduce, trace, and test a hypothesis | Baseline output and history trace |
| 0:55–1:15 | Fix: make the smallest safe change and verify | Reviewed diff and regression evidence |
| 1:15–1:25 | Break, rotate roles, then open the [constraint reveal](rescue/REVEAL.md) | Revised acceptance checks |
| 1:25–1:45 | Attack the repair and decide the memory policy | Boundary-case record |
| 1:45–2:05 | Exchange repairs for peer review; reproduce a partner’s checks and challenge the diff | Independent verification and review notes |
| 2:05–2:25 | Demo and cross-examination | Before/after behavior, limitation, repair decision |
| 2:25–2:30 | Log, review, and commit | Agent Engineering Log and shipped/blocked line |

## 1. Set up the case

Copy the entire [rescue folder](rescue/) into `exercises/week3-rescue/` in your own repository. Keep the packet files together. Do not replace your working `ribot/` application with this deliberately broken exercise or initialize a nested repository.

From the copied folder:

```text
python -m unittest -v
python assistant.py
```

The starting suite has **7 passes and 1 intentional failure**. Save the output before editing. Read [INCIDENT.md](rescue/INCIDENT.md) for the current behavior contract; the inherited [README](rescue/README.md) is evidence to check, not an authoritative specification.

## 2. Understand, diagnose, then repair

Follow the [investigation guide](investigation.md). Copy [RESCUE_RECORD.md](templates/RESCUE_RECORD.md) to `docs/WEEK3_RESCUE_RECORD.md`. Draw the data flow and record a hypothesis before making changes. Keep supplied checks intact; add your own checks in a separate `test_*.py` file.

Team roles:

- **Incident lead:** maintains the timeline, hypothesis, and acceptance criteria, traces dictionaries, lists, branches, and evidence.
- **Agent navigator:** requests explanations and targeted searches; reviews every suggestion.

Rotate roles at the reveal. 

**AI use:** Record assistance in your Agent Engineering Log. An unavailable agent should not block the mission.

## 3. Reveal, challenge, and review

Open [REVEAL.md](rescue/REVEAL.md) only after the first repair attempt or supported diagnosis. Complete the memory-policy and boundary sections of your rescue record. Exchange your repair with another pair: have them reproduce your checks, inspect the diff.

## 4. Demo and hand off

Without AI, walk through the exact list passed to the reply backend. Explain your memory policy, one boundary limitation, and why your repair is the smallest safe change. 

Use the [Git checklist](GIT_CHECKLIST.md). Before leaving, commit:

- `exercises/week3-rescue/`: your minimal repair or documented attempt, supplied checks, and added regression checks.
- `docs/WEEK3_RESCUE_RECORD.md`: architecture sketch, hypothesis–test–change–verification record, memory policy, boundary cases, and demo note.
- A Week 3 entry in `docs/AGENT_ENGINEERING_LOG.md` using the [template](templates/AGENT_ENGINEERING_LOG.md).
