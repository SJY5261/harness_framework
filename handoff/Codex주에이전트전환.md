# Codex 주 에이전트 전환

_시작: 2026-07-24 / 상태: 주 전환·UserPromptSubmit 호환 수정 완료 / 전체 런타임 재감사 대기_

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

## 2026-07-24 Codex 규칙 최적화

- 상시 로드 규칙을 운영 원칙(`AGENTS.md`)과 제품 불변식(`PROJECT_RULES.md`)으로 다시 압축했다.
- `docs/SECOND_BRAIN.md`에 규칙·활성 상태·결정·증적·Notion 일지의 역할과 승격 수명주기를 정의했다.
- `HANDOFF.md`를 활성 작업·다음 행동 중심의 짧은 인덱스로 정리하고 `PATHS.md`를 상대 경로 중심으로 교정했다.
- 하네스는 모든 docs 자동 주입 대신 phase `context_files`만 읽는다. 저장소 밖 경로와 누락 파일은 실패 처리한다.
- 하네스의 `git add -A`를 제거했다. 기존 staged 변경이 있으면 중단하고, 기존 dirty 경로를 제외한 신규 작업 경로만 명시적으로 스테이징한다.
- 검증: 관련 테스트 `59 passed`, Python 컴파일 및 phase 컨텍스트 경로 검사 통과.

## 2026-07-28 UserPromptSubmit 호환 결함 수정

### 현상

- `AGENTS.md`, `PROJECT_RULES.md`, `HANDOFF.md` 중 하나가 변경된 뒤 다음 프롬프트를 제출하면 `hook returned invalid user prompt submit JSON output` 오류가 발생했다.
- 오류는 비차단이었지만 규칙 변경 알림이 모델 컨텍스트에 전달되지 않았고, 상태 파일은 이미 갱신돼 같은 변경에 대한 알림도 재시도되지 않았다.

### 원인

- `.codex/hooks/context_freshness_gate.py`가 `[규칙 신선도 알림] ...` 평문을 출력했다.
- Codex 훅 파서는 `{` 또는 `[`로 시작하는 stdout을 JSON 후보로 판정한다. 해당 평문은 `[`로 시작하지만 유효한 JSON 배열이 아니어서 파싱에 실패했다.
- Claude 자동 의존성 문제가 아니라 Claude 시절의 평문 알림 형식을 Codex 훅으로 옮기면서 출력 계약의 상태 전이 경로를 검증하지 않은 마이그레이션 결함이다.

### 해결

- 알림을 공식 `hookSpecificOutput.hookEventName=UserPromptSubmit` 및 `additionalContext` JSON으로 출력하도록 수정했다.
- 최초 실행 무출력 → 규칙 파일 변경 후 유효 JSON → 같은 상태 재실행 무출력 순서의 회귀 테스트를 `scripts/test_codex_migration.py`에 추가했다.

### 채택 이유

- 알림 앞의 `[`만 제거하는 평문 우회보다 공식 JSON 계약이 파서 휴리스틱 변화에 덜 취약하고, 컨텍스트 주입 목적도 명시적이다.
- 기존 감시 대상과 세션별 해시 저장 방식은 유지해 기능 범위와 실행 비용을 바꾸지 않았다.

### 결과

- 하네스 전체 `60 passed`, Python 컴파일, `git diff --check` 통과.
- 과거 세션 상태를 이용한 실제 스크립트 실행에서 JSON 출력·후속 무출력 확인.
- 커밋 `185d9ae`를 `myfork/feat-code-cache`에 push했다.
- 커밋 이후 실제 사용자 프롬프트에서 오류 대신 `[규칙 신선도 알림]` 개발자 컨텍스트가 정상 주입돼 Codex 수명주기 검증도 통과했다.

### 검증 누락 회고

- 최초 전환 검증은 설정 파싱·일반 실행·첫 실행 무출력에 치우쳤고, 규칙 파일 변경 후에만 열리는 훅 분기를 실행하지 않았다.
- “Claude 자동 의존성 제거”와 “Codex 런타임 출력 계약 완전 호환”을 구분하지 않아 전환 완료 판정을 과도하게 낙관적으로 기록했다.

## 다음 단계

- [ ] `.codex/hooks.json`의 모든 이벤트를 최초·변경·차단·실패 상태로 실행해 출력 계약을 재검증한다.
- [ ] `.codex/`, 실행 스크립트, 자동화에서 Claude 전용 경로·환경 변수·출력 형식·세션 포맷 의존성을 전수 검색하고 실제 호출 경로 기준으로 분류한다.
- [ ] `.claude/` 잔존 파일은 선택적 호환 자산과 잘못 남은 활성 의존성으로 구분하고, 활성 Codex 경로에서 자동 호출되지 않는지 재확인한다.
- [ ] 재감사 결과를 근거로 이 문서의 상태를 다시 완료로 전환한다.

## 블로커·주의

- 기존 `scripts/daily_worklog.py`와 여러 handoff 파일은 작업 시작 전부터 미추적 상태였다. 이번 전환과 직접 관련된 파일만 선별해 커밋한다.
- 과거 문서의 “Claude/answer-reviewer 검증 완료” 표기는 당시 사실 기록이므로 소급 변경하지 않는다.
- 현재 확인된 UserPromptSubmit 결함은 수정됐지만, 같은 방식의 상태 전이 누락이 다른 훅·자동화에 없는지는 아직 전수 검증하지 않았다.

## 관련 파일·경로

- `AGENTS.md`
- `PROJECT_RULES.md`
- `CLAUDE.md`
- `.codex/`
- `scripts/execute.py`
- `scripts/daily_worklog.py`
- `discussion/TEMPLATE.md`
- `handoff/Codex진행안내.md`
