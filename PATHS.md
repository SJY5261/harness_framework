# 경로 안내

경로는 가능한 한 저장소 상대 경로를 사용한다. 현재 하네스 루트는 작업 환경에서 `git rev-parse --show-toplevel`로 확인하며 과거 문서의 `E:\harness_framework`는 현재 루트로 재해석한다.

| 약칭/역할 | 저장소 기준 경로 |
|---|---|
| `&하네스` | `.` |
| `%클라우드` | `Projects/Tomes-Cloud` |
| `%테스트` | `Projects/Test-Automize` |
| Codex 운영 규칙 | `AGENTS.md` |
| 프로젝트 불변식 | `PROJECT_RULES.md` |
| 현재 작업 인덱스 | `HANDOFF.md` |
| 세컨브레인 구조 | `docs/SECOND_BRAIN.md` |
| Codex 공용 설정 | `.codex/` |
| 하네스 실행기 | `scripts/execute.py` |
| 작업일지 자동화 | `scripts/daily_worklog.py` |
| Phase 정의 | `phases/` |

## Tomes-Cloud

| 역할 | `%클라우드` 기준 경로 |
|---|---|
| 개발 실행 배치 | `shell/runDev.local.bat` |
| 로컬 설정 | `src/main/resources/application-local.yml` |
| SQL 매퍼 | `src/main/resources/sqlMaps/` |
| Java 소스 | `src/main/java/com/tomes/` |
| JSP 뷰 | `src/main/webapp/WEB-INF/views/` |
| 정적 리소스 | `src/main/webapp/resource/` |
| ParamQuery 11 | `src/main/webapp/resource/plugins/paramquery-11.0.0/` |
| WAR | `build/libs/ROOT.war` |

## Test-Automize

| 역할 | `%테스트` 기준 경로 |
|---|---|
| QA 실행기 | `qa_agent/agent_run.py` |
| 환경 설정 | `.env`, `config.py` |
| 단위 테스트 | `tests/` |
| TC 계획 캐시 | `qa_agent/tc_plans/` |

로그의 절대 위치는 PC마다 다를 수 있으므로 실행 설정이나 실제 프로세스에서 확인한다. 비밀이 포함될 수 있는 `.env`와 로컬 설정은 문서에 복사하지 않는다.
