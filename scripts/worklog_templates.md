# 작업일지 detail 템플릿 목록 (daily_worklog.py 참조)

`daily_worklog.py`가 작업별 `detail`을 쓸 때 따를 수 있는 서술 템플릿 모음.
각 detail 문단은 **`소제목 — 본문`** 형태(빈 줄 `\n\n`로 구분)로 쓰며, Notion에서
소제목은 굵은 파란색, 본문은 다음 줄로 렌더된다(`_detail_block` 처리).

현재 기본값은 **STAR/PPP 혼합형(배경·진행·결과·임팩트)** — 1번.
작업 성격에 따라 아래 다른 템플릿의 소제목으로 바꿔 써도 된다.

---

## 1. STAR/PPP 혼합형 (기본 권장)
일반 개발 작업 1건을 흐름대로 서술. 대부분의 작업에 적합.

```
배경·목적 — 왜 이 작업을 했나(문제·요청·동기).
진행      — 어느 파일에 무엇을 어떻게 했나(구체적 방법·근거).
결과·임팩트 — 결과·수치·확인내용 + 이 작업이 왜 중요했는지/무엇이 좋아졌는지.
```

## 2. 디버깅·장애형 (원인·수정·검증)
버그·성능 문제처럼 "원인 규명 → 수정 → 검증"이 핵심인 작업.

```
증상·측정 — 무엇이 어떻게 잘못/느렸나(정량화).
원인      — 코드로 규명한 근본 원인.
수정·검증 — 무엇을 고쳤고, 어떻게 확인했나(전/후 수치).
```

## 3. STAR (Situation/Task/Action/Result)
면접·평가 서류처럼 한 건을 깊게 풀어 쓸 때.

```
상황 — 당시 맥락·제약.
과제 — 내가 맡은 목표.
행동 — 실제로 한 일.
결과 — 임팩트·수치.
```
출처: STAR 행동 면접 프레임워크.

## 4. PPP (Progress/Plans/Problems)
짧은 일/주간 상태보고. 오버헤드 최소.

```
진행 — 완료한 것.
계획 — 다음 할 일(→ 일지의 next 필드와 연계).
문제 — 막힌 것·블로커(→ 일지의 issues 필드와 연계).
```
출처: PPP 상태보고 방법론.

## 5. Brag/Impact형 (Context/Action/Result)
성과·인수인계 강조. 평가 시즌·승진 근거용.

```
맥락 — 왜 중요했나.
행동 — 내가 한 것.
임팩트 — 무엇이 좋아졌나(수치·범위).
```
출처: Julia Evans Brag Document, Pragmatic Engineer Work Log.

---

## 참고 출처
- The Pragmatic Engineer — Work Log Template for Software Engineers
- Notion — Work Log for Software Engineers
- Wikipedia — Progress, plans, problems (PPP)
- Atlassian — 4Ls Retrospective (Loved/Loathed/Longed for/Learned)
- STAR (Situation/Task/Action/Result) 행동 면접 프레임워크
- Opensource.com — What is a developer journal?
