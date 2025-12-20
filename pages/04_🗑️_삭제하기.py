import streamlit as st
import db_connect as db
from datetime import datetime
import pandas as pd

st.title("✏️ 지출 내역 수정")

try:
    if "delete_seq" not in st.session_state:
        st.error("잘못된 접근입니다. 대시보드에서 선택해주세요.")
        st.stop()

    ID = st.session_state["delete_seq"]
    st.write(f"삭제할 번호표: **{ID}번")

    df = db.get_data_from_db()
    target_row = df[df["ID"] == int(ID)].iloc[0]

    with st.form("delete_form"):
        # del_seq = st.number_input("ID", value=target_row["ID"])
        st.write(f"### ⚠️ 정말 삭제하시겠습니까?")
        st.write(f"내역: **{target_row['Item']}**")
        st.write(f"금액: **{target_row['Amount2']}**")

        if st.form_submit_button("삭제 완료"):
            db.delete_data(ID)
            st.success("삭제되었습니다! 🚀")
            st.switch_page("pages/app.py")


except Exception as e:
    st.error(f"에러가 발생했습니다 ㅠㅠ: {e}")
