# HANDOFF — 활성 작업 인덱스

_최종 갱신: 2026-08-03_

이 파일은 현재 작업을 찾기 위한 인덱스다. 운영 규칙은 `AGENTS.md`, 제품·안전 규칙은 `PROJECT_RULES.md`, 조건부 절차는 `docs/processes/`, 세부 경위는 연결된 `handoff/`, 완료 이력과 증적은 `logs/`에서 확인한다. 오래된 git·서버·DB 상태는 기록을 믿지 말고 다시 측정한다.

## 현재 환경

- 사용자 환경 맞춤 판단과 현재 PC·도구·작업 성향의 정본은 [`context/README.md`](context/README.md)에서 찾는다.
- 경로 정본은 `PATHS.md`, 작업별 변동 상태와 다음 행동은 아래 활성 작업과 연결된 handoff에서 확인한다. 오래된 git·프로세스·서버·DB 상태는 다시 측정한다.

## 활성 작업

- [SiteAdmin_재질표면처리매핑] **1~7단계 구현·개발 DB 125건 반영·격리 전체 빌드 완료 / UI·기존 데이터 정책 대기** — 슬라이드 15 기준 다대다 테이블, 조회·저장 API, 공통코드 응답·필터·캐시 무효화를 구현했다. 구형 D03 데이터 18,954건과 신형 매핑 불일치 13건은 변경하지 않았고, Site Admin 코드 정본 29↔51 불일치와 함께 8단계 전 결정이 필요하다 — [상세](handoff/SiteAdmin_재질표면처리매핑.md)
- [Codex주에이전트전환] **현재 PC 핵심 개발·테스트 기능 호환 완료 / GUI 도구 데이터 이관 대기** — 버전·설치 위치의 완전 복제 대신 실제 업무 명령을 기준으로 D: Python 3.14.6, 테스트 의존성, Playwright 1.61.0·Chromium, 제품 웹루트 junction을 복구했다. Codex 훅 8 PASS, Chromium 실행 PASS, `%테스트` 191 PASS/기존 3 FAIL로 업무 PC 기준과 일치하며 Git 원격·Gradle도 정상이다. VS Code·Codex 개인 홈·SourceTree·DBeaver·Git 전역 데이터 이관은 별도 대기 — [상세](handoff/Codex주에이전트전환.md)
- [업무PC복귀인계] **주요 복구·Codex 훅·실화면 재검증 완료 / 개발 DB TLS 결정·미전달 원본 대기·POP 실기기 보류** — 개발 런타임·경로·Windows `workspace` 샌드박스 복구와 Codex 훅 상태 전이 검증을 완료했다. 개발 DB 서버는 TLS가 비활성이고 Connector/J도 기본 비SSL 연결이며, 로컬 MariaDB 설정에는 존재하지 않는 `E:` 플러그인 경로가 남아 있어 적용 방침 결정이 필요하다. POP 바코드 스캐너 실기기 검증은 2026-07-29 사용자 결정으로 보류했다. 하네스 60 PASS, 제품 빌드 PASS, `%테스트` 191 PASS/기존 계획 불일치 3 FAIL — [상세](handoff/업무PC복귀인계.md)
- [가공확정] **KAN-63 / KAN-6 구현·빌드 완료, KAN-35 DB 반영 완료, KAN-38 화면·POP 실기기 검증 보류** — 재확정 예외를 작업트리에 복원하고 작업상세정보의 가공확정 일시·진행상태 표시를 제거했다. 제조원가 분석 메뉴 8행은 영구 백업 후 숨김 처리·검증·COMMIT 완료. 작업지시 현황추적 화면과 POP 바코드 스캐너 실기기 검증은 사용자 결정에 따라 보류 — [상세](handoff/가공확정.md)
- [단가검토] **사용자 결정 대기** — 단가입력 개편 검증 완료. 배송비 컬럼명·견적→주문 복사 여부 결정 후 DDL 및 기록조회 후속 작업 — [상세](handoff/단가검토.md)
- [DB결함] **구현·SMD DB 반영·제품 브랜치 push·PR 리뷰와 신입 개발자용 코드·DB 학습 가이드 완료 / 제품 PR 미생성** — `origin/main` `fb3c240` → `feature-control-0713` `2aad3db`의 실질 diff는 커밋 `88bf7dc` 4파일이며 clean build PASS. 2026-08-01 원본 미확보로 `Desktop\Tomes\PR`에 재구성본을 만들었다는 기록이 있으나, 2026-08-03 현재 해당 경로는 없고 `Desktop\PR\[07.31 DB결함 코드 학습 가이드]`의 원본 MD·HTML만 확인된다. 원본 HTML 좌측 목차는 제거했고 테마·인쇄 도구는 상단에 유지했다. 폐기한 `[07.29 DB결함 코드 이해 리뷰]`는 재사용하지 않는다 — [상세](handoff/DB결함.md)
- [거래명세표] **보류** — 슬라이드36·라벨모달은 `stash@{0}`에 보관. 수량 의미와 라벨 보호 정책 결정 후 재개 — [상세](handoff/거래명세표.md)
- [기타] **대기 항목 모음** — 도면팝업 실화면 검증, 로컬 설정 복구 경위, 직원 목록 캐시 개선 — [상세](handoff/기타.md)

## 운영 문서

- Codex 진행 안내: [handoff/Codex진행안내.md](handoff/Codex진행안내.md)
- 세컨브레인 구조: [docs/SECOND_BRAIN.md](docs/SECOND_BRAIN.md)
- 완료 이력: [logs/HANDOFF_ARCHIVE.md](logs/HANDOFF_ARCHIVE.md)
