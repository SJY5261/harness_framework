# Codex 저장소 진입점

Codex는 작업을 시작할 때 다음 저장소 정본을 순서대로 읽는다.

1. `CLAUDE.md` — 공통 프로젝트 규칙과 개발 안전 규칙
2. `HANDOFF.md` — 현재 작업 인덱스. 사용자 요청과 관련된 `handoff/<작업>.md`만 이어서 읽는다.

규칙 본문은 이 파일에 복사하지 않는다. 내용이 충돌하면 더 구체적인 작업 지시와 최신 저장소 정본을 우선하고, 적용 여부가 불명확하면 사용자에게 보고한다.

## Codex 적용 제외

`CLAUDE.md` 중 Claude Code 런타임에만 존재하는 다음 규칙은 Codex에 적용하지 않는다.

- Claude memory 사용 및 관리
- Claude 전용 서브에이전트 종류와 호출 방식
- `answer-reviewer` 에이전트 및 `answer_review_gate.py` 게이트 절차와 답변 배너
- Claude Code 전용 훅, 슬래시 명령, 상태줄, 컨텍스트 초기화(`/clear`) 절차
- Claude가 `codex exec`를 호출할 때의 오케스트레이터 역할
- `CLAUDE.md`의 토큰 절약 규칙 중 Explore/general-purpose 등 Claude 전용 서브에이전트로 위임하라는 지시는 Codex에 적용하지 않는다. Codex는 사용 가능한 자체 협업 수단의 사용이 명시적으로 허용된 경우에만 위임하고, 그렇지 않으면 `rg`로 범위를 먼저 좁혀 필요한 부분만 읽고 대형 출력은 요약·부분 조회해 같은 토큰 절약 목적을 지킨다.

단, 위 항목에 함께 적힌 저장소 안전 규칙, 사실 검증 원칙, 인코딩 규칙, HANDOFF 갱신 규칙은 Codex에도 적용한다.

## Claude 사용 불가 시

사용자가 Claude의 토큰 소진·서비스 장애 등 사용 불가 상태를 알리면 Codex는 `CLAUDE.md`의 `단일 에이전트 장애 대응 모드`에 따라 임시 오케스트레이터가 된다. Claude 전용 호출 절차만 생략하고 구현·검증·HANDOFF 갱신을 계속하며, 상대 검토가 필요한 판단은 완료로 가장하지 않고 `peer_review_pending`으로 남긴다.
