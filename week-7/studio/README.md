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

Evaluate the feature you agreed on. Put new feature ideas in a separate future issue rather than adding them to this delivery.

## 7. Developer: revise. Project Owner: accept and merge.

**Developer:** address the review, rerun the tests, and push the correction to the same branch. The PR updates automatically. Reply briefly with what changed.

**Project Owner:** pull the updated branch, rerun the checks, and approve and merge when satisfied. Close the issue if GitHub has not already closed it. Return to your default branch and pull the merged result.


## Deliverables

Submit the link to Github repo where you work as the owner. Do not delete any branch.
