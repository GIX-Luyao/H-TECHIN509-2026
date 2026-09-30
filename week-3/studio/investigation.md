# Investigation guide

## Understand before editing

Read the incident, inherited README, entry point, backend, memory helper, and supplied checks. Draw the actual execution path from terminal input to printed response. Identify:

- Where history is created and the shape of each message dictionary.
- Which branches handle commands and which handle ordinary text.
- When user and assistant messages are appended.
- Which list is passed to the backend and which list `/show` displays.
- What `/reset` changes and what `/exit` returns to the loop.

Mark README claims as confirmed, contradicted, or untested. Do not infer runtime behavior from comments alone. Record file/function references in your sketch.

## Reproduce and diagnose

Run the supplied suite and the exact incident transcript. Save the baseline. Predict the state after every input, then inspect it using `/show` or temporary local prints. Record the contents of the backend request as well as stored history.

State one falsifiable hypothesis. Identify the smallest observation that would reject it. Run that check before editing. Explain how the evidence supports or rejects your hypothesis; a plausible agent explanation is not evidence by itself.

Optional agent prompt:

> Explain the path from input to response in these files, with function references. Do not edit files or propose a patch yet. Separate observed behavior from assumptions, and identify one observation that could disprove my hypothesis.

## Make the smallest safe repair

Write the expected behavior first. Change only what your diagnosis supports. Preserve command behavior, the system message, message ordering, and the backend interface. Do not rewrite the assistant, hard-code the reported answer, weaken checks, or introduce a live model.

Add at least one regression check beyond the supplied suite. It must catch the original defect, not just repeat the incident with the same fixture. Demonstrate that it fails on the original code and passes on your repair, using a separate copy if needed; preserve your working files.

Rerun all checks and repeat the terminal transcript. Read the diff with your partner. Remove temporary debugging prints or explain why an intentional diagnostic remains. Update the inherited README to reflect behavior you actually verified, separating implemented behavior from proposed memory policy.

## Hand off honestly

Open the constraint reveal when directed. Record which behavior is implemented, which is only a proposal, and which remains broken. A green suite supports the tested behaviors; it does not prove general intelligence or cover every boundary. The backend is a deterministic teaching fixture that only recalls a synthetic project code from user messages.
