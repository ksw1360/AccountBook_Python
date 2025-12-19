import sqlite3
import pandas as pd
from datetime import datetime


# =========================================================
# 1. [공통] DB 연결 심부름꾼 (파일 DB라 ID/PW 필요 없음!)
# =========================================================
def get_connection():
    # 파일 이름만 적으면 끝. 없으면 알아서 만듦.
    conn = sqlite3.connect("account_book.db")
    return conn


# =========================================================
# 0. [초기화] 테이블 없으면 만들기 (SQLite는 이게 필요함)
# =========================================================
def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    # 테이블 만드는 쿼리 (SQL Server랑 거의 같음)
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS AccountBook (
            ID INTEGER PRIMARY KEY AUTOINCREMENT,
            CardName TEXT,
            Amount INTEGER,
            Item TEXT,
            PayDate TEXT,
            PayUser TEXT,
            CreateDT TEXT,
            UpdateDT TEXT
        )
    """
    )
    conn.commit()
    conn.close()


def init_db2():
    conn = get_connection()
    cursor = conn.cursor()

    # 수입 테이블 만들기
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS income (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            amount INTEGER,
            source TEXT,
            author TEXT,
            date TEXT
        )
        """
    )
    conn.commit()
    conn.close()


# 앱 실행될 때마다 테이블 있는지 확인 (맨 처음에만 실행됨)
init_db()
init_db2()


# =========================================================
# 2. 데이터 조회 (SELECT)
# =========================================================
def get_data_from_db():
    conn = get_connection()

    # FORMAT 함수가 없어서 콤마는 나중에 찍어야 함
    query = """
    SELECT ID
         , CardName
         , Amount
         , Item
         , PayDate
    FROM AccountBook
    ORDER BY PayDate DESC
    """
    df = pd.read_sql(query, conn)
    conn.close()

    # 파이썬(Pandas)에서 콤마 찍기 (더 쉬움!)
    if not df.empty:
        df["Amount2"] = df["Amount"].apply(lambda x: f"{x:,.0f}원")
    else:
        df["Amount2"] = []  # 데이터 없으면 빈 리스트

    return df


# =========================================================
# 3. 데이터 추가 (INSERT)
# =========================================================
def insert_data(card_name, amount, item, pay_date, pay_user):
    conn = get_connection()
    cursor = conn.cursor()

    now_dt = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    sql = """
    INSERT INTO AccountBook 
    (CardName, Amount, Item, PayDate, PayUser, CreateDT, UpdateDT) 
    VALUES (?, ?, ?, ?, ?, ?, ?)
    """
    # 날짜를 문자열로 변환해서 넣어야 함
    cursor.execute(
        sql, (card_name, amount, item, str(pay_date), pay_user, now_dt, now_dt)
    )
    conn.commit()
    conn.close()


# =========================================================
# 4. 데이터 수정 (UPDATE)
# =========================================================
def update_data(id_val, card_name, amount, item, pay_date, user_name):
    conn = get_connection()
    cursor = conn.cursor()

    now_dt = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    sql = """
    UPDATE AccountBook 
    SET CardName = ?, 
        Amount = ?, 
        Item = ?, 
        PayDate = ?,
        PayUser = ?,
        UpdateDT = ?
    WHERE ID = ? 
    """
    cursor.execute(
        sql, (card_name, amount, item, str(pay_date), user_name, now_dt, id_val)
    )
    conn.commit()
    conn.close()


# =========================================================
# 5. 데이터 삭제 (DELETE)
# =========================================================
def delete_data(id_val):
    conn = get_connection()
    cursor = conn.cursor()
    sql = "DELETE FROM AccountBook WHERE ID = ?"
    cursor.execute(sql, (id_val,))  # 튜플 형태 주의 (id_val,)
    conn.commit()
    conn.close()


# =========================================================
# 6. 수입 총합 함수
# =========================================================
def get_total_income():
    conn = sqlite3.connect("income.db")
    query = "SELECT SUM(amount) FROM income where date LIKE ?"
    today_str = datetime.now().strftime("%Y-%m-%d") + "%"
    total = pd.read_sql_query(query, conn, params=(today_str,)).iloc[0, 0]
    conn.close()
    return total if total is not None else 0
