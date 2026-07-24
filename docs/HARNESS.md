# Codex 하네스 실행 계약

`scripts/execute.py`는 `phases/<phase>/index.json`의 pending step을 Codex로 순차 실행한다.

## Phase 인덱스

```json
{
  "project": "Tomes-Cloud",
  "phase": "example",
  "context_files": [
    "docs/ARCHITECTURE.md",
    "handoff/example.md"
  ],
  "steps": [
    {"step": 0, "name": "inspect", "status": "pending"}
  ]
}
```

- `AGENTS.md`와 `PROJECT_RULES.md`는 항상 주입한다.
- `context_files`는 해당 phase에 필요한 파일만 저장소 상대 경로로 명시한다.
- 모든 `docs/*.md`를 자동 주입하지 않는다. 관련 없는 문서가 토큰을 차지하거나 지시 충돌을 만드는 것을 막기 위함이다.
- 저장소 밖 경로와 존재하지 않는 파일은 실행 전에 오류로 중단한다.
- step의 목표, 제약, 완료 조건과 검증 명령은 `stepN.md`에 둔다.

## 실행

```powershell
py scripts/execute.py <phase-directory>
```

`--push`는 하네스 브랜치를 원격에 푸시해야 할 때만 사용한다. `%클라우드` 커밋은 phase 프롬프트가 금지하며 사용자 권한 정책을 따른다.

실행 시작 전에 staged 변경이 있으면 중단한다. 기존 unstaged·미추적 경로는 기준선으로 보존하고, step 실행 뒤 새로 생긴 경로와 phase 상태 파일만 명시적으로 스테이징한다.

## 완료 계약

- AC를 직접 검증한다.
- 성공 시 step 상태를 `completed`, 실패 시 `error`, 사용자·외부 상태가 필요하면 `blocked`로 기록한다.
- 출력 JSON은 `stepN-output.json`에 남긴다.
- 재시도는 최대 3회이며 같은 실패를 반복하지 않도록 이전 오류를 다음 프롬프트에 포함한다.
