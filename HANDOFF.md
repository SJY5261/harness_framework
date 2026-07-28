# HANDOFF — 활성 작업 인덱스

_최종 갱신: 2026-07-28_

이 파일은 현재 작업을 찾기 위한 인덱스다. 세부 경위는 연결된 `handoff/` 문서, 완료 이력과 증적은 `logs/`에서 확인한다. 오래된 git·서버·DB 상태는 기록을 믿지 말고 다시 측정한다.

## 현재 환경

- 하네스 루트: `D:\harness_framework` (과거 `E:\harness_framework`, `D:\tomes\harness-framework` 기록은 현재 루트로 재해석)
- JDK 21은 `D:\Tool\jdk-21\jdk-21`이며 사용자 `JAVA_HOME`과 `Path` 등록 완료.
- Python 3.14.6과 `py` 런처, `%테스트` 요구 패키지·pytest·Playwright Chromium 설치 완료. Python·Scripts·Launcher 경로는 사용자 `Path`에 등록했고 `PYTHONUTF8=1`을 복구했다.
- DBeaver 25.0.1에 `Tomes-Cloud` MariaDB 연결과 드라이버를 복구했고, 비밀번호는 DBeaver 보안 저장소에만 저장했다.
- 실제 실행·개발 설정은 `D:\harness_framework`, `D:\Tool`, `D:\LOGS` 기준으로 통일했다. 환경 변수, Git, 편집기, 예약 작업, 바로가기, 서비스에는 옛 `E:` 프로젝트 경로가 없다. 과거 문서·로그의 `E:`는 이력으로 보존한다.
- `%클라우드` 커밋은 사용자 몫이며 브랜치·dirty 상태는 작업 시작 시 직접 확인한다.
- DailyWorklog는 평일 17:30 예약 작업으로 복구했다. 이 PC에는 `NOTION_TOKEN`이 없어 로컬 JSON만 생성하며 백필 절차는 `logs/notion_이관대기.md`를 따른다.
- Codex Windows `workspace` 샌드박스는 포맷 전 SID가 남은 작업공간 ACL을 현재 사용자·샌드박스 그룹 기준으로 복구했다. Python 공용 등록, 샌드박스 전용 Temp와 Gradle 캐시를 개인 Codex 설정에 연결했고 반복 초기화·하네스 59 PASS·제품 빌드 PASS를 재확인했다.
- Codex 하네스 공용 규칙은 새 실패·경고·잠재 결함·회귀·보안 위험을 결과에 명시하되, 현재 범위 안의 되돌릴 수 있고 안전한 해결은 자동 적용한다. 데이터 손실·권한/공개 확대·비가역 변경·큰 호환성 분기·요구 결과 변경처럼 중요한 결정만 사용자에게 확인한다.
- 공통 DB 주의: SYSTEM_ID로 테넌트를 확인하고 빈 문자열은 `IS NOT NULL AND LENGTH(...) > 0`으로 판정한다.

## 활성 작업

- [업무PC복귀인계] **주요 복구·D 드라이브 경로·Codex 샌드박스·실화면 재검증 완료 / 미전달 원본·POP 실기기 대기** — GitHub 인증과 하네스 push, 제품 HEAD `c0ac256` 동기화, 가공확정 제품 파일 2개, 개발 런타임·경로·DailyWorklog와 Windows `workspace` 샌드박스 복구 완료. 업무 PC에서 개발 서버와 재구성한 실화면 4개 케이스도 통과했다. 샌드박스 내부 하네스 59 PASS, 제품 빌드 PASS, `%테스트` 191 PASS/기존 계획 불일치 3 FAIL. 개인 PC의 원본 증적·Codex 알림 원본과 POP 스캐너 실기기 검증은 대기 — [상세](handoff/업무PC복귀인계.md)
- [가공확정] **KAN-63 / KAN-6 구현·빌드 완료, KAN-35 DB 반영 완료, KAN-38 화면 확정 전 보류** — 재확정 예외를 작업트리에 복원하고 작업상세정보의 가공확정 일시·진행상태 표시를 제거했다. 제조원가 분석 메뉴 8행은 영구 백업 후 숨김 처리·검증·COMMIT 완료. 작업지시 현황추적 화면은 사용자 결정에 따라 정확한 화면 사양이 확정될 때까지 구현하지 않음 — [상세](handoff/가공확정.md)
- [단가검토] **사용자 결정 대기** — 단가입력 개편 검증 완료. 배송비 컬럼명·견적→주문 복사 여부 결정 후 DDL 및 기록조회 후속 작업 — [상세](handoff/단가검토.md)
- [DB결함] **구현·제품 브랜치 push·PR 리뷰 3종 완료 / 독립 검토 대기** — 시드, 수동입력 차단, CONTROL_NUM 보정, 프로시저 동시성 가드 적용. `%클라우드` 커밋 `88bf7dc`를 `origin/feature-control-0713`에 push했고, `Desktop\PR\[07.28 DB결함 수정 리뷰]`에 MD·HTML·Codex Sites URL을 모두 생성했다. Sites 버전 7은 현재 사용자 1명만 허용한 상태로 배포 완료. 고위험 DB 변경 검토 상태는 상세 문서 기준 — [상세](handoff/DB결함.md)
- [거래명세표] **보류** — 슬라이드36·라벨모달은 `stash@{0}`에 보관. 수량 의미와 라벨 보호 정책 결정 후 재개 — [상세](handoff/거래명세표.md)
- [기타] **대기 항목 모음** — 도면팝업 실화면 검증, 로컬 설정 복구 경위, 직원 목록 캐시 개선 — [상세](handoff/기타.md)

## 운영 문서

- Codex 진행 안내: [handoff/Codex진행안내.md](handoff/Codex진행안내.md)
- 세컨브레인 구조: [docs/SECOND_BRAIN.md](docs/SECOND_BRAIN.md)
- 완료 이력: [logs/HANDOFF_ARCHIVE.md](logs/HANDOFF_ARCHIVE.md)
