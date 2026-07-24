# Claude 진행 안내 (2026-07-24 시작)

## 작업 목표
Claude Code가 긴 작업을 수행할 때 사용자가 경과 시간, 최근 작업, 실제 계획 진행도와 컨텍스트 사용량을 확인하고, 의미 있는 단계 전환은 대화로 안내받게 한다.

## 완료
- `.claude/statusline.py` 추가: Claude Code 세션 JSON과 최근 transcript 일부를 로컬에서 읽어 `경과 시간 / 실제 계획 완료 수 / 최근 작업 / context / 비용`을 표시한다.
- `.claude/settings.json`에 프로젝트 상태줄과 5초 갱신을 등록했다.
- `CLAUDE.md`에 장시간 작업 착수·단계 전환·검증·블로커·5분 이상 무안내 예상 시 진행 보고 규칙을 추가했다.
- 근거 없는 완료율·남은 시간 추정을 금지하고, 실제 TaskCreate/TaskUpdate 기록이 있을 때만 계획 수치를 표시한다.
- `scripts/test_statusline.py` 단위 테스트 3건 통과, settings JSON 파싱·py_compile·샘플 CLI 출력 확인.
- 기존 `scripts/test_execute.py`까지 함께 실행한 확대 검증은 `PYTHONUTF8=1` 기준 총 54건 중 52건 통과·2건 실패. 실패는 이번 변경과 무관한 기존 테스트/구현 불일치(`__new__` 인스턴스의 guardrail 캐시 필드 부재, 커밋 예시를 기대하는 옛 preamble 테스트)이며 이번 범위에서 수정하지 않았다.

## 진행중·미완
- 없음.

## 다음 단계
- 새 Claude Code 상호작용부터 상태줄 표시를 확인한다. 프로젝트 설정은 자동 재로딩되지만 현재 화면에 바로 나타나지 않으면 Claude Code 세션을 한 번 다시 시작한다.

## 블로커·주의
- 상태줄은 로컬 스크립트라 API 토큰을 사용하지 않는다.
- transcript는 매 갱신 때 마지막 256KB만 읽어 긴 세션에서도 전체 파일 반복 로드를 피한다.
- 계획 수치는 Claude가 TaskCreate/TaskUpdate를 실제로 사용한 작업에서만 표시된다.

## 관련 파일·경로
- `.claude/statusline.py`
- `.claude/settings.json`
- `scripts/test_statusline.py`
- `CLAUDE.md`
