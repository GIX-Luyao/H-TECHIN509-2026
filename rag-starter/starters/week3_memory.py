"""Week 3 faded exercise: build conversation memory as a list of dicts.

Fill in each # TODO. Reference: ribot/chatbot.py
Run:  python starters/week3_memory.py
"""

from __future__ import annotations


def run() -> None:
    # messages is the bot's memory: a list of {"role", "content"} dicts.
    messages: list[dict[str, str]] = [
        {"role": "system", "content": "You are a helpful assistant."}
    ]

    while True:
        user = input("you > ").strip()

        if user == "/exit":
            break
        if user == "/show":
            for m in messages:
                print(f"  [{m['role']}] {m['content']}")
            continue

        # TODO 1: append the user's message as a dict with role "user" and content `user`
        # messages.append(...)

        # TODO 2: start with the echo below; once the loop works, upgrade it to a REAL
        #         reply with:  from ribot.llm import chat   then   reply = chat(messages)
        #         (works offline — and the bot will answer from its memory!)
        reply = f"(echo) {user}"
        # TODO 3: append the assistant reply to messages too

        print(f"bot > {reply}\n")

    print(f"\nConversation had {len(messages)} messages.")


if __name__ == "__main__":
    run()
