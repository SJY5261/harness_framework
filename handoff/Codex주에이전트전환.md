# Codex 주 에이전트 전환

_시작: 2026-07-24 / 최종 갱신: 2026-07-30_

## 현재 상태

- Codex가 기본 에이전트이며 별도 지시가 없으면 Codex 단독으로 작업한다.
- UserPromptSubmit 훅은 현재 해시가 신뢰·활성화된 상태다.
- 사용자 설치 개발 도구의 실행 파일 정본은 `D:\Tool`, 변경 가능한 도구 데이터·캐시 정본은 `D:\ToolData`, 실행 로그 정본은 `D:\LOGS`다.
- Python·Git·GitHub CLI·Node/npm·Java·VS Code 본체·Claude Code 실파일·DBeaver·IntelliJ·MariaDB는 D: 실행을 확인했다.
- VS Code 사용자 터미널 환경의 `PATH`·`CODEX_INSTALL_DIR`는 `D:\Tool\nodejs`를 가리키며, 현재 세션에서도 D: `codex-cli 0.146.0` 실행을 확인했다.
- Playwright·npm·pip·Python 사용자 기반·GitHub CLI·JetBrains·Next.js·Unreal·Gradle 데이터는 D: 이관과 C: 원본 제거를 완료했고, 필요한 C: 기본 경로에는 D: 대상 junction만 남겼다.
- VS Code 사용자 데이터 자동 복사가 재실행 경쟁 조건으로 실패해 VS Code·Copilot·Codex·SourceTree·DBeaver·Git 후속 이관과 최종 환경 변수 전환은 대기 상태다.

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
- VS Code 사용자 설정의 `terminal.integrated.env.windows`는 D: Node/Codex를 PATH 최우선과 `CODEX_INSTALL_DIR`로 지정했다. 현재 프로세스의 `codex --version`은 D: `codex-cli 0.146.0`으로 통과했다.
- Gradle 사용자 홈은 2,137개 파일 검증 후 `D:\ToolData\Gradle`로 이관됐고 C: 원본 대신 D: 대상 junction이 남아 있다.

## 2026-07-30 재검증 및 C: 원본 정리

### 현상

- 자동 이관 로그는 Gradle 사용자 홈 2,137개 파일 검증과 D: 이관을 완료한 뒤, VS Code 사용자 데이터 복사에서 `robocopy` 종료 코드 9로 중단됐다.
- 완료된 데이터 항목의 C: 경로는 모두 D: 정본을 가리키는 junction이며 C: 실파일 원본은 남아 있지 않았다.
- C:에는 실행 본체 `bin\codex.js`가 빠진 Codex 0.145.0 설치가 남아 있었고 D: 정본은 정상 동작하는 0.146.0이었다.
- D: Python의 콘솔 실행기 21개는 제거된 C: Python 실행 경로를 내장해 `pip.exe` 같은 직접 실행이 종료 코드 1로 실패한다. `python -m pip`과 Python 모듈 실행은 정상이다.

### 원인

- 자동 이관은 시작 전에만 차단 프로세스를 확인했다. 15:20:11에 이관을 시작한 뒤 Gradle 복사 도중 15:20:36에 VS Code가 다시 실행됐고, 항목별 재확인 없이 열린 VS Code DB·캐시 복사를 시작해 실패했다.
- C: Codex는 부분 삭제된 이전 0.145.0 코드이고 D: Codex는 이후 0.146.0으로 갱신돼 완전 중복 버전 비교 조건을 만족하지 않았다.
- Python 패키지와 실행기를 D:에 보존하는 과정에서 Windows 콘솔 실행기 내부의 절대 C: Python 경로는 다시 생성되지 않았다.

### 해결

- C: Codex 설치는 정확한 예상 경로, 허용된 코드 항목만 존재, D:와 래퍼 3개 해시 일치, C: 실행 본체 부재, 사용 프로세스 0건을 확인한 뒤 실파일 폴더를 제거했다.
- 삭제 직후 `D:\Tool\nodejs\codex.cmd --version`으로 `codex-cli 0.146.0` 정상 실행을 재확인했다.
- 미완료 도구 데이터의 C: 원본과 자동 재시도 Run 항목은 보존했다. VS Code의 불완전한 D: 복사본도 후속 비교·정리 전에는 삭제하지 않았다.

### 채택 이유

- 완료 항목의 C: 실파일만 제거하고 기본 경로 호환에 필요한 junction을 유지하면 중복 저장 공간을 없애면서 업데이트·기존 경로 계약을 보존할 수 있다.
- C: Codex에는 고유 설정·사용자 데이터가 없고 실행할 수 없는 이전 코드만 남아 있어, 동작하는 D: 정본을 검증한 뒤 제거하는 편이 버전이 다른 불완전 사본을 유지하는 것보다 안전하다.
- 현재 사용 중인 도구 데이터는 강제로 이동하지 않아 미저장 작업과 설정 손실을 피했다.

### 결과와 미완료 영역

- 완료·C: 원본 제거: Playwright 브라우저, npm 캐시, Next.js 데이터, pip 캐시, Gradle 사용자 홈, Python 사용자 기반, GitHub CLI 설정·local data, JetBrains roaming·local, Unreal Engine local data.
- VS Code: 사용자 데이터, profile·확장, shared data가 C: 원본 상태다. 첫 복사의 D: 부분 산출물 정리와 항목별 프로세스 재확인 보완 후 재시도가 필요하다.
- GitHub Copilot: 사용자 데이터가 C: 원본 상태다.
- Codex: 실행 파일은 D: 완료, C: 이전 설치는 제거 완료. 개인 홈과 전용 임시 폴더는 C: 원본 상태이며 `CODEX_HOME` 전환이 남았다.
- DBeaver: 사용자 데이터와 Eclipse 데이터가 C: 원본 상태다.
- SourceTree: 앱, local·roaming 데이터가 C: 원본 상태이며 D: 시스템 Git 전환도 남았다.
- Git: 전역 `.gitconfig`의 D: 이관과 `GIT_CONFIG_GLOBAL` 전환이 남았다.
- Python: D: Python과 모듈은 정상이나 콘솔 실행기 21개의 옛 C: 절대 경로를 D: 호환 포인터 또는 실행기 재생성으로 보완해야 한다.
- 마무리: 사용자 환경의 `CODEX_HOME`, `VSCODE_EXTENSIONS`, `GIT_CONFIG_GLOBAL`, `GRADLE_USER_HOME` 전환, 자동 재시도 Run 항목 제거, 완료 로그 확인이 남았다.

## 다음 단계

- [ ] 자동 이관 스크립트에 각 후속 항목 직전 차단 프로세스 재확인과 `robocopy` 오류 증적을 추가한다.
- [ ] VS Code·Codex·SourceTree·DBeaver가 종료된 안전한 시점에 불완전한 VS Code D: 복사본을 검증·정리하고 나머지 이관을 재시도한다.
- [ ] Python 콘솔 실행기 21개의 제거된 C: Python 경로를 D: 호환 포인터 또는 실행기 재생성으로 복구한다.
- [ ] 새 VS Code/Codex 세션에서 `CODEX_HOME`, 확장 경로, 사용자 데이터, Git·Gradle·DBeaver·SourceTree 경로를 재검증한다.
- [ ] 완료 로그 `D:\LOGS\work-tools-d-migration-20260730.log`와 사용자 Run 항목 제거를 확인한다.

## 주의

- 실행 중 도구가 남아 있는 동안 최종 이관은 의도적으로 대기한다.
- Windows·드라이버·Chrome 같은 설치 관리자가 위치를 고정하는 시스템 구성요소, Windows 설치 캐시, Desktop 보고서 경로는 작업 도구 데이터 이관 대상이 아니다.
- 공개 이력에 남은 기존 원격 DB 자격증명은 별도 교체가 필요하다. 이력 재작성과 force-push는 사용자 승인 전 수행하지 않는다.
