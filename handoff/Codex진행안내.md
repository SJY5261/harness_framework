# Codex 진행 안내 (2026-07-24 전환)

## 작업 목표
Codex가 긴 작업을 수행할 때 사용자가 현재 단계, 완료한 일, 다음 일, 블로커를 대화에서 확인할 수 있게 한다. 제품 UI의 계획·에이전트 상태는 보조 수단으로 사용한다.

## 완료
- `AGENTS.md`에 장시간 작업 착수·단계 전환·검증·블로커·5분 이상 무안내 예상 시 진행 보고 규칙을 정본화했다.
- Codex commentary 업데이트를 기본 진행 안내 채널로 사용한다.
- 실제 체크리스트가 있을 때만 계획 수치를 표시하고 근거 없는 완료율·남은 시간 추정을 금지했다.
- 개인 전역 `~/.codex/AGENTS.md`와 저장소 `AGENTS.md`에 새 실패 또는 문제 가능성이 있는 경고·잠재 문제 발견 시 영향과 선택지를 알리고, 해결이 이미 요청된 경우가 아니면 수정 전에 사용자 확인을 받는 규칙을 추가했다.
- Claude 상태줄(`.claude/statusline.py`, `.claude/settings.json`)은 Claude를 선택적으로 사용할 때의 호환 자산으로 보존했다.
- `scripts/test_statusline.py` 단위 테스트 3건 통과, settings JSON 파싱·py_compile·샘플 CLI 출력 확인.
- 기존 `scripts/test_execute.py`까지 함께 실행한 확대 검증은 `PYTHONUTF8=1` 기준 총 54건 중 52건 통과·2건 실패. 실패는 이번 변경과 무관한 기존 테스트/구현 불일치(`__new__` 인스턴스의 guardrail 캐시 필드 부재, 커밋 예시를 기대하는 옛 preamble 테스트)이며 이번 범위에서 수정하지 않았다.

## 진행중·미완
- 없음.

## 다음 단계
- 새 Codex 대화부터 개인 전역 규칙이 모든 저장소에 적용되고, 이 저장소에서는 루트 `AGENTS.md`가 같은 원칙을 명시적으로 유지한다.

## 블로커·주의
- Claude 상태줄은 Codex 상태나 진행률을 표시하지 않는다.
- Codex 진행 안내는 별도 AI 호출 없이 주 대화의 commentary로 제공한다.

## 관련 파일·경로
- `AGENTS.md`
- `.codex/config.toml`
- `.codex/hooks.json`
- `scripts/test_statusline.py`
- `.claude/statusline.py` (선택적 Claude 호환)
