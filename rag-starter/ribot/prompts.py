"""Week 2: the prompt is just strings you assemble.

Nothing here calls a model. You build the exact text that WOULD be sent, and print it.
"""

from __future__ import annotations


def build_system_prompt(persona: str, tone: str, rule: str) -> str:
    """Assemble a multi-line system prompt from three pieces, using an f-string."""
    return f"""You are {persona}.
Speak in a {tone} tone.
Always follow this rule: {rule}
""".strip()


def clean_question(raw: str) -> str:
    """Tidy raw user input before it ever reaches a model (Week 2 string methods)."""
    return raw.strip().lower().replace("  ", " ")


def build_messages(system_prompt: str, user_question: str) -> list[dict[str, str]]:
    """Turn a system prompt + a question into the list-of-dicts the model expects."""
    return [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": clean_question(user_question)},
    ]


if __name__ == "__main__":  # `python -m ribot.prompts`
    sp = build_system_prompt(
        persona="a helpful HR policy assistant",
        tone="concise and friendly",
        rule="always cite the policy section you used",
    )
    msgs = build_messages(sp, "  How many VACATION days do I GET? ")
    print("=== SYSTEM PROMPT ===")
    print(sp)
    print("\n=== FULL MESSAGES (what we would send) ===")
    for m in msgs:
        print(f"[{m['role']}] {m['content']}")
