# HANDOFF — 활성 작업 인덱스

_최종 갱신: 2026-07-30_

이 파일은 현재 작업을 찾기 위한 인덱스다. 운영 규칙은 `AGENTS.md`, 제품·안전 규칙은 `PROJECT_RULES.md`, 조건부 절차는 `docs/processes/`, 세부 경위는 연결된 `handoff/`, 완료 이력과 증적은 `logs/`에서 확인한다. 오래된 git·서버·DB 상태는 기록을 믿지 말고 다시 측정한다.

## 현재 환경

- 사용자 환경 맞춤 판단과 현재 PC·도구·작업 성향의 정본은 [`context/README.md`](context/README.md)에서 찾는다.
- 경로 정본은 `PATHS.md`, 작업별 변동 상태와 다음 행동은 아래 활성 작업과 연결된 handoff에서 확인한다. 오래된 git·프로세스·서버·DB 상태는 다시 측정한다.

## 활성 작업

- [Codex주에이전트전환] **D: 실행 파일 정본 완료 / 도구 데이터 즉시 항목 이관 완료·실행 중 항목 자동 완료 대기** — `D:\ToolData`는 사용자·SYSTEM·관리자 전체 권한과 Codex 샌드박스 수정 권한으로 한정했다. Playwright·npm·pip·Python 사용자 기반·GitHub CLI·JetBrains 데이터는 D: 이관·실행 검증을 마쳤고, VS Code·Copilot·Codex·SourceTree·DBeaver·Gradle·Git 데이터는 해당 프로세스 종료 후 숨김 작업이 해시 검증·junction 전환까지 완료한다 — [상세](handoff/Codex주에이전트전환.md)
- [업무PC복귀인계] **주요 복구·Codex 훅·실화면 재검증 완료 / 개발 DB TLS 결정·미전달 원본 대기·POP 실기기 보류** — 개발 런타임·경로·Windows `workspace` 샌드박스 복구와 Codex 훅 상태 전이 검증을 완료했다. 개발 DB 서버는 TLS가 비활성이고 Connector/J도 기본 비SSL 연결이며, 로컬 MariaDB 설정에는 존재하지 않는 `E:` 플러그인 경로가 남아 있어 적용 방침 결정이 필요하다. POP 바코드 스캐너 실기기 검증은 2026-07-29 사용자 결정으로 보류했다. 하네스 60 PASS, 제품 빌드 PASS, `%테스트` 191 PASS/기존 계획 불일치 3 FAIL — [상세](handoff/업무PC복귀인계.md)
- [가공확정] **KAN-63 / KAN-6 구현·빌드 완료, KAN-35 DB 반영 완료, KAN-38 화면·POP 실기기 검증 보류** — 재확정 예외를 작업트리에 복원하고 작업상세정보의 가공확정 일시·진행상태 표시를 제거했다. 제조원가 분석 메뉴 8행은 영구 백업 후 숨김 처리·검증·COMMIT 완료. 작업지시 현황추적 화면과 POP 바코드 스캐너 실기기 검증은 사용자 결정에 따라 보류 — [상세](handoff/가공확정.md)
- [단가검토] **사용자 결정 대기** — 단가입력 개편 검증 완료. 배송비 컬럼명·견적→주문 복사 여부 결정 후 DDL 및 기록조회 후속 작업 — [상세](handoff/단가검토.md)
- [DB결함] **구현·제품 브랜치 push·사용자 변경 범위 PR 리뷰 MD/HTML 완료 / 후속 후보 별도 지시 대기** — `%클라우드` 커밋 `88bf7dc`를 push했고, `Desktop\PR\[07.28 DB결함 수정 리뷰]`에는 사용자가 변경한 `CONTROL_NUM` 백필·DDL과 `SP_CONTROL_BATCH` 가드·검증·선택적 복구 SQL만 포함했다. 자동 Claude 검토 대기는 제거하고 긴 진행 이력은 `logs/handoff/`로 분리했다 — [상세](handoff/DB결함.md)
- [거래명세표] **보류** — 슬라이드36·라벨모달은 `stash@{0}`에 보관. 수량 의미와 라벨 보호 정책 결정 후 재개 — [상세](handoff/거래명세표.md)
- [기타] **대기 항목 모음** — 도면팝업 실화면 검증, 로컬 설정 복구 경위, 직원 목록 캐시 개선 — [상세](handoff/기타.md)

## 운영 문서

- Codex 진행 안내: [handoff/Codex진행안내.md](handoff/Codex진행안내.md)
- 세컨브레인 구조: [docs/SECOND_BRAIN.md](docs/SECOND_BRAIN.md)
- 완료 이력: [logs/HANDOFF_ARCHIVE.md](logs/HANDOFF_ARCHIVE.md)
