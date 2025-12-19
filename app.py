import streamlit as st
import db_connect as db
import pandas as pd
from openpyxl import Workbook
from openpyxl.chart import BarChart, Reference
from openpyxl.utils.dataframe import dataframe_to_rows
from io import BytesIO
import os
import sys

# ----------------------------- 페이지 설정 -----------------------------
st.set_page_config(page_title="우리집 가계부", page_icon="💰", layout="wide")
st.title("💰 우리집 가계부 Pro")

# ----------------------------- 데이터 로드 -----------------------------
try:
    df = db.get_data_from_db()  # 전체 데이터 가져오기

    if df.empty:
        st.warning("아직 등록된 지출 내역이 없습니다!")
        st.stop()

    # ----------------------------- 사이드바 설정 -----------------------------
    st.sidebar.title("🔧 설정")

    # 카드 선택 멀티셀렉트
    card_list = sorted(df["CardName"].unique())
    selected_cards = st.sidebar.multiselect(
        "확인하고 싶은 카드를 선택하세요", card_list, default=card_list
    )

    # 데이터 필터링 (CardName + Amount만 사용)
    filtered_df = df[df["CardName"].isin(selected_cards)][["CardName", "Amount"]]

    # ----------------------------- 엑셀 + 차트 생성 함수 -----------------------------
    def to_excel_with_chart(data_df: pd.DataFrame) -> bytes:
        if data_df.empty:
            st.warning("선택된 데이터가 없습니다. 엑셀 파일을 생성할 수 없어요.")
            return None

        wb = Workbook()
        ws = wb.active
        ws.title = "카드별 지출"

        # 데이터 쓰기
        for row in dataframe_to_rows(data_df, index=False, header=True):
            ws.append(row)

        # 막대 차트 생성
        chart = BarChart()
        chart.title = "카드별 지출 금액"
        chart.style = 10
        chart.type = "col"  # 세로 막대
        chart.y_axis.title = "금액 (원)"
        chart.x_axis.title = "카드 이름"

        # 데이터 범위 설정 (filtered_df 기준으로 동적으로!)
        data_range = Reference(
            ws, min_col=2, min_row=1, max_col=2, max_row=len(data_df) + 1
        )
        categories = Reference(ws, min_col=1, min_row=2, max_row=len(data_df) + 1)

        chart.add_data(data_range, titles_from_data=True)
        chart.set_categories(categories)
        ws.add_chart(chart, "E2")

        # BytesIO로 저장
        output = BytesIO()
        wb.save(output)
        output.seek(0)
        return output.getvalue()

    # ----------------------------- 메인 화면 -----------------------------
    col1, col2 = st.columns([1, 2])

    with col1:
        st.write("### 📊 지출 요약")
        total_amount = filtered_df["Amount"].sum()
        # income_total = db.get_total_income()  # 총 수입 가져오기
        income_total = db.get_total_income()  # 총 수입 가져오기
        st.metric("총 수입", f"{income_total:,} 원")
        rest_amount = income_total - total_amount
        st.metric("남은 금액", f"{rest_amount:,} 원")
        st.metric("선택된 카드 총 지출", f"{total_amount:,} 원")

    with col2:
        st.write("### 💳 카드별 지출 그래프")
        st.bar_chart(filtered_df, x="CardName", y="Amount")

    st.divider()

    # ----------------------------- 상세 내역 및 수정/삭제 -----------------------------
    if st.sidebar.checkbox("상세 내역 표 보기", value=True):
        st.write("### 📋 상세 내역")
        st.dataframe(filtered_df, use_container_width=True)

        st.write("### 🛠️ 내역 수정 / 삭제")

        if not filtered_df.empty:
            # 전체 df에서 ID 기반으로 선택 옵션 만들기 (필터링된 것만 보여주기 위해)
            display_options = (
                df[df["CardName"].isin(selected_cards)]["ID"].astype(str)
                + ". "
                + df["Item"]
                + " ("
                + df["Amount"].astype(str)
                + "원)"
            )

            option = st.selectbox("수정/삭제할 내역 선택", display_options)
            selected_seq = int(
                option.split(".")[0]
            )  # selected_id 대신 selected_seq로 통일

            col_btn1, col_btn2 = st.columns(2)
            script_dir = os.path.dirname(os.path.abspath(__file__))

            with col_btn1:
                if st.button("✏️ 수정하기"):
                    st.session_state["edit_seq"] = selected_seq  # 여기서 설정!
                    st.switch_page(
                        os.path.join(script_dir, "pages", "03_✏️_수정하기.py")
                    )

            with col_btn2:
                if st.button("🗑️ 삭제하기"):
                    st.session_state["delete_seq"] = selected_seq  # 여기서 설정!
                    st.switch_page(
                        os.path.join(script_dir, "pages", "04_🗑️_삭제하기.py")
                    )

    # ----------------------------- 엑셀 다운로드 버튼 (사이드바) -----------------------------
    st.sidebar.divider()
    st.sidebar.write("💾 **보고서 다운로드**")

    excel_data = to_excel_with_chart(filtered_df)

    if excel_data:
        st.sidebar.download_button(
            label="📊 엑셀 다운로드 (차트 포함)",
            data=excel_data,
            file_name="우리집가계부_보고서.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )

    # ----------------------------- 네비게이션 링크 (사이드바 하단) -----------------------------
    st.sidebar.divider()
    st.sidebar.page_link("app.py", label="🏠 홈", icon="🏠")
    st.sidebar.page_link(
        os.path.join(script_dir, "pages", "02_📝_지출_입력.py"),
        label="➕ 지출 입력",
        icon="📝",
    )
    st.session_state["edit_seq"] = selected_seq  # 여기서 설정!
    st.sidebar.page_link(
        os.path.join(script_dir, "pages", "03_✏️_수정하기.py"),
        label="✏️ 지출 수정",
        icon="✏️",
    )
    st.session_state["delete_seq"] = selected_seq  # 여기서 설정!
    st.sidebar.page_link(
        os.path.join(script_dir, "pages", "04_🗑️_삭제하기.py"),
        label="🗑️ 지출 삭제",
        icon="🗑️",
    )
    st.sidebar.page_link(
        os.path.join(script_dir, "pages", "board.py"), label="📢 미니 게시판", icon="📢"
    )
    st.sidebar.page_link(
        os.path.join(script_dir, "pages", "05_🎁_수입입력.py"),
        label="🎁 수입 입력",
        icon="🎁",
    )

except Exception as e:
    st.error(f"앗! 오류가 발생했어요: {e}")
    st.info("DB 연결이나 데이터 로드에 문제가 있을 수 있어요. 확인해보세요!")
