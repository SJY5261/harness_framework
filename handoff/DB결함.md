# DB결함 — 현재 인수인계

_최종 상태: 2026-07-31 원격 브랜치·제품 diff·라이브 DB·테스트를 재검토한 상태를 유지한다. 별도 코드 이해 리뷰는 사용자 판단에 따라 폐기했다. 긴 진행 이력은 [역사 보존본](../logs/handoff/DB결함_2026-07-28_history.md)에 있다._

## 현재 상태

- `%클라우드` 관련 기능 변경은 커밋 `88bf7dc`이며, `feature-control-0713`의 로컬·upstream·실제 원격 HEAD는 모두 `2aad3db`로 일치한다.
- 현재 PR 비교는 `origin/main` `fb3c240` → `origin/feature-control-0713` `2aad3db`이고 diff는 4파일 `+504/-142`다.
- 사용자 지정 폴더 `C:\Users\User\Desktop\PR\[07.28 DB결함 수정 리뷰]`에는 현재 상태를 반영한 MD 정본과 자체완결 HTML 두 파일만 있다.
- `C:\Users\User\Desktop\PR\[07.31 DB결함 코드 학습 가이드]`에는 신입 개발자가 코드·DB를 처음 인수인계받는 기준으로 수주→작업지시 전체 흐름과 번호·내부키·10개 테이블의 핵심 컬럼·실제 FK와 논리 조인·이중발행 방지·사본 동기화·삭제 전파·DB 계약을 대분류한 MD 정본과 자체완결 HTML 두 파일만 있다. 자동발번 화면명·Map 키·`TBL_SYSTEM` 컬럼 차이, 프로시저 실제 추가 블록, `CONTROL_NUM` 백업·백필·`NOT NULL` DDL, 스키마 확인 SQL도 포함한다.
- `C:\Users\User\Desktop\PR\[07.29 DB결함 코드 이해 리뷰]`는 2026-07-31 사용자 판단에 따라 AI 슬롭으로 폐기했다. 해당 산출물은 정본·참고자료로 재사용하지 않는다.
- 리뷰 범위는 사용자가 직접 변경한 `CONTROL_NUM` 백업·백필·`NOT NULL` DDL과 `smd.SP_CONTROL_BATCH` 가드·검증·선택적 복구 SQL이다.
- 외부 협력자의 KAN-64/STP 변경과 다른 후속 변경은 리뷰에서 제외했다.
- 제품 GitHub PR과 PR 기반 check run은 아직 없다.
- Sites는 이번 내용으로 재게시하지 않았다.

## 확정 결정

- DB 적용 대상은 `smd`만이며 `smd2`, `jet`은 제외한다.
- `smd.BAK_TBL_CONTROL_CTRLNUM_260720` 22행과 `SP_CONTROL_BATCH_BAK_260720`은 복구 지점으로 유지한다.
- 프로시저 복구는 전체 백업 덮어쓰기보다 이번 잠금·오류·`NOT EXISTS` 블록만 선택적으로 제거해 범위 밖 변경을 보존한다.
- 실제 실행 원문이 보존되지 않은 SQL은 실행문으로 단정하지 않고, 기록 기반 재현 SQL과 라이브 `SHOW FULL COLUMNS`·`SHOW CREATE PROCEDURE` 근거를 구분한다.
- Claude 또는 별도 리뷰어를 자동 호출하지 않는다. 추가 독립 검토는 사용자가 명시적으로 요청하거나 새 고위험 판단이 생겼을 때만 진행한다.

## 최종 검증

- 원격 커밋 `2aad3db` clean worktree에서 `gradlew build -q --max-workers=4 --no-daemon` PASS.
- 제품 PR diff 정형성 PASS, `order.xml` XML 파싱 PASS, mapper statement id 208개 중 중복 0.
- `CONTROL_NUM`: NULL 0건, nullable=`NO`, 길이 30, 기존 문자셋·collation 유지.
- 백업 `BAK_TBL_CONTROL_CTRLNUM_260720` 22행과 `SP_CONTROL_BATCH_BAK_260720` 유지.
- `SP_CONTROL_BATCH`: 기존 `DEFINER`, 원본 주문 잠금, SQLSTATE `45000`, `NOT EXISTS`, `S10R40` 제외, 내부 COMMIT 없음 유지.
- 동시 이중 매핑: 잠금 대기 후 SQLSTATE `45000` 차단 확인.
- 정상 비재고·`S10R40` 회귀: 생성 흐름 확인 후 테스트 데이터 롤백, 잔재 0.
- 살아 있는 이중 매핑 0, 테스트 표식 잔재 0.
- `%테스트`: 직접 관련 호환 테스트 1 PASS, 전체 191 PASS/기존 OSR-173 계획 불일치 3 FAIL.
- 리뷰 MD·HTML의 사용자 변경 범위, `<details>` 짝, UTF-8 BOM 없음, 자체완결 HTML을 확인했다.
- 새 코드 학습 가이드는 MD 1,418줄이며 MD·HTML의 제목 87개·표 24개·코드 블록 35개·접기 영역 5개가 일치한다. HTML 목차 75개, 외부 의존성 0, UTF-8 BOM 없음, 브라우저 page error 0을 확인했다.
- 2026-07-31 라이브 `smd.INFORMATION_SCHEMA`에서 문서의 핵심 10개 테이블과 `TBL_*.COLUMN` 참조 39개가 모두 존재함을 대조했다. 자료형·NULL·PK·인덱스, 물리 FK 2개, 매핑 트리거 3개와 `SP_TRIG_CONTROL_PART_ORDER`의 `_MAIN` 재구성 경로를 확인했다.
- 신규 스키마 확인에서 `TBL_CONTROL.CONTROL_NUM` 인덱스가 비유니크이고, `REGIST_NUM` 길이가 원본 50자·스테이징/사본 30자로 다름을 확인했다. 현재 번호 형식에는 즉시 영향이 없어 문서 주의점으로만 기록하고 코드·DDL은 변경하지 않았다.
- 문서에 적은 Java 메서드 12개와 MyBatis id 16개가 현재 코드에 존재하고 대상 4파일에 미커밋 diff가 없음을 대조했다.
- 폐기 후 `[07.29 DB결함 코드 이해 리뷰]`의 원래 경로가 존재하지 않음을 확인했다. 복구가 필요하면 Windows 휴지통에서 되돌릴 수 있다.

## 별도 후속 후보

다음 항목은 완료 범위에 포함하지 않았으며 자동 진행하지 않는다.

- `TBL_OUT_BARCODE.CONTROL_SEQ` 비유니크 인덱스: 영향분석 완료, 현재 인덱스 없음·23,978행, DDL 적용 결정 대기.
- 기존 매핑 없는 활성 컨트롤 `16031 / AUTO-16031`: 활성 1행·살아 있는 매핑 0행 유지, 정리 결정 대기.
- 과거 복사 컬럼 드리프트: 2026-07-14 수량 4·단가 2건에서 현재 수량 5·단가 2건으로 변경, 추가 수량 1건 의미 판별 후 보정 결정.
- `%테스트` `44c14cc`: 저장소·커밋·push 분리는 완료했지만 별도 PR은 미생성.

## 재개 순서

1. 제품 PR을 만들거나 리뷰 파일을 게시할 때 현재 원격 ref가 위 기준과 같은지 다시 확인한다.
2. 사용자가 위 후속 후보 또는 추가 독립 검토를 명시했는지 확인한다.
3. 관련 DB·git 상태를 다시 측정한다.
4. DB 변경이면 `docs/processes/DB_CHANGE_REPORT.md`와 사용자 승인 절차를 적용한다.
5. 과거 경위나 세부 SQL이 필요할 때만 역사 보존본을 읽는다.
