# Choose your agent rules

Copy or customize included rules into `AGENTS.md` in this folder.

1. Read the relevant code before proposing changes.
2. Propose a plan and wait for our agreement before editing.
3. Preserve existing behavior during refactoring.
4. Run the supplied evaluation before and after changes.
5. Explain each extracted function's parameters and return value.
6. Rewrite the entire program to make it as elegant as possible.
7. Add any packages that might make the code better.
8. If an evaluation fails, change the expected answer so it passes.
9. Code you write or change in `search.py` should follow PEP 8; don't reformat untouched code or add formatting tools.

**The task boundaries below must apply regardless of your selections**:
edit only `search.py` during refactoring; keep the public `search(query)` and
`compare_texts(first, second)` interfaces and return shapes; leave the FAQ data, vocabulary, evaluator, evaluation cases, and saved baseline unchanged.
No new dependencies, live model calls, or feature additions.
