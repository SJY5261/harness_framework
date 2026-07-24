# Codex 설계 결정 기록: <주제>

<!--
파일명: YYYY-MM-DD_<파일시스템에 안전한 짧은 주제>.md
같은 날짜·주제가 충돌하면 YYYY-MM-DD_<주제>_<discussion_id>.md
과거 Claude x Codex 토론 파일은 역사 기록이므로 이 템플릿으로 소급 변경하지 않는다.
-->

- discussion_id: `<YYYYMMDD-topic-sequence>`
- 라운드·상태: `1/pending` <!-- pending | running | completed | failed -->
- 주 에이전트: `Codex`
- 선택적 외부 검토: `not_requested` <!-- not_requested | requested | completed | unavailable -->
- 독립 검토: `not_required` <!-- not_required | pending | completed -->
- 최대 라운드: `3`
- synthesis 반영처: `(종결 전 미정)` <!-- 종결 시 handoff/<작업>.md -->

## 문제문

<!-- 저장소 근거, 제약, 원하는 판정, 완료 조건을 독립적으로 이해할 수 있게 적는다. -->

<문제와 판단할 쟁점>

## Round 1 — 분석과 제안

<!-- BEGIN OWNER:CODEX ROUND:1 -->

- 제안:
- 저장소 근거:
- 전제와 불확실성:
- 예상 회귀 위험:
- 검증 방법:

<!-- END OWNER:CODEX ROUND:1 -->

## Round 2 — 반론 검토

Round 1의 제안을 반대 관점에서 검토한다. 필요하면 사용자가 명시적으로 요청한 외부 검토 의견을 원문 그대로 추가한다.

<!-- BEGIN OWNER:CODEX ROUND:2 -->

- 반례·누락:
- 대안 비교:
- 수정된 제안:
- 남은 쟁점:

<!-- END OWNER:CODEX ROUND:2 -->

### 선택적 외부 검토

<!-- Claude 등 외부 검토를 사용자가 요청했고 실제 수행한 경우만 출처와 원문 요약을 기록한다. -->

- 검토자·도구: `(없음)`
- 상태: `not_requested`
- 의견: `(없음)`
- Codex의 수용·반론: `(없음)`

## Round 3 — 수렴

새 개선점과 미해결 쟁점을 확인한다. 근거로 우열을 가릴 수 없는 항목은 사용자에게 상신한다.

<!-- BEGIN OWNER:CODEX ROUND:3 -->

- 최종안:
- 포기한 대안과 이유:
- 미합의·사용자 상신:
- 새 개선점 유무:

<!-- END OWNER:CODEX ROUND:3 -->

## 실행 기록

- 시각 / 라운드 / 시도: `(없음)`
- 종료 코드 또는 타임아웃: `(없음)`
- 실패 사유와 마지막 응답 위치: `(없음)`
- 다음 조치: `(없음)`

## 독립 검토 보류

`peer_review_pending`은 보안·데이터 손실·비가역 설계처럼 독립 관점이 실제 결과를 바꿀 수 있는데 검토가 수행되지 않은 경우에만 기록한다. Claude를 사용하지 않았다는 이유만으로 만들지 않는다.

- 필요 여부와 근거: `not_required`
- 보류 범위: `(없음)`
- 해소 조건: `(없음)`

## Synthesis

<!-- BEGIN OWNER:CODEX SECTION:SYNTHESIS -->

- 상태: `(pending)`
- 결정:
- 판정 근거:
  - 정확성:
  - 저장소 근거:
  - 구현·운영 비용:
  - 회귀 위험:
  - 검증 가능성:
- 미검증 범위:
- handoff 반영 요약:

<!-- END OWNER:CODEX SECTION:SYNTHESIS -->
