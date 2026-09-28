"""The Week 1 check must never use configured providers or hide failures."""
import importlib.util
import os
from pathlib import Path
from unittest.mock import patch

import pytest

spec = importlib.util.spec_from_file_location(
    "check_env", Path(__file__).resolve().parents[1] / "scripts" / "check_env.py"
)
check_env = importlib.util.module_from_spec(spec)
spec.loader.exec_module(check_env)


def test_health_check_is_offline_and_restores_configuration(capsys):
    configured = {"OPENAI_API_KEY": "synthetic-not-a-key", "RIBOT_LLM": "ollama", "RIBOT_EMBED": "ollama"}
    with patch.dict(os.environ, configured), patch("socket.socket", side_effect=AssertionError("Network forbidden")):
        check_env.main()
        assert all(os.environ[name] == value for name, value in configured.items())
    assert "All core checks passed." in capsys.readouterr().out


def test_failed_chat_does_not_report_success(capsys):
    with patch("ribot.chatbot.ChatBot.reply", return_value=""):
        with pytest.raises(RuntimeError, match="Chat round-trip"):
            check_env.main()
    assert "All core checks passed." not in capsys.readouterr().out
