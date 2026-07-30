# Codex 주 에이전트 전환

_시작: 2026-07-24 / 최종 갱신: 2026-07-30_

## 현재 상태

- Codex가 기본 에이전트이며 별도 지시가 없으면 Codex 단독으로 작업한다.
- UserPromptSubmit 훅은 현재 해시가 신뢰·활성화된 상태다.
- 사용자 설치 개발 도구의 실행 파일 정본은 `D:\Tool`, 변경 가능한 도구 데이터·캐시 정본은 `D:\ToolData`, 실행 로그 정본은 `D:\LOGS`다.
- Python·Git·GitHub CLI·Node/npm·Java·VS Code 본체·Claude Code 실파일·DBeaver·IntelliJ·MariaDB는 D: 실행을 확인했다.
- VS Code 사용자 터미널 환경의 `PATH`·`CODEX_INSTALL_DIR`와 실행 중 세션이 먼저 찾는 C: 호환 shim은 `D:\Tool\nodejs`를 가리키며, 현재 세션에서도 `codex-cli 0.145.0` 실행을 확인했다.
- 2026-07-30 작업 도구 데이터 D: 이관은 즉시 항목 완료, 실행 중 항목 자동 완료 대기 상태다.

이전 전환 경위와 상세 검증 기록은
[`logs/handoff/Codex주에이전트전환-20260730-작업도구이관전.md`](../logs/handoff/Codex주에이전트전환-20260730-작업도구이관전.md)에 보존한다.

## 유지 결정

- 저장소 운영 정본은 `AGENTS.md`, 제품·안전 규칙 정본은 `PROJECT_RULES.md`다.
- Claude는 현재 프롬프트에서 사용자가 명시했을 때 Claude 세션에서 별도로 사용한다.
- 개인 모델·요금제·인증·알림·권한은 저장소 설정에 고정하지 않는다.
- 외부 요구사항 정본을 확보하지 못하면 구현을 추정하지 않고 사용자 검토를 요청한다.
- 공개 포크에는 신규 민감정보를 올리지 않으며 저장소 소유 Git 훅을 우회하지 않는다.

## 2026-07-30 작업 도구 데이터 D: 이관

### 현상

- 영구 사용자 `Path`는 D: 정본이지만 현재 VS Code가 이관 전 환경을 상속해 기존 C: Codex CLI를 먼저 찾았다.
- 기존 C: Codex 설치는 `bin\codex.js`가 이미 빠진 부분 삭제 상태여서 현재 프로세스의 `codex --version`이 실패했다. D: Codex `0.145.0`은 정상이다.
- SourceTree 앱·Pageant·내장 Git, VS Code 확장·사용자 데이터, Playwright 브라우저, 여러 도구 캐시·설정이 C: 사용자 프로필에 남아 있었다.
- Codex 임시 폴더의 pytest 하위 폴더는 샌드박스 ACL 때문에 일반 작업 프로세스에서 접근 거부됐다.

### 원인

- Windows 사용자 계정은 D:에 쓸 수 있지만 Codex의 제한된 샌드박스 토큰은 별도 ACL이 없는 D: 경로에 쓰지 못한다.
- C: 사용자 프로필에는 샌드박스 접근 ACE가 있고 `D:\harness_framework`에는 `CodexSandboxUsers` 수정 권한이 추가돼 있지만 기존 `D:\Tool` 밖의 새 데이터 경로에는 그 권한이 없었다.
- VS Code·SourceTree·Playwright 등은 기본 사용자 데이터 위치를 C: 프로필로 선택하며, 실행 파일을 D:로 옮겨도 데이터 위치는 자동 변경하지 않는다.

### 해결

- `D:\ToolData`를 만들고 이 루트만 D:의 넓은 `Authenticated Users` 상속을 끊었다. 현재 사용자·SYSTEM·관리자는 전체 권한, `CodexSandboxUsers`는 수정 권한만 하위 상속한다.
- `scripts/migrate_work_tools_to_d.ps1`에 복사 → SHA-256 검증 → C: 원본 제거 → D: 대상 junction 생성 절차를 구현했다.
- 즉시 이관 완료:
  - Playwright 브라우저 → `D:\ToolData\Playwright\Browsers`
  - npm·pip 캐시 → `D:\ToolData\npm`, `D:\ToolData\pip`
  - Python 사용자 기반 → `D:\ToolData\Python\UserBase`
  - GitHub CLI 설정·local data → `D:\ToolData\GitHubCLI`
  - JetBrains 향후 사용자 데이터 → `D:\ToolData\JetBrains`
  - Next.js telemetry·Unreal Engine local data → `D:\ToolData\Nextjs`, `D:\ToolData\UnrealEngine`
- 실행 중 항목은 강제 종료하지 않고 숨김 대기 프로세스와 사용자 로그인 재시도를 등록했다.
  - VS Code 사용자·profile·확장·shared storage와 GitHub Copilot
  - Codex 홈·전용 임시 폴더·부분 삭제된 C: CLI
  - SourceTree 앱·local·roaming 데이터·내장 Git 설정
  - DBeaver 사용자·Eclipse 데이터
  - Gradle 사용자 홈
  - Git 전역 설정
- SourceTree는 최종 이관 시 `D:\Tool\Git` 시스템 Git을 사용하도록 변경한다.
- Codex 공식 환경변수 `CODEX_HOME`과 VS Code 공식 `VSCODE_EXTENSIONS`, Playwright 공식 `PLAYWRIGHT_BROWSERS_PATH` 등 지원 경로를 우선 사용하고, 전역 실행 진입점이 없는 사용자 데이터는 C: 호환 junction으로 물리 저장소만 D:에 둔다.

### 채택 이유

- D: 전체 ACL을 완화하지 않고 도구 데이터 루트만 허용해 샌드박스 경계를 유지한다.
- 실행 중인 편집기·에이전트·DB 도구를 강제 종료하지 않아 현재 세션과 미저장 작업을 보존한다.
- C: 호환 junction은 업데이트 프로그램과 기존 바로가기의 기본 경로 계약을 유지하면서 실파일을 D:에 둘 수 있다.
- 캐시를 무조건 새로 받지 않고 원본과 D: 복사본을 파일별 검증해 불필요한 재설치와 설정 손실을 피한다.

### 현재 검증

- `D:\ToolData` ACL: 상속 보호, 현재 사용자·SYSTEM·관리자 전체 권한, `CodexSandboxUsers` 수정 권한 확인.
- Playwright Chromium 실제 실행 경로: D: 확인.
- npm cache, pip cache, Python user base, GitHub CLI config: 사용자 환경과 실제 명령에서 D: 확인.
- GitHub CLI 인증: D: 설정 경로에서 keyring 로그인 확인.
- C:의 즉시 이관 원본 경로는 D: 대상 junction으로 확인.
- VS Code 사용자 설정의 `terminal.integrated.env.windows`는 D: Node/Codex를 PATH 최우선과 `CODEX_INSTALL_DIR`로 지정했고, 기존 C: Codex shim도 D: 래퍼를 호출한다. 현재 프로세스의 `codex --version`은 `codex-cli 0.145.0`으로 통과했다.
- Gradle 사전 복사는 실행 중 daemon의 잠긴 파일 때문에 완료하지 않았으며 C: 원본을 유지했다. 최종 자동 이관에서 daemon 종료 후 다시 동기화·검증한다.

## 다음 단계

- [ ] 사용자가 VS Code·Codex·SourceTree·DBeaver와 C: Gradle daemon을 종료하면 숨김 이관 프로세스가 나머지를 완료한다.
- [ ] 새 VS Code/Codex 세션에서 `CODEX_HOME`, 확장 경로, 사용자 데이터, Git·Gradle·DBeaver·SourceTree 경로를 재검증한다.
- [ ] 완료 로그 `D:\LOGS\work-tools-d-migration-20260730.log`와 사용자 Run 항목 제거를 확인한다.

## 주의

- 실행 중 도구가 남아 있는 동안 최종 이관은 의도적으로 대기한다.
- Windows·드라이버·Chrome 같은 설치 관리자가 위치를 고정하는 시스템 구성요소, Windows 설치 캐시, Desktop 보고서 경로는 작업 도구 데이터 이관 대상이 아니다.
- 공개 이력에 남은 기존 원격 DB 자격증명은 별도 교체가 필요하다. 이력 재작성과 force-push는 사용자 승인 전 수행하지 않는다.
