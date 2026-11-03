"""Week 10: tool calling with a LOCAL model served by Ollama.

`llm.chat_tools()` sends tools to an API model, or to the scripted FakeToolLLM offline.
This module adds the third option: an Ollama model that genuinely chooses tools on your
own machine, with no data leaving it. It speaks Ollama's native `/api/chat` tool format
and converts to and from the same block shapes the harness uses, so the agent loop is
identical whichever model is answering.

    RIBOT_LLM=ollama OLLAMA_MODEL=qwen3.5:2b python -m ribot.assistant

Not every model supports tools: Ollama rejects tools for some (gemma3:1b, for example),
and very small models that do support them often pick the wrong tool or none at all.
That is worth measuring, not hiding: run `python -m ribot.agent_eval` per model.
"""

from __future__ import annotations

import json
import urllib.error
import urllib.request
from typing import Sequence

from .config import get_settings
from .llm import ToolMessage, chat_tools


def to_ollama_messages(messages: Sequence[ToolMessage]) -> list[dict]:
    """Convert harness-shaped messages into Ollama's /api/chat format."""
    converted: list[dict] = []
    tool_names: dict[str, str] = {}  # tool_use id -> tool name (Ollama wants the name)
    for message in messages:
        content = message.get("content")
        if isinstance(content, str):
            converted.append({"role": message["role"], "content": content})
            continue
        for block in content if isinstance(content, list) else []:
            kind = block.get("type")
            if kind == "tool_use":
                tool_names[block["id"]] = block["name"]
                converted.append(
                    {
                        "role": "assistant",
                        "content": "",
                        "tool_calls": [
                            {
                                "function": {
                                    "name": block["name"],
                                    "arguments": block.get("input", {}),
                                }
                            }
                        ],
                    }
                )
            elif kind == "tool_result":
                converted.append(
                    {
                        "role": "tool",
                        "content": str(block.get("content", "")),
                        "tool_name": tool_names.get(block.get("tool_use_id", ""), ""),
                    }
                )
            elif kind == "text":
                converted.append({"role": message["role"], "content": block["text"]})
    return converted


def _parse_arguments(arguments: object) -> dict:
    """Ollama sends a dict; some models send a JSON string instead. Accept both."""
    if isinstance(arguments, dict):
        return arguments
    try:
        parsed = json.loads(str(arguments or "{}"))
    except json.JSONDecodeError:
        return {}
    return parsed if isinstance(parsed, dict) else {}


def from_ollama_reply(body: dict, turn: int) -> ToolMessage:
    """Convert an Ollama /api/chat response into a harness-shaped assistant message."""
    message = body.get("message", {}) or {}
    calls = message.get("tool_calls") or []
    if calls:
        function = calls[0].get("function", {})
        return {
            "role": "assistant",
            "stop_reason": "tool_use",
            "content": [
                {
                    "type": "tool_use",
                    "id": calls[0].get("id") or f"toolu_ollama_{turn:03d}",
                    "name": function.get("name", ""),
                    "input": _parse_arguments(function.get("arguments")),
                }
            ],
        }
    return {
        "role": "assistant",
        "stop_reason": "end_turn",
        "content": [{"type": "text", "text": message.get("content", "")}],
    }


class OllamaToolLLM:
    """A local model that receives tool declarations and may ask for one to run."""

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

    def chat_tools(
        self, messages: Sequence[ToolMessage], tools: Sequence[dict]
    ) -> ToolMessage:
        payload = {
            "model": self.model,
            "messages": to_ollama_messages(messages),
            "tools": [
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
            "stream": False,
            "options": {"temperature": self.temperature},
        }
        return from_ollama_reply(self._post(payload), turn=len(list(messages)))

    def _post(self, payload: dict) -> dict:
        request = urllib.request.Request(
            f"{self.host}/api/chat",
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        try:
            with urllib.request.urlopen(request, timeout=self.timeout) as response:
                return json.loads(response.read().decode("utf-8"))
        except urllib.error.HTTPError as err:  # must come before URLError (a subclass)
            detail = err.read().decode("utf-8", errors="replace")
            raise RuntimeError(
                f"Ollama refused the request for {self.model!r} ({err.code}): {detail}. "
                "If it says the model does not support tools, pick a tool-capable model "
                "(for example a qwen3.5 or granite4 model) with OLLAMA_MODEL=..."
            ) from err
        except (urllib.error.URLError, OSError) as err:
            raise RuntimeError(
                f"Ollama not reachable at {self.host}. Install it from ollama.com, "
                f"start it, and run `ollama pull {self.model}`. (Original error: {err})"
            ) from err


def chat_tools_routed(
    messages: Sequence[ToolMessage], tools: Sequence[dict]
) -> ToolMessage:
    """Ollama when RIBOT_LLM=ollama; otherwise `llm.chat_tools` (API key or offline)."""
    settings = get_settings()
    if settings.llm_backend == "ollama":
        return OllamaToolLLM(
            model=settings.ollama_model, host=settings.ollama_host
        ).chat_tools(messages, tools)
    return chat_tools(messages, tools)
