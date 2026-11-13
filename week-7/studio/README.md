# Week 7 studio: Build and ship a feature for your partner

## 1. Your roles

Work in pairs. Each student has two roles:

| Role | Your responsibility |
| --- | --- |
| **Project Owner** | Choose a small feature for your own final project, define its acceptance tests, explain the requirements, and test and accept the delivery. |
| **Developer** | Implement your partner's feature, run the tests, deliver a pull request, and address the owner's feedback. |

You are the **Project Owner of your project** and the **Developer for your partner's project**. Both students develop concurrently, on their partner's repository. Stay available to answer each other's questions.

By the end, each student should have one small feature delivered for their project and one contribution delivered to their partner. Use **one GitHub issue and one pull request per feature**.

## 2. Get ready

Use synthetic or sanitized sample data if any.

As Project Owner:

1. Show your partner how to run the project and its existing tests.
2. Add your partner as a repository collaborator. A private repository is fine; give the instructor access as well.
3. Confirm that you can run `python -m pytest` from the folder containing your project's code and tests. If setup fails, ask for help before proceeding.

Use the Week 7 notebook's class, memory, and `Tool` examples as starting points. Your studio feature should be small enough to implement in **about 60 minutes**.

> **What good looks like.** The steps below include weak and strong examples. They all use one
> made-up feature, an **office-hours lookup**: `find_office_hours(course, csv_path)` reads a small
> CSV and returns the office-hours slot for a course. Use it to judge your own work; don't copy it as your feature.

## 3. Project Owner: choose a feature and define the tests first

Choose **one** feature that helps your final-project assistant. For example:

- A tool that looks up a deadline or contact from a small local dataset.
- A tool that performs a simple calculation relevant to your project.
- A memory method that keeps a limited number of recent messages while preserving the system message.
- Saving and restoring a conversation using the lesson's example.

Choose a small function or method with clear inputs and outputs. A tool can be called directly for this studio; connecting it to the agent loop can follow later.

**Before implementation, write at least two acceptance tests:**

1. A normal input with its expected result.
2. An edge case with its expected behavior.

Use `pytest` and the lesson's test examples. Test the **deterministic** function behaviors.

As the owner, you should provide test sample data to your developer so that they can validate the function behaviors.

Commit and push the tests and sample data to your project's default branch before the developer starts. Please clearly document your tests so that your developer is clear about which ones to run.

<details>
<summary><b>What good looks like: acceptance tests</b></summary>

Sample data, `tests/data/office_hours_sample.csv` (synthetic):

```text
course,slot
TECHIN 509,Tue 3:00-4:00 PM (Room 270)
TECHIN 510,Thu 10:00-11:00 AM (Zoom)
TECHIN 513,Mon 1:00-2:00 PM (Room 214)
```

**Weak**

```python
def test_office_hours():
    result = find_office_hours("TECHIN 509")
    assert result is not None
```

- It passes even if the function returns the wrong slot, or any string at all.
- There is no edge case, so the developer has to guess what happens for an unknown course.
- It doesn't say which data to use or how to run it.

**Strong**

```python
"""Acceptance tests for the office-hours lookup (issue #3).

Run:  python -m pytest tests/test_office_hours.py -v
Data: tests/data/office_hours_sample.csv (synthetic)
"""
from pathlib import Path

from ribot.office_hours import find_office_hours

SAMPLE = Path(__file__).parent / "data" / "office_hours_sample.csv"


def test_known_course_returns_its_slot():
    assert find_office_hours("TECHIN 509", SAMPLE) == "Tue 3:00-4:00 PM (Room 270)"


def test_unknown_course_returns_not_found_instead_of_raising():
    assert find_office_hours("TECHIN 999", SAMPLE) == "Not found"
```

- Each test asserts an **exact** expected value taken from the sample data.
- The test names state the behavior, so a failing test explains itself.
- The edge case pins a decision the owner made: return `"Not found"` and don't raise.
- The file header tells the developer what to run and which data it uses.

</details>

## 4. Project Owner: communicate the requirements

Create one GitHub issue in your repository. Keep it short; use this template:

```text
Title: Add [one small feature]

Purpose: My assistant needs this to ...
Build: [function/method name, inputs, return value, and important behavior]
Start here: [code file, sample data, and useful lesson example]
Acceptance tests: [test file and exact command to run it]
Out of scope: [what should remain unchanged]
```

<details>
<summary><b>What good looks like: the issue</b></summary>

**Weak**

```text
Title: office hours

Can you add office hours to my bot? Tests are in the repo. Thanks!
```

The developer has to guess the function name, the return value, what happens for an unknown
course, which test to run, and where to stop.

**Strong**

```text
Title: Add office-hours lookup

Purpose: My assistant needs this to answer "when are office hours for TECHIN 509?"
  from local data instead of guessing.
Build: find_office_hours(course: str, csv_path) -> str in ribot/office_hours.py.
  Returns the slot for an exact course match. Returns "Not found" for an
  unknown course; never raises.
Start here: tests/data/office_hours_sample.csv; Week 7 lesson, Tool section
  (for context only).
Acceptance tests: tests/test_office_hours.py
  Run: python -m pytest tests/test_office_hours.py -v
Out of scope: wrapping it as a Tool, the agent loop, fuzzy matching,
  any change to chatbot.py.
```

</details>

Show the developer the issue and walk through your two tests. Explain how the feature will help your final-project agent.

**Developer:** explain the request back to the owner before editing:

> "I will implement ___ in ___. Given ___, it should return ___. For the edge case, it should ___. I will check it with ___."

Resolve differences now. Agree on the function signature, expected behavior, and scope. Put any clarification in the issue; a short comment is enough. Repeat this conversation for the other student's project.

## 5. Developer: implement your partner's feature

Clone your partner's repository into a separate folder. Please confirm owner’s need before implementing anything to avoid unnecessary iterations.

Use the owner's setup instructions and run the acceptance tests **before** editing. You should expect failures from tests. Your goal is to turn these tests green, i.e., passing tests.

1. Read the issue, tests, sample data, and relevant existing code.
2. Implement the smallest change that satisfies the agreed behavior with your agent.
3. Run the acceptance tests until they pass.
4. Run the existing test suite and check for new failures.
5. Ship your deliverable to owner.

**Do not weaken an assertion or hardcode the test answers.** Implement the agreed behavior using the supplied data. If a test contradicts the requirement, discuss it with the owner. The owner must agree to the test changes.

Commit the relevant files and push your branch. Open a pull request into the owner's default branch and request the owner's review. Include only:

```text
Closes #<issue-number>

Change: [one sentence]
Verification: [commands run and results]
```

<details>
<summary><b>What good looks like: the implementation and the PR</b></summary>

**Weak implementation (hardcoded to the tests)**

```python
def find_office_hours(course, csv_path):
    if course == "TECHIN 509":
        return "Tue 3:00-4:00 PM (Room 270)"
    return "Not found"
```

Both acceptance tests pass, but the function never reads the CSV. Any other course returns
`"Not found"`. The owner's extra input in step 6 is there to catch this.

**Weak PR description**

```text
Fixed it. Tests pass now.
```

**Strong PR description**

```text
Closes #3

Change: Add find_office_hours() in ribot/office_hours.py; it reads the CSV and
  returns the slot for an exact course match, or "Not found".
Verification:
  python -m pytest tests/test_office_hours.py -v  -> 2 passed
  python -m pytest                                -> 14 passed (same as main before the change)
```

The strong version links the issue, so merging closes it. It says what changed in one sentence and
gives the reviewer the exact commands to rerun, with results to compare against.

</details>


## 6. Project Owner: run the tests and review the delivery

Test the developer's branch yourself. First ensure your own work is committed and `git status` is clean. If it is not, save your work before switching branches. For the branch name above:


1. Run the acceptance-test command from your issue.
2. Run the existing test suite and compare it with the starting results.
3. Try one additional input within the agreed scope, using your sample data to determine the expected result.
4. Ask the developer to explain anything you do not understand.

Leave a GitHub review:

- **Approve** if the agreed behavior works and the change is understandable.
- **Request changes** if it does not. Give the input, expected result, actual result, and command that reproduces the problem.

For example: "For an unknown ID, I expected `Not found`, but the function raises `KeyError`. Running the second acceptance test reproduces this."

<details>
<summary><b>What good looks like: the review</b></summary>

**Weak approve:** `LGTM 👍`
It doesn't say what you ran, so you may have approved code you never tested.

**Weak request changes:** `Doesn't work for other courses, please fix.`
It doesn't say which course, what you expected, or how to reproduce it, so the developer has to
investigate from scratch.

**Strong request changes** (this catches the hardcoded version above):

```text
Input:    find_office_hours("TECHIN 510", "tests/data/office_hours_sample.csv")
Expected: "Thu 10:00-11:00 AM (Zoom)"  (row 3 of the sample CSV)
Actual:   "Not found"
Reproduce:
  python -c "from ribot.office_hours import find_office_hours; print(find_office_hours('TECHIN 510', 'tests/data/office_hours_sample.csv'))"
Both acceptance tests pass, but the function doesn't seem to read the CSV.
```

**Strong approve:**

```text
Ran python -m pytest tests/test_office_hours.py -v: 2 passed.
Full suite: 14 passed, same as main before the PR.
Extra input: "TECHIN 513" returned "Mon 1:00-2:00 PM (Room 214)", matching the CSV.
I can follow the code and the CSV parsing. Approving.
```

</details>

Evaluate the feature you agreed on. Put new feature ideas in a separate future issue rather than adding them to this delivery.

## 7. Developer: revise. Project Owner: accept and merge.

**Developer:** address the review, rerun the tests, and push the correction to the same branch. The PR updates automatically. Reply briefly with what changed.

**Project Owner:** pull the updated branch, rerun the checks, and approve and merge when satisfied. Close the issue if GitHub has not already closed it. Return to your default branch and pull the merged result.


## What a complete delivery looks like

The instructor checks these items on GitHub. Your owner work is in your own repo. Your developer
work is the PR you opened in your partner's repo.

**As Project Owner (your repo)**

- [ ] Tests and sample data are on the default branch, committed **before** the developer's PR.
- [ ] At least one normal-case and one edge-case test, each asserting an exact expected value. The test file says how to run it.
- [ ] Sample data is synthetic: no real names, emails, IDs, or secrets.
- [ ] One issue that follows the template. Any clarification is added as an issue comment.
- [ ] A review that says what you ran and which extra input you tried. A "Request changes" review gives input, expected result, actual result, and a reproduce command.
- [ ] The PR is merged, the issue is closed, and no branch is deleted.

**As Developer (your PR in your partner's repo)**

- [ ] The PR description has `Closes #n`, a one-sentence change, and verification commands with their results.
- [ ] The diff touches only the agreed feature. No assertion is weakened and no test is deleted without the owner's agreement in a comment.
- [ ] No hardcoded test answers: the code works from the supplied data.
- [ ] Review feedback is addressed with a new commit on the same branch, plus a short reply saying what changed.

**Both:** `python -m pytest` passes on the default branch after the merge.

## Deliverables

Submit the link to Github repo where you work as the owner. Do not delete any branch.
