# Codex 주 에이전트 전환

_시작: 2026-07-24 / 상태: 완료_

## 작업 목표

Claude Code 중심의 규칙·자동화·협업 체계를 Codex 중심으로 전환한다. Claude는 정상 작업의 의존성에서 제거하고 사용자가 명시적으로 요청할 때만 선택적 보조 도구로 남긴다.

## 결정

- Codex가 기본 오케스트레이터다.
- `AGENTS.md`가 Codex 운영 정본, `PROJECT_RULES.md`가 제품 중립 프로젝트 규칙 정본이다.
- `CLAUDE.md`와 `.claude/`는 선택적 호환 진입점·자산으로 보존한다.
- 개인 모델·요금제·인증·알림·권한은 저장소 `.codex/config.toml`에 고정하지 않는다.
- `peer_review_pending`은 Claude 부재가 아니라 독립 검토가 실제로 필요한 고위험 판단이 미검토일 때만 사용한다.
- 과거 `discussion/` 원문은 역사 자료로 수정하지 않는다. 새 토론만 Codex 중심 템플릿을 사용한다.

## 완료

- `CLAUDE.md`의 공통 정본 역할을 제거하고 선택적 호환 포인터로 축소.
- 기존 Claude 장문 규칙을 `docs/CLAUDE_LEGACY_RULES.md` 역사 보관본으로 이동.
- `AGENTS.md`, `PROJECT_RULES.md`를 Codex 중심 정본으로 재구성.
- `.codex/config.toml`, `.codex/hooks.json`, 규칙 신선도 알림 훅 추가.
- 파괴 명령 차단 `PreToolUse` 훅은 Windows Codex CLI 실검증에서 차단되지 않아 제거했다. 훅은 강제 보안 경계로 간주하지 않는다.
- `scripts/execute.py`의 기본 에이전트를 `claude -p`에서 `codex exec --sandbox workspace-write`로 전환. 승인 우회 옵션 제거.
- `scripts/daily_worklog.py` 요약을 읽기 전용·ephemeral Codex 실행으로 전환하고 Codex 세션 수집 추가. Claude 세션은 선택적 호환 수집만 유지.
- `discussion/TEMPLATE.md`를 Codex 분석·반론·수렴 구조로 전환.
- 진행 안내 정본을 `handoff/Codex진행안내.md`로 전환.

## 검증

- 관련 테스트 `56 passed`.
- Python 컴파일, hooks JSON, config TOML 파싱 성공.
- 실제 `codex exec --strict-config` 실행으로 저장소 설정·훅 로드와 마지막 메시지 출력 계약 확인.
- 활성 자동화의 `claude -p`, 승인 우회 옵션 제거 확인.

## 다음 단계

- 이후 작업은 Codex 진입점과 진행 안내 규칙을 기본으로 사용한다.

## 블로커·주의

- 기존 `scripts/daily_worklog.py`와 여러 handoff 파일은 작업 시작 전부터 미추적 상태였다. 이번 전환과 직접 관련된 파일만 선별해 커밋한다.
- 과거 문서의 “Claude/answer-reviewer 검증 완료” 표기는 당시 사실 기록이므로 소급 변경하지 않는다.

## 관련 파일·경로

- `AGENTS.md`
- `PROJECT_RULES.md`
- `CLAUDE.md`
- `.codex/`
- `scripts/execute.py`
- `scripts/daily_worklog.py`
- `discussion/TEMPLATE.md`
- `handoff/Codex진행안내.md`
