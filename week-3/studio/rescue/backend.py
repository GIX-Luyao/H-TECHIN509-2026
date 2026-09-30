"""Offline teaching fixture. No external model, files, or network access."""
import re

CODE = re.compile(r"^my project code is ([A-Za-z0-9-]+)[.!]?$", re.I)
NO_CODE = "I do not have a project code in this conversation."


def reply(messages):
    users = [m["content"] for m in messages if m["role"] == "user"]
    latest = users[-1] if users else ""
    if CODE.fullmatch(latest):
        return "Project code noted."
    if latest.lower().rstrip("?") == "what is my project code":
        for content in reversed(users):
            match = CODE.fullmatch(content)
            if match:
                return f"Your project code is {match.group(1)}."
        return NO_CODE
    return "Noted. Ask 'What is my project code?' to check conversation context."
