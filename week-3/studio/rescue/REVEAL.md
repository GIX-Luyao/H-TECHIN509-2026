# Constraint reveal: the fix must survive a longer conversation

Open after your initial repair attempt or supported diagnosis. Rotate roles before continuing.

The product owner now requires a bounded request. The inherited README claims that history already has a limit. Verify that claim before relying on it.

## Decide the memory policy

For this classroom estimate, allow **4,000 tokens total**: 200 for the system instruction, 100 for the current user input, and 300 reserved for the next reply. Estimate each completed historical user/assistant exchange at 200 tokens. These are exercise assumptions, not measurements; ignore formatting overhead and state that limitation.

Compare keeping all history, retaining recent complete exchanges, pinning the first exchange plus recent exchanges, and keeping a summary plus recent exchanges (budget 400 tokens for the summary). Calculate your chosen policy after 20 and 200 completed exchanges. A turn means one user message plus its assistant reply; the system message is separate.

Document what is kept, dropped, or summarized, why, and the exact question that exposes an accepted failure. Specify whether you limit stored history or only the request, when trimming occurs, and how an oversized single message is handled. A turn count alone cannot guarantee a token budget.

If your initial repair is stable, implement a small recent-history policy and check its boundary with a two-exchange window. Keep the system instruction and current input, and drop complete old exchanges. If blocked, provide a hand-traced policy and clearly label it **proposed, not implemented**. Do not add automatic summarization or a tokenizer dependency during this session.

## Attack the boundaries

Record predictions and observations for every row:

| Case | Challenge |
|---|---|
| Empty history | Distinguish a fresh system-only conversation from an actual empty list. What does each helper do? What should be supported? |
| Long message | Try a synthetic 5,000-character message. Does a count-based window bound its size? Do not equate characters with tokens. |
| `/reset` | After recalling a fact, reset and ask again. Is the system instruction preserved and the old fact unavailable? |
| Exit | Does `/exit` terminate without calling the backend or appending a message? |
| Memory limit | Put a fact just inside and then outside the chosen request window. Predict before running; include the new question when counting. |

Inspect the actual request list, not only `/show`. For an unimplemented policy, mark the boundary result as a manual trace, not a passing runtime check. Keep passing checks for the original repair while adding constraint checks that respect the new contract; the short incident conversation must still work.
