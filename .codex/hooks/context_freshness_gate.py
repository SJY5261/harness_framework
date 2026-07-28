#!/usr/bin/env python3
"""Codex UserPromptSubmit hook: notify when repository rules changed mid-session."""

import hashlib
import json
import sys
import tempfile
from pathlib import Path


for _stream in (sys.stdout, sys.stderr):
    if hasattr(_stream, "reconfigure"):
        _stream.reconfigure(encoding="utf-8", errors="replace")

ROOT = Path(__file__).resolve().parents[2]
WATCH = {
    "AGENTS.md": ROOT / "AGENTS.md",
    "PROJECT_RULES.md": ROOT / "PROJECT_RULES.md",
    "HANDOFF.md": ROOT / "HANDOFF.md",
}


def _input():
    try:
        raw = sys.stdin.read()
        return json.loads(raw) if raw.strip() else {}
    except Exception:
        return {}


def _digest(path):
    try:
        return hashlib.sha256(path.read_bytes()).hexdigest()
    except OSError:
        return None


def main():
    data = _input()
    session_id = str(data.get("session_id") or data.get("sessionId") or "nosession")
    safe_id = "".join(c for c in session_id if c.isalnum() or c in "-_") or "nosession"
    state = Path(tempfile.gettempdir()) / f"tomes_codex_rules_{safe_id}.json"
    current = {name: _digest(path) for name, path in WATCH.items()}

    previous = None
    if state.exists():
        try:
            previous = json.loads(state.read_text(encoding="utf-8"))
        except Exception:
            previous = None
    try:
        state.write_text(json.dumps(current, ensure_ascii=False), encoding="utf-8")
    except OSError:
        return 0

    if previous is None:
        return 0
    changed = [
        name for name, digest in current.items()
        if digest is not None and previous.get(name) != digest
    ]
    if changed:
        files = ", ".join(changed)
        notice = (
            f"[규칙 신선도 알림] 세션 중 변경된 정본: {files}. "
            "해당 규칙에 근거해 판단하기 전에 원본을 다시 읽고 대조하세요."
        )
        print(
            json.dumps(
                {
                    "hookSpecificOutput": {
                        "hookEventName": "UserPromptSubmit",
                        "additionalContext": notice,
                    }
                },
                ensure_ascii=False,
            )
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
