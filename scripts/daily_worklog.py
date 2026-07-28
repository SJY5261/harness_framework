#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""daily_worklog.py - 그날 작업 내용/배운 지식을 정리해 Notion에 기록.

수집: 3개 git 저장소의 그날(KST) 커밋 + Codex 중심 세션 로그(jsonl)
요약: codex exec (headless) 로 구조화 JSON 생성
출력: Notion API 로 풍부한 블록(콜아웃/표/토글/체크박스)으로 렌더
       --style tracker(기본): '작업 트래커' DB에 작업(task)마다 1행. 제목엔 날짜 미포함.
       --style page : 부모 페이지 하위에 일자 페이지
       --style db   : 부모 페이지 하위 데이터베이스에 일자 항목(없으면 DB 생성)
       --style both : 둘 다(테스트용)

다일(여러 날) 작업 이어쓰기(tracker):
  작업 정체성을 logs/worklog_tasks.json(원장)에 id<->Notion page_id 로 영구 보존한다.
  실행 시 원장의 '열린(미완) 작업' 목록 + HANDOFF.md 를 Codex에 주고, 오늘 한 일이
  어느 작업의 연속인지(task_ref)를 '제목이 아니라 맥락+HANDOFF'로 판정. 연속이면 그
  page 에 진행분을 append + 상태 갱신(끝나면 '완료'), 새 일이면 새 행+원장 등록.
  같은 날 재실행은 멱등(원장 days 기록). 식별이 id 라 제목이 바뀌어도 안전.

환경변수:
  NOTION_TOKEN            Notion Internal Integration Secret (ntn_... / secret_...)
  NOTION_TRACKER_DB_ID    '작업 트래커' DB ID (tracker 방식, 기본)
  NOTION_PARENT_PAGE_ID   기록을 쌓을 부모 페이지 ID (page/db 방식용)
  NOTION_DATABASE_ID      (선택) 이미 만든 일지 DB ID. 없으면 db 모드에서 자동 생성 후 안내.

옵션:
  --date YYYY-MM-DD   대상 날짜(기본: 오늘 KST)
  --style page|db|both   출력 방식 (기본 page)
  --dry-run           Notion 전송 없이 마크다운/JSON만 logs/ 에 저장
  --no-ai             Codex 요약 생략(원자료 기반 최소 JSON)
  --model NAME        Codex 요약 모델(생략 시 사용자 Codex 기본값)
  --title-suffix STR  제목 뒤에 붙일 표식(테스트 중복 구분용)
  --status STR        '작업 트래커' 행 상태 수동 지정(시작 전|진행 중|완료).
                      생략 시 그날 하네스 스텝 완료 여부로 자동 판정.

cp949 환경 대비: 모든 입출력 UTF-8 명시.
"""
import argparse
import datetime as _dt
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
sys.stderr.reconfigure(encoding="utf-8", errors="replace")

# --- 경로/설정 ---------------------------------------------------------------
# 현재 업무 PC 하네스 루트는 D:\harness_framework이며, 다른 환경에서도 이 파일 위치로 루트를 판별한다.
# 스크립트 위치(scripts/ 상위)에서 자동 유도한다 — 양쪽 PC에서 수정 없이 동작.
HARNESS = Path(__file__).resolve().parent.parent
REPOS = [
    HARNESS,
    HARNESS / "Projects" / "Tomes-Cloud",
    HARNESS / "Projects" / "Test-Automize",
]
CODEX_SESSION_DIR = Path.home() / ".codex" / "sessions"
CLAUDE_TRANSCRIPT_DIR = (
    Path.home() / ".claude" / "projects"
    / re.sub(r"[^A-Za-z0-9]", "-", str(HARNESS))
)
LOG_DIR = HARNESS / "logs"
HANDOFF_PATH = HARNESS / "HANDOFF.md"
# 작업 정체성 원장: 작업마다 안정적 id <-> Notion page_id 를 보존해, 이어짐을
# 제목이 아니라 page_id 로 매칭한다(제목 충돌 리스크 제거). 다일 작업의 시작~완료
# 히스토리를 여기에 누적한다.
TASK_LEDGER = LOG_DIR / "worklog_tasks.json"
# 노션 미접속 환경(개인 PC)에서 쌓인 일지의 이관 대기 목록(복귀 후 --from-json 백필).
PENDING_PATH = LOG_DIR / "notion_이관대기.md"
HANDOFF_CHAR_CAP = 24000  # 프롬프트에 넣을 HANDOFF 상한(최근 인수인계 위주).
SESSION_CHAR_CAP = 120000  # AI 요약 입력 상한
MSG_CHAR_CAP = 2000        # 메시지 1건 상한. 작업 식별에는 앞부분이면 충분해 장문 답변을 절단
NOTION_VERSION = "2022-06-28"
NOTION_API = "https://api.notion.com/v1"
WEEKDAY_KO = ["월", "화", "수", "목", "금", "토", "일"]
STATUS_CHOICES = ["시작 전", "진행 중", "완료"]


def log(msg: str) -> None:
    print(f"[worklog] {msg}", flush=True)


# --- 1) 날짜 ----------------------------------------------------------------
def resolve_date(arg: str | None) -> _dt.date:
    if arg:
        return _dt.date.fromisoformat(arg)
    # 시스템 TZ가 이미 KST(+09:00)임을 확인함 -> 로컬 today가 곧 KST today.
    return _dt.date.today()


# --- 2) git 수집 ------------------------------------------------------------
def collect_git(date: _dt.date) -> str:
    since = f"{date.isoformat()} 00:00:00"
    until = f"{date.isoformat()} 23:59:59"
    out = []
    for repo in REPOS:
        if not (repo / ".git").exists():
            continue
        try:
            res = subprocess.run(
                ["git", "-C", str(repo), "log", "--all",
                 f"--since={since}", f"--until={until}",
                 "--pretty=format:%h|%an|%s", "--stat"],
                capture_output=True, text=True, encoding="utf-8",
                errors="replace", timeout=60,
            )
            body = res.stdout.strip()
        except Exception as e:  # noqa: BLE001
            body = f"(git 오류: {e})"
        out.append(f"### 저장소: {repo.name}\n{body if body else '(그날 커밋 없음)'}")
    return "\n\n".join(out)


# --- 3) 세션 로그 수집 -------------------------------------------------------
def _extract_text(content) -> str:
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts = []
        for blk in content:
            if isinstance(blk, dict) and blk.get("type") == "text":
                parts.append(blk.get("text", ""))
        return "\n".join(parts)
    return ""


def _collect_claude_sessions(date: _dt.date) -> list[str]:
    """선택적 호환: 같은 날 Claude를 명시적으로 사용한 경우 함께 수집."""
    if not CLAUDE_TRANSCRIPT_DIR.exists():
        return []
    start = _dt.datetime.combine(date, _dt.time.min).timestamp()
    end = _dt.datetime.combine(date, _dt.time.max).timestamp()
    files = [p for p in CLAUDE_TRANSCRIPT_DIR.glob("*.jsonl")
             if start <= p.stat().st_mtime <= end]
    files.sort(key=lambda p: p.stat().st_mtime)
    # 세션 경계를 보존한다(파일 1개 = 세션 1개). 보통 한 세션이 한 작업 단위라,
    # 에이전트가 작업을 끊을 때의 1차 단서가 된다(같은 작업이 여러 세션이면 병합).
    blocks = []
    for i, f in enumerate(files, 1):
        try:
            lines = f.read_text(encoding="utf-8", errors="replace").splitlines()
        except Exception:  # noqa: BLE001
            continue
        chunks = []
        for ln in lines:
            ln = ln.strip()
            if not ln:
                continue
            try:
                obj = json.loads(ln)
            except json.JSONDecodeError:
                continue
            role = obj.get("type")
            if role not in ("user", "assistant"):
                continue
            msg = obj.get("message") or {}
            text = _extract_text(msg.get("content")).strip()
            if not text:
                continue
            if text.startswith("[SYSTEM NOTIFICATION") or text.startswith("<system-reminder>"):
                continue
            if len(text) > MSG_CHAR_CAP:
                text = text[:MSG_CHAR_CAP] + " ...(중략)"
            tag = "나" if role == "user" else "Claude"
            chunks.append(f"{tag}: {text}")
        if not chunks:
            continue
        header = f"===== Claude 세션 {i} (id {f.stem[:8]}, 메시지 {len(chunks)}개) ====="
        blocks.append(header + "\n" + "\n\n".join(chunks))
    return blocks


def _collect_codex_sessions(date: _dt.date) -> list[str]:
    day_dir = CODEX_SESSION_DIR / f"{date.year:04d}" / f"{date.month:02d}" / f"{date.day:02d}"
    if not day_dir.exists():
        return []
    blocks = []
    for i, path in enumerate(sorted(day_dir.glob("*.jsonl")), 1):
        chunks = []
        correct_workspace = False
        try:
            lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
        except OSError:
            continue
        for line in lines:
            try:
                obj = json.loads(line)
            except json.JSONDecodeError:
                continue
            if obj.get("type") == "session_meta":
                cwd = str((obj.get("payload") or {}).get("cwd") or "")
                correct_workspace = bool(cwd) and Path(cwd).resolve() == HARNESS.resolve()
                continue
            if obj.get("type") != "event_msg":
                continue
            payload = obj.get("payload") or {}
            kind = payload.get("type")
            if kind not in ("user_message", "agent_message"):
                continue
            text = str(payload.get("message") or "").strip()
            if not text or text.startswith("[SYSTEM"):
                continue
            if len(text) > MSG_CHAR_CAP:
                text = text[:MSG_CHAR_CAP] + " ...(중략)"
            chunks.append(f"{'나' if kind == 'user_message' else 'Codex'}: {text}")
        if correct_workspace and chunks:
            header = (
                f"===== Codex 세션 {i} "
                f"(id {path.stem[-8:]}, 메시지 {len(chunks)}개) ====="
            )
            blocks.append(header + "\n" + "\n\n".join(chunks))
    return blocks


def collect_sessions(date: _dt.date) -> str:
    blocks = _collect_codex_sessions(date)
    blocks.extend(_collect_claude_sessions(date))
    joined = "\n\n\n".join(blocks)
    if len(joined) > SESSION_CHAR_CAP:
        joined = "...(앞부분 생략)...\n\n" + joined[-SESSION_CHAR_CAP:]
    return joined if joined else "(그날 세션 로그 없음)"


# --- 3b) 작업 원장(ledger) + HANDOFF -----------------------------------------
def load_ledger() -> dict:
    """작업 정체성 원장 로드. tasks=[{id,title,page_id,status,summary,started,
    last_updated,days[]}], next_seq."""
    if TASK_LEDGER.exists():
        try:
            d = json.loads(TASK_LEDGER.read_text(encoding="utf-8"))
            d.setdefault("tasks", [])
            d.setdefault("next_seq", len(d["tasks"]) + 1)
            return d
        except Exception:  # noqa: BLE001
            log("원장 파싱 실패 -> 새 원장으로 시작")
    return {"tasks": [], "next_seq": 1}


def save_ledger(led: dict) -> None:
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    TASK_LEDGER.write_text(json.dumps(led, ensure_ascii=False, indent=2),
                           encoding="utf-8")


def open_tasks(led: dict) -> list:
    """아직 완료되지 않은(이어지는) 작업들."""
    return [t for t in led.get("tasks", []) if t.get("status") != "완료"]


def format_open_tasks(led: dict) -> str:
    rows = []
    for t in open_tasks(led):
        started = t.get("started", "?")
        summ = (t.get("summary") or "").replace("\n", " ")[:160]
        rows.append(f"- [id={t['id']}] {t.get('title','(제목없음)')} "
                    f"(시작 {started}) — {summ}")
    return "\n".join(rows) if rows else "(없음)"


def record_pending(date: _dt.date) -> None:
    """NOTION_TOKEN 없는 환경에서 생성한 일지를 이관 대기 목록에 기록(날짜당 1줄, 멱등).
    업무용 PC 복귀 후 `--from-json logs/worklog_<날짜>.json` 으로 전송하고 [x] 처리한다."""
    iso = date.isoformat()
    line = f"- [ ] {iso} — `logs/worklog_{iso}.json`"
    if PENDING_PATH.exists():
        txt = PENDING_PATH.read_text(encoding="utf-8")
        if f"- [ ] {iso}" in txt or f"- [x] {iso}" in txt:
            return
        if not txt.endswith("\n"):
            txt += "\n"
        PENDING_PATH.write_text(txt + line + "\n", encoding="utf-8")
    else:
        PENDING_PATH.write_text(
            "# 노션 이관 대기 목록\n\n"
            "노션 미접속 환경에서 생성된 작업일지. 업무용 PC 복귀 후 각 항목을\n"
            "`python scripts/daily_worklog.py --from-json logs/worklog_<날짜>.json` 으로 전송하고 [x] 처리.\n\n"
            + line + "\n", encoding="utf-8")
    log(f"이관 대기 기록: {PENDING_PATH.name} <- {iso}")


def mark_pending_done(date: _dt.date) -> None:
    """--from-json 백필 성공 시 이관 대기 목록의 해당 날짜를 [x] 로 체크."""
    if not PENDING_PATH.exists():
        return
    iso = date.isoformat()
    txt = PENDING_PATH.read_text(encoding="utf-8")
    new = txt.replace(f"- [ ] {iso}", f"- [x] {iso}")
    if new != txt:
        PENDING_PATH.write_text(new, encoding="utf-8")
        log(f"이관 대기 체크 완료: {iso}")


def collect_handoff() -> str:
    try:
        txt = HANDOFF_PATH.read_text(encoding="utf-8", errors="replace")
    except Exception:  # noqa: BLE001
        return "(HANDOFF.md 없음)"
    # 최신 인수인계가 위쪽에 쌓이므로 앞부분 위주로 상한 적용.
    return txt[:HANDOFF_CHAR_CAP]


# --- 4) Codex 구조화 요약 ---------------------------------------------------
# detail 서술 템플릿 목록은 scripts/worklog_templates.md 참조(기본: STAR/PPP 혼합형).
PROMPT_TMPL = """\
아래는 {date} ({wd}요일)에 내가 한 개발 작업의 원자료다.
(1) git 커밋 로그/변경 통계, (2) Codex 중심 대화 세션 로그.
이걸 그날 한 '작업 단위'로 끊어서 아래 JSON 스키마로 정확히 채워 출력하라.

{{
  "summary": "그날 전체를 한 문장으로(80자 내외)",
  "tasks": [
    {{
      "task_ref": "이 작업이 아래 '열린 작업(진행 중)' 목록 중 하나를 이어서 한 것이면 그 작업의 id를 글자 그대로(예: 't-0003'), 새로 시작한 작업이면 'new'. 판단은 제목 글자가 아니라 '무슨 일을 하던 작업인가'라는 맥락과 HANDOFF 히스토리로 한다.",
      "title": "이 작업을 5~16자로 압축한 제목(명사구)",
      "summary": "이 작업을 한 문장으로(60자 내외) - Notion 설명칸/상단 콜아웃에 들어감",
      "detail": "이 작업의 구체적 내용을 '소제목 — 본문' 형태의 문단 2~4개로 나눠 서술하고, 문단 사이는 빈 줄(\\n\\n)로 구분한다. 각 문단은 짧은 소제목(2~12자)으로 시작하고 ' — '(공백+긴대시+공백)로 본문을 잇는다(예: '배경·목적 — ...', '진행 — ...', '결과·임팩트 — ...'). 흐름은 (1)배경·목적: 왜 했나 (2)진행: 어느 파일에 무엇을 어떻게 (3)결과·임팩트: 결과·수치·확인내용과 '이 작업이 왜 중요했는지/무엇이 좋아졌는지'. 작업 성격에 맞으면 소제목은 바꿔도 됨(예: 원인/수정/검증). summary를 반복하지 말고 한 단계 더 깊게, 본문 한 문단은 1~3문장.",
      "status": "완료 또는 진행 중 (그날 이 작업이 끝났으면 '완료', 이어서 할 게 남았으면 '진행 중')",
      "tech": ["이 작업에서 다룬 도구/기술. 'Spring Boot — bootRun' 처럼 '이름 — 용도' 형식."],
      "learnings": [{{"title": "이 작업에서 배운 점 5~12자", "detail": "부연 1~2문장(100자 내외)"}}],
      "issues": [{{"problem": "이 작업에서 부딪힌 문제", "solution": "어떻게 해결했는지"}}],
      "next": ["이 작업에 이어서 할 일. 없으면 빈 배열."],
      "tags": ["이 작업 분류 키워드 2~4개. 예: 'Spring Boot','자동화'"]
    }}
  ]
}}

규칙:
- 위 JSON 객체 하나만 출력. 코드펜스(```)·머리말·설명·메타문장 금지.
- '[검토 불요...]', 검토 배너 같은 메타 문장 절대 금지. 너는 업무 보고서를 쓰는 것이다.
- 문체는 보고서체로 쓴다: 객관적·간결·건조하게, 사실과 결과 위주. 1인칭 감상·자기평가('재밌었다','뿌듯','보람'), 구어체('~했어요','~같다','~인 듯','~네요'), 군더더기 수식어를 쓰지 마라. 종결은 개조식 또는 평서형('~함/~했음/~음' 또는 '~한다/~했다')으로 통일한다. (초등학생 일기 같은 어투 금지 — 동료에게 제출하는 업무 보고서 수준)
- 업무와 무관한 개인 상담, 개인용 문서 작성·이동·정리 같은 내용은 summary와 tasks를 포함한 모든 출력 필드에서 제외하라. 한 세션에 업무와 개인 내용이 섞였으면 업무 내용만 사용하고, 제외했다는 사실도 출력하지 마라.
- 작업 단위로 끊기 + 병합(중요): 세션 자료는 '===== 세션 N ====='으로 구분돼 있고, 보통 한 세션이 한 작업 단위다 → 작업을 나눌 때의 1차 단서로 삼아라. 다만 노션에 쓰기 전에 그날 한 일을 먼저 리스트업한 뒤, 같은 작업을 여러 세션에서(예: 다른 조건으로) 시도했거나 여러 커밋에 흩어진 경우 그것들을 **하나의 task 로 병합**하라 — 세션마다 따로 task 를 만들지 마라. 세션 경계는 단서일 뿐 절대 규칙이 아니다(같은 목표·같은 대상이면 한 작업). 결과는 의미 있는 작업 단위 tasks(보통 4~7개), 너무 잘게 쪼개지 말 것.
- 작업을 나눈 만큼 각 작업의 detail 은 충실하게 써라(위 '소제목 — 본문' 라벨형 문단 2~4개). summary는 한 줄 압축, detail은 그 작업만의 구체적 서술 — 둘을 분명히 다르게. detail에 '벽 같은 한 덩어리 문장' 금지(반드시 문단을 라벨로 나눌 것).
- 기술/배운점/이슈/다음할일은 각각 가장 관련된 작업 밑에 배치하라. 어디에도 안 묶이면 가장 가까운 작업에 넣어라.
- status 는 반드시 '완료' 또는 '진행 중' 둘 중 하나.
- 이어지는 작업 판정(중요): 아래 '열린 작업(진행 중)' 목록은 이전 날부터 끝나지 않고 이어지는 작업들이다(각 작업의 id·제목·시작일·누적 맥락 포함). 오늘 한 일이 그 중 한 작업의 연속이면 해당 task_ref 에 그 id 를 넣고, status 는 오늘로 끝났으면 '완료', 아직 남았으면 '진행 중'으로 둔다. 새로 시작한 일만 task_ref='new'. 판정 근거는 제목 글자 일치가 아니라 '같은 목표·같은 대상·같은 흐름의 작업인가'라는 맥락과 아래 HANDOFF 히스토리다. 애매하면 HANDOFF의 '진행중·미완/다음 단계'에 그 작업이 살아있는지로 판단한다. 목록이 '(없음)'이면 전부 new.
- title은 명사구로 짧게(날짜를 넣지 마라). 이어지는 작업(task_ref!='new')의 title 은 열린 작업의 기존 제목을 그대로 쓰는 것을 우선한다(맥락이 더 정확해지면 다듬어도 됨 — 식별은 id로 하므로 제목이 바뀌어도 안전). 원자료에 근거 없는 내용·과장 금지(특히 detail의 수치·결과는 자료에 있는 것만). 모든 값 한국어. 빈 섹션은 빈 배열로.

=== 열린 작업(진행 중) 목록 — 이어짐 판정 기준 ===
{open_tasks}

=== HANDOFF 히스토리(작업 시작~현재 인수인계) ===
{handoff}

=== git 자료 ===
{git}

=== 세션 자료 ===
{sessions}
"""


def find_codex() -> str | None:
    return shutil.which("codex") or shutil.which("codex.exe")


def run_codex(prompt: str, model: str | None = None) -> str:
    exe = find_codex()
    if not exe:
        raise RuntimeError("codex CLI를 찾을 수 없음 (PATH 확인)")
    # 프로젝트 규칙과 쓰기 권한이 필요 없는 독립 요약 작업으로 실행한다.
    workdir = tempfile.mkdtemp(prefix="worklog_codex_")
    output_file = Path(workdir) / "last-message.txt"
    cmd = [
        exe, "exec",
        "--skip-git-repo-check",
        "--sandbox", "read-only",
        "--ephemeral",
        "--output-last-message", str(output_file),
    ]
    if model:
        cmd.extend(["--model", model])
    cmd.append("-")
    res = subprocess.run(
        cmd, input=prompt, cwd=workdir,
        capture_output=True, text=True, encoding="utf-8",
        errors="replace", timeout=600,
    )
    if res.returncode != 0:
        raise RuntimeError(f"codex 실행 실패(rc={res.returncode}): {res.stderr[:500]}")
    if not output_file.exists():
        raise RuntimeError("codex 최종 메시지 파일이 생성되지 않음")
    return output_file.read_text(encoding="utf-8").strip()


def parse_json_lenient(text: str) -> dict:
    """Codex 출력에서 JSON 객체 추출(코드펜스/잡텍스트 허용)."""
    t = text.strip()
    if t.startswith("```"):
        t = re.sub(r"^```[a-zA-Z]*\n?", "", t)
        t = re.sub(r"\n?```$", "", t).strip()
    try:
        return json.loads(t)
    except json.JSONDecodeError:
        pass
    # 본문 중 첫 { ~ 마지막 } 추출
    s, e = t.find("{"), t.rfind("}")
    if s >= 0 and e > s:
        return json.loads(t[s:e + 1])
    raise ValueError("Codex 출력에서 JSON을 찾지 못함")


def _normalize_task(t: dict) -> dict:
    for k in ("tech", "learnings", "issues", "next", "tags"):
        t.setdefault(k, [])
    t.setdefault("title", "작업")
    t.setdefault("summary", t.get("detail", ""))
    ref = str(t.get("task_ref") or "new").strip()
    t["task_ref"] = ref if ref else "new"
    if t.get("status") not in STATUS_CHOICES:
        t["status"] = "진행 중"
    return t


def build_data(date: _dt.date, git_text: str, sessions: str, use_ai: bool,
               open_tasks_text: str = "(없음)", handoff_text: str = "",
               model: str | None = None) -> dict:
    wd = WEEKDAY_KO[date.weekday()]
    if not use_ai:
        return {
            "summary": f"{date.isoformat()} 작업(요약 생략)",
            "tasks": [{
                "task_ref": "new",
                "title": "작업(요약 생략)",
                "summary": f"{date.isoformat()} 작업(요약 생략)",
                "status": "진행 중",
                "tech": [], "learnings": [], "issues": [], "next": [], "tags": [],
                "_raw": {"git": git_text, "sessions": sessions[:4000]},
            }],
        }
    prompt = PROMPT_TMPL.format(date=date.isoformat(), wd=wd,
                               open_tasks=open_tasks_text or "(없음)",
                               handoff=handoff_text or "(HANDOFF.md 없음)",
                               git=git_text, sessions=sessions)
    log(f"Codex 구조화 요약 생성 중... (model={model or 'user-default'})")
    raw = run_codex(prompt, model=model)
    data = parse_json_lenient(raw)
    data.setdefault("summary", f"{date.isoformat()} 작업")
    tasks = data.get("tasks") or []
    # 구 포맷(highlights 기반) 출력 호환: 한 일 항목을 작업으로 래핑
    if not tasks and data.get("highlights"):
        tasks = [{"title": h.get("title", ""), "summary": h.get("detail", "")}
                 for h in data["highlights"] if isinstance(h, dict)]
    data["tasks"] = [_normalize_task(t) for t in tasks if isinstance(t, dict)]
    return data


# --- 5) Notion 공통 ---------------------------------------------------------
def _headers(token: str) -> dict:
    return {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "Notion-Version": NOTION_VERSION,
    }


def to_app_url(url: str) -> str:
    """노션 https URL -> 데스크톱 앱 스킴(notion://). 앱에서 열리게(하네스 규칙)."""
    if isinstance(url, str) and url.startswith("https://"):
        return "notion://" + url[len("https://"):]
    return url


def normalize_page_id(raw: str) -> str:
    m = re.findall(r"[0-9a-fA-F]{32}", raw.replace("-", ""))
    if not m:
        return raw.strip()
    h = m[-1].lower()
    return f"{h[0:8]}-{h[8:12]}-{h[12:16]}-{h[16:20]}-{h[20:32]}"


def _rich(text: str):
    return [{"type": "text", "text": {"content": (text or "")[:2000]}}]


def _para(text: str):
    return {"object": "block", "type": "paragraph",
            "paragraph": {"rich_text": _rich(text)}}


def _h2(text: str):
    return {"object": "block", "type": "heading_2",
            "heading_2": {"rich_text": _rich(text)}}


def _bullet(text: str):
    return {"object": "block", "type": "bulleted_list_item",
            "bulleted_list_item": {"rich_text": _rich(text)}}


def _label_rich(title: str, detail: str):
    """제목 줄(굵게+파란색) + 줄바꿈 + 설명 줄 (스캔하기 좋게)."""
    rt = [{"type": "text", "text": {"content": (title or "")[:200]},
           "annotations": {"bold": True, "color": "blue"}}]
    if detail:
        rt.append({"type": "text", "text": {"content": "\n" + detail[:1800]}})
    return rt


def _labeled_bullet(item):
    """item 이 {title,detail} 면 라벨형, 문자열이면 일반 불릿."""
    if isinstance(item, dict):
        rt = _label_rich(item.get("title", ""), item.get("detail", ""))
    else:
        rt = _rich(str(item))
    return {"object": "block", "type": "bulleted_list_item",
            "bulleted_list_item": {"rich_text": rt}}


def _todo(text: str):
    return {"object": "block", "type": "to_do",
            "to_do": {"rich_text": _rich(text), "checked": False}}


def _divider():
    return {"object": "block", "type": "divider", "divider": {}}


def _callout(text: str, emoji: str = "📌", color: str = "blue_background"):
    return {"object": "block", "type": "callout",
            "callout": {"rich_text": _rich(text), "icon": {"emoji": emoji},
                        "color": color}}


def _toggle(title: str, children: list):
    return {"object": "block", "type": "toggle",
            "toggle": {"rich_text": _rich(title), "children": children}}


def _tech_table(tech: list):
    """tech 리스트('이름 — 용도') -> 2열 표."""
    rows = []
    for item in tech:
        parts = re.split(r"\s[—–-]\s", item, maxsplit=1)
        name = parts[0].strip()
        usage = parts[1].strip() if len(parts) > 1 else ""
        rows.append({
            "object": "block", "type": "table_row",
            "table_row": {"cells": [_rich(name), _rich(usage)]},
        })
    header = {
        "object": "block", "type": "table_row",
        "table_row": {"cells": [_rich("도구/기술"), _rich("용도")]},
    }
    return {
        "object": "block", "type": "table",
        "table": {"table_width": 2, "has_column_header": True,
                  "has_row_header": False, "children": [header] + rows},
    }


def _detail_block(para: str):
    """detail 문단을 '소제목 — 본문' 으로 분리해 라벨(굵은 파란색)+본문 줄로 렌더.
    구분자(' - '/em·en dash)가 없거나 라벨이 길면 일반 문단으로 폴백."""
    m = re.match(r"^(.{1,24}?)\s+[—–-]\s+(.+)$", para, re.S)
    if m:
        label, body = m.group(1).strip(), m.group(2).strip()
        return {"object": "block", "type": "paragraph",
                "paragraph": {"rich_text": _label_rich(label, body)}}
    return _para(para)


def build_task_blocks(task: dict) -> list:
    """작업 1건 -> 풍부한 Notion 블록(트래커 행 본문)."""
    summary = task.get("summary", "") or task.get("detail", "")
    blocks = [_callout(summary, "📌", "blue_background")]

    detail = (task.get("detail") or "").strip()
    if detail and detail != task.get("summary", ""):
        blocks.append(_h2("📝 작업 내용"))
        for para in detail.split("\n\n"):
            para = para.strip()
            if para:
                blocks.append(_detail_block(para))

    if task.get("tech"):
        blocks.append(_h2("🛠️ 기술 / 도구"))
        blocks.append(_tech_table(task["tech"]))

    if task.get("learnings"):
        blocks.append(_h2("💡 배운 점"))
        blocks += [_labeled_bullet(x) for x in task["learnings"]]

    issues = [i for i in task.get("issues", []) if isinstance(i, dict) and i.get("problem")]
    if issues:
        blocks.append(_h2("🐛 이슈 · 해결"))
        for it in issues:
            blocks.append(_toggle(it.get("problem", ""),
                                  [_para("해결: " + it.get("solution", ""))]))

    if task.get("next"):
        blocks.append(_h2("📋 다음 할 일"))
        blocks += [_todo(x) for x in task["next"]]

    if task.get("_raw"):  # --no-ai 일 때 원자료
        blocks.append(_divider())
        blocks.append(_toggle("원자료(git/세션)", [
            _para("git:\n" + task["_raw"]["git"][:1800]),
            _para("sessions:\n" + task["_raw"]["sessions"][:1800]),
        ]))
    return blocks


def build_blocks(data: dict) -> list:
    """그날 전체 -> 한 페이지 블록(page/db 방식용). 작업별 섹션으로 렌더."""
    blocks = [_callout(data.get("summary", ""), "📌", "blue_background"), _divider()]
    for t in data.get("tasks", []):
        blocks.append(_h2("✅ " + t.get("title", "작업")))
        blocks += build_task_blocks(t)
        blocks.append(_divider())
    return blocks


def _post(url: str, token: str, payload: dict):
    import requests
    r = requests.post(url, headers=_headers(token), data=json.dumps(payload), timeout=30)
    if r.status_code >= 300:
        raise RuntimeError(f"Notion {url} 실패 {r.status_code}: {r.text[:600]}")
    return r.json()


def _patch_children(page_id: str, token: str, children: list):
    import requests
    r = requests.patch(f"{NOTION_API}/blocks/{page_id}/children",
                       headers=_headers(token),
                       data=json.dumps({"children": children}), timeout=30)
    if r.status_code >= 300:
        raise RuntimeError(f"Notion 블록 추가 실패 {r.status_code}: {r.text[:400]}")


def _append_blocks(page_id: str, token: str, blocks: list):
    """생성 직후 100개 초과분 분할 append(첫 100개는 create가 이미 보냄)."""
    rest = blocks[100:]
    while rest:
        batch, rest = rest[:100], rest[100:]
        _patch_children(page_id, token, batch)


def _append_all(page_id: str, token: str, blocks: list):
    """기존 페이지에 블록 전체를 100개씩 분할 append(이어지는 작업 진행분 추가용)."""
    rest = list(blocks)
    while rest:
        batch, rest = rest[:100], rest[100:]
        _patch_children(page_id, token, batch)


# --- 5a) 방식 page ----------------------------------------------------------
def create_as_page(token: str, parent_id: str, title: str, blocks: list) -> str:
    page = _post(f"{NOTION_API}/pages", token, {
        "parent": {"page_id": parent_id},
        "properties": {"title": {"title": _rich(title)}},
        "children": blocks[:100],
    })
    _append_blocks(page["id"], token, blocks)
    return page.get("url", page["id"])


# --- 5b) 방식 db ------------------------------------------------------------
def create_database(token: str, parent_id: str, title: str) -> str:
    db = _post(f"{NOTION_API}/databases", token, {
        "parent": {"type": "page_id", "page_id": parent_id},
        "title": _rich(title),
        "properties": {
            "이름": {"title": {}},
            "날짜": {"date": {}},
            "요일": {"select": {"options": [{"name": w} for w in WEEKDAY_KO]}},
            "한줄요약": {"rich_text": {}},
            "기술스택": {"multi_select": {}},
        },
    })
    return db["id"]


def add_db_item(token: str, db_id: str, date: _dt.date, title: str,
                data: dict, blocks: list) -> str:
    wd = WEEKDAY_KO[date.weekday()]
    tags = [str(t)[:90].replace(",", " ") for t in (data.get("tags") or [])][:8]
    props = {
        "이름": {"title": _rich(title)},
        "날짜": {"date": {"start": date.isoformat()}},
        "요일": {"select": {"name": wd}},
        "한줄요약": {"rich_text": _rich(data.get("summary", ""))},
        "기술스택": {"multi_select": [{"name": t} for t in tags if t]},
    }
    page = _post(f"{NOTION_API}/pages", token, {
        "parent": {"database_id": db_id},
        "properties": props,
        "children": blocks[:100],
    })
    _append_blocks(page["id"], token, blocks)
    return page.get("url", page["id"])


# --- 5c) 방식 tracker (기존 '작업 트래커' DB에 행 추가) ----------------------
# 트래커 DB 규격(노션 기본 태스크 트래커):
#   작업 이름(title) / 상태(status) / 설명(rich_text) / 마감일(date) /
#   작업 유형(multi_select) / 우선순위·노력 수준(select) / 기한 경과(formula)
# 주의: 기한 경과 = if(마감일 < now(), "Past Due", "") 라 상태와 무관하게
#       과거 마감일이면 Past Due 가 뜸 -> 작업일지 행은 '마감일'을 비운다.
def page_exists(token: str, page_id: str) -> bool:
    """원장의 page_id 가 노션에 아직 살아있는지(수동 삭제 대비)."""
    import requests
    try:
        r = requests.get(f"{NOTION_API}/pages/{page_id}",
                         headers=_headers(token), timeout=30)
        if r.status_code >= 300:
            return False
        return not r.json().get("archived", False)
    except Exception:  # noqa: BLE001
        return False


def _date_prop(start: str | None, end: str | None):
    """'작업 기간' date 속성. start==end 면 단일 날짜, 다르면 범위."""
    if not start:
        return None
    val = {"start": start}
    if end and end != start:
        val["end"] = end
    return {"date": val}


def _tags_prop(tags):
    """'태그' multi_select. 콤마 불가·중복 제거·최대 10개."""
    clean, seen = [], set()
    for t in tags or []:
        s = str(t)[:90].replace(",", " ").strip()
        if s and s not in seen:
            seen.add(s)
            clean.append(s)
    return {"multi_select": [{"name": s} for s in clean[:10]]}


def update_tracker_row(token: str, page_id: str, status: str,
                       title: str | None = None, summary: str | None = None,
                       period_start: str | None = None,
                       period_end: str | None = None, tags=None) -> None:
    """기존 트래커 행의 상태(+선택적으로 제목·설명·작업 기간·태그)를 갱신.
    이어지는 작업이 끝났으면 status='완료'. 식별은 page_id 라 제목 변경도 안전."""
    import requests
    props = {"상태": {"status": {"name": status}}}
    if title:
        props["작업 이름"] = {"title": _rich(title)}
    if summary:
        props["설명"] = {"rich_text": _rich(summary)}
    dp = _date_prop(period_start, period_end)
    if dp:
        props["작업 기간"] = dp
    if tags is not None:
        props["태그"] = _tags_prop(tags)
    r = requests.patch(
        f"{NOTION_API}/pages/{page_id}", headers=_headers(token),
        data=json.dumps({"properties": props}), timeout=30)
    if r.status_code >= 300:
        raise RuntimeError(f"Notion 행 갱신 실패 {r.status_code}: {r.text[:300]}")


def create_tracker_item(token: str, db_id: str, title: str,
                        summary: str, status: str, blocks: list,
                        period_start: str | None = None,
                        period_end: str | None = None, tags=None):
    """트래커 행 생성. (url, page_id) 반환 — page_id 를 원장에 저장한다."""
    props = {
        "작업 이름": {"title": _rich(title)},
        "상태": {"status": {"name": status}},
        "설명": {"rich_text": _rich(summary)},
    }
    dp = _date_prop(period_start, period_end)
    if dp:
        props["작업 기간"] = dp
    if tags is not None:
        props["태그"] = _tags_prop(tags)
    page = _post(f"{NOTION_API}/pages", token, {
        "parent": {"database_id": db_id},
        "properties": props,
        "children": blocks[:100],
    })
    _append_blocks(page["id"], token, blocks)
    return page.get("url", page["id"]), page["id"]


# --- main -------------------------------------------------------------------
def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--date")
    ap.add_argument("--style", choices=["tracker", "page", "db", "both"],
                    default="tracker")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--no-ai", action="store_true",
                    help="Codex 요약을 생략하고 원자료 기반 최소 JSON 생성")
    ap.add_argument("--no-claude", action="store_true", help=argparse.SUPPRESS)
    ap.add_argument("--model", default=None,
                    help="Codex 요약 모델(기본: 사용자 Codex 설정)")
    ap.add_argument("--title-suffix", default="")
    ap.add_argument("--status", choices=STATUS_CHOICES, default=None)
    ap.add_argument("--from-json", dest="from_json", default=None,
                    help="이미 생성된 logs/worklog_<날짜>.json 을 읽어 수집·요약 없이 "
                         "Notion 전송(노션 미접속 기간 백필용). 날짜는 파일명에서 유도.")
    args = ap.parse_args()

    if args.from_json and not args.date:
        m = re.search(r"(\d{4}-\d{2}-\d{2})", Path(args.from_json).name)
        if not m:
            log("--from-json 파일명에 날짜가 없음 -> --date 로 지정 필요")
            return 1
        args.date = m.group(1)

    date = resolve_date(args.date)
    wd = WEEKDAY_KO[date.weekday()]
    log(f"대상 날짜: {date.isoformat()} ({wd}), style={args.style}")

    if args.from_json:
        git_text = sessions = "(from-json: 수집 생략)"
    else:
        git_text = collect_git(date)
        log(f"git 자료 {len(git_text)}자")
        sessions = collect_sessions(date)
        log(f"세션 자료 {len(sessions)}자")

    token = os.environ.get("NOTION_TOKEN")
    parent = os.environ.get("NOTION_PARENT_PAGE_ID")
    tracker = os.environ.get("NOTION_TRACKER_DB_ID")

    # 작업 원장 로드: 열린 작업 목록과 HANDOFF 히스토리를 Codex에 줘서
    # '오늘 한 일이 어느 작업의 연속인가'를 제목이 아니라 맥락으로 판정하게 한다.
    led = load_ledger()
    open_list = open_tasks(led)
    open_tasks_text = format_open_tasks(led)
    handoff_text = collect_handoff()
    if open_list:
        log(f"열린 작업(진행 중) {len(open_list)}건 — 이어짐 판정 기준으로 전달")

    if args.from_json:
        src = Path(args.from_json)
        data = json.loads(src.read_text(encoding="utf-8"))
        data.setdefault("summary", f"{date.isoformat()} 작업")
        data["tasks"] = [_normalize_task(t) for t in (data.get("tasks") or [])
                         if isinstance(t, dict)]
        log(f"from-json 로드: {src} (수집·요약 생략)")
    else:
        data = build_data(date, git_text, sessions,
                          use_ai=not (args.no_ai or args.no_claude),
                          open_tasks_text=open_tasks_text, handoff_text=handoff_text,
                          model=args.model)
    tasks = data.get("tasks", [])
    log(f"작업(tasks) {len(tasks)}건")

    suffix = (" " + args.title_suffix) if args.title_suffix else ""
    title = f"작업일지 {date.isoformat()} ({wd}){suffix}"
    blocks = build_blocks(data)

    # 산출물 백업 저장 (from-json 은 원본이 이미 logs/ 에 있으므로 재저장 생략)
    if not args.from_json:
        LOG_DIR.mkdir(parents=True, exist_ok=True)
        (LOG_DIR / f"worklog_{date.isoformat()}.json").write_text(
            json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
        log(f"JSON 저장: {LOG_DIR / ('worklog_' + date.isoformat() + '.json')}")

    if args.dry_run or not token:
        why = "dry-run" if args.dry_run else "NOTION_TOKEN 미설정"
        log(f"Notion 전송 생략 ({why}). 블록 {len(blocks)}개 준비됨.")
        # 노션 미접속 환경(토큰 없음)이면 이관 대기 목록에 기록해 뒀다가 복귀 후 백필.
        if not token and not args.dry_run:
            record_pending(date)
        return 0

    # --- 방식 tracker: 기존 '작업 트래커' DB에 작업별 행 추가(기본) ---
    if args.style == "tracker":
        if not tracker:
            log("NOTION_TRACKER_DB_ID 미설정 -> tracker 전송 생략")
            return 0
        if not tasks:
            log("[tracker] 작업(tasks) 없음 -> 생성할 행 없음")
            return 0
        db_id = normalize_page_id(tracker)
        by_id = {t["id"]: t for t in led["tasks"]}
        created = appended = skipped = 0
        for t in tasks:
            row_title = f"{t.get('title', '작업')}{suffix}"  # 제목에 날짜 없음
            # 상태: 수동 지정(--status)이 최우선, 없으면 작업별 판정값(완료/진행 중)
            row_status = args.status or t.get("status", "진행 중")
            ref = t.get("task_ref", "new")
            entry = by_id.get(ref) if ref != "new" else None
            # 이어지는 작업: 원장에 page_id 가 있고 노션에 살아있으면 그 행에 이어쓴다.
            if entry and entry.get("page_id") and page_exists(token, entry["page_id"]):
                if date.isoformat() in entry.get("days", []):
                    log(f"[tracker] {date.isoformat()} 진행분 이미 반영됨 -> 스킵: {entry.get('title')}")
                    skipped += 1
                    continue
                day_blocks = ([_divider(),
                               _h2(f"📅 {date.isoformat()} ({wd}) 진행분")]
                              + build_task_blocks(t))
                _append_all(entry["page_id"], token, day_blocks)
                # 태그 누적(중복 제거), 작업 기간 = 시작~오늘
                merged_tags = list(dict.fromkeys(
                    (entry.get("tags") or []) + (t.get("tags") or [])))
                update_tracker_row(token, entry["page_id"], row_status,
                                   title=row_title, summary=t.get("summary", ""),
                                   period_start=entry.get("started"),
                                   period_end=date.isoformat(), tags=merged_tags)
                entry["title"] = t.get("title", entry.get("title"))
                entry["summary"] = t.get("summary", entry.get("summary", ""))
                entry["status"] = row_status
                entry["tags"] = merged_tags
                entry["last_updated"] = date.isoformat()
                entry.setdefault("days", []).append(date.isoformat())
                log(f"[tracker] 진행분 추가({entry['id']}, 상태={row_status}): {row_title}")
                appended += 1
                continue
            # 새 작업: 같은 날 재실행 멱등 — 오늘 시작한 동일 제목 작업이 이미
            # 원장에 있으면 중복 생성 방지(날짜내 백스톱, 정체성은 id 기반 유지).
            dup = next((e for e in led["tasks"]
                        if e.get("started") == date.isoformat()
                        and e.get("title") == t.get("title", "작업")), None)
            if dup:
                log(f"[tracker] 오늘 생성한 동일 작업({dup['id']}) 존재 -> 스킵: {row_title}")
                skipped += 1
                continue
            # 행 생성 후 원장에 id<->page_id 등록.
            if ref != "new":
                log(f"[tracker] task_ref={ref} 원장에 없거나 행 소실 -> 새 작업으로 생성")
            new_tags = list(dict.fromkeys(t.get("tags") or []))
            url, page_id = create_tracker_item(token, db_id, row_title,
                                               t.get("summary", ""), row_status,
                                               build_task_blocks(t),
                                               period_start=date.isoformat(),
                                               period_end=date.isoformat(),
                                               tags=new_tags)
            new_id = f"t-{led['next_seq']:04d}"
            led["next_seq"] += 1
            led["tasks"].append({
                "id": new_id,
                "title": t.get("title", "작업"),
                "page_id": page_id,
                "status": row_status,
                "summary": t.get("summary", ""),
                "tags": new_tags,
                "started": date.isoformat(),
                "last_updated": date.isoformat(),
                "days": [date.isoformat()],
            })
            by_id[new_id] = led["tasks"][-1]
            log(f"[tracker] 행 생성({new_id}, 상태={row_status}): {row_title} -> {to_app_url(url)}")
            created += 1
        save_ledger(led)
        log(f"[tracker] 완료: 생성 {created} / 진행분추가 {appended} / 스킵 {skipped} "
            f"(원장 {TASK_LEDGER})")
        if args.from_json:
            mark_pending_done(date)
        return 0

    # --- 방식 page/db/both: 부모 페이지 하위 ---
    if not parent:
        log("NOTION_PARENT_PAGE_ID 미설정 -> page/db 전송 생략")
        return 0
    parent_id = normalize_page_id(parent)

    if args.style in ("page", "both"):
        url = create_as_page(token, parent_id, title, blocks)
        log(f"[page] 생성 완료: {to_app_url(url)}")

    if args.style in ("db", "both"):
        db_id = os.environ.get("NOTION_DATABASE_ID")
        if not db_id:
            db_id = create_database(token, parent_id, "업무일지 DB")
            log(f"[db] 데이터베이스 생성됨. NOTION_DATABASE_ID 로 등록하세요: {db_id}")
        url = add_db_item(token, db_id, date, title, data, blocks)
        log(f"[db] 항목 생성 완료: {to_app_url(url)}")

    if args.from_json:
        mark_pending_done(date)
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as e:  # noqa: BLE001
        log(f"오류: {e}")
        sys.exit(1)
