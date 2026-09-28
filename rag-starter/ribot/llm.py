"""The single place we talk to a language model.

`chat(messages)` takes a list of {"role", "content"} dicts (exactly the structure you
build by hand in Week 3) and returns the assistant's reply as a string.

- If an API key is configured, it calls the real model.
- Otherwise it uses `FakeLLM`, a deterministic stand-in so everything works offline.
- Week 8: `chat_tools(messages, tools)` is the structured tool-calling twin — declared
  tool schemas in, a block-shaped assistant message out (see ribot/harness.py); offline
  it uses the equally deterministic `FakeToolLLM`.
- Week 10 (opt-in): set `RIBOT_LLM=ollama` to talk to a local Ollama model instead —
  same messages in, same string out, no data leaves your machine.
"""

from __future__ import annotations

import json
import re
import urllib.error
import urllib.request
from typing import Sequence

from .config import get_settings

Message = dict[str, str]

# Week 8 harness messages: `content` may be a plain string OR a list of typed blocks
# (`tool_use` / `tool_result` / `text`) — the shapes in data/tool_call_transcript.json.
ToolMessage = dict[str, object]

# Sentinel embedded in the agent's system prompt so the offline FakeLLM knows to
# play along with the "reply with SEARCH: ..." tool protocol (see ribot/agent.py).
TOOL_PROTOCOL_MARKER = "reply with a line that starts with SEARCH:"

# Sentinel for the Week-4 structured-output lesson. When a system prompt asks for JSON,
# the offline FakeLLM answers with JSON instead of prose — and deliberately wraps it in a
# ```json fence, because that is what real models actually do. Week 4's parse_model_json()
# is the code that has to survive it.
JSON_PROTOCOL_MARKER = "reply with JSON only"

# Sentinel for the Week-9 query-rewrite lesson. When a system prompt asks for a standalone
# rewrite, the offline FakeLLM returns the two turns stitched together — deliberately the
# SAME result the heuristic in ribot/rewrite.py produces, so the plumbing is visible offline
# and the lesson can be honest that a real model is the part that gets smarter here.
REWRITE_PROTOCOL_MARKER = "Rewrite the follow-up as a standalone question."

# Memory demo (Weeks 1 & 3): recognize "my name is X" and "what's my name?".
_NAME_RE = re.compile(r"\bmy name is ([A-Za-z][\w-]*)", re.IGNORECASE)
_ASK_NAME_RE = re.compile(r"\b(what(?:'s|’s| is) my name|who am i)\b", re.IGNORECASE)


class FakeLLM:
    """A tiny, deterministic 'model' for offline use. Not smart — just predictable.

    It demonstrates the one thing that matters in Weeks 1-3: a model only "remembers"
    what is inside `messages`. Tell it your name and it can answer later — but ONLY if
    the earlier turns were kept in the list. Drop the history and it forgets.

    Four modes, picked from what the system prompt contains:
      - `TOOL_PROTOCOL_MARKER`    -> plays the "SEARCH: ..." tool protocol (Week 8)
      - `JSON_PROTOCOL_MARKER`    -> answers with fenced JSON (Week 4 structured output)
      - `REWRITE_PROTOCOL_MARKER` -> stitches a follow-up into a standalone question (Week 9)
      - otherwise                  -> the memory demo, then a canned prose reply
    """

    def chat(self, messages: Sequence[Message]) -> str:
        system = " ".join(m["content"] for m in messages if m["role"] == "system")
        last_user = next(
            (m["content"] for m in reversed(messages) if m["role"] == "user"), ""
        )
        results = [
            m["content"] for m in messages if m["content"].startswith("SEARCH RESULTS:")
        ]

        # Agent mode: if the bot is allowed to use the search tool and hasn't yet, do so.
        if TOOL_PROTOCOL_MARKER in system and not results:
            return f"SEARCH: {last_user}"

        # Grounded-answer mode: we have retrieved context, so answer from it.
        if results:
            context = results[-1].replace("SEARCH RESULTS:", "").strip()
            snippet = context[:240].strip()
            if not snippet:
                return "I don't know based on the documents I have."
            return f"Based on the documents: {snippet}"

        # Rewrite mode (Week 9): the system prompt asked for a standalone question, so
        # stitch the earlier question and the follow-up together. This is exactly what the
        # offline heuristic does — the honest offline story is "the wiring works," not
        # "the fake model is clever."
        if REWRITE_PROTOCOL_MARKER in system:
            earlier, follow_up = "", last_user.strip()
            for line in last_user.splitlines():
                if line.lower().startswith("earlier question:"):
                    earlier = line.split(":", 1)[1].strip()
                elif line.lower().startswith("follow-up question:"):
                    follow_up = line.split(":", 1)[1].strip()
            return f"{earlier} {follow_up}".strip()

        # Structured-output mode (Week 4): the system prompt asked for JSON, so hand back
        # JSON — fenced, the way real models habitually do, so the parser has real work to do.
        if JSON_PROTOCOL_MARKER in system:
            payload = {
                "question": last_user.strip(),
                "topic": "unknown",
                "needs_human": False,
            }
            return "```json\n" + json.dumps(payload, indent=2) + "\n```"

        # Memory demo: the model sees ONLY what's in `messages`. If earlier turns were
        # kept, it can recall them; if they were thrown away, it can't. That's "memory."
        told_name = _NAME_RE.search(last_user)
        if told_name:
            return (
                f"Nice to meet you, {told_name.group(1)}! I'll remember that — "
                "as long as this turn stays in the conversation history."
            )
        if _ASK_NAME_RE.search(last_user):
            for m in messages:
                if m["role"] == "user":
                    earlier = _NAME_RE.search(m["content"])
                    if earlier:
                        return (
                            f"You told me earlier — your name is {earlier.group(1)}. "
                            "(I only know because that turn is still in the messages list.)"
                        )
            return "I don't know your name — you haven't told me in this conversation."

        # Plain chat mode (Weeks 1-4): a friendly canned reply that echoes the input.
        persona = "your assistant"
        stripped = system.strip()
        if stripped.lower().startswith("you are "):
            persona = stripped[len("you are ") :].split(".")[0].strip()
        return (
            f"(offline demo reply) Speaking as {persona}: here is a placeholder answer to "
            f'"{last_user}". Add an API key in .env for real responses.'
        )


class FakeToolLLM:
    """Offline stand-in that speaks the STRUCTURED tool-calling envelope (Week 8).

    Same honesty rule as `FakeLLM`: it is scripted, not smart. First turn it picks a
    tool — `list_sources` if the question sounds like it's about the library itself,
    otherwise the first tool that takes a `query` — and after a `tool_result` arrives
    it answers from that result. Offline you are studying the LOOP MECHANICS, not
    model agency; with a real key the tool choice is genuinely the model's.

    Replies use the same shapes as `data/tool_call_transcript.json`: an assistant
    message whose `content` is a list of blocks, stopping on `tool_use` or `end_turn`.
    """

    _ABOUT_LIBRARY = ("which documents", "what documents", "sources", "library", "indexed")

    def chat_tools(
        self, messages: Sequence[ToolMessage], tools: Sequence[dict]
    ) -> ToolMessage:
        last_result = _last_tool_result(messages)

        # A tool already ran: answer from its result, the way FakeLLM answers from
        # SEARCH RESULTS. Empty result -> honest "I don't know".
        if last_result is not None:
            snippet = str(last_result)[:240].strip()
            if not snippet:
                text = "I don't know based on the documents I have."
            else:
                text = f"Based on the documents: {snippet}"
            return {
                "role": "assistant",
                "stop_reason": "end_turn",
                "content": [{"type": "text", "text": text}],
            }

        # First turn: pick a tool, deterministically.
        question = next(
            (
                m["content"]
                for m in reversed(list(messages))
                if m["role"] == "user" and isinstance(m["content"], str)
            ),
            "",
        )
        name, args = self._pick_tool(question, tools)
        return {
            "role": "assistant",
            "stop_reason": "tool_use",
            "content": [
                {
                    "type": "tool_use",
                    "id": f"toolu_offline_{len(list(messages)):03d}",
                    "name": name,
                    "input": args,
                }
            ],
        }

    def _pick_tool(self, question: str, tools: Sequence[dict]) -> tuple[str, dict]:
        lowered = question.lower()
        by_name = {t["name"]: t for t in tools}
        if "list_sources" in by_name and any(
            phrase in lowered for phrase in self._ABOUT_LIBRARY
        ):
            return "list_sources", {}
        for tool in tools:
            if "query" in tool.get("input_schema", {}).get("properties", {}):
                return tool["name"], {"query": question, "k": 3}
        # No searchable tool declared: fall back to the first one, no arguments.
        first = tools[0]
        return first["name"], {}


def _last_tool_result(messages: Sequence[ToolMessage]) -> str | None:
    """The content of the most recent tool_result block, or None if no tool ran yet."""
    for message in reversed(list(messages)):
        content = message.get("content")
        if not isinstance(content, list):
            continue
        for block in content:
            if isinstance(block, dict) and block.get("type") == "tool_result":
                return str(block.get("content", ""))
    return None


class OllamaLLM:
    """Chat with a *local* model served by Ollama (https://ollama.com).

    Same interface as `FakeLLM`: `chat(messages)` in, reply string out. This is the
    Week 10 "localize" path — the whole point is that `ribot` never needs to know which
    backend is answering. Nothing here is installed by default and nothing changes unless
    you opt in with `RIBOT_LLM=ollama` (or construct this class yourself).

    Uses only the standard library (urllib), so it works on locked-down machines where
    extra installs are blocked — you still need Ollama itself running, of course.
    """

    def __init__(
        self,
        model: str = "llama3.2",
        host: str = "http://localhost:11434",
        temperature: float = 0.2,
        timeout: float = 120.0,
    ) -> None:
        self.model = model
        self.host = host.rstrip("/")
        self.temperature = temperature
        self.timeout = timeout

    def chat(self, messages: Sequence[Message]) -> str:
        payload = json.dumps(
            {
                "model": self.model,
                "messages": list(messages),
                "stream": False,
                "options": {"temperature": self.temperature},
            }
        ).encode("utf-8")
        request = urllib.request.Request(
            f"{self.host}/api/chat",
            data=payload,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        try:
            with urllib.request.urlopen(request, timeout=self.timeout) as response:
                body = json.loads(response.read().decode("utf-8"))
        except (urllib.error.URLError, OSError) as err:
            raise RuntimeError(
                f"Ollama not reachable at {self.host} — install it from ollama.com, "
                f"start it, and run `ollama pull {self.model}`. "
                f"(Original error: {err})"
            ) from err
        return body.get("message", {}).get("content", "")


def chat(messages: Sequence[Message], temperature: float = 0.2) -> str:
    """Send a conversation and return the assistant reply text.

    Args:
        messages: list of {"role": "system"|"user"|"assistant", "content": str}
        temperature: sampling temperature for the real model (ignored offline)
    """
    settings = get_settings()

    # Opt-in local backend (Week 10): RIBOT_LLM=ollama. Default behavior is unchanged.
    if settings.llm_backend == "ollama":
        return OllamaLLM(
            model=settings.ollama_model,
            host=settings.ollama_host,
            temperature=temperature,
        ).chat(messages)

    if not settings.has_key:
        return FakeLLM().chat(messages)

    # Real path. Imported lazily so the offline path needs no openai install.
    from openai import OpenAI

    client = OpenAI(api_key=settings.api_key, base_url=settings.base_url)
    response = client.chat.completions.create(
        model=settings.chat_model,
        messages=list(messages),
        temperature=temperature,
    )
    return response.choices[0].message.content or ""


def chat_tools(
    messages: Sequence[ToolMessage], tools: Sequence[dict], temperature: float = 0.2
) -> ToolMessage:
    """Send a conversation WITH declared tools; return the full assistant message.

    This is the Week 8 structured envelope: `tools` is a list of declarations
    (name / description / input_schema, exactly the shapes in
    data/tool_call_transcript.json), and the reply is an assistant message whose
    `content` is a list of blocks — a `tool_use` block when the model wants a tool
    run, a `text` block when it is answering. Your loop in ribot/harness.py decides
    what happens next; the model never runs anything itself.

    - No API key -> the deterministic `FakeToolLLM` (also used for RIBOT_LLM=ollama:
      the Week 10 local path speaks plain chat only, so tools stay offline there).
    - Real key -> the OpenAI-compatible tools API, converted to and from the same
      block shapes so the harness code is identical offline and live.
    """
    settings = get_settings()
    if settings.llm_backend == "ollama" or not settings.has_key:
        return FakeToolLLM().chat_tools(messages, tools)

    from openai import OpenAI

    client = OpenAI(api_key=settings.api_key, base_url=settings.base_url)
    response = client.chat.completions.create(
        model=settings.chat_model,
        messages=_to_openai_messages(messages),
        tools=[
            {
                "type": "function",
                "function": {
                    "name": t["name"],
                    "description": t["description"],
                    "parameters": t["input_schema"],
                },
            }
            for t in tools
        ],
        temperature=temperature,
    )
    return _from_openai_reply(response.choices[0].message)


def _to_openai_messages(messages: Sequence[ToolMessage]) -> list[dict]:
    """Convert our transcript-shaped messages into the OpenAI wire format."""
    converted: list[dict] = []
    for message in messages:
        content = message.get("content")
        if isinstance(content, str):
            converted.append({"role": message["role"], "content": content})
            continue
        blocks = content if isinstance(content, list) else []
        for block in blocks:
            if block.get("type") == "tool_use":
                converted.append(
                    {
                        "role": "assistant",
                        "content": None,
                        "tool_calls": [
                            {
                                "id": block["id"],
                                "type": "function",
                                "function": {
                                    "name": block["name"],
                                    "arguments": json.dumps(block.get("input", {})),
                                },
                            }
                        ],
                    }
                )
            elif block.get("type") == "tool_result":
                converted.append(
                    {
                        "role": "tool",
                        "tool_call_id": block["tool_use_id"],
                        "content": str(block.get("content", "")),
                    }
                )
            elif block.get("type") == "text":
                converted.append({"role": message["role"], "content": block["text"]})
    return converted


def _from_openai_reply(reply) -> ToolMessage:
    """Convert an OpenAI reply back into our transcript-shaped assistant message."""
    if getattr(reply, "tool_calls", None):
        call = reply.tool_calls[0]
        try:
            arguments = json.loads(call.function.arguments or "{}")
        except json.JSONDecodeError:
            arguments = {}
        return {
            "role": "assistant",
            "stop_reason": "tool_use",
            "content": [
                {
                    "type": "tool_use",
                    "id": call.id,
                    "name": call.function.name,
                    "input": arguments,
                }
            ],
        }
    return {
        "role": "assistant",
        "stop_reason": "end_turn",
        "content": [{"type": "text", "text": reply.content or ""}],
    }
