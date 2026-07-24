# Step 1: cache-evict

## 읽어야 할 파일

먼저 아래 파일들을 읽고 프로젝트의 아키텍처와 설계 의도를 파악하라:

- `docs/ARCHITECTURE.md`
- `docs/ADR.md`
- `E:\Tomes-Cloud\src\main\java\com\tomes\service\impl\SystemServiceImpl.java`
  (63~136행: commonCodeModifyGrid — 수정 대상,
   429~439행: getSessionCodeList — 캐시 이름 확인,
   12~13행: CacheEvict/Cacheable import 이미 존재)
- `E:\Tomes-Cloud\src\main\java\com\tomes\config\RedisCacheConfig.java` (cacheManager 빈 목록)
- `E:\Tomes-Cloud\src\main\java\com\tomes\service\impl\InnodaleServiceImpl.java` (step0에서 수정됨 — 위임 분기 확인)

이전 step에서 만들어진 코드를 꼼꼼히 읽고, 설계 의도를 이해한 뒤 작업하라.

## 배경

step0에서 `/json-list`의 공통코드 조회가
`getSessionCodeList`의 Redis 캐시(TTL 1시간)를 타게 되었다.
그런데 시스템 관리자가 공통코드 관리 화면에서 코드를 저장하면
(`SystemServiceImpl.commonCodeModifyGrid` → TBL_CODE/TBL_CODE_LANG
INSERT·UPDATE) 캐시가 무효화되지 않아 최대 1시간 동안
구버전 코드가 화면에 나간다. 이 step은 저장 시 캐시를 비운다.

## 작업

`SystemServiceImpl.commonCodeModifyGrid(Map<String, Object> map)` 메서드에
@CacheEvict를 추가한다:

```java
@CacheEvict(
    value = "com:tomes:service:impl:SystemServiceImpl:getSessionCodeList",
    allEntries = true,
    cacheManager = "everyHour"
)
```

핵심 규칙 (위반 금지):

- `value`는 getSessionCodeList의 @Cacheable `value`와 **문자 단위로 동일**해야
  한다. 다르면 엉뚱한 캐시를 지우고 실제 캐시는 남는다.
- `cacheManager = "everyHour"`를 명시하라. 이유: RedisCacheConfig에
  @Primary가 every5Seconds로 지정되어 있어, 생략하면 다른 매니저가 잡힌다.
- `allEntries = true`를 사용하라. 이유: 캐시 키가
  systemId:highCode:codeCd 조합이라 특정 테넌트의 키만 골라 지우는 것은
  Spring 캐시 추상화로 불가능하다. 코드 변경은 드문 이벤트이므로
  전체 삭제 비용은 무시 가능하며, 데이터 정합성이 우선이다.
- commonCodeModifyGrid의 **본문 로직은 한 줄도 변경하지 마라.**
  어노테이션 추가만 허용된다.

## Acceptance Criteria

```bash
cd E:/Tomes-Cloud && ./gradlew build -q   # 컴파일 에러 없음
```

## 검증 절차

1. 위 AC 커맨드를 실행한다.
2. 아키텍처 체크리스트를 확인한다:
   - getSessionCodeList의 @Cacheable value 문자열과 @CacheEvict value 문자열이 완전히 일치하는가?
   - cacheManager="everyHour"가 명시되어 있는가?
   - PROJECT_RULES.md의 변경 불변식을 위반하지 않았는가?
3. 결과에 따라 `phases/code-cache/index.json`의 step 1을 업데이트한다:
   - 성공 → `"status": "completed"`, `"summary": "산출물 한 줄 요약"`
   - 수정 3회 시도 후에도 실패 → `"status": "error"`, `"error_message": "구체적 에러 내용"`
   - 사용자 개입 필요 → `"status": "blocked"`, `"blocked_reason": "구체적 사유"` 후 즉시 중단

## 금지사항

- commonCodeModifyGrid의 비즈니스 로직(INSERT/UPDATE 분기, JSON 파싱)을 수정하지 마라. 이유: 이 step의 범위는 캐시 무효화 어노테이션 추가뿐이다.
- 다른 메서드의 @Cacheable(getSessionCodeList, selectGfileFileImageInfo 등)을 건드리지 마라. 이유: step0이 의존하는 캐시 동작이 바뀐다.
- 주석 처리된 기존 @Cacheable/@CacheEvict(421행, 460행 등)를 살리지 마라. 이유: 과거에 의도적으로 비활성화된 것으로, 이번 작업 범위가 아니다.
- MyBatis XML의 기존 queryId를 변경하지 마라 (PROJECT_RULES.md).
- 기존 테스트를 깨뜨리지 마라.
