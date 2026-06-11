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

## 상태 관리
- 서버 세션: Redis (Spring Session)
- 인증 상태: JWT 토큰 / 파일 토큰 (Interceptor에서 검증)
- 캐시: Redis (Spring Cache)
