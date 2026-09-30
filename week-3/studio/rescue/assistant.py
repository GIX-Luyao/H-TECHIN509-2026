"""Inherited terminal assistant used for the Week 3 rescue exercise."""
from backend import reply
from memory import initial_history, request_messages


def handle(history, text):
    """Return (display_text, should_exit); history is updated in place."""
    text = text.strip()
    if text == "/exit":
        return "bye!", True
    elif text == "/show":
        return "\n".join(f"[{m['role']}] {m['content']}" for m in history), False
    elif text == "/reset":
        history[:] = history[:1]
        return "Conversation reset.", False
    elif not text:
        return "", False
    history.append({"role": "user", "content": text})
    answer = reply(request_messages(history))
    history.append({"role": "assistant", "content": answer})
    return answer, False


def main():
    history = initial_history()
    print("Helpdesk assistant: /show, /reset, /exit")
    while True:
        text = input("you > ")
        output, done = handle(history, text)
        if output:
            print(f"assistant > {output}")
        if done:
            break


if __name__ == "__main__":
    main()
