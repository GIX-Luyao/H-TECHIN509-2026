"""Week 10: the quick-start script gets a fresh clone to a running agent, or names the fix."""

import importlib.util
import json
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location(
    "quickstart", ROOT / "scripts" / "quickstart.py"
)
quickstart = importlib.util.module_from_spec(spec)
sys.modules["quickstart"] = quickstart  # dataclasses look their module up here
spec.loader.exec_module(quickstart)

Step = quickstart.Step
StepResult = quickstart.StepResult


def completed(returncode=0, stdout="", stderr=""):
    return subprocess.CompletedProcess(
        args=[], returncode=returncode, stdout=stdout, stderr=stderr
    )


# ---- the runner -------------------------------------------------------------------


def test_run_steps_stops_at_first_failure_and_prints_the_fix():
    ran = []
    lines = []

    def step(name, result):
        def run():
            ran.append(name)
            return result

        return Step(name, run)

    steps = [
        step("one", StepResult(True, "fine")),
        step("two", StepResult(False, "broken", fix="do the thing")),
        step("three", StepResult(True, "never reached")),
    ]
    assert quickstart.run_steps(steps, out=lines.append) is False
    assert ran == ["one", "two"]
    text = "\n".join(lines)
    assert "broken" in text and "do the thing" in text
    assert "never reached" not in text


def test_run_steps_turns_an_unexpected_crash_into_a_failed_step():
    def boom():
        raise ValueError("surprise")

    lines = []
    assert quickstart.run_steps([Step("crashy", boom)], out=lines.append) is False
    assert "surprise" in "\n".join(lines)


def test_run_steps_reports_success_when_every_step_passes():
    lines = []
    steps = [
        Step("a", lambda: StepResult(True, "ok a")),
        Step("b", lambda: StepResult(True, "ok b")),
    ]
    assert quickstart.run_steps(steps, out=lines.append) is True


# ---- individual checks ------------------------------------------------------------


def test_python_version_check():
    assert quickstart.check_python((3, 12, 1)).ok
    old = quickstart.check_python((3, 9, 18))
    assert not old.ok and "3.10" in old.fix


def test_venv_check_passes_inside_a_venv_and_fails_outside():
    assert quickstart.check_venv(
        prefix="/repo/.venv", base_prefix="/usr", environ={}
    ).ok
    outside = quickstart.check_venv(prefix="/usr", base_prefix="/usr", environ={})
    assert not outside.ok and "activate" in outside.fix.lower()


def test_venv_check_accepts_a_named_conda_env_but_not_base():
    named = {"CONDA_PREFIX": "/conda/envs/ribot", "CONDA_DEFAULT_ENV": "ribot"}
    result = quickstart.check_venv(
        prefix="/conda/envs/ribot", base_prefix="/conda/envs/ribot", environ=named
    )
    assert result.ok and "conda" in result.message
    base = {"CONDA_PREFIX": "/conda", "CONDA_DEFAULT_ENV": "base"}
    assert not quickstart.check_venv(
        prefix="/conda", base_prefix="/conda", environ=base
    ).ok


def test_install_command_prefers_uv_and_falls_back_to_pip(tmp_path):
    req = tmp_path / "requirements.txt"
    with_uv = quickstart.install_command(req, uv_path="/bin/uv", python="py")
    assert with_uv[:3] == ["/bin/uv", "pip", "install"] and str(req) in with_uv
    without_uv = quickstart.install_command(req, uv_path=None, python="py")
    assert without_uv[:4] == ["py", "-m", "pip", "install"] and str(req) in without_uv


def test_install_failure_shows_the_tail_of_the_error(tmp_path):
    (tmp_path / "requirements.txt").write_text("numpy\n", encoding="utf-8")
    result = quickstart.install_requirements(
        tmp_path,
        runner=lambda *a, **k: completed(
            1, stderr="ERROR: No matching distribution for numpy"
        ),
        which=lambda _name: None,
    )
    assert not result.ok
    assert "No matching distribution" in result.message


def test_install_fails_clearly_without_requirements_file(tmp_path):
    result = quickstart.install_requirements(
        tmp_path, runner=None, which=lambda _n: None
    )
    assert not result.ok and "requirements.txt" in result.message


def test_env_file_is_optional(tmp_path):
    result = quickstart.check_env_file(tmp_path, runner=None)
    assert result.ok and "offline" in result.message.lower()


def test_env_file_must_be_git_ignored(tmp_path):
    (tmp_path / ".env").write_text("OPENAI_API_KEY=\n", encoding="utf-8")
    calls = []

    def runner(cmd, **kwargs):
        calls.append(cmd)
        if cmd[:2] == ["git", "rev-parse"]:
            return completed(0)
        return completed(1)  # git check-ignore: NOT ignored

    result = quickstart.check_env_file(tmp_path, runner=runner)
    assert not result.ok and ".gitignore" in result.fix
    assert ["git", "check-ignore", "-q", ".env"] in calls


def test_env_file_ignored_passes(tmp_path):
    (tmp_path / ".env").write_text("OPENAI_API_KEY=\n", encoding="utf-8")
    result = quickstart.check_env_file(tmp_path, runner=lambda cmd, **k: completed(0))
    assert result.ok


def test_env_file_outside_git_is_fine(tmp_path):
    (tmp_path / ".env").write_text("OPENAI_API_KEY=\n", encoding="utf-8")
    result = quickstart.check_env_file(tmp_path, runner=lambda cmd, **k: completed(128))
    assert result.ok


@pytest.mark.parametrize(
    ("environ", "expected"),
    [
        ({}, "offline"),
        ({"OPENAI_API_KEY": "  "}, "offline"),
        ({"OPENAI_API_KEY": "synthetic"}, "API"),
        ({"RIBOT_LLM": "Ollama", "OPENAI_API_KEY": "synthetic"}, "Ollama"),
    ],
)
def test_describe_mode(environ, expected):
    assert expected in quickstart.describe_mode(environ)


def test_ollama_check_is_skipped_unless_selected():
    result = quickstart.check_ollama({}, opener=None)
    assert result.ok and "skipped" in result.message


def test_ollama_check_reports_unreachable_server():
    def opener(url, timeout):
        raise OSError("connection refused")

    result = quickstart.check_ollama({"RIBOT_LLM": "ollama"}, opener=opener)
    assert not result.ok and "ollama serve" in result.fix.lower()


def tags_response(*names):
    body = json.dumps({"models": [{"name": name} for name in names]}).encode("utf-8")

    class Response:
        def __enter__(self):
            return self

        def __exit__(self, *exc):
            return False

        def read(self):
            return body

    return lambda url, timeout: Response()


def test_ollama_check_passes_when_the_model_is_pulled():
    environ = {"RIBOT_LLM": "ollama", "OLLAMA_MODEL": "llama3.2"}
    result = quickstart.check_ollama(environ, opener=tags_response("llama3.2:latest"))
    assert result.ok and "llama3.2" in result.message


def test_ollama_check_names_the_pull_command_when_the_model_is_missing():
    environ = {"RIBOT_LLM": "ollama", "OLLAMA_MODEL": "qwen3.5:2b"}
    result = quickstart.check_ollama(environ, opener=tags_response("llama3.2:latest"))
    assert not result.ok
    assert "ollama pull qwen3.5:2b" in result.fix and "llama3.2:latest" in result.fix


def test_duplicate_tool_names_are_found():
    class T:
        def __init__(self, name):
            self.name = name

    assert quickstart.duplicate_names([T("a"), T("b"), T("a")]) == ["a"]
    assert quickstart.duplicate_names([T("a"), T("b")]) == []


def test_check_tools_lists_the_real_toolbox():
    result = quickstart.check_tools()
    assert result.ok
    for name in (
        "search_docs",
        "list_sources",
        "remember",
        "save_draft",
        "current_date",
    ):
        assert name in result.message


def test_check_tools_rejects_a_duplicate_name():
    def make_tools(_retriever):
        class T:
            name = "search_docs"
            description = "Search."

        return [T(), T()]

    result = quickstart.check_tools(make_tools=make_tools)
    assert not result.ok and "search_docs" in result.message


def test_check_tools_rejects_an_empty_description():
    def make_tools(_retriever):
        class T:
            name = "mystery"
            description = "  "

        return [T()]

    result = quickstart.check_tools(make_tools=make_tools)
    assert not result.ok and "mystery" in result.message


def test_command_step_passes_and_fails_on_return_code():
    ok = quickstart.run_command(
        ["x"], ROOT, "it worked", "fix it", runner=lambda c, **k: completed(0)
    )
    assert ok.ok and ok.message == "it worked"
    bad = quickstart.run_command(
        ["x"],
        ROOT,
        "it worked",
        "fix it",
        runner=lambda c, **k: completed(2, stdout="3 failed"),
    )
    assert not bad.ok and "3 failed" in bad.message and bad.fix == "fix it"


# ---- the whole script -------------------------------------------------------------


def test_step_names_follow_the_flags():
    full = [
        s.name for s in quickstart.build_steps(skip_install=False, skip_tests=False)
    ]
    short = [s.name for s in quickstart.build_steps(skip_install=True, skip_tests=True)]
    assert "Install requirements" in full and "Run the test suite" in full
    assert "Install requirements" not in short and "Run the test suite" not in short
    assert full[0] == "Python version"
    assert short[-1] == "Tool menu"


def test_main_offline_without_install_or_tests_succeeds(capsys, monkeypatch):
    monkeypatch.setattr(
        quickstart, "check_venv", lambda **k: StepResult(True, "venv ok")
    )
    code = quickstart.main(["--skip-install", "--skip-tests"])
    out = capsys.readouterr().out
    assert code == 0, out
    assert "python -m ribot.assistant" in out


def test_main_returns_nonzero_when_a_step_fails(capsys, monkeypatch):
    monkeypatch.setattr(
        quickstart,
        "check_python",
        lambda *a, **k: StepResult(False, "too old", fix="upgrade"),
    )
    code = quickstart.main(["--skip-install", "--skip-tests"])
    assert code == 1
    assert "upgrade" in capsys.readouterr().out
