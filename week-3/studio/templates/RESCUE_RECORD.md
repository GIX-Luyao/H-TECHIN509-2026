# Week 3 rescue record

Save as `docs/WEEK3_RESCUE_RECORD.md`. Use synthetic evidence only.

## Team and acceptance criteria

- Date, teammates, initial roles, and rotations:
- Reported symptom and expected behavior:
- Acceptance criteria before editing:

## Architecture / data-flow sketch

Draw or describe input → command branches → history mutation → request preparation → backend → reply append → output. Include file/function references, the system message, and the distinction between stored and sent history.

- Inherited README claims: confirmed / contradicted / untested, with evidence:
- Predicted and observed list of dictionaries after each incident input:

## Hypothesis–test–change–verification

| Step | Evidence |
|---|---|
| Reproduction command and baseline output | |
| Hypothesis and an observation that would disprove it | |
| Diagnostic test and actual observation | |
| Smallest change and why it addresses the cause | |
| Added regression check: original failure and repaired result | |
| Full-suite result and terminal replay | |
| Diff review, reviewer, and remaining uncertainty | |

## Memory policy after reveal

- Implemented / proposed only:
- What is kept, dropped, or summarized, and why:
- Definition of turn, window size, system-message treatment:
- Stored history versus request limit; exact trimming point:
- Budget calculation after 20 and 200 completed exchanges:
- Oversized-message behavior and estimate limitations:
- Accepted failure and the question that exposes it:

| Boundary | Prediction | Observed result or explicitly labeled manual trace | Decision / limitation |
|---|---|---|---|
| Fresh conversation and actual empty list | | | |
| Long message | | | |
| `/reset` | | | |
| `/exit` | | | |
| At / beyond memory limit | | | |

## Demo and handoff

- Repaired behavior or predicted memory failure shown:
- Independent peer review: reviewer, reproduced checks, challenged case, and my response:
- What I understood only after trying to break the system:
- What remains broken or unverified and next diagnostic step:
- README correction made:
- Commit / repository URL:
- Shipped: <verified behavior> OR Blocked: <specific blocker and next step>:
