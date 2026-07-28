# 업무용 PC 복귀 인계

_최종 갱신: 2026-07-28 / 상태: 주요 복구·Codex 샌드박스·실화면 재검증 완료 / 미전달 원본·POP 실기기 검증 대기_

## 현재 상태

- 업무용 PC 수리 기간 중 현재 PC에서 진행한 작업은 크게 두 가지다.
  1. 저장소의 주 에이전트를 Claude에서 Codex로 전환
  2. 가공확정 페이지 폐지 영향 조사와 관련 수정·검증
- 이 문서는 PC 간 이동 목록만 요약한다. 작업 판단과 검증의 정본은 아래 연결된 상세 handoff를 따른다.

## 목표·완료 조건

- 업무용 PC에서 아래 커밋, 미커밋 제품 코드, 로컬 전용 설정과 검증 자료를 누락 없이 이어받는다.
- 업무용 PC에서 세 저장소의 Git 상태를 다시 확인하고 관련 기능을 재검증한다.
- 반영 완료 후 각 항목의 `업무용 PC 반영` 상태를 완료로 바꾸고 이 문서를 보관 처리한다.

## 변경 요약

### 1. Claude에서 Codex 주 에이전트로 전환

상태: **구현·검증·하네스 커밋 완료 / 업무용 PC 동기화 완료**

- Codex를 기본 오케스트레이터로 변경했다.
- `AGENTS.md`를 Codex 운영 정본, `PROJECT_RULES.md`를 제품·안전 규칙 정본으로 분리했다.
- `CLAUDE.md`와 `.claude/`는 사용자가 요청할 때만 쓰는 선택적 호환 자산으로 남겼다.
- 하네스 실행기와 일일 작업일지 요약의 기본 호출을 `codex exec`로 전환했다.
- 세컨브레인 구조, 경로 문서, 활성 handoff 인덱스와 진행 안내를 Codex 기준으로 정리했다.
- 관련 테스트는 최종 59개 통과했고 Python 컴파일, 설정 파싱, phase 컨텍스트 경로 검사를 통과했다.

업무용 PC에서 받아야 할 `&하네스` 커밋:

| 커밋 | 내용 |
|---|---|
| `40a8a0e` | 진행 상황 표시 기반 추가 |
| `98aaf0d` ~ `d96732d` | 진행 handoff 문구·UTF-8 처리 보정 |
| `72a3bc4` | Codex 주 에이전트 전환 |
| `898f4db` | Codex 규칙·컨텍스트 흐름 최적화 |
| `b562e37` | 결과 보고 형식 표준화 |

업무용 PC 최소 반영 기준은 `&하네스` 브랜치 `feat-code-cache`, HEAD `536f9a1`
(`b562e37` 이후 업무 PC 복귀 인계 문서 커밋 포함)이었다. 인증 복구 완료 기준
`b15f2e9` 이후 D 드라이브 경로 통일 커밋 `68282e1`도 원격에 반영했다.

상세 정본: `handoff/Codex주에이전트전환.md`

### 2. 가공확정 페이지 작업

상태: **재확정 제품 코드 2개 병합·제품 HEAD 동기화·업무 PC 실화면 재검증 완료 / 원본 증적 미전달 / 후속 구현 대기**

- KAN-63의 “페이지 삭제”를 파일 삭제가 아닌 메뉴 비활성으로 확정했다.
- dev DB에서 가공확정 메뉴를 비활성화했고 백업·복원 자료를 남겼다. 운영 DB에는 아직 적용하지 않았다.
- `S53R14` 소비처와 페이지 제거 영향을 조사했다. 상태 자체를 즉시 제거하면 POP, 소재주문, 도면 바코드 등에 영향이 있어 별도 설계가 필요하다.
- 가공확정 페이지가 사라진 뒤 일부 파트가 잠기는 문제를 막기 위해 작업지시확정 재확정 예외를 추가했다.
- 아래 2개 제품 파일은 아직 미커밋 상태이며, 변경량은 `+23/-2`다.

| 파일 | 변경 목적 |
|---|---|
| `Projects/Tomes-Cloud/src/main/webapp/WEB-INF/views/common/create_control.jsp` | 가공확정 이력이 없는 비외주 파트의 작업지시 재확정 허용 |
| `Projects/Tomes-Cloud/src/main/webapp/resource/modules/pages/order/control-manage.js` | 동일한 재확정 예외를 작업지시관리 화면에 적용 |

- 정적 문법 검사와 개인 PC의 dev 실화면 4개 케이스가 통과했다. 개인 PC 원본 증적은 미전달이지만, 업무 PC에서 현재 수정 조건을 기준으로 네 가지를 재구성해 다시 통과했다.
- 실제 POP 바코드 스캔 실기기 확인은 하지 않았다.
- 다음 구현 순서는 KAN-6 → KAN-35 → KAN-38이다.

개인 PC 기준 `%클라우드` HEAD `c0ac256`은 GitHub 인증 후 `origin/main`에서 확인됐다.
업무용 PC의 `feature-control-0713`을 `3b52126`에서 `c0ac256`으로 fast-forward했고,
기존 staged/unstaged 변경과 미추적 파일 목록은 그대로 복원했다. 위 2개 파일의 기능
변경도 유지되며 안전 백업은 `stash@{0}`에 남겼다.

상세 정본: `handoff/가공확정.md`

## PC 이동 대상

| 구분 | 대상 | 전달 방식 | 업무용 PC 반영 |
|---|---|---|---|
| 하네스 커밋 | `40a8a0e` ~ `b562e37` | 원격 동기화 후 HEAD 확인 | **완료** — 최소 기준 `536f9a1`, 인증 복구 `b15f2e9`, D 경로 통일 `68282e1` 원격 반영 |
| 제품 미커밋 diff | `%클라우드` 위 2개 파일 | 현재 파일을 덮어쓰지 말고 Git diff로 병합 | **완료** — 전달본과 줄바꿈 정규화 후 내용 일치 |
| 제품 로컬 커밋 | `%클라우드` HEAD `c0ac256` 포함 16커밋 | push 또는 Git bundle/patch | **완료** — 인증 후 `origin/main`에서 확인, `feature-control-0713` fast-forward |
| 가공확정 증적 | `logs/가공확정_*` | 관련 로그·JSON·스크린샷 디렉터리 선별 복사 | **부분** — 개인 PC 원본은 미전달, 업무 PC 재검증 증적 신규 생성 |
| 로컬 실행 설정 | `%클라우드/shell/runDev.local.bat`, `%테스트/.env` 등 | 승인된 보안 매체로 별도 이동 | **완료(현재 환경)** — 기존 비밀값 보존, `D:\harness_framework`·`D:\Tool`·`D:\LOGS` 기준으로 통일하고 서버·Gradle·테스트 경로 확인 |
| Codex 개인 설정 | 모델·인증·알림·전역 권한 | 저장소에 넣지 않고 업무용 PC에서 별도 설정 | **부분** — 기존 인증·모델과 elevated Windows 샌드박스·전용 Temp·Gradle 홈 설정 완료, 알림 원본만 미전달 |
| 개발 런타임 | JDK 21, Python, Node, MySQL, Playwright | 업무 PC 사용자 환경 설정 | **완료** — Python 3.14.6·의존성·Chromium 포함, 사용자 `Path`·`PYTHONUTF8=1`, 샌드박스용 Python 공용 등록과 PowerShell `RemoteSigned` 설정 |
| Git/GitHub | Git 작성자·GCM·GitHub CLI | 사용자 설정·브라우저 인증 | **완료** — `SJY5261` 키링 인증, GitHub 전용 credential helper 연결, 하네스 push·제품 fetch 확인 |
| 작업일지 자동화 | `scripts/run_worklog.bat`, `DailyWorklog` | 현재 경로로 교정 후 평일 17:30 예약 | **완료(로컬)** — dry-run 통과, Notion 토큰은 미전달 |

비밀번호, 토큰, 계정값은 이 문서나 Git에 기록하지 않는다.

## 결정

- 두 작업을 하나의 PC 복귀 문서에서 요약하고 상세 내용은 기존 handoff에 연결한다 — 중복 기록으로 상태가 어긋나는 것을 줄이기 위해서다.
- 2026-07-24 이후 새 변경은 이 문서 하단 변경 기록에 계속 추가한다 — 업무용 PC 복귀 시 이동 범위를 한곳에서 확인하기 위해서다.
- 제품 미커밋 파일은 자동 커밋하지 않는다 — `%클라우드` 커밋은 사용자 몫이라는 저장소 규칙을 따른다.
- PC 이관 근거는 `C:\Users\User\Desktop\Downloads`만 사용한다. `C:\Users\User\Downloads`의 일반 앱 설치 파일은 이번 작업 범위가 아니다.

## 이후 변경 기록

| 날짜 | 저장소 | 변경 내용 | 파일·커밋 | 검증 | 업무용 PC 반영 |
|---|---|---|---|---|---|
| 2026-07-27 | `&하네스` | 업무용 PC 복귀 인계 문서 작성 | `handoff/업무PC복귀인계.md`, `HANDOFF.md` | 문서와 Git diff 확인 | 대기 |
| 2026-07-27 | 업무용 PC | 하네스 동기화, 제품 2파일 병합, Git safe.directory 3개와 JDK 21 사용자 환경 설정 | `536f9a1`, 기록 커밋 `accadf2`(로컬), 제품 JSP/JS 2개 | 하네스 HEAD·제품 diff·JS 문법·설정값 확인 | 부분 완료 |
| 2026-07-27 | 업무용 PC | 포맷 후 개발 환경 복구 | Python 3.14.6, GitHub CLI, Playwright Chromium, `%테스트/.env`, `run_worklog.bat`, `DailyWorklog`, `D:\GITHUB\tomes-cloud-v1-master` junction | 하네스 59 PASS, 제품 build PASS, Playwright PASS, `%테스트` 191 PASS/3 FAIL | 부분 완료 |
| 2026-07-27 | 업무용 PC | GitHub 인증과 원격 동기화, Python UTF-8 복구 | 하네스 `801528f` push, 제품 `c0ac256` fast-forward, `PYTHONUTF8=1` | GitHub API·Git 원격 읽기, 제품 build, 하네스 59 PASS, 로컬 변경 목록 보존 확인 | 주요 복구 완료 |
| 2026-07-27 | 업무용 PC | 남은 항목 재확인, 개발 실행 경로·JDK 보정, 가공확정 실화면 재검증 | `runDev.local.bat`, `logs/가공확정_업무PC재검증_2026-07-27.json` | 서버·DB 연결, 기존 확정 자동화 1건, 재구성한 화면 4건 통과 | 실화면 완료·POP 실기기 대기 |
| 2026-07-27 | 업무용 PC | 수리 후 `C:`, `D:` 두 드라이브 환경에 맞춰 프로젝트 관련 경로 전수 정리 | 하네스·제품·테스트 보조 설정, 환경 변수, Git, 편집기, 예약 작업 | 실제 설정의 옛 `E:`·개인 PC 경로 0건, 하네스 59 PASS, Gradle help PASS, `%테스트` 191 PASS/기존 3 FAIL | 경로 통일 완료 |
| 2026-07-27 | 업무용 PC | DBeaver의 `Tomes-Cloud` 개발 DB 연결 복구 | DBeaver 25.0.1 로컬 워크스페이스·MariaDB 3.5.2 드라이버 | 저장 연결 1건, 보안 자격 증명 저장소, `SELECT 1` 통과 | 완료 |
| 2026-07-28 | 업무용 PC·`&하네스` | 포맷 전 SID로 인한 Codex Windows 샌드박스 초기화 오류 복구 | 작업공간 소유권·ACL, Python 3.14 HKLM 등록, 개인 Codex Temp·Gradle 홈, `artifacts/acl_before_codex_sandbox_fix_2026-07-28.txt` | `workspace` 반복 초기화·실제 쓰기, `read-only`·`.git`·`.codex` 쓰기 차단, 하네스 59 PASS, 제품 build PASS, `%테스트` 191 PASS/기존 3 FAIL | 샌드박스 완료 |

## 검증

- 세 저장소의 `git status --short --branch`, 최근 커밋, stash 목록 확인 — 통과
- `%클라우드` 미커밋 2개 파일의 실제 diff와 수정 시각 확인 — 통과
- 두 상세 handoff와 커밋별 변경 파일 대조 — 통과
- 하네스 `feat-code-cache`의 D 경로 통일 커밋 `68282e1` 원격 반영 확인 — 통과
- 전달 제품 파일 2개와 업무 PC 병합본 비교 — 통과(줄바꿈 형식 제외 내용 일치)
- `git diff --check`, `node --check control-manage.js` — 통과
- `%클라우드` Gradle 빌드(JDK 21, `--max-workers=4 --no-daemon`) — 통과(기존 Lombok 경고 1건)
- 하네스 마이그레이션 테스트·Python 컴파일 — 59개 통과
- `%테스트` 전체 pytest — 191개 통과, OSR-173 계획 파일의 기존 `assert_eval` 누락으로 3개 실패
- Playwright Chromium headless 실행 — 통과
- DailyWorklog `--dry-run --no-ai`와 평일 17:30 예약 작업 — 통과
- GitHub CLI `SJY5261` 키링 인증, 하네스 `myfork/feat-code-cache` push, 제품 `origin` fetch — 통과
- 제품 `feature-control-0713`을 `c0ac256`으로 fast-forward 후 staged/unstaged·미추적 목록 보존 — 통과
- `PYTHONUTF8=1` 사용자 설정 후 하네스 테스트 — 59개 통과
- dev 서버 `local` 프로필·DB 연결과 기존 작업지시확정 자동화 `CD-FT-CTL-032` — 통과
- DBeaver 25.0.1 `Tomes-Cloud` 연결·MariaDB 3.5.2 드라이버·보안 자격 증명 저장 후 `SELECT 1` — 통과
- 개인 PC 원본 증적은 찾지 못해 수정된 두 화면의 허용·차단 조건으로 네 가지를 재구성해 실화면 검증 — 4개 통과, 실제 저장 요청은 차단
- POP 바코드 실기기 — 연결 장치 중 식별 가능한 스캐너가 없어 미실행
- 세 저장소의 실행 설정, 환경 변수, Git safe.directory, VS Code·터미널, 예약 작업, 바로가기, 서비스, SourceTree에서 옛 `E:`와 개인 PC 루트 재검색 — 실제 사용 설정 0건
- `D:\harness_framework`, `D:\Tool`, `D:\LOGS` 대상 존재 여부와 Git Bash `/d/` 경로 확인 — 통과
- `SetNamedSecurityInfoW failed: 5` 원인을 작업공간의 포맷 전 소유자 SID와 이전 샌드박스 ACE로 확인하고, ACL 복원본 저장 후 현재 사용자 소유권·현재 `CodexSandboxUsers` 상속 ACE로 정규화 — 통과
- `codex sandbox -P :workspace` 반복 초기화와 별도 `CodexSandboxOffline` 계정 실행·하위 쓰기 — 통과. `:read-only`, `.git`, `.codex` 쓰기 시도 — 정상 차단
- 샌드박스 계정의 Python 3.14 `py` 인식, 전용 Temp, 격리된 Gradle 캐시 적용 후 하네스 59 PASS·제품 전체 빌드 PASS. `%테스트`는 191 PASS/기존 OSR-173 3 FAIL

## 다음 행동

1. 개인 PC의 `logs/가공확정_*` 원본 증적이 남아 있다면 선별 전달해 업무 PC 재검증 항목과 대조한다.
2. 개인 Codex 알림 원본이 필요하면 승인된 보안 매체로 전달한다.
3. `%테스트`의 OSR-173 계획 파일과 테스트 기대값 불일치를 별도 저장소 결함으로 정리한다.
4. POP 바코드 스캐너를 연결한 뒤 실제 입력과 후속 상태 반영을 검증한다.
5. 위 항목 완료 후 표를 완료로 바꾸고 이 문서를 보관 처리한다.

## 블로커·위험

- 가공확정 재확정 수정 2개 파일을 포함한 제품 로컬 변경은 미커밋 상태이므로 커밋 전까지 작업트리를 보존해야 한다. `c0ac256` fast-forward 직전 tracked 상태는 제품 `stash@{0}`에도 안전 백업했다.
- 개인 PC의 가공확정 원본 증적과 Codex 알림 원본은 전달 폴더에 없다. 전역 샌드박스 권한은 업무 PC에서 재구성했고, 화면 재검증 증적은 `logs/가공확정_업무PC재검증_2026-07-27.json`에 새로 남겼다.
- 과거 문서·로그·검증 산출물에는 당시 사용한 `E:` 경로가 남아 있다. 실행 설정과 구분되는 이력이므로 일괄 치환하지 않았다.
- `%테스트`의 `tests/test_osr173_size_type_change.py`는 `CD-FT-OSR-173.json`에 없는 `assert_eval` 레시피를 요구해 3개가 실패한다. 환경 실패가 아니라 커밋된 계획 데이터 불일치다.
- 운영 DB 메뉴 비활성은 아직 미적용이다. 적용 시 백업·트랜잭션·검증 SELECT 후 사용자 확인을 받고 COMMIT해야 한다.
- `%테스트/.env`, `application-local.yml`, `runDev.local.bat` 등에는 비밀이 있을 수 있어 일반 문서나 Git으로 옮기면 안 된다.

## 관련 경로

- `handoff/Codex주에이전트전환.md`
- `handoff/가공확정.md`
- `logs/가공확정_S53R14_소비처조사_2026-07-23.md`
- `logs/가공확정_재확정검증_2026-07-24/`
- `logs/가공확정_업무PC재검증_2026-07-27.json`
- `artifacts/acl_before_codex_sandbox_fix_2026-07-28.txt`
- `PATHS.md`
