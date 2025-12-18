import streamlit as st
import db_connect as db
from datetime import datetime
import pandas as pd

st.title("✏️ 지출 내역 수정")
st.write("1")

try:
    st.write("2")
    st.write(st.session_state)
    # 1. 짐 풀기 (가져온 ID 확인)
    if "edit_seq" not in st.session_state:
        st.error("잘못된 접근입니다. 대시보드에서 선택해주세요.")
        st.stop()

    ID = st.session_state["edit_seq"]
    st.write(f"수정할 번호표: **{ID}번**")

    # -----------------------------------------------
    # [핵심] 기존 데이터 가져와서 칸 채워두기
    # -----------------------------------------------
    # (편의상 전체 다 가져와서 필터링하는 방식.
    #  나중엔 SELECT * FROM ... WHERE ID=? 로 하는 게 정석입니다)
    df = db.get_data_from_db()
    target_row = df[df["ID"] == int(ID)].iloc[0]  # 딱 그 한 줄만 뽑기!

    # 2. 입력창에 기존 값(value) 넣어주기
    with st.form("edit_form"):
        new_card = st.text_input("카드 이름", value=target_row["CardName"])
        new_amount = st.number_input("금액", value=target_row["Amount"], step=1000)
        new_item = st.text_input("내역", value=target_row["Item"])

        # 날짜 처리 (DB에서 가져온 건 문자열일 수도 있어서 변환 필요)
        # 일단 오늘 날짜로 기본값 설정 (기존 날짜 넣으려면 변환 로직 필요)
        new_date = st.date_input("결제일", datetime.now())
        new_user = st.text_input(
            "사용자", value="김상우"
        )  # DB에 있으면 value=target_row['PayUser']

        # 3. 진짜 수정 버튼
        if st.form_submit_button("수정 완료"):
            db.update_data(ID, new_card, new_amount, new_item, new_date, new_user)
            st.success("수정되었습니다! 🚀")

            # 다시 대시보드로 복귀
            st.switch_page("app.py")

except Exception as e:
    st.error(f"에러가 발생했습니다 ㅠㅠ: {e}")
