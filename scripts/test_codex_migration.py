"""Codex-primary migration tests for worklog automation."""

import importlib.util
import io
import json
import os
import subprocess
import datetime as dt
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest


ROOT = Path(__file__).parent.parent


def _load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


worklog = _load("daily_worklog", ROOT / "scripts" / "daily_worklog.py")


def test_run_codex_is_read_only_ephemeral_and_uses_stdin(tmp_path):
    fake_exe = str(tmp_path / "codex.exe")

    def fake_run(cmd, **kwargs):
        output_path = Path(cmd[cmd.index("--output-last-message") + 1])
        output_path.write_text('{"summary":"ok","tasks":[]}', encoding="utf-8")
        return MagicMock(returncode=0, stdout="", stderr="")

    with patch.object(worklog, "find_codex", return_value=fake_exe), patch(
        "subprocess.run", side_effect=fake_run
    ) as run:
        result = worklog.run_codex("PROMPT")

    cmd = run.call_args[0][0]
    assert cmd[:2] == [fake_exe, "exec"]
    assert ["--sandbox", "read-only"] == cmd[cmd.index("--sandbox"):cmd.index("--sandbox") + 2]
    assert "--ephemeral" in cmd
    assert cmd[-1] == "-"
    assert run.call_args[1]["input"] == "PROMPT"
    assert json.loads(result)["summary"] == "ok"


def test_collect_codex_session_filters_workspace(tmp_path):
    session_root = tmp_path / "sessions"
    day_dir = session_root / "2026" / "07" / "24"
    day_dir.mkdir(parents=True)
    events = [
        {
            "type": "session_meta",
            "payload": {"cwd": str(worklog.HARNESS)},
        },
        {
            "type": "event_msg",
            "payload": {"type": "user_message", "message": "요청"},
        },
        {
            "type": "event_msg",
            "payload": {"type": "agent_message", "message": "진행"},
        },
    ]
    (day_dir / "rollout-test.jsonl").write_text(
        "\n".join(json.dumps(event, ensure_ascii=False) for event in events),
        encoding="utf-8",
    )

    with patch.object(worklog, "CODEX_SESSION_DIR", session_root):
        blocks = worklog._collect_codex_sessions(worklog._dt.date(2026, 7, 24))

    assert len(blocks) == 1
    assert "나: 요청" in blocks[0]
    assert "Codex: 진행" in blocks[0]


def test_collect_claude_history_is_read_only_and_keeps_session_boundary(tmp_path):
    transcript_root = tmp_path / "claude-project"
    transcript_root.mkdir()
    transcript = transcript_root / "session.jsonl"
    events = [
        {"type": "user", "message": {"content": "Claude 명시 요청"}},
        {"type": "assistant", "message": {"content": "Claude 작업 결과"}},
    ]
    transcript.write_text(
        "\n".join(json.dumps(event, ensure_ascii=False) for event in events),
        encoding="utf-8",
    )
    target_date = dt.date(2026, 7, 24)
    stamp = dt.datetime(2026, 7, 24, 12, 0, 0).timestamp()
    os.utime(transcript, (stamp, stamp))

    with patch.object(worklog, "CLAUDE_TRANSCRIPT_DIR", transcript_root), patch(
        "subprocess.run"
    ) as run:
        blocks = worklog._collect_claude_sessions(target_date)

    run.assert_not_called()
    assert len(blocks) == 1
    assert "Claude 세션 1" in blocks[0]
    assert "나: Claude 명시 요청" in blocks[0]
    assert "Claude: Claude 작업 결과" in blocks[0]


def test_context_freshness_hook_emits_valid_codex_json_after_rule_change(
    tmp_path, monkeypatch, capsys
):
    hook = _load(
        "context_freshness_gate",
        ROOT / ".codex" / "hooks" / "context_freshness_gate.py",
    )
    watched = {
        name: tmp_path / name
        for name in (
            "AGENTS.md",
            "PROJECT_RULES.md",
            "HANDOFF.md",
            "docs/SECOND_BRAIN.md",
        )
    }
    for path in watched.values():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("initial", encoding="utf-8")

    monkeypatch.setattr(hook, "WATCH", watched)
    monkeypatch.setattr(hook.tempfile, "gettempdir", lambda: str(tmp_path))
    payload = json.dumps(
        {
            "session_id": "hook-contract-test",
            "turn_id": "turn-1",
            "hook_event_name": "UserPromptSubmit",
            "prompt": "test",
        }
    )

    monkeypatch.setattr(hook.sys, "stdin", io.StringIO(payload))
    assert hook.main() == 0
    assert capsys.readouterr().out == ""

    watched["AGENTS.md"].write_text("changed", encoding="utf-8")
    monkeypatch.setattr(hook.sys, "stdin", io.StringIO(payload))
    assert hook.main() == 0
    output = json.loads(capsys.readouterr().out)
    hook_output = output["hookSpecificOutput"]
    assert hook_output["hookEventName"] == "UserPromptSubmit"
    assert "AGENTS.md" in hook_output["additionalContext"]

    monkeypatch.setattr(hook.sys, "stdin", io.StringIO(payload))
    assert hook.main() == 0
    assert capsys.readouterr().out == ""


def test_codex_hook_resolves_script_from_workspace_ancestor():
    config = json.loads((ROOT / ".codex" / "hooks.json").read_text(encoding="utf-8"))
    handler = config["hooks"]["UserPromptSubmit"][0]["hooks"][0]

    assert "context_freshness_gate.py" in handler["command"]
    assert "dirname" in handler["command"]
    assert "context_freshness_gate.py" in handler["commandWindows"]
    assert "Split-Path -Parent" in handler["commandWindows"]
    assert r"D:\Tool\Python\Launcher\py.exe" in handler["commandWindows"]
    assert not handler["commandWindows"].lstrip().lower().startswith("powershell")


def test_codex_windows_hook_command_runs_from_nested_workspace(tmp_path):
    if os.name != "nt":
        pytest.skip("Windows command hook contract")

    config = json.loads((ROOT / ".codex" / "hooks.json").read_text(encoding="utf-8"))
    handler = config["hooks"]["UserPromptSubmit"][0]["hooks"][0]
    payload = json.dumps(
        {
            "session_id": "hook-windows-command-test",
            "turn_id": "turn-1",
            "hook_event_name": "UserPromptSubmit",
            "prompt": "test",
        }
    )
    env = os.environ.copy()
    env["TEMP"] = str(tmp_path)
    env["TMP"] = str(tmp_path)

    result = subprocess.run(
        ["powershell.exe", "-NoProfile", "-Command", handler["commandWindows"]],
        cwd=ROOT / "Projects" / "Tomes-Cloud",
        input=payload,
        text=True,
        encoding="utf-8",
        errors="replace",
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
        env=env,
    )

    assert result.returncode == 0, result.stderr
    assert result.stdout == ""
    assert (tmp_path / "tomes_codex_rules_hook-windows-command-test.json").is_file()
