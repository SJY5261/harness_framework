# 경로 안내 (Path Reference)

주요 파일 및 디렉토리 경로 모음. 새로운 경로가 추가될 때마다 이 파일을 업데이트한다.

---

## 프로젝트 루트

| 역할 | 경로 |
|------|------|
| 하네스 프레임워크 | `E:\harness_framework\` |
| Tomes-Cloud 서버 | `E:\Tomes-Cloud\` |
| 테스트 자동화 | `E:\Test-Automize\` |

---

## 하네스 프레임워크 (`E:\harness_framework\`)

| 역할 | 경로 |
|------|------|
| 프로젝트 규칙 (가드레일) | `E:\harness_framework\CLAUDE.md` |
| 워크플로우 정의 | `E:\harness_framework\.claude\commands\harness.md` |
| Claude Code 설정 (훅 등) | `E:\harness_framework\.claude\settings.json` ← 훅 변경 시 아래 파일도 함께 수정 |
| Claude Code 설정 (Tomes-Cloud용) | `E:\Tomes-Cloud\.claude\settings.json` ← 위 파일과 항상 동일하게 유지 |
| 하네스 실행 스크립트 | `E:\harness_framework\scripts\execute.py` |
| Phase 관리 디렉토리 | `E:\harness_framework\phases\` |
| 경로 안내 (이 파일) | `E:\harness_framework\PATHS.md` |

---

## 로그 (`E:\LOGS\`)

| 역할 | 경로 |
|------|------|
| 서버 실행 로그 (당일) | `E:\LOGS\tomes-cloud\server\server.log` |
| 서버 로그 아카이브 | `E:\LOGS\tomes-cloud\server\archived\` |
| Gradle 빌드 로그 | `E:\LOGS\tomes-cloud\build\build.log` |
| pytest 단위 테스트 로그 | `E:\LOGS\tomes-cloud\test\test.log` |

---

## Tomes-Cloud (`E:\Tomes-Cloud\`)

| 역할 | 경로 |
|------|------|
| 서버 시작 배치 (로컬) | `E:\Tomes-Cloud\shell\startServer.local.bat` |
| 로그 설정 | `E:\Tomes-Cloud\src\main\resources\logback-spring.xml` |
| 앱 설정 (로컬) | `E:\Tomes-Cloud\src\main\resources\application-local.yml` |
| SQL 매퍼 XML | `E:\Tomes-Cloud\src\main\resources\sqlMaps\` |
| SQL 매퍼 XML (v1) | `E:\Tomes-Cloud\src\main\resources\sqlMaps\v1\` |
| Java 소스 | `E:\Tomes-Cloud\src\main\java\com\tomes\` |
| JSP 뷰 | `E:\Tomes-Cloud\src\main\webapp\WEB-INF\views\` |
| 정적 리소스 | `E:\Tomes-Cloud\src\main\webapp\resource\` |
| ParamQuery Grid 라이브러리 | `E:\Tomes-Cloud\src\main\webapp\resource\plugins\paramquery-11.0.0\` |
| 빌드 산출물 (WAR) | `E:\Tomes-Cloud\build\libs\ROOT.war` |

---

## Test-Automize (`E:\Test-Automize\`)

| 역할 | 경로 |
|------|------|
| QA 에이전트 메인 실행 | `E:\Test-Automize\qa_agent\agent_run.py` |
| 환경 설정 | `E:\Test-Automize\.env` |
| 설정 파일 | `E:\Test-Automize\config.py` |
| 단위 테스트 | `E:\Test-Automize\tests\` |
| TC 실행 계획 캐시 | `E:\Test-Automize\qa_agent\tc_plans\` |
| QA 에이전트 로그 | `D:\LOGS\` |
