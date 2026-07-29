# DB결함 — 역사 보존본

_2026-07-14 HANDOFF.md 작업별 분리로 생성. 범위: 결함ⓐ채번·ⓑ이중매핑·ⓒ복사컬럼 드리프트·ⓓ삭제 미전파, 작업관리 DB 문제 재분류, 거래명세표 중복행 근원 분석. 섹션 최신순, 원문 그대로 이동._

## [2026-07-28] 사용자 변경 범위 PR 리뷰 MD·HTML 정리
- 사용자 지정 경로 `C:\Users\User\Desktop\PR\[07.28 DB결함 수정 리뷰]`의 MD 정본과 자체완결 HTML에는 사용자가 직접 변경한 `CONTROL_NUM` 변경 전후, 백업·백필·`NOT NULL` DDL, `SP_CONTROL_BATCH` 실제 가드 블록, 사후 검증·선택적 복구 SQL만 포함했다.
- 7/20 단일 실행 SQL 파일은 저장소에 미보존임을 명시하고, 백업·백필은 작업 기록 기반 최종 상태 재현 SQL, 컬럼 정의·프로시저 가드는 7/28 라이브 `SHOW FULL COLUMNS`·`SHOW CREATE PROCEDURE` 재확인본으로 출처를 구분했다. 현재 컬럼 nullable=`NO`, 백업 22행.
- 외부 협력자의 KAN-64/STP 변경과 다른 후속 변경명은 리뷰에서 제외했다. 프로시저 복구는 범위 밖 변경을 보존하도록 백업 전체 덮어쓰기 대신 이번 잠금·오류·`NOT EXISTS` 블록만 선택적으로 제거한다.
- 작업 폴더의 `아티팩트.url`을 제거해 MD·HTML 정확히 2개만 남겼고, 두 파일에 사용자 변경만 포함됨·`<details>` 짝·UTF-8 BOM 없음·HTML 문서 셸을 검증했다. SHA-256: MD `84B05CF9...8E06B`, HTML `78DAA5EB...73093`.
- 기존 원격 Sites는 삭제하지 않았지만 이번 내용은 재게시하지 않았으며, 앞으로도 웹 게시를 별도 요청하지 않는 한 MD·HTML 2개만 생성한다.
- 규칙 적용 전 단일 파일 `C:\Users\User\Desktop\PR\DB결함_수정_PR_리뷰.md`는 비교·복구용으로 보존하며 삭제·덮어쓰기하지 않음.

## [2026-07-20] 스탭4 — SP_CONTROL_BATCH 동시 이중매핑 DB 가드 완료 (smd만)
- 사용자 승인 후 기존 프로시저를 `SP_CONTROL_BATCH_BAK_260720`으로 완전 복제·원본 대조하고, `smd.SP_CONTROL_BATCH`만 교체. DEFINER=`tomes`@`%`, 2개 파라미터, 기존 스테이징 삭제, 내부 COMMIT 없음 보존.
- 추가 방어 3종: ①비재고(`S10R40` 제외) 원본 `TBL_ORDER` 행을 `FOR UPDATE`로 잠가 동시 발행 직렬화 ②작업지시 생성 전에 살아 있는 컨트롤 매핑 재검사, 존재 시 `SIGNAL SQLSTATE '45000' / ORDER_ALREADY_MAPPED_TO_ALIVE_CONTROL`로 전체 트랜잭션 중단 ③매핑 INSERT에도 살아 있는 컨트롤 기준 `NOT EXISTS` 백스톱. 따라서 조용한 skip·빈 유령 컨트롤을 만들지 않고 실패 전체가 롤백됨.
- 배포 과정 안전 중단 3회: 원문 탭 혼용과 동일 조건 2곳 때문에 기계 앵커가 유일하지 않아 교체 전 중단. 원본은 세 번 모두 미변경, 백업 동일성 재확인 후 `TBL_CONTROL_PART_ORDER` INSERT 구간을 구조적으로 한정해 최종 교체 성공.
- 동시성 실증 PASS: conn1이 주문 27087을 `FOR UPDATE`로 잠근 동안 conn2 프로시저가 1.506초 대기 → 잠금 해제 후 errno 1644/SQLSTATE 45000으로 차단. 테스트 스테이징·컨트롤 잔재 0.
- 정상 회귀 PASS(모두 트랜잭션 롤백): 미매핑 QA 주문 92008226은 컨트롤/부품/매핑/컨트롤바코드/출고바코드 각 정상 생성 후 잔재 0. `S10R40`은 신규 ORDER_SEQ 매핑 정상 생성 후 잔재 0.
- 최종 무결성: SMD 실제 주문 기준 살아 있는 이중 매핑 0, TEST-SP 표식 잔재 0. 매핑 없는 활성 컨트롤은 사전 분석에 있던 기존 16031(`AUTO-16031`) 1건 그대로. 첫 전역 쿼리는 테넌트·실주문 조인 없이 재고용 독립 ORDER_SEQ 숫자 충돌까지 세어 8,240건으로 오측정했으며, `TBL_ORDER`+동일 SYSTEM_ID 범위로 교정해 0건 확인.
- `peer_review_pending`: Claude 토큰 소진 fallback 중 Codex 단독 구현. Claude 복구 후 프로시저 diff와 위 검증 기록만 교차 리뷰.
- 결론: 계획된 스탭1~4 완료. 백업 `BAK_TBL_CONTROL_CTRLNUM_260720`(22행)과 `SP_CONTROL_BATCH_BAK_260720` 유지. 별도 보류 과제(TBL_OUT_BARCODE 비유니크 인덱스, 기존 16031 정리, 과거 드리프트 데이터 보정)는 이번 범위 밖.
- PR 리뷰용 통합 아티팩트 작성: `C:\Users\USER\Desktop\PR리뷰\[07.20 DB결함 수정 리뷰].md` — 미커밋 DB결함 5파일과 SMD DB 반영의 원인·수정·검증·개선·복구 지점을 저장소별 커밋 분리 경계와 함께 정리.

## [2026-07-20] 스탭3 2단계 — CONTROL_NUM 백필 COMMIT + NOT NULL DDL 완료
- 사용자 승인 후 `smd`만 실행. 선행조건(백업 22행/원본 NULL 22행/CONTROL_SEQ 일치 22행) 재검증 후 백필 22행 COMMIT: 활성은 `LEGACY-<CONTROL_SEQ>`, 소프트 삭제는 `DEL_NULL_<CONTROL_SEQ>`.
- `TBL_CONTROL.CONTROL_NUM`을 기존 정의를 보존해 `varchar(30) CHARACTER SET utf8mb3 COLLATE utf8mb3_general_ci NOT NULL COMMENT '작업지시번호'`로 변경.
- 최종 검증 PASS: NULL 0건, nullable=NO, 길이 30, 문자셋/collation 동일, 백업 `BAK_TBL_CONTROL_CTRLNUM_260720` 22행 유지. 샘플: 17027=`DEL_NULL_17027`, 91000001=`DEL_NULL_91000001`, 91000007=`LEGACY-91000007`.
- 실행 중 PowerShell→Python 표준입력 인코딩으로 COMMENT 리터럴이 `??????`로 1회 손상됨(HEX `3F`×6). 즉시 ASCII 유니코드 이스케이프로 동일 ALTER를 재실행해 원문 복구, 최종 HEX `EC9E91EC9785ECA780EC8B9CEBB288ED98B8` 일치 확인. 데이터·제약 영향 없음.
- 다음: 스탭4 SP_CONTROL_BATCH NOT EXISTS 가드 + 조용한 skip/빈 컨트롤 방지 구체안 승인 및 구현.

## [2026-07-20] 스탭3 1단계 — CONTROL_NUM 백업 + 롤백 리허설 완료
- 현재 `smd.TBL_CONTROL.CONTROL_NUM IS NULL` 22건 재확인: 활성 1건(91000007), 소프트 삭제 21건. 컬럼은 `varchar(30)`, utf8mb3_general_ci, nullable.
- before-image 백업 테이블 `smd.BAK_TBL_CONTROL_CTRLNUM_260720` 생성, NULL 대상 22행 보존·원본과 CONTROL_SEQ 기준 22/22 일치 확인.
- 트랜잭션 리허설: 활성은 `LEGACY-<CONTROL_SEQ>`, 삭제행은 `DEL_NULL_<CONTROL_SEQ>`로 UPDATE. 22행 영향, NULL 0, 백필값 22개 모두 고유, 최대 길이 17/30으로 PASS.
- 리허설 UPDATE는 `ROLLBACK` 완료: 원본 NULL 22건 그대로, 백업 22행 유지. 첫 시도는 조회 트랜잭션이 열린 상태에서 `start_transaction()`을 호출해 UPDATE 전 중단됐고, 명시적 commit 후 트랜잭션 시작으로 교정해 재실행 성공.
- 다음: 사용자 2단계 승인 후 동일 UPDATE를 COMMIT하고 기존 문자셋·collation·comment를 보존한 `CONTROL_NUM varchar(30) NOT NULL` ALTER 및 최종 검증. 스탭4 SP 가드는 그 뒤 별도 승인.

## [2026-07-20] 스탭4 사전 영향분석 — SP_CONTROL_BATCH 소비처 전수 + 3스키마 본문 실측 (조회만, 코드 무변경 — answer-reviewer 검증 OK)
- **소비처 전수 확정**: 앱 호출부는 OrderServiceImpl 3곳뿐(:160 createNewStockControl / :1913 createNewControl / :2085 createNewControlForOrder — 7/20 워킹트리 기준, call_procedure.xml:7 경유 2인자 호출). DB 내부(다른 루틴·이벤트·트리거)에서 SP_CONTROL_BATCH 참조 0건(information_schema 3스키마 실측). 3곳 모두 ⓑ 사전검사 배선 + SP 후 무조건 deleteControlExcel, **발행 건수 검증 없음**.
- **★스키마 실태 교정(7/15 "3스키마 복제" 서술 정정)**: smd↔smd2 SP는 사실상 동일(시그니처 IN 표기만 차이). **jet은 다른 버전** — 1파라미터, CONTROL_NUM 커서, CONTROL_NUM NOT EXISTS 가드 이미 활성, 컬럼 상이(LATHE_YN/INSERT_ID), jet.TBL_SYSTEM 자체가 없음 → 현 앱이 서비스 불가(추론: 구버전/별도 앱 스키마). **스탭4 DDL 대상 = smd만 (7/20 사용자 확정 "DB는 SMD만 사용, 다른 건 신경쓰지 마") — smd2·jet 제외**. 트리거 3종(TRIG_INSERT/UPDATE/DELETE_TBL_CONTROL_PART_ORDER)은 3스키마 모두 실존(7/15 서술 유지).
- smd2는 TBL_SYSTEM 0행·스테이징 0행(활성 테넌트 없음). dev 데이터소스는 smd 고정(application-local.yml:28). smd 활성 테넌트 8개 전부 AUTO_NUM_CREATE_YN='Y'(BASIC NULL).
- **긍정 영향**: 레이스 창(50~100ms) DB 레벨 완전 차단 / 트리거 연쇄 정합(skip 시 _MAIN 미생성) / OUT_BARCODE도 매핑 조인이라 정합 / 성능 무해(IDX_CONTROL_PART_ORDER_ORDER_SEQ 실존·매핑 1.8만행, 테넌트 스케일 안전).
- **리스크(설계 반영 필수 4가지)**: ①조용한 skip — 3곳 전부 건수 검증 없어 사용자는 성공 인식·주문 미발행 → SP 후 매핑 건수 검증 병행 ②빈 유령 컨트롤 — 전량 skip 시 TBL_CONTROL+PART+CONTROL_BARCODE는 생성되는데 작업지시관리 V1 목록이 매핑 INNER JOIN(v1/order.xml:419)이라 화면 미노출·UI 삭제 불가(결번 1개, 중복은 아님) → 컨트롤 생성 단계 가드 or 말미 정리 ③가드 스코프 = 살아있는 TBL_CONTROL(DEL_YN='N') 조인 필수(죽은 매핑 잔존) ④S10R40 제외 필수(스톡 스테이징 createControlExcel_stock order.xml:2993~에 ORDER_SEQ 컬럼 자체 없음, NEXTVAL 신규 채번). 기타: DEFINER=tomes@% 유지 주의, SP 내부 커밋 없음 불변.
- 라이브 DB 수치(참조 0건·테넌트 8행·인덱스·18124행)는 세션 스크립트 실측(scratchpad check_sp_refs.py 등, 세션 1dc0705f). SP 본문 3스키마 덤프 = scratchpad sp_control_batch_bodies.txt.
- **[같은 날 후속] 리스크 성격 분류(사용자 질문, answer-reviewer 검증 OK)**: 부정영향의 뿌리는 전부 기존 구조 결함 — ①발행 무검증+스테이징 무조건 삭제는 기존(SP 매핑 INSERT에 `A.ORDER_QTY IS NOT NULL` 필터가 이미 있어 오늘도 조용한 skip 가능) ②유령 컨트롤 구조도 기존(살아있는 SMD 컨트롤 683건 중 매핑 0건 1건 실존 — 16031 'AUTO-16031' 4/30, 테스트 산물 추정) ③죽은 매핑 잔존은 결함ⓓ 계열 기존. 가드는 새 결함을 만들지 않고 "skip 동작"을 도입해 기존 결함들을 발화시키는 방아쇠 — 보완 없이 넣으면 이중매핑이 미발행+유령행으로 형태만 바뀜. S10R40 제외·DEFINER·트랜잭션은 결함 아닌 설계/작업 조건.
- 다음: 이 분석을 반영한 스탭4 구체안(가드 SQL + 건수 검증 + 빈 컨트롤 처리) 작성 → 사용자 승인 후 DDL. 스탭3(NULL 백필+NOT NULL DDL)은 여전히 선행 대기 중.

## [2026-07-16 오후] 스탭2 수동입력 차단(자동채번 서버 강제) — 완료 (%클라우드 2파일, 미커밋, 실검증 4/4 PASS)
### 변경 (스키마 변경 없음 — TBL_SYSTEM 컬럼 그대로)
- `OrderServiceImpl.java` 4개 메서드: `autoNumCreateYn`을 세션값 대신 **상수 "Y"로 강제**(주석으로 정책 명기) — 접수번호 2곳(createNewOrder, saveFromOrderManage) + 작업지시번호 2곳(createNewControl, createNewControlForOrder). 'N' 분기(수동 createOrder / CONTROL_NUM=''→NULL 스테이징 / 수동 CONTROL_NUM 저장)가 도달 불능이 됨. 전달만 하는 managerOrderStatus/orderConfirmFromDrawing은 무수정(최종 소비처인 createNewControlForOrder에서 강제됨).
- `attr/tabs/bottom2.jsp`: 사이트마스터 팝업(site_info_pop_form, tiles bottom으로 메인 셸 포함) AUTO_NUM_YN 셀렉트에서 **N 옵션 제거**(Y만 잔존). 폼 정의는 이 파일이 유일(전수 grep). 기존 'N'/NULL 테넌트 편집 시 셀렉트가 빈 표시 → 필수값 검사(bottom2.js:274)가 Y 선택을 강제 — 저장하면 Y로 정착.
### 검증 (compileJava OK, 8081 재기동 후 앱 엔드포인트 — 세션 46668b2e scratchpad verify_manual_block_step2.py, 리포트 verify_manual_block_report.json)
- 4/4 PASS: T1 접수번호 자동채번 회귀(2607-SMD-003-0001) / T2 수동 REGIST_NUM("MANUAL-VRF-0716") 지정 생성 → 수동값 무시·자동채번 저장(DB에 수동값 0건) / T3 작업지시 발행 회귀(C26-0716-0001, 매핑 1건) / T4 메인 셸 HTML의 AUTO_NUM_YN 옵션 ["Y"]뿐.
- 검증 데이터(주문 2·컨트롤 1, 표식 ITEM_NM='VRF수동차단') 앱 경로 소프트 삭제, 잔존 0.
- 한계: 실제 'N' 테넌트 세션으로의 실검증은 TBL_SYSTEM 토글(DB 직접 수정)이 필요해 미실시(사용자 질문 규칙). 단 강제값이 컴파일 타임 상수라 'N' 분기 도달 불능은 코드로 확정적.
- 8081 = 이번 세션 재기동(스탭2 + 7/15 풀 56커밋 반영, logs/bootrun_8081_0716_step2.log, 기존 PID 39016 종료함).
### 다음
- **스탭3 착수 전 사용자 질문 필요**(DDL): 백필 대상 실측(7/16) = smd만 22건(살아있는 NULL 1건=91000007 구세대 시드 + 삭제행 21건 — 92000001은 스탭1 시드 교정으로 해소돼 7/15의 23건에서 감소). smd2·jet은 NULL 0건. CONTROL_NUM 컬럼 = varchar(30) NULL, 3스키마 동일. 구체안 제시 후 사용자 승인 대기.

## [2026-07-16] 스탭1 %테스트 시드 upsert 교정 — 완료 (%테스트 1파일, 미커밋, 실검증 10/10 PASS)
### 착수 전 실측으로 확정된 사실 (7/15 분석 보정)
- 앵커 견적 '자동화테스트' = **EST_SEQ 9022** → 시드 활동 범위는 **92000001~92000013뿐**. 91000xxx 대역은 구세대 픽스처(est 12195 주문 27087~27099) 잔재로 시드가 더는 건드리지 않음.
- 따라서 **"91000001 부활 여부" 결정은 불필요해짐** — 현 앵커에서 시드 재실행이 91000001을 만지지 않아 7/3 삭제 상태 그대로 유지됨(실검증 PASS). 단, 앵커 견적이 재생성돼 EST_SEQ가 9022가 아니게 되면 시드가 91-대역으로 회귀해 91000001 부활+번호/매핑 중복 위험 — 앵커 교체 시 구세대 정리 선행 필요(주의로만 기록).
- 91000007(NULL, 구세대 대역)은 시드로 교정 불가 → **스탭3 백필 23건에 포함해 처리**(변동 없음).
### 변경 (reviewer/data_provisioner.py 1파일 — 활성 오버레이. archive 베이스는 무수정)
- TBL_CONTROL upsert에 `CONTROL_NUM=VALUES(CONTROL_NUM)` 추가 → 재프로비저닝 시 NULL 자가 교정. 실행 결과 92000001이 'C25-1016-0001'로 즉시 교정됨(살아있는 C25-1016-0001 유일 확인 — 91000001은 죽어 있어 충돌 없음).
- 매핑(TBL_CONTROL_PART_ORDER/_MAIN) upsert에 ORIGINAL_SIDE_QTY/OTHER_SIDE_QTY 추가.
- TBL_OUTSIDE_REQUEST upsert에 OUTSIDE_ORDER_NUM/ATTACH_PO_YN/INCLUDE_WATERMARK, _DETAIL에 FINISH/GRIND/SURFACE_YN 3종 추가.
- TBL_INVOICE upsert에 INVOICE_DT=NOW() 추가.
- ★TBL_INVOICE_DETAIL·TBL_MONTH_CLOSE_ORDER는 **ORDER_SEQ가 PK에 포함**(SHOW KEYS 실측)이라 upsert로 교정 불가 — 세대 교체 때마다 옛 ORDER_SEQ 행이 누적되는 구조(실측: 디테일 106행, 마감주문 45행). 교정 = stale 삭제 방식: 인보이스별 현행 ORDER_SEQ 외 디테일 삭제 + reset 헬퍼(_reset_order_regression_control_links)에 TBL_MONTH_CLOSE_ORDER 92-대역 purge 추가(기존 매핑 rebuild 패턴 미러링).
### 검증 (표준 경로 ensure_order_data 실행 — 세션 4bc0e463 scratchpad verify_seed_upsert_fix2.py)
- 10/10 PASS: 92000001 번호 교정 / 91000001 비부활 / 살아있는 NULL=[91000007]만 / 픽스처 13건 매핑 각 1건(이중 매핑 0) / QA 검색 키(2510-SMD-001-0001·C25-1016-0001) 불변 / 외주·인보이스·마감 컬럼 갱신+stale 정리.
- 실행 전 before-image 백업: `logs/seed_before_image_2026-07-16.json` (10개 스냅샷, 되돌리기 참조용).
- pytest는 이 환경 파이썬에 미설치라 미실행 — 유일한 관련 테스트(test_reviewer_data_provisioner_compat: 임포트+SYSTEM_ID)는 임포트 확인으로 동일 커버.
- 주의: 검증 과정에서 시드가 실제 실행돼 DB에 반영됨(픽스처 대역 한정 — 92000001 번호, stale 정리 등). qa_agent 실화면 QA는 미실행.
### 신규 발견 레거시 (정리 여부는 별도 결정 — 스탭3 데이터 보정 논의에 연결)
- 구세대 픽스처가 전부 살아있음: est 12064 주문(26026~26048)·est 12195 주문(27087~27099) + 91000002~91000012 컨트롤. 이로 인해 **작업지시번호 C25-1016-0002~0012가 살아있는 2건씩 중복**(91/92 대역, 실측), REGIST_NUM 2510-SMD-001-*도 세대당 1건씩 총 3건 중복. QA는 현행 통과 조건(REGIST_NUM 검색·min_rows 1) 기준 영향 없음.
- 기타 잔재: est 9022 잔여 주문 5건(92008226~30, 시드 비관리·상태 업데이트만 받음), 짝수 IV-QA 인보이스(5/16 생성, 현행 시드 비관리), 91-대역 외주 디테일 행.
### 다음
- **스탭2 수동입력 차단 착수 지시됨**(7/16, 사용자 "남은 작업 진행" — 컨텍스트 팽창으로 새 세션에서 착수하기로 합의) → 스탭3 NULL 보정 23건+DDL → 스탭4 SP 가드.
- ★사용자 지시(7/16): **테이블 스키마 변경(컬럼 추가·수정·삭제, NOT NULL DDL, 프로시저 변경 포함)은 실행 전 반드시 사용자에게 구체안을 제시하고 질문할 것.** 스탭2는 스키마 변경 없음(서버 강제 + 사이트마스터 N 옵션 제거, TBL_SYSTEM 컬럼은 그대로) — 바로 진행 가능. 스탭3·4는 착수 시점에 DDL/프로시저 변경안을 먼저 질문.
- 스탭2 구현 참고: 7/14 섹션의 구현안(OrderServiceImpl 분기 3곳 서버 강제 + site-master.jsp N 옵션 제거) 및 7/15 섹션의 위험 근거(EMPTY_STRING_IS_NULL + OrderServiceImpl:1944, createNewControl 1774~ 조건부).

## [2026-07-15] 잔여 스탭(시드 교정→NOT NULL DDL→SP 가드 등) 영향 전수분석 (조회만, 코드 무변경 — answer-reviewer 검증 OK)
- ★확정 위험(스탭2 NOT NULL DDL): 라이브 sql_mode=EMPTY_STRING_IS_NULL(전역 실측 — ''를 NULL로 저장) + `OrderServiceImpl:1944`(createNewControlForOrder가 AUTO_NUM_CREATE_YN='N'이면 **매 호출 무조건** CONTROL_NUM='' 대입) → 스테이징 NULL → SP_CONTROL_BATCH가 TBL_CONTROL에 그대로 복사. CONTROL_NUM NOT NULL 걸면 'N' 테넌트 발행 경로 즉사. **대책 = 수동입력 차단(자동채번 서버 강제)을 DDL보다 먼저/동시 적용**. createNewControl updateList 분기(1774~)도 containsKey만 검사라 빈값 시 동일 위험(조건부).
- 보정 규모 정정: NULL CONTROL_NUM은 **23건**(살아있는 2건=시드 91000007/92000001 + 소프트삭제 21건) — 7/8 MD의 "2건"은 살아있는 행만 센 것. DDL은 삭제행도 검사하므로 전량 백필 선행.
- REGIST_NUM은 TBL_ORDER에 **이미 NOT NULL**(실측) — 스탭2 실제 DDL 대상은 TBL_CONTROL.CONTROL_NUM뿐. TBL_ORDER INSERT 3경로 전부 non-null 보장·NULL화 UPDATE 없음(전수).
- ★신규 발견: TBL_CONTROL_PART_ORDER에 AFTER INSERT/UPDATE/DELETE 트리거 3종 실존 → `SP_TRIG_CONTROL_PART_ORDER`가 _MAIN을 DELETE 후 첫 ORDER_SEQ 1행으로 재생성. 즉 **_MAIN은 트리거가 매핑에서 자동 재생성**(7/13 "INSERT가 저장소에 없음=DB측 생성" 규명). 같은 트리거·SP가 smd/smd2/jet 3스키마에 복제 — SP 가드 DDL은 스키마별 반영 필요.
- 스탭3(SP NOT EXISTS 가드) 설계 조건: ①가드는 반드시 **TBL_CONTROL 조인 + DEL_YN='N'** 스코프(removeControl이 매핑행을 안 지워 죽은 매핑 잔존 — 단순 존재검사면 정상 재발행 차단됨) ②S10R40 제외 유지 ③조용한 skip 파급: SP 호출 3곳(140/1802/1955) 전부 발행 건수 검증 없음 + 스테이징 무조건 삭제 → skip된 주문은 소리없이 미발행. SP 후 매핑 건수 검증 추가 권장 ④해당 컨트롤의 주문이 전량 skip되면 매핑 0건 빈 컨트롤+CONTROL_BARCODE만 생성됨(화면 노출 형태 확인 필요).
- 스탭1(시드 upsert 교정): 앱 프로세스 무영향(테스트 DB 픽스처 대역 한정). 주의 — CONTROL_NUM 복원+DEL_YN='N' 부활 로직은 7/3 시드측 삭제 처리(91000001)를 되돌리므로 처리 방침 결정, QA 검색 키(2510-SMD-001-0001/C25-1016-0001) 불변 유지. 시드 직접 매핑 DELETE/INSERT는 위 트리거를 발화시킴(픽스처 1:1이라 현재 무해). 추가 upsert 갭: PART_ORDER의 ORIGINAL/OTHER_SIDE_QTY, OUTSIDE_REQUEST(_DETAIL) 각 3컬럼, INVOICE_DETAIL·MONTH_CLOSE_ORDER의 ORDER_SEQ, INVOICE의 INVOICE_DT.
- 인덱스(ⓓ 후속): TBL_OUT_BARCODE CONTROL_SEQ 인덱스는 **비유니크 필수**(컨트롤당 다수 바코드 정상 + insertOutBarcode order.xml:5466~은 CONTROL_SEQ 미포함=NULL행 존재). 비유니크면 파손 요소 없음.
- 데드코드 경계: `estimate.xml:632` insertEstimateOrderControlMaster는 CONTROL_NUM 없이 TBL_CONTROL INSERT(현재 미호출) — 향후 배선 시 NOT NULL 즉시 위반. merge INSERT 2종(createPartOrderToMerge/Ver2) 데드 재확인.
- 실측 스크립트: 세션 d58ca57b scratchpad measure_notnull_impact*.py (smd 라이브, Test-Automize config 재사용).

## [2026-07-14] 수동 번호입력 차단 정책 — 사용자 결정, 구현 미착수
- 사용자 결정: 접수번호·작업지시번호 **수동 입력 차단**(자동채번 전용화). 근거 실측(7/14, answer-reviewer 검증): 전 활성 테넌트가 이미 AUTO_NUM_CREATE_YN='Y'(TBL_SYSTEM, BASIC 템플릿만 NULL), 비정형 번호는 접수 18·작업지시 65건 전부 테스트 산물 형태(TEST-*/QA-*) — 수동 운영 관행 없음. 설정 원천 = TBL_SYSTEM(사이트마스터 site-master.jsp에서 편집), 서버는 CommonUtility.getParameterMap:89가 세션 userInfo로 덮어써 클라이언트 위조 불가.
- 'N' 분기에 번호 외 다른 기능 없음(검증) — 차단 시 잃는 것은 외부 체계 번호 직접 지정 능력뿐(신규 테넌트 온보딩 요구 가능성만 영업/PM 확인 권장).
- 구현안(합의): ①서버 강제('N'이어도 자동채번 강제 또는 수동 번호 저장 거부 — OrderServiceImpl 분기 3곳) ②사이트마스터 N 옵션 제거/비활성 ③효과: 수동 중복 레이스 소멸+채번 원자화가 전 경로 커버, 수동용 중복검사 사장화(정리는 사장 코드 일괄 건).

## [2026-07-14] 결함ⓒ 드리프트 A안(가드 전파) 구현 (%클라우드, 미커밋, 실검증 7/7 PASS)
### 결정/범위
- 사용자 확정: A안(가드 전파) 착수. 착수 전 사전 실측(preflight_drift.py) — 살아있는 매핑 64건 중 수량 불일치 4(전부 단일 매핑=드리프트 패턴, 배정 운영 흔적 없음)·단가 불일치 미마감 2/마감 0·병합 1·마감 16. 팀 확인 2문항(배정수량·마감 단가조정 운영)은 병행 확인 사항 — 가드가 두 운영을 구조적으로 보호하므로 착수 비차단으로 판단.
### 변경 (2파일, 기존 미커밋 위에 추가)
- `order.xml`: ①기존 `updateControlPartOrderFromOrderManage`에 DELIVERY_DT·ITEM_NM 조건부 SET 추가(queryId·기존 로직 불변) ②신규 5문 — `updateControlPartOrderMainFromOrderManage`(_MAIN 납기·납품일·품명 무가드), `updateControlPartOrderQtyGuarded`/`AmtGuarded`(매핑), `MainQtyGuarded`/`MainAmtGuarded`(_MAIN). 가드 = 살아있는 컨트롤 조인 + MERGE_CONTROL_SEQ IS NULL(병합 합산 보호) + TBL_MONTH_CLOSE_ORDER NOT EXISTS 3키(마감 조정 단가 보호) + 수량만 단일 매핑 HAVING COUNT=1(분할 배정 보호 — 자기참조는 파생테이블 IN으로 1093 회피).
- `OrderServiceImpl.java`: saveFromOrderManage 전파 분기 확장 — 매핑=납기/접수번호/납품일/품명(oldMap 키), _MAIN=납기/납품일/품명, 수량=oldMap 키+tempMap 신값 비어있지 않을 때(매핑+_MAIN), 단가=oldMap에 UNIT_FINAL_(EST_)AMT 있을 때(매핑+_MAIN). createInvoice의 updateDeliveryDt 직후 **전용 격리 맵**(ORDER_SEQ·DELIVERY_DT·LOGIN_USER_SEQ만)으로 납품일 전파 2문 호출(그리드 행 필드 오염 방지).
### 검증 (라이브 8081 재기동, 앱 엔드포인트 실증 — verify_drift_a.py, 세션 6a47c64d scratchpad, 리포트 verify_drift_a_report.json)
- 7/7 PASS: T1 납품일·품명·납기(회귀) 전파(매핑+_MAIN 실측) / T2 수량 전파 / T3 단가 전파(콤마 입력 "1,500"→1500) / T4 마감 가드(합성 마감행 후 단가 수정 → 주문만 2000, 사본 1500 불변) / T5 병합 가드(수량 불변) / T6 다중 매핑 가드(합성 복제로 매핑 2행화 → 수량 [7,7] 불변·단가는 [3000,3000] 전파 — 가드 차등 정확) / T7 거래명세표 createInvoice 납품일 전파.
- 합성 조작(마감행 CLOSE_VER=999·MERGE 99999999·복제 매핑)은 검증 데이터 행에만 수행 후 전량 제거. 검증 주문 2건 앱 경로 소프트 삭제, 거래명세표 IV-SMD-000073 removeInvoice(직접 파라미터 형식 — data 래핑 아님 주의), 잔재 0 실측(check_residue.py).
- compileJava·order.xml 정형성 OK. answer-reviewer 6주장+부작용 5항목 적대 검증 반박 0 (비차단 관찰 1: _MAIN 무가드 문은 값 <if> 전부 미발화 시 감사컬럼만 갱신 — 정합 무영향).
### 남은 것/주의
- 팀 확인 2문항은 가드 조정용으로 여전히 유효: ①단일 매핑에서 의도적 수량 차이(부분 발행) 운영 실재 시 수량만 B안(전파 제외+감시) 전환 ②마감 단가조정 운영은 가드로 기보호.
- 과거 이미 어긋난 데이터(수량 4·단가 2건, preflight 실측) 보정은 별도 마이그레이션 결정(백업→트랜잭션→사용자 COMMIT).
- 역방향(작업지시관리→주문) 미동기화는 현행 유지(배정 의미 존중) — 정책 결정 대기. B안 잔여 요소(불일치 배지·리포트)와 사장 코드 정리는 별건.
- 8081 = 이번 세션 재기동(A안 반영, logs/bootrun_8081_0714_driftA.log, 기존 PID 22084 종료함).

## [2026-07-13] 결함ⓒ 복사컬럼 드리프트 전면 분석 — 아티팩트 산출 (조회만, 코드 무변경)
- 사용자 지시로 사용 화면·전파 경로 전수 분석 + 해결방안 아티팩트 생성: `바탕화면\예시\드리프트분석\복사컬럼_드리프트_분석_260713.html` (Artifact 게시 https://claude.ai/code/artifact/1105060e-f616-47f3-ae87-7ff92f9ab090). 병렬 Explore 3방향(전파/소비처/진입점) + 쟁점 직접 재검증 + answer-reviewer 12주장 전수 확인(반박 0).
- **핵심 신규 사실**: ①사본 테이블은 2개(TBL_CONTROL_PART_ORDER + **_MAIN** — _MAIN은 단가 갱신 경로·INSERT 자체가 저장소에 없음=DB측 생성·스냅샷 고정, 작업지시관리/원가분석 V1의 단가·합계가 이걸 씀) ②수주관리 미전파 컬럼은 수량·단가2 외에 **DELIVERY_DT·ITEM_NM**도 ③거래명세표 createInvoice의 updateDeliveryDt도 매핑 미전파 ④작업지시관리는 역방향 드리프트(매핑만 수정, 주문 미반영) ⑤전역 수량 SF_GET_CONTROL_PART_QTY=SUM(매핑 ORDER_QTY)×PART_UNIT_QTY(v1/order.xml:169 인라인 실측) — 29파일 253회 사용 ⑥납기초과 목록(selectBusinessOverOrderListV1, v1:1323)이 사본 납기를 WHERE에 사용 ⑦단가검토 팝업 updateOrderPartUnitFinalEstAmt(orderCalculate.xml:437)가 유일한 주문+매핑 동시 기록(모범 패턴, S10R50 제외).
- **★7/10 결론 정정 2건**: ⑴"단가는 덮는 경로 없어 전파가 가장 안전" → **마감이력이 매핑 단가를 직접 조정**(updateControlPartFromCloseHistory order.xml:3509, close-history.jsp:1846 배선 실확인) — 무가드 전파는 마감 조정값 파괴 위험 ⑵"합침 경로가 ORDER_QTY를 덮음(배정수량 근거)" → 해당 INSERT 2종(createPartOrderToMerge/Ver2)은 **사장 코드**, 배정 의미의 실근거는 작업지시관리 편집(order.xml:1154)+병합 합산(updateSumControlPartOrderQty:6637).
- **권고(아티팩트 6절)**: 착수 전 팀 확인 2문항(배정수량 운영? 마감 단가조정 운영?) → 1단계 DELIVERY_DT·ITEM_NM 전파 추가(저위험) → 2단계 수량·단가 A안(미마감+비병합+단일매핑 가드 전파, 기본 권고)/B안(소비처 교정+불일치 감시) 택일 → 3단계 역방향 정책·사장 코드 정리. 최고위험 소비처=출고수량 생성/완료판정(inspection.xml:1330·1338, 사본 수량으로 TBL_OUT 생성)과 마감이력 정산(order.xml:1704).
- 착수는 사용자 결정 대기(ⓒ 보류 상태 유지). 행번호는 7/13 워킹트리 기준(채번 원자화 반영 후).

## [2026-07-13] 결함ⓐ 채번(MAX+1) 원자화 — 접수번호+작업지시번호 (%클라우드, 미커밋, 실검증 ALL PASS)
### 변경 (3파일, ⓑⓓ 변경 위에 추가 — ★EstimateServiceImpl.java는 이번에 처음 수정됨)
- `sqlMaps/order.xml`: ①`createRegistNum`·`selectRegistNumForEst`에 FOR UPDATE(잠금 읽기 — REPEATABLE READ 스냅샷이 미커밋 채번을 못 보는 커밋 경계 레이스를 커밋까지 유지되는 범위락으로 차단) ②`createControlNum` 파생테이블의 TBL_CONTROL 분기에만 FOR UPDATE(TBL_CONTROL_EXCEL 스테이징 분기는 인덱스 없어 풀스캔 락이라 제외 — 테넌트 격리 유지) ③신규 `acquireNumberingLock`(GET_LOCK 10s)/`releaseNumberingLock`. 기존 queryId 무수정.
- `OrderServiceImpl.java`: createNewOrder/saveFromOrderManage(접수번호, 락키 TOMES_REGNUM_{SID}_{COMP})·createNewControl/createNewControlForOrder(작업지시번호, 락키 TOMES_CTRLNUM_{SID}) — 자동채번 시 채번~INSERT(작업지시는 SP 실행까지) 구간 GET_LOCK 직렬화, finally 해제. 헬퍼 acquireNumberingLock(실패 시 ServiceNotValidException)/releaseNumberingLock(예외 삼킴) 추가.
- `EstimateServiceImpl.java`: registerEstimateOrder(견적→주문 전환 채번) 동일 REGNUM 락 + 동일 헬퍼 + import 1건.
- 원리: GET_LOCK(같은 그룹 동시 진입 직렬화, 빈 범위 갭락 데드락 방지) + FOR UPDATE(락 해제~커밋 사이 틈 차단) 이중. 채번 소비 경로 전수(createRegistNum 3곳/createControlNum 2곳/createOrderAuto·insertEstimateOrderMaster) 락 구간 안 확인.
### 검증 (라이브 8081 재기동 후 앱 엔드포인트 — verify_numbering_atomic.py/verify_numbering_post.py/test_lock_behavior.py, 세션 6a47c64d scratchpad)
- PASS: 접수번호 동시생성 8라운드x2스레드=16건 전부 유일(수정 전 7/9엔 5라운드 내 재현) / 단일요청 3행 연속채번(-0001~0003) 회귀 / 작업지시 동시발행 3라운드=C26-0713-0001~0006 전부 유일·200(빈 범위 케이스 포함, 데드락 없음) / 이번달 REGIST_NUM·오늘 CONTROL_NUM 살아있는 중복 0 / 락 잔류 0.
- 파생테이블 내 FOR UPDATE 갭락 실증(다른 커넥션 INSERT 1205 타임아웃, 롤백 프로브) — answer-reviewer 지적 (b) 해소. SP 내부 커밋 없음은 7/10 "확정 트랜잭션 전체 롤백" 실측으로 뒷받침.
- compileJava 통과·order.xml 정형성 OK. 검증 데이터(주문 19건, 표식 ITEM_NM='VRF원자화') 전부 앱 경로 소프트 삭제, 잔존 0.
### 주의/잔존
- 네임드락은 커넥션 스코프 — release 실패가 반복되면 풀 커넥션에 락 잔류 가능(채번 요청 10s 대기 후 실패라는 안전한 방향이지만 기능 마비). 이상 시 `SELECT IS_USED_LOCK('TOMES_REGNUM_...')` 확인. 스케일: 락 키=테넌트(+발주사) 단위 순간 보유라 1000테넌트 무해, FOR UPDATE 범위는 복합인덱스(SYSTEM_ID,DEL_YN,REGIST_NUM / CONTROL_NUM 인덱스)로 테넌트 격리.
- 수동 번호 입력(AUTO_NUM_CREATE_YN='N') 경로의 비원자적 중복검사는 기존 그대로(채번 아님, 이번 범위 밖).
- 8081 = 이번 세션 재기동 서버(수정 반영, logs/bootrun_8081_0713_numlock.log). 미커밋 누적 = OrderServiceImpl+order.xml(ⓐⓑⓓ) + EstimateServiceImpl(ⓐ) + estimate 3파일(단가검토 별건). 커밋은 사용자 몫.
- 남은 계획(7/9 순서): %테스트 시드 upsert 교정 → NOT NULL 보정+DDL → SP NOT EXISTS 가드. TBL_OUT_BARCODE 인덱스 DDL 결정 대기(ⓓ 섹션).

## [2026-07-10 오후] 결함ⓓ 삭제 미전파 — removeControl 바코드 전파 (%클라우드, 미커밋, 실검증 PASS)
### 변경 (2파일, 결함ⓑ 변경 위에 추가)
- `sqlMaps/order.xml`: removeControlPartBarcode 아래에 update 2개 추가(기존 queryId 무수정) — `removeControlBarcodeByControl`/`removeOutBarcodeByControl`(컨트롤 단위 DEL_YN='Y'+UPDATE_DT+UPDATE_SEQ, 기존 소프트 삭제 관례 미러링: drawingUpload.xml revDelete·inspection.xml:1244 패턴).
- `OrderServiceImpl.removeControl`: 본삭제 분기(PART_NUM 없음)에서 orderMapper.removeControl 직후 바코드 2테이블 소프트 삭제 호출 추가 + `LOGIN_USER_SEQ`를 세션 map에서 행에 주입(기존엔 미주입이라 removeControl의 UPDATE_SEQ가 사실상 null이었음 — 감사컬럼 부수 교정). 파트 삭제 분기(물리 DELETE)·merge 경로(:711, 자체적으로 updateControlPartOrderPackingCnt2+createOutBarcodeToMerge로 처리)는 무변경.
### 검증 (라이브 8081 재기동, 앱 엔드포인트 실증 — 세션 scratchpad verify_delete_propagation.py, 리포트 verify_del_fix_report.json)
- PASS: 주문 생성→확정(CONTROL_BARCODE 1·OUT_BARCODE 1 생성)→removeControl→컨트롤 DEL_YN=Y(+UPDATE_SEQ=85 기록)·양 바코드 LIVE 0(UPDATE_SEQ 기록됨). 검증 데이터 소프트 삭제 정리, 잔존 0.
- compileJava·order.xml 정형성 OK.
### ★스케일 주의 (실측 기반, 사용자 결정 대기)
- TBL_CONTROL_BARCODE는 CONTROL_SEQ 인덱스 있음. **TBL_OUT_BARCODE는 CONTROL_SEQ 인덱스 없음**(ORDER_SEQ 복합+PK뿐) → removeOutBarcodeByControl은 현재 풀스캔(EXPLAIN 실측 rows 24106, 현 2.4만행·removeControl은 저빈도 관리자 액션이라 당장 무해).
- ORDER_SEQ 서브쿼리 우회는 기각: EXPLAIN상 여전히 풀스캔인 데다 매핑과 ORDER_SEQ 불일치 행 57건(실측)을 놓침. **권고 = TBL_OUT_BARCODE에 CONTROL_SEQ 인덱스 추가 DDL**(운영 DB 변경이라 사용자 결정·별도 관리).
### 기타
- 소프트 삭제된 과거 컨트롤들의 기존 잔존 바코드(역사 데이터)는 팀장 방침(시드 산물 정리 불요)대로 미정리 — 이번 수정은 향후 삭제부터 전파.
- 미커밋 누적 = OrderServiceImpl.java + order.xml(ⓑ+ⓓ) + estimate 3파일(별건). 8081은 이번 세션 재기동 서버(logs/bootrun_8081_0710_delfix.log).

## [2026-07-10 오후] 결함ⓑ 이중 매핑 — Java 발행 사전검사 구현 (%클라우드, 미커밋, 실검증 PASS)
### 변경 (2파일)
- `sqlMaps/order.xml` 끝에 select 2개 추가(기존 queryId 무수정): `selectControlExcelAliveMappedOrderList`(스테이징 TBL_CONTROL_EXCEL IN_UID 기준, 살아있는 작업지시(TBL_CONTROL.DEL_YN='N')에 매핑된 주문 목록, WORK_TYPE S10R40 제외 — SP가 신규 ORDER_SEQ 채번이라 재사용 없음), `selectAliveControlNumByOrderSeq`(단건 주문의 살아있는 매핑 CONTROL_NUM). ★실측 발견: **TBL_CONTROL_PART_ORDER에 DEL_YN 컬럼이 없음**(라이브 SHOW COLUMNS) — 과거 HANDOFF의 "매핑 DEL_YN=N" 서술은 부정확, 매핑 생존 판정은 조인된 컨트롤 DEL_YN만으로 한다(기존 쿼리 관례와 동일).
- `OrderServiceImpl.java` 5곳: ①createNewStockControl SP 직전 검사(차단 시 기존 model "list" 계약 재사용 — 스톡 스테이징엔 ORDER_SEQ 컬럼 자체가 없어 사실상 미발화, 방어용) ②createNewControl SP 직전 검사(flag=true + message에 대상 REGIST_NUM(CONTROL_NUM) 나열) ③createNewControlForOrder SP 직전 백스톱(차단 시 resCode=CONTROL_EXISTS, 스테이징 삭제는 항상 수행) ④orderConfirmFromDrawing 상태변경 **전** 기발행 검사(7/9 실증된 결정적 결함 경로 — flag/message, drawing_upload.jsp:1043이 그대로 알림) ⑤managerOrderStatus: CONTROL_EXISTS인데도 S34R10이면 발행 호출하던 분기를 else 안으로 이동(기존엔 CONTROL_EXISTS 분기 파라미터 누락 500으로 우연 차단 → 명시 차단. UI는 order-manage.js:1611이 CONTROL_EXISTS 알림 기처리).
### 검증 (라이브 8081 재기동 후 앱 엔드포인트 실증 — 세션 scratchpad verify_dup_mapping_fix.py, 리포트 verify_dup_fix_report.json)
- **PASS 3건**: 정상 발행 회귀(SUCCESS·매핑 1·CONTROL_NUM 채번) / 순차 재확정 차단(200+CONTROL_EXISTS, 매핑 1 유지 — 기존 500) / 도면업로드 재확정 차단(flag=true "이미 작업지시(C26-0710-0002)가 발행된 주문입니다...", 매핑 1 유지).
- **잔존(예정)**: 동시 확정 레이스는 여전히 이중 매핑 재현(2스레드 동시 → 매핑 2 실측) — Java 사전검사는 창 축소용이고 완전 차단은 **SP NOT EXISTS 가드(후속 단계, DB 아티팩트라 DDL 별도 관리)** 담당(7/3 권장안 2).
- 검증 데이터(주문 6·컨트롤 4, 표식 ITEM_NM='VRF검증F') 전부 앱 경로 소프트 삭제, 잔존 0.
- 시행착오 1건: 1차 구현이 매핑 테이블 B.DEL_YN을 참조해 1054 오류 → 확정 트랜잭션 전체 롤백(실측)됨을 확인 후 교정. gradlew compileJava 통과(`build` 전체는 기동 중 서버의 리소스 잠금으로 processResources 실패 — 컴파일·XML 정형성은 정상).
### 서버/브랜치 주의
- 8081 = 이번 세션이 재기동한 bootRun(수정 코드 반영, logs/bootrun_8081_0710_dupfix2.log). 12:01 자동 재기동 서버(PID 37180)와 중간 서버(44660)는 종료함.
- 현 체크아웃 **feature_hightChart_260703**(사용자 전환 추정, main.jsp는 워킹트리에 없음=커밋된 듯). 미커밋 = OrderServiceImpl.java + order.xml(이번 건) + estimate 3파일(단가검토 건). 커밋은 사용자 몫 — 브랜치·파일 분리 주의.
### 다음 단계 (7/9 계획 순서)
- %테스트 시드 upsert 교정 → NOT NULL 데이터 보정+DDL → SP NOT EXISTS 가드(동시성 완전 차단). 채번(MAX+1) 원자화·바코드 삭제 전파는 별도 결정(저확률/누적성).

## [2026-07-10] 결함ⓒ 복사컬럼 드리프트 심층 분석 → 사용자 결정 보류 (조회만, 코드 무변경)
- **사용자 결정: ⓒ는 내버려두고 다음 문제로** ("내버려두고 다음 문제", 2026-07-10). 아래 분석은 추후 착수 시 재사용.
- 복사컬럼 정의: TBL_CONTROL_PART_ORDER의 TBL_ORDER 복사 컬럼들(order.xml:866 createControlPartOrder — REGIST_NUM/ORDER_NUM/ORDER_QTY/UNIT_FINAL_(EST_)AMT/납기/도면/명칭류 등 21개). 드리프트 원인 = 수주관리 저장 전파 목록(OrderServiceImpl.java:1292~1317)에 **수량·단가만 누락**(납기·접수번호는 order.xml:1119, 프로젝트명 계열은 :5481로 전파됨).
- 소비처 전수조사(answer-reviewer 검증 6건 확정): ①마감/종료이력(selectControlCloseHistoryList:1667/EndHistory:1792 — 표시+`C.UNIT_FINAL_AMT*C.ORDER_QTY` 합계+단가범위 WHERE, 프래그먼트:105~133의 C가 이 두 쿼리에서만 매핑 테이블, ControlManage/CostAnalysis에선 C=_MAIN) ②출고수량 생성(inspection.xml:1087/1330 — 매핑 ORDER_QTY로 TBL_OUT.OUT_QTY INSERT, 데이터 생성이라 파급 최대) ③주문관리 CONTROL_EST_AMT(order.xml:4899→4813) ④거래명세서 수량 CONTROL_PART_QTY(:2371/2401 — 금액은 TBL_ORDER라 7/9 "거래명세표 무관" 판단은 금액 한정으로 정정) ⑤접수번호 중복검사(selectBeforeInsertDuplicationRegistList:2849) ⑥v1 집계 다수(SUM(ORDER_QTY) 계열).
- 복사 설계 이유(확정 2 + 추론 2): ①무주문 작업지시 기능 — 매핑이 ORDER_SEQ 자체 채번(:901 NEXTVAL, 호출부 TBL_ORDER 무검증)으로 부모 없이 생성되는 정상 경로 3곳 → 복사 컬럼이 유일 원본 ②합침 경로(createPartOrderToMergeVer2:3757)는 ORDER_QTY를 #{CONTROL_ORDER_QTY}로 덮음 → 매핑 수량='배정 수량'의 독립 의미 ③(추론)발행 시점 스냅샷 — 단 일부 필드는 전파돼 혼재 ④(추론)조인 회피. git init commit(884505f)부터 존재해 도입 경위 기록 없음.
- 착수 시 시사점: 원본조회 전환은 무주문 매핑 때문에 전면 불가 / 수량 무조건 전파는 배정수량 파괴 위험 / **단가(UNIT_FINAL_(EST_)AMT)는 덮는 경로 없어 전파 추가가 가장 안전한 첫 수**.
- 다음 작업이던 결함ⓑ 이중 매핑 수정은 2026-07-10 오후 착수·완료(최상단 섹션 참조).

## [2026-07-09] 작업관리 DB 문제 재분류 + 화면 프로세스 실증 검증 (t-0027 후속, 코드 무변경)
### 정책 결정(사용자 전달)
- ①CONTROL_NUM·REGIST_NUM NOT NULL 추가 확정 ②주문:작업지시=N:1 확정 ③팀장 방침: 시드 산물 데이터 꼬임은 정리 불요, **화면 프로세스상 문제만 검증/수정**.
### 실증 검증 결과 (앱 엔드포인트만 사용, 시드 무관 — 세션 scratchpad verify_process_defects.py, answer-reviewer 검증 OK)
- **재현됨(순수 앱 결함, 수정 대상)**: ⓐ접수번호 중복(동시 등록 2건→같은 번호 2607-SMD-002-0001, MAX+1 무잠금+자동채번 모드는 중복검사 생략) ⓑ이중 매핑(동시 확정→살아있는 지시 2건 매핑, 5/19 실사례와 동일 기전) + **작업지시번호 중복도 함께 재현**(C26-0709-0001 2건) ⓒ복사컬럼 드리프트(수주관리 수량·단가 수정이 매핑 미반영) ⓓ삭제 미전파(removeControl 후 바코드·매핑 DEL_YN=N 생존).
- **비재현(시드 산물 확정, 무시)**: 번호 NULL 작업지시(앱 생성분 전부 번호 보유), 고아 매핑(주문 물리 DELETE 경로 자체 없음). 순차 재확정은 500 오류로 우연히 차단(CONTROL_EXISTS 분기 파라미터 누락→SP 오류, 추론).
- **기존 감사(7/8 MD) 정정 2건**: "접수번호 중복체크 오탐" 위험 철회(근거 쿼리 order.xml:2848/3987 둘 다 사장 코드 — 도달성 미추적이 원인, 이후 3단계 추적을 기본 절차화), CONTROL_STATUS NULL은 설계상 미확정 상태(발행 스테이징 미지정+종료취소 버튼이 명시적 NULL 세팅) — 보정 불요 권고.
- 검증 데이터 정리 완료: 주문 92012002/92012003·지시 19001~19003 전부 소프트 삭제(S34R20/DEL_ 접두). 물리 잔여(매핑 3행, 바코드 8건 DEL_YN=N)는 결함ⓓ 특성상 잔존 — 표식 ITEM_NM='VRF검증'.
### [같은 날 후속] 충돌 창 실측 + 이중 매핑 결정적 경로 실증 (answer-reviewer 검증 OK)
- **충돌 창 스윕 실측(dev, 유휴)**: 접수번호 중복 창 **<40ms**(0ms만 재현, 배치 저장도 창 증폭 없음 — 배치 증폭 가설 실측 반박·철회), 이중 매핑 레이스 창 **50~100ms**(100ms부터 비재현). 운영 판단: 접수번호 중복은 저확률로 우선순위 하향 가능(단 창은 부하·데이터 비례 확대, DB 유니크 부재).
- **★이중 매핑 결정적 경로 실증**: 발행 완료 주문을 **5초+ 뒤** `/orderConfirmFromDrawing`(도면업로드 팝업의 "저장 후 확정" 흐름, drawing_upload.jsp:1038~1053)으로 재확정 → 두 번째 지시+매핑 생성(매핑 1→2), 성공 경로 실행(SQL 트레이스 확인). 가드가 PDF·사업자·납기·S34R30뿐, 기발행 검사 없음(OrderServiceImpl:1432~1504). **시간·동시성 무관 결정적 재현** — 5/19 실사례(6~17초 간격)와 패턴 일치, 유력 경위로 추정(추론). UI에서 발행된 주문의 도면 저장 진입이 차단되는지는 미확인(서버는 무조건 수용 실증).
- 최종 운영 재현성: 이중 매핑(도면업로드 경로)=결정적 / 드리프트·삭제 미전파=단독 조작 100% / 접수번호 중복·확정 레이스=저확률(창 0.04~0.1초).
- 실험 데이터 전부 앱 경로 소프트 삭제 정리(표식 ITEM_NM='VRF검증W'/'VRF검증D' 포함, 잔존 살아있는 주문 0 확인).
### 다음 단계
- 수정 착수 순서(계획): Java 발행 사전검사(**도면업로드 확정 경로 최우선** + SP 호출 3곳) → %테스트 시드 upsert 교정 → NOT NULL 데이터 보정+DDL → SP NOT EXISTS 가드. 채번(MAX+1) 원자화·바코드 삭제 전파는 별도 결정(저확률/누적성).
- 산출물 MD: 바탕화면 `MD\고아매핑_문제3_경위_해결계획_260709.md` — 팀장 방침 반영 전 버전이라 재분류 반영 갱신 필요.

## [2026-07-03] 거래명세표에 작업지시번호(C26-0624-0007) 끼어드는 현상 — 원인 분석 (코드 무변경, answer-reviewer 2회 검증)
### 현상/직접 원인 (라이브 DB 실측)
- 접수번호 2510-SMD-001-0012(발주사 SMD-1002)의 주문 ORDER_SEQ=27098이 TBL_CONTROL_PART_ORDER에 **2행 매핑**: C25-1016-0012(CONTROL_SEQ 91000012, 6/8 시드 INSERT_SEQ '1') + C26-0624-0007(CONTROL_SEQ 18007, 6/24 사용자 85 발행). 둘 다 DEL_YN='N', MERGE_CONTROL_SEQ NULL.
- 거래명세표 목록 쿼리 `selectControlTransactionStatementList`(order.xml:2353, UNION ALL 2분기 중 신규생성=branch1)는 매핑 서브쿼리를 ORDER_SEQ로 LEFT JOIN만 하고 중복제거 없음 → 매핑 수만큼 행 복제. 상단 합계 `selectControlTransactionStatementInfo`(order.xml:2331)도 같은 조인이라 **합계 2배**(실측: 12,000 표시, 실제 6,000).
- 수주관리 `selectOrderManageListV1`(v1/order.xml:595)은 GROUP BY A.ORDER_SEQ(861행)로 접어 1행만 보임 → 화면 간 불일치로 "끼어드는" 것처럼 보임.
### 근원 (이중 매핑이 왜 생기나)
- 작업지시 발행은 DB 프로시저 `SP_CONTROL_BATCH`(call_procedure.xml:7, id=SP_CONTROL_EXCEL_BATCH; OrderServiceImpl 140/1752/1905에서 호출)가 TBL_CONTROL_EXCEL 스테이징에서 INSERT하며, ORDER_SEQ를 `CASE WHEN WORK_TYPE='S10R40' THEN NEXTVAL ELSE A.ORDER_SEQ END`로 **기존 주문 SEQ 재사용** + "이미 살아있는 다른 작업지시에 매핑돼 있는지" 검사 전무(프로시저 본문은 저장소에 없음 — 라이브 DB SHOW CREATE로 실측). Java 사전검사(selectBeforeInsertDuplicationControlList, selectCheckControlDuplicateVer3)도 CONTROL_NUM 중복만 체크.
- merge(합치기)는 `updateControlPartOrderMergeSeq`(order.xml:6627) UPDATE 방식이라 매핑행 추가 없음 → 이중 매핑은 설계상 상정 밖. DB 유니크 제약도 없음.
- 동일 패턴 이중 매핑 주문 전체 9건: 26020, 26068, 26069, 27087(같은 지시에 2행), 27088, 27089, 27092, 27095, 27098. 6/24 발행분 5건은 전부 6/8 시드 주문과 겹침.
### [같은 날 후속] 오류 데이터 정리 완료 + 중복 검증 단계 분석 (사용자 지시로 실행)
- **이중 매핑 유형 확정(전수 실측)**: 시드+사용자 6건(27087~27098) / **사용자+사용자 3건**(26020, 26068, 26069 — 5/19 test계정이 6~17초 간격 이중 발행, 시드 무관). 즉 순수 앱 경로에서도 재현되는 기능 결함.
- **데이터 정리(커밋됨)**: 중복 작업지시 9건을 앱 removeControl 관례대로 소프트 삭제(DEL_YN='Y' + CONTROL_NUM 'DEL_' 접두, UPDATE_SEQ='DUP_CLEANUP'). 대상: 18003~18007(C26-0624-0003~0007, QA시드 픽스처 위 6/24 중복발행분), 17039/17042/17043(C26-0519-0005/0008/0009, 이중발행 나중 것), 91000001(CONTROL_NUM NULL 결함 시드 — 이 건만 시드 쪽 삭제, C26-0611-0001 유지).
- 선정 근거: 시드(C25-1016-*)는 %테스트 `reviewer/data_provisioner.py`가 관리하는 QA 픽스처(CD-FT-ORD-001이 접수 2510-SMD-001-0001/작업 C25-1016-0001 검색, 재프로비저닝 시 재생성)라 시드 유지가 정본. 전 대상 하위 데이터(TBL_POP/TBL_OUT) 0건, 컨트롤당 주문 1건 전수 확인 후 진행.
- 절차: before-image 백업 `BAK_TBL_CONTROL_DUPFIX_260703`(9행, DB에 보존) → 트랜잭션 UPDATE 9행 → 검증(전 DB 이중매핑 0건 / 9개 주문 각 살아있는 매핑 1건 / 27098 거래명세표 재현 1행·합계 6,000 정상) → COMMIT. 스크립트: 세션 scratchpad fix_dup_controls.py. **되돌리기**: 백업 테이블에서 CONTROL_NUM/DEL_YN 복원.
- 잔존 주의: 소프트 삭제된 컨트롤들의 TBL_OUT_BARCODE 행은 물리적으로 남음. 라벨 출력 쿼리(selectOutgoingLabelType4, inspection.xml:1805)는 GROUP BY ORDER_SEQ,PACKING_NUM이라 여분 라벨 안 나옴(확인). 바코드 스캔 역추적이 죽은 컨트롤로 연결될 수 있는 점만 잠재 이슈로 기록.
- **중복 검증 단계 분석(권장안, 미구현 — 사용자 결정 대기)**:
  1. (1순위) Java 서비스: SP_CONTROL_BATCH 호출 3곳(OrderServiceImpl createNewStockControl:140 / createNewControl:1752 / createNewControlForOrder:1905) 공통 사전검사 — 발행 대상 중 "이미 살아있는 작업지시에 매핑된 ORDER_SEQ" 존재 시 발행 중단+대상 안내. 기존 사전검사(selectBeforeInsertDuplicationControlList order.xml:2836, selectCheckControlDuplicateVer3)는 CONTROL_NUM 중복만 봄. IDX_CONTROL_PART_ORDER_ORDER_SEQ 인덱스 있어 테넌트 스케일 안전.
  2. (동시성 백스톱) SP_CONTROL_BATCH 매핑 INSERT SELECT에 NOT EXISTS(살아있는 컨트롤 매핑) 가드 — 더블클릭 레이스(26020 실사례) 방어. 조용한 skip이라 1과 병행 필수. S10R40(NEXTVAL 신규 SEQ) 제외 유지. ※프로시저는 저장소 밖 DB 아티팩트라 변경 시 별도 DDL 관리 필요.
  3. (표시 방어, 선택) 거래명세표 목록(order.xml:2353)/합계(2331) 쿼리 dedup — 재오염 시 화면 보호.
  4. DB UNIQUE 제약은 부적합: 죽은 작업지시의 매핑 행이 남는 구조라 ORDER_SEQ 유니크는 정상 재발행도 차단. MariaDB filtered unique 미지원.
- 분석/실행 스크립트: 세션 scratchpad check_ts_dup*.py, analyze_dup_deps.py, fix_dup_controls.py (pymysql, 121.165.20.66/smd). 산출물 MD: 바탕화면 `MD\거래명세표_작업지시번호_중복_원인분석_260703.md`.
