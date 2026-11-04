"""Week 7: a tool is a small class. Week 8: the agent harness runs these.

A tool bundles what a model needs to CHOOSE it (name, description, input schema) with the
Python function your code RUNS. The fields map onto the production tool-calling APIs:

| Tool field     | Anthropic API  | OpenAI API   | MCP                       |
|----------------|----------------|--------------|---------------------------|
| `name`         | `name`         | `name`       | `name`                    |
| `description`  | `description`  | `description`| `description`             |
| `input_schema` | `input_schema` | `parameters` | `inputSchema`             |
| `read_only`    | —              | —            | `annotations.readOnlyHint`|
| `run`          | your code      | your code    | your server's code        |

The model sees `declaration()` and never sees `run`. `call()` never raises: bad arguments,
a crash inside the function, or a non-text return value all come back as a `ToolResult`
with `is_error=True`, which the agent loop hands to the model so it can try again.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

# JSON Schema type names -> the Python types that satisfy them.
JSON_TYPES: dict[str, type | tuple[type, ...]] = {
    "string": str,
    "integer": int,
    "number": (int, float),
    "boolean": bool,
}


@dataclass(frozen=True)
class ToolResult:
    """What a tool hands back to the model: text, plus a flag when something went wrong."""

    content: str
    is_error: bool = False


@dataclass(frozen=True)
class Tool:
    """One tool = what the model sees (name, description, schema) + the function we run."""

    name: str
    description: str
    input_schema: dict
    run: Callable[..., str]  # any function that returns a string
    read_only: bool = True  # False = it changes something (saves, sends, deletes)

    def declaration(self) -> dict:
        """The part the model sees, in the Anthropic / MCP shape."""
        return {
            "name": self.name,
            "description": self.description,
            "input_schema": self.input_schema,
        }

    def to_openai(self) -> dict:
        """The same declaration in OpenAI's envelope."""
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": self.input_schema,
            },
        }

    def check_args(self, args: dict) -> str:
        """Return '' if args fit the schema, otherwise what is wrong."""
        properties = self.input_schema.get("properties", {})
        for field in self.input_schema.get("required", []):
            if field not in args:
                return f"missing required argument {field!r}"
        for field, value in args.items():
            if field not in properties:
                return f"unknown argument {field!r}"
            expected = JSON_TYPES.get(properties[field].get("type"))
            if expected and not isinstance(value, expected):
                return f"{field!r} should be a {properties[field]['type']}"
        return ""

    def call(self, args: dict) -> ToolResult:
        """Check the arguments, run the function, and turn any failure into an error result."""
        if not isinstance(args, dict):
            return ToolResult(f"Bad arguments for {self.name}: expected an object", True)
        problem = self.check_args(args)
        if problem:
            return ToolResult(f"Bad arguments for {self.name}: {problem}", is_error=True)
        try:
            output = self.run(**args)
        except Exception as err:  # reported to the model, never hidden
            return ToolResult(f"{self.name} failed: {err}", is_error=True)
        if not isinstance(output, str):
            kind = type(output).__name__
            return ToolResult(f"{self.name} returned {kind}, not text", is_error=True)
        return ToolResult(output)
