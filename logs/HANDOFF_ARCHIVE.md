# HANDOFF 아카이브 — 종결된 세션 이력

> 2026-07-09 HANDOFF.md에서 분리(원본 순서 유지). 활성 항목은 `&하네스\HANDOFF.md` 참조.
> 일별 상세는 logs/worklog_YYYY-MM-DD.json, 커밋 이력은 각 저장소 git 참조.

## [2026-07-08] 개인 브랜치 전부 main 기준 최신화 (%클라우드, 사용자 지시로 실행 — 푸시는 안 함)
### 배경
- 7/3 이후 사용자가 직접 정리한 것들: 워킹트리 미커밋 4파일은 `logs/cloud_local_changes_backup_2026-07-08.patch`로 백업 후 리셋됨(estmateCalculate.xml, v1/estmateCalculate.xml, estimate JSP, transaction_statement.jsp — 목업제거+기타플래그+라벨모달 작업분). main엔 퍼블리싱 머지(PR #23)+유사형태 리뉴얼이 들어와 대폭 변경됨.
### 실행 결과 (전부 로컬, origin 푸시 없음)
- 로컬 main: bf93be6 → **93211d4** (origin/main과 일치, fetch refspec ff).
- **main으로 fast-forward** (고유 커밋 0이었음): Danga-order(현 체크아웃, merge ff) / feature_caching_2606, feature_hightChart_260703, feature_invoice_260703(branch -f 포인터 이동). 전부 93211d4.
- **feature_drawing_popup_260702**: main 머지 커밋 6ad0dff, 무충돌. 고유 변경 3건 생존 확인(publishing/bottom.css object-fit:contain, bottom.jsp link, bottom.js:141 resizable:false).
- **Sun-Pro**: main 머지 커밋 ea39bcd. Java 3파일 충돌(SystemService/SystemServiceImpl/InnodaleServiceImpl) → **main측 채택으로 해소**(Sun-Pro 고유 Java 변경 = getSessionUserList 캐시·updateUser evict·CODE 캐시무효화가 main에 전부 포함돼 있음을 대조 확인, 손실 0). 머지 후 Sun-Pro↔main 차이 = logback-spring.xml +21줄(로그 추적 설정)만.
- 검증: 충돌 마커 0, compileJava --rerun-tasks 통과(경고만). `gradlew build`의 :processResources는 가동 중인 8081 서버(빌드 산출물 잠금) 탓에 실패 — 머지와 무관.
- **[같은 날 후속] 푸시 완료(사용자 지시)**: Danga-order/Sun-Pro/feature_caching_2606/feature_drawing_popup_260702 4개 origin 푸시, 전부 ff — branch -vv로 원격 일치 확인. feature_hightChart_260703/feature_invoice_260703은 원격 브랜치가 없고 내용이 main과 동일해 푸시 대상에서 제외(원격 생성 원하면 별도 지시). 체크아웃은 Danga-order로 복귀시킴.

## [2026-07-03] 극단비율 "완결형" 도면 재검증 (코드 무변경, 원복 완료)
- 사용자 지적: 앞선 극단비율 테스트 파일이 A4 도면을 띠로 잘라 만든 것이라 팝업 내용 자체가 잘린 도면이었음 → 실도면의 완결 뷰(치수·공차 포함)를 원본 해상도 그대로 재배치한 합성본으로 재검증(make_complete_extreme.py).
- complete_wide_4to1(3508x877): 아래뷰+위뷰+로고+테두리, 잘림 없음. complete_tall_1to4(619x2479): 뷰를 90도 CW 회전 배치 → 서버 270도 회전 후 팝업에서 글자 정립(의도대로 확인됨).
- 결과 동일: 수정전 fill 왜곡 / 수정후(CSS주입) contain 4:1 보존·잘림 없음·JS에러 0. 캡처 `예시\도면팝업_썸네일검증\real_extreme_complete_wide41|tall14_before|after.png`. 썸네일 MD5 원복 확인.

## [2026-07-03] 도면 썸네일 글자 가독성 검증 (코드 무변경)
### 요지 (사용자 진짜 관심사 = 비율 아닌 "썸네일 생성 시 글자 깨짐")
- 생성 파이프라인(`FileUploadServiceImpl.java:717 MakePDFImageConvert`): PNG 축소가 아니라 **PDF를 DPI별 재렌더** — base 300dpi(3508x2479) / .thumbnail 130dpi(1520x1074) / .mini 30dpi(350x247) / .print(base 가로면 90도 회전본).
- **썸네일 파일 자체는 글자 안 깨짐**(치수공차 +0.02/-0.00까지 또렷 — 벡터 재렌더라 열화 없음).
- **깨지는 지점**: ①팝업 실표시 = 1520px 썸네일을 ~732px 박스로 브라우저 축소(0.48x, 실효 ~62dpi) → 공차 글자 흐릿(판독 한계), 로고 부속텍스트 뭉개짐 ②.mini(30dpi) = 공차 텍스트 완전 판독불가(다만 용도가 TV 카드·공정현황 `/qsimage`라 글자 판독 목적 아님 — tv_pop/tv_mct/process_dashBoard/bottom.js:4772).
- 근거 산출물: 바탕화면 `예시\도면팝업_썸네일검증\text_compare_dims.png / text_compare_logo.png`(base/thumbnail/팝업표시/mini 4단계 동일영역 크롭 대조, make_text_compare.py 세션 scratchpad).
- 팝업 `/qimage`=thumbnail 130dpi, `/qsimage`=mini 30dpi (StaticUrlController.java:286~).

## [2026-07-03] 도면 미리보기 극단 비율 — 실파일 전수조사 + 실팝업 검증 (코드 무변경)
### 실파일 조사 (answer-reviewer 검증 OK)
- 로컬 업로드 루트 `C:\ws\tomes`(application-local.yml). cad 도면 PNG 948개(237세트×base/mini/print/thumbnail) 전수 IHDR 측정: **base 전부 3508x2479(1.42:1 A4 가로), print만 2479x3508. 극단 비율(3:1+) 도면 0건** — 파이프라인이 A4로 정규화하는 듯.
- 유일한 극단 비율 실사용 이미지 = `upload\etc\20260303\file-80384819-*`/`file-16366397-*` (565x131=**4.31:1**, 확장자 없는 PNG) — 도면 아닌 **TOMES CLOUD 바코드 라벨**.
- 한계: DB TBL_FILE엔 cad 30,816건, 대부분 `/home/admin/datadir`(서버 디스크)라 로컬 측정 불가. 재고관리 그리드 대부분 blank(400x300) 폴백인 이유이기도 함.
### 실팝업 검증 (파일 스왑 방식, DB 무변경, 원복 완료)
- gfileSeq **31633**(TOMES-DWG-A-0008, FILE_PATH가 로컬 C:/ws/tomes)의 `.thumbnail.png`를 백업 후 바코드로 교체 → 재고관리 fileSearchIcon 팝업 실오픈 측정 → **MD5 일치 원복 완료**.
- 결과: 수정전(현 브랜치) fit=fill → 732x529(1.38:1)로 **왜곡** / 수정후(CSS 3속성 주입) contain → 732x170(4.31:1) **비율보존**. 캡처 바탕화면 `예시\도면팝업_썸네일검증\real_extreme_431_before|after.png`.
- **★중요: 현재 %클라우드 체크아웃 = `feature_invoice_260703`이며 도면팝업 수정(object-fit:contain, publishing/bottom.css)이 없음**(bottom.jsp:997 = 구버전 inline height:100%만). 수정본은 `feature_drawing_popup_260702`에만 존재 → 위 "수정후"는 검증 페이지에 동일 CSS를 브라우저 주입해 재현한 것. 8081 서버는 현재 수정 전 상태로 동작 중.
- 검증 팁: 재고관리 그리드도 미적재 플레이크 있음(아이콘 1개만 감지) → 검색 클릭+아이콘 수 폴링 재시도 필요. 그리드 행 순서가 실행마다 달라 icon_index 고정 금지, gfileSeq로 탐색(verify_extreme_real2.py, 세션 scratchpad).

## [2026-07-02] 변경 스타일 → publishing CSS 분리 (진행중, %클라우드)
### 요구
- 도면 미리보기·수주현황에서 변경된 style을 **화면 JSP명과 동일한 CSS 파일**로 분리해 `resource/asset/css/publishing/`(신규 폴더)에 배치. **각 작업은 해당 기능 브랜치에서 진행**(도면=feature_drawing_popup_260702 / 수주현황=feature_business_status_260702). 커밋은 사용자가 직접(질문으로 확정).
### 완료 — 도면 미리보기 (feature_drawing_popup_260702, 미커밋)
- 신규 `publishing/bottom.css`: `#drawingImage{object-fit:contain; display:block; margin:0 auto}` (64627d9에서 추가된 3개 속성만 이동. 기존 inline `height:100%`와 onerror 속성은 JSP에 유지).
- `attr/tabs/bottom.jsp`: img 인라인에서 3속성 제거 + 상단에 `<link href="/resource/asset/css/publishing/bottom.css">` 추가.
- 라이브 검증(8081, Playwright): bottom.css HTTP 200, #drawingImage computed object-fit:contain/display:block/margin:0 auto 유지, inline은 height:100%만.
### 완료 — 수주현황 (feature_business_status_260702, 미커밋)
- 사용자가 도면 브랜치 커밋+수주현황 브랜치 전환을 직접 수행 → 신규 `publishing/business-status.css`(배지 4규칙+셀패딩 1규칙 이동), business-status.jsp `<style>` 블록 제거 + `<link>` 추가(구분 배지 render 코드는 JSP에 그대로).
- 라이브 검증: business-status.css HTTP 200, 배지 computed 38x18/inline-flex/#dbeafe/radius4 전부 외부 CSS로 적용, JSP 내 잔존 `<style>` 0, JS에러 0. (기하 재검증은 탭 강제표시 상태라 참고용 — 규칙 내용이 이동 전과 byte 동일해 정렬은 기존 검증 유효)
- **자동화 주의(재발)**: 이 화면 탭 콘텐츠 래퍼 `span.addTapPage`가 display:none으로 남는 플레이크 있음(데이터는 로드되는데 그리드 0x0·셀 0). 검증 시 `.page-tab-list` 탭 재클릭 + span 강제표시 + resize 필요(verify_bstatus_css.py 참조).
- 주의: 5b3ee62 커밋 메시지엔 "13px 축소"라 적혔지만 실제 내용은 최종본(클래스만, style 없음)이 맞음.

---

## [2026-07-02] 브랜치 분리 완료 (%클라우드 — 사용자 승인 하 실행, 푸시는 안 함)
- 사용자 확정 플랜: ①단가검토는 Danga-order 유지 ②main 갱신 ③④도면팝업/수주현황을 main 기반 별도 브랜치로 커밋. 브랜치명 규칙 `feature_특징_YYMMDD`.
- 실행 결과(전부 검증):
  - `git fetch origin main:main` — 로컬 main 3228c7f -> b1b64bf(체크아웃 없이 ff). 구 main은 estimate JSP 881줄 차이라 switch 불가였음 -> fetch refspec으로 회피.
  - `feature_drawing_popup_260702` = 커밋 64627d9 "fix: 도면 미리보기 팝업 창 크기 고정 및 썸네일 비율 유지" (bottom.js+bottom.jsp, 각 1줄).
  - `feature_business_status_260702` = 커밋 5b3ee62 "feat: 수주현황 그리드 헤더에 작업상세/도면 아이콘 표시" (business-status.jsp).
  - **푸시 완료(사용자 지시)**: 두 브랜치 모두 origin에 push + 업스트림 설정(원격 해시 = 로컬 커밋 일치 확인). PR 생성 링크만 안내, PR은 안 만듦.
  - 미커밋은 estimate_unit_price_calculate.jsp(목업 제거, 커밋 대기)만. stash 비움.
  - 주의: 푸시 직후 reflog(14:30)에 내가 실행하지 않은 checkout 연쇄(Danga-order→business→main→drawing_popup)가 있음 — 사용자가 IDE/터미널에서 직접 둘러본 것으로 추정, 현재 체크아웃 feature_drawing_popup_260702. estimate JSP 미커밋 변경은 전 브랜치 동일 파일이라 무사히 유지됨.
- 다음: estimate JSP 커밋 시점, PR 생성 여부 — 사용자 지시 대기.

## [2026-07-02] 브랜치 분리 시도 -> 사용자 지시로 전량 원복 (%클라우드, 위 항목으로 대체됨)
- 사용자가 "작업별 새 브랜치 분리 필요" 언급 -> 구성 질문 무응답 상태에서 stash 2건+새 브랜치 2개(origin/main 기반) 생성·전환을 자의 실행 -> **사용자 질책 후 지시받아 전량 원복 완료**.
- 원복 결과(검증됨): Danga-order 체크아웃, 미커밋 4파일(bottom.js/bottom.jsp/business-status.jsp/estimate_unit_price_calculate.jsp) 원상복귀, stash 비움, 임시 브랜치 2개 삭제. 커밋 0건.
- **재발 방지 규칙 메모리 저장**: %클라우드 깃 상태 변경(브랜치 생성/전환·stash 등)은 명시 지시 시에만, 무응답이면 대기(feedback_cloud_git_state_ops_explicit_only).
- 유용한 부수 확인(조회): origin/main(b1b64bf)이 로컬 main보다 29커밋 앞서고, **Danga-order는 PR #19로 origin/main에 이미 머지됨**. 대상 3파일(bottom.js/jsp, business-status.jsp)은 origin/main과 diff 없음 -> 추후 분리 시 무충돌 이동 가능. 패치 백업 3개 scratchpad\git_backup\ 보관 중.
- 브랜치 분리 자체는 미해결 과제로 남음 — 사용자 지시 대기.

## [2026-07-02] 도면 미리보기 팝업(공통) 리사이즈 고정 + 썸네일 비율깨짐 수정 (%클라우드, 미커밋)
### 배경 (설계서 260629 PPTX 슬라이드 5 = "도면 보기" 공통 미리보기 모달)
- pq-grid fileSearchIcon 클릭 -> `callQuickDrawingImageViewer` -> `#common_quick_drawing_popup`(마크업 attr\tabs\bottom.jsp:992, init bottom.js:134, 함수 정의 3곳: attr\page\body-script.jsp:1039 / attr\common\body-script.jsp:1295 / resource\modules\attr\tabs\body-script.js:1001).
- 주의: "PPTX n번 이미지"는 media/imageN.png가 아니라 **슬라이드 순서** 기준(슬라이드3=도면등록/교체, 슬라이드5=도면보기 — media 번호로 착각해 한 번 헛짚음).
- 디자인 리뉴얼은 **사용자가 보류**("순수 디자인 수정 안 함"). 기능 수정만 진행.
### 변경 (2건, 각 한 줄, 미커밋 — %클라우드 커밋 사용자 몫)
- `resource/modules/attr/tabs/bottom.js:141` `resizable:true`->`false` (창 테두리 드래그 리사이즈 금지, 타이틀바 드래그 이동은 유지).
- `WEB-INF/views/attr/tabs/bottom.jsp:997` img에 `object-fit:contain` + `display:block; margin:0 auto`(공간 기준 중앙 배치, 사용자 추가 요청) + `onerror` blank.jpg 폴백 추가. 인라인 유지(CSS 이관 가능함을 22개 includer 전수 확인했으나 사용자가 인라인 유지 결정).
### 썸네일 깨짐 원인 (검증 완료)
- 인라인 `height:100%` + app.css(@import app/reset.css:56-60, 고도화 260601 추가)의 전역 `img{display:block;max-width:100%}` 조합 -> 높이고정+폭클램프 = fill 왜곡. 서버 `/qimage`(ImageView.java:84-97)가 세로도면을 270도 회전해 가로로 긴 이미지로 내려줘 빈발. 디코드실패 404(ImageView.java:107-114)+onerror 부재 = 깨진 아이콘.
### 검증
- 재현 하네스(실제 관리자 CSS 전부+마크업 복제, Playwright 1920x1080): 4비율(4:1/A판형/정사각/1:4)+404, 수정 전 왜곡·깨진아이콘 / 수정 후 전부 비율보존·넘침0·placeholder. 스크린샷 바탕화면 `예시\도면팝업_썸네일검증\shot_before|after_*.png`.
- **실서버(8081) 실측**: 재고관리 fileSearchIcon 5건 클릭 -> 전부 computed object-fit:contain(JSP 핫리로드 반영 확인), 비율보존, 넘침0. 실도면 1520x1074 정상 렌더. `예시\도면팝업_썸네일검증\real_1~5.png`, 스크립트 scratchpad\thumb_verify\.
- 실측 스크린샷에서 상세보기 버튼 우측이 살짝 잘려 보이는 건(전 케이스 동일) 이번 변경과 무관한 기존 상태로 추정 — 미조사.

---

## [2026-07-02] 수주현황(business-status) 그리드 헤더에 아이콘 렌더 (%클라우드, 미커밋)
### 배경 (화면설계서 260629 PPTX 슬라이드 40 = 수주관리>수주현황)
- 설계서 `고도화 및 수정 화면설계서_260629_01.pptx` **슬라이드 40**(media상 image61)이 수주현황(달력 화면) 설계. 주석: 전체 디자인 정리 / ①반품·불량·긴급 상태칩 / ②컬럼 위치 조정(작업지시번호 뒤에 작업상세 아이콘). 설계 이미지에는 아이콘 컬럼의 **헤더에도** 아이콘이 그려짐.
- 주의: 같은 PPTX 슬라이드 26·27은 수주관리(order-manage)+신규수주등록 설계로 별건(비용상세보기/고객사Rev./업데이트일시 등 — 전부 미반영 상태, 이 세션 앞부분에서 비교 완료).
### 변경 (pages/order/business-status.jsp만, 미커밋 — %클라우드 커밋 사용자 몫)
- 아이콘 컬럼 위치 이동(작업지시번호 뒤)은 **사용자가 직접 수행**. 이번 변경은 헤더 아이콘만.
- `title: ''` 였던 아이콘 컬럼 6곳(일별수주현황·긴급/반품/불량·납기지연 각 2곳, 307·324·447·465·540·558행)의 title에 셀과 동일 아이콘 span 삽입:
  `'<span class="shareIcon|fileSearchIcon"></span>'` — **인라인 style 없이 클래스만**(처음 13px 축소 style을 넣었다가 사용자 지시로 제거, 원본 17px 그대로). 사용자 실화면 확인 "적당하다"로 확정.
- **[추가] 긴급/반품/불량 그리드 구분 컬럼 상태칩(설계 ①)**: 바탕화면 `badges.html` 기준으로 구분 render를 배지 span으로 교체(반품=파랑/불량=노랑/긴급=빨강, 38x18 라운드 칩 CSS를 JSP 상단 `<style>`로 이식). TYPE_NM 값 3종은 order.xml selectBusinessEmergencyList(3543~3546행) CASE로 확정. 기존 render의 {style}(긴급 빨강글자/반품 노랑배경) 제거됨.
  - **클래스명은 `.badge` 아닌 `.business-status-badge`**(+--return/--defect/--urgent): admin 화면에 `.badge{padding:3px 7px}`(부트스트랩3 계열)가 이미 로드돼 충돌 → 개명 회피. 정적 grep으론 login CSS에만 보였으나 **computed style 실측으로 로드 확인**(grep만 믿지 말 것, 출처 시트 미특정).
  - **중앙정렬 함정**: pqGrid 셀은 `<div class=pq-grid-cell><div>내용</div></div>` 이중 구조라 render {style}은 바깥 셀만 적용됨. 안쪽 div의 `padding:3px 5px` 때문에 38px 칩이 우측 삐져나감 → render에 `cls:'business-status-badge-cell'` + CSS `.business-status-badge-cell > div{padding-left/right:0}`. 구분 컬럼 minWidth 40→44.
  - 검증(라이브 8081, Playwright 1920x1080, 메뉴 실진입): 실데이터 18행(반품6/긴급8/불량4), 셀중심=배지중심(965.3) 일치·overflow 0·배지 누락 셀 0·JS에러 0. 반품/긴급 육안 확인(scratchpad bizbadge_scrolled.png), 불량은 뷰포트 밖(동일 렌더경로). 주의: 이 그리드는 로딩 직후 pq-pending-refresh로 잠깐 hidden일 수 있어 검증 시 폴링 필요(verify_badge*.py).
### 근거 (pqGrid 11 소스 확인)
- `plugins/paramquery-11.0.0/pqgrid.dev.js` createHeaderCell(9411행)이 title을 escape 없이 raw HTML로 concat → 태그 렌더됨. getTitle(9365행)상 title은 문자열/함수 모두 가능.
- 이 화면은 toolbar:false + 엑셀내보내기/틀고정 셀렉트 없음 → title HTML 부작용 없음. (order-manage에 같은 걸 적용할 땐 exportGridToExcel은 stripHtml로 안전하지만, Fix/필터 셀렉트가 column.title을 그대로 option에 써서 빈 option 생김 — 보강 필요)
### 검증
- 8081 서버 가동 중(HTTP 200), JSP 핫리로드로 반영. 코드 상태는 grep으로 6곳 재확인. 실화면은 **사용자가 직접 확인 후 "적당하다"로 승인** — 이 건은 완료.

---

## [2026-07-01] PC 강제종료 후 상태 정정 (중요 — 아래 옛 섹션들보다 이 항목이 최신)
### 배경
- PC가 강제 종료되어 직전 HANDOFF가 실제 저장소 상태를 못 따라감. 재개 시 git 실측으로 대조한 결과 아래 불일치 확인.
### 실측 확인 (%클라우드, Danga-order)
- **아래 "[2026-07-01] 수주(order) 단가검토 DOM 견적 통일"·"견적 pqGrid 전환" 등 '미커밋'이라 적힌 작업들은 실제로는 이미 커밋됨**:
  - `6495ece` (2026-07-01 13:01, sjy5261, "단가검토 화면 수정") — estimate/order jsp·css, order css 삭제, order-manage.jsp 포함.
  - `02d9e27` (2026-07-01 13:43, sjy5261, "단가검토 아이콘 및 드롭다운박스 누락 수정").
  - 즉 옛 섹션들의 "미커밋" 표기는 무시할 것(HANDOFF가 커밋 시점을 못 따라간 상태였음).
- **현재 워킹트리 유일 미커밋 소스 변경**: `estimate_unit_price_calculate.jsp` 1개(+17/-40). 내용 = 견적 팝업 잔여 하드코딩 목업 전면 제거(기본정보 기타/접수번호, 기록조회 아코디언 건수 8/1/2/3→0 및 4그리드 샘플배열→[], 가공실적 요약 13,700/328,800/A→빈값, 외주단가합계 20,500→빈값, 가공실적/외주 그리드 목업→[]). **미커밋(%클라우드 커밋 사용자 몫).**
- untracked: `.claude/`, `shell/runDev.local.bat`. dev 서버 8081 LISTENING(재개 시 PID 25952).
### 라이브 검증 (8081, 1920x1080, EST_SEQ=12195)
- scratchpad/verify_est_mockup_removed.py: 최초 로딩 시 기타/접수번호/가공실적요약/외주합계 전부 빈값·아코디언 (0)x4·그리드 6개 rowCount 0. onLoadPage(12195) 후 실데이터 적재 정상(도면 유사형상테스트·페이저 1/10·규격 100*50*10·형태수량 단품/2). **JS 에러 0**. 요약·그리드가 빈 건 견적 CONTROL_SEQ 부재로 실쿼리 없음(설계상 정상). 캡처 est_mockup_loaded.png.
### 다음 단계
- estimate JSP 목업제거 변경은 검증 완료 — 사용자 커밋 대기. order JSP엔 별도 잔여 목업 있는지 미점검(필요 시 동일화).

---
_(주의: 아래는 강제종료 전 작성분 — '미커밋' 표기 다수는 위 정정대로 이미 커밋됨)_

## [2026-07-01] 답변검토 훅 / Stop 훅 구조 분석 (분석만 — 미적용)
### 배경
- 사용자: "검토 훅/스탑 훅 등 답변검토 부분이 불필요하게 복잡해진 것 같다. 분석해봐." answer-reviewer 검토 거쳐 확인함.
### 확인된 구조 (하나의 "답변검토" 행동이 6곳 분산)
- (a) `.claude/settings.json` Stop 훅 -> `answer_review_gate.py` 등록
- (b) `answer_review_gate.py` (transcript 파싱 + CLAIM_KEYWORDS 탐지 + 옵트아웃 마커)
- (c) `.claude/agents/answer-reviewer.md` (검토 에이전트, sonnet, 읽기전용)
- (d) `CLAUDE.md` "검토 반영 답변 구분 배너" + 옵트아웃 규칙
- (e) `memory/feedback_answer_reviewer.md`
- (f) `MEMORY.md` 인덱스 줄
### 복잡함이 낀 지점 (근거 확인됨)
1. 백스톱이 구조적으로 약함 — `answer_review_gate.py:9` 스스로 "답변 텍스트는 이미 화면에 표시된 뒤 실행되므로 첫 노출은 막지 못한다"고 인정. 즉 정정 답변을 하나 더 붙이게 유도할 뿐(이중 답변 구조).
2. 키워드 그물 과대 — CLAIM_KEYWORDS(줄19-26)에 git/커밋/쿼리/함수/메서드/캐시/브랜치/.java/.js 등 일반 기술어 포함 -> 웬만한 기술 턴마다 발동.
3. 옵트아웃 마커(`[검토 불요`, 줄30)는 2번 과발동을 되돌리는 패치 -> 넓은 게이트와 옵트아웃이 상쇄.
4. Stop 훅에 매 턴 종료마다 무조건 `gradlew build`+`pytest` 실행 블록(settings.json 줄16-24) — 리뷰와 무관하게 매 Stop이 비쌈.
- (참고) `context_freshness_gate.py`는 UserPromptSubmit 훅으로 답변검토와 별개(규칙 신선도용).
### 추천안 (미적용 — 실행 안 함)
1. 게이트를 "범위/변경 보고" 신호로 좁히기(git/커밋/브랜치/변경사항/수정사항만 남기고 일반 코드어휘 제거) -> 과발동 해소 + 옵트아웃 제거 가능.
2. Stop의 build+pytest를 `.java/.xml/.yml/.gradle` 더티일 때만 조건부 실행.
3. 정책 정본 1곳(CLAUDE.md)만 두고 메모리/에이전트는 포인터로 정리(6곳 동기화 부담 감소).
### 상태
- 사용자 "스스로 판단해" -> 게이트 좁히기 + Stop 조건부화로 진행 제안했으나, 설정 변경은 사전 확인 규칙([[feedback_explain_before_sensitive]])이라 확인 대기 중 대화가 단가검토로 전환됨. **훅/settings는 실제로 아무것도 변경 안 함.** 재개 시 위 추천안 1~3부터.

## [2026-07-01] 수주(order) 단가검토 DOM을 견적으로 전면 통일 (%클라우드, 미커밋)
### 요구/방침 (사용자 지시 절차)
- "견적/수주 단가검토 CSS를 하나로 통일. DOM 100% 동일하게." 절차: ①수주 DOM id/class 규칙 기억 ②수주 DOM 전부 삭제(form 포함), script만 남김 ③견적 DOM 전부 복사 붙여넣기 ④id/class만 수주값으로, 도면번호->작업지시번호 ⑤inline `<style>`를 CSS로 이관 ⑥실험 컴포넌트(우측 가공비 슬라이드 등) 버리고 그리드로.
### 변경 (전부 미커밋)
- **DOM 교체**: `order_unit_price_calculate.jsp`의 form 내부 DOM(.upc-root)을 견적 DOM 구조로 전면 교체. id/class는 수주값(orderCalculateForm, order-input-group, orderProcessGrid/orderOutGrid, CONTROL_NUM_SEL, DRAWING_NUM_html, SURFACE_NM_html, REGIST_NUM_html, OUTSIDE_UNIT_AMT, 공급가 실기능 UNIT_FINAL_AMT, DTL_EST_AMOUNT_html/DTL_AMOUNT_html). 헤더 라벨 도면번호->작업지시번호. **스크립트(비즈니스 로직) 무수정.** (섹션별 치환+스크립트 3종으로 실행: scratchpad/port_order_dom.py, port_records_and_style.py, unify_css.py)
- **가공실적/외주이력**: 정적 table -> 견적 pqGrid(orderProcessGrid/orderOutGrid). 견적 렌더헬퍼(perf*Render)+`fnInitPerfGrid`/`fnInitOutGrid` 수주 스크립트에 이식 + dataModel local 목업. 기존 tbody(orderProcessListHtml/outsideListHtml)는 hidden 보존(append no-op).
- **기록조회 그리드**: 수주 fnInitRecordGrid 설정(height220/flex)을 견적 것(content-fit 높이 + colModel 너비 정의)으로 교체.
- **우측 가공비 슬라이드 팝업(right_popup: 일반/특수가공) 제거**(견적엔 없음, 실험 흔적).
- **inline `<style>` -> CSS 이관**: 견적·수주 두 JSP head의 `<style>` 블록 제거, 각 규칙을 CSS로 이관.
- **CSS 통일 1개**: 수주 링크를 `estimate_unit_price_calculate.css`로 변경, `order_unit_price_calculate.css` **삭제**(불참조). 통합 CSS에 `#estimateCalculateForm,#orderCalculateForm` / `.estimate-input-group,.order-input-group` 병기 + order 전용 클래스(order_input_change 등) 흡수.
- **버튼 라벨**: `pages/order/order-manage.jsp`의 ORDER_MANAGE_UNIT_PRICE_CALCULATE "단가 검토"->"단가 상세검토" + 팝업 `<title>`도.
- **드롭다운 정리**: 소재/표면 select(.td_select)에 견적과 동일 SVG 캐럿 추가(통합 CSS -> 견적·수주 공통). 수주 작지번호는 실제 `<select id="CONTROL_NUM_SEL" class="upc-drawsel">`(견적 도면번호와 동일 구조)로 교체.
- **수주 목업 데이터 추가**: 기본정보 13행 + 외주단가합계 20,500 + 견적가합계 12,400 + 공급가 13,000. (단가입력/가공실적요약/상단그리드는 이식 때 견적 목업 포함)
### 무결성 검증 (정적)
- DOM 중복 id 없음(76개 전수). div 68/68 균형. answer-reviewer 최종검토 OK(6개 주장 파일 일치).
### 부작용 / 다음 단계 (중요)
- **바코드 드롭됨**: 견적 DOM엔 바코드가 없어 ORDER_CALCULATE_BARCODE_NUM/orderCalculateBarcodeSpan/Img 사라짐 -> 스캔 기능이면 재추가 필요(사용자 결정 대기).
- **스크립트 참조 21개 no-op**: right_popup 계열(orderNormalProcessCostListHtml/orderEtcProcessCostListHtml/UNIT_PROCESS_AMT_CAL/level*/btnPorcessCalculateUpdate 등) + 바코드 + 일부 총계(UNIT_*_TOT_AMT_html) + LINK_CHK. 요소 없어 jQuery no-op(에러 아님)이나 해당 기능 비활성. 되살릴지 결정 필요.
- **작지번호 dropdown 실데이터 미배선**: 견적 DRAWING_NUM_SEL처럼 옵션 채우는 핸들러 없음(현재 목업 옵션 1개). id를 _html->_SEL로 바꿔 auto-loop 텍스트 채움 대체됨.
- **실화면(라이브) 렌더 미검증** — 정적/무결성 검증만 함. dev 서버(8081) 띄워 수주관리->단가 상세검토 팝업 실렌더(그리드/캐럿/레이아웃/목업) 확인 필요.
### 관련 파일 (이번 작업 변경분)
- `common/order_unit_price_calculate.jsp`(M, DOM+그리드 스크립트 이식)
- `css/estimate_unit_price_calculate.css`(M, 통합본)
- `css/order_unit_price_calculate.css`(D, 삭제)
- `pages/order/order-manage.jsp`(M, 버튼 라벨)
- (참고: estimate-register.jsp 변경은 이번 작업 아님 — 이전부터 미커밋)

## [2026-07-01] 견적 "상세 견적 검토" 가공실적/외주이력 상단목록 pqGrid 전환 (%클라우드, 미커밋)
### 요구/방침
- 사용자: 가공실적·외주이력 컴포넌트에서 **상단 목록은 pqGrid 사용**, **아래 가로로 값 매칭되는 영역(요약)은 스크립트로 채울 예정**. "우선 지금 디자인 유지하는 방향으로 pqGrid로 구성". 데이터 배선은 다음 단계. 관련 메모리 [[project_perf_grid_design]].
### 변경 (JSP)
- 가공실적 상단 table(tbody#estimateProcessListHtml) -> `<div id="estimateProcessGrid" class="upc-perf-grid">`. **estimateProcessListHtml tbody는 display:none table 안에 hidden 보존**(기존 append 스크립트 fnGetEstimateProcessItem이 무해 no-op 되도록).
- 외주이력 상단 table -> `<div id="estimateOutGrid" class="upc-out-grid">`.
- **하단 요약 table 2개 유지**(가공실적: UNIT_COST_PROCESS_AMT/COST_PROCESS_SUM_AMT/INSPECT_GRADE_LIST · 외주단가합계). id 그대로라 기존 스크립트가 계속 채움.
- 스크립트: `fnInitPerfGrid(data)`/`fnInitOutGrid(data)` + 합성셀 render(`perfEquipRender` 장비명+작업자 2줄, `perfCostRender` 가공원가+임률 2줄) + `perfErrRender`(불량 빨강). 페이지 로드 시 빈 데이터로 즉시 호출. **데이터 갱신은 fnInitPerfGrid(data) 호출 말고 `$('#estimateProcessGrid').pqGrid('option','dataModel',{data}); refreshDataAndView` 권장**(재호출은 재초기화라 반영 안 됨 — 검증 중 확인).
- colModel: 가공실적=장비명 EQUIP_NM/공정 PROCESS_TYPE_NM/가공시간 WORKING_TIME/수량 FINISH_QTY/불량 ERROR_QTY/가공원가(임률) COST_PROCESS_AMT. 외주=빈아이콘 OUT_ICON/업체명 VENDOR_NM/공정 PROCESS_NM/공급단가 SUPPLY_AMT(외주 dataIndx는 실쿼리 미연결이라 임시). 필드명은 기존 fnGetEstimateProcessItem(selectInspectionListV1) 기준.
- 불량은 **cls 아닌 render**(perfErrRender)로 — cls는 pqGrid에서 헤더까지 물들여 빨강 헤더 됨(1차 실수 -> render로 교정).
### 변경 (CSS)
- `.upc-perf-grid/.upc-out-grid`의 `.pq-grid-col`(=ParamQuery11 헤더 셀)에 background #1a7f55 초록+흰 글자(기존 table.upc-grid 초록 헤더 유지). 1차에 `.pq-header-table th` 셀렉터 썼다가 회색(#d9d9d9) 그대로 -> `.pq-grid-col`로 교정. hwrap:true로 헤더 '...' 방지. `.upc-cell-sub`(7px 회색), `.upc-cell-error`(#e03131) 추가. 그리드 width 100%.
### 검증 (라이브 8081, 1920x1080)
- verify_perfgrid2/3.py: 두 그리드 초기화·헤더 6/4개 정확·헤더 배경 rgb(26,127,85)=초록·글자 흰색·전 헤더 clipped=false(가공원가(임률) 안잘림)·JS에러 0. 하단 요약 id 4개 유지. 샘플 데이터(dataModel 갱신) 주입 시 장비명 2줄"(홍길동)"·불량 "2" 빨강(rgb 224,49,49)·가공원가 2줄 렌더 정상. 캡처 perf_data.png(기존 table 디자인과 동일 모습).
### 주의/다음
- 미커밋(%클라우드 커밋 사용자 몫). JSP=핫리로드, CSS=하드리로드.
- **데이터 배선(다음 단계)**: 상단 목록 실데이터를 pqGrid dataModel로 피드(견적은 CONTROL_SEQ 없어 유사형상 연동 필요-기존 2단계 과제). 하단 매칭 요약도 스크립트로 채움(사용자 예정). 외주이력 실쿼리 미연결.
- order(수주)엔 미적용.

### [추가] 가공실적/외주 그리드 컬럼 폭을 목업에 맞춤 (2026-07-01)
- 소스: PPTX image4는 데이터/구분선 없어 픽셀로 컬럼폭 검출 실패 -> **목업 원본 CSS가 정답**. `C:\Users\USER\Desktop\예시\단가검토\참고-PPTX원본이미지\index.html` colgroup: 가공실적 **24/16/18/12/12/18**(%), 외주이력 **8/30/30/32**(%). (외주 헤더 목업은 '업체명/업체명' 오타 -> 실제 '공정' 유지, 폭만 채용.)
- 수정(JSP colModel width): 가공실적 fnInitPerfGrid **96/64/72/48/48/72**, 외주 fnInitOutGrid **32/120/120/128**, 각 컬럼 **minWidth:1**.
- **핵심 교훈(pqGrid autoFit 비율)**: width를 작은 px(24,16..)로 주면 autoFit이 남는공간 균등분배해 비율 왜곡. width 작은값+기본 minWidth면 작은컬럼 안줄고 큰컬럼이 남는폭 흡수(첫컬럼 과대). -> **width를 컨테이너 폭에 맞춘 px 스케일(합≈컨테이너)로 주고 minWidth:1로 기본최소폭 제약 해제** 해야 autoFit이 비율 유지. (기록조회 그리드는 고정폭+minWidth 방식이라 다름)
- 검증(라이브): 가공실적 실측 24.1/16/18/12/12/17.8, 외주 8/30.1/29.8/32.1 = 목업 목표 ±0.2 일치. measure_gridcols.py. 캡처 right_final.png.
- **★ 이후 사용자가 목업값 대신 직접 지정(자율측정 불신)** -> 최종값으로 교체:
  - 가공실적: 6컬럼 **전부 동일**(width 100 통일, minWidth:1) -> 실측 66/67 균등.
  - 외주이력: 아이콘 **16**(width/min/max 고정), 업체명 **125**(고정), 공정 **70**(고정), 공급단가 width190+minWidth1(**나머지** 흡수) -> 실측 16/125/70/188. (고정 3개는 min=max=width로 잠금, 나머지 컬럼만 열어야 특정폭+나머지 구현됨.)
  - 하단 요약 라벨폭(colgroup px): 가공실적요약 `<col40 x3><col><col55 x2><col>`(1EA가공원가·품질검사기록=col1~3합120, 합계=col5~6합110, 값셀 나머지), 외주요약 `<col40 x5><col><col>`(외주단가합계=col1~5합200, 값셀 나머지) -> 실측 라벨 120/120/110/200.
  - measure_gridpx.py / measure_labels.py.

### [추가] 우측 컴포넌트 비율을 PPTX image4에 맞춤 (2026-07-01)
- 방법: PPTX image4.png(3600x2040, slide4 베이스 목업) 우측 컬럼을 픽셀 분석(초록/파랑 헤더밴드 y투영+타이틀 실측)해 목표 비율 산출, 내 화면은 DOM(.upc-col-right 하위 4블록 rect)로 측정. 둘 다 전체 span 대비 %로 정규화 비교. 스크립트 scratchpad/measure_ratio.py, 분석 pptx_right.png.
- 목표(전체 span 대비, PPTX): 가공실적21.1 / 외주16.2 / 단가입력33.3 / 견적공급가13.3 / 사이여백16.2.
- 수정: CSS `.upc-col-right` **justify-content:space-between**(남는 세로를 컴포넌트 사이 갭 균등분배 -> PPTX처럼 컴포넌트 내용맞춤+여백넉넉). perf/out/견적공급가 블록 flex:(24/16/20) 1 auto -> **flex:0 0 auto**(내용맞춤), perf max-height:240 제거. 견적공급가만 **min-height:120px**(내용이 작아 목표13% 확보). JSP fnInitPerfGrid 빈shell **visRows 4->2**(가공실적 목록 축소로 perf 비율 하향).
- 결과(라이브 1920x1080): 가공실적19.9 / 외주15.7 / 단가입력35.2 / 견적공급가13.1 / 갭16.1. 편차 perf-1.2/out-0.5/price+1.9/supply-0.2/gap-0.1. **gap·supply 정확 일치**, 나머지 ±1.2 이내. price(단가입력)만 +1.9(행 많아 내용 고정, 더 못 줄임). 캡처 right_final.png — 컴포넌트 내용맞춤+여백균등, footer 보임, 흰공간 없음.
- 반복 과정(허락받아 자율): space-between+내용맞춤 1차 -> perf 큼 -> visRows 4->3 -> supply 부족 -> 견적공급가 grow(과함,갭붕괴) 되돌림 -> min-height:120 -> perf 미세큼 -> visRows 3->2 로 수렴.
- 주의: 각 컴포넌트 내용맞춤이라 작은 해상도서 내용합>높이면 스크롤(space-between 무효, footer 접근가능). 이전 F(해상도 적응 flex-grow)를 대체함.

### [추가] 가공실적 그리드-요약 사이 흰공간 제거 (2026-07-01, 재수정)
- 증상: 상단 pqGrid **데이터행 아래 빈 바디(62px 흰 여백)**와 요약 사이. 측정으로 정체 특정: grid-box와 요약는 이미 밀착(갭0), 흰공간은 pqGrid가 grid-box를 height:100%로 채우는데 데이터가 적어 데이터행 아래가 빈 흰색. (원래 table 디자인의 upc-grid-fill 역할과 동일 자리)
- **1차 실수/교정**: 처음엔 빈 shell을 height 34(헤더만)로 만들어 목록 영역까지 없앰 -> 사용자 "그리드 영역은 보존, 데이터행 아래 의미없는 흰공간만 없애라" 지적. 목록 보존하도록 재수정.
- 수정(현재): CSS `.upc-grid-box` **flex:0 0 auto, overflow:hidden**(내용 높이 밀착). JSP fnInitPerfGrid: `rowCnt=data?len:0; visRows=rowCnt>0?rowCnt:4; gridH=Math.min(33+visRows*32,240)`, height:gridH. -> **데이터 있으면 행수만큼(요약 밀착, 빈여백 제거), 빈 shell은 목록 4행 영역 보존**, 초과 시 스크롤.
- **데이터 배선 시 주의**: height가 초기화 시점 고정 -> 데이터 넣을 때 `pqGrid('option','height', Math.min(33+rows*32,240))` + `pqGrid('option','dataModel',{data})` + `refreshDataAndView`로 height 동시 갱신(dataModel만 바꾸면 height 고정돼 빈여백/스크롤).
- 검증: 빈 shell 목록4행+요약(gap_empty.png), 데이터2행 밀착(_whitespace_below_lastRow 62->4px, gap_filled.png), JS에러0. 외주이력(fnInitOutGrid height:'100%', upc-scroll2 90px)은 미변경.

## [2026-07-01] 견적 "상세 견적 검토" 단가입력 소재/표면 드롭다운 정리 (%클라우드, 미커밋)

## [2026-07-01] 견적 "상세 견적 검토" 단가입력 소재/표면 드롭다운 정리 (%클라우드, 미커밋)
### 대상/요구
- 파일: `common/estimate_unit_price_calculate.jsp` + `css/estimate_unit_price_calculate.css`. 단가입력 컴포넌트의 소재/표면 드롭다운: ①소재·표면 select 아이콘(화살표) 없게 ②표면은 데이터영역 셀 병합 + 하나의 드롭다운만.
### 변경
- **표면 하나만(JSP)**: 표면 데이터 셀(td colspan=2, 이미 병합)에 select 2개였음 — SURFACE_TREAT(H_D03 표면처리)+SURFACE_TREAT_DETAIL(H_D04 상세). SURFACE_TREAT_DETAIL select에 `style="display:none;"` 추가해 숨김 -> SURFACE_TREAT 하나만 셀폭 채움(w 90->184). **제거 아닌 숨김**: 인라인 JS가 #SURFACE_TREAT_DETAIL을 .html()/.val()로 참조(569/570/619/624줄 옵션채움, 996줄 저장) -> element 남겨 저장/스크립트 보존. 코드체계 D04->D03 통합 방향과도 일치([[project_code_system_migration]]).
- **아이콘 제거(CSS)**: `.upc-root .td_select`에 `background-image:none; -webkit/-moz/appearance:none;` + `::-ms-expand{display:none}` 추가. (기존 파일엔 background:transparent만 있었고 appearance:none은 전역 CSS 유래 computed였음 -> 화면 CSS에 명시적 보장. upc-drawsel(도면번호)과 달리 td_select엔 커스텀 화살표 배경이 원래 없음.)
### 검증 (라이브 8081, onLoadPage(12195) 데이터로드, 확대캡처 device_scale 2~3)
- probe_unit3.py: SURFACE_TREAT_DETAIL display:none·visible:false·w0, SURFACE_TREAT w184(td 201 채움), td colspan=2 유지. probe_unit2.py: 소재/표면 3 select 전부 appearance:none·bgImage:none(화살표 없음). 확대크롭 surface_loaded.png로 화살표 부재 육안 확인.
- answer-reviewer 검토: 표면 display:none·JS참조 다수 확인 OK. 최초 초안의 ".td_select에 appearance:none 있음" 표현은 파일 미선언(전역 computed)이라 지적받아 -> CSS에 명시 추가로 정정·해소.
### 주의
- 미커밋(%클라우드 커밋 사용자 몫). CSS=하드리로드, JSP=핫리로드(재시작 불필요). order(수주)엔 미적용.

## [2026-07-01] 견적 "상세 견적 검토" 기록조회 그리드 컬럼폭/hwrap (%클라우드, 미커밋)

## [2026-07-01] 견적 "상세 견적 검토" 기록조회 그리드 컬럼폭/hwrap (%클라우드, 미커밋)
### 대상/방식
- 파일: `common/estimate_unit_price_calculate.jsp`(견적, URL `/estimateUnitPriceCalculate`)의 기록조회 4그리드(recEstGrid/recOrderGrid/recOutEstGrid/recOutOrderGrid) colModel + `fnInitRecordGrid` 옵션.
### 변경 (사용자 지시)
- No 컬럼: width 50->40, minWidth 44->40 (4그리드 전부)
- 작업상세 아이콘 컬럼(`recDetailCol()` 공유 팩토리, 발주/외주견적/외주발주에만): width 24->40, minWidth 18->40
- 등록일자(REG_DT): width 92->75, minWidth 신규 75 (4그리드 전부). minWidth를 줘야 autoFit 비례축소로부터 폭이 보호됨(미지정 시 컨테이너에 맞춰 줄어듦).
- `fnInitRecordGrid` pqGrid 옵션에 `hwrap: true` 추가 -> 헤더 텍스트가 '...'로 잘리지 않고 wrap. (order-manage/control-manage/stock-manage 등 표준 grid 옵션과 동일.)
### 검증 (라이브 8081, 직접 /estimateUnitPriceCalculate goto, 1920x1080)
- scratchpad/verify_reccol.py: 아코디언 4개 강제펼침 + pqGrid refresh 후 헤더 leaf(.pq-grid-col-leaf) 실측. No=40·등록일자=75·아이콘=40 (발주/외주견적/외주발주). 견적기록은 아이콘 컬럼 없어 autoFit 남는폭 분배로 No=43·등록일자=77(약 +2~3px). 헤더 전 컬럼 clipped=false(잘림 없음). 캡처 scratchpad/recacc.png.
- answer-reviewer 검토 OK(4변경 전부 JSP 일치, queryId/로직 불변).
### 주의
- 미커밋(%클라우드 커밋은 사용자 몫). JSP라 핫리로드 작동(재시작 불필요). order(수주) JSP에는 미적용 — 동일화 필요 시 별도 지시.

## [2026-06-30] 견적 "상세 견적 검토" 팝업 image4(PPTX) 정밀 일치 A1~B15 (%클라우드, 미커밋)
### 대상/방식
- 파일: `common/estimate_unit_price_calculate.jsp`(견적, URL `/estimateUnitPriceCalculate`), `resource/asset/css/estimate_unit_price_calculate.css`. 기준: `단가검토 및 유사형상_260622.pptx` slide4(image4). 화면분석 세션(ea7b326d)의 차이목록 A1~B15.
- 검증: 라이브 8081 재기동 후 Playwright 캡처(1920x1080, EST 자동화테스트, AUTO-001) ↔ 목업 영역 크롭 대조. 15항목 모두 반영 확인.
### 적용 내역 (구조 A / 스타일 B)
- A1 도면View 안내문구 우측이동+문구교체(교차선택)+xi-presentation 아이콘 / A2 견적·공급가 '비고' 전체폭 행 제거(#NOTE는 hidden 보존-저장JS 참조) / A3 도면번호 셀 드롭다운 외형(upc-fauxsel+xi-angle-down) / A4 가공실적 선두 인덱스열 제거(헤더 col/th + JS row의 (idx+1)셀) / A6 기록조회 pqGrid 높이 행수맞춤(fnInitRecordGrid height 220고정→content-fit, 발주기록 컴팩트)
- B7 ■머리표 초록→검정 / B8 자동계산 배지→xi-calculator 아이콘 / B9 수량 'EA' 접미 제거 / B10 규격·형태 ' / ' 구분자 / B11 페이저 얇은꺽쇠→유니코드 삼각형(◀▶)+박스제거 / B12 도면번호 박스 좌측정렬 / B13 공급가행 라벨·화살표 회색(특이도 .upc-lbl.upc-disabled) / B14 기본정보 행 분리간격(border-spacing) / B15 '유사형태 기록조회'→'유사형태기록조회'
- **A5 보류(의도)**: 외주이력 2번째 헤더 목업 '업체명/업체명'은 명백한 오타 → 실제 '공정' 유지(분석도 동의). 사용자 확인 필요시 변경.
- B8 아이콘 글리프는 XEicon xi-calculator(그리드형)라 목업 계산기와 미세차 — 퍼블리셔 글리프 교체 여지.
### ★ JSP 핫리로드 근본수정 (별건이나 중요)
- 증상: JSP/CSS 수정이 화면에 반영 안 됨(서버 재시작해야 보임). 원인: `application-local.yml`의 jsp init-parameters가 `server.jsp:`(잘못)에 있어 Spring Boot 무시 → Jasper development=false. → `server.servlet.jsp:`로 들여쓰기 교정. 재기동 후 핫리로드 실작동 검증(재시작 없이 한 B11 편집이 work디렉토리에서 재컴파일됨). 자세히: 메모리 [[feedback_auto_server_restart]].
- **주의**: yml/JSP/CSS 모두 미커밋. %클라우드 커밋은 사용자 몫. application-local.yml 변경은 local 프로파일(dev) 전용.


## [2026-06-29] 단가검토 커밋 메시지 성격 확인 (코드 변경 없음)
### 내용
- 사용자 질문: 단가검토 페이지 수정을 커밋할 때 "마이그레이션"이라 하면 되나?
- 워킹트리 대조(Danga-order 브랜치, git diff/status): 변경은 정확히 JSP 2개(M, estimate/order_unit_price_calculate.jsp) + 신규 CSS 2개(A). **Java/매퍼XML/queryId 변경 없음**(`git status --short -- *.java *.xml` 빈 결과로 재확인).
- 판정(answer-reviewer 검토 OK): 이건 데이터/코드체계 **마이그레이션이 아니라 화면 markup을 목업 레이아웃으로 재구성한 UI 작업**(헤더/페이저/기본정보/기록조회 패널 신설, 인라인 style→외부 CSS 분리, canvas fit CSS 변경). → 권장 type **`feat`**(UI 구조 신설), 또는 동작 동일성 강조 시 `refactor`. "migration"은 부정확.
- **미해결(사용자 결정 대기)**: 견적+수주가 같은 Danga-order 워킹트리에 함께 있음. 메모리 정책(`project_danga_branch_policy`)상 견적은 **Danga-estimate 브랜치 신설 후 분리 커밋** 예정 → 지금 둘 다 커밋할지/분리할지 사용자 답변 대기 중. 답에 따라 커밋 메시지 확정.
- 코드/파일 변경 없음(권고만).

## [2026-06-29] 단가검토 좌측 기록조회 그리드 목업 (견적+수주, %클라우드, 미커밋)
### 요구
- 견적/수주 단가검토 좌측 "기록조회(동일 도면번호)" 4그리드를 다운로드 image(C:\Users\USER\Downloads\image.png) 기준으로 목업 채움. 그리드 내 아이콘은 작업상세정보 팝업(`g_item_detail_pop_view`)을 여는 shareIcon — 다른 그리드(order-manage.js 등)의 colModel render+postRender 방식과 동일.
### 변경 (estimate_unit_price_calculate.jsp / order_unit_price_calculate.jsp 둘 다, 미커밋)
- 아코디언 헤더에 건수 표기: 견적기록(8)/발주기록(1)/외주견적기록(2)/외주발주기록(3).
- `fnInitRecordGrid` 4호출에 image 기준 샘플 데이터 주입(견적8/발주1/외주견적2/외주발주3행). 컬럼명 외주 2종은 외주견적번호/외주발주번호로 보정.
- 작업상세 아이콘 컬럼: `recDetailCol()` 팩토리(매 그리드 새 객체) + `recDetailRender`(shareIcon span) + `recDetailPostRender`(클릭→`g_item_detail_pop_view`). **발주/외주견적/외주발주에만** 추가, 견적기록은 아이콘 없음(image 일치).
- 주의: 이 팝업엔 bottom.js 미로드라 `g_item_detail_pop_view` 미정의 → 클릭 핸들러 `typeof ...==='function'` 가드(목업이라 호출 시 안전 무동작). 실연결 시 키(CONTROL_SEQ/CONTROL_DETAIL_SEQ)+함수 로드 필요.
- 데이터는 로컬 샘플(실 "동일 도면번호" 쿼리 미연결). 테넌트 스케일: 정적 데이터·쿼리 없음 → 부하 영향 없음.
### 검증 (라이브 8081 재기동 후, 견적 팝업 실렌더)
- 서버 재기동 필수였음: 기존 PID 1536이 옛 JSP 서빙(Jasper 미재컴파일) → 종료 후 bootRun 새로 기동(logs/bootrun_recgrid.log). 현재 새 PID로 8081 LISTENING.
- scratchpad/verify_rec_grid.py: 견적 단가검토 팝업 열어 #recAccordion 확인. 헤더 건수 4개 정확, 견적 8행/발주 1행 로드, 강제펼침 후 아이콘 수 견적0·발주1·외주견적2·외주발주3(각 행마다, 견적만 없음). 캡처 scratchpad/rec_grid_est.png — image와 일치.
- 수주(order) JSP: **동일 코드 적용**(편집 동일), 견적에서 실렌더 검증 완료. order 팝업 별도 라이브 캡처는 미실시(진입경로 상이).
### 다음 단계
- 실 "동일 도면번호" 쿼리 연결 시 각 `fnInitRecordGrid` 4번째 인자(data) 교체 + 행 rowData에 CONTROL_SEQ/CONTROL_DETAIL_SEQ 채우고 g_item_detail_pop_view 로드.

---

_이전 최종 갱신: 2026-06-29 (가공실적 1단계)_

## [2026-06-29] 견적 단가검토 가공실적 컴포넌트 1단계 (구조+배선, %클라우드, 미커밋)
### 요구/결정
- 세 팝업(견적 단가검토 / 수주 단가검토 / 유사형상 기록조회)의 가공실적 컴포넌트는 **동일**해야 함. 기준은 **PPTX image4(견적)=image6(수주)** — 둘이 픽셀 동일: 메인그리드[장비명/공정/가공시간/수량/불량/가공원가(임률)] + 요약[1EA가공원가/합계/품질검사기록]. **order가 이미 이 PPTX 레이아웃과 일치**, 유사형상은 요약이 다름(임률가공비/가동시간계/반영가공비/불량실적 — 추후 통일 대상). 사용자 지시: "일단 order 기준으로 작업, 통일은 나중에" + "1단계로 해".
### 핵심 제약 (검증 확정)
- 가공실적 데이터는 전부 `TBL_MCT_WORK`(실제 기계가공 로그)에서 나오고 **조회키가 CONTROL_SEQ/CONTROL_DETAIL_SEQ**(수주/작업지시). 쿼리 `orderCalculate.selectInspectionListV1`(소스: TBL_MCT_WORK/TBL_EQUIP/TBL_MCT_WORK_INSPECT/TBL_CONTROL_PART/TBL_USER) + 품질검사 `drawingSameArchive.selectInspectionArchiveDataList`.
- 견적 데이터 쿼리(`selectEstimateDataList`/`selectEstimateCalculateDataList`)는 TBL_ESTIMATE/_DETAIL만 써서 **CONTROL_SEQ/ORDER_SEQ가 없음** → 견적 품목엔 자기 가공실적이 원천적으로 없음. order는 자기 CONTROL_SEQ로 채움. 견적은 유사형상에서 고른 과거주문 CONTROL키를 되먹여야 채워짐(2단계).
### 1단계 완료 (estimate_unit_price_calculate.jsp만 수정, 미커밋)
- 가공실적 메인 그리드 tbody에 `id="estimateProcessListHtml"`, 요약 셀에 `UNIT_COST_PROCESS_AMT`/`COST_PROCESS_SUM_AMT`/`INSPECT_GRADE_LIST` 부여(order와 동일 마크업·class).
- order의 가공실적/품질검사 채우기 로직을 견적용 함수 `fnGetEstimateProcessItem()`로 이식(selectInspectionListV1 + selectInspectionArchiveDataList). `setEstimateRowSelect`에서 호출.
- **CONTROL_SEQ 가드**: estimateData.CONTROL_SEQ 없으면 셀 비우고 return → 견적은 키가 없어 그리드 빈 상태(구조/배선만 order와 동일, 2단계 데이터 피드 준비). fnIsEmpty는 공통 attr/common/body-script.jsp 전역 헬퍼.
### 검증 (라이브 8081, EST_SEQ=12195)
- 서버 재기동: bootRun은 **`--args='--spring.profiles.active=local --server.port=8081'` 필수**(application.yml 비어있음, local 기본포트=80). 프로파일/포트 누락 시 banner 직후 exit1. 로그 logs/bootrun_8081i.log, 현재 PID 1536.
- 스크립트 scratchpad/verify_est_perf.py: 신규 id 4개 존재, 헤더=장비명|공정|가공시간|수량|불량|가공원가(임률)(PPTX 일치), fn 정의됨, 페이저 1/10→next→2/10 정상, **JS에러 0**, 그리드 rowCount 0(가드 정상). 캡처 scratchpad/est_perf_block.png.
### 다음 단계 / 주의
- **2단계(데이터 피드)**: 유사형상에서 고른 과거주문 CONTROL키를 견적 팝업으로 되먹여 fnGetEstimateProcessItem에 전달.
- **유사형상 요약 통일**: 추후 유사형상 요약을 PPTX(1EA가공원가/합계/품질검사기록)로 맞춰야 세 팝업 완전 동일. 단 현재 동작중인 가동시간계/반영가공비/불량실적 3필드 제거라 사용자 확인 필요.
- 유사형상 죽은코드: selectMctworkArchiveDataList가 채우려는 `drawingSameMCTWorkHtml` tbody가 HTML에 미선언(무효).
- 오늘 아침 java 프로세스 3개(23060/32980/33960) 잔존(포트 미점유, 미확인이라 미정리).

---

_이전 최종 갱신: 2026-06-29 (세션 종료)_

## ★ 현재 상태 요약 (먼저 읽기)
### 작업 목표
단가검토 팝업 2종 UI 개선 — 견적(`estimate_unit_price_calculate`) / 수주(`order_unit_price_calculate`). order 디자인을 estimate에 이식하고, 양쪽에 공통 개선 적용. 모두 %클라우드, **전부 미커밋**(커밋은 사용자 몫).

### 완료 (이번 세션, 라이브 검증됨)
- **견적(estimate)**: ①order 디자인 이식(색·단가입력 라벨 파랑/크림 분리·보류셀 단색·도면 cover) ②목록적재 결함 수정(setEstimateRowSelect에 페이저·헤더 도면번호 배선 추가 — 이전엔 데이터 담겨도 0/0 표시) ③기록조회 pqGrid 이식 ④기본정보 행별 갱신(규격/소재/표면/형태수량/등록일자 바인딩) ⑤최초로딩 목업 제거 ⑥우측 비율 PPTX(24/16/36/20) ⑦해상도 적응(flex 가중치) ⑧외주이력 2행+스크롤 ⑨도면번호 박스 빈값 크기유지.
- **수주(order)**: estimate와 동일 적용 — 해상도 적응·외주이력 2행 스크롤·목업 제거·기본정보 행별 갱신·작업지시번호 박스 크기유지. (order는 백엔드 있어 실데이터로 채워짐, 공급가 정상)
- **라이브 검증**: 견적 EST_SEQ=12195 / 수주 CONTROL_DETAIL_SEQ=92000013. 1920x1080·1600x900·1536x864에서 footer 보임·overflow 없음. 데이터 적재 정상, JS에러 0, 빈 도면번호박스 180x26 유지.

### 미완 / 다음 단계 (결정 대기)
- **기타·접수번호(양쪽)**: 쿼리에 컬럼 없어 빈 셀 — 백엔드 컬럼 추가 또는 행 제거 결정 필요.
- **기록조회 그리드(양쪽)**: 실 "동일 도면번호" 쿼리 미연결(빈 그리드, strNoRows). 연결하려면 dataModel.data 교체.
- **1366x768**: ~50px 초과로 스크롤(흔치 않은 해상도, 안전장치로 처리). 더 줄이려면 추가 압축 필요.
- **견적 등록일자**=UPDATE_DT(수정일시) 매핑 — 라벨 뉘앙스. 등록일시 전용 컬럼 필요 시 교체.
- **견적/공급가**: estimate에만 '비고' 행 1개(공급가 비활성 대체). PPTX와 다름 — 유지 결정.
- **도면 canvas cover** 실렌더 미검증(테스트 항목에 이미지 GFILE 없음).

### 블로커·주의
- **미커밋 4파일**: estimate JSP(M)/CSS(??), order JSP(M)/CSS(??). estimate·order JSP는 **init 커밋본 외엔 미커밋** → 06-26 재구성 + 이번 변경이 한 덩어리. `git restore` 시 전부 소실 → **커밋 권장**.
- 서버 8081 가동 중. **CSS=하드리로드 / JSP·Java=재시작 필요**(재시작 자동화 규칙 메모리 저장됨).
- 검증 도구: %테스트 `.env`(WEB_URL=smd.localhost:8081) + `nav.login_simple`. DB=smd(121.165.20.66). 테스트 스크립트 scratchpad/test_est_*.py, test_order.py, measure_*.py.

### 관련 파일
- `%클라우드\src\main\webapp\WEB-INF\views\common\estimate_unit_price_calculate.jsp` / `order_unit_price_calculate.jsp`
- `%클라우드\src\main\webapp\resource\asset\css\estimate_unit_price_calculate.css` / `order_unit_price_calculate.css`
- 쿼리: `sqlMaps\v1\estmateCalculate.xml`(selectEstimateCalculateDataListV1), `sqlMaps\orderCalculate.xml`(selectOrderCalculateDataList)

---

## [2026-06-29] 견적 단가검토 = 수주(order) 변경점 이식 + 목록 적재 기능 검증/수정 (%클라우드)
### 대상/방식 (미커밋 — 커밋 사용자 몫)
- `estimate_unit_price_calculate.jsp`(수정) + `.../css/estimate_unit_price_calculate.css`(신규·untracked). order(17:02 재구성본)가 estimate(16:18 마감본)보다 앞서 있어 그 갭(변경점)을 이식.
### A. order 변경점 이식 (디자인)
- CSS: 초록 `#2f7d5f->#1a7f55`, 슬레이트 `#5a6470->#6b7280`. 단가입력 라벨색 분리: `.upc-blue=#a9d3f5`(파랑,합계/헤더행) / `.upc-lbl=#f5ecc8`(크림,입력라벨) — 기존엔 둘 다 #d6e6f4. 보류셀 해치->단색 `#f3f5f7`. 인풋 height:100%->22px 고정 + :focus 크기불변. 우측 perf-block flex:1 1 auto/min120(가공실적 채움)·out-block flex:0 0 auto. scroll2/sticky thead/acc-grid width 추가.
- JSP: 단가입력 upc-blue/upc-lbl 재배정(규격/형태·수량적용가·적용금액계=파랑). 도면 canvas 인라인스타일 object-fit cover로 교체.
- 유지한 견적 고유차: 제목 "상세 견적 검토", 헤더=도면번호(작업지시·바코드 없음), 견적번호, 공급가 행 비활성, 종전단가 hidden, 수주 전용 비활성행 미추가.
- order와 의도적 불일치 1건: 가공실적·외주이력은 견적 백엔드가 없어 order 정적샘플(3,200/76,800/에이탑/1,500)을 넣었다 되돌림(레이아웃만, 값 비움). 이유: 실데이터와 나란히 영구 가짜값=오해. 견적단계엔 가공실적 본래 없음.
### B. "목록 적재" 기능 검증 + 수정 (사용자 요청)
- 호출흐름: 견적작성 `#btnEstimateUnitPriceCalculate`(estimate-regist.js 2236) -> window.open('/estimateUnitPriceCalculate') -> onLoadPage(EST_SEQ) -> getEstimateDataList(estimateCalculate.selectEstimateDataList) -> 데이터 있으면 첫 행 자동선택·폼 채움.
- 검증(라이브 8081, EST_SEQ=12195 상세10행, smd.localhost:8081 .env 자격증명, qa nav.login_simple): 목록 적재 정상(datasource 10건·hidden목록 20tr·첫행 노랑선택·실데이터·JS에러 0).
- 발견 결함: order setOrderRowSelect엔 있는 헤더 페이저(estPagerInfo)·도면번호박스(estHeaderDrawingBox) 갱신이 estimate setEstimateRowSelect엔 누락 -> 데이터는 담겨도 페이저가 0/0 정적, 헤더가 샘플 DWG-TOMES-001 고정 -> "목록 안 담긴 것처럼" 보임.
- 수정: setEstimateRowSelect 첫머리에 order와 동일 배선 추가(페이저 idx+1/length, 헤더박스=현재행 DRAWING_NUM). 재검증 PASS: 1/10 표시, 헤더=유사형상테스트, prev/next로 1/10->2/10->3/10 + 행별 규격·수량·단가합계 실시간 갱신.
### 검증/한계
- div 60/60·form1/1·table8/8, 핵심 스크립트 ID 전수 1개씩 보존. 캡처 scratchpad est_danga_12195.png/est_final_12195.png, 테스트 test_est_danga.py/test_est_nav.py(nav.login_simple, headless).
- 도면 canvas 실렌더 미검증(테스트 행에 이미지 GFILE 없음). 가공실적/외주이력 실데이터는 견적 백엔드 부재로 영구 비표시(설계상).
### 관련 파일
- `.../common/estimate_unit_price_calculate.jsp`, `.../css/estimate_unit_price_calculate.css`.

### C. [추가요청] 기록조회 그리드 + 기본정보 행별 갱신 (estimate JSP)
- 1) 기록조회 그리드: 정적 placeholder 4개 -> order와 동일 pqGrid(11.0.0) 이식. `recEstGrid/recOrderGrid/recOutEstGrid/recOutOrderGrid` 컨테이너 + `fnInitRecordGrid()`(스크립트 끝) + 아코디언 FIFO 토글(최대2). **데이터는 order처럼 로컬 샘플**(실 "동일 도면번호" 쿼리 연결은 추후 — order도 동일 상태). 라이브 검증: 견적기록5행/발주기록1행 렌더, 4개 모두 pq-grid 초기화.
- 2) 기본정보 행별 갱신: 정적이던 규격/소재종류/표면처리/형태·수량/등록일자를 V1 쿼리(selectEstimateCalculateDataListV1) 값으로 바인딩. 단가입력과 id 겹치는 규격(SIZE_TXT)/형태·수량(WORK_TYPE_NM·ITEM_QTY)은 중복 id 회피 위해 `BI_SIZE_TXT_html`/`BI_WORK_QTY_html`로 분리해 fnJsonEstimateDataToFormHtml 콜백에서 명시 셋팅. 등록일자=UPDATE_DT_html, 소재종류=MATERIAL_DETAIL_NM_html, 표면처리=SURFACE_TREAT_NM_html+SURFACE_TREAT_DETAIL_NM_html은 auto 루프가 자동 반영. 라이브 검증(prev/next): 규격 100->200->300, 형태/수량 단품/2->3->4 행마다 갱신.
- **한계/보고**: 등록일자는 UPDATE_DT(수정일시)라 라벨 뉘앙스 있음. 소재/표면 없는 행은 빈값(실데이터 그대로). 가공실적/외주이력은 견적 백엔드 없어 비표시 유지. div60/60·form1/1·table8/8·중복id 0.

### D. [추가요청] 최초 로딩 시 무의미한 목업 데이터 제거 (estimate JSP)
- 정적 하드코딩 샘플 전부 비움(셀/구조/ID는 유지, 값은 onLoadPage->fnJson이 채움):
  - 기본정보 13행 값(등록일자/견적번호/도면번호/품명/고객사/프로젝트/모듈명/규격/소재종류/표면처리/형태수량/기타/접수번호) -> 빈 셀.
  - 헤더 도면번호 박스(estHeaderDrawingBox) DWG-TOMES-001 -> 빈값.
  - 단가입력 SIZE_TXT/WORK_TYPE_NM/ITEM_QTY/UNIT_MATERIAL_AUTO_AMT(3,450)/UNIT_SURFACE_AUTO_AMT(2,345)/TOT_AMT(334,800), 견적가 input value(12,400)/DTL_AMOUNT(12,400) -> 빈값.
  - 기록조회 그리드 4종 로컬 샘플 배열 -> [] (그리드 형태 유지, strNoRows '(목록 추후 연결)' 표시).
- 검증: grep 잔여 목업 0. 라이브(EST_SEQ=12195) — 최초 로딩 시 전 셀 빈값, onLoadPage 후 실데이터 정상 적재(도면 유사형상테스트/규격 100*50*10/금액계 18,800/페이저 1/10). 단가입력 소재·표면 select는 첫 옵션 기본값 표시(목업 아님, HighCode 서버 옵션). 캡처 scratchpad est_clean_load.png.
- 미해결 잔존: 기타·접수번호는 빈 셀(견적 쿼리 컬럼 없음 — 백엔드 추가/행 제거 결정 대기).

### E. [추가요청] 우측 컴포넌트 비율을 PPTX image4에 맞춤 (estimate CSS만)
- 기준: 사용자 제공 캡처 2장(PPTX 회색헤더 vs 내 화면 초록헤더) + PPTX image4. PPTX 우측 섹션 비율(타이틀 위치 측정) = 가공실적 24 / 외주이력 16 / 단가입력 36 / 견적공급가 20 (%).
- 시행착오(기록): 가공실적이 남는높이 다 먹던 문제(과대) -> grid-box 62px로 과축소(데이터영역 사라짐) -> 행 padding/인풋 높이까지 줄였다가, 측정 결과 **행 높이는 원래(34px)가 PPTX 비율(행당 ~33px)에 맞고 진짜 문제는 가공실적 슬랙 독식뿐**임을 확인하고 행 축소를 전부 되돌림.
- 최종(estimate CSS만, **order 미변경**): `.upc-perf-block` `flex:0 0 auto`(가공실적 안 늘림). `.upc-grid-box` `flex:0 0 auto; height:130px`(데이터영역 ~4행, PPTX). 행/인풋은 원복(upc-price/upc-grid padding 6px, td_input 22px). 남는 높이는 `.upc-out-block`+`.estimate-input-group + .estimate-input-group`(견적공급가)에 `flex:1 1 auto`로 나눠 채워 하단 공백 제거(footer 하단 정착). footer margin-top:auto는 제거.
- 잔존 차이: 견적/공급가에 estimate 전용 '비고' 행 1개 존재(PPTX는 비고가 열) — 공급가 비활성이라 NOTE 자리 확보용. 기능상 유지.

### F. [추가요청] 해상도 적응 — 고정 비율이 해상도 깨던 문제 (estimate CSS만)
- 문제: E에서 비율을 1920x1080 고정값으로 잡아, **1536x864(1080p@125% 배율 등) 등 낮은 해상도에서 content(951px) > 컬럼(788px)로 footer가 잘림**(overflow:hidden). "해상도 안맞" 신고.
- 해결(반응형): 우측 섹션을 **flex grow 가중치로 가변화** — `.upc-perf-block flex:24 1 auto`(min96/**max240**, 과대 방지), `.upc-out-block flex:16 1 auto`, 견적공급가 `flex:20 1 auto`. 단가입력은 행 높이 보존 위해 고정(flex:0 0 auto). `.upc-grid-box`는 `flex:1 1 auto;min-height:0`(가공실적 데이터영역이 화면에 맞춰 늘고/줄음). col-right `overflow-y:auto`(작은 화면 스크롤 안전). content 최소높이 축소 위해 행 압축(upc-price padding 4px, td_input 20px, col gap 8px).
- 검증(라이브, EST_SEQ=12195, footer 가시성+overflow): **1920x1080 / 1600x900 / 1536x864 = footer 보임·스크롤 없음 OK**. 1366x768만 50px 초과로 스크롤(footer 접근 가능). 1080 비율 측정: 가공실적 23.9 / 외주 16.3 / 단가 33.2 / 견적 19.8 (%) — PPTX(24/16/36/20)에 거의 일치. 작은 화면에선 가공실적 데이터영역이 줄며 적응(해상도 우선). CSS 직접 서빙 → 재시작 불필요.

### G. [추가요청] 외주이력 2행+스크롤 / 도면번호 박스 빈값 크기유지 / 수주(order) 동일작업
- **외주이력 2행 스크롤(estimate)**: `.upc-scroll2` max-height:92px -> `height:90px`(헤더+2행 고정 reserve)+overflow-y:auto+sticky헤더. 목업 3행으로 검증: visibleRows=2, 3번째 스크롤(확인 후 테스트행 제거, 평소 빈 상태).
- **도면번호/작업지시번호 박스 빈값 크기유지(양 화면)**: `.upc-wo-box`를 `display:inline-flex; align-items/justify-content:center; min-height:26px` 추가 -> 값 없어도 180x26 유지. 라이브 확인(order 빈 박스 w180 h26).
- **수주(order) 동일 작업 = estimate와 똑같이 적용(order CSS/JSP만)**:
  - CSS: 해상도 적응(perf-block flex:24/min96/max240, out-block flex:16, `.order-input-group + .order-input-group` flex:20, col-right overflow-y:auto, gap8, price padding4, td_input20), scroll2 height:90px, wo-box min-height.
  - JSP: 최초 로딩 목업 제거(헤더 작지번호/기본정보 13행 값/단가입력 샘플/가공실적·외주이력 요약/기록조회 그리드 4종 -> 빈값·[]; JS가 실데이터로 덮음). 기본정보 행별 바인딩(규격=BI_SIZE_TXT_html, 형태수량=BI_WORK_QTY_html 명시 셋팅; 소재종류=MATERIAL_DETAIL_NM_html, 표면처리=SURFACE_NM_html은 fnJson auto-loop). 종전단가 등 비활성행/right_popup/스크립트·queryId 불변.
  - 검증(라이브 CONTROL_DETAIL_SEQ=92000013, 1920x1080 & 1536x864): 데이터 적재 OK(pager 1/2·작지 C25-1016-0013·도면 유사형상테스트·형태수량 단품/4·견적가/공급가 3,000/12,000 실값·order 고유 공급가 정상), footer 보임·overflow 없음, 빈 박스 180x26, div77/77·중복id 0·JS에러 0. (규격/소재/표면이 빈 건 해당 주문항목에 실데이터 없음 — 바인딩은 형태수량 채워짐으로 입증)
- div60/60(estimate)·77/77(order). estimate JSP는 재시작 필요 변경 시 자동 재시작 규칙 적용.

## [2026-06-26] 수주 단가검토 팝업 — image6 "목업-우선(방식B)" 전면 재구성 (%클라우드, order_unit_price_calculate)
### 대상/방식
- 파일: `common/order_unit_price_calculate.jsp`(수정) + `resource/asset/css/order_unit_price_calculate.css`(신규·untracked). 브랜치 main, **미커밋**(커밋 사용자 몫).
- 방식 B(목업-우선): 본문을 PPTX image6 목업 마크업 구조로 전면 재구성, CSS는 목업 style.css 이식(전 클래스 `upc-` 접두 + `.upc-root` 스코프). 기능 전부 보존.
### 동시편집 사고/정리
- 다른 세션(transcript `06aecd85`)이 같은 order 파일을 동시 편집(단가입력 174줄 재구성 + CSS upc-hold) → 사용자 지시로 그 편집을 NEW→OLD 되돌리고 내가 단일세션으로 재작업. estimate_unit_price_calculate.jsp/.css는 그 세션 소관(미터치).
### 완료 (기능보존 검증: grep + answer-reviewer)
- 기능 훅 전수 보존: id 91개·name·c:forEach(H_D01/D03/D04·H_1057)·canvas(img_c)·pqGrid 4개·right_popup(죽은 UI verbatim). div 균형.
- 레이아웃: 헤더(제목/페이저/작업지시번호/바코드/유사형태버튼) / 좌(기본정보 13행+기록조회 아코디언) / 중(도면 canvas, object-fit cover) / 우(가공실적·외주이력·단가입력·견적공급가·푸터).
- 기본정보: 목업 13행(등록일자~접수번호)+값. 목업에 없는 수주필드(작업/수량·진행상태·종전단가)는 **비활성(upc-disabled) 행**으로 표시(id 보존).
- 색(image6 픽셀대조): 초록 #1a7f55 / 헤더 파랑 #a9d3f5 / 입력라벨 크림 #f5ecc8 / 슬레이트 #6b7280. 단가입력 **합계행(규격/형태·단가합계·금액계·수량적용가·적용금액계)=파랑**, 입력라벨(소재비·소둔·제관·용접·가공비 등)=크림. 보류셀 upc-hold=단색 #f3f5f7(해치 제거).
- 우측 컬럼: 가공실적이 컬럼을 채움(flex:1 1 auto, image6처럼 긴 데이터영역), 가공실적/외주이력 그리드 max-height+overflow 스크롤(헤더 sticky).
- 기록조회 pqGrid: 로컬 샘플데이터 + height 220, 셀폭 채움(width:100%).
- 인풋: td_input/td_select **고정높이 22px + :focus 박스변화 차단** → 포커스 시 컴포넌트 크기 불변.
- TEMP: 표시값은 목업 샘플 하드코딩(실주문 선택 시 JS가 덮음). backing 없는 행(품명/규격/소재종류/표면처리/모듈명/등록일자/형태수량/기타)은 정적 샘플 → 실데이터 와이어링 필요.
### 검증/한계
- 정적 렌더(전체 25 CSS, 1920×1080)로 색·레이아웃·스크롤·비활성·인풋높이 확인. 캡처: `C:\Users\USER\Desktop\예시\단가검토\캡쳐\`(upc_render.png+좌/우 크롭). 렌더 하니스: `scratchpad/render_upc.py`(header.jsp의 25개 CSS 전부 로드).
- **라이브(8081) 미검증**: 기록조회 pqGrid 실렌더·도면 canvas cover 실동작·인풋 포커스 크기불변. 하드리로드로 확인 필요(CSS/JSP는 src 직접 서빙, Jasper 재컴파일).
### 주의
- CSS `var(--upc-*)`가 브라우저에서 미해석되는 현상 → 전부 리터럴 색으로 인라인(원인 미확정). 미사용 토큰 `--upc-blue-head:#d6e6f4` 잔존(무해).
- python 직접 치환으로 order JSP가 LF 줄바꿈(git autocrlf가 커밋 시 정규화, 내용 diff 무영향).
### 회고(색 오분류)
- 수량적용가/적용금액계를 위치/그룹 추정으로 크림 분류 → image6 셀별 픽셀샘플로 파랑 정정. 교훈: 라벨 색은 그룹 추정 말고 **셀별 직접 샘플**.

## [2026-06-26] 견적 페이지 — order 완성본 수준으로 마감 (%클라우드)
order(수주) 페이지가 다른 세션에서 `upc-` 접두사 목업+이식으로 정상 완성됨을 확인. 동일 기준으로 견적 페이지(`estimate_unit_price_calculate.jsp`)를 마감.
- **CSS**: `estimate_unit_price_calculate.css`를 order CSS와 동일 구조로 재작성(form id만 estimate). 마감 헬퍼 전부 포함: `upc-perf-block`/`upc-out-block`/`upc-grid-box`/`upc-grid-fill`/`upc-fillcell`/`upc-empty`/`upc-autocalc`/`upc-dropdown`/`upc-selcell`/`upc-prev`.
- **본문 마감(완성도 차이 해소)**: ①미바인딩 셀에 목업 샘플값 채움(기본정보 13행 전부, 단가입력 3,450/2,345/334,800/규격300*50*10/수량5, 견적가 12,400 — 실데이터 연결 시 JS가 id매핑 셀 덮음) ②가공실적/외주이력을 해치 placeholder→목업 grid-box/grid-fill/fillcell 레이아웃으로 ③기본정보 미바인딩 행을 해치→샘플 디자인필, 도면번호는 upc-dropdown(노랑) ④페이저 0/0·헤더 도면번호 박스 채움(정적, 스크립트 연동 전).
- **불변**: image4 차이(도면번호 헤더/바코드 없음/견적번호/공급가 비활성) 유지, estimate ID·`estimate-input-group`·인라인 스크립트 불변(diff 0). 종전단가(PREV_UNIT_FINAL_AMT_ITEM_QTY_html)는 image4 미표시라 hidden 보존.
- **검증**: 핵심 ID 45개 1개씩·중복 0·태그 균형(div 59/59·table 8/8·form 1/1)·스크립트 diff 0. 재시작 후 1920×1080 렌더 — image4/order 수준으로 채워져 표시, Jasper/500 에러 없음.
- **남음**: 페이저 n/total·헤더 도면번호 실시간 갱신, 가공실적/외주이력/기록조회 실데이터는 견적 백엔드/스크립트 연동 필요(현재 정적 디자인필).

## [2026-06-26] 단가검토 팝업 2종 페이지 식별 정정 + 견적 페이지 image4 재구성 (%클라우드)
### 페이지 식별 (재발 방지 — 중요)
- `order_unit_price_calculate.jsp` = 제목 "단가검토", `/orderUnitPriceCalculate`, **수주관리**에서 열림(`order/control-manage.js`, `order/order-manage.js`), 목업 **image6**.
- `estimate_unit_price_calculate.jsp` = 제목 "단가계산(견적)", `/estimateUnitPriceCalculate`, **견적작성**에서 열림(`biz/estimate-regist.js`), 목업 **image4(상세 견적 검토)**.
- PPTX `바탕화면\Tomes\(26.06)단가검토 변경점\단가검토 및 유사형상_260622.pptx`: image4=견적, image6=수주. 사용자 제공 `참고-PPTX원본이미지/index.html`은 image6 기준.
- 1차 실수: "견적작성의 단가검토"를 제목 문자열만 보고 order 페이지로 오인 → 호출처(window.open) 추적으로 정정. **페이지 식별은 컨트롤러 매핑+호출 JS로 확정할 것.**
### 작업 (견적 페이지 image4 재구성)
- 대상: `estimate_unit_price_calculate.jsp`(견적작성용). order와 달리 마이그레이션 전 상태였음.
- image4 레이아웃으로 전면 재구성, **스크립트 미변경**, 기존 ID/name/class 보존, 신규/미지원은 보류.
  - 헤더: 제목 "상세 견적 검토" + 페이저(btnPrev/NextEstimateData 헤더 이동) + 도면번호 박스 + 유사형태버튼. (image4엔 바코드 없음)
  - 좌: 기본정보(견적번호·도면번호·품명·고객사·프로젝트·모듈명·종전단가 연계 / 등록일자·규격·소재종류·표면처리·형태수량·기타·접수번호 보류) + 기록조회 아코디언(정적 placeholder).
  - 중앙: 도면 캔버스(img_c) + 목업 프레임/Tab 힌트.
  - 우: 가공실적·외주이력(견적 백엔드 미지원 → placeholder) + 단가입력(목업 구조, 기존 ID 연계) + 견적/공급가(단가/합계/비고, **공급가 행 비활성**).
  - 신규 단가필드(배송비·기타추가·수량적용가·적용금액계)·기본정보 신규행·공급가행 = `.hold`(사선 해치) placeholder.
  - 숨김 보존(display:none): UNIT_ETC_AMT(기타), btnUnitHeatAmt·UNIT_HEAT_AUTO_AMT_html(열처리 자동계산 보조), 대상List(estimateCalculateMasterGrid·estimateDetailListHtml·UNIT_QTY_TOTAL_html·DTL_AMOUNT_TOTAL_html — 선택/이전다음/요약 로직 참조).
- **구현 방식(최종, 사용자 선택)**: "목업 복붙+갈고리 이식". 즉 `참고-PPTX원본이미지`(flex 목업, image6)의 마크업/CSS를 베이스로 가져와 image4로 각색하고, 그 위에 기능 갈고리(id/name/input/select+JSTL, `.checkUnitCalChanged`/`.estimate-input-group`)를 주입. 마크업은 목업 클래스(`.app-header`/`.col-left|center|right`/`table.info`/`table.grid`/`table.price`/`.acc-item`/`.drawing-frame`/`.footer-btns`) 사용. (reshape-in-place 1차본을 이 방식으로 재작성함)
- CSS 신규: `resource/asset/css/estimate_unit_price_calculate.css` = **목업 style.css를 .upc-root 스코프로 이식** + `.upc-hold`(보류 해치). JSP head에 링크. (스크립트 토글 클래스 estimate_input_change/estimate_yellow는 기존 인라인 <style> 유지.)
- **CSS 클래스 충돌 사고+해결(중요 교훈)**: 1차로 목업의 **범용 클래스명**(info/grid/price/blue/lbl/val/arrow/hold…)을 그대로 썼더니, 이 화면에 로드되는 **전역 스타일시트 25+개**(suite/common/layout/app/style.css 등)가 같은 이름을 다른 색·아이콘으로 정의해 **충돌**(헤더가 의도한 #2f7d5f가 아닌 #00c8a1 청록, .lbl 투명, .arrow가 깨진 아이콘 등). computed style 측정으로 확인 후, **모든 시각 클래스에 고유 접두사 `upc-` 부여**(`.upc-info/.upc-grid/.upc-price/.upc-blue/.upc-lbl/.upc-val/.upc-spec/.upc-hold/.upc-acc-*/.upc-app-header/.upc-col-*/.upc-sec-title/.upc-arrow` 등)해 격리 → 색·아이콘 정상화 검증(헤더 #2f7d5f, blue #d6e6f4, orange #c8641e, ▼ 정상). 기능/앱 클래스(td_input·td_select·estimate-input-group·autocalc_badge·defaultBtn·canvas-div·zoomOutBtn·d-flex)는 유지. **교훈: 전역 CSS가 깔린 화면에 목업 이식 시 범용 클래스명은 반드시 네임스페이스(접두사) 처리.**
### 제약/주의
- **스크립트 변경 금지** 때문에 동적 표시에 스크립트가 필요한 요소(헤더 페이저 n/total, 헤더 도면번호 박스)는 placeholder(보류)로 둠. 와이어링하려면 setEstimateRowSelect 등에 표시 라인 추가 필요(추후 합의).
- 우측 컬럼이 높이 빠듯해 하단 버튼이 견적/공급가 비고행과 근접/겹쳐 보일 수 있음 → 퍼블리셔 CSS 마감 항목(견적/공급가에 비고행 추가분).
### 검증
- 스크립트 참조 핵심 ID 45개 전부 마크업 1개씩, 중복 0, 태그 균형(div 47/47·table 7/7·form 1/1), 스크립트 영역 diff 0(불변). (가공비 상세팝업/일반·특수가공 관련 스크립트 참조 ID는 원본 견적 페이지에도 없던 것 → 그대로 부재, 회귀 아님.)
- 실화면 렌더: 재시작 후 로그인 → `/estimateUnitPriceCalculate` 1920×1080 캡처. image4 레이아웃대로 표시, 보류 해치 구분, 소재/표면 select 렌더, Jasper/500 에러 없음. (scratchpad/verify_est.py)
### order 페이지(수주)
- [2026-06-26] 단가입력/견적공급가 재구성분 그대로 유지(원복 보류 — 다른 세션 동시작업 가능성, 사용자 지시).
### 관련 파일
- `.../views/common/estimate_unit_price_calculate.jsp`(head CSS 링크 + 본문 전면 재구성, 스크립트 미변경)
- `.../resource/asset/css/estimate_unit_price_calculate.css`(신규)

## [2026-06-26] 단가검토 팝업 — 단가입력/견적·공급가 목업 레이아웃 재구성 (%클라우드)
### 작업 목표
`order_unit_price_calculate.jsp`의 우측 **단가입력 / 견적·공급가** 영역을 참고 목업(`바탕화면\예시\단가검토\참고-PPTX원본이미지\index.html`) 구조로 재구성. **스크립트(인라인 JS) 미변경**, 기존 ID/name/class 전부 보존, 매칭되는 기능만 연계, 신규 컴포넌트는 placeholder 보류. (사용자 질문에서 A안 선택)
### 완료
- **단가입력 재구성**(목업 구조): 규격/형태(전폭) → 수량·소재·표면 → 소재비/표면처리(자동계산+↳입력반영) → 소둔/연마·제관/열처리·용접/배송비·가공비/기타추가 → 단가합계/금액계 → 수량적용가/적용금액계. `table.rowStyle`+`order_blue/palegoldenrod/bg-palegray` 등 기존 의미클래스 유지(CSS 파일이 목업 팔레트로 재정의).
- **견적/공급가 재구성**: 단가/합계/**비고** 3열. 기존 NOTE 2종을 비고 칼럼에 매핑(견적가 비고=`UNIT_AMT_NOTE`, 공급가 비고=`NOTE`). 기존엔 단가입력에 있던 `UNIT_AMT_NOTE`를 여기로 이동.
- **신규(보류) placeholder**: 배송비·기타추가·수량적용가·적용금액계 = 자리만, 미연결. `.upc-hold`(사선 해치)로 시각 구분. CSS에 `.upc-root .upc-hold` 추가.
- **숨김 보존**(목업에 자리 없으나 스크립트가 합계/저장에 참조 → 제거 시 데이터 손실): `UNIT_ETC_AMT`(기타, unitAmtList 합계·저장 포함), `btnUnitHeatAmt`+`UNIT_HEAT_AUTO_AMT_html`(열처리 자동계산 보조). form 내 `display:none` div로 보존.
### 검증
- 스크립트 참조 ID 31개 전부 마크업 존재(자동 대조), 중복 ID 0, 태그 균형(div 92/92·table 10/10·form 1/1).
- **실화면 렌더 통과**: 재시작 후 로그인(Test-Automize `nav.login`) → `/orderUnitPriceCalculate` 1920×1080 캡처. 단가입력/견적·공급가 목업대로 표시, 보류 셀 해치 구분, 소재/표면 select 렌더, Jasper/500 에러 없음. (스크립트 `scratchpad/verify_upc.py`)
- **중요(재학습)**: JSP 구조 변경은 **서버 재시작 후에야 반영**됨(Jasper 캐시). 1차 검증 때 옛 JSP가 서빙돼 신규 마커 미검출 → 재시작 후 정상. 또한 bootRun을 **같은 로그 파일로 중복 기동하면 파일 잠금으로 재시작 bat이 exit 1**(무동작) — 새 로그 파일 사용 또는 기존 태스크 정지 후 기동할 것.
### 미완 / 다음 단계
- **보류 4종 와이어링 미정**: 배송비·기타추가·수량적용가·적용금액계는 백엔드/계산 스펙 확정 후 연결 필요. 특히 `기타추가`가 기존 `기타`(`UNIT_ETC_AMT`)와 동일 개념이면 hidden 보존분을 노출로 전환할지 사용자 확인 필요(현재는 별개로 간주해 hidden 보존).
- 좌측(기본정보·기록조회)·중앙(도면)·가공실적·외주이력은 이전 세션 마이그레이션 상태 그대로(이번 변경 범위 아님).
- 데이터 적재 상태(작지 선택/바코드)에서 합계·저장·이전/다음 동작 실데이터 검증은 미수행(빈/기본옵션 렌더만 확인).
### 관련 파일
- `.../views/common/order_unit_price_calculate.jsp`(단가입력·견적공급가 tbody 교체, hidden 보존 div 추가)
- `.../resource/asset/css/order_unit_price_calculate.css`(`.upc-hold` 추가)

## [2026-06-25] 단가검토 팝업 디자인 교체 (%클라우드, PPTX image6) — grill-me 합의 후 B방식
### 작업 목표
견적작성 > 단가검토 새 창 팝업(`/orderUnitPriceCalculate` → `common/order_unit_price_calculate.jsp`)을 PPTX 목업(`바탕화면\예시\단가검토\참고-PPTX원본이미지\index.html`) 디자인으로 교체. CSS **별도 파일**, 기록조회는 **ParamQuery Grid(형태만)**.
### 방향 전환 (중요 — 1차 오해)
- 1차: "나머지 컴포넌트는 기존 테이블 형태 유지"를 옛 외형 유지로 오해 → 레이아웃만 옮기고 화면은 옛날 그대로. 사용자 "전혀 아니잖아" 반려.
- **grill-me 스킬 도입 후 `/grilling`으로 합의**: 외관·레이아웃은 목업(B), 단 저장/계산 기능 필드는 삭제 안 함(보완), 죽은/숨겨진 UI는 미터치.
### 완료 (모두 %클라우드 파일, 미커밋 — 커밋은 사용자 몫)
- **신규 CSS(별도, 전면개정)**: `.../resource/asset/css/order_unit_price_calculate.css` — 목업 팔레트. **`.upc-root` 스코프**로 기존 의미클래스 재정의(`order_green→초록 라벨`, `order_blue/palegoldenrod→연파랑`, `bg-palegray→연회색`, `order_darkgrey→슬레이트`, `table.rowStyle→그리드 보더`) + 헤더바·3단·도면 프레임·아코디언·버튼. JSP 인라인 `<style>` !important 색상은 특이도(`.upc-root .x`)+!important로 상회. **퍼블리셔는 이 파일만 마감.**
- **JSP 마크업 최소 변경**(기능 ID/구조 보존, 시각은 CSS 담당):
  - 최상위 컨테이너에 `upc-root`, 제목 "단가검토"→**"단가 상세검토"**.
  - 헤더바: 페이저(◀ n/total ▶, `btnPrevOrderData/Next`를 footer→헤더 이동)+작업지시번호 박스(`upcWoBox`)+바코드+유사형태버튼.
  - 좌측: `대상 List` 그리드 **제거**(품목 이동=헤더 페이저). `기본정보`(유지)+`기록조회 아코디언`(pqGrid 4개 `recEstGrid/recOrderGrid/recOutEstGrid/recOutOrderGrid`, **빈 shell**, 토글 최대2개 FIFO).
  - 중앙: 도면 캔버스(확대/이동) 유지 + 목업 프레임(`upc-drawing-frame`)+"Tab 키" 안내.
  - 3단 컬럼 `upc-col-left/center/right`(폭 360/auto/400px). 우측·footer·하단버튼 구조 유지(CSS로 외형).
  - `setOrderRowSelect`에 페이저/작지번호 갱신 + 스크립트 끝 pqGrid shell init + 아코디언 토글 추가. **나머지 JS 전부 보존.**
### 합의된 처리 원칙 (재작업 시 준수)
- 저장/계산 필드(예: 표면상세 `SURFACE_TREAT_DETAIL`)는 목업에 안 보여도 **삭제 금지**(DB 저장 스펙 깨짐 방지). 현재 단가입력 구조 그대로 둠.
- 목업에만 있고 backing 없는 것(배송비·수량적용가·적용금액계·기록조회 그리드)은 **형태만**(placeholder), 동작/저장 없음 — 추후 확정.
- **죽은 UI 미터치**: `.right_popup`(가공비 슬라이드 팝업)은 `display:none`+오프스크린+트리거(`#processingCostBtn`) 버튼이 마크업에 없어 **현재 열 수 없는 죽은 UI** → 그대로 둠.
### 검증
- `gradlew compileJava` OK. 구조 OK(div 93/93·form 1/1, upc-root·col-left/center/right·제목·도면프레임 적용, canvas 보존).
- **미실시: 런타임 실화면 렌더 검증**(JSP 런타임 컴파일 + 견적작성 controlDetailSeqList 필요). 1차 오해 재발 방지 위해 **실화면을 목업과 직접 대조 필수**.
- 제거된 `대상 List` 관련 JS(`#orderDetailListHtml` 등)는 DOM 없는 무해 no-op로 잔존.
### 관련 파일
- `.../WEB-INF/views/common/order_unit_price_calculate.jsp`(수정), `.../resource/asset/css/order_unit_price_calculate.css`(신설/전면개정).
- 스킬 도입: `&하네스\.claude\skills\grill-me\SKILL.md`, `grilling\SKILL.md`(mattpocock/skills 원본).

## [2026-06-25] 노션 작업일지 자동화 3개 요구 반영 (daily_worklog.py)
### 작업 목표
사용자 추가 요구 3건을 `&하네스\scripts\daily_worklog.py`(tracker 방식)에 반영:
1. 다일(여러 날) 작업은 매일 새로 쓰지 말고 **최초 행에 이어쓰기**, 완료되면 상태='완료'로.
2. 행 이름에 날짜 넣지 말 것.
3. "초등학생 일기 같다"는 어투 제거 → 보고서체로.
### 설계 반려→재설계 (중요)
- 1차 구현은 **제목 문자열 동일성**으로 다일 작업을 매칭했음. 사용자가 반려: claude가 매일 짓는 제목은 흔들리고 '버그 수정'같은 일반 제목은 무관한 작업끼리 병합되는 리스크가 있어, 작업 정체성을 제목에 맡기면 안 됨. "작업 단위 맥락"과 HANDOFF 히스토리로 시작~완료를 감지해야 함.
- → **작업 정체성 원장(ledger) 기반으로 재설계**.
### 완료 (모두 &하네스 파일, 미커밋 — 커밋은 사용자 몫)
- **요구2 — 날짜 제거**: tracker 행 제목 `YYYY-MM-DD 작업명` → `작업명`.
- **요구1 — 다일 이어쓰기(원장 방식)**:
  - **원장 `&하네스\logs\worklog_tasks.json`** 신설: `{tasks:[{id:"t-0001",title,page_id,status,summary,started,last_updated,days[]}],next_seq}`. 함수 `load_ledger/save_ledger/open_tasks/format_open_tasks`. 매칭은 **제목이 아니라 영구 id↔Notion page_id**.
  - **이어짐 판정**: 실행 시 원장의 열린(상태!=완료) 작업 목록 + `HANDOFF.md` 전문(상한 24000자)을 프롬프트(`{open_tasks}`,`{handoff}`)로 주입. claude가 각 작업에 `task_ref`(열린 id 또는 'new')를 붙여 **맥락+HANDOFF로** 연속 여부 판정(제목 글자 아님).
  - **세션 경계 단서 + 병합**: `collect_sessions`가 세션(파일)마다 `===== 세션 N (id, 메시지수) =====` 헤더 부여(경계 보존, 기존엔 한 덩어리). 프롬프트가 '한 세션≈한 작업'을 분할 단서로 쓰되, 같은 작업을 여러 세션에서 시도한 경우 하루 작업 리스트업 후 **하나의 task로 병합**(세션마다 따로 X)하도록 지시. 검증: 2026-06-24 세션 7개 경계 정상 추출.
  - **루프**: `by_id`=원장 전체(완료 포함). `task_ref`가 원장 id(완료 포함)이고 `page_exists`면 → `_append_all`로 `[divider+H2 "📅 날짜(요일) 진행분"+작업블록]` 추가 + `update_tracker_row`(상태·제목·설명, 끝나면 '완료') + 원장 days/status 갱신. 멱등: 이어쓰기는 `date in days` 스킵, **신규는 '오늘 시작한 동일 제목' 원장 항목 있으면 스킵**(날짜내 백스톱). 'new'/원장에 없음/행 소실이면 `create_tracker_item`(이제 `(url,page_id)` 반환)으로 새 행 + 원장 `t-NNNN` 등록.
  - 제거된 함수: `find_tracker_row`, `list_inprogress_titles`, `update_tracker_status`(→`update_tracker_row`로 통합). 신설: `_append_all`, `page_exists`, `update_tracker_row`.
- **요구3 — 보고서체**: PROMPT_TMPL "너는 일지를 쓴다"→"업무 보고서를 쓴다" + 문체 규칙(1인칭 감상·자기평가·구어체 금지, 개조식/평서형, '초등학생 일기 어투 금지' 명시).
- env(token/tracker) 읽기 + 원장 로드를 build_data 앞으로 이동(open_tasks/handoff 주입 위해).
### 검증
- 스텁 시뮬레이션 ALL PASS + **2026-06-25 라이브 실주행 완료**.
### 라이브 재생성 + 컬럼 정리 (2026-06-25, 사용자 승인)
- **구형 행 정리**: 트래커의 구형 작업일지 행 20개(`YYYY-MM-DD 제목`, 6/22~24)를 아카이브(휴지통, 복구가능). 사용자 승인 후 실행.
- **6/22→6/23→6/24 순서 라이브 재생성**: 원장(`logs/worklog_tasks.json`) 누적, 같은 작업 날짜별 이어쓰기·완료전환 정상. 6/23 1차 실패(claude 300초 초과) → `run_claude` 타임아웃 300→**600**으로 상향 후 성공.
- **스케줄러 동시 실행 관측**: 17:30 `DailyWorklog`가 자동 발화해 06-25분을 같은 원장으로 이어붙임(t-0008완료·t-0002/7/10 append + 신규 t-0011~13). 자동 세션에서도 신로직 정상 확인.
- **컬럼 정리(사용자 승인)**: '작업 트래커'는 Notion '작업(Tasks)' 타입 컬렉션 → 일부 속성 삭제 불가. 삭제: 기한경과·노력수준·우선순위·파일첨부. 삭제불가(시스템필수): 담당자(빈 채 잔존). 재활용: 마감일→**작업 기간**(범위), 작업유형→**태그**. 스크립트가 `_date_prop`/`_tags_prop`로 자동 채움, 원장에 `tags` 필드 추가(합집합 누적). 기존 13행 작업기간·태그 백필 완료(4일치 JSON에서 태그 수집, task_ref·제목 매칭).
- 최종: 13행 모두 작업기간(다일 범위)·태그 표시. DB 컬럼=작업이름/상태/설명/작업기간/태그/담당자(잔존)/업데이트시간.
### 주의
- `_append_blocks`(생성직후 blocks[100:])와 `_append_all`(전체) 혼동 주의.
- 원장이 노션과 어긋날 때(수동 삭제) `page_exists`로 감지해 새 작업 폴백.
- 레거시 모드(`--style page|db|both`)는 미사용이라 손대지 않음(제목에 날짜 잔존).
### 관련 파일
- `&하네스\scripts\daily_worklog.py`(수정), `&하네스\logs\worklog_tasks.json`(원장, tags 포함), `logs/worklog_2026-06-2[2-5].json`, 메모리 `project_notion_worklog_automation.md`(갱신).

## [2026-06-25] 하네스 규칙 신선도 합의안(M1·M2·P1·P2) 적용 완료
### 작업 목표
SESSION_DIALOGUE.md 합의안("로드된 규칙 스냅샷=최신이라 단정→원본 미대조" 반복실패 차단)을 실제 적용.
### 완료 (모두 &하네스 파일, 미커밋 — 커밋은 사용자 몫)
- **M1 (대화형 세션):** `.claude/hooks/context_freshness_gate.py` 신설 + `.claude/settings.json`에 UserPromptSubmit 훅 등록. CLAUDE.md·MEMORY.md의 sha256 해시가 세션 첫 관측 이후 바뀌면 프롬프트 제출 시 "원본 Read 재대조" 지시를 컨텍스트 주입. 세션 첫 프롬프트는 baseline만 저장(무출력). 상태는 temp/tomes_ctx_fresh_<session_id>.json(세션별 파일, 경쟁 회피). 시나리오 테스트 PASS(첫=무출력/내용변경=알림/무변경=무출력). mtime 아닌 내용해시라 touch는 알림 안 냄(의도).
- **M2 (하네스 자동 세션):** `scripts/execute.py` — guardrails를 step·재시도마다 신선도 검사 후 재로딩. `_guardrails_signature()`(CLAUDE.md+docs mtime_ns)/`_read_guardrails()`/`_load_guardrails()`(캐시) 분리, `__init__`에 캐시 필드, `_execute_single_step` 루프 첫줄에서 재로딩. 기존엔 run당 1회만 로드돼 mid-run 편집이 후속 step에 stale했음. py_compile PASS.
- **P1:** CLAUDE.md 개발 프로세스(104줄 "단정 금지" 뒤)에 "로드된 컨텍스트는 stale·일부일 수 있다…원본 Read 재대조" 1줄.
- **P2:** CLAUDE.md 지적사항 회고 검증정의(핵심 문단)에 "그 '기준'이 최신인지부터 확인(시작 스냅샷 신뢰 금지)" 반줄.
### 주의 / 사고 보고
- **사고:** 훅 테스트 중 `git checkout -- CLAUDE.md`를 실행해 **미커밋이던 working-tree CLAUDE.md(143줄)를 통째로 HEAD(76줄)로 되돌림**. 이 대화 초반 Read로 확보한 전문에서 복원 + P1/P2 재적용. 정밀 대조로 손실 0 확인(143+2=145줄, 전 섹션 존재). 교훈: 미커밋 파일에 destructive git 명령 금지.
- **CLAUDE.md 취약점:** 커밋본은 76줄, working-tree는 143줄 분량이 미커밋 상태. 누군가 git checkout/restore하면 또 날아감 → 사용자 커밋 권장.
- 검증: settings.json valid JSON, 두 py py_compile PASS, 훅 시나리오 테스트 PASS. gradlew build는 무관(Java/Spring 변경 없음).
- UserPromptSubmit 훅은 죽은 세션엔 못 닿음(합의문 한계 그대로). 이미 진행 중인 step 세션도 다음 프롬프트/다음 step부터 적용.

## [2026-06-23] %클라우드 단가검토 팝업 2개 시각 전면 재작성 (PPT slide 3~7, image4/6)
### 작업 목표
사용자 지침(화면을 비우고 새로 / 틀 먼저 / 시각 먼저, 기능은 후속)에 따라 **단가검토 팝업 2개**를 PPT 목업대로 재작성:
- [견적작성]>[단가검토] = `estimate_unit_price_calculate.jsp` (제목 '상세 견적 검토', image4)
- [수주관리]>[단가검토] = `order_unit_price_calculate.jsp` (제목 '단가 상세검토', image6/7)
두 팝업 UI는 동일(제목·식별자만 다름: 견적=도면번호 / 수주=작업지시번호). **유사형태 기록조회(similar_record/drawing-same_archive)는 대상 아님** — 초반 오인해 손댔던 similar_record.jsp는 원복함.
### 완료 (시각 골격) — 둘 다 미커밋(사용자 몫), 브랜치 feature_caching_2606
- 목표 레이아웃: 헤더(제목 + 식별자칩 + 유사형태기록조회 버튼) / 좌 w_20 = 기본정보 + 기록조회(동일 도면번호, 견적기록·발주기록 아코디언) / 중 w_55 = 도면 View(+우상단 BNG 공정계산값 3D 썸네일 + Tab 힌트) / 우 w_25 = 가공실적·외주이력·단가입력·견적/공급가 + 하단 이전/다음/닫기/저장/저장다음.
- **기능 보존 방식**: head·`<script>`·form·hidden·AJAX·queryId 전부 그대로 두고, 본문 마크업만 교체. 기존 기능 ID 블록(기본정보표/기록조회 아코디언/도면 canvas/우측 전체)은 원본에서 그대로 슬라이스해 재배치 → ID 누락 0 (견적 53/53, 수주 82/82). div 균형 OK. 수주의 숨김 가공요건 슬라이드패널(right_popup)도 보존.
- 이전 세션 대비 개선: 좌측 w_15→w_20으로 넓혀 '기본정보/기록조회' 라벨 겹침 해소, 헤더에 식별자칩 추가, 도면 3D 썸네일 추가.
- **2차 디테일 패스(색·표 구성, image4/6 픽셀 추출)**: 목업 팔레트 적용 — 초록 `#187854`(기본정보 라벨·가공실적/외주이력 헤더, .mk_green), 연파랑 `#a8ccf0`(단가입력 수량/소재/표면/단가합계/금액계 헤더·견적공급가 헤더, .mk_blue), 노랑 `#f0e4c0`(단가입력 소재비·표면처리·소둔·제관·용접·가공비·연마·열처리·배송비·기타추가, .mk_yellow), 회색(기록조회 아코디언/표헤더, .mk_grayhdr/.mk_acc). 기본정보 행을 목업 구성(등록일자/품명/규격/소재종류/표면처리/형태수량/기타/접수번호 등)으로 재배치. 단가입력을 목업 구조(소재비·표면처리 자동계산+↳입력, 배송비·기타추가·단가합계·수량적용가·적용금액계)로 재구성.
- 재작성 스크립트: scratchpad/rebuild_est2.py, rebuild_order2.py. 검증샷: scratchpad/est2.png, order2.png. ID 보존 견적53/수주82 누락0, div 균형 OK.
- 신규 미바인딩(후속 와이어링 필요): 기본정보 신규행(등록일자/규격/소재종류/표면처리/형태수량/기타), 단가입력 배송비·수량적용가·적용금액계. (데이터/JS 연결은 후속)
- **앱 재기동 완료**(2026-06-23 16:29, 8081 local). 사용자가 두 팝업 실화면 확인 단계.
- **3차 패스(사용자 리뷰 반영, rebuild_est3.py/rebuild_order3.py)**: ①헤더에 이전/다음+카운터(`estRecordCounter`/`orderRecordCounter`, 미바인딩)+식별자필드(견적 도면번호=DRAWING_NUM_html / 수주 작업지시번호=CONTROL_NUM_html을 헤더로 이동, 기본정보쪽은 플레이스홀더)+바코드(수주) 추가. ②`shadow` 카드+여백 제거 → `.mk_frame` 테두리 박스 1개에 헤더(border-bottom)와 3컬럼(border-right)을 붙여 꽉 채움. ③하단 버튼은 닫기/저장/저장다음만(이전/다음은 헤더로 이동). ④BNG 3D 썸네일 제거(용도 불명). 견적 53/53·수주 82/82 ID 보존, div 균형, 가공요건 슬라이드(right_popup) 보존.
- **주의(버그 교훈)**: head 경계를 라인번호 하드코딩(L[:56])하면 이전 패스의 <style> 증가로 `</head><body><form><hidden>`가 잘려나감. → head 경계는 body div(`w_100 h_100 p-4/3`) 위치로 동적 계산할 것. (est3에서 1회 깨졌다가 누락블록 삽입으로 복구함)
- 재기동 2회차 완료(2026-06-23 16:58, 8081). #4(표 값)는 실데이터/플레이스홀더 이슈로 코드 무수정(특정 셀 오값 신고 시 대응).
- **4차 패스(리뷰 2차)**: ①수주 기본정보를 수주 목업 image6 필드로 교체(등록일자/작업지시번호/도면번호/품명/고객사/프로젝트/모듈명/규격/소재종류/표면처리/형태수량/기타/접수번호 — 견적과 거의 동일·작업지시번호만 다름, 사용자가 '목업 그대로' 선택). 수주 고유 ID(CONTROL_STATUS_DT/CONTROL_PART_QTY_INFO/PART_STATUS/PREV_UNIT_FINAL_AMT_html)는 미표시 div로 보존. ②기록조회 아코디언 2개→4개(견적기록/발주기록/외주견적기록/외주발주기록, 뒤 2개는 미바인딩 플레이스홀더 display:none·신규 id sameDrawingOut(Est/Order)Cnt/Body/ListHtml) — 견적·수주 둘 다. ③헤더 식별자 칸(.mk_field) min-width→width:230px 고정(이전엔 빈 채로 늘어나 이상해 보임). 견적 47/47·수주 72/72 div 균형, 수주 ID 0/82 누락. 재기동 3회차(2026-06-23 17:22, 8081).
### 검증
- 정적 렌더 하니스 `scratchpad/render_check.py <shot.png> <common\xxx.jsp>` (본문 추출→JSP/JSTL·script 제거→header.jsp css 링크→http.server:8099+playwright 1920x1080). 결과 `scratchpad/new_est.png`, `scratchpad/new_order.png` — 목업 image4/image6과 헤더·좌·중·우 일치 확인. 임시 webapp/_sr_preview.html 삭제 완료.
- **한계**: 하니스는 script를 제거해 렌더하므로 도면 canvas는 빈칸이고 **런타임 동작은 미검증**. 모든 기능 ID·script 보존했으나 실앱 확인 필요.
### 미완 / 다음 단계
- **실앱 검증 필수**: JSP 구조 변경은 앱 재시작 후 반영(이전 세션 관찰). 재시작 후 두 팝업 열어 데이터 로딩·도면·단가입력·저장·이전/다음 정상 동작 확인. (%테스트 Playwright 스크립트 scratchpad/show_order_danga2.py / est 재현 참고)
- 헤더 식별자칩 값 바인딩(DRAWING_NUM_TITLE/CONTROL_NUM_TITLE), 도면 3D 썸네일(drawing3dThumb) 소스 연결.

## [2026-06-23] %클라우드 단가검토 -> 상세검토 개편 (PPT '단가검토 및 유사형상_260622')
### 작업 목표
견적작성>단가검토(견적) 팝업과 수주관리>단가검토 팝업을 PPT의 '상세검토' 화면으로 개편. 디자인 디테일은 퍼블리셔 담당(화면 골격·기능 위주). 기존 백엔드 재사용 결정. 유사형태 기록조회(별도 팝업)는 범위 제외.
### 환경/브랜치
- %클라우드 브랜치 `Danga_estimate`. **커밋 안 함**(사용자 몫).
- 미커밋 WIP(SecurityConfig/WebContextConfig)는 내 것 아님 — 건드리지 않음.
- **중요**: 재기동 중 `application-local.yml`(gitignore, 로컬 시크릿)이 워킹트리에 없어 부팅 실패 발견. 사용자 승인하에 git 이력(`6c37383^`)본을 복원함 -> src/main/resources/application-local.yml (원격 DB 121.165.20.66 대상, gitignore라 커밋 안 됨). 앱 8081 정상 기동.
- 재기동 방법: `shell/runDev.local.bat` 또는 `gradlew bootRun --args="--spring.profiles.active=local --server.port=8081"`. 매퍼 XML 변경은 재기동 필요(JSP/JS는 즉시).
### 완료 + 실화면 검증(%테스트 Playwright)
- 이름변경: 견적작성 버튼 '단가 검토'->'상세 견적 검토', 견적팝업 제목->'상세 견적 검토', 수주팝업 제목->'단가 상세검토'.
- Phase 1(수주 팝업 `order_unit_price_calculate.jsp`): 좌측에 **기록조회(동일 도면번호) 아코디언**(견적기록/발주기록) 신설. `drawingSameArchive.selectEstArchiveDataListV1`/`selectBasicArchiveDataListV1` 재사용 + 두 쿼리에 **조건부 DRAWING_NUM 필터**(`v1/orderSameArchive.xml`, queryId 불변·기존 호출자 무해) 추가. `fnGetSameDrawingArchive(data)`가 행 로딩 시 호출.
- 실측: 수주관리>단가검토 팝업 열어 도면 '유사형상테스트' -> 견적기록 10/발주기록 10 정상 표시. (캡처: scratchpad/danga_popup_full.png, danga_popup_accordion.png)
### Phase 2 + 섹션 재구성 완료 + 실화면 검증 (2026-06-23)
PPT 섹션 구성에 맞춰 두 팝업을 재구성(픽셀 디자인은 퍼블리셔). 목표 구조: **좌측 = 기본정보 + 기록조회(동일 도면번호) 아코디언 / 중앙 = 도면 view / 우측 = 가공실적 + 외주이력 + 단가입력 + 견적/공급가.**
- **대상 List 제거**(두 팝업 모두 — PPT에 없음). 관련 JS(masterGrid/detailListHtml/summary/화살표키)는 요소 없으면 no-op, 이전/다음 버튼은 datasource 기반이라 정상.
- 견적 팝업: 기본정보를 우측→좌측 상단으로 이동(중복 id 제거), 우측에 가공실적·외주이력 **영역(빈 테이블 셸) 추가**(데이터 연결은 Phase 3). 좌측 기본정보 42%/기록조회 58%.
- 수주 팝업: 우측은 원래 일치. 좌측에서 대상List 제거, 기본정보 42%/기록조회 58%.
- 실측(재시작 후): 수주(도면 유사형상테스트) 견적10/발주10, 견적(EST_SEQ 12161) 견적10/발주12. 캡처: scratchpad/danga_popup_full.png, est_danga_popup_full.png.
- **중요(JSP 캐시)**: local 설정이 development:true/modificationTestInterval:0이라도 **실측상 JSP 구조 변경이 재컴파일로 즉시 반영되지 않음 → JSP 변경 후엔 앱 재시작 필요**. (매퍼/JSP 변경 모두 재시작 권장)
### 미완 (다음 단계)
- Phase 3: 기록조회 행 클릭 시 우측 데이터(선택 기록의 가공실적·외주이력·단가) View 전용 로딩 + Tab 원복(PPT 슬라이드 5·7). 견적 팝업의 가공실적·외주이력 셸에 이때 데이터 연결(drawingSameArchive.selectMctworkArchiveDataList/selectArchiveNormalProcessList/외주 등 재사용 후보).
- 레이아웃: 좌측 w_15 컬럼이 좁아 아코디언 cramped — 퍼블리셔 정리 예정.
### 검증 스크립트
- scratchpad/show_order_danga2.py (qa_agent.tools 재사용, headed). 핵심: 로그인 후 BASE_URL 1회 재로드로 탭 활성화 안정화, 그리드 선택 대신 window.open+onLoadPage(cds) 재현.

## [2026-06-23] Notion 작업일지 자동화 -> '작업 트래커' DB 행으로 전환
### 작업 목표
매일 17:30 자동 생성되던 작업일지를 별도 페이지가 아니라 기존 노션 '작업 트래커' DB에 행으로 쌓되, 본문 작성 형식은 그대로 유지.
### 완료
- '작업 트래커'는 노션 기본 태스크 트래커 DB(id 387e556f-7f1c-80df-9abe-cb060fa6e2d8). 속성: 작업 이름(title)/상태(status: 시작 전·진행 중·완료)/설명(rich_text)/마감일(date)/작업 유형·우선순위·노력 수준/기한 경과(formula).
- `기한 경과` = if(마감일<now(), "Past Due", "") — 상태 무관·과거 마감일이면 무조건 Past Due. -> 작업일지 행은 **마감일을 비운다**(날짜는 제목·본문에).
- daily_worklog.py 수정: `--style tracker`(신규 기본값) 추가. User 환경변수 `NOTION_TRACKER_DB_ID` 등록(setx, 스케줄러 상속).
- **작업 단위 분할(최종)**: 하루=1행이 아니라 **작업(task)마다 1행**. claude 프롬프트가 `tasks[]` 출력 → 작업당 행 1개, 본문엔 그 작업의 기술·배운점·이슈·다음할일. 행 제목 = `YYYY-MM-DD 작업명`(중복방지 키). 상태는 작업별 claude 판정('완료'/'진행 중'), `--status`로 전 행 강제(수동 우선). 동일 제목 스킵.
- 테스트: 어제(6-22)로 실행 → **작업 7건 = 7행 생성 성공**(완료 3/진행 중 4). 본문 작업별 분리 확인.
### 미완·주의
- 트래커에 남은 **날짜단위 옛 테스트 행 1건**(제목 "작업일지 2026-06-22 (월)", https://app.notion.com/p/2026-06-22-388e556f7f1c81efb266fd1bbe133f8c )은 구 방식 산물 — 사용자가 삭제 가능.
- 기존 page/db 방식 코드는 남아있으나 기본은 tracker. parent 페이지의 옛 일지 페이지도 정리 가능.
- daily_worklog.py는 매 실행마다 logs/worklog_<date>.json 을 덮어씀. `--no-claude`로 재실행하면 빈 데이터로 클로버됨(주의).


## [2026-06-22] 메인 로드 불필요 엔드포인트 비활성화(팝업 선조회 제거) + 속도 측정 (미커밋, bottom.js)
### 작업 목표
사용자 요청: 메인화면 로드 시점에 남아있는 불필요 엔드포인트 확인 -> 비활성화 -> 속도 비교(사용자 육안 + 내 측정).
### 발견(실측, bo.log + headless Playwright)
- 매 메인 로드(로그인/새로고침)마다 **닫혀있는 팝업의 그리드/셀렉트박스가 데이터를 선조회**: `inspection.selectInspectionPopInfoList1` `selectInspectionPopInfoList2` `selectCommItemDetailInfoGrid1`(검사관리 팝업 그리드 3) + `material.selectCommonWarehouseManageList`(공통 창고 팝업 그리드) + `inspection.selectRandRange`(Rand범위 셀렉트박스). 5종.
- 원인: bottom.js가 page ready에 이 팝업 그리드들을 `location:"remote"`로 init -> ParamQuery는 `_create` 시 remote면 무조건 fetch(pqgrid.dev.js:10951 `if(location==="remote") that.refresh()`). 팝업 실제 open 시 open 핸들러가 다시 조회하므로 init 조회는 **순수 중복**.
- (별개) `dataSource.getBusinessCompanyList/getOutsourceProcessCompanyList`는 로그인 시 1회만(새로고침엔 안 뜸), bottom.js 밖이라 이번 범위 제외.
### 수정(미커밋, 1파일 bottom.js, LOADOPT 마커로 7곳 표시)
- 검사 팝업 그리드 3 + 창고 그리드 init: `location:"remote"` -> `location:"local", data:[]` (init 자동조회 차단).
- 검사 팝업 open 핸들러(show.bs.modal): 각 그리드 refresh 직전 `dataModel.location='remote'` 전환 추가.
- 창고 open(fnCommonWarehouse else분기): `location='remote'`+postData 세팅 후 refreshDataAndView.
- randRange 셀렉트박스: 로드 시 top-level `randRangeSelBox()` 호출 제거 -> rand_range_popup show.bs.modal로 이동(open 시 채움).
### 측정 결과 (headless reload x5 중앙값)
- **엔드포인트: 5종 -> 0종**(BEFORE/AFTER 각 5회 재현, 대시보드 6종은 정상 유지=문법/동작 OK).
- **wall-clock: ~10275ms -> ~10211ms(노이즈 내 변동 없음)**. 이유: 메인 로드 병목은 AJAX가 아니라 **정적 리소스 152건**(이미지/JS, dev bootRun에서 각 ~5초 직렬). 제거한 5종은 서버 ~10-60ms로 빠르고 타 요청과 병렬이라 임계경로 아님. (06-19 캐싱 결론과 동일 맥락: 체감속도와 무관, 서버/DB 부하 절감이 실익.)
### 미완·주의
- **사용자 육안 검증 필요(★)**: ①검사관리 팝업 ②공통 창고 팝업 ③Rand범위 팝업 — open 시 그리드/셀렉트박스가 정상 채워지는지. (open 핸들러 remote 전환이 핵심, 깨지면 빈 그리드)
- bottom.js는 전 페이지 공용 -> 이 5종 절감은 모든 화면 로드에 적용됨(메인 한정 아님).
- %클라우드 미커밋(bottom.js 1파일). 커밋은 사용자 몫. bootRun이라 새로고침으로 즉시 반영(재빌드 불필요).
- 측정 스크립트: scratchpad/measure_main.py, slowreq.py.


## [2026-06-19] 견적 표준계산 관리 표면처리 종류(SURFACE_TREAT, D03) 부분 마이그레이션 완료
### 작업 목표
같은 페이지 surface_treatment_cost_grid의 표면처리 종류(SURFACE_TREAT) 코드원문 노출 해결. (표면처리 색상=SURFACE_TREAT_DETAIL=D04는 사용자 지시로 보류)
### 코드그룹 확정
- JS(estimate-standard-calculation-manage.js): 표면처리 종류=**D03**(1207 editor/1215 render), 표면처리 색상=**D04**(1238/1252). → 종류만 처리, 색상(D04) 미처리.
### 완료 (TBL_CALC_SURFACE.SURFACE_TREAT만 UPDATE, 비운영 DB)
- **정의서 D03 구간 신뢰불가 발견**: 정의서는 D03R20(삼산화철피막)→PH0101이라 하나 실제 마스터 PH0101=인산염피막 / OX0101=삼산화철피막 (명칭 불일치=정의서 오류). → 정의서 코드 맹신 안 하고 **신 마스터 명칭+정의서 둘 다 일치하는 것만** 안전 이행.
- 이행(6행): D03R00→NA0101(표면처리없음), D03R21(도장)→PA0101, D03R22·D03R25(레이던트)→OX0201. (구 백업 명칭과 신 마스터 명칭 정확 일치 + 정의서가 동일명칭 정규코드 D03R15/16을 그 값으로 명시)
- 화면 PASS: S51R40(후처리>표면처리) 탭에서 도장/레이던트가 이름 표시 확인(스크린샷 scratchpad/surf_clean.png). 색상(D04)은 D04R% 코드 그대로(보류대로).
- before-image: scratchpad/surf_before_image.txt(23행). SQL: scratchpad/surf_migrate.sql. 매핑: scratchpad/d03_map.json.
### 미완·보류 (사용자 결정 필요 — 표면처리 종류 잔존 17행)
- **D03R20(삼산화철피막, 2행)**: 정의서=PH0101(인산염피막) ↔ 명칭=OX0101(삼산화철피막) **충돌**. 어느 코드로 할지 결정 필요. (명칭 기준이면 OX0101 권장)
- **D03R10 아노다이징(7행)**: 신체계는 색상별 AN 코드(AN0101 백색…22종)로 분화. 종류만으론 색상 미상 → **종류+색상 병합(보류된 D04/재설계 영역) 필요**. 단독 매핑 불가.
- **D03R18/R23/R26 도금(6행)**: 신체계 PL 세부유형(크롬/니켈/아연 도금 등)·CR/PO로 분화. 어느 도금인지 결정 필요.
- **D03R34(1행)·'8'(1행)**: 정의서·구백업(TBL_CODE_BAK) 모두 부재. 정체불명.
- NULL(3행): 빈값, 조치 불필요.
### 주의
- 표면처리 색상(SURFACE_TREAT_DETAIL=D04)은 그룹 폐지(마스터 0건)라 데이터로 불가, JS 재설계 필요(보류 유지).
- %클라우드 코드 무변경(DB만). 커밋은 사용자 몫.

## [2026-06-19] 견적 표준계산 관리 소재종류 DB 마이그레이션 실행 완료 (비운영 DB, 백업 사용자 보유)
### 작업 목표
견적 표준계산 관리 소재종류(MATERIAL_DETAIL) 코드 원문(CODE_CD) 노출 = 트랜잭션에 구코드(D01R%) 잔존 / 마스터는 신코드 전환됨으로 인한 매핑실패. 데이터 마이그레이션으로 해결 + 화면 테스트.
### 분기/브랜치 정리(확인 결과)
- %클라우드 현재 브랜치 `feature_caching_2606`. 통합커밋 `b0270a1`("캐싱 기능 통합…")에 ①재질>소재종류 REF_CD 필터(JS 499/1932 Etc) ②getUserList Redis 캐싱이 **모두 반영됨**(원본 a73d99a/55439f8는 Sun-Pro 단독이나 내용은 통합커밋에 포함). 문제2 누락 아님.
### 완료 (DB 마이그레이션 실행+커밋+검증, 사용자 무승인 진행 지시)
- 대상: **TBL_CALC_MATERIAL_NORMAL / TBL_CALC_MATERIAL_STANDARD 의 MATERIAL_DETAIL만**. 마스터(TBL_CODE/LANG/GROUP)·다른 테이블 무변경(reviewer 확인).
- 매핑출처: 정의서 `바탕화면\기준코드 관련\톰스클라우드_코드변경_최신.xlsx` 시트 `코드정의서_변화관리3.0` (D열=구 CODE_CD, H열=신 상세코드). D01 64행 추출 → `scratchpad/d01_map.json`.
- 실행결과(검증 완료): NORMAL 91행=신코드90+구코드1(D01R65), STANDARD 14행=전부 신코드. 총 100행 UPDATE. D01R65(NIDSOFT 1행)는 매핑불가로 제외. D01R18→CS0101(SS41=SS400 구JIS 동일재질, D01R17과 통합)로 처리(추론, 근거 충분).
- 화면 테스트 PASS: GNB 경유 로그인(test/SMD)→견적관리>견적 표준계산 관리. 일반소재비 87행·규격소재비 12행 전부 이름 표시(코드원문 0). 렌더함수 알고리즘 재현 + 스크린샷(scratchpad/screen_clean.png)으로 확인.
- before-image: `scratchpad/before_image.txt`(101행). exec SQL: `scratchpad/migrate.sql`(+COMMIT).
### 미완·다음 (사용자에게 별도 요청 예정)
- **D01R65(NIDSOFT NORMAL 1행, MATERIAL_TYPE=D02R30)**: 정의서·구백업(TBL_CODE_BAK) 모두 부재 → 매핑 불가로 미처리. 사용자 확인 필요(올바른 신코드 지정).
- 같은 구코드 잔재가 다른 테이블에도 있음(TBL_CALC_SURFACE의 SURFACE_TREAT=D03R%/SURFACE_TREAT_DETAIL=D04R%, TBL_ESTIMATE_DETAIL/ORDER/CONTROL 등의 MATERIAL_DETAIL). 이번 범위 외 — 필요 시 별도 요청.
- 표면처리 색상(D04 그룹 폐지, 마스터 0건)은 데이터로 불가, JS 재설계 필요(보류 — 사용자 D04 보류 지시).
### 주의
- 비운영 DB이며 사용자가 백업 보유. mysql 접속 `--ssl=0 -h121.165.20.66 -utomes -p'jmes!20191107' smd`.
- %클라우드 미커밋 없음(이번 작업은 DB만, 코드 무변경). 커밋은 사용자 몫.

## [2026-06-19] 견적 표준계산 관리 소재종류 수정 + 코드체계 전환(TBL_CODE_BAK->TBL_CODE) 분석 (재부팅 전 인수인계)

### 작업 목표
견적관리>견적 표준계산 관리 그리드의 소재종류(MATERIAL_DETAIL) 이슈 해결: ①재질 선택 무관하게 소재종류 전체 출력 ②CODE_NM이 아닌 CODE_CD 원문 노출. + 원인인 코드체계 전환 영향 분석 + PR 리뷰 MD 작성.

### 완료
- **JS 수정(미커밋, 2줄)** `Projects/Tomes-Cloud/src/main/webapp/resource/modules/pages/biz/estimate-standard-calculation-manage.js`:
  - 일반소재비(499줄, materialCostNormalColModel)·규격소재비(1932줄, materialCostStandardModel)의 소재종류 editor.options를 `fnGetCommCodeGridSelectBox('D01')` -> `fnGetCommCodeGridSelectBoxEtc('D01', rowData.MATERIAL_TYPE)`로 변경. 근거: D01(소재종류).REF_CD가 D02(재질) 1:1 참조. render(507/1940줄)는 표시변환용이라 전체목록 유지(무변경). 동작 패턴은 표면처리종류(1207줄)와 동일.
  - 헬퍼 정의: `resource/modules/attr/tabs/body-script.js` 506~539 (SelectBox=전체, SelectBoxEtc=REF_CD 필터).
- **코드체계 전환 분석 완료**: 정의서 `바탕화면\기준코드 관련\톰스클라우드_코드변경_최신.xlsx`(시트 코드정의서_변화관리3.0, ASIS=구 CODE_CD / TOBE=신 상세코드). 위치식(D01RXX/D03RXX/D04RXX) -> 의미식(AL0101/NA0101/AN0101). D02(재질) 코드 불변, D01 재명명(참조 동일), **D03+D04 -> D03 단일그룹 통합(D04 폐지, live DB 0행)**, S51/S56/S60 등 UI하드코딩. 메모리 `project_code_system_migration` 저장.
- **PR 리뷰 MD**: `바탕화면\PR리뷰\[06.19 요약].md` (마크다운 파이프 표 - **렌더링/미리보기에서만 정렬**됨. 문자표는 한글 ambiguous-width로 정렬 보장 불가라 파이프표로 결정). 메모리 `feedback_pr_review_md_format` 저장.

### 진행 중 · 미완 (★다음 세션 핵심)
- **소재종류 CODE_CD 노출의 근본원인 = 트랜잭션 데이터가 구코드(D01RXX) 잔존**. 마스터(TBL_CODE D01=AL0101식 78개)엔 D01R% 없음 -> render 매핑 실패 -> 코드 원문. (AL 4행만 신코드 AL0101~04라 정상). JS는 정상이며 **데이터 마이그레이션(UPDATE)이 해결책**.
- **마이그레이션 SQL 생성 완료(미실행)**: `scratchpad\migrate_material_detail.sql` (백업 CREATE + START TRANSACTION + UPDATE 50여건). 대상 **NORMAL 83행 + STANDARD 14행 = 97행, 50개 구코드**. 매핑 타깃 50개 전부 D01 마스터 존재 검증 완료(answer-reviewer 검증 통과). 매핑표: `scratchpad\d01_map.json`.
- **사용자 확인 대기(아직 실행 안 함)**: ①97행 마이그레이션 실행 여부 ②보류 2개 처리: **D01R18**(NORMAL 3행; 정의서 [삭제]/신코드 공란, 명칭 SS40 -> 추론: D01R17과 같은 SS40이라 CS0101 통합 추정) / **D01R65**(NORMAL 1행; 정의서에 아예 없음, 불명).

### 다음 단계
1. 사용자에게 위 ①② 확인받기. 확인되면 보류 2개 반영 후 SQL 실행(백업 -> UPDATE -> 검증 SELECT -> COMMIT). **운영 DB 변경이라 반드시 확인 후 실행.**
2. 실행 후 화면에서 두 그리드 소재종류가 이름으로 표시되는지 확인.
3. (별도 범위) 표면처리 그리드 재설계: 1238줄 폐지된 D04 참조 제거 + 1207줄 D03 재질필터(신구조 불일치, 일부 재질 빈목록) + 종류/색상 D03 단일구조 반영. SURFACE_TREAT/DETAIL도 구코드(D03R/D04R) 잔존.

### 블로커 · 주의
- **운영 DB 직접 UPDATE**: `smd`(121.165.20.66). 접속 `/e/Tool/mariaDB/bin/mysql --ssl=0 -h121.165.20.66 -utomes -p'jmes!20191107' smd` (**--ssl=0 필수**, 서버가 SSL 미지원). SQL에 백업테이블+트랜잭션 포함했으나 자의 실행 금지.
- 같은 구코드 잔재가 다른 테이블에도 있음(TBL_CALC_MATERIAL_SPEC/LOSS, TBL_ESTIMATE_DETAIL, TBL_ORDER, TBL_CONTROL_* 의 MATERIAL_DETAIL; TBL_CALC_SURFACE의 SURFACE_TREAT/DETAIL). 이번은 견적 표준계산 관리(NORMAL/STANDARD)만.
- 표면처리 색상 드롭다운은 D04 그룹 0행이라 항상 빔(데이터로 못 채움).
- %클라우드 미커밋(JS 2줄). 커밋은 사용자 몫.
- DB 컬럼 주의: TBL_CODE에 CODE_NM 컬럼 없음(약어는 ABBR_NM), 코드명은 TBL_CODE_LANG.CODE_NM.

### 관련 파일 · 경로
- 수정 JS: `Projects/Tomes-Cloud/.../pages/biz/estimate-standard-calculation-manage.js` (499, 1932 변경 / 1207·1238 표면처리 / 507·1940 render)
- 헬퍼: `.../attr/tabs/body-script.js` 506~539
- 정의서/영향범위: `바탕화면\기준코드 관련\톰스클라우드_코드변경_최신.xlsx`, `TBL_CODE1_영향범위.xlsx`
- PR MD: `바탕화면\PR리뷰\[06.19 요약].md`
- scratchpad: `migrate_material_detail.sql`, `d01_map.json`, `present_old.txt`, `d01_master.txt`
- 메모리(신규): `project_code_system_migration`, `feedback_pr_review_md_format`

## [2026-06-19] TBL_USER 표시용 목록(getUserList) Redis 캐싱 구현 (미커밋, 빌드 PASS)
- **범위 합의**: 사용자 요청 "TBL_USER 캐싱" → 보안/변경잦음 고려해 "표시용 드롭다운/목록만"으로 한정(로그인/인증/권한 제외). code-cache(selectSessionCodeList)와 동일 위임 패턴 재사용.
- **대상**: `dataSource.getUserList`(data_source.xml:6-13, `USER_ID/USER_NM`, `DEL_YN='N' AND SYSTEM_ID=#{LOGIN_SYSTEM_ID}`)만. main.jsp·estimate-list 등 다수 화면이 /json-list로 매 로드 직조회하던 것.
- **구현 3파일(%클라우드, 미커밋)**:
  1. `SystemService.java`(:35) — `getSessionUserList(String systemId)` 인터페이스 선언 추가.
  2. `SystemServiceImpl.java` — getSessionUserList `@Cacheable`(value `...:getSessionUserList`, key `#systemId`, cacheManager `everyHour`) 신설 + `updateUser()`에 `@CacheEvict`(동일 value, allEntries=true, everyHour) 추가 + `import CacheEvict`.
  3. `InnodaleServiceImpl.getList` — selectSessionCodeList 분기 다음에 `queryId=="dataSource.getUserList"` && systemId 있으면 getSessionUserList 위임(없으면 기존 DAO 경로).
- **무효화 범위 정정**: 계획의 CustomerServiceImpl는 제외함 — signup은 신규 SYSTEM_ID 전체 생성이라 해당 systemId 캐시가 애초 없음(무효화 실익 0). 일반 사용자 관리 경로 updateUser() 한 곳 + TTL(1h) 안전망으로 충분. updateAdminUser(관리자 등록)는 드물고 TTL로 정리되므로 보류(필요 시 추가 가능).
- **검증**: gradlew build -q PASS(경고는 기존 deprecated/unchecked). answer-reviewer 6항목 OK(캐시명 문자일치/everyHour 명시/위임분기/인터페이스 정합/key 충분/과잉무효화 없음).
- **실화면 end-to-end 검증 완료(2026-06-19, bo.log 실측)**: 현 가동서버는 bootRun(build/classes, 10:58 기동)으로 새 코드 반영됨(javap로 getSessionUserList 확인). 임시 Playwright 스크립트(scratchpad, test/1 로그인)로 측정:
  - **캐싱 PASS**: 메인 로드 시 getUserList DB 1회(11:16:56) 후 reload 2회(11:17:00/12)에서 DB 0건=Redis 적중. (대조: 캐시 안되는 selectSystemInfo는 같은구간 4건). 주의: 클라 메모리캐시 영향 배제 위해 reload(클라캐시 소멸)로 측정 — 서버 Redis 적중 확정.
  - **무효화 PASS**: test 사용자 정보를 원본 그대로 되돌려 /updateUser 저장(USER_PWD/R_USER_PWD 미포함 → 쿼리 if조건상 비번 무변경, before==after 홍길동/SMD/1022 확인). insertMasterUser 11:23:43 실행→@CacheEvict. 직전 reload DB 0건(적중)→evict 후 reload(11:23:55) DB 1건(미스 재조회). "updateUser→Redis clear→다음 로드 DB 최신" 전구간 증명.
  - **데이터 무손상**: 무변경 저장이라 DB 잔존 테스트데이터 없음. Redis엔 11:23:55 재캐시 존재(정상, TTL 1h).
- **캐싱 ON/OFF 메인로드 직접 비교(2026-06-19, 사용자 요청)**: InnodaleServiceImpl.getList 맨앞에 임시 우회(`if(true) return dao.getList`) 넣어 캐싱 OFF 빌드로 서버 재기동→measure_main.py(headless, reload 7회)로 ON/OFF 측정. 결과: 클라 전체 load 중앙값 ON 9208ms vs OFF 8043ms(노이즈로 OFF가 빠름=캐싱 무관), 변동폭 4~9초가 캐싱효과 압도. 서버 DB 절감은 캐싱대상 쿼리 로드당 ~34ms(getUserList 8 + selectSessionCodeList 26)뿐. **결론: 캐싱은 메인 새로고침 체감속도와 사실상 무관(서버 DB부하/동시성 보호 의미). 체감 "빨라짐"은 브라우저캐시/서버워밍업/착시 추정.** 측정 후 임시코드 원복 완료, 서버 캐싱ON으로 재기동(HTTP200 확인). 측정 중 서버 2회 재시작함.
- **주의**: %클라우드 미커밋(3파일). 커밋은 사용자 몫. PR(오늘 오전 작업 포함 예정)에 이 캐싱 + 조인버그(system.xml:238 KR->EN) 함께 보고 대상.

## [2026-06-18→19 정정] 이전 "미완"으로 적혔으나 실제 완료된 항목 (transcript 확인)
- **임시 테스트 데이터: 삭제 완료**(2026-06-18 16:55). D01TEST 코드/랭 + SMD/D01 그룹 타깃 DELETE로 공유 DB 원상복구 확인. (단 16:48 Redis 캐시엔 잠시 잔존 — admin 저장/TTL로 정리)
- **%클라우드 커밋: 완료**(2026-06-18, 사용자 직접). `7c647dd "브라우저 캐시 원복 및 로그 추적"` — logback(+21)/body-script.jsp(-4)/json-list-cache.js(-143)/body-script.js(-2). 추적 미커밋 0 클린. 아래 06-18 항목들의 "미커밋"은 이 커밋으로 해소됨.

## [2026-06-18] 캐시 무효화 end-to-end 실화면 검증 완료 + 별건 버그 발견
- **검증 완료(서버 Redis 캐시 + 무효화)**: bo.log 실측.
  - 캐싱: 메인 로드/새로고침에서 selectSessionCodeList가 Redis 적중(SQL 미실행) — 11:01 1회 실행 후 계속 적중.
  - 무효화: admin에서 SMD 선택+D01TEST 비고를 '클로드 최고'로 저장(updateCommonCodeAdmin→TBL_CODE, systemType=CODE) → InnodaleServiceImpl.modifyGrid가 Redis clear → 메인 재로드(16:48:06)에서 selectSessionCodeList **재실행**(Redis 미스→DB) → 결과에 D01TEST NOTE='클로드 최고' 반영 확인.
  - 결론: "기준코드(TBL_CODE) 변경 → modifyGrid 무효화 → 다음 로드 시 DB 최신 서빙" 전 구간 증명.
- **검증 위해 추가한 임시 DB 데이터(공유 smd DB, 미정리)**: TBL_CODE/TBL_CODE_LANG의 SMD/D01/D01TEST 3행 + TBL_CODE_GROUP의 SMD/D01 그룹 1행. (현재 NOTE='클로드 최고') → 검증 끝나면 삭제 예정. 삭제 후 Redis엔 잠시 잔존(다음 코드저장/TTL까지).
- **[PR 리뷰 보고 항목] selectSessionCodeList 조인 버그(미수정, 사용자 지시로 보류)**: sqlMaps/system.xml 238행 C 조인이 `C.LANG_CD='KR'` — CODE_NM_EN 자리인데 KR로 매칭돼 영문명에 한국어명이 들어감. 정상 형제 쿼리 selectCommonCodeListAdmin(2148행)은 `C.LANG_CD='EN'`. 추론: B조인 복붙 후 'KR'→'EN' 미수정. 대부분 코드의 KR=EN이라 미발견, KR≠EN일 때만 표면화. 수정안: 238행 'KR'→'EN'. **지금 수정 금지, PR 생성 시 함께 보고.**
- **데이터 모델 주의(검증 중 확인)**: 현재 운영 admin 화면(시스템 미선택)은 TBL_BASIC_CODE를 편집하나 런타임 캐시(selectSessionCodeList)는 TBL_CODE를 읽음 → 다른 테이블. TBL_BASIC_CODE→TBL_CODE 동기화는 시스템 신규등록 시 1회뿐(insertCommonCodeForSystem). 즉 현재 운영 편집은 런타임에 자동 반영 안 됨(별도 점검 필요할 수 있음).

## [2026-06-18] 클라 측 localStorage/TTL영속/BroadcastChannel 전부 원복 (방향 전환)
- **사용자 결정**: Redis(서버) 캐시만 유지하고, 이번 캐시 작업이 클라에 얹은 영속(sessionStorage->localStorage)+BroadcastChannel 수정을 전부 파기. 원래 있던 클라 메모리 캐시(ttlCache+TTL)는 유지(옵션 1).
- **방법**: %클라우드 3개 파일을 init 커밋(884505f)으로 git checkout 원복(이 캐시 코드는 이미 커밋돼 있었음). 되돌린 파일:
  1. resource/asset/js/json-list-cache.js -> 메모리 캐시만 남음. localStorage 영속(persist*), PERSIST_*, BroadcastChannel 제거. (init의 메모리 전용 __jsonListCacheClear는 원본이라 유지)
  2. WEB-INF/views/attr/tabs/body-script.jsp -> 106행 window.__jsonListCacheScope 제거.
  3. resource/modules/attr/tabs/body-script.js -> fnAdminModifyPQGrid의 __jsonListCacheClear() 호출 제거.
- **유지(Redis 관련)**: SystemServiceImpl step1 @CacheEvict 제거 상태, InnodaleServiceImpl admin evict(systemType "CODE" clear). system jsp는 이미 호출 제거돼 원본과 동일.
- **검증**: grep 잔존참조 0(메모리 전용 __jsonListCacheClear 1건만 = 원본). node --check PASS. answer-reviewer로 git 베이스라인 검증 완료.
- **주의**: %클라우드 미커밋(3파일 원복 + logback-spring.xml 로그추가). 커밋은 사용자 몫. logback 변경은 검증용이라 별도(원하면 따로 원복).

## [2026-06-18] 클라 캐시 무효화를 admin 경로로 일원화 (미커밋)
- **결정**: 무효화 신호를 admin 공통코드 저장 경로로 통일. 어제 "클라 무효화 생략"의 본의는 전 사용자 전역 push(B-2) 보류였고, admin 화면 자체의 무효화 누락은 정정 대상.
- **수정 2파일(%클라우드, 미커밋)**:
  1. `resource/modules/attr/tabs/body-script.js` fnAdminModifyPQGrid(공용 저장함수) success 콜백에 `systemType==='CODE'`일 때만 `__jsonListCacheClear()` 추가. 서버측 evict(InnodaleServiceImpl, "CODE"일 때만)와 대칭. menu/site/codegroup 저장엔 미발동.
  2. `WEB-INF/views/pages/system/common-code-master.jsp` 기존 __jsonListCacheClear() 호출 제거(안 쓰는 경로).
- **결과**: admin 코드 저장 시 Redis(InnodaleServiceImpl.clear) + 브라우저 localStorage(__jsonListCacheClear) 둘 다 무효화. 호출부는 admin 경로 1곳으로 일원화.
- **참고**: __jsonListCacheClear의 BroadcastChannel은 같은 브라우저 다른 탭/창만 전파(다른 사용자 아님). 전 사용자 push 아님.
- **검증**: body-script.js node --check PASS. answer-reviewer OK. (JSP는 2줄 제거)
- **주의**: 미커밋 2파일. 커밋은 사용자 몫.

## [2026-06-18] code-cache step1 @CacheEvict 제거 (기존 경로 무효화 취소, 미커밋)
- **사용자 지시**: admin 페이지가 아닌 기존 경로의 무효화 취소. 해당 기능(일반 사용자화면 코드수정)은 실질적으로 사용하지 않음.
- **제거**: `SystemServiceImpl.commonCodeModifyGrid()`의 `@CacheEvict`(step1, getSessionCodeList allEntries/everyHour) 삭제 + 미사용된 `import ...CacheEvict` 제거(465행 주석은 무관). 본문 로직 무변경.
- **남는 무효화**: admin 경로 evict(InnodaleServiceImpl.java, systemType=="CODE"일 때 clear)만 유지. 기존 step1 경로는 미발동이라 취소해도 동작 영향 없음.
- **검증**: gradlew build -q PASS(경고는 기존 deprecated/unchecked 노트).
- **주의**: %클라우드 미커밋(SystemServiceImpl.java + InnodaleServiceImpl.java 2파일). 커밋은 사용자 몫.

## [2026-06-17] code-cache STEP B-1 진행 — admin 무효화 누락 경로 점검+서버 evict (미커밋)
- **STEP 범위 결정**: 사용자와 논의. 현 규모(고객 적음)+기준코드 거의 불변 → B-2(전 사용자 즉시 push: SSE/폴링)는 오버스펙(개악)이라 보류. B-1(전파 사슬 빈틈 점검/검증)만 진행.
- **STEP A 실화면 검증 완료**: 가동서버(smd.localhost:8081) 실 Chrome 2창 측정. ①영속저장 PASS(localStorage scope=SMD) ②새창 캐시공유 PASS(hit_persist=1, selectSessionCodeList 재요청 0) ③broadcast PASS(수신창 메모리 clear + 공유 localStorage 비워짐). 임시 _verify_stepA.py로 측정 후 삭제.
- **누락 경로 점검(검증완료)**: 기존 무효화는 commonCodeModifyGrid(@CacheEvict, step1) 1곳뿐. 누락 2개 —
  (A) admin 공통코드: admin/common-code-master.jsp → /paramQueryModifyGrid → InnodaleServiceImpl.modifyGrid. 서버 evict 없음 + 클라 clear 없음.
  (B) 시스템 신규등록 updateSystem(register)→insertCommonCodeForSystem. 새 SYSTEM_ID 코드라 기존 캐시 무관 → 실익 낮음, 보류.
  - 사용자 정보: 일반 사용자화면 코드수정은 막아둠. 기준코드 변경 코드경로 = admin 1곳 + DB직접뿐. 추론: step1 @CacheEvict는 현재 실질 미발동(둬도 무해).
  - 함정: modifyGrid는 11개 화면 공용 범용 저장 메서드 → 무조건 evict는 개악.
- **구현(미커밋, 1파일 InnodaleServiceImpl.java)**: everyHour CacheManager 주입 + modifyGrid 끝에서 systemType=="CODE"일 때만 getSessionCodeList 캐시 clear. CODEGROUP(TBL_CODE_GROUP)은 무관이라 제외. 클라 무효화는 사용자 결정대로 생략(서버만). 기존 로직 무변경.
- **검증**: gradlew build -q PASS. answer-reviewer 통과(캐시명 step1과 문자 동일, @Qualifier everyHour 일치, systemType=="CODE" 외 과잉무효화 없음). CRUDGrid()도 modifyGrid 경유라 CODE면 동일 발동(의도).
- **남은 B-1**: 실화면 end-to-end 검증(admin 코드 저장→Redis 캐시 비워져 재요청 시 DB 최신) — 서버 재빌드/재시작 필요. TTL 30분 유지.
- **주의**: %클라우드 미커밋(InnodaleServiceImpl.java). 커밋은 사용자 몫. 경로 B 미적용.

## [2026-06-16] %테스트 화면 하단 메트릭 오버레이 추가 (검증 대기: 실화면)
- **목적**: 코드캐시 실화면 검증 보조. Playwright 화면 하단에 ①화면 Depth(메뉴 경로+중첩단계: 메인/모달/새창) ②API 요청(/json-list queryId별 집계) ③캐시(window.__jsonListCacheStats) 실시간 표시.
- **수정 1파일**: `Projects\Test-Automize\qa_agent\tools.py`
  1. `_API_HOOK_JS` 상수 신설 — fetch/XHR 래핑해 `window.__qaApiLog`에 적재(queryId 추출). 캐시 HIT 시 실제 XHR 미발생이라 API 패널엔 안 잡히고 캐시 stats에만 → 검증 핵심.
  2. `_OVERLAY_JS`에 좌하단 패널 `#__qa_overlay_metrics__` + `updateMetrics()` + 1초 폴링 타이머 추가. modal auto-hide 대상(header/#__qa_overlay__)에서 제외해 팝업 떠 있어도 계속 보임.
  3. `_ensure_browser`에서 `add_init_script(_API_HOOK_JS)` 선주입 + 로그인 후 evaluate 2곳.
  4. `_ensure_browser` viewport 환경변수 분기 — `QA_AGENT_FIT_SCREEN=1`이면 `no_viewport=True` + launch args `--start-maximized`(실제 모니터 크기에 맞춤), 미설정 시 기존 `viewport=1920x1080` 유지(기존 자동화 불변 → 규칙 준수).
- **검증**: py_compile PASS, 추출 JS node --check PASS. `_overlay_log` 시그니처 불변 → 기존 테스트(test_cumulate_recovery_policy의 monkeypatch) 영향 없음.
- **실화면 검증 완료(2026-06-16)**: agent_run --row 6 PASS(39초). 임시 검증 스크립트(_ensure_browser→tc_navigate→evaluate, 실행 후 삭제)로 좌하단 패널 실측: hasPanel=true, API 후킹 동작(/json-list 9건 queryId별 집계), 캐시 stats=ttl:9/miss:9, Depth="메인(L1)". 스크린샷으로 3패널(상단 TC/우하단 Tool/좌하단 메트릭) 비충돌 확인. 단 Depth 경로는 검증 스크립트가 TC정보 미주입이라 "미상" 표시 — agent_run 정식 실행 시 menu/screen 채워짐.
- **참고**: persist HIT은 0(첫 로드라 정상, set만 됨). localStorage 영속 HIT은 새창/새로고침에서 확인 가능(STEP A 핵심) — 미실측.
- **해상도 이슈 해결(2026-06-16)**: 사용자 모니터 1707x1067(DPI 150%)에서 고정 viewport 1920x1080이 우측·하단 잘려 하단 패널 안 보임. 위 4번(QA_AGENT_FIT_SCREEN) 도입으로 해결. 시연 스크립트가 이 변수를 켜고 실행 → 잘림 없이 하단 패널(좌하단 메트릭/우하단 Tool) 표시 확인.
- **주의**: 미커밋. %테스트 git 커밋도 사용자 확인 필요(정책상 %클라우드만 명시했으나 동일 보수적으로 대기).

## [2026-06-16] 코드캐시 후속 플랜 수립 + STEP A 구현 (검증 대기: 실화면)
- **배경/플랜**: 사용자 4원칙(1.표시 동일성 2.같은페이지 중복I/O 3.다른페이지(팝업/새창) 중복I/O 4.기준TBL 변경 반영)에 맞춰 오늘 플랜 수립. 메모리 `project_code_cache_principles` 참조. STEP A(클라 캐시 저장소 전환)부터 진행키로 사용자 선택.
- **사전 조사(확정)**: 서버 통로 이미 존재 — /json-list → InnodaleServiceImpl.getList:60 → (queryId=systemMapper.selectSessionCodeList & LOGIN_SYSTEM_ID 있으면) SystemServiceImpl.getSessionCodeList:434 @Cacheable(everyHour, Redis 1h). 무효화는 commonCodeModifyGrid:63 @CacheEvict(allEntries). 팝업/새창 JSP도 대부분 tabs/body-script.jsp를 include → json-list-cache.js + __jsonListCacheScope(SYSTEM_ID) 로드됨. 문제는 sessionStorage가 창마다 별도라 새창이 캐시 공유 못 함.
- **STEP A 구현(미커밋, 1파일)**: `resource/asset/js/json-list-cache.js`
  1. 영속 계층 sessionStorage → localStorage 전환(persistStore() 헬퍼 도입). 같은 origin 모든 창(팝업/새창) 캐시 공유. scope(SYSTEM_ID) 가드·TTL 30분 유지.
  2. BroadcastChannel('jsonListCache') 추가 — __jsonListCacheClear가 clear를 전 창에 broadcast, 수신 창은 메모리 ttlCache/inflight만 비움(공유 localStorage는 발신 창이 이미 비움). 미지원 브라우저는 자동 무시.
- **검증**: node --check PASS. **node 스모크 테스트 11건 PASS(2026-06-16 재개 세션)** — localStorage·BroadcastChannel 모킹으로 작성: 영속 set, 새 창 공유 HIT(localStorage 전환 핵심), scope 불일치/TTL 만료 폐기, clear가 localStorage 비움 + 브로드캐스트로 타 창 메모리 clear, 비영속 쿼리·scope 없음 시 미저장. (하네스 측 임시 하네스라 결과만 기록, 파일은 정리)
- **남은 검증(실화면, 미실행)**: runDev로 띄워 ①메인 로드 후 새 창/팝업 열어 Network에서 selectSessionCodeList 재요청 안 나가는지(localStorage HIT) ②공통코드 저장 시 다른 열린 창의 캐시도 비워지는지(broadcast). 서버+브라우저 조작이라 사용자 개입 필요.
- **주의**: localStorage는 영구라 로그아웃 후에도 잔존하나 scope=SYSTEM_ID 가드로 타 테넌트 차단(코드목록은 시스템 단위라 사용자 무관).
- **다음 단계**: STEP B(기준변경 무효화 전파 완성/검증) → STEP C(selectBox 진입 일원화) → STEP D(selectBox 함수 통합·3벌 중복 정리, 영향범위 커서 신중).

## [2026-06-12] 코드목록 클라이언트 캐시 B안 구현 완료 (검증 대기: 실화면)
- **구현**: json-list-cache.js에 sessionStorage 영속 계층 추가.
  selectSessionCodeList를 로그인 세션당 1회만 수신 (PERSIST_PREFIXES).
  TTL 30분(서버 everyHour 이내), 테넌트 가드(entry.scope=SYSTEM_ID 대조),
  async:false 호출엔 동기 success(respondCached) — g_code 타이밍 보존.
- **수정 파일 3개 (%클라우드, 미커밋)**:
  1. resource/asset/js/json-list-cache.js — 영속 계층 본체
  2. WEB-INF/views/attr/tabs/body-script.jsp — `window.__jsonListCacheScope`
     (sessionScope.authUserInfo.SYSTEM_ID) 노출
  3. WEB-INF/views/pages/system/common-code-master.jsp — 코드 저장 성공 시
     `__jsonListCacheClear()` 호출(무효화)
- **검증 완료**: node --check, node 스모크 테스트 11건 전부 PASS
  (영속 적중/스코프 불일치 폐기/TTL 만료/클리어/타 쿼리 비영속/동기 success),
  gradlew build 통과.
- **남은 검증(실화면)**: runDev로 띄워 로그인 → F5 → Network 탭에서
  json-list(selectSessionCodeList) 요청이 안 나가는지 + 콘솔 PERSIST HIT 확인.
- **한계(의도적 범위 제한)**: common/page/sample body-script.jsp 3개 템플릿은
  json-list-cache.js 자체를 미포함이라 영속 캐시 미적용(본 앱은 tabs 셸 사용).
- **참고**: 코드 수정 후 타 사용자 브라우저는 최대 30분 구버전 가능(기존
  메모리 캐시와 동일한 성격의 시차).

## [2026-06-12] 코드목록 클라이언트 캐시 제안 (사용자 결정 대기)
- **배경**: selectSessionCodeList(TBL_CODE 520건)의 DB 구간은 어제 Redis 캐시로 완료. 남은 것은 브라우저-서버 HTTP 구간 — 전체 페이지 로드(로그인·F5·common/page/sample 템플릿 진입)마다 요청 발생. 기존 json-list-cache.js는 메모리 캐시라 페이지 로드 시 소멸.
- **추가 발견**: tabs body-script.js의 해당 AJAX가 `async:false`(동기) — 메인 로드 렌더 블로킹 지점.
- **제안(B안 추천)**: json-list-cache.js에 sessionStorage 계층 추가 → 로그인 세션당 1회만 수신. 무효화 3종: 로그인 시 클리어 + TTL(서버 everyHour와 정합) + 공통코드 저장 시 클리어. 주의: 멀티테넌트 키에 SYSTEM_ID 포함, payload 크기 실측.
- **상태**: 사용자 결정 대기 (진행 지시 없었음).

## [2026-06-12] %클라우드 커밋 정책 규칙화
- 사용자 지시: "%클라우드 커밋은 절대 말없이 진행 금지, 사용자 전담". CLAUDE.md 자율 실행 안전 규칙 최상단 + 메모리(feedback_cloud_commit_policy) + execute.py 규칙 6(기존)에 반영.

## [2026-06-12] devtools 도입 — 인텔리제이식 Java 자동 재시작 완성
- **변경**: ①%클라우드 build.gradle에 `developmentOnly 'org.springframework.boot:spring-boot-devtools'` 추가(bootRun 전용, bootWar 미포함 — ROOT.war 내 부재 확인) ②runDev.local.bat에 watcher 창(`gradlew classes --continuous`) 단계 추가. CLI에선 devtools가 컴파일된 클래스 변경만 감지하므로 저장→자동 컴파일 watcher가 필수.
- **검증(전부 PASS)**: gradlew build 통과 / bootRun 기동 시 LiveReload(35729) 활성 / Java 주석 추가 후 classes 재컴파일 → "Restarting due to 1 class path change" → 5~7초 내 재기동 → HTTP 200 응답. 임시 수정은 원복 완료, 검증 서버는 종료함.
- **사용법**: `shell\runDev.local.bat` 실행 → 본 창(서버) + WATCH 창(자동 컴파일) 2개 뜸. Java 저장만 하면 몇 초 뒤 자동 재시작. JS/CSS는 즉시, JSP는 새로고침 반영(기존과 동일). WAR 배포 검증은 deploy.local.bat.
- **주의**: build.gradle 변경은 미커밋(커밋은 사용자 몫). devtools 재시작 후 Redis 세션과의 궁합(재로그인 필요 여부)은 실사용에서 1회 확인 필요. 재시작이 거슬리면 watcher 창만 닫으면 기존 동작으로 복귀.

## [2026-06-12] 디렉토리 재구성 — Projects\ 하위로 이동 (경로 참조 일괄 갱신)
- **변경**: 사용자가 `E:\Tomes-Cloud` → `E:\harness_framework\Projects\Tomes-Cloud`, `E:\Test-Automize` → `E:\harness_framework\Projects\Test-Automize` 로 이동. 구 경로는 더 이상 존재하지 않음. 각 프로젝트는 자체 git 저장소 유지(하네스 repo의 중첩 git 추적은 사용자가 소스트리에서 수동 처리 완료).
- **이 문서의 과거 항목**: 아래 [2026-06-11] 이전 항목들의 `E:\Tomes-Cloud`, `E:\Test-Automize` 경로는 모두 새 경로로 읽을 것 (역사 기록이라 수정하지 않음).
- **갱신 완료 파일**:
  1. `CLAUDE.md` — 약칭 경로, 명령어(cd 경로), 안전 규칙("%클라우드 작업 시 Projects\Tomes-Cloud 외부 수정 금지"로 재해석, phases/·HANDOFF.md 예외 명시), 재구성 안내 추가.
  2. `PATHS.md` — 전체 경로 갱신(프로젝트 내부 경로는 루트 기준 상대 경로로 전환).
  3. `.claude\settings.json` + `Projects\Tomes-Cloud\.claude\settings.json` — Stop 훅의 빌드/테스트 cd 경로 갱신(두 파일 동기화 유지). 훅 로직 자체는 무변경.
  4. `scripts\execute.py` — 프롬프트 규칙 6의 커밋 금지 경로 갱신.
  5. `Projects\Test-Automize\.env` — TOMES_ROOT, LOG_DIR 갱신.
  6. `Projects\Tomes-Cloud\shell\` — deploy.local.bat, runDev.local.bat의 PROJECT_DIR / startServer.local.bat의 DEPLOY_PATH 갱신 (구 경로 하드코딩이라 서버 기동·배포가 깨지는 상태였음).
  7. 메모리 `feedback_project_aliases.md` — 약칭 경로 갱신.
- **수정하지 않은 것(의도적)**: `phases/code-cache/*`(완료된 phase의 역사 기록), `logs/*`(로그), `docs/*.md`(경로 아님, 프로젝트명 표기만).
- **주의**: 로컬 서버 URL(`http://smd.localhost:8081/`), 로그 위치(`E:\LOGS\`, `D:\LOGS\`)는 프로젝트 외부라 영향 없음. %클라우드 bat 3개 수정은 미커밋 변경으로 남음(커밋은 사용자 몫). IDE(인텔리제이 등) 프로젝트 열기 경로는 사용자가 직접 새 경로로 다시 열어야 함.

## [2026-06-11] runDev.local.bat 생성 — 인텔리제이식 라이브 반영
- **위치**: `E:\Tomes-Cloud\shell\runDev.local.bat` (미추적). 8081 정지 → `gradlew bootRun --args="--spring.profiles.active=local --server.port=8081"`.
- **원리**: bootRun은 WAR 패키징 없이 src/main/webapp을 직접 서빙 → JS/CSS 저장 즉시, JSP는 Jasper 재컴파일로 새로고침 시 반영. Java 수정만 재실행 필요(devtools 미도입).
- **테스트**: body-script.js 마커 추가/제거 모두 빌드 없이 HTTP 즉시 반영 PASS. tomcat-embed-jasper 의존성 존재 확인(build.gradle 46행).
- **사용 구분**: 개발 = runDev.local.bat / 배포 검증 = deploy.local.bat(WAR).

## [2026-06-11] code-cache 최종 검증 완료 ✅
- **Redis 캐시 적중 확인**: 첫 로드(14:42:39) selectSessionCodeList SQL 1회 실행, 강력 새로고침(14:43:39)엔 selectSystemInfo만 실행되고 코드 SQL 미실행 = Redis 응답. 캐싱 작업 전체 완료.
- **남은 정리(사용자 결정 대기)**: ①%클라우드 staged 캐싱 코드 3파일 커밋 ②body-script.js 543행 `console.error('에러 확인용')` 제거 ③&하네스 feat-code-cache 브랜치 push/머지 여부.
- **차기 개선 후보**: selectSystemInfo가 요청마다 실행(1분 27회, SystemServiceImpl 421행 @Cacheable 주석 상태) — 캐싱 후보. estimate-standard-calculation-manage.js change 핸들러 'update' 재진입 제거(분석 완료, 미적용).

## [2026-06-11] deploy.local.bat 생성·테스트 완료
- **위치**: `E:\Tomes-Cloud\shell\deploy.local.bat` (미추적). 정지→bootWar 빌드→기동을 한 명령으로. 사용: `deploy.local.bat` (증분) / `deploy.local.bat clean` (강제 재빌드).
- **배경**: "수정 반영 안 됨" 재발 문의. 팀원의 `clean bootWar`가 듣는 원리 = ①bootWar만 실행해 일반 war의 ROOT.war 덮어쓰기 회피(이중 출력 충돌, war enabled=false로 이미 근본 해결됨) ②clean으로 증분 상태 오염 제거(6/9 데몬 크래시 후유증 가능). 스크립트는 순서 실수·파일 잠금까지 차단.
- **1차 작성본 사고(수정됨)**: findstr 패턴 공백이 OR 해석 → 모든 LISTENING 프로세스에 kill 시도. 비관리자라 시스템 영향 없음 확인(VS Code/mysqld/java 생존). 수정: `findstr /c:` 단일 패턴 체인(AND) + 드라이런 검증 후 재테스트. 교훈: bat의 findstr 다중 단어 = OR.
- **테스트**: 1차(서버 없음→빌드→기동) PASS, 2차(가동 중 8081 프로세스만 정확히 kill→교체) PASS, HTTP 서빙 검증 PASS.
- **검증 대기(이어서)**: 사용자 로그인→메인 로드→강력 새로고침 후 sql.query 로그에서 selectSessionCodeList가 2회째 안 나가는지(Redis 적중) 확인.

## [2026-06-11] %클라우드 커밋 정책 변경 (C안 적용)
- **경위**: step 세션들이 execute.py 프롬프트 규칙 6("모든 변경사항을 커밋하라")에 따라 %클라우드 Sun-Pro에 직접 커밋(3건). 사전에 "코드 커밋은 사용자 몫"이라 안내했던 것과 불일치 → 사용자 지적.
- **조치**:
  1. %클라우드 커밋 3개 `reset --soft`로 취소. 코드 변경(+37줄, 3파일)은 staged 상태로 보존. 기존 미커밋 변경(build.gradle, logback)은 unstaged로 분리 유지.
  2. execute.py 프롬프트 규칙 6을 "git 커밋 직접 실행 금지, 특히 E:\Tomes-Cloud 절대 금지"로 교체. FEAT_MSG의 em-dash도 ASCII로 변경.
  3. 메모리 저장: feedback_verify_agent_prompts (자동 세션 행동 단정 전 주입 프롬프트 전문 확인).
- **현재 %클라우드 상태**: staged = code-cache 코드 3파일 / unstaged = build.gradle, logback, body-script.js의 사용자 디버그 라인(`console.error('에러 확인용')` 543행) / untracked = bat, .claude, hs_err×3.
- **남은 것**: 서버 재시작 + 캐싱 동작 검증(sql.query 로그 + 화면 체감). 커밋은 사용자 결정 대기.

## [2026-06-11] code-cache step 2 완료 (client-memoize) — task 전체 완료
- **완료**: `body-script.js`(tabs용)의 `fnGetCommCodeGridSelectBox`/`fnGetCommCodeGridSelectBoxEtc`에 `g_codeSelectBoxCache` 메모이제이션 적용(키 `SB|highCd|topOption`, `ETC|highCd|refCd`). g_code AJAX 재로드 success에서 캐시 초기화. 함수 시그니처·반환 형태·`new Option('', null)` 동작 보존.
- **사전 조사**: 호출부 300건(JS/JSP 27개 파일) 패턴 검사 — 반환 배열 변형(push/splice/sort/pop) 호출부 없음(.filter 등 비변형만) → slice() 복사 없이 캐시 배열 직접 반환. `console.error('1')`은 파일에 이미 부재했음(이전 디버깅 세션에서 제거된 듯 — 제거 작업 불필요).
- **검증**: `gradlew build -q` 통과, node --check 통과, AC grep 전부 PASS. 커밋: %클라우드 Sun-Pro fc62c5c, &하네스 feat-code-cache 8686003(index.json step2=completed).
- **다음 단계**: code-cache 3개 step 모두 완료 → 서버 재시작(shell\startServer.local.bat, gradlew build 후) + estimate-standard-calculation-manage 화면에서 렌더링 체감 확인. 필요 시 feat-code-cache 브랜치 push/PR.
- **주의**: %클라우드에 step과 무관한 미커밋 변경(build.gradle, logback-spring.xml) 잔존 — 커밋하지 않고 그대로 둠.

## [2026-06-11] code-cache step 1 완료 (cache-evict)
- **완료**: `SystemServiceImpl.commonCodeModifyGrid()`에 @CacheEvict 추가 — value는 getSessionCodeList의 @Cacheable과 문자 단위 동일(`com:tomes:service:impl:SystemServiceImpl:getSessionCodeList`), `allEntries=true`, `cacheManager="everyHour"` 명시(@Primary가 every5Seconds라 생략 불가). 본문 로직 무변경(어노테이션 5줄만 추가).
- **검증**: `gradlew build -q` 통과(경고는 기존 코드의 deprecated/unchecked 노트). 커밋: %클라우드 Sun-Pro 5e8b025, &하네스 feat-code-cache a8ef166(index.json step1=completed).
- **다음 단계**: step 2 client-memoize(body-script.js 두 함수 메모이즈 + console.error('1') 제거). 완료 후 서버 재시작 + 화면 확인.

## [2026-06-11] code-cache step 0 완료 (server-cache)
- **완료**: `InnodaleServiceImpl.getList()`에 위임 분기 추가 — queryId가 `systemMapper.selectSessionCodeList`이고 LOGIN_SYSTEM_ID가 있으면 주입된 `SystemService.getSessionCodeList()`(기존 Redis @Cacheable, everyHour) 호출. 없으면 기존 DAO 경로 유지(멀티테넌트 안전). 순환 의존성 없음 확인(SystemServiceImpl은 DAO만 주입).
- **검증**: `gradlew build -q` 통과. 커밋: %클라우드 Sun-Pro 454d822, &하네스 feat-code-cache a701100(index.json step0=completed).
- **다음 단계**: step 1 cache-evict(commonCodeModifyGrid에 @CacheEvict), step 2 client-memoize. 완료 후 서버 재시작(startServer.local.bat) + 화면 확인.

## [2026-06-11] 공통코드 캐싱 task 생성 (code-cache)
- **목표**: 고정 기준코드의 반복 DB 조회·렌더링 순회 제거 (서버 Redis + 클라이언트 메모이즈)
- **핵심 발견**: `/json-list`(selectSessionCodeList)는 캐시를 안 타지만, 동일 쿼리를 감싼 `SystemServiceImpl.getSessionCodeList()`에 이미 Redis @Cacheable(everyHour) 존재 → 위임만 하면 됨. 클라이언트엔 json-list-cache.js(30분 메모리 캐시)도 이미 존재.
- **생성 파일**: `phases/index.json`, `phases/code-cache/index.json`, `phases/code-cache/step0~2.md`
  - step0 server-cache: InnodaleServiceImpl.getList → getSessionCodeList 위임 (LOGIN_SYSTEM_ID 없으면 우회)
  - step1 cache-evict: commonCodeModifyGrid에 @CacheEvict(allEntries, cacheManager="everyHour")
  - step2 client-memoize: body-script.js 두 함수 메모이즈 + console.error('1') 제거
- **다음 단계**: `python3 scripts/execute.py code-cache` 실행 → 완료 후 gradlew build + 서버 재시작(startServer.local.bat) + 화면 확인
- **주의**: 멀티테넌트 — 캐시 키에 SYSTEM_ID 필수. @Primary cacheManager가 every5Seconds라 evict에 everyHour 명시 필요.

## [2026-06-11] estimate-standard-calculation-manage 무한루프 디버깅
- **증상**: `fnGetCommCodeGridSelectBoxEtc`의 for문이 무한반복처럼 보임 + 심어둔 `console.error('1')`(body-script.js:532)가 반영 안 됨.
- **무한반복 원인(분석 완료, 수정 미적용)**: `estimate-standard-calculation-manage.js`의 change 핸들러(645행·2090행)가 source 필터에 `'update'`를 포함 → `updateRow` API가 다시 change를 발생시켜 재진입 + merge 범위 전파 + `refreshView` 중복 호출(660·683행)로 렌더 폭증. for문 자체는 무한 아님. 수정안: source 필터에서 `'update'` 제거(표면처리비 그리드 1331행은 이미 그렇게 되어 있음).
- **반영 안 된 원인(해결)**: 서버가 `java -jar build\libs\ROOT.war` 방식(shell\startServer.local.bat). 구 프로세스(9:38 시작)가 신규 WAR 빌드(9:43) 이전에 떠서 구버전 서빙 중이었음. PID 32788 종료 → bat 재실행 → HTTP로 `console.error('1')` 서빙 확인 완료.
- **워크플로우**: 소스 수정 → `gradlew build` → 서버 재시작 (이 순서 필수. 정적 리소스도 WAR에 포함됨).
- **주의**: 함수 정의가 3곳(tabs용 `resource/modules/attr/tabs/body-script.js:528`=본 앱 사용, `views/attr/page/body-script.jsp:593`, `views/attr/common/body-script.jsp:515`). 디버깅 끝나면 body-script.js:532의 `console.error('1')` 제거 필요.

---

## 작업 목표
- 직전 본 작업: **%테스트(E:\Test-Automize)를 사용해 "TBL_CODE1 영향 범위.xlsx" 기반으로 이전에 테스트했던 14개 쿼리를 다시 테스트**하기.
- 그 전에 환경/규칙 정비를 먼저 진행 중이었음.

## 완료
- **프로젝트 약칭 규칙 확정**: `%클라우드`=E:\Tomes-Cloud, `%테스트`=E:\Test-Automize(최신), `&하네스`=E:\harness_framework. (CLAUDE.md + 메모리 반영) ※ 구버전 E:\Tomes-AutoTest는 사용자가 삭제함.
- **권한 모드 변경**: `&하네스\.claude\settings.local.json`의 `permissions.defaultMode` = `"bypassPermissions"` (자동 승인). 위험명령 차단 PreToolUse 훅·빌드/테스트 Stop 훅은 유지.
- **CLAUDE.md 규칙 추가**: (1) 민감 작업(설정 변경 등)은 yes/no 전 본문 상세 설명, (2) 세션 관리 규칙(HANDOFF 상시 갱신 + 컨텍스트 ~50% 사용자 주도 초기화).
- **상태줄 설정**: 컨텍스트 사용량 % 상시 표시(`[ctx 48% (96k/200k)]`), 50%↑면 `[!ctx ...]`. 스크립트 `C:\Users\USER\.claude\statusline-command.sh`, 설정 `C:\Users\USER\.claude\settings.json`.
- 메모리 파일: feedback_project_aliases / feedback_explain_before_sensitive / feedback_session_handoff 저장.

## 진행 중 · 미완
- **%테스트 프로젝트 파악(미완)**: README/CLAUDE.md/qa_agent 구조/테스트 실행 방식(`python -m qa_agent.agent_run --row N`)/시나리오 포맷(docs/scenarios의 CD-FT-BIZ-*.json) 등을 아직 못 읽음. 권한 프롬프트·사용자 인터럽트로 중단됨.
- **14개 쿼리 재테스트(미착수)**.

## 다음 단계
1. (재시작 후) bypassPermissions·상태줄 적용 확인.
2. **%테스트 파악 먼저**: README, CLAUDE.md(E:\Test-Automize\CLAUDE.md), HANDOFF_NEXT_SESSION.md, qa_agent/, test_auto/, docs/scenarios 샘플, config.py, requirements.txt 읽고 "아는 것/모르는 것" 정리해 사용자에게 보고.
3. 그 다음 14개 쿼리를 %테스트 방식으로 테스트.

## 14개 쿼리 (테스트 대상 — TBL_CODE1→TBL_CODE / TBL_CODE_LANG1→TBL_CODE_LANG 마이그레이션)
- `sqlMaps/v1/main.xml`: selectProcessHistoryList-mainV1 (메인 대시보드) — 1개
- `sqlMaps/v1/material.xml`: 12개 (소재 주문등록 / 보유 소재 관리 / 재고관리). 예: selectItemOrderRegisterListV1, selectInWarehouseManageListV1, selectInsideStockListV1 등
- `sqlMaps/material.xml`: selectInsideStockAbbrNm (line 2297, 소재 관리>내부 재고) — 1개
- 원본 영향범위 엑셀: `C:\Users\USER\Desktop\기준코드 관련\TBL_CODE1_영향범위.xlsx` (전체 112개 참조 중 위 14개가 실제 변경됨). 엑셀 덤프: `E:\harness_framework\logs\xlsx_dump.txt`
- 이전(구버전 Tomes-AutoTest) 테스트 결과: CD-MAIN-001, CD-MAT-001~009 = 10/10 통과. **단, %테스트엔 해당 시나리오(CD-MAT/CD-MAIN)가 없음** → 새로 매핑/작성 필요할 수 있음.

## 블로커 · 주의
- 로컬 서버 URL: `http://smd.localhost:8081/` (이전 확인 시 HTTP 302 = 가동 중). 개발서버는 `https://dev-smd.tomes.co.kr:8081`.
- gws(Google Sheets) OAuth 토큰 만료 이력 있음 — 시트 연동 테스트 시 재인증 필요할 수 있음.
- 재고관리 메뉴는 작업관리(MENU_SEQ 1058) 하위로 이동됨(SEQ=1061). 메뉴 Depth 판단은 [시스템][메뉴관리] 페이지(DEL_YN='N' 활성 메뉴) 기준.
- 3단계 이상(상세/팝업/탭) 쿼리는 추가 인터랙션 자동화 필요.

## [2026-07-14 이동] 메인 가동율 차트 V1 쿼리 적용 건 — 사용자 '이 건 마무리' 확정으로 HANDOFF에서 이동
(main.jsp 차트 변경은 커밋 9f49184로 반영 확인. 잔존 표시/구조 이슈는 handoff/차트.md의 07-03 섹션에서 계속 관리. 아래는 원문 그대로.)

## [2026-07-09] 메인 가동율 차트 V1 쿼리 적용 + JS null 가드 (%클라우드, 미커밋)
- **[07-10 마무리]** PR리뷰 MD 작성: 바탕화면 `PR리뷰\[07.09 메인 가동율차트 V1쿼리 전환].md`(answer-reviewer 검토 OK — 플로우 행번호·죽은 Highcharts 판정·diff stat 전부 실측 일치). 사용자 판단 확정: **실사용 기능 문제 없음, 이 건 마무리**. 잔존(REAL_RATIO 클램프 미적용·집계일 버튼 핸들러 2회 등록·막대 뜸·죽은 코드 정리)은 보류 목록 유지. 현재 체크아웃 **Danga-order**로 전환돼 있음(미커밋 4파일 = main.jsp + 견적 3파일) — 커밋 시 브랜치·파일 분리 주의.
- 배경: 배치 데이터 부재(TBL_BATCH_MCT_WORK 최신 20260609)로 차트 빈 화면 문의 → 점검 중 레거시 쿼리 결함 3건 확인(테넌트 격리 누락·고아 장비 NULL명→JS 크래시·복수작업자 조인 중복→Average 왜곡). 상세 근거는 07-03 섹션과 동일 + 이번에 DB 실측으로 확정(고아 362행 도달가능 2025-10-15~2026-03-29, 타테넌트 조인 2870행, 복수작업자 장비-일 16건).
- 변경(main.jsp 2줄, 사용자 지시): ①371행 queryId `main.selectOperatingRateChart` → `main.selectOperatingRateChartV1`(v1/main.xml:6 — SYSTEM_ID 상시 필터 + INNER JOIN TBL_EQUIP(고아 배제) + WORK_EQUIP IN 서브쿼리(중복 제거)) ②326행 `(rowData.EQUIP_NM || '').toLowerCase()` null 가드.
- 검증(라이브 8081 실화면, Playwright 세션 scratchpad verify_chart_v1.py): 핫리로드로 V1 queryId 요청 확인, 06/09+작업자·구역 '전체'에서 4건 응답(Average 14/NC-01 11/NC-02 14/NC-03 16%)·막대 4개 렌더·JS에러 0·스크린샷 육안 확인. V1 vs 레거시 동일 날짜 SQL 결과 동치도 사전 확인.
- ★검증 시 주의: test 계정 세션은 구역 기본값이 E05R50으로 잡혀 있어(장비들은 E05R10) 기본 조회가 0건 — 구역 '전체' 필요. 또한 07-08 이후 배치 데이터가 없어 기본 집계일자(어제)는 항상 0건(SP_BATCH_MCT_WORK_DT 수동 실행 여부는 사용자 결정 대기).
- 잔존(보류): 표시/구조 이슈(막대 뜸·SQL이 HTML 생성·픽셀 하드코딩)와 죽은 Highcharts 게이지 코드·이제 미참조가 된 레거시 selectOperatingRateChart 정리 — 07-03 섹션 참조. 커밋은 사용자 몫.
