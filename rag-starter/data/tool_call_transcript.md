# `tool_call_transcript.json` — one real tool-calling exchange, annotated

This file is the Week 8 "same loop, sturdier envelope" claim as **data you can parse**: the
exact three-part exchange a production system uses where our course scaffold uses the
`SEARCH:` text protocol. Load it with `json.loads` — the Module 8 assignment's floor asks you
to extract the tool name, the typed arguments, and the result text.

The `exchange` list has three turns:

**1. `1_request` — telling the model the tool exists.** Where the course scaffold puts one
sentence in the system prompt ("reply with a line that starts with SEARCH:"), the request
declares the tool up front in `tools=[...]`: a name (`search_docs`), a description, and an
`input_schema` (a JSON Schema of the **typed** arguments). A malformed call is rejected before
your code ever sees it — our `startswith("SEARCH:")` parser has no such guarantee.

**2. `2_assistant_tool_use` — the model asks for the tool.** Instead of a magic string to
parse, the reply carries a `tool_use` content block: the tool's `name`, an `id`, and `input`
that arrives as **already-parsed, typed arguments** (`{"query": "password reset", "k": 3}`).
`stop_reason: "tool_use"` is the loop condition — the structured version of "does the reply
start with `SEARCH:`?"

**3. `3_tool_result` — feeding the result back.** Where the scaffold appends a plain-text
`SEARCH RESULTS: ...` message, production sends a `tool_result` turn whose `tool_use_id` ties
the answer to the exact request — no ambiguity even with several calls in flight. Then you
call the model again, inside the same capped loop you wrote this week.

Nothing conceptual changed: declare a tool, detect the request, run your function, feed the
result back, cap the iterations.
