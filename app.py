import streamlit as st
import db_connect as db
import pandas as pd
import io
import subprocess

st.set_page_config(page_title="우리집 가계부", page_icon="💰", layout="wide")

# 제목
st.title("💰 우리집 가계부 Pro")

try:
    # -------------------------------------------------------
    # 1. 엑셀 변환 함수 (기능 정의는 맨 위에 하는 게 안전합니다)
    # -------------------------------------------------------
    def to_excel_with_chart(df):
        output = io.BytesIO()
        # 엑셀 엔진 설정 (xlsxwriter 설치 필수!)
        writer = pd.ExcelWriter(output, engine="xlsxwriter")

        # 데이터 붙여넣기
        df.to_excel(writer, index=False, sheet_name="Sheet1")

        # 차트 그리기 준비
        workbook = writer.book
        worksheet = writer.sheets["Sheet1"]
        chart = workbook.add_chart({"type": "column"})

        # 데이터 개수 세기 (데이터가 없으면 0)
        max_row = len(df)

        # 데이터가 있을 때만 차트 설정 (에러 방지)
        if max_row > 0:
            chart.add_series(
                {
                    "categories": ["Sheet1", 1, 0, max_row, 0],
                    "values": ["Sheet1", 1, 1, max_row, 1],
                    "name": "카드별 지출 금액",
                }
            )
            # 차트 위치 설정
            worksheet.insert_chart("A9", chart)

        writer.close()
        return output.getvalue()

    # -------------------------------------------------------
    # 2. 데이터 가져오기 & 사이드바 설정
    # -------------------------------------------------------
    df = db.get_data_from_db()

    st.sidebar.title("🔧 설정")

    # 필터
    card_list = df["CardName"].unique()
    selected_cards = st.sidebar.multiselect(
        "확인하고 싶은 카드를 고르세요", card_list, default=card_list
    )

    # 데이터 필터링
    filtered_df = df[df["CardName"].isin(selected_cards)]

    # -------------------------------------------------------
    # 3. 메인 화면 그리기
    # -------------------------------------------------------
    col1, col2 = st.columns([1, 2])

    with col1:
        st.write("### 📊 지출 요약")
        total_money = filtered_df["Amount"].sum()
        st.metric(label="선택된 카드 합계", value=f"{total_money:,}원")

    with col2:
        st.write("### 💳 지출 그래프")
        st.bar_chart(filtered_df, x="CardName", y="Amount")

    st.write("---")

    if st.sidebar.checkbox("상세 내역 표 보기", value=True):
        st.write("### 📋 상세 내역")
        st.dataframe(filtered_df, use_container_width=True)

        st.write("### 🛠️ 내역 수정하기 ###")

        if not df.empty:
            option = st.selectbox(
                "수정/삭제할 내역을 선택하세요",
                df["ID"].astype(str) + ". " + df["Item"] + " (" + df["Amount"] + ")",
            )

            if option:
                selected_seq = option.split(".")[0]

                # 버튼들을 예쁘게 가로로 배치
                col1, col2 = st.columns(2)

                with col1:
                    if st.button("✏️ 수정하러 가기"):
                        st.session_state["edit_seq"] = selected_id
                        st.switch_page("pages/03_✏️_수정하기.py")

                with col2:
                    if st.button("🗑️ 삭제하러 가기"):
                        st.session_state["delete_seq"] = selected_id
                        st.switch_page("pages/04_🗑️_내역_삭제.py")
            else:
                st.info(
                    "💡 아직 등록된 지출 내역이 없습니다. 왼쪽 사이드바에서 추가해주세요!"
                )

        # option = st.selectbox(
        #     "수정할 내역을 선택하세요",
        #     df["ID"].astype(str)
        #     + "."
        #     + df["Item"]
        #     + "("
        #     + df["Amount"].astype(str)
        #     + ")",
        # )

        # selected_seq = option.split(".")[0]

        # if st.button("✏️ 수정하러 가기"):
        #     st.write("selected_seq" + selected_seq)
        #     st.session_state["edit_seq"] = selected_seq

        #     st.switch_page("pages/03_✏️_수정하기.py")

        # if st.button(" 삭제하러 가기"):
        #     st.write("delete_seq" + selected_seq)
        #     st.session_state["delete_seq"] = selected_seq

        #     st.switch_page("pages/04_🗑️_삭제하기.py")

    # -------------------------------------------------------
    # 4. 다운로드 버튼 (★여기가 문제였을 수 있음!)
    # -------------------------------------------------------
    st.sidebar.write("---")
    st.sidebar.write("💾 **고급 보고서 다운로드**")

    # 함수 실행해서 데이터 받기
    excel_data = to_excel_with_chart(filtered_df)

    # 버튼 만들기 (들여쓰기 주의: if문이나 함수 안에 들어가면 안 됨)
    st.sidebar.download_button(
        label="📊 엑셀 파일 다운로드 (차트 포함)",
        data=excel_data,
        file_name="가계부_보고서_차트포함.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )

    st.title("메인 대시보드")

    with st.sidebar:
        st.header("지출입력")
        st.write("---")  # 구분선

    # 여기 안에서는 .sidebar 안 붙여도 알아서 들어갑니다
    st.page_link("app.py", label="🏠 홈으로", icon="🏠")
    st.page_link("pages/02_📝_지출_입력.py", label="➕ 지출 입력", icon="📝")
#    st.page_link("pages/edit.py", label="지출 수정", icon="📝")

# st.sidebar.download_button(
#    label="지출입력",
#    st.page_link("pages/add.py", label="➕ 지출 입력하러 가기", icon="📝")
# )


except Exception as e:
    st.error(f"에러가 발생했습니다 ㅠㅠ: {e}")
