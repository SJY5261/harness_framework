# 정적 리소스 캐시 적용 - 메인 로드 병목 분석/수정 보고

> 대상: %클라우드(Tomes-Cloud)
> 작성: 2026-06-23
> 상태: 워킹트리 미커밋(config 2파일). 커밋은 사용자 몫.
> 측정: curl + Playwright(headless) 실측. 분석은 answer-reviewer 검증 반영.

---

## 1. 배경 / 문제

메인화면 로드가 느리고 "점점 늘어나는" 체감. 네트워크 탭 기준 비교 요청에서 출발.

- 캐싱 이전/이후 비교 기록(HANDOFF.md): 캐싱 ON/OFF로 메인 로드시간 차이가
  노이즈 범위(변동 4~9초)라, 서버 Redis/코드 캐싱은 로드시간과 사실상 무관함을 이미 확인.
- 따라서 실제 병목을 새로 측정해 규명.

---

## 2. 측정으로 드러난 병목 (현재 dev bootRun 기준)

전체 리소스 전수 집계(Resource Timing API):

- 리소스 약 150건 / 총 약 2.5MB, 단일 호스트(smd.localhost:8081)
- 타입별: script 49개(~1.4MB), img 20, css 33, link 33, 데이터 xhr 15
- 가장 느린 리소스 TOP이 0.7~5KB짜리 작은 이미지인데 각 8~10초.
  그런데 서버 응답시간(TTFB)은 1.2초 미만, curl 격리 측정은 3~22ms.
  -> 시간 대부분이 다운로드/서버처리가 아니라 "대기(큐잉)".

### 핵심 단서 - 정적 파일이 매번 재다운로드됨
- 새로고침인데도 전송량이 2.3MB 그대로(150건 재다운로드).
- 정적 응답 헤더가 캐시 금지였음:
  ```
  Cache-Control: no-cache, no-store, max-age=0, must-revalidate
  Expires: 0
  ```

---

## 3. 근본 원인

`/resource/**` 의 모든 JS/CSS/이미지가 `no-store`로 내려와 브라우저가
아무것도 캐시하지 못함 -> 매 로드/새로고침마다 150건/2.3MB 재다운로드.

원인은 설정 두 곳:

1. 커스텀 리소스 핸들러가 캐시 헤더를 안 줌
   - `WebContextConfig.addResourceHandlers`가 `/resource/**`를 커스텀 등록하면서
     `setCacheControl`을 호출하지 않음.
   - Spring Boot의 `spring.web.resources.cache.cachecontrol`(yml: max-age 365d)은
     자동 핸들러에만 적용되고 커스텀 핸들러엔 안 먹음 -> yml 설정이 죽어 있었음.

2. Spring Security 기본 헤더라이터
   - `SecurityConfig`가 `.headers(...)`에서 frameOptions(disable)만 손대고
     나머지 기본 헤더라이터는 그대로 둠.
   - 응답에 `Cache-Control`이 없을 때 Security가 `no-store`를 써넣음.
     (응답의 `X-Content-Type-Options: nosniff`도 같은 기본 헤더라이터 흔적)

정리: 핸들러가 캐시를 안 정함(1) -> 헤더 없음 -> Security가 no-store로 채움(2).

### 보조 원인 (dev 한정)
- HTTP/1.1 단일 호스트 + 150요청 -> 동시연결 ~6개에 줄 서는 큐잉.
- 캐시가 없으니(위 근본원인) 이 큐잉 비용을 매 로드 전액 지불.
- 단, 운영(application-production.yml)은 `http2.enabled: true`라 멀티플렉싱 ->
  이 6연결 큐잉은 운영에선 다름(주로 dev 측정 환경 문제).

---

## 4. 적용한 수정 (config 2파일, 미커밋)

### 4.1 WebContextConfig.java - 캐시 헤더 부여(핵심)
```java
registry.addResourceHandler("/resource/**").addResourceLocations("/resource/")
        .setCacheControl(CacheControl.maxAge(365, TimeUnit.DAYS).cachePublic());
```
import 추가: `org.springframework.http.CacheControl`, `java.util.concurrent.TimeUnit`.
swagger/webjars 핸들러는 무변경.

효과: `/resource/**` 응답에 `Cache-Control: max-age=31536000, public` 부여.

### 4.2 SecurityConfig.java - 정적 경로를 Security에서 제외
```java
@Bean
public WebSecurityCustomizer webSecurityCustomizer() {
    return web -> web.ignoring().requestMatchers("/resource/**");
}
```
import 추가: `...web.configuration.WebSecurityCustomizer`. 기존 filterChain 빈 무변경.

역할: `/resource/**`를 Security 필터 체인에서 완전히 제외.
- 주 목적은 정적 요청의 보안 필터 오버헤드 제거(SecurityContext 로딩/CSRF/세션 처리 등)
  + no-store를 찍는 기본 헤더라이터 경로 제거.

### 4.3 둘의 관계 (정확히)
- 변경 4.1(setCacheControl)만으로도 `max-age` 헤더는 보호됨.
  Spring Security `CacheControlHeadersWriter`는 응답에 `Cache-Control`이 이미 있으면
  덮어쓰지 않기 때문(추론, Spring Security 동작 기준).
- 변경 4.2는 "덮어쓰기 방지"가 아니라 필터 오버헤드 제거가 본 목적.
  둘을 함께 둔 건 헤더 + 오버헤드를 깔끔히 정리하려는 것.

---

## 5. 효과 (실측, 동일 스크립트/머신)

| 항목 | 수정 전 | 수정 후 | 개선 |
|---|---|---|---|
| 정적 헤더 | no-cache,no-store,max-age=0 | max-age=31536000, public | - |
| 새로고침 load 중앙값(reload x8) | 15791 ms | 3177 ms | 약 -80% |
| 새로고침 전송량 | 2297 KB | 60 KB | 약 -97% |
| 새로고침 load 이벤트 | 12658 ms | 1121 ms | 약 -91% |
| json-list-cache.js (매 reload) | 3~8초 | 0.1 ms | 캐시 적중 |

- 첫 진입(콜드 캐시)은 그대로 약 10초 - 캐시가 비어 한 번은 받아야 함.
  개선은 새로고침/화면전환부터.
- 수정 후 새로고침에 남는 약 3초는 정적이 아니라 데이터 AJAX 쿼리(차트/팝업 선조회 등).

---

## 6. 주의 / 후속

1. 배포 시 cache-busting 필수
   - `max-age=1년`이라 파일명/쿼리스트링 버저닝이 없으면 변경된 JS/CSS가
     브라우저에 1년간 갱신 안 될 수 있음. 운영 반영 시 반드시 함께 도입.
   - ParamQuery/plugins 같은 버전 디렉토리는 안전. 앱 자체 파일(body-script.js 등)이 대상.

2. web.ignoring()은 `/resource/**`에 보안 필터를 전부 우회
   - 정적 공개 리소스라 허용 가능하나, 이 경로엔 인증/CSRF가 안 걸린다는 점 인지.

3. 운영 실제 헤더 확인 권장
   - no-store 근본원인은 프로필 공통 코드라 운영에도 동일 적용될 공산.
     단 운영 앞단 NCP 인프라(LB/캐시)가 헤더를 덮을 가능성은 코드만으론 판단 불가.
   - 운영 도메인에 `curl -I`로 정적 헤더를 찍어 효과를 확정할 것.

4. 추가 개선 후보(이번 범위 밖)
   - 2순위: 리소스 개수 축소(번들/스프라이트) - 콜드 첫 로드에 효과.
   - 3순위: 로컬에도 http2.enabled(운영엔 이미 있음) - 측정/체감을 운영과 정렬.

---

## 7. 변경 파일

| 파일 | 변경 |
|---|---|
| src/main/java/com/tomes/config/WebContextConfig.java | /resource/** 핸들러에 setCacheControl + import 2 |
| src/main/java/com/tomes/config/SecurityConfig.java | WebSecurityCustomizer(/resource/** ignoring) + import 1 |

- 워킹트리 미커밋. %클라우드 커밋은 사용자 몫.
- (별건) 쿼리 캐시 service 4파일은 별도 커밋 b504ace "Redis 캐시 쿼리 추가 반영"(브랜치 feature_caching_2606 + Danga_estimate)으로 반영됨.
