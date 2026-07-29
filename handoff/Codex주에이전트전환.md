# Codex 주 에이전트 전환

_시작: 2026-07-24 / 상태: Codex 단독 운영 정책·런타임 재감사 완료 / 공개 포크 신규 민감정보 차단 적용_

## 작업 목표

Claude Code 중심의 규칙·자동화·협업 체계를 Codex 중심으로 전환한다. Claude는 정상 작업의 의존성에서 제거하고 사용자가 명시적으로 요청할 때만 선택적 보조 도구로 남긴다.

## 결정

- Codex가 기본 오케스트레이터다.
- 별도 명시가 없으면 Codex 단독으로 수행한다. Claude는 Claude 세션에서 별도 관리하며, 현재 프롬프트가 Claude 사용을 명시한 경우만 예외다.
- `AGENTS.md`가 Codex 운영 정본, `PROJECT_RULES.md`가 제품 중립 프로젝트 규칙 정본이다.
- `CLAUDE.md`와 `.claude/`는 선택적 호환 진입점·자산으로 보존한다.
- 기존 grilling 절차는 폐기하며 Codex로 이식하지 않는다.
- Jira·MCP·첨부 이미지 등 외부 정본을 확보하지 못하면 handoff나 코드로 추정 구현하지 않고 사용자 검토를 요청한다.
- Codex와 Claude가 명시적으로 각각 사용된 경우에도 공통 HANDOFF·로그·경로 기록을 갱신해 작업 이력의 공백을 막는다.
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

## 2026-07-28 사용자 전달 보고서 규칙 확장

- PR 설명·PR리뷰뿐 아니라 사용자가 파일 형태로 요청한 일반 보고서도 `Desktop\PR\[MM.DD 요약]` 작업 폴더에 저장한다.
- 작업 폴더에는 9절 형식의 MD 정본과 그 정본에서 만든 자체완결 HTML 정확히 2개만 둔다.
- 일반 보고서는 PR 전용 브랜치·변경량 메타를 강제하지 않고 `현상 → 원인 → 해결 → 채택 이유 → 결과` 구조와 보고서용 메타를 사용한다.
- Sites 게시는 계속 사용자의 명시적 요청이 있을 때만 수행한다.
- 첫 적용 사례로 UserPromptSubmit 훅 오류 분석 보고서를 `[07.28 UserPromptSubmit 훅 오류 분석]` 폴더에 MD·HTML로 생성한다.

## 2026-07-29 단일 Codex 운영·문서 구조 2단계 정리

### 현상

- 상시 규칙, 조건부 절차, 템플릿, 과거 이력이 일부 MD에 함께 누적됐다.
- Codex 활성 실행 경로와 Claude 세션 전용 자산의 경계가 문서에는 있었지만 전체 호출 경로 재감사가 남아 있었다.
- `.codex/hooks.json`이 상대경로로 훅을 호출해 저장소 하위 경로에서 세션을 시작하면 스크립트를 찾지 못할 가능성이 있었다.

### 해결

- `PR_작성규칙.md`의 양식과 DB 절차를 `templates/`, `docs/processes/`로 분리했다.
- 크기·혼합 기준을 넘는 문서는 원문을 `logs/`에 보존하고 현재 handoff를 자동 축약하도록 정했다.
- `DB결함.md`, `단가검토.md`의 전체 기존 본문을 `logs/handoff/`로 이동하고 현재 상태·결정·다음 행동만 새 handoff에 남겼다.
- Codex 단독 기본, Claude 명시 요청 예외, `.claude/` 별도 관리, grilling 폐기, 외부 정본 미확보 시 중단을 공통 규칙에 반영했다.
- 작업일지는 Claude를 실행하지 않고 Codex 및 명시적으로 사용된 Claude 세션 JSONL을 읽기 전용으로 합치도록 명시했다.
- Codex 훅은 저장소 루트를 동적으로 구해 실행하도록 수정하고 `docs/SECOND_BRAIN.md`도 신선도 감시 대상에 포함했다.

### 런타임 감사 결과

- `scripts/execute.py`는 `codex exec`만 호출한다.
- `scripts/daily_worklog.py`의 AI 요약은 읽기 전용·ephemeral `codex exec`만 사용한다.
- Claude 관련 활성 코드는 과거 세션 JSONL 읽기뿐이며 `claude -p` 또는 Claude 프로세스 호출은 없다.
- Codex `.codex/hooks.json`에는 답변 검토 `Stop` 훅이 없고 `UserPromptSubmit` 규칙 신선도 알림만 있다.
- `.claude/settings.json`의 answer-review 훅과 `.claude/skills/`는 Claude 세션 전용 자산이다. Codex에서는 호출·수정하지 않는다.
- `.claude/settings.local.json`의 `bypassPermissions`는 Claude 세션 설정이므로 이번 Codex 작업에서 변경하지 않는다.

### 검증

- Python 컴파일과 `.codex/hooks.json` 파싱 통과.
- `scripts/` 전체 테스트 `62 passed`.
- `Projects/Tomes-Cloud` 하위 경로에서 Windows 훅 명령을 직접 실행해 종료 코드 0과 상태 파일 생성을 확인했다.
- 첫 하위 경로 보완안은 내부 Git 루트를 잘못 선택해 실패했으며, 현재 경로의 상위 디렉터리에서 실제 `.codex`를 찾는 방식으로 교정 후 통과했다.
- pytest 기본 임시 폴더는 기존 ACL로 설정 단계에서 실패했으며, 저장소 안의 실행 전용 임시 폴더로 재실행해 전체 통과했다. 임시 폴더는 실행 후 제거했다.
- `DB결함.md`, `단가검토.md` 역사 보존본은 이동 직후 제목 한 줄을 가상 복원한 SHA-256이 원본과 일치함을 확인했다. 이후 혼합 줄바꿈을 CRLF로 통일했으므로 최종 파일의 바이트 해시는 달라졌지만 본문 문장과 섹션은 유지했다.

## 2026-07-29 공개 포크 운영·민감정보 차단

- 개발자의 [공개 튜토리얼](https://raspy-roll-970.notion.site/340f7725c9d98176b68bd31c823c7540)은 원본 저장소와 `git clone ... my-project` 빠른 시작을 명시한다. 의도된 클론·프로젝트별 수정 사용의 근거로 확인했으며, 별도 판매·재배포·재라이선스는 명시되지 않아 범위 밖으로 둔다.
- 사용자는 현재 공개 포크 브랜치를 유지하되 신규 민감정보를 올리지 않기로 결정했다.
- GitHub Secret Scanning과 Push Protection의 활성 상태를 확인했다. 일반 비밀번호 할당과 공급자 미지원 비밀, 원시 바이너리까지 로컬 커밋·푸시 전에 차단하도록 저장소 소유 Git 훅과 검사기를 추가했다.
- 새 PC·새 clone에서는 `py scripts/install_git_hooks.py`를 한 번 실행한다. 훅 실패는 `--no-verify`로 우회하지 않는다.
- 기존 공개 이력의 원격 DB 자격증명은 별도 교체가 필요하다. 이력 재작성과 force-push는 수행하지 않았다.

## 2026-07-29 Windows 훅·Codex 설치 경로 정리

### 현상

- `UserPromptSubmit`마다 `hook exited with code 1`이 반복됐다.
- Codex CLI가 C: `0.145.0`과 D: `0.144.6`에 중복 설치돼 사용자 `Path`에서 C:가 D:보다 먼저 선택됐다.

### 원인

- Codex가 Windows `commandWindows`를 PowerShell로 실행하는데 `.codex/hooks.json`이 다시 `powershell -NoProfile -Command`를 호출했다. 이중 PowerShell에서 `$dir`, `$hook` 변수가 바깥 셸에 먼저 확장돼 사라지고 경로 탐색의 마지막 `exit 1`로 종료됐다.
- D: npm 전역 경로는 맞았지만 `D:\Tool\nodejs\node_modules\@openai`가 관리자 소유·일반 사용자 읽기 전용 ACL이라 일반 npm 갱신이 `EPERM`으로 실패했다.

### 해결

- `commandWindows`에서 중첩 `powershell -NoProfile -Command`를 제거하고 `py -3 -X utf8`로 훅 스크립트를 직접 실행하게 했다.
- 문자열 포함 검사에 더해 Codex와 동일하게 PowerShell로 `commandWindows`를 실행하고, 제품 하위 경로에서 종료 코드 0·무출력·상태 파일 생성을 확인하는 Windows 회귀 테스트를 추가했다.
- D: Codex를 UAC 관리자 설치로 `0.145.0`에 맞추고 사용자 `Path`에서 C:의 루트·shim 두 항목을 제거해 `D:\Tool\nodejs`만 남겼다.
- 현재 대화를 포함한 C: 기반 프로세스를 강제 종료하지 않도록, 해당 프로세스들이 종료된 직후 정확한 C: 설치 루트만 삭제하는 숨김 정리 작업을 등록했다. 결과 로그는 `D:\LOGS\codex-c-install-cleanup-20260729.log`다.

### 채택 이유

- 훅 명령 본문과 Codex의 셸 책임을 분리하면 Windows 변수의 이중 확장을 없애면서 기존 상위 경로 탐색 동작을 유지할 수 있다.
- D: 버전을 현재 사용하던 C:와 동일하게 맞춰 설치 위치만 바꾸고 기능 버전 변경은 피했다.
- 실행 중인 CLI를 즉시 삭제하거나 종료하는 대신 종료 후 삭제해 현재 세션과 다른 열린 Codex 세션의 데이터 손실 위험을 피했다.

### 결과

- 훅 JSON 파싱·Python 컴파일·제품 하위 경로 직접 실행은 통과했다.
- 신규 Windows 실실행 테스트를 포함한 `scripts/test_codex_migration.py`는 `6 passed`, 하네스 전체는 `70 passed`다. 최초 pytest는 기존 샌드박스 Temp ACL과 전용 임시 폴더 부모 누락으로 fixture 설정이 두 차례 실패했으며, 저장소 내부 전용 임시 경로를 명시하고 제가 만든 임시 폴더만 제거한 재실행에서 통과했다.
- D: 패키지 메타데이터와 직접 실행이 모두 `0.145.0`, C: 항목을 제외한 새 사용자 `Path`에서 `codex` 해석 결과가 `D:\Tool\nodejs\codex.ps1`임을 확인했다.
- C: 설치 루트는 이 기록 시점에 실행 중인 세션 때문에 존재하며, 세션 종료 후 자동 삭제 및 로그 확인이 남아 있다.

## 2026-07-29 훅 신뢰 상태 반복 경고 해소

### 현상

- 새 세션마다 `UserPromptSubmit` 훅이 `modified / review required`로 표시되고 실행되지 않는다는 보고가 있었다.

### 원인

- 저장소의 현재 훅 정의와 사용자 설정의 `trusted_hash`는 이미 일치했지만, 같은 훅 상태에 `enabled = false`가 남아 있었다.
- 경고를 캡처한 세션은 현재 해시가 사용자 설정에 저장되기 전에 시작됐고, 이후 새 0.145.0 app-server의 `hooks/list`에서는 훅이 `trusted`이지만 비활성으로 확인됐다.

### 해결

- Codex의 공식 `config/batchWrite` 경로로 현재 신뢰 해시를 유지하면서 사용자 설정의 훅 상태만 `enabled = true`로 변경했다.
- 저장소의 `.codex/hooks.json`과 훅 스크립트는 변경하지 않았다.

### 채택 이유

- 훅 정의를 다시 바꾸거나 신뢰 검사를 우회하지 않고, 남아 있던 비활성 상태만 되돌리는 최소 변경이다.
- 직접 설정 파일을 임의 편집하는 대신 현재 Codex가 사용하는 구성 쓰기 경로를 사용해 병합·재로드 계약을 지켰다.

### 결과

- 새 0.145.0 app-server에서 `enabled: true`, `trustStatus: trusted`, 현재 해시 일치를 확인했다.
- 훅 스크립트 Python 컴파일과 직접 실행은 종료 코드 0, 관련 회귀 테스트는 저장소 내부 전용 임시 경로에서 `6 passed`다.
- 기본 pytest 임시 경로는 기존 ACL 때문에 최초 실행에서 1 passed/5 errors였으며, 코드 결함이 아니라 fixture 생성 실패임을 확인한 뒤 전용 경로로 재검증했다.

## 다음 단계

- [x] 관련 Python 컴파일·테스트·훅 하위 경로 실행을 검증한다.
- [x] 문서 링크·인코딩·크기와 최종 diff를 검증한다.
- [x] 변경된 Codex 훅 정의의 현재 해시를 신뢰하고 활성화한 뒤 새 app-server에서 상태를 재검증한다.
- [ ] `.claude/skills/`의 grilling 자산 정리는 Claude 세션에서 별도로 수행한다.
- [ ] C: 자동 정리가 완료되지 않은 원인을 확인하고, 실행 중인 세션 종료 후 C: 설치·shim·사용자 `Path`를 정리할지 결정한다.

## 블로커·주의

- 기존 `scripts/daily_worklog.py`와 여러 handoff 파일은 작업 시작 전부터 미추적 상태였다. 이번 전환과 직접 관련된 파일만 선별해 커밋한다.
- 과거 문서의 “Claude/answer-reviewer 검증 완료” 표기는 당시 사실 기록이므로 소급 변경하지 않는다.
- 현재 확인된 UserPromptSubmit 결함은 수정됐지만, 같은 방식의 상태 전이 누락이 다른 훅·자동화에 없는지는 아직 전수 검증하지 않았다.
- C: 자동 정리는 완료되지 않았다. 현재 `codex`는 C: shim을 먼저 선택하고 `codex doctor`는 실행 패키지 루트(C:)와 npm 전역 패키지 루트(D:) 불일치로 install/update 2건을 실패 처리한다. 두 설치 모두 0.145.0이어서 이번 훅 신뢰 판정의 직접 원인은 아니며, 실행 중인 세션을 종료하거나 설치·`Path`를 변경하지 않았다.
- 2026-07-29 동시 작업이 `e852e43`, `9d40074`, `c20bc26`을 생성해 `myfork/feat-code-cache`에 push했다. 현재 워킹트리는 clean이며 이 세 커밋은 이번 Codex가 직접 실행한 커밋이 아니다.
- `9d40074`는 작업일지·패치 백업·분석 로그·이미지 등 41개 파일을 추가했다. 신규 파일에서 일반적인 API 키·토큰·개인키·비밀번호 할당 패턴은 발견되지 않았지만 공개 가능한 업무 데이터인지 별도 검토가 필요하다.
- 원격 `SJY5261/harness_framework`는 PUBLIC이다. 기존 `logs/check_rows.py`에는 플레이스홀더가 아닌 13자 비밀번호와 원격 호스트 설정이 있고 `ac2553f`부터 공개 이력에 남아 있다. 값은 보고서에 남기지 않는다.
- 위 자격증명은 우선 교체가 필요하다. Git 이력에서 제거하려면 이력 재작성과 force-push가 필요하므로 사용자 승인 전에는 실행하지 않는다.

## 관련 파일·경로

- `AGENTS.md`
- `PROJECT_RULES.md`
- `CLAUDE.md`
- `.codex/`
- `scripts/execute.py`
- `scripts/daily_worklog.py`
- `discussion/TEMPLATE.md`
- `handoff/Codex진행안내.md`
