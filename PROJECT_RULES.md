# Tomes 프로젝트 규칙

에이전트 제품과 무관한 제품·개발·안전 규칙의 정본이다. 운영 방식은 `AGENTS.md`, 경로는 `PATHS.md`, 현재 상태는 `HANDOFF.md`를 따른다.

## 제품과 구조

- `%클라우드`: Spring Boot 본 애플리케이션 (`Projects/Tomes-Cloud`)
- `%테스트`: 테스트 자동화 (`Projects/Test-Automize`)
- `&하네스`: 이 저장소 루트
- 기술 스택: Java 21, Spring Boot 3.5, Gradle, WAR, MyBatis XML, JSP/JSTL, ParamQuery Grid 11.0.0, MariaDB, Redis

## 변경 불변식

- 기존 MyBatis `queryId`를 변경하지 않는다.
- 신규 DB 비밀번호, JWT 시크릿, API 키를 저장소 파일에 하드코딩하지 않는다.
- ParamQuery Grid는 11.0.0 API만 사용한다.
- JSP와 연결된 Java 메서드 시그니처·URL 매핑을 요청 없이 바꾸지 않는다.
- SQL은 기존 `sqlMaps/` 구조를 따르고 요청 없이 새 매퍼 파일을 만들지 않는다.
- 비즈니스 로직은 ServiceImpl, DB 접근은 DaoImpl에 둔다. 컨트롤러에 비즈니스 로직을 넣지 않는다.
- 요청 범위 밖의 기능 추가·리팩터링·파일 수정을 하지 않는다.

## 변경 권한과 Git

- `%클라우드` Git 커밋·푸시는 사용자 몫이다. 해당 턴에 명시적으로 요청받은 경우만 수행한다.
- `&하네스`와 `%테스트` 변경은 검증 후 이번 작업 파일만 커밋·푸시한다.
- 기존 미커밋·미추적 파일을 자동 스테이징하거나 정리하지 않는다.
- force-push, rebase, reset, 광범위 삭제 등 파괴적 작업은 별도 승인을 받는다.
- 파일 삭제는 요청의 직접 결과일 때만 하며 정확한 대상을 먼저 확인한다.
- 제품 코드는 `Projects/Tomes-Cloud` 밖에서 수정하지 않는다. 하네스 상태 기록은 예외다.

## DB 안전

- 조건 없는 DELETE와 TRUNCATE를 실행하지 않는다.
- UPDATE·마이그레이션 전 대상 백업, 트랜잭션, 검증 SELECT를 준비한다.
- 운영 DB는 검증 후 사용자 확인을 받고 COMMIT한다.
- 테넌트 식별자는 USER_ID로 추정하지 않고 실제 SYSTEM_ID 경로를 확인한다.
- 이 MariaDB에서 빈 문자열 비교는 `!=''` 대신 `IS NOT NULL AND LENGTH(...) > 0`을 사용한다.

## 확장성과 보안

- 테넌트 1,000개 이상을 기준으로 N+1, 반복 조회, 풀스캔, 전역 락, 무페이지네이션 적재를 검토한다.
- 캐시 키에는 테넌트 격리와 적절한 만료·무효화 전략을 둔다.
- 사용자 입력, 권한 경계, SQL 조립, 파일·URL 처리 변경은 보안 회귀를 검토한다.
- 우려가 현실적이면 가정·영향·대안·검증 결과를 관련 handoff에 기록한다.

## 검증

- 저장소 주장은 원본 파일, 호출 경로, git 상태와 테스트로 확인한다.
- 코드 존재만으로 동작을 판정하지 않는다. 정의 → 호출·라우팅 → 실제 트리거를 추적한다.
- Java·매퍼 XML·YAML 변경: `%클라우드`에서 `.\gradlew build -q`
- 테스트 자동화 변경: `%테스트`에서 `py -m pytest tests\ -q`
- 화면 동작 변경: 관련 테스트 또는 `py -m qa_agent.agent_run --row {TC_ROW_NUMBER} --skip-global-seeds`
- Java·XML·YAML은 dev 서버 재기동 후 확인한다. JSP·CSS·JS는 핫리로드 상태를 확인한다.
- 결과는 통과·실패·미실행으로 구분하고 미실행 이유를 보고한다.

## 파일과 인코딩

- UTF-8(BOM 없음)을 사용한다.
- Python 텍스트 I/O와 subprocess는 UTF-8을 명시하고 콘솔 오류 처리는 `errors="replace"`를 사용한다.
- PowerShell 파일 I/O는 UTF-8을 명시하고 배치 파일은 `chcp 65001`을 사용한다.
- 로그·빌드 원문 전체를 대화나 handoff에 복사하지 않고 요약과 증적 경로만 남긴다.
