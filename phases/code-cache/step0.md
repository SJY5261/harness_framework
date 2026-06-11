# Step 0: server-cache

## 읽어야 할 파일

먼저 아래 파일들을 읽고 프로젝트의 아키텍처와 설계 의도를 파악하라:

- `E:\harness_framework\docs\ARCHITECTURE.md`
- `E:\harness_framework\docs\ADR.md`
- `E:\Tomes-Cloud\src\main\java\com\tomes\controller\JsonController.java` (81~85행: /json-list 엔드포인트)
- `E:\Tomes-Cloud\src\main\java\com\tomes\service\impl\InnodaleServiceImpl.java` (수정 대상)
- `E:\Tomes-Cloud\src\main\java\com\tomes\service\InnodaleService.java` (인터페이스)
- `E:\Tomes-Cloud\src\main\java\com\tomes\service\impl\SystemServiceImpl.java` (429~439행: getSessionCodeList — 이미 @Cacheable 적용됨)
- `E:\Tomes-Cloud\src\main\java\com\tomes\service\SystemService.java` (인터페이스)
- `E:\Tomes-Cloud\src\main\java\com\tomes\domain\code\CodeSearch.java` (실제 필드명·세터 확인 필수)
- `E:\Tomes-Cloud\src\main\resources\sqlMaps\system.xml` (233~248행: selectSessionCodeList 쿼리)
- `E:\Tomes-Cloud\src\main\java\com\tomes\component\CommonUtility.java` (34~95행: getParameterMap — 세션의 LOGIN_SYSTEM_ID가 paramMap에 병합되는 과정)

## 배경

공통코드 조회(`/json-list`, queryId=`systemMapper.selectSessionCodeList`)는
페이지·팝업 로드마다 MariaDB를 조회한다(약 523건).
그런데 `SystemServiceImpl.getSessionCodeList(CodeSearch)`가 **정확히 같은
쿼리**를 이미 Redis @Cacheable(cacheManager="everyHour", 키:
systemId:highCode:codeCd)로 감싸고 있다. 이 step은 `/json-list` 경로가
그 캐시를 타도록 위임 분기만 추가한다.

## 작업

`InnodaleServiceImpl.getList(Map<String, Object> hashMap)`를 수정한다.

1. `SystemService`를 InnodaleServiceImpl에 주입한다.
   기존 클래스의 의존성 주입 스타일(필드 @Autowired / 생성자)을 그대로 따른다.
2. 메서드 앞부분에 분기를 추가한다 (의사 시그니처):

```java
String queryId = (String) hashMap.get("queryId");
String systemId = (String) hashMap.get("LOGIN_SYSTEM_ID");
if ("systemMapper.selectSessionCodeList".equals(queryId)
        && systemId != null && !systemId.isEmpty()) {
    CodeSearch codeSearch = new CodeSearch();
    // CodeSearch.java를 읽고 실제 세터명 사용:
    // systemId   <- hashMap.get("LOGIN_SYSTEM_ID")
    // highCode   <- hashMap.get("HIGH_CD")   (없으면 null 그대로)
    // codeCd     <- hashMap.get("CODE_CD")   (없으면 null 그대로)
    return systemService.getSessionCodeList(codeSearch);
}
// 기존 로직 그대로 (다른 queryId는 동작 불변)
```

핵심 규칙 (위반 금지):

- **멀티테넌트 안전**: LOGIN_SYSTEM_ID가 null/빈 문자열이면 위임하지 말고
  기존 경로로 보낸다. 이유: 캐시 키가 테넌트를 구분하지 못하면
  타사 코드가 노출된다.
- `getSessionCodeList`의 @Cacheable 어노테이션(키·TTL·cacheManager)을
  변경하지 마라. 이유: 기존 호출처가 있을 수 있고 step1의 evict가
  이 캐시 이름을 기준으로 동작한다.
- 같은 빈 내부 호출(self-invocation)은 @Cacheable 프록시를 우회한다.
  반드시 주입받은 `systemService` 빈을 통해 호출하라.
- 순환 의존성이 발생하면(SystemServiceImpl이 InnodaleService를 주입하는
  경우) 임의로 구조를 바꾸지 말고 status를 `blocked`로 기록하고 중단하라.
  단, 현재 SystemServiceImpl은 innodaleDao(DAO)만 사용하므로
  발생하지 않을 것으로 예상된다.

## Acceptance Criteria

```bash
cd E:/Tomes-Cloud && ./gradlew build -q   # 컴파일 에러 없음
```

## 검증 절차

1. 위 AC 커맨드를 실행한다.
2. 아키텍처 체크리스트를 확인한다:
   - ARCHITECTURE.md 디렉토리 구조를 따르는가? (서비스 로직은 ServiceImpl에만)
   - ADR 기술 스택을 벗어나지 않았는가? (ADR-004: Redis Spring Cache)
   - CLAUDE.md CRITICAL 규칙을 위반하지 않았는가? (queryId 변경 금지)
3. 결과에 따라 `E:\harness_framework\phases\code-cache\index.json`의 step 0을 업데이트한다:
   - 성공 → `"status": "completed"`, `"summary": "산출물 한 줄 요약 (수정 파일 경로 포함)"`
   - 수정 3회 시도 후에도 실패 → `"status": "error"`, `"error_message": "구체적 에러 내용"`
   - 사용자 개입 필요 → `"status": "blocked"`, `"blocked_reason": "구체적 사유"` 후 즉시 중단

## 금지사항

- MyBatis XML(sqlMaps/)의 기존 queryId를 변경하지 마라. 이유: 컨트롤러·서비스가 문자열로 직접 참조하므로 런타임 오류 발생 (CLAUDE.md CRITICAL).
- `selectSessionCodeList` 외 다른 queryId의 처리 경로를 바꾸지 마라. 이유: /json-list는 전 화면이 공유하는 범용 엔드포인트다.
- 새 캐시 어노테이션·새 CacheManager를 만들지 마라. 이유: 기존 getSessionCodeList 캐시를 재사용하는 것이 이 설계의 핵심이다.
- application-*.yml에 신규 비밀번호·시크릿을 추가하지 마라 (CLAUDE.md CRITICAL).
- E:\Tomes-Cloud 외부 디렉토리의 파일을 수정하지 마라 (phases/code-cache/index.json 상태 업데이트는 예외).
- 기존 테스트를 깨뜨리지 마라.
