import sys, pymysql
sys.path.insert(0, r'E:\Tomes-AutoTest')

conn = pymysql.connect(
    host='121.165.20.66', port=3306,
    user='tomes', password='jmes!20191107',
    database='smd', charset='utf8mb4'
)
cur = conn.cursor()

# 1depth(PARENT=0) + 2depth 메뉴명 계층 구조
cur.execute("""
    SELECT p.MENU_SEQ, pl.MENU_NM as depth1_nm,
           c.MENU_SEQ as child_seq, cl.MENU_NM as depth2_nm,
           c.SORT_NUM
    FROM TBL_BASIC_MENU p
    JOIN TBL_BASIC_MENU_LANG pl ON p.MENU_SEQ = pl.MENU_SEQ AND pl.LANG_CD='KR'
    JOIN TBL_BASIC_MENU c ON c.PARENT_MENU_SEQ = p.MENU_SEQ
    JOIN TBL_BASIC_MENU_LANG cl ON c.MENU_SEQ = cl.MENU_SEQ AND cl.LANG_CD='KR'
    WHERE p.PARENT_MENU_SEQ = 0 AND p.USE_YN='Y' AND p.DEL_YN='N'
    ORDER BY p.SORT_NUM, c.SORT_NUM
""")
rows = cur.fetchall()

with open(r'E:\harness_framework\logs\menu_db.txt', 'w', encoding='utf-8') as f:
    for r in rows:
        f.write(f'{r[1]:15s}  >  {r[3]}\n')

conn.close()
print(f'done: {len(rows)}건')
