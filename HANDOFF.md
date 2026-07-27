# HANDOFF — 활성 작업 인덱스

_최종 갱신: 2026-07-27_

이 파일은 현재 작업을 찾기 위한 인덱스다. 세부 경위는 연결된 `handoff/` 문서, 완료 이력과 증적은 `logs/`에서 확인한다. 오래된 git·서버·DB 상태는 기록을 믿지 말고 다시 측정한다.

## 현재 환경

- 하네스 루트: `D:\harness_framework` (과거 `E:\harness_framework`, `D:\tomes\harness-framework` 기록은 현재 루트로 재해석)
- JDK 21은 `D:\Tool\jdk-21\jdk-21`이며 사용자 `JAVA_HOME`과 `Path` 등록 완료.
- Python 3.14.6과 `py` 런처, `%테스트` 요구 패키지·pytest·Playwright Chromium 설치 완료. Python·Scripts·Launcher 경로는 사용자 `Path`에 등록했다.
- `%클라우드` 커밋은 사용자 몫이며 브랜치·dirty 상태는 작업 시작 시 직접 확인한다.
- DailyWorklog는 평일 17:30 예약 작업으로 복구했다. 이 PC에는 `NOTION_TOKEN`이 없어 로컬 JSON만 생성하며 백필 절차는 `logs/notion_이관대기.md`를 따른다.
- 공통 DB 주의: SYSTEM_ID로 테넌트를 확인하고 빈 문자열은 `IS NOT NULL AND LENGTH(...) > 0`으로 판정한다.

## 활성 작업

- [업무PC복귀인계] **부분 반영 / 미전달 자료·인증 대기** — 하네스·가공확정 제품 파일 2개와 개발 런타임·경로·DailyWorklog 복구 완료. 하네스 59 PASS, 제품 빌드 PASS, `%테스트` 191 PASS/기존 계획 불일치 3 FAIL. 제품 HEAD `c0ac256`, 검증 증적, 개인 Codex 알림·권한 원본과 GitHub 인증은 대기 — [상세](handoff/업무PC복귀인계.md)
- [가공확정] **KAN-63 / 진행 중** — 화면 비활성 및 잠긴 파트 재확정 검증 완료. 다음은 KAN-6 → KAN-35 → KAN-38 구현, `%클라우드` 수정분 커밋과 배포 시 운영 메뉴 반영 — [상세](handoff/가공확정.md)
- [단가검토] **사용자 결정 대기** — 단가입력 개편 검증 완료. 배송비 컬럼명·견적→주문 복사 여부 결정 후 DDL 및 기록조회 후속 작업 — [상세](handoff/단가검토.md)
- [DB결함] **구현 완료·독립 검토 대기** — 시드, 수동입력 차단, CONTROL_NUM 보정, 프로시저 동시성 가드 적용. 고위험 DB 변경 검토 상태는 상세 문서 기준 — [상세](handoff/DB결함.md)
- [거래명세표] **보류** — 슬라이드36·라벨모달은 `stash@{0}`에 보관. 수량 의미와 라벨 보호 정책 결정 후 재개 — [상세](handoff/거래명세표.md)
- [기타] **대기 항목 모음** — 도면팝업 실화면 검증, 로컬 설정 복구 경위, 직원 목록 캐시 개선 — [상세](handoff/기타.md)

## 운영 문서

- Codex 진행 안내: [handoff/Codex진행안내.md](handoff/Codex진행안내.md)
- 세컨브레인 구조: [docs/SECOND_BRAIN.md](docs/SECOND_BRAIN.md)
- 완료 이력: [logs/HANDOFF_ARCHIVE.md](logs/HANDOFF_ARCHIVE.md)
