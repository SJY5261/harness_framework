# [Codex연계] Claude Code x Codex CLI 협업 체계

_생성: 2026-07-16 (Codex 세션 로그 역추적으로 복원) / 최종 갱신: 2026-07-21 (취약점 보완 토론 3라운드 종결 + 구현 완료)_

## 작업 목표
Claude Code와 Codex CLI를 `&하네스` 저장소를 공유하는 협업 체계로 묶는다.

## 완료
- 개념 설계 (7/15 Codex 세션).
- **설계 재검토 + Claude↔Codex 교차 토론 3라운드 종결 (7/20)** — 원안을 수정한 최종 설계에 양측 합의, "새 개선점 없음" 상호 선언. 전문: `discussion/2026-07-20_협업체계_설계토론.md` (synthesis 섹션이 정본).
- 하이브리드 중계 방식 실증 1회: Claude 세션이 `codex exec --sandbox workspace-write`를 3회 호출해 파일 기반 토론이 실제로 동작함을 확인 (codex-cli 0.144.4, `E:\Tool\nodejs\codex`).
- 최종 설계 구현: `AGENTS.md` 진입점, `discussion/TEMPLATE.md` 상태 계약·소유 구간 템플릿, `CLAUDE.md` 오케스트레이션·블라인드 Round 1·실패/안전 검사 규칙 반영.
- 장애 대응 모드 구현: 한쪽 토큰 소진·서비스 장애 시 다른 쪽이 임시 오케스트레이터가 되는 `single-agent-fallback`, 위험 작업 권한 유지, `peer_review_pending`, 복구 후 일괄 교차 리뷰 절차를 정본과 템플릿에 반영.
- **peer_review_pending 일괄 리뷰 완료 (7/21, Claude 복구 후)** — Codex 단독 구현분(장애 대응 모드) 대상. answer-reviewer 교차검증 거쳐 4건 결함 확인: ①execute.py에 Codex 폴백 실행 경로 부재(자동화 러너는 하드코딩된 `claude -p` 호출만 있음) ②토론 실패↔장애 대응 모드 전환 임계값 연결 규칙 부재 ③peer_review 범위 문구가 CLAUDE.md 원 조항보다 handoff 쪽이 좁게 자체 규정됨 ④AGENTS.md "Codex 적용 제외" 목록에 토큰절약 규칙(서브에이전트 위임 지시) 누락. `peer_review: completed`(리뷰 자체는 종결).
- **취약점 보완 정식 토론 3라운드 종결 + 구현 완료 (7/21)** — 블라인드 Round 1 절차 최초 실증. 4건 전부 합의·구현됨: ①execute.py는 코드 변경 없이 `CLAUDE.md` 단일 에이전트 장애 대응 모드에 "무인 step 실행은 폴백 미지원, 수동 인계 시 diff 대조 후 이어받는다"는 적용 범위 문구 추가(Claude 구현) ②`CLAUDE.md`에 콘텐츠성/인프라성 실패 분류 + 회복 가능 인프라 오류 1회 재시도 연결 규칙 추가(Claude 구현) ③handoff 축소 문구는 이미 해소돼 무변경, `CLAUDE.md` peer_review 조항에 "범위를 다른 문서에서 좁게 재정의하지 않는다" 재발방지 문장만 추가(Claude 구현) ④`AGENTS.md` 제외 목록에 토큰절약 규칙 서브에이전트 위임 제외 + 대체 지침 항목 추가(Codex 구현, 소유권 양보로 합의). 전문·판정근거: `discussion/2026-07-21_협업체계_취약점보완.md`(synthesis가 정본). 안전검사(호출 전후 diff 대조) 매 라운드 통과.

## 결정 (7/20 합의)
1. `brain/` 등 신설 폐기 → 기존 handoff 체계 재사용. Claude memory는 공유 정본 제외. 결정 수명주기: handoff "결정" 섹션 → ARCHIVE → 범용 규칙은 CLAUDE.md 승격.
2. 신설물은 `AGENTS.md`(얇은 포인터 + Codex 적용 제외 목록) + `discussion/`뿐.
3. 중계는 Claude 세션이 오케스트레이터(codex exec 호출). 최소 권한, 실패 처리 규칙, diff 기반 안전 검사, 블라인드 Round 1 절차 포함.
4. 토론은 최대 3라운드, 트리거 한정(설계 갈림길/회귀 위험/비가역 변경/사용자 요청), 미합의는 사용자 상신.
5. 토론 파일 상태 계약(discussion_id/라운드·상태/소유자/최대 라운드/synthesis 반영처), `discussion/`에 영구 보존.
6. 한쪽 사용 불가 시 사용 가능한 에이전트가 단독 운영하되 권한은 확대하지 않는다. 상대 검토가 필요한 항목은 `peer_review_pending`으로 남기고 복구 후 일괄 검토한다.
- 장기 과제(지금 안 함): CLAUDE.md 공통 규칙의 중립 파일 분리.

## 진행중·미완
- 없음. 4건 결함 모두 조치 완료.

## 다음 단계
- 없음(이 작업은 종결). 향후 실제 장애 상황이 발생하면 이번에 추가된 연결 규칙(콘텐츠성/인프라성 분류)이 실전에서 잘 작동하는지 사후 확인할 것.

## 블로커·주의
- 기술 블로커 없음. codex exec 동작 확인됨(codex-cli 0.144.6).
- 두 CLI는 자동 대화하지 않음 — Claude가 오케스트레이터 역할(합의된 구조).
- 협업 모드: `normal`로 복귀(7/21, 이 세션에서 Claude 활성 확인). 상대 검토: `completed`(위 4건 결함 발견, 조치는 별도 작업).
- 구 쟁점("연계"의 의미 이원 해석)은 7/20 사용자 지시(교차 토론 실행)로 ①공유 브레인+교차 토론 체계 쪽으로 사실상 해소.

## 관련 파일·경로
- **설계 정본**: `discussion/2026-07-20_협업체계_설계토론.md` (Round 1~3 + Synthesis)
- Codex 세션 로그(원안): `C:\Users\USER\.codex\sessions\2026\07\15\rollout-2026-07-15T08-33-05-*.jsonl`
- `C:\Users\USER\.codex\config.toml` — trust 등록만 있음
