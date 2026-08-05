# 아키텍처: Tomes-Cloud

## 디렉토리 구조
```
src/main/
├── java/com/tomes/
│   ├── controller/       # REST API & 웹 컨트롤러
│   ├── service/          # 서비스 인터페이스
│   ├── service/impl/     # 서비스 구현체
│   ├── dao/              # DAO 인터페이스
│   ├── dao/impl/         # DAO 구현체
│   ├── domain/           # DTO / 요청-응답 객체
│   ├── entity/           # 핵심 엔티티
│   ├── config/           # 설정 클래스
│   ├── component/        # 유틸리티 컴포넌트
│   ├── security/         # 암호화·보안
│   ├── filter/           # 서블릿 필터
│   ├── interceptor/      # 요청 인터셉터
│   ├── schedule/         # 스케줄링 작업
│   └── exception/        # 예외 처리
├── resources/
│   ├── application*.yml  # 환경별 설정 (local / develop / production)
│   ├── logback-spring.xml
│   └── sqlMaps/          # MyBatis XML 매퍼
│       └── v1/           # API v1 매퍼
└── webapp/
    ├── WEB-INF/views/    # JSP 뷰 (140개+)
    └── resource/
        └── plugins/paramquery-11.0.0/
```

## 데이터 흐름
```
브라우저 (JSP + ParamQuery Grid)
  → Filter (CloudAutoLoginFilter, LogbackFilter)
  → Interceptor (JwtAuthInterceptor / FileTokenAuthInterceptor)
  → Controller
  → ServiceImpl (비즈니스 로직)
  → DaoImpl → MyBatis XML → MariaDB
  → JSON 응답 / JSP 렌더링
```

## 패턴
- MyBatis XML 기반 SQL (JPA 미사용)
- Apache Tiles로 JSP 공통 레이아웃 관리
- 기준코드: SF_GET_CODE_NM() DB 함수로 코드명 조회

## 멀티테넌트
- 도메인 기반 테넌트 식별: `dev-{SYSTEM_ID}.tomes.kr` 형태로 도입 기업별 서브도메인 부여
- SYSTEM_ID 컬럼으로 DB 데이터 기업별 분리
- 기준코드는 공통 기준으로 통일하되, 기업별 추가 요청 시 개별 설정 가능
- 현재 클라우드 제품은 회사가 정한 공통 규격을 고객에게 적용하며, 공통 기준코드는 주로 `BASIC`과 `USE_YN`으로 관리
- 정책성 데이터는 `BASIC`만 직접 참조하지 않고 `SYSTEM_ID`별 설정을 먼저 해석한 뒤 공통값으로 후퇴할 수 있는 구조를 사용
- 이 경계는 향후 고객 요구 중심의 온프라미스 제품에서도 동일 기능을 별도 복제하지 않고 정책 데이터만 바꿔 재사용하기 위한 것
- 온프라미스 전용 관리 기능은 실제 요구가 생길 때 추가하며, 현재는 테넌트 식별·정책 조회·기본값 결정 지점만 분리

## 상태 관리
- 서버 세션: Redis (Spring Session)
- 인증 상태: JWT 토큰 / 파일 토큰 (Interceptor에서 검증)
- 캐시: Redis (Spring Cache)
