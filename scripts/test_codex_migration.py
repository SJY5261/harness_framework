"""Codex-primary migration tests for worklog automation."""

import importlib.util
import json
from pathlib import Path
from unittest.mock import MagicMock, patch


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
