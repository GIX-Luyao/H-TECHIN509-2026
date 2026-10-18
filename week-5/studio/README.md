# Week 5 studio: Set the rules, refactor, verify

Work in pairs. You will agree on rules for your coding agents
and refactor one working FAQ search program.

## Start here

Clone the repo and navigate to the Module 5 Studio directory.
Open a terminal in the folder containing this README and run:

```bash
python3 search.py
```

On Windows, you may want to use `python` instead of `python3` in every command.
The demo selects `password`. If it does not run, ask the instructor for help before continuing. 

## Directory structure

```text
Studio/
├── README.md          # these instructions
├── search.py          # the deliberately repetitive program you refactor
├── evaluate.py        # supplied checks (do not edit)
├── eval_cases.json    # supplied test questions (do not edit)
├── RULE_CARDS.md      # candidate rules for AGENTS.md
├── TEAM_NOTES.md      # the only short record to fill in
│
│   # created during the studio:
├── AGENTS.md          # your agreed rules (Part 1)
├── baseline.json      # saved by `evaluate.py --baseline`; never overwrite
└── after.json         # saved by `evaluate.py --after` (Part 2 and 3)
```

## Part 1 — Choose the rules

**What these files are.** `AGENTS.md` and `CLAUDE.md` are plain Markdown files of standing instructions for a coding agent: how to run the code, what not to touch, and how to make changes. 
The agent reads them at the start of a session, so you don't have to repeat the rules in every prompt.

| File | Read by | Typical contents |
| --- | --- | --- |
| `AGENTS.md` | Open convention shared by many tools (Codex, Cursor, GitHub Copilot, Gemini CLI, …) | "Run `python3 evaluate.py` after every change." "Do not edit `eval_cases.json`." |
| `CLAUDE.md` | Claude Code | Same kind of rules. To reuse one file, put a single line `@AGENTS.md` in `CLAUDE.md`. |

**Why it matters.** Rules written once are applied consistently across sessions and partners. 
They are guidance, not enforcement: the agent may still ignore them, so you check its work.

1. Read `RULE_CARDS.md`. Independently think which rule should be included to `AGENTS.md` or `CLAUDE.md`.
2. Present your choices and agree on include/exclude decisions together.
3. Create `AGENTS.md` beside `search.py` with the included rules.

## Save the baseline BEFORE editing

Run
```bash
python3 evaluate.py --baseline
```

Expected starting result: **5/6 correct**. This saves `baseline.json`. Keep it.
The last question exposes a limitation of the word-count model; do not fix it as part of this refactoring task. Never overwrite the baseline after editing.

## Part 2 — Codebase Refactor

### Independently propose

Each student opens their own copy of the unchanged starter with the same agreed `AGENTS.md`. 
Ask an agent to explain the functionality of `search.py`. Alternatively, you can read the file yourself without using agents.
Based on your understanding of the functionality, think about how to refactor the code using functions. Be specific about the input and output of each function.

Then each student independently works with your agent to propose a plan to refactor the codebase. An example prompt is given below:

> Do not edit any files. Propose at most two small function extractions that remove repeated code. For each function, identify its name, inputs, return value, and places it will be called. Preserve behavior, public interfaces, data, and return shapes. Do not add dependencies or features. 
> Do not change evaluate.py, eval_cases.json, or baseline.json. Wait for our agreement.

Feel free to modify the prompt accordingly. Please pay attention to the boundaries set in the example prompt, especially if you would like to revise the example prompt. 

### Compare and agree

First compare your own proposed functions with your agent's output. Refine either to get your refactor proposal. 

Then each student explains their proposal; Compare repeated code, function inputs/outputs, and how easy each plan is to explain.
Record one agreed plan in `TEAM_NOTES.md`; it may combine the proposals. You can leverage another agent to judge/explain proposals.

### Execute together

Choose ONE working copy with the original baseline as your shared submission.
Do not merge two independently edited versions.

- Extraction 1: Student A directs the agent and operates the keyboard. B reads the diff and checks the function's inputs, return value, and call sites.
- Extraction 2: swap roles. B directs; A reviews.

Run `python3 evaluate.py --after` after each extraction. If it fails, inspect the changed code with your partner and ask the agent for a small correction.
Do not change the checks to make them pass.

## Part 3 — Verify and explain

B runs the final check; A compares it with the baseline:

```bash
python3 evaluate.py --after
```

The command saves `after.json`. Success means **5/6 correct AND PASS**.
The evaluator checks individual FAQ selections and every candidate score, plus small checks of `compare_texts`. An unchanged total alone is insufficient.
Scores may differ only within a tiny numerical tolerance. These checks provide bounded evidence on the supplied examples, not a proof for all possible inputs.

## Submit

Submit a link to your GitHub repo on Canvas. Include your partner's name in the repo's README.md. 
