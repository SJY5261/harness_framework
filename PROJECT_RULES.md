# 프로젝트 공통 규칙: Tomes-Cloud

이 파일은 에이전트 제품과 무관한 프로젝트·개발·안전 규칙의 정본이다. Codex 운영 방식은 `AGENTS.md`, 현재 작업 상태는 `HANDOFF.md`와 관련 `handoff/<작업>.md`를 따른다.

## 경로와 약칭

- `%클라우드` → `Projects\Tomes-Cloud` (Spring Boot 본 애플리케이션)
- `%테스트` → `Projects\Test-Automize` (테스트 자동화)
- `&하네스` → 저장소 루트
- 개인 PC 기간에는 하네스 루트가 `D:\tomes\harness-framework`다. 과거 문서의 `E:\harness_framework`는 동일한 하위 구조의 현재 루트로 해석한다.

## 기술 스택

- Java 21, Spring Boot 3.5, Gradle, WAR
- MyBatis XML, JSP/JSTL, ParamQuery Grid 11.0.0
- MariaDB, Redis

## 절대 위반 금지

- 기존 MyBatis `queryId`를 변경하지 않는다.
- 신규 DB 비밀번호, JWT 시크릿, API 키를 설정 파일에 하드코딩하지 않는다.
- ParamQuery Grid는 11.0.0 API만 사용한다.
- JSP 수정 시 연결된 Java 메서드 시그니처와 URL 매핑을 임의로 변경하지 않는다.
- SQL 매퍼는 기존 `sqlMaps/` 구조를 따르고 요청 없이 새 매퍼 파일을 만들지 않는다.
- 비즈니스 로직은 ServiceImpl, DB 접근은 DaoImpl에 둔다. 컨트롤러에 비즈니스 로직을 넣지 않는다.
- 요청 범위 밖의 구현·리팩터링·파일 수정을 하지 않는다.

## 자율 실행과 변경 권한

- `%클라우드` git 커밋은 사용자 몫이다. 해당 턴에 명시적으로 요청받은 경우에만 수행한다.
- `&하네스`의 관련 변경은 Codex가 검증 후 커밋·푸시한다. 관련 없는 기존 미커밋·미추적 파일을 포함하지 않는다.
- force-push, rebase, reset, 광범위 삭제 등 파괴적 작업은 별도 승인을 받는다.
- 파일 삭제 전 이유와 정확한 경로를 보고한다.
- `%클라우드` 작업은 `Projects\Tomes-Cloud` 밖의 제품 코드를 수정하지 않는다. 하네스 상태·HANDOFF 갱신은 예외다.
- 설정·권한 같은 민감한 변경은 무엇을·어떻게·왜 바꿀지 먼저 설명하고 승인을 받는다.

## DB 안전

- 전체 DELETE와 TRUNCATE를 실행하지 않는다.
- DB UPDATE·마이그레이션 전에는 대상 백업, 트랜잭션, 실행 후 검증 SELECT를 준비한다.
- 운영 DB는 검증 후 사용자 확인을 받고 COMMIT한다. 자의로 COMMIT하지 않는다.

## 확장성

- 기능 변경 시 테넌트 1,000개 이상을 기준으로 N+1, 반복 조회, 캐시 키 폭증·격리, 전역 락·풀스캔, 무페이지네이션 전체 적재를 검토한다.
- 테넌트 단위 격리, 증분 처리, 적정 캐시 키, 인덱스·페이지네이션을 기본 전제로 삼는다.
- 우려가 있으면 스케일 리스크, 부하 가정, 대안을 답변과 HANDOFF에 기록한다.

## HANDOFF

- `HANDOFF.md`는 공통 상태와 작업별 한 줄 포인터만 가진 인덱스다.
- 상세 경위·결정·검증·다음 단계는 관련 `handoff/<작업>.md`에 기록한다.
- 작업 분기점과 세션 종료 전에 상세 파일과 인덱스 한 줄을 갱신한다.
- 종결 작업은 상세 내용을 `logs/HANDOFF_ARCHIVE.md`로 옮긴 뒤 활성 인덱스에서 제거한다.

## 조사와 컨텍스트 절약

- 약 1,000줄 이상 파일은 `rg`로 범위를 좁힌 뒤 필요한 구간만 읽는다.
- 여러 파일 조사는 먼저 `rg`와 파일 목록으로 범위를 제한한다.
- 로그·빌드 출력은 실패 원인과 요약만 가져오고 대형 원문을 대화에 싣지 않는다.
- 3단계 이상 작업은 착수 전에 단계와 완료 조건을 공유한다.

## 인코딩

- 소스와 문서는 UTF-8(BOM 없음)으로 저장한다.
- Python 텍스트 입출력과 subprocess에는 `encoding="utf-8"`을 명시하고 콘솔은 UTF-8 `errors="replace"`로 구성한다.
- PowerShell 파일 입출력은 UTF-8을 명시한다.
- 배치 파일은 `chcp 65001`을 사용한다.
- 커밋 메시지와 로그 포맷에는 cp949에서 깨지는 비ASCII 장식 문자를 쓰지 않는다.

## 검증과 보고

- 사실과 추론을 구분하고, 추론은 근거와 함께 표시한다.
- 저장소·코드·동작 주장은 원본 파일, 호출 경로, git 상태, 빌드·테스트로 확인한다.
- 코드 존재만으로 화면 노출이나 동작을 판정하지 않는다. 정의 → 호출·라우팅 → 실제 트리거를 추적하고 가능하면 실화면으로 검증한다.
- Java·설정 변경은 Gradle 빌드, 로직 변경은 관련 pytest 또는 실화면 QA를 수행한다.
- 검증 결과는 통과·실패·미실행과 이유를 답변과 HANDOFF에 기록한다.
- 사용자 지적이 발생하면 검증 수행 여부, 놓친 이유, 근본원인, 보강한 검증 방법까지 보고한다.

## 주요 검증 명령

```powershell
cd Projects\Tomes-Cloud
.\gradlew build -q

cd ..\Test-Automize
py -m pytest tests\ -q

py -m qa_agent.agent_run --row {TC_ROW_NUMBER} --skip-global-seeds
```

Java·매퍼 XML·yml 변경은 dev 서버 재기동이 필요하다. JSP·CSS·JS는 JSP 핫리로드 설정이 활성일 때 즉시 반영된다.
