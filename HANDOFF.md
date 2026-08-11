# HANDOFF — 활성 작업 인덱스

_최종 갱신: 2026-08-11_

이 파일은 현재 작업을 찾기 위한 인덱스다. 운영 규칙은 `AGENTS.md`, 제품·안전 규칙은 `PROJECT_RULES.md`, 조건부 절차는 `docs/processes/`, 세부 경위는 연결된 `handoff/`, 완료 이력과 증적은 `logs/`에서 확인한다. 오래된 git·서버·DB 상태는 기록을 믿지 말고 다시 측정한다.

## 현재 환경

- 사용자 환경 맞춤 판단과 현재 PC·도구·작업 성향의 정본은 [`context/README.md`](context/README.md)에서 찾는다.
- 경로 정본은 `PATHS.md`, 작업별 변동 상태와 다음 행동은 아래 활성 작업과 연결된 handoff에서 확인한다. 오래된 git·프로세스·서버·DB 상태는 다시 측정한다.

## 활성 작업

- [노션작업일지자동화] **과거 누락분 백필·예약 경로 복구 완료 / 8/4 최종본 로컬 준비·인증 후 전송 대기** — 오전 백필은 실제 Notion 재조회까지 확인했다. 8/4 최종 작업 4건은 17:41 로컬 JSON으로 다시 생성해 이관 대기 목록에 보존했으며, 공식 Integration 토큰·DB ID가 없어 외부 전송은 하지 않았다. 사용자 계획에 따라 8/5 인증 복구 후 `--from-json` 전송과 재조회 검증을 진행한다 — [상세](handoff/토큰절감.md)
- [SiteAdmin_재질표면처리매핑] **환경별 매핑 조회·D03 REF_CD 후퇴 제거·대분류 상속 구현 커밋 완료 / refCd 분기 가독성 변경 미커밋·최신 v3 인증 세션 확인 대기** — 원격 `feature-materialmap-0803`의 `43690a0`은 코드 5파일 `+48/-10`이며, D03은 `MATERIAL_TYPE_CDS`, 다른 기준코드는 기존 `REF_CD`를 사용한다. 2026-08-07에는 별도 worktree에서 동일 함수 3곳을 기본 `refCd`·D03 `mapCd` 명시 분기로 정리해 문법·분기 단위 검증·전체 빌드를 통과했다. 재현 SQL은 원격 커밋에 포함되지 않은 미추적 파일이라 별도 결정이 필요하다 — [상세](handoff/SiteAdmin_재질표면처리매핑.md)
- [Codex주에이전트전환] **현재 PC `work` 프로필·핵심 개발·테스트 기능 호환 완료 / GUI 도구 데이터 이관 대기** — 저장소 밖 로컬 마커와 `scripts/pc_profile.ps1`로 PC를 구분하며, `%클라우드`의 Claude 로컬 설정과 개발 실행 배치는 기능 stash에서 제외해 작업트리에 유지한다. 프로필 테스트 4 PASS, 하네스 76 PASS이며 기존 개발·테스트 기능과 Git 원격·Gradle도 정상이다. VS Code·Codex 개인 홈·SourceTree·DBeaver·Git 전역 데이터 이관은 별도 대기 — [상세](handoff/Codex주에이전트전환.md)
- [업무PC복귀인계] **주요 복구·Codex 훅·실화면 재검증 완료 / 개발 DB TLS 결정·미전달 원본 대기·POP 실기기 보류** — 개발 런타임·경로·Windows `workspace` 샌드박스 복구와 Codex 훅 상태 전이 검증을 완료했다. 개발 DB 서버는 TLS가 비활성이고 Connector/J도 기본 비SSL 연결이며, 로컬 MariaDB 설정에는 존재하지 않는 `E:` 플러그인 경로가 남아 있어 적용 방침 결정이 필요하다. POP 바코드 스캐너 실기기 검증은 2026-07-29 사용자 결정으로 보류했다. 하네스 60 PASS, 제품 빌드 PASS, `%테스트` 191 PASS/기존 계획 불일치 3 FAIL — [상세](handoff/업무PC복귀인계.md)
- [%테스트현대화] **전체 205 PASS·OSR-173 실동작 PASS / GWS OAuth 인증 대기** — 결정론 우선 정책에 맞춰 자동 Stage4 heal을 제거하고 batch를 최대 20으로 제한했으며, 선택적 AI 설정·제품 경로·GWS 실행 경로를 중앙화했다. OSR-173은 현재 제품의 실제 SIZE_TYPE 옵션과 W/H/T/D/L 표시 계약으로 Stage4·시드·Sheet 쓰기 없이 PASS했다. GWS 0.22.5는 D:에 설치했지만 OAuth client/login이 없어 최신 Sheet 확인과 row 899 menu2 불일치 정정은 대기한다 — [상세](handoff/테스트현대화.md)
- [가공확정] **KAN-63 / KAN-6 구현·빌드 완료·통합 stash 보관, KAN-35 DB 반영 완료, KAN-38 화면·POP 실기기 검증 보류** — 재확정 예외 2파일과 작업상세 표시 제거 5파일을 사용자 요청에 따라 통합 stash 객체 `d2c8a638e1f508bd4672b47fc191245061c2c02b`로 분리해 작업트리에서 제거했다. 기존 두 독립 stash도 안전 복사본으로 유지한다 — [상세](handoff/가공확정.md)
- [단가검토] **변경 3파일 독립 stash 보관 / 사용자 결정 대기** — 단가입력 개편과 기록조회 변경을 별도 stash로 분리했다. 배송비 컬럼명·견적→주문 복사 여부 결정 후 DDL 및 후속 작업을 재개한다 — [상세](handoff/단가검토.md)
- [DB결함] **실동작 6 PASS·0 FAIL / 기능 검증 완료** — 최초 신규 주문 FAIL은 시퀀스나 제품 변경이 아니라 8/7 Codex 테스트 잔존 12건의 고정 `ORDER_SEQ` 충돌이었다. 해당 주문·작업·검사·가공 참조만 정리한 뒤 단건과 동시 2건을 재실행해 `ORDER_SEQ`·접수번호 유일성과 락 해제, 테스트 잔존 0건을 확인했다. 제품 변경은 미커밋 상태다 — [상세](handoff/DB결함.md)
- [거래명세표] **보류** — 슬라이드36·라벨모달은 `stash@{0}`에 보관. 수량 의미와 라벨 보호 정책 결정 후 재개 — [상세](handoff/거래명세표.md)
- [테넌트기준코드사용여부] **개발 DB 저장 테이블 생성 완료 / V2 화면·저장 API·테넌트 한정 캐시 무효화 연결 대기** — `TBL_TENANT_CODE_USE`에 테넌트별 D01·D03 `USE_YN`을 분리 저장하도록 복합 PK와 CHECK를 적용했고 초기 0건·트랜잭션 롤백 0건을 확인했다. 재현 SQL은 `%클라우드` `docs/db/20260811_tenant_code_use.sql`에 있다 — [상세](handoff/SiteAdmin_재질표면처리매핑.md)
- [기타] **빌드·테스트 설정 분리 stash 완료 / 대기 항목 모음** — `%클라우드`의 JUnit Platform 활성화 변경은 stash 객체 `b75b9c07d25904b604ff6b4980860c28287b7816`로 분리했다. 도면팝업 실화면 검증, 로컬 설정 복구 경위, 직원 목록 캐시 개선은 대기 중이다 — [상세](handoff/기타.md)

## 운영 문서

- Codex 진행 안내: [handoff/Codex진행안내.md](handoff/Codex진행안내.md)
- 세컨브레인 구조: [docs/SECOND_BRAIN.md](docs/SECOND_BRAIN.md)
- 완료 이력: [logs/HANDOFF_ARCHIVE.md](logs/HANDOFF_ARCHIVE.md)
