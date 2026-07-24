# HANDOFF — 다음 세션 인수인계 (인덱스)

_최종 갱신: 2026-07-14 (작업별 분리 개편)_

> 이 파일은 인덱스만 유지한다. 작업별 상세 내용은 `handoff/<작업주제>.md`에, 종결 이력은 `logs/HANDOFF_ARCHIVE.md`에 있다.
> 갱신 방법: 공통 상태와 작업별 한 줄 엔트리는 여기서, 상세 진행 내용은 해당 handoff/ 파일에서 수정한다.

## 공통 상태 (2026-07-15 실측)
- %클라우드 체크아웃: **Danga-order** = main = origin/main = `aa63bb2` (7/15 사용자 지시로 main 풀 56커밋 + Danga-order fast-forward 병합 완료. 7/15 사용자가 직접 push 완료 — origin/Danga-order도 aa63bb2 일치, ahead 0). ★세션 git의 GitHub 자격증명은 만료 상태(GCM 브라우저 재인증 필요) — 세션에서 fetch/push 시 멈추므로 원격 작업은 사용자에게 요청할 것. 브랜치 전환 이력이 잦았음 — 커밋 시 브랜치·파일 분리 주의.
- 미커밋 7파일 (커밋은 전적으로 사용자 몫, 말없이 커밋 금지):
  - `OrderServiceImpl.java` + `sqlMaps/order.xml` = DB결함 ⓐⓑⓓ+ⓒA안 수정분 (7/15 stash@{0}에서 충돌 없이 복원, build 통과) + 7/16 스탭2 자동채번 강제(OrderServiceImpl 4개 메서드)
  - `attr/tabs/bottom2.jsp` = DB결함 스탭2 사이트마스터 N 옵션 제거
  - `EstimateServiceImpl.java` = DB결함 ⓐ(견적→주문 전환 채번 락)
  - `v1/estmateCalculate.xml` + `estimate_unit_price_calculate.jsp` + `estimate_unit_price_calculate.css` = 단가검토 건
  - untracked: `.claude/`, `artifacts/`(단가검토 테이블구성안 MD), `shell/runDev.local.bat`(사용자 재기동 스크립트 — 8081 자동 재기동 사례 있음)
- 8081 dev 서버: 7/16 오후 재기동 (`logs/bootrun_8081_0716_step2.log`) — 스탭2 수정 + 7/15 풀 56커밋 반영됨.
- 재개 시 우선순위 후보: ①[DB결함] %테스트 시드 upsert 교정(계획 순서상 다음) ②수동입력 차단 정책 구현(사용자 결정됨, 서버 강제+사이트마스터 정리 — 상세 handoff/DB결함.md 참조 대화 7/14) ③[단가검토] 단가입력 1-3은 사용자 통보 대기. 커밋 정리는 사용자 몫.
- **stash 1건 (2026-07-20 재구성, 사용자 승인)**: `stash@{0}` = 거래명세표 슬라이드36+라벨모달(transaction_statement.jsp 단독, base 3b52126 — 현 HEAD 기준이라 바로 apply 가능). 구 stash 2건(7/15 DB결함, 7/8 4파일)은 내용이 워킹트리/커밋에 있음을 확인 후 drop, 백업 패치 `logs/stash_backup_2026-07-20_*.patch` 2개 저장 — 경위 상세: handoff/거래명세표.md.
- 공통 상태 갱신(7/20 실측): %클라우드 HEAD가 `3b52126`(publishing_2606 머지)로 진전됨(위 9행의 aa63bb2 스냅샷은 stale). 차트 파일(main.jsp·main.xml·v1/main.xml)은 9f49184 이후 변경 없음 확인.
- `application-local.yml`은 7/8 유실 후 복구본(6c37383~1 + JSP 핫리로드 키 교정) — 이상 동작 시 이 파일 먼저 의심.
- 검증 공통 주의: 이 MariaDB는 빈 문자열 비교가 NULL 평가(`!=''` 금지 → IS NOT NULL+LENGTH()>0) / pqGrid 렌더 판정은 'Loading...' 텍스트 말고 :visible로 / 테넌트 SYSTEM_ID='SMD'(USER_ID로 테넌트 찾지 말 것).
- ★예약작업 DailyWorklog(노션 작업일지, 평일 17:30) **7/15 비활성화됨**(BIOS 업데이트 간섭 방지, 사용자 지시). 7/16 17:30 전에 `Enable-ScheduledTask -TaskName DailyWorklog`로 재활성화 필요.

## 작업별 현황 (상세는 각 파일)
- [단가검토] 스탭1-1(기록조회 최근 3년)·스탭2 착수분(기록조회 조회전용 모드, 7/14 21 PASS)에 이어 **7/16 단가입력 개편 완료(15 PASS)** — 수량적용가/적용금액계 삭제, 기타추가=계산 구성요소(기존 UNIT_ETC_AMT로 저장까지 동작), 배송비=마지막 1회 가산+총계(배송비 포함) 신설(화면 전용, 저장은 DDL 대기). 미커밋 3파일. 남은 결정=배송비 컬럼명·견적→주문 복사 여부(통보 전 DDL 금지), 기록조회 데이터 표시는 다음 단계 — 상세: handoff/단가검토.md
- [DB결함] **계획 스탭1~4 완료**(코드 미커밋): 시드 교정·수동입력 차단·`CONTROL_NUM` 22건 백필+NOT NULL에 이어 `smd.SP_CONTROL_BATCH` 주문행 잠금+살아 있는 매핑 SIGNAL+NOT EXISTS 가드 적용. 동시성 차단·정상 주문·S10R40 회귀 PASS, SMD 실제 주문 이중매핑 0·테스트 잔재 0. DB/프로시저 백업 유지. Claude fallback 구현분은 `peer_review_pending` — 상세: handoff/DB결함.md
- [차트] 메인 가동율 V1 쿼리 적용은 커밋됨(9f49184)·사용자 "이 건 마무리" 확정 → 아카이브로 이동. 잔존 표시/구조 이슈(막대 뜸·SQL의 HTML 생성 등)는 보류 목록으로 유지 — 상세: handoff/차트.md
- [거래명세표] 슬라이드36+라벨모달 구현분은 **7/20 재구성된 stash@{0}**(transaction_statement.jsp 단독, base 3b52126 — 바로 apply 가능)에 보관(+백업 패치 2종). 재개 시 남은 결정(수량 의미·PACKING_CNT 이원화·출하 라벨 보호 등)부터 — 상세: handoff/거래명세표.md
- [기타] 도면팝업 CSS 분리는 커밋·머지됨(7c01d3f, PR#26 — 실화면 검증만 미실시) / application-local.yml 복구 경위 / getCompanyStaffList 캐시 개선(사용자 트리거 대기) — 상세: handoff/기타.md
- [토큰절감] 7/20 오전 토큰 급소진 원인 분석 완료 → daily_worklog.py 절감 개선(--model sonnet 기본 등) 완료 → 노션 백필도 7/20 오늘자까지 실전송 캐치업 완료(7/17 무활동 확인). 다음: CLAUDE.md 다이어트 승인 대기 — 상세: handoff/토큰절감.md
- [Claude????] ??? ?? ???(?? ????? ?? ?????? ???context???) + ??? ?? ?? ?? ????? ?? ? ??: handoff/Claude????.md
- [Codex연계] Claude x Codex 협업 체계 — 7/20 최종 설계 완료, 7/21 peer_review 완료(4건 결함 발견) + 정식 3라운드 토론(블라인드 Round 1 최초 실증)으로 4건 전부 합의·구현 완료(CLAUDE.md 3건, AGENTS.md 1건) — 상세: handoff/Codex연계.md, 정본: discussion/2026-07-21_협업체계_취약점보완.md

## 규칙 변경 공지
- 2026-07-13 CLAUDE.md에 토큰 절약 규칙 신설됨 — 작업 시 참조.
- 2026-07-15 answer_review_gate.py v2 + answer-reviewer 정의 보강(합성 트랜스크립트 14/14 검증). 게이트가 엄격해짐: 검토 호출은 Agent subagent_type만 인정(파일 Read로는 통과 불가, SendMessage 이어쓰기 미인정), 옵트아웃 마커는 최종 메시지에 전체 문구 그대로, 검토 시 최종 메시지 배너 필수, 턴당 차단 2회 상한, 옵트아웃은 logs/answer_review_optouts.log에 기록. 리뷰어 의뢰 시 ①원 질문 전문 ②초안 전체 ③참조 파일 목록 필수 전달.
