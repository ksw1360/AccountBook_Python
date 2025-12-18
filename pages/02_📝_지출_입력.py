import streamlit as st
import db_connect as db
from datetime import datetime

st.title("가로 길이 조절 테스트")
col_main, col_empty1, col_empty2 = st.columns([3, 1, 1])

now = datetime.now()
today_str = now.strftime("%Y-%m-%d")
payday_str = now.strftime("%Y-%m")

with col_main:
    # 좁아진 구역(col_main) 안에 넣으니까 가로가 줄어듦!
    values_1 = st.text_area("항목", height=100)
    values_2 = st.text_area("금액", height=100)
    values_3 = st.text_area("출처", height=100)
    values_4 = st.date_input("결제일", datetime.now())
    #    values_5 = st.text_area("작성자", "ksw1360", height=100)
    #    values_6 = st.text_area("작성일시", today_str, height=100)
    #    values_7 = st.text_area("수정자", "ksw1360", height=100)
    #    values_8 = st.text_area("수정일시", today_str, height=100)
    values_5 = st.text_area("로그인", "Admin", height=100)

# DB 저장 추가할 예정
df = db.get_data_from_db()

if df is not None and not df.empty:
    if st.button("DB에 저장하기"):
        db = db.insert_data(
            values_1,
            values_2,
            values_3,
            values_4,
            #            values_5,
            #            values_6,
            #            values_7,
            #            values_8,
            values_5,
        )
        st.success("삭제되었습니다! 🚀")
        st.switch_page("app.py")
