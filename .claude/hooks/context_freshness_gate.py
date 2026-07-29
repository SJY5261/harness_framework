#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
UserPromptSubmit hook: 규칙 파일 신선도 게이트 (M1).

CLAUDE.md / MEMORY.md 가 이 세션이 마지막으로 본 이후 변경됐으면, 모델이
답하기 전에 "원본을 다시 읽고 대조하라"는 지시를 컨텍스트에 주입한다.
변경이 없으면 아무것도 출력하지 않는다(추가 토큰 0, 속도 영향 없음).

세션 시작 시 파일은 이미 로드되므로, 한 세션에서 '처음 보는' 시점은 baseline
으로만 저장하고 주입하지 않는다. 그 이후의 변경분만 주입한다(중복 알림 방지).

상태는 세션별 파일(temp/tomes_ctx_fresh_<session_id>.json)에 저장해 동시 세션
간 경쟁을 피한다. answer_review_gate.py 와 동일하게 stdin JSON 을 읽는다.

배경: SESSION_DIALOGUE.md 합의안 M1. 시작 시 주입된 규칙 스냅샷이 stale 해도
사람 의지로 재읽기를 떠올려야 발동하던 것을, 이벤트(프롬프트 제출)에 묶어
시스템이 강제한다.
"""
import sys
import json
import hashlib
import tempfile
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
sys.stderr.reconfigure(encoding="utf-8", errors="replace")

# .claude/hooks/ -> .claude/ -> repo root
ROOT = Path(__file__).resolve().parent.parent.parent

# 감시 대상: 규칙 정본(CLAUDE.md) + 메모리 인덱스(MEMORY.md)
WATCH = {
    "CLAUDE.md": ROOT / "CLAUDE.md",
    "MEMORY.md": Path.home() / ".claude" / "projects"
    / "E--harness-framework" / "memory" / "MEMORY.md",
}


def read_stdin_json():
    try:
        raw = sys.stdin.read()
        return json.loads(raw) if raw.strip() else {}
    except Exception:
        return {}


def file_hash(p: Path):
    try:
        return hashlib.sha256(p.read_bytes()).hexdigest()
    except Exception:
        return None


def state_path(session_id: str) -> Path:
    safe = "".join(c for c in session_id if c.isalnum() or c in "-_") or "nosession"
    return Path(tempfile.gettempdir()) / f"tomes_ctx_fresh_{safe}.json"


def main():
    data = read_stdin_json()
    session_id = str(data.get("session_id") or "nosession")

    current = {name: file_hash(p) for name, p in WATCH.items()}

    sp = state_path(session_id)
    prev = {}
    first_seen = True
    if sp.exists():
        try:
            prev = json.loads(sp.read_text(encoding="utf-8"))
            first_seen = False
        except Exception:
            prev = {}

    # 상태를 항상 최신으로 갱신(다음 프롬프트가 이번을 기준으로 비교)
    try:
        sp.write_text(json.dumps(current, ensure_ascii=False), encoding="utf-8")
    except Exception:
        pass

    # 세션 첫 프롬프트: 파일은 시작 시 이미 로드됨 -> baseline 만 저장, 주입 없음
    if first_seen:
        sys.exit(0)

    changed = [
        name for name, h in current.items()
        if h is not None and prev.get(name) != h
    ]
    if not changed:
        sys.exit(0)

    files = ", ".join(changed)
    notice = (
        f"[규칙 신선도 알림] 이 세션 시작 이후 다음 규칙 파일이 변경되었습니다: {files}. "
        f"시작 시 로드된 내용은 이제 stale 합니다. 이 규칙에 근거해 판단/보고하기 전에 "
        f"해당 파일을 Read 로 전체 다시 읽어 현재 내용과 대조한 뒤 진행하세요."
    )
    print(notice)
    sys.exit(0)


if __name__ == "__main__":
    main()
