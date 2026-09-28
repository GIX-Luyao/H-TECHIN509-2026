# `rag-starter` — the HMSTI 509 personal-assistant spine

This is the **one repository you grow all term**. In Week 1 it already runs a working assistant shell.
Every week after, you replace a piece of "borrowed magic" with code you understand, until by
**Demo Day (Week 9)** it is a Retrieval-Augmented Generation (RAG) personal assistant that answers
**grounded, cited** questions over a safe work-library corpus and can be demoed locally or, when
the data is synthetic/sanitized, at a public URL. In Week 10 you harden it into a take-away
professional assistant package: safe data posture, local-first roadmap, and a small markdown
assistant-memory file.

It is designed to run **with or without** an API key:

- **With a key** (instructor-provided or your own): real LLM + real embeddings.
- **Offline / no key**: a deterministic `FakeLLM` and a pure-Python `fallback_embed()` so class
  demos, exercises, and tests still work on any laptop, including locked-down corporate machines.

The offline path is a teaching safety net, not a truly intelligent local model. The architecture is
deliberately provider-swappable: in Week 10 you actually point the `chat()` boundary at a **local
Ollama model** and re-run your tests — see "Run it against a local model" below.

> **Golden rule:** never commit secrets or real customer/PII data. See [`SECURITY.md`](SECURITY.md).

---

## Quick start (5 minutes)

> **Anything below fail?** Go straight to [`SETUP_TROUBLESHOOTING.md`](SETUP_TROUBLESHOOTING.md) —
> the known-failures guide (Windows/corporate machines first). Setup problems are never graded.

Install uv once (https://docs.astral.sh/uv/ — or `pip install uv` if the installer is
blocked), then from this folder:

**Windows (PowerShell):**

```powershell
uv venv
.venv\Scripts\Activate.ps1
uv pip install -r requirements.txt

copy .env.example .env             # (optional) then paste your key into .env
python scripts\check_env.py        # check everything works (no key required)
python -m ribot.chatbot            # talk to the assistant (works offline)
```

**macOS / Linux:**

```bash
uv venv
source .venv/bin/activate
uv pip install -r requirements.txt

cp .env.example .env               # (optional) then paste your key into .env
python scripts/check_env.py        # check everything works (no key required)
python -m ribot.chatbot            # talk to the assistant (works offline)
```

`check_env.py` always verifies the offline path, even when a key is configured. It does not validate API credentials or model connectivity. The interactive assistant uses your configured backend; without a key or local-model setting it uses FakeLLM.

**Week 1 minimum:** if dependency installation is blocked, Python 3.10+ alone can run `python scripts/check_env.py` and the no-key terminal assistant. The Arena also needs no extra packages.

If PowerShell refuses to run `Activate.ps1`, that's the #2 known failure — the one-line fix
is in [`SETUP_TROUBLESHOOTING.md`](SETUP_TROUBLESHOOTING.md).

---

## How the files map to the weeks

| Week | You learn | File you build / use | Fallback if stuck |
|------|-----------|----------------------|-------------------|
| 1 | setup, Git, run an assistant | `ribot/chatbot.py`, `app.py` | `FakeLLM` (offline) |
| 2 | strings, f-strings → the assistant profile prompt | `ribot/prompts.py` | — |
| 3 | lists, dicts, control flow → memory | `ribot/chatbot.py` (`ChatBot.history`) | reference `ChatBot` |
| 4 | functions, `try/except`, JSON | `ribot/textprep.py` | reference functions |
| 5 | embeddings + cosine similarity | `ribot/similarity.py`, `ribot/embeddings.py` | `fallback_embed()`, `data/embeddings_fixture.json` |
| 6 | files, chunking, vector store → work library | `ribot/chunking.py`, `ribot/vectorstore.py`, `ribot/build_index.py` | `InMemoryStore`, sample docs |
| 7 | classes + unit tests | `ribot/chatbot.py` classes, `tests/` | reference classes + sample tests |
| 8 | tool schemas + a bounded agent harness | `ribot/harness.py` (on-ramp: `ribot/agent.py`) | the `SEARCH:` single-tool loop + sample corpus |
| 9 | local/public demo day | `app.py`, `requirements.txt` | recorded demo video |
| 10 | harden + localize + remember | `SECURITY.md`, `.env`, grounding guardrail, `assistant_memory.md` | triage-assigned single fix |

`starters/` holds **blanked** versions of key files (with `# TODO` lines) for the in-class
faded exercises. The fully-worked code in `ribot/` is your **known-good reference**: if your own
copy breaks mid-week, you can sync one file back to the reference and keep moving.

> `ribot/` is written in idiomatic working Python, so it uses shorthand (type hints,
> decorators, comprehensions, …) the course never asks you to *write*. The decoder ring is
> [`IDIOMS.md`](IDIOMS.md) — read, don't reproduce.

---

## Layout

```
rag-starter/
├── ribot/                 # the package you build up over the term
│   ├── config.py          # loads settings + API key from .env
│   ├── llm.py             # chat() — real OpenAI OR offline FakeLLM
│   ├── prompts.py         # Week 2: assemble the prompt from strings
│   ├── chatbot.py         # Week 1/3/7: ChatBot/PersonalAssistant + ConversationLogger
│   ├── textprep.py        # Week 4: clean_message, build_conv, export_to_json
│   ├── similarity.py      # Week 5: cosine_similarity (pure-Python + NumPy)
│   ├── embeddings.py      # Week 5: embed() + fallback_embed() + fixture
│   ├── chunking.py        # Week 6: chunk_text()
│   ├── vectorstore.py     # Week 6: Chroma OR pure-Python InMemoryStore
│   ├── retriever.py       # Week 6: Retriever (embed → search → chunks)
│   ├── build_index.py     # Week 6: load → chunk → embed → store
│   └── agent.py           # Week 8: single-tool assistant loop
├── app.py                 # Week 9: Streamlit UI for local/public demo
├── assistant_memory.md    # Week 10 stretch/final artifact: local markdown memory (student-created)
├── data/
│   ├── sample_docs/       # synthetic, non-PII fallback corpus (office/HR flavor)
│   ├── sample_docs_engineering/  # synthetic engineering corpus (spec, work instruction, NCR log)
│   ├── embeddings_fixture.json   # precomputed fallback vectors
│   ├── tool_call_transcript.json # Week 8: a real structured tool-calling exchange, as parseable data
│   └── tool_call_transcript.md   # annotation of that transcript, part by part
├── starters/              # blanked exercise files (# TODO)
├── scripts/
│   ├── check_env.py       # "does my machine work?" (no key needed)
│   └── build_fixture.py   # regenerate embeddings_fixture.json
├── tests/                 # pytest examples (Week 7)
├── requirements.txt
├── pyproject.toml
├── .env.example
├── .gitignore
├── SECURITY.md
└── SETUP_TROUBLESHOOTING.md   # known setup failures + fixes (Windows first)
```

**Corpus options:** `data/sample_docs/` is the default office/HR-flavored corpus.
`data/sample_docs_engineering/` is an alternative with an engineering register — a fake
component spec, a work instruction, and an NCR log (all fully synthetic and marked as such).
Point `build_index(folder=...)` at either one, or at your own **synthetic/sanitized** docs.

---

## Running each layer

```bash
python -m ribot.chatbot          # Week 1/3: terminal assistant chat
python -m ribot.build_index      # Week 6: build the document index
python -m ribot.agent            # Week 8 on-ramp: text-protocol agent (SEARCH:)
python -m ribot.harness          # Week 8 floor: structured two-tool harness
streamlit run app.py             # Week 9: web UI
pytest                           # Week 7: run the tests
```

Everything above runs offline. Add a key in `.env` to use a real API-backed model. For professional
use, keep private docs local, publish only synthetic/sanitized demo docs, and treat Week 10's local
model + markdown-memory path as the bridge from class project to personal work assistant.

---

## Run it against a local model (Ollama)

Week 10's "localize" step, as a build instead of a promise: `chat()` can talk to a **local**
model served by [Ollama](https://ollama.com) — no API key, no data leaving your machine.

```bash
# One-time: install Ollama from ollama.com, then pull a small model:
ollama pull llama3.2
```

**Windows (PowerShell):**

```powershell
$env:RIBOT_LLM = "ollama"
python -m ribot.chatbot
```

**macOS / Linux:**

```bash
RIBOT_LLM=ollama python -m ribot.chatbot
```

Unset the variable (or open a new terminal) and the default behavior is back: FakeLLM
offline, real API with a key. `OLLAMA_MODEL` and `OLLAMA_HOST` override the defaults
(`llama3.2`, `http://localhost:11434`). If Ollama isn't running you get one clear error
telling you exactly that — see `OllamaLLM` in `ribot/llm.py`; it's ~40 lines and uses only
the standard library. Then re-run `pytest` and note what changed: that diff is your Week 10
localize write-up.

**Going fully local (Week 10 stretch):** the LLM swap alone is *half*-local — your documents
still flow through the embedding call. `RIBOT_EMBED=ollama` (PowerShell:
`$env:RIBOT_EMBED = "ollama"`) points `get_embedder()` at a local embedding model too — see
`OllamaEmbedder` in `ribot/embeddings.py` (one-time: `ollama pull nomic-embed-text`).
Defaults are unchanged unless you opt in.
