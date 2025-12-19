# app.py (메인 페이지)
import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime

st.title("📢 나의 미니 게시판")

# DB 연결 (가계부에서 썼던 거 재활용)
conn = sqlite3.connect("board.db")
c = conn.cursor()
c.execute(
    """CREATE TABLE IF NOT EXISTS posts
             (id INTEGER PRIMARY KEY AUTOINCREMENT,
              title TEXT, content TEXT, author TEXT, date TEXT)"""
)
conn.commit()

# 글 쓰기
with st.form("write_post"):
    title = st.text_input("제목")
    content = st.text_area("내용", height=200)
    author = st.text_input("작성자")
    if st.form_submit_button("글 쓰기"):
        if title and content and author:
            c.execute(
                "INSERT INTO posts (title, content, author, date) VALUES (?, ?, ?, ?)",
                (title, content, author, datetime.now().strftime("%Y-%m-%d %H:%M")),
            )
            conn.commit()
            st.success("글 작성 완료!")
            st.rerun()
        else:
            st.error("모두 입력해주세요!")

# 글 목록
st.write("### 📋 게시글 목록")
df = pd.read_sql_query(
    "SELECT id, title, author, date FROM posts ORDER BY date DESC", conn
)
if not df.empty:
    for _, row in df.iterrows():
        with st.expander(f"**{row['title']}** - {row['author']} ({row['date']})"):
            # 상세 내용 불러오기
            c.execute("SELECT content FROM posts WHERE id=?", (row["id"],))
            content = c.fetchone()[0]
            st.write(content)
            if st.button("삭제", key=f"del_{row['id']}"):
                c.execute("DELETE FROM posts WHERE id=?", (row["id"],))
                conn.commit()
                st.success("삭제되었습니다!")
                st.rerun()
else:
    st.info("아직 작성된 글이 없어요. 첫 글을 작성해보세요!")
