# Claude x Codex 설계 토론: <주제>

<!--
파일명: YYYY-MM-DD_<파일시스템에 안전한 짧은 주제>.md
같은 날짜·주제가 충돌하면 YYYY-MM-DD_<주제>_<discussion_id>.md
이 템플릿의 소유 구간 표식은 호출 전후 diff 안전 검사에 사용하므로 삭제하지 않는다.
-->

- discussion_id: `<YYYYMMDD-topic-sequence>`
- 라운드·상태: `1/pending` <!-- pending | running | completed | failed -->
- 협업 모드: `normal` <!-- normal | single-agent-fallback -->
- 활성/사용 불가 에이전트: `Claude+Codex / 없음`
- 상대 검토: `not_required` <!-- not_required | pending | completed -->
- 섹션 소유자: `문제문=Claude / Claude 의견=Claude / Codex 의견=Codex / Synthesis=Claude`
- 최대 라운드: `3`
- synthesis 반영처: `(종결 전 미정)` <!-- 종결 시 handoff/<작업>.md -->

## 문제문

<!-- Round 1 양측에 동일하게 제공할 완결형 문제문. 저장소 근거, 제약, 원하는 판정을 포함한다. -->

<문제와 판단할 쟁점>

## Round 1 — 블라인드 독립 의견

Round 1에서는 문제문만 고정한다. Claude 의견은 세션 안에서 먼저 확정하되 파일에 쓰지 않고, Codex에는 문제문과 필요한 정본 경로만 전달한다. 양측 의견이 모두 확정된 뒤 아래 두 구간을 공개한다.

<!-- BEGIN OWNER:CLAUDE ROUND:1 -->
### Claude

(작성 대기)
<!-- END OWNER:CLAUDE ROUND:1 -->

<!-- BEGIN OWNER:CODEX ROUND:1 -->
### Codex

(작성 대기)
<!-- END OWNER:CODEX ROUND:1 -->

## Round 2 — 교차 검토

상대의 직전 의견에 대한 동의·반론, 근거, 수정안, 새 개선점을 기록한다.

<!-- BEGIN OWNER:CLAUDE ROUND:2 -->
### Claude

(작성 대기)
<!-- END OWNER:CLAUDE ROUND:2 -->

<!-- BEGIN OWNER:CODEX ROUND:2 -->
### Codex

(작성 대기)
<!-- END OWNER:CODEX ROUND:2 -->

## Round 3 — 수렴 및 종료 확인

남은 쟁점과 새 개선점 유무를 명시한다. 3라운드에서 합의되지 않은 항목은 더 진행하지 않고 사용자에게 상신한다.

<!-- BEGIN OWNER:CLAUDE ROUND:3 -->
### Claude

(작성 대기)
<!-- END OWNER:CLAUDE ROUND:3 -->

<!-- BEGIN OWNER:CODEX ROUND:3 -->
### Codex

(작성 대기)
<!-- END OWNER:CODEX ROUND:3 -->

## 실행 기록

<!-- 실패·재시도 때만 추가한다. 같은 소유 구간에 결과를 중복 append하지 않는다. -->

- 시각 / 라운드 / 시도: `(없음)`
- 종료 코드 또는 타임아웃: `(없음)`
- 실패 사유와 마지막 응답 위치: `(없음)`
- 다음 조치: `(없음)`

## 장애 대응 기록

<!-- 한쪽 에이전트가 사용 불가할 때만 작성한다. 토큰 잔량을 추정하지 말고 사용자 통보 또는 명확한 호출 실패를 근거로 한다. -->

- 전환 시각·사유: `(없음)`
- 활성/사용 불가 에이전트: `(없음)`
- 단독 수행 범위: `(없음)`
- peer_review_pending 항목: `(없음)`
- 정상 모드 복귀·후속 검토 결과: `(없음)`

## Synthesis

<!-- BEGIN OWNER:CLAUDE SECTION:SYNTHESIS -->
- 상태: `(pending)`
- 합의 사항: `(작성 대기)`
- 미합의·사용자 상신: `(없음)`
- 판정 근거:
  - 정확성: `(작성 대기)`
  - 저장소 근거: `(파일 경로와 검증 결과)`
  - 구현·운영 비용: `(작성 대기)`
  - 회귀 위험: `(작성 대기)`
  - 검증 가능성: `(작성 대기)`
- handoff 반영 요약: `(작성 대기)`
<!-- END OWNER:CLAUDE SECTION:SYNTHESIS -->

합의되지 않은 상대 의견은 삭제하거나 의미를 바꾸지 않는다. 근거가 부족하거나 판정 기준으로 우열을 가릴 수 없는 항목은 사용자 상신으로 남긴다.
