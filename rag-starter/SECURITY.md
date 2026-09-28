# SECURITY.md — fill this in during Week 10

Four lines. Keep it honest and short. This is what you show before sharing your app.

## Keys — where are your API keys stored?
> e.g. "In a local `.env` file (git-ignored) and in Streamlit Cloud **Secrets**. Never committed.
>      Verified with `git grep -i 'sk-'` returning nothing."

## PII — what data does the bot see, and what do you tell users?
> e.g. "The deployed app indexes ONLY the synthetic sample docs. No real customer/patient data.
>      Users are told not to paste sensitive information."

## Grounding — how does the bot avoid making things up?
> e.g. "Answers are built only from retrieved chunks; when retrieval returns nothing relevant the
>      bot replies 'I don't know based on the documents I have.'"

## Local vs Public Mode — which mode is this repo in, and what changes if you switch?
> e.g. "Local-first by default: the offline FakeLLM (or `RIBOT_LLM=ollama`) over my local docs —
>      nothing leaves my machine. The public Streamlit demo indexes synthetic docs only and
>      reads its API key from Cloud Secrets."

---

### Quick self-check before you deploy
- [ ] `.env` is in `.gitignore` and is NOT in `git log` (`git log -p | grep -i OPENAI_API_KEY`)
- [ ] No keys committed: `git grep -i "sk-"` is empty
- [ ] Public deployment indexes synthetic/sample docs only
- [ ] The bot refuses (instead of inventing) when it has no relevant context
- [ ] You can explain every line you submit, AI-free
