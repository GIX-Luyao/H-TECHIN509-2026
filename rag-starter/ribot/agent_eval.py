"""Weeks 8-10: test what the agent DOES, not just what retrieval finds.

hits@3 (ribot/evaluate.py) asks "did search find the right chunk?". An agent can have
perfect retrieval and still misbehave: search when it shouldn't, skip a tool it needs, or
answer a question its documents can't support. Each case in data/agent_cases.json states
the behavior we expect; this module runs the real agent loop on each one and checks it.

    python -m ribot.agent_eval                    # offline: scripted model, some skips
    RIBOT_LLM=ollama python -m ribot.agent_eval   # a local model's real decisions

Offline, the FakeToolLLM is scripted, so cases marked `needs_real_model` are skipped
rather than faked. Action tools are always declined here, so the eval never writes files.
"""

from __future__ import annotations

import json
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Sequence

from .agent_loop import AgentTurn, run_harness_turn
from .build_index import build_index
from .config import get_settings
from .harness import Tool
from .toolbox import deny_all, make_assistant_tools

CASES_PATH = Path(__file__).resolve().parent.parent / "data" / "agent_cases.json"
NO_TOOL = "none"
_REFUSAL_PHRASES = (
    "don't know",
    "do not know",
    "couldn't find",
    "could not find",
    "not in the documents",
    "no information",
)


@dataclass(frozen=True)
class AgentCase:
    question: str
    expect_tool: str | None = None
    expect_refusal: bool = False
    needs_real_model: bool = False
    note: str = ""


@dataclass(frozen=True)
class CaseResult:
    case: AgentCase
    passed: bool
    skipped: bool
    reasons: tuple[str, ...]
    turn: AgentTurn | None


def _parse_case(raw: object, index: int) -> AgentCase:
    if not isinstance(raw, dict) or not str(raw.get("question", "")).strip():
        raise ValueError(f"case {index} needs a non-empty 'question'")
    expect_tool = raw.get("expect_tool")
    if expect_tool is not None and not isinstance(expect_tool, str):
        raise ValueError(f"case {index}: 'expect_tool' must be a string or null")
    return AgentCase(
        question=str(raw["question"]).strip(),
        expect_tool=expect_tool,
        expect_refusal=bool(raw.get("expect_refusal", False)),
        needs_real_model=bool(raw.get("needs_real_model", False)),
        note=str(raw.get("note", "")),
    )


def load_cases(path: Path = CASES_PATH) -> list[AgentCase]:
    """Read and validate the case file; raise ValueError with the bad case's number."""
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    raw_cases = data.get("cases") if isinstance(data, dict) else None
    if not isinstance(raw_cases, list) or not raw_cases:
        raise ValueError(f"{path} must contain a non-empty 'cases' list")
    return [_parse_case(raw, i) for i, raw in enumerate(raw_cases, start=1)]


def is_refusal(answer: str) -> bool:
    lowered = answer.lower().replace("’", "'")
    return any(phrase in lowered for phrase in _REFUSAL_PHRASES)


def check_turn(case: AgentCase, turn: AgentTurn) -> tuple[str, ...]:
    """Every way this turn missed the expected behavior (empty means it passed)."""
    called = [step.name for step in turn.steps]
    reasons: list[str] = []
    if case.expect_tool == NO_TOOL and called:
        reasons.append(f"expected no tool, but it called {called}")
    elif case.expect_tool not in (None, NO_TOOL) and case.expect_tool not in called:
        reasons.append(
            f"expected {case.expect_tool}, but it called {called or 'nothing'}"
        )
    if case.expect_refusal and not is_refusal(turn.answer):
        reasons.append("expected an honest 'I don't know', but it answered")
    if not case.expect_refusal and is_refusal(turn.answer):
        reasons.append("refused a question it should answer")
    if turn.hit_cap:
        reasons.append("hit the step limit")
    return tuple(reasons)


def using_scripted_model() -> bool:
    """True offline: no key and no local model, so the FakeToolLLM answers."""
    settings = get_settings()
    return settings.llm_backend != "ollama" and not settings.has_key


def evaluate_agent(
    tools: Sequence[Tool], cases: Sequence[AgentCase]
) -> list[CaseResult]:
    scripted = using_scripted_model()
    results: list[CaseResult] = []
    for case in cases:
        if scripted and case.needs_real_model:
            results.append(CaseResult(case, False, True, ("needs a real model",), None))
            continue
        turn = run_harness_turn(case.question, tools)
        reasons = check_turn(case, turn)
        results.append(CaseResult(case, not reasons, False, reasons, turn))
    return results


def _report(results: Sequence[CaseResult]) -> str:
    lines = []
    for r in results:
        mark = "SKIP" if r.skipped else ("PASS" if r.passed else "FAIL")
        lines.append(f"[{mark}] {r.case.question}")
        tools = [s.name for s in r.turn.steps] if r.turn else []
        if r.turn:
            lines.append(f"       tools: {tools or 'none'}")
        lines.extend(f"       - {reason}" for reason in r.reasons if not r.skipped)
    ran = [r for r in results if not r.skipped]
    passed = sum(r.passed for r in ran)
    lines.append(f"\n{passed}/{len(ran)} passed, {len(results) - len(ran)} skipped")
    return "\n".join(lines)


def main() -> None:
    backend = (
        "offline (scripted FakeToolLLM)" if using_scripted_model() else "real model"
    )
    print(f"agent eval — backend: {backend}\n")
    with tempfile.TemporaryDirectory() as scratch:
        tools = make_assistant_tools(
            build_index(quiet=True),
            confirm=deny_all,
            memory_path=Path(scratch) / "assistant_memory.md",
            drafts_dir=Path(scratch) / "drafts",
        )
        print(_report(evaluate_agent(tools, load_cases())))


if __name__ == "__main__":  # `python -m ribot.agent_eval`
    main()
