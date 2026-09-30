# Incident 031: “It can show my project code but cannot recall it”

All inputs here are synthetic. The user supplied this transcript:

```text
you > My project code is ORBIT-17
assistant > Project code noted.
you > What is my project code?
assistant > I do not have a project code in this conversation.
you > /show
```

The earlier project-code message is visible in `/show`. The user expected the second reply to contain `ORBIT-17`.

## Current acceptance contract

- Ordinary input adds one user dictionary, produces a reply using conversation context, then adds one assistant dictionary.
- The backend can recall the latest project code declared in an earlier user message. It must not recall a code after `/reset`.
- `/show` displays stored history without appending messages or calling the backend.
- `/reset` clears conversation exchanges and retains the original system instruction.
- `/exit` ends the terminal loop without appending a message or calling the backend.
- Blank input does nothing. A question before any project code receives the “no project code” reply.
- Keep the reply backend deterministic and offline. Preserve its `reply(messages)` interface.

The starting suite has 7 passing checks and 1 failing check. This is an incomplete safety net. Add a regression check of your own and inspect the boundaries after the reveal. The inherited README's other claims are unverified.

First deliver a data-flow sketch and reproducible diagnosis. Only then change code. Save evidence, not just a screenshot of passing checks.
