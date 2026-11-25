# SECURITY.md — fill this in during Week 10

Five short sections. Keep them honest. This is what you show before sharing your assistant.

## Keys — where are your API keys stored?
> e.g. "In a local `.env` file (git-ignored). Never committed.
>      Verified with `git grep -i 'sk-'` returning nothing."

## PII — what data does the bot see, and what do you tell users?
> e.g. "The assistant indexes ONLY the synthetic sample docs. No real customer/patient data.
>      Users are told not to paste sensitive information."

## Grounding — how does the bot avoid making things up?
> e.g. "Answers are built only from retrieved chunks; when retrieval returns nothing relevant the
>      bot replies 'I don't know based on the documents I have.'"

## Tools — what can the agent do, and what needs your OK?
> e.g. "Read-only: search_docs, list_sources, current_date, plus my tools <names>.
>      Actions (each asks me y/N before it runs): remember, save_draft.
>      Every tool failure comes back to the model as an error; the loop stops after 4 steps."

## Local vs API Mode — which parts run on your machine, and what leaves it?
> e.g. "Local-first by default: the offline FakeLLM (or `RIBOT_LLM=ollama`) over my local docs —
>      nothing leaves my machine. With the class API key, my question and the retrieved chunks
>      are sent to the API provider, so the docs I index in that mode are synthetic only."

---

### Quick self-check before you share your repo
- [ ] `.env` is in `.gitignore` and was never committed (`git log --oneline -- .env` is empty)
- [ ] No keys committed: `git grep -n -E "sk-[A-Za-z0-9_-]{20,}"` is empty
- [ ] Every action tool asks before it runs (`gated()`), and `python scripts/quickstart.py` passes
- [ ] Anything you demo, share, or send to an API indexes synthetic/sample docs only
- [ ] The bot refuses (instead of inventing) when it has no relevant context
- [ ] You can explain every line you submit, AI-free
