"""Conversation storage and request preparation."""
SYSTEM = "You are a concise helpdesk assistant. Use the supplied conversation."


def initial_history():
    return [{"role": "system", "content": SYSTEM}]


def request_messages(history):
    """Prepare context for the reply backend."""
    return history[:1] + history[-1:]
