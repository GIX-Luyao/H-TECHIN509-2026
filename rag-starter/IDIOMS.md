# Idioms You'll *Read* Before You *Write* Them

The reference code in `rag-starter/ribot/` is written the way working Python is really
written — which means it uses some shorthand the course never asks you to produce. This
page is the decoder ring. **None of this is required writing.** When one of these appears
in a cell marked *"GIVEN — run as-is"* or in `ribot/`, look it up here, read it once, and
move on. The weeks in parentheses say when (or whether) each one becomes yours.

## You will see these everywhere, from Week 1

**Type hints / annotations** — `def clean(text: str) -> str:` or `history: list[dict[str, str]]`.
The part after `:` or `->` is a *label* saying what type goes there. Python ignores it at
runtime — it's documentation for humans and tools. Read `x: list[str]` as "x, a list of
strings." (`from __future__ import annotations` at the top of files is pure ritual enabling
these labels — skip it.) *Never required writing in this course.*

**`import` / `from x import y` / `python -m ribot.chatbot`** — pulling in code from another
file. A folder of Python files with an `__init__.py` is a *package*; `python -m package.module`
runs one file of it as a program. The `if __name__ == "__main__":` block at a file's bottom
is "only run this when executed directly, not when imported."

**Keyword arguments** — `json.dump(data, f, indent=2)` or `store.add(ids=..., documents=...)`.
Naming the argument (`indent=2`) instead of relying on position. You'll write these
naturally from Week 6 on; until then just read them as "the `indent` option set to 2."

**f-string format specs** — `f"{score:5.3f}"` (3 decimal places, width 5), `f"{text!r}"`
(show quotes and hidden spaces, like `repr()`). The part after `:` or `!` is display
polish, never logic.

## Loops in disguise (Weeks 4–5 make these yours)

**List comprehension** — `[clean(m) for m in msgs]` is exactly the loop
`out = []; for m in msgs: out.append(clean(m))` in one line. (Week 4 stretch.)

**Generator expression** — same shape without brackets, feeding another function:
`sum(x * y for x, y in zip(a, b))` means "multiply pairs and add them up as you go."

**`zip(a, b)`** — walks two lists in lockstep, giving pairs. **`enumerate(chunks)`** —
walks one list, giving `(index, item)` pairs.

**Tuple unpacking** — `best_chunk, best_score = "", -1.0` assigns two things at once;
`for chunk, score in hits:` splits each pair as it loops. A *tuple* is just an immutable
list, usually holding "a few things that belong together" — like the `(chunk, score)`
pairs your retriever returns.

**Ternary expression** — `"HIT" if hit else "miss"` is a one-line `if/else` that produces
a value.

**`break` / `continue`** — inside a loop: `break` exits the loop now; `continue` skips to
the next iteration. (You use these from Week 3's command loop.)

## Objects and classes (Week 7 makes the core yours)

**Method calls / attributes** — `store.add(...)`, `store.count()`, `bot.history`. Before
Week 7, read `thing.action(...)` as "ask `thing` to do `action`" and `thing.data` as
"`thing`'s stored data." Week 7 shows you the machinery (`class`, `self`, `__init__`).

**Inheritance / `super()`** — `class BuggyChatBot(ChatBot):` means "a ChatBot with some
parts changed"; `super().reply(...)` calls the original version. Used in a couple of
Week 7–8 demos; *beyond this course's scope to write* — just read it as "a modified copy."

**Decorator** — the `@something` line directly above a `def` or `class` wraps it with
extra behavior: `@dataclass` auto-writes boilerplate, `@st.cache_resource` says "build
once, reuse," `@pytest.mark.parametrize` runs a test many times. Read `@x` as "modified
by x" and read on.

**Lambda** — `key=lambda pair: pair[1]` is a tiny unnamed function, here "sort by each
pair's second item."

## Files, text, and paths (Week 6 makes files yours)

**`with open(...) as f:`** — opens a file and *guarantees* it closes, even on error. The
Week 4 assignment hands you this two weeks early as a copy-me incantation; Week 6 explains
it properly. `with` also shows up on non-file things (`st.spinner(...)`) — same promise:
"set up, then clean up no matter what."

**`pathlib.Path`** — an object for file paths: `Path("docs") / "notes.md"` joins paths,
`.glob("*")` lists a folder, `.read_text()` reads a file, `.suffix` is the extension.

**Regex (`re.sub`, `re.compile`)** — pattern matching on text: `r"[^\w\s]"` means "any
character that isn't a letter, digit, or space." Powerful, cryptic, and *never required
writing here* — read the comment next to it for what the pattern does. Two places hand you a
regex as a **copy-me incantation** (Week 4's `clean_message`) or ask you to **choose between
written patterns** (Week 10's leak scanner); neither asks you to author one.

**Set literal** — `{".md", ".txt"}` is an unordered collection used for fast "is it one of
these?" membership checks.

## Rare cameos (fine to just recognize)

**Walrus `:=`** — `if prompt := st.chat_input():` assigns *and* tests in one step: "grab
the input, and if it's non-empty…" (One appearance, in `app.py`.)

**`next(...)` with a default** — `next((m for m in reversed(msgs) if ...), "")` means
"the first match walking backwards, or `""` if none."

**`getattr` / `hasattr`** — "does this object have this attribute?" — used for graceful
fallbacks.

**`assert x, "message"`** — crash with the message if `x` is false; the engine behind
every self-check cell and every pytest you write in Week 7.

**`subprocess.run([...])`** — run a terminal command from Python; used only to run
`git grep`/`pytest` inside notebooks.

---

*If you meet an unexplained idiom that isn't on this page, that's a bug in the course
materials — post it in the cohort channel.*
