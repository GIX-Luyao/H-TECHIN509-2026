"""Week 7: tests for the Tool class (ribot/tools.py). Fully offline."""

from ribot.tools import Tool, ToolResult


def _echo(text: str, times: int = 1) -> str:
    return " ".join([text] * times)


ECHO = Tool(
    name="echo",
    description="Repeat the given text. Use it only in tests.",
    input_schema={
        "type": "object",
        "properties": {
            "text": {"type": "string", "description": "What to repeat"},
            "times": {"type": "integer", "description": "How many times"},
        },
        "required": ["text"],
    },
    run=_echo,
)


def test_valid_call_returns_the_function_output():
    assert ECHO.call({"text": "hi", "times": 2}) == ToolResult("hi hi")


def test_missing_required_argument_is_an_error_result():
    result = ECHO.call({})
    assert result.is_error
    assert "text" in result.content


def test_unknown_argument_is_an_error_result():
    assert ECHO.call({"text": "hi", "loud": True}).is_error


def test_wrong_argument_type_is_an_error_result():
    assert ECHO.call({"text": "hi", "times": "two"}).is_error


def test_non_dict_arguments_are_an_error_result():
    assert ECHO.call(["hi"]).is_error


def test_crash_inside_the_function_becomes_an_error_result():
    def broken(text: str) -> str:
        raise RuntimeError("disk full")

    tool = Tool("broken", "fails", {"type": "object", "properties": {"text": {"type": "string"}}}, broken)
    result = tool.call({"text": "x"})
    assert result.is_error
    assert "disk full" in result.content


def test_non_text_output_is_an_error_result():
    tool = Tool("number", "returns an int", {"type": "object", "properties": {}}, lambda: 42)
    assert tool.call({}).is_error


def test_declaration_hides_the_function():
    declaration = ECHO.declaration()
    assert set(declaration) == {"name", "description", "input_schema"}


def test_openai_envelope_carries_the_same_schema():
    envelope = ECHO.to_openai()
    assert envelope["type"] == "function"
    assert envelope["function"]["parameters"] == ECHO.input_schema


def test_tools_are_read_only_by_default():
    assert ECHO.read_only is True
