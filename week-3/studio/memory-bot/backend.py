"""Offline stand-in for a model. It can remember a name said earlier in the messages."""

NAME_PREFIX = "my name is "
NO_NAME = "I do not know your name yet."


def find_name(messages):
    """Return the most recent name a user stated, or an empty string."""
    name = ""
    for message in messages:
        text = message["content"].strip()
        if message["role"] == "user" and text.lower().startswith(NAME_PREFIX):
            name = text[len(NAME_PREFIX):].strip(" .!")
    return name


def reply(messages):
    """Answer the latest user message using only the messages it was given."""
    latest = messages[-1]["content"].strip().lower().rstrip("?!.")
    name = find_name(messages)
    if latest == "what is my name":
        if name:
            return f"Your name is {name}."
        return NO_NAME
    if latest.startswith(NAME_PREFIX):
        return f"Nice to meet you, {name}."
    return "Noted. Ask 'What is my name?' to test my memory."
