#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Stop hook: answer review gate. (v2 — 2026-07-15 개선)

이번 턴 답변이 코드/깃 사실 주장을 포함하는데 answer-reviewer 서브에이전트로
검증하지 않았으면, 턴 종료를 막고 검토를 강제한다. 검토를 거쳤으면 최종
메시지에 구분 배너(CLAUDE.md 규칙)가 있는지도 확인한다.

v2 변경점 (v1 결함 교정):
- 검토 호출 탐지: tool_use JSON 문자열 매칭(파일 Read만 해도 오통과) →
  Agent tool_use 의 input.subagent_type == "answer-reviewer" 정밀 매칭.
- stop_hook_active 무조건 통과 제거 → 세션 상태 파일로 턴당 차단 2회 상한.
  (1회 차단 후 무검토로 재종료하면 통과되던 구멍 봉쇄. 상태 IO 실패 시에만
  구버전 동작(stop_hook_active 통과)으로 폴백해 무한루프를 방지한다.)
- ASCII 키워드: substring(diff가 different에 매칭) → 단어 경계 정규식.
- 옵트아웃 마커: 턴 전체 프리픽스 매칭(규칙 인용만으로 오통과) →
  '최종 assistant 메시지'에 '전체 마커 문구'가 있을 때만 인정.
- 옵트아웃 사용 시 logs/answer_review_optouts.log 에 감사 기록.

v3 변경점 (2026-07-21 루프 결함 교정):
- 턴 경계 오판 교정: Stop 훅 차단 피드백(isMeta=true)과 async agent 완료
  task-notification(origin.kind=task-notification, promptSource=system)이 트랜스크립트에
  type=user 비 tool_result 로 저장돼 last_user_idx 를 갱신시켰다. 그 결과 앞선 reviewer
  호출이 턴 밖으로 빠져 reviewer_invoked=False 로 오판(재검토 무한 요구)되고, turn_key
  가 매 주입 메시지마다 바뀌어 MAX_BLOCKS_PER_TURN 상한이 무력화돼 루프가 발생했다.
  → last_user_idx 산정을 구조적 필드(origin.kind=="human" / promptSource=="typed") 기반
  genuine_user_verdict 로 바꿔 '진짜 사용자 입력'에만 턴 경계를 고정한다. 메타 필드가
  없는 구버전 트랜스크립트는 기존 휴리스틱(tool_result + 텍스트 시그니처)으로 폴백한다.

한계: 답변 텍스트는 이미 화면에 표시된 뒤 실행되므로 첫 노출은 막지 못한다.
선검토(CLAUDE.md '검토 반영 답변 구분 배너' 규칙)가 정본이고 이 훅은 백스톱이다.
알려진 탐지 공백: SendMessage 로 기존 리뷰어 에이전트를 이어 쓰는 경우는
subagent_type 이 없어 탐지하지 못한다(신규 Agent 호출을 사용할 것).
"""
import sys
import json
import re
import tempfile
from datetime import datetime
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
sys.stderr.reconfigure(encoding="utf-8", errors="replace")

# 코드/깃 사실 주장 신호 — ASCII 는 단어 경계로, 한글은 substring 으로 검사
ASCII_CLAIM_RE = re.compile(
    r"\b(git|commit|diff|branch|redis|sessionstorage|cacheable|cacheevict|"
    r"queryid|serviceimpl|daoimpl|controller)\b"
    r"|\.(java|jsp|js|xml|yml|gradle)\b",
    re.IGNORECASE,
)
KO_CLAIM_KEYWORDS = [
    "커밋", "브랜치", "변경사항", "변경 내역", "변경된", "수정사항",
    "캐시", "쿼리", "메서드", "함수", "클래스",
    "수정했", "변경했", "추가했", "삭제했", "이동했", "생성했", "구현했",
]
REVIEWER_NAME = "answer-reviewer"
# 옵트아웃: CLAUDE.md 규칙의 전체 마커 문구가 '최종 메시지'에 있을 때만 인정
REVIEW_SKIP_MARKER = "[검토 불요: 신규 저장소 사실 주장 없음]"
BANNER_SIG = "검토 반영 답변 (REVIEW-VERIFIED)"
MAX_BLOCKS_PER_TURN = 2
# 주입된 합성 user 메시지(진짜 사용자 입력 아님) — 메타 필드 없는 구버전 폴백용
SYNTHETIC_USER_SIGNS = (
    "SYSTEM NOTIFICATION - NOT USER INPUT",
    "<task-notification>",
    "Stop hook feedback",
    "[검토 훅]",
)

HARNESS_ROOT = Path(__file__).resolve().parents[2]
OPTOUT_LOG = HARNESS_ROOT / "logs" / "answer_review_optouts.log"


def read_stdin_json():
    try:
        raw = sys.stdin.read()
        return json.loads(raw) if raw.strip() else {}
    except Exception:
        return {}


def iter_records(path):
    try:
        with open(path, encoding="utf-8", errors="replace") as fh:
            for line in fh:
                line = line.strip()
                if not line:
                    continue
                try:
                    yield json.loads(line)
                except Exception:
                    continue
    except Exception:
        return


def content_text(content):
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts = []
        for x in content:
            if isinstance(x, dict) and x.get("type") == "text":
                parts.append(x.get("text", ""))
        return " ".join(parts)
    return ""


def is_tool_result(content):
    return isinstance(content, list) and any(
        isinstance(x, dict) and x.get("type") == "tool_result" for x in content
    )


def is_synthetic_user(content):
    """구버전 폴백: 메타 필드가 없을 때 텍스트 시그니처로 합성 메시지 판별."""
    txt = content_text(content)
    return any(sign in txt for sign in SYNTHETIC_USER_SIGNS)


def genuine_user_verdict(rec):
    """진짜 사용자 입력 여부. True=사용자, False=합성(피드백/알림), None=메타 없음.

    트랜스크립트 최상위 메타 필드로 판정한다:
      진짜 사용자: origin.kind=="human" / promptSource=="typed"
      Stop 훅 피드백: isMeta==true
      task-notification: origin.kind=="task-notification", promptSource=="system"
    """
    origin = rec.get("origin")
    if isinstance(origin, dict) and "kind" in origin:
        return origin.get("kind") == "human"
    ps = rec.get("promptSource")
    if ps is not None:
        return ps == "typed"
    if rec.get("isMeta"):
        return False
    return None


def has_claims(text):
    if ASCII_CLAIM_RE.search(text):
        return True
    return any(kw in text for kw in KO_CLAIM_KEYWORDS)


def reviewer_invoked_in(content):
    """Agent tool_use 의 subagent_type 으로만 판정 (파일 Read/Grep 오통과 방지)."""
    if not isinstance(content, list):
        return False
    for x in content:
        if not (isinstance(x, dict) and x.get("type") == "tool_use"):
            continue
        inp = x.get("input")
        if isinstance(inp, dict) and inp.get("subagent_type") == REVIEWER_NAME:
            return True
    return False


def state_path(session_id):
    safe = "".join(c for c in session_id if c.isalnum() or c in "-_") or "nosession"
    return Path(tempfile.gettempdir()) / f"tomes_answer_gate_{safe}.json"


def load_blocks(session_id, turn_key):
    """이 턴에서 이미 차단한 횟수. 상태 IO 실패 시 None."""
    try:
        sp = state_path(session_id)
        if not sp.exists():
            return 0
        st = json.loads(sp.read_text(encoding="utf-8"))
        return int(st.get("blocks", 0)) if st.get("turn") == turn_key else 0
    except Exception:
        return None


def save_blocks(session_id, turn_key, blocks):
    try:
        state_path(session_id).write_text(
            json.dumps({"turn": turn_key, "blocks": blocks}), encoding="utf-8"
        )
        return True
    except Exception:
        return False


def log_optout(session_id, last_text):
    try:
        OPTOUT_LOG.parent.mkdir(parents=True, exist_ok=True)
        head = " ".join(last_text.split())[:100]
        with open(OPTOUT_LOG, "a", encoding="utf-8") as fh:
            fh.write(
                f"{datetime.now().isoformat(timespec='seconds')} "
                f"session={session_id} answer_head={head}\n"
            )
    except Exception:
        pass


def build_reason(kind):
    banner = (
        "========================================\n"
        "||||  검토 반영 답변 (REVIEW-VERIFIED)\n"
        "||||  아래부터 검증을 거친 내용입니다\n"
        "========================================\n"
    )
    if kind == "banner":
        return (
            "[검토 훅] answer-reviewer 검토는 확인됐지만 최종 메시지에 구분 배너가 "
            "없습니다. 검토 결과(누락/오류 지적)를 반영·정정한 최종 답변을 아래 배너로 "
            "시작해 다시 제시하세요 (CLAUDE.md '검토 반영 답변 구분 배너' 규칙 정본):\n"
            + banner
        )
    return (
        "[검토 훅] 이 답변에 코드/깃 사실 주장이 포함된 것으로 보입니다. "
        "answer-reviewer 서브에이전트(Agent 툴, subagent_type=answer-reviewer 신규 호출 "
        "— SendMessage 이어쓰기는 인정되지 않음)로 범위와 사실을 실제 저장소와 대조 "
        "검증하세요. 의뢰 시 ①원 사용자 질문 전문 ②답변 초안 전체 ③참조한 파일 목록을 "
        "함께 전달합니다. 검증 후 아래 큰 구분 배너로 시작해 검토된 답변을 제시하세요 "
        "(CLAUDE.md '검토 반영 답변 구분 배너' 규칙 정본):\n"
        + banner +
        "누락이나 오류가 있으면 정정하세요. "
        "이번 답변에 신규 저장소 사실 주장이 없다면(개념 질문·기검증 사실 재진술 등) "
        "최종 메시지에 '" + REVIEW_SKIP_MARKER + "' 마커(전체 문구 그대로)를 넣어 "
        "검토를 생략할 수 있습니다."
    )


def main():
    data = read_stdin_json()

    transcript = data.get("transcript_path")
    if not transcript:
        sys.exit(0)

    records = list(iter_records(transcript))
    if not records:
        sys.exit(0)

    # 마지막 '진짜' 사용자 메시지 위치 찾기.
    # 구조적 메타 필드(origin.kind/promptSource)로 판정하고, 메타가 없는 구버전
    # 트랜스크립트는 tool_result + 텍스트 시그니처 휴리스틱으로 폴백한다.
    # (Stop 훅 피드백·task-notification 이 type=user 비 tool_result 로 저장돼 턴
    #  경계를 흔들던 v2 루프 결함 교정 — v3)
    last_user_idx = -1
    for i, rec in enumerate(records):
        if rec.get("type") != "user":
            continue
        verdict = genuine_user_verdict(rec)
        if verdict is True:
            last_user_idx = i
        elif verdict is False:
            continue
        else:  # 메타 없음 → 구버전 폴백
            content = rec.get("message", {}).get("content")
            if is_tool_result(content) or is_synthetic_user(content):
                continue
            last_user_idx = i

    turn = records[last_user_idx + 1:] if last_user_idx >= 0 else records

    assistant_texts = []
    reviewer_invoked = False
    for rec in turn:
        if rec.get("type") != "assistant":
            continue
        content = rec.get("message", {}).get("content")
        text = content_text(content)
        if text.strip():
            assistant_texts.append(text)
        if reviewer_invoked_in(content):
            reviewer_invoked = True

    if not assistant_texts:
        sys.exit(0)

    all_text = " ".join(assistant_texts).lower()
    last_text = assistant_texts[-1]
    claims = has_claims(all_text)
    optout = REVIEW_SKIP_MARKER in last_text
    banner_ok = BANNER_SIG in last_text

    session_id = str(data.get("session_id") or "nosession")
    turn_key = last_user_idx
    blocks = load_blocks(session_id, turn_key)
    if blocks is None:
        # 상태 IO 불가 — 구버전 폴백: 재진입이면 통과(무한루프 방지)
        if data.get("stop_hook_active"):
            sys.exit(0)
        blocks = 0
    if blocks >= MAX_BLOCKS_PER_TURN:
        sys.exit(0)

    block_kind = None
    if reviewer_invoked:
        if not banner_ok and not optout:
            block_kind = "banner"
    elif claims and not optout:
        block_kind = "review"

    if block_kind:
        if not save_blocks(session_id, turn_key, blocks + 1):
            # 카운트를 못 남기면 재차단 시 무한루프 위험 — 재진입 상태면 포기
            if data.get("stop_hook_active"):
                sys.exit(0)
        print(json.dumps(
            {"decision": "block", "reason": build_reason(block_kind)},
            ensure_ascii=False,
        ))
        sys.exit(0)

    if claims and optout and not reviewer_invoked:
        log_optout(session_id, last_text)

    sys.exit(0)


if __name__ == "__main__":
    main()
