"""Week 10: from a fresh clone to a running agent, one command.

    python scripts/quickstart.py            # every check, then tells you how to start
    python scripts/quickstart.py --run      # ... and starts the assistant when all pass
    python scripts/quickstart.py --skip-install --skip-tests   # the quick re-check

Each step either passes or stops the script with the exact fix. Run it again after the
fix; it picks up from the top. Nothing here calls a paid model: the health check runs
offline, and the Ollama step only checks that your local server answers.
"""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
import urllib.request
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Iterable, Mapping, Sequence

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

MIN_PYTHON = (3, 10)
OUTPUT_TAIL_LINES = 12
OLLAMA_TIMEOUT_SECONDS = 3
DEFAULT_OLLAMA_HOST = "http://localhost:11434"
START_COMMAND = "python -m ribot.assistant"

Runner = Callable[..., subprocess.CompletedProcess]


@dataclass(frozen=True)
class StepResult:
    """One check's outcome: did it pass, what we saw, and how to fix it if not."""

    ok: bool
    message: str
    fix: str = ""


@dataclass(frozen=True)
class Step:
    """A named check. `run` returns a StepResult; it may also raise, which counts as a failure."""

    name: str
    run: Callable[[], StepResult]


# ---- the runner -------------------------------------------------------------------


def run_steps(steps: Sequence[Step], out: Callable[[str], None] = print) -> bool:
    """Run steps in order; stop at the first failure and print its fix."""
    total = len(steps)
    for number, step in enumerate(steps, start=1):
        out(f"[{number}/{total}] {step.name}")
        try:
            result = step.run()
        except Exception as err:  # noqa: BLE001 - any crash is reported, never hidden
            result = StepResult(
                False,
                f"crashed: {type(err).__name__}: {err}",
                fix="Read the error above; it names the file and line.",
            )
        if not result.ok:
            out(f"      FAILED: {result.message}")
            if result.fix:
                out(f"      Fix:    {result.fix}")
            out(
                f"\nStopped at step {number} ({step.name}). Fix it, then run "
                "`python scripts/quickstart.py` again."
            )
            return False
        out(f"      ok: {result.message}")
    return True


def _tail(text: str, lines: int = OUTPUT_TAIL_LINES) -> str:
    kept = [line for line in text.strip().splitlines() if line.strip()][-lines:]
    return "\n        ".join(kept)


def run_command(
    cmd: Sequence[str],
    root: Path,
    ok_message: str,
    fix: str,
    runner: Runner = subprocess.run,
) -> StepResult:
    """Run a command in the repo; pass on exit code 0, otherwise show the end of its output."""
    done = runner(list(cmd), cwd=root, capture_output=True, text=True)
    if done.returncode == 0:
        return StepResult(True, ok_message)
    output = _tail(f"{done.stdout or ''}\n{done.stderr or ''}")
    return StepResult(
        False,
        f"`{' '.join(cmd)}` exited with {done.returncode}:\n        {output}",
        fix,
    )


# ---- individual checks ------------------------------------------------------------


def check_python(version_info: Sequence[int] = tuple(sys.version_info)) -> StepResult:
    found = ".".join(str(part) for part in version_info[:3])
    if tuple(version_info[:2]) >= MIN_PYTHON:
        return StepResult(True, f"Python {found}")
    need = ".".join(str(part) for part in MIN_PYTHON)
    return StepResult(
        False,
        f"Python {found} is too old.",
        fix=f"Install Python {need} or newer, recreate .venv with it, and re-run.",
    )


def check_venv(
    prefix: str = sys.prefix,
    base_prefix: str = sys.base_prefix,
    environ: Mapping[str, str] = os.environ,
) -> StepResult:
    """A venv (or a named conda env) must be active, so installs stay inside the project."""
    if prefix != base_prefix:
        return StepResult(True, f"virtual environment at {prefix}")
    conda_env = environ.get("CONDA_DEFAULT_ENV", "")
    if conda_env and conda_env != "base" and environ.get("CONDA_PREFIX") == prefix:
        return StepResult(True, f"conda environment {conda_env!r} at {prefix}")
    return StepResult(
        False,
        "No virtual environment is active, so packages would install into your system Python.",
        fix="Activate it first: `source .venv/bin/activate` (macOS/Linux) or "
        "`.venv\\Scripts\\Activate.ps1` (Windows). No .venv yet? `uv venv` or "
        "`python -m venv .venv`.",
    )


def install_command(
    requirements: Path, uv_path: str | None, python: str = sys.executable
) -> list[str]:
    """uv when it is installed (fast, the course default), pip otherwise."""
    if uv_path:
        return [uv_path, "pip", "install", "-r", str(requirements), "--python", python]
    return [python, "-m", "pip", "install", "-r", str(requirements)]


def install_requirements(
    root: Path,
    runner: Runner | None = subprocess.run,
    which: Callable[[str], str | None] = shutil.which,
) -> StepResult:
    requirements = root / "requirements.txt"
    if not requirements.is_file():
        return StepResult(
            False,
            f"requirements.txt is missing from {root}.",
            fix="Restore it from git: `git checkout -- requirements.txt`.",
        )
    cmd = install_command(requirements, which("uv"))
    return run_command(
        cmd,
        root,
        "packages from requirements.txt are installed",
        fix="Read the last error line. A typo'd or unpinnable package name is the usual cause; "
        "a corporate network may also block installs (see SETUP_TROUBLESHOOTING.md).",
        runner=runner or subprocess.run,
    )


def check_env_file(root: Path, runner: Runner | None = subprocess.run) -> StepResult:
    """`.env` is optional. When it exists, Git must ignore it."""
    if not (root / ".env").is_file():
        return StepResult(
            True,
            "no .env file: the assistant runs offline (FakeLLM). "
            "Copy .env.example to .env to add a key or switch on Ollama.",
        )
    run = runner or subprocess.run
    inside = run(
        ["git", "rev-parse", "--is-inside-work-tree"],
        cwd=root,
        capture_output=True,
        text=True,
    )
    if inside.returncode != 0:
        return StepResult(
            True,
            ".env found (this folder is not a git repo, so it cannot be committed)",
        )
    ignored = run(
        ["git", "check-ignore", "-q", ".env"], cwd=root, capture_output=True, text=True
    )
    if ignored.returncode == 0:
        return StepResult(True, ".env found and git-ignored")
    return StepResult(
        False,
        ".env exists but Git would commit it.",
        fix="Add a line `.env` to .gitignore. If .env was ever committed, run "
        "`git rm --cached .env`, commit, and rotate every key that was in it.",
    )


def describe_mode(environ: Mapping[str, str]) -> str:
    if environ.get("RIBOT_LLM", "").strip().lower() == "ollama":
        return "local model via Ollama (RIBOT_LLM=ollama)"
    if environ.get("OPENAI_API_KEY", "").strip():
        return "API model (OPENAI_API_KEY is set)"
    return "offline (FakeLLM: scripted, so it shows the loop but does not really choose tools)"


def _model_is_pulled(model: str, names: Iterable[str]) -> bool:
    wanted = model if ":" in model else f"{model}:latest"
    return any(name in (model, wanted) for name in names)


def check_ollama(
    environ: Mapping[str, str],
    opener: Callable[..., object] | None = urllib.request.urlopen,
) -> StepResult:
    """Only when RIBOT_LLM=ollama: is the server up, and is the model pulled?"""
    if environ.get("RIBOT_LLM", "").strip().lower() != "ollama":
        return StepResult(True, "skipped (not using Ollama)")
    from ribot.config import DEFAULT_OLLAMA_MODEL

    host = environ.get("OLLAMA_HOST", DEFAULT_OLLAMA_HOST).rstrip("/")
    model = environ.get("OLLAMA_MODEL", DEFAULT_OLLAMA_MODEL)
    try:
        with opener(f"{host}/api/tags", timeout=OLLAMA_TIMEOUT_SECONDS) as response:
            body = json.loads(response.read().decode("utf-8"))
    except (OSError, ValueError) as err:
        return StepResult(
            False,
            f"Ollama did not answer at {host} ({err}).",
            fix="Start the Ollama app (or run `ollama serve`), then re-run. "
            "To go back to offline mode, remove RIBOT_LLM from .env.",
        )
    names = [entry.get("name", "") for entry in body.get("models", [])]
    if not _model_is_pulled(model, names):
        return StepResult(
            False,
            f"Ollama is running but {model!r} is not pulled.",
            fix=f"Run `ollama pull {model}`, or set OLLAMA_MODEL in .env to one "
            f"you have: {', '.join(names) or 'none yet'}.",
        )
    return StepResult(True, f"Ollama is up at {host} with {model}")


def check_backend() -> StepResult:
    """Load .env the way the assistant does, then report and check the chosen backend."""
    import ribot.config  # noqa: F401 - importing it loads .env into os.environ

    ollama = check_ollama(os.environ)
    if not ollama.ok:
        return ollama
    return StepResult(True, describe_mode(os.environ))


def duplicate_names(tools: Iterable[object]) -> list[str]:
    counts = Counter(getattr(tool, "name", "") for tool in tools)
    return sorted(name for name, count in counts.items() if count > 1)


def check_tools(
    make_tools: Callable[..., Sequence[object]] | None = None
) -> StepResult:
    """Build the index and the assistant's toolbox; every name unique, every description filled."""
    from ribot.build_index import build_index
    from ribot.toolbox import make_assistant_tools

    retriever = build_index(quiet=True)
    tools = (make_tools or make_assistant_tools)(retriever)
    repeated = duplicate_names(tools)
    if repeated:
        return StepResult(
            False,
            f"two tools share the name(s) {repeated}; the model cannot tell them apart.",
            fix="Rename one of them in ribot/my_tools.py.",
        )
    blank = [
        tool.name for tool in tools if not str(getattr(tool, "description", "")).strip()
    ]
    if blank:
        return StepResult(
            False,
            f"tool(s) {blank} have no description, so the model never knows when to call them.",
            fix="Write a description that says WHEN to use the tool.",
        )
    names = ", ".join(tool.name for tool in tools)
    return StepResult(True, f"index built; {len(tools)} tools on the menu: {names}")


# ---- the whole script -------------------------------------------------------------


def build_steps(skip_install: bool, skip_tests: bool, root: Path = ROOT) -> list[Step]:
    python = sys.executable
    steps = [
        Step("Python version", lambda: check_python()),
        Step("Virtual environment", lambda: check_venv()),
    ]
    if not skip_install:
        steps.append(Step("Install requirements", lambda: install_requirements(root)))
    steps += [
        Step(".env and secrets", lambda: check_env_file(root)),
        Step(
            "Offline health check",
            lambda: run_command(
                [python, "scripts/check_env.py"],
                root,
                "chat, memory and embeddings work offline",
                fix="Read the error above. A ModuleNotFoundError means the install step was skipped "
                "or failed: re-run without --skip-install.",
            ),
        ),
        Step("Model backend", check_backend),
        Step("Tool menu", lambda: check_tools()),
    ]
    if not skip_tests:
        steps.append(
            Step(
                "Run the test suite",
                lambda: run_command(
                    [python, "-m", "pytest", "-q"],
                    root,
                    "all tests pass",
                    fix="Run `python -m pytest -q` to see every failure; fix the first one listed.",
                ),
            )
        )
    return steps


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Get this repo from a fresh clone to a running agent."
    )
    parser.add_argument(
        "--skip-install", action="store_true", help="don't install requirements.txt"
    )
    parser.add_argument("--skip-tests", action="store_true", help="don't run pytest")
    parser.add_argument(
        "--run", action="store_true", help="start the assistant when every check passes"
    )
    args = parser.parse_args(argv)

    print(f"ribot quick start in {ROOT}\n")
    if not run_steps(build_steps(args.skip_install, args.skip_tests)):
        return 1
    print(f"\nReady. Start your agent with:\n\n    {START_COMMAND}\n")
    print("Inside it: /trace shows which tools ran, /exit quits.")
    if args.run:
        return subprocess.call([sys.executable, "-m", "ribot.assistant"], cwd=ROOT)
    return 0


if __name__ == "__main__":
    sys.exit(main())
