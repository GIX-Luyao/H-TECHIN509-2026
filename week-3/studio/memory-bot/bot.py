"""Terminal memory bot. Commands: /show, /reset, /exit."""
from backend import reply
from memory import add_turn, new_history, request_messages


def show(history):
    """Return the stored history as printable lines."""
    lines = []
    for message in history:
        lines.append(f"[{message['role']}] {message['content']}")
    return "\n".join(lines)


def respond(history, text):
    """Handle one line typed by the user and return what to print."""
    if text == "/show":
        return show(history)
    if text == "/reset":
        history.clear()
        return "Conversation reset."
    if text.strip() == "":
        return ""
    add_turn(history, "user", text)
    answer = reply(request_messages(history))
    add_turn(history, "assistant", answer)
    return answer


def main():
    history = new_history()
    print("Memory bot. Commands: /show, /reset, /exit")
    while True:
        text = input("you > ")
        if text.strip() == "/exit":
            print("bye!")
            break
        output = respond(history, text)
        if output:
            print(f"bot > {output}")


if __name__ == "__main__":
    main()
