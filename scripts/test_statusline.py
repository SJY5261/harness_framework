"""Project Claude Code status-line tests."""

import importlib.util
import json
from pathlib import Path


STATUSLINE_PATH = Path(__file__).parent.parent / ".claude" / "statusline.py"
SPEC = importlib.util.spec_from_file_location("statusline", STATUSLINE_PATH)
statusline = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(statusline)


def _write_transcript(path, blocks):
    event = {"message": {"role": "assistant", "content": blocks}}
    path.write_text(json.dumps(event, ensure_ascii=False) + "\n", encoding="utf-8")


def test_build_status_shows_recent_tool_context_and_cost(tmp_path):
    transcript = tmp_path / "session.jsonl"
    _write_transcript(
        transcript,
        [{"type": "tool_use", "name": "Bash", "input": {"command": "py -m pytest -q"}}],
    )
    data = {
        "transcript_path": str(transcript),
        "cost": {"total_duration_ms": 522000, "total_cost_usd": 0.84},
        "context_window": {"used_percentage": 37},
    }

    result = statusline.build_status(data)

    assert "[작업 08:42]" in result
    assert "현재: 명령 실행: py -m pytest -q" in result
    assert "context 37%" in result
    assert "$0.84" in result


def test_task_progress_is_only_shown_when_real_tasks_exist(tmp_path):
    transcript = tmp_path / "session.jsonl"
    events = [
        {
            "message": {
                "role": "assistant",
                "content": [
                    {
                        "type": "tool_use",
                        "id": "tool-use-create",
                        "name": "TaskCreate",
                        "input": {"subject": "구현"},
                    },
                    {
                        "type": "tool_use",
                        "id": "update-1",
                        "name": "TaskUpdate",
                        "input": {"taskId": "1", "status": "completed"},
                    },
                ],
            }
        }
    ]
    transcript.write_text(
        "\n".join(json.dumps(event, ensure_ascii=False) for event in events),
        encoding="utf-8",
    )

    result = statusline.build_status(
        {
            "transcript_path": str(transcript),
            "cost": {"total_duration_ms": 1000},
            "context_window": {},
        }
    )

    assert "계획 1/1" in result


def test_missing_transcript_uses_safe_fallback():
    result = statusline.build_status(
        {
            "transcript_path": "does-not-exist.jsonl",
            "cost": {"total_duration_ms": 0},
            "context_window": {"used_percentage": None},
        }
    )

    assert result == "[작업 00:00] | 현재: 응답 준비 | context 0%"
