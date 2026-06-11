# 프로젝트: Tomes-Cloud

## 프로젝트 약칭 (대화 지칭 규칙)
사용자가 아래 약칭으로 말하면 해당 디렉토리를 가리키는 것으로 해석한다. 답변에서도 이 약칭을 사용해도 된다.
- `%클라우드` → `E:\Tomes-Cloud` (Spring Boot 본 애플리케이션)
- `%테스트` → `E:\Test-Automize` (최신 테스트 자동화 프로젝트. 구버전 `E:\Tomes-AutoTest`는 삭제됨)
- `&하네스` → `E:\harness_framework` (하네스 프레임워크)

## 기술 스택
- Java 21 + Spring Boot 3.5
- MyBatis (SQL 매퍼, XML 기반)
- JSP + JSTL (뷰 레이어)
- ParamQuery Grid 11.0.0 (UI 그리드)
- MariaDB (DB), Redis (세션/캐시)
- Gradle (빌드), WAR 배포

## 아키텍처 규칙

### CRITICAL — 절대 위반 금지
- CRITICAL: MyBatis XML의 기존 queryId를 변경하지 마라. 컨트롤러·서비스에서 문자열로 직접 참조하므로 변경 시 런타임 오류 발생.
- CRITICAL: application-*.yml에 신규 DB 비밀번호·JWT 시크릿·API 키를 하드코딩하지 마라. 기존 하드코딩은 유지하되 신규 추가 시 금지. (보안 정책 미확정으로 추후 변경 가능)
- CRITICAL: ParamQuery Grid는 반드시 11.0.0 API를 사용하라. 7.x 문법 사용 금지.
- CRITICAL: JSP 수정 시 연결된 Java 컨트롤러의 메서드 시그니처·URL 매핑을 임의로 변경하지 마라.
- CRITICAL: SF_GET_CODE_NM() 호출 시 첫 번째 인자는 TBL_CODE_GROUP1 기준값을 사용하라. (해당 테이블 구조 변경 예정으로 이 조항은 추후 수정될 수 있음)

### 일반 규칙
- SQL 매퍼 XML은 sqlMaps/ 하위에만 추가하고, 새 XML 파일을 무단 생성하지 마라.
- 비즈니스 로직은 ServiceImpl에, DB 접근은 DaoImpl에만 작성한다. 컨트롤러에 로직을 넣지 마라.
- 기존 Test-Automize 테스트를 깨뜨리는 변경을 하지 마라.
- 지시된 범위 외 추가 구현·리팩터링을 하지 마라.
- 작업 전 관련 파일(Controller, ServiceImpl, DaoImpl, XML, JSP)을 모두 읽고 흐름을 파악한 뒤 수정하라.

## 자율 실행 안전 규칙
- 파일을 삭제하기 전에 반드시 삭제 이유와 대상 경로를 보고한다.
- 작업 지시에 명시된 파일 외에 다른 파일을 수정하지 마라.
- E:\Tomes-Cloud 외부 디렉토리의 파일을 수정하지 마라.
- DB 데이터를 직접 삭제(DELETE 전체, TRUNCATE)하지 마라.
- 확신이 없으면 실행하지 말고 현재 상태를 보고한 뒤 지시를 기다린다.
- 설정 변경(settings.json, 권한 모드 등) 같은 민감한 작업은 yes/no를 묻기 전에, 무엇을·어떻게·왜 바꿀지 답변 본문으로 상세히 설명한 뒤 확인을 받는다. (권한 다이얼로그/툴 호출의 짧은 설명만으로는 파악이 어려우므로)

## 세션 관리 규칙
- Handoff 상시 유지: 작업 분기점마다, 그리고 세션 종료 전에 항상 `&하네스\HANDOFF.md`를 갱신해 다음 세션이 인수인계받게 한다. 포맷: 작업 목표 / 완료 / 진행중·미완 / 다음 단계 / 블로커·주의 / 관련 파일·경로.
- 컨텍스트 최적화(목표 임계치 ≈ 50%): 한계까지 채우면 핵심 정보가 묻혀 답변 품질이 떨어지므로, 여유 있을 때 새 세션으로 넘긴다. 체험하며 임계치는 조정 가능.
- 트리거 역할 분담:
  - 정확한 50% 감지는 **사용자(화면 게이지)** 권한. 사용자가 "초기화"라고 하면 즉시 HANDOFF 최종 갱신 후 `/clear` 안내.
  - 나는 보조로, 대화량 기준 추정으로 "절반쯤 온 듯" 알림을 줄 수 있으나 부정확함을 명시한다.
  - [한계] 모델은 세션을 스스로 `/clear` 할 수 없고 50%를 정확히 자동 감지하지 못한다. 마지막 `/clear`는 사용자 동작이며, 그 직전까지(HANDOFF 갱신, 재개용 한 줄 명령 제시)는 자동으로 준비한다.

## 인코딩 규칙 (Windows cp949 환경 — 위반 시 반복 장애)
이 환경은 Windows 한국어 로케일(ANSI 코드페이지 cp949)이다. 인코딩을 명시하지 않은 텍스트 입출력은 cp949로 처리되어, UTF-8 한글·특수문자(`—`, `✓`, 이모지)에서 UnicodeDecodeError/UnicodeEncodeError가 발생한다. (실제 사례: execute.py가 CLAUDE.md 읽기·git 출력 디코드·print에서 3회 연속 크래시)

- **Python**: `open()`, `Path.read_text()/write_text()`, `subprocess.run(text=True)`에 **항상 `encoding="utf-8"` 명시** (외부 프로세스 출력은 `errors="replace"` 권장). 새 스크립트는 시작부에 `sys.stdout.reconfigure(encoding="utf-8", errors="replace")` (stderr 동일) 추가. 실행 시 `PYTHONUTF8=1` 병행 권장.
- **PowerShell 5.1**: 파일 쓰기 시 `-Encoding utf8` 명시 (기본값은 UTF-16/ANSI).
- **배치(.bat)**: 첫 부분에 `chcp 65001` 포함.
- **커밋 메시지·로그 포맷 문자열**: 비ASCII 특수문자(`—`, `✓`, `↻` 등) 사용 금지. ASCII(`-`, `OK`, `retry`)로 대체. 이유: cp949 콘솔로 출력될 수 있다.
- **파일 생성**: 소스·문서 파일은 UTF-8(BOM 없음)로 저장한다.

## 개발 프로세스
- 커밋 메시지는 conventional commits 형식을 따른다 (feat:, fix:, refactor:, chore:).
- 사실과 추론을 구분한다. 모르는 것은 모른다고 말하고, 추론이 필요한 경우 "추론:" 으로 명시한다.

## 명령어
```bash
# 빌드 (컴파일 오류 확인)
cd E:/Tomes-Cloud && ./gradlew build -q

# 단위 테스트
cd E:/Test-Automize && pytest tests/ -q

# 실제 화면 QA 검증 (Step AC에서 사용)
cd E:/Test-Automize && python -m qa_agent.agent_run --row {TC_ROW_NUMBER} --skip-global-seeds
```

## 주요 경로 참조
PATHS.md 참조: E:\harness_framework\PATHS.md
