# 경로 안내 (Path Reference)

주요 파일 및 디렉토리 경로 모음. 새로운 경로가 추가될 때마다 이 파일을 업데이트한다.

※ 2026-06-12 디렉토리 재구성: `E:\Tomes-Cloud` → `E:\harness_framework\Projects\Tomes-Cloud`,
`E:\Test-Automize` → `E:\harness_framework\Projects\Test-Automize` 로 이동됨.

---

## 프로젝트 루트

| 역할 | 경로 |
|------|------|
| 하네스 프레임워크 | `E:\harness_framework\` |
| Tomes-Cloud 서버 | `E:\harness_framework\Projects\Tomes-Cloud\` |
| 테스트 자동화 | `E:\harness_framework\Projects\Test-Automize\` |

---

## 하네스 프레임워크 (`E:\harness_framework\`)

| 역할 | 경로 |
|------|------|
| 프로젝트 규칙 (가드레일) | `E:\harness_framework\CLAUDE.md` |
| 워크플로우 정의 | `E:\harness_framework\.claude\commands\harness.md` |
| Claude Code 설정 (훅 등) | `E:\harness_framework\.claude\settings.json` ← 훅 변경 시 아래 파일도 함께 수정 |
| Claude Code 설정 (Tomes-Cloud용) | `E:\harness_framework\Projects\Tomes-Cloud\.claude\settings.json` ← 위 파일과 항상 동일하게 유지 |
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

## Tomes-Cloud (`E:\harness_framework\Projects\Tomes-Cloud\`)

이하 경로는 루트(`E:\harness_framework\Projects\Tomes-Cloud\`) 기준 상대 경로.

| 역할 | 경로 (루트 기준) |
|------|------|
| 서버 시작 배치 (로컬) | `shell\startServer.local.bat` |
| 개발용 라이브 실행 배치 | `shell\runDev.local.bat` |
| 배포 배치 (빌드+재기동) | `shell\deploy.local.bat` |
| 로그 설정 | `src\main\resources\logback-spring.xml` |
| 앱 설정 (로컬) | `src\main\resources\application-local.yml` |
| SQL 매퍼 XML | `src\main\resources\sqlMaps\` |
| SQL 매퍼 XML (v1) | `src\main\resources\sqlMaps\v1\` |
| Java 소스 | `src\main\java\com\tomes\` |
| JSP 뷰 | `src\main\webapp\WEB-INF\views\` |
| 정적 리소스 | `src\main\webapp\resource\` |
| ParamQuery Grid 라이브러리 | `src\main\webapp\resource\plugins\paramquery-11.0.0\` |
| 빌드 산출물 (WAR) | `build\libs\ROOT.war` |

---

## Test-Automize (`E:\harness_framework\Projects\Test-Automize\`)

이하 경로는 루트(`E:\harness_framework\Projects\Test-Automize\`) 기준 상대 경로.

| 역할 | 경로 (루트 기준) |
|------|------|
| QA 에이전트 메인 실행 | `qa_agent\agent_run.py` |
| 환경 설정 | `.env` |
| 설정 파일 | `config.py` |
| 단위 테스트 | `tests\` |
| TC 실행 계획 캐시 | `qa_agent\tc_plans\` |
| QA 에이전트 로그 | `D:\LOGS\` (절대 경로) |
