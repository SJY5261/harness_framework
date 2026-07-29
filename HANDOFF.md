# HANDOFF — 활성 작업 인덱스

_최종 갱신: 2026-07-29_

이 파일은 현재 작업을 찾기 위한 인덱스다. 운영 규칙은 `AGENTS.md`, 제품·안전 규칙은 `PROJECT_RULES.md`, 조건부 절차는 `docs/processes/`, 세부 경위는 연결된 `handoff/`, 완료 이력과 증적은 `logs/`에서 확인한다. 오래된 git·서버·DB 상태는 기록을 믿지 말고 다시 측정한다.

## 현재 환경

- 하네스 루트: `D:\harness_framework` (과거 `E:\harness_framework`, `D:\tomes\harness-framework` 기록은 현재 루트로 재해석)
- JDK 21은 `D:\Tool\jdk-21\jdk-21`이며 사용자 `JAVA_HOME`과 `Path` 등록 완료.
- Python 3.14.6과 `py` 런처, `%테스트` 요구 패키지·pytest·Playwright Chromium 설치 완료. Python·Scripts·Launcher 경로는 사용자 `Path`에 등록했고 `PYTHONUTF8=1`을 복구했다.
- DBeaver 25.0.1에 `Tomes-Cloud` MariaDB 연결과 드라이버를 복구했고, 비밀번호는 DBeaver 보안 저장소에만 저장했다.
- 실제 실행·개발 설정은 `D:\harness_framework`, `D:\Tool`, `D:\LOGS` 기준으로 통일했다. 환경 변수, Git, 편집기, 예약 작업, 바로가기, 서비스에는 옛 `E:` 프로젝트 경로가 없다. 과거 문서·로그의 `E:`는 이력으로 보존한다.
- DailyWorklog는 평일 17:30 예약 작업으로 복구했다. 이 PC에는 `NOTION_TOKEN`이 없어 로컬 JSON만 생성하며 백필 절차는 `logs/notion_이관대기.md`를 따른다.
- Codex Windows `workspace` 샌드박스는 포맷 전 SID가 남은 작업공간 ACL을 현재 사용자·샌드박스 그룹 기준으로 복구했다. Python 공용 등록, 샌드박스 전용 Temp와 Gradle 캐시를 개인 Codex 설정에 연결했고 반복 초기화·하네스 59 PASS·제품 빌드 PASS를 재확인했다.

## 활성 작업

- [Codex주에이전트전환] **공개 포크 사용 근거 확인·신규 민감정보 차단 적용 / 기존 자격증명 교체 필요** — 개발자 튜토리얼에서 의도된 클론·프로젝트별 수정 사용을 확인했다. GitHub 보호 기능에 더해 일반 비밀번호·원시 바이너리를 커밋·푸시 전에 막는 저장소 훅을 추가했으며, 기존 공개 이력의 원격 DB 자격증명은 별도 교체가 필요하다 — [상세](handoff/Codex주에이전트전환.md)
- [업무PC복귀인계] **주요 복구·Codex 훅·실화면 재검증 완료 / 개발 DB TLS 결정·미전달 원본·POP 실기기 대기** — 개발 런타임·경로·Windows `workspace` 샌드박스 복구와 Codex 훅 상태 전이 검증을 완료했다. 개발 DB 서버는 TLS가 비활성이고 Connector/J도 기본 비SSL 연결이며, 로컬 MariaDB 설정에는 존재하지 않는 `E:` 플러그인 경로가 남아 있어 적용 방침 결정이 필요하다. 하네스 60 PASS, 제품 빌드 PASS, `%테스트` 191 PASS/기존 계획 불일치 3 FAIL — [상세](handoff/업무PC복귀인계.md)
- [가공확정] **KAN-63 / KAN-6 구현·빌드 완료, KAN-35 DB 반영 완료, KAN-38 화면 확정 전 보류** — 재확정 예외를 작업트리에 복원하고 작업상세정보의 가공확정 일시·진행상태 표시를 제거했다. 제조원가 분석 메뉴 8행은 영구 백업 후 숨김 처리·검증·COMMIT 완료. 작업지시 현황추적 화면은 사용자 결정에 따라 정확한 화면 사양이 확정될 때까지 구현하지 않음 — [상세](handoff/가공확정.md)
- [단가검토] **사용자 결정 대기** — 단가입력 개편 검증 완료. 배송비 컬럼명·견적→주문 복사 여부 결정 후 DDL 및 기록조회 후속 작업 — [상세](handoff/단가검토.md)
- [DB결함] **구현·제품 브랜치 push·사용자 변경 범위 PR 리뷰 MD/HTML 완료 / 후속 후보 별도 지시 대기** — `%클라우드` 커밋 `88bf7dc`를 push했고, `Desktop\PR\[07.28 DB결함 수정 리뷰]`에는 사용자가 변경한 `CONTROL_NUM` 백필·DDL과 `SP_CONTROL_BATCH` 가드·검증·선택적 복구 SQL만 포함했다. 자동 Claude 검토 대기는 제거하고 긴 진행 이력은 `logs/handoff/`로 분리했다 — [상세](handoff/DB결함.md)
- [거래명세표] **보류** — 슬라이드36·라벨모달은 `stash@{0}`에 보관. 수량 의미와 라벨 보호 정책 결정 후 재개 — [상세](handoff/거래명세표.md)
- [기타] **대기 항목 모음** — 도면팝업 실화면 검증, 로컬 설정 복구 경위, 직원 목록 캐시 개선 — [상세](handoff/기타.md)

## 운영 문서

- Codex 진행 안내: [handoff/Codex진행안내.md](handoff/Codex진행안내.md)
- 세컨브레인 구조: [docs/SECOND_BRAIN.md](docs/SECOND_BRAIN.md)
- 완료 이력: [logs/HANDOFF_ARCHIVE.md](logs/HANDOFF_ARCHIVE.md)
