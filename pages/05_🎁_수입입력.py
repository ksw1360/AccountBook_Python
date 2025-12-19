import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime

st.title("🎁 수입입력")

# DB 연결
conn = sqlite3.connect("income.db")
c = conn.cursor()
c.execute(
    """CREATE TABLE IF NOT EXISTS income
             (id INTEGER PRIMARY KEY AUTOINCREMENT, 
             title Text, amount INTEGER, source TEXT, author TEXT, date TEXT)"""
)
conn.commit()

# 수입 입력 폼
with st.form("income_form"):
    title = st.text_input("수입 제목")
    amount = st.number_input("수입 금액", min_value=0, step=1000)
    source = st.text_input("수입 출처")
    author = st.text_input("작성자")
    if st.form_submit_button("수입 입력"):
        if title and amount > 0 and source and author:
            c.execute(
                "INSERT INTO income (title, amount, source, author, date) VALUES (?, ?, ?, ?, ?)",
                (
                    title,
                    amount,
                    source,
                    author,
                    datetime.now().strftime("%Y-%m-%d %H:%M"),
                ),
            )
            conn.commit()
            st.success("수입이 성공적으로 입력되었습니다!")
            st.rerun()
        else:
            st.error("모든 필드를 올바르게 입력해주세요.")
# 수입 내역 표시
st.write("### 📋 수입 내역")
df = pd.read_sql_query(
    "SELECT id, title, amount, source, author, date FROM income ORDER BY date DESC",
    conn,
)
if not df.empty:
    st.dataframe(df)
else:
    st.info("아직 입력된 수입 내역이 없습니다.")
