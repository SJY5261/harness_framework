"""
시트 A열(메뉴명1) 누락된 그룹 헤더를 DB GNB 구조 기준으로 일괄 업데이트.
"""
import sys, json, subprocess, shutil
sys.path.insert(0, r'E:\Tomes-AutoTest')

gws = shutil.which('gws.cmd') or 'gws.cmd'
SHEET_ID = '1HjYzZryKSpU2ksnQg03sPEL66WhMVdrziocR8QQ2bKE'
TAB = '자동화테스트'

# row: menu1 값 (DB GNB 기준, 현재 비어있거나 틀린 행만)
UPDATES = {
    34:   '견적관리',
    113:  '견적관리',
    255:  '수주관리',
    279:  '수주관리',
    305:  '수주관리',
    333:  '수주관리',   # 수주관리 > 작업지시관리
    513:  '수주관리',   # 수주관리 > 가공확정
    575:  '작업관리',   # 작업관리 > 제조원가 분석
    616:  '작업관리',   # 작업관리 > 재고관리  ← 핵심
    813:  '외주관리',
    901:  '외주관리',
    1005: '외주관리',
    1050: '외주관리',
    1080: '외주관리',
    1220: '소재관리',
    1252: '소재관리',
    1358: '생산관리',
    1409: '생산관리',
    1440: '생산관리',
    1458: '생산관리',
    1604: '검사관리',
    1637: '검사관리',
    1747: '출하관리',
}

print(f'총 {len(UPDATES)}개 셀 업데이트 시작...')

# 개별 업데이트 (batchUpdate로 묶으면 좋지만 단순성 우선)
ok, fail = 0, 0
for row_num, menu1 in sorted(UPDATES.items()):
    params = json.dumps({
        'spreadsheetId': SHEET_ID,
        'range': f'{TAB}!A{row_num}',
        'valueInputOption': 'USER_ENTERED',
    })
    body = json.dumps({'values': [[menu1]]}, ensure_ascii=False)
    r = subprocess.run(
        [gws, 'sheets', 'spreadsheets', 'values', 'update', '--params', params, '--json', body],
        capture_output=True, text=True, encoding='utf-8'
    )
    if r.returncode == 0:
        ok += 1
        print(f'  A{row_num} = {menu1}  OK')
    else:
        fail += 1
        print(f'  A{row_num} = {menu1}  FAIL: {r.stderr[:60]}')

print(f'\n완료: OK={ok} / FAIL={fail}')
