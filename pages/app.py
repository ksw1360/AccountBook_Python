import time
import streamlit as st
import db_connect as db
import pandas as pd
from openpyxl import Workbook
from openpyxl.chart import BarChart, Reference
from openpyxl.utils.dataframe import dataframe_to_rows
from io import BytesIO

# ----------------------------- 페이지 설정 -----------------------------
st.set_page_config(page_title="우리집 가계부", page_icon="💰", layout="wide")
st.title("💰 우리집 가계부 Pro")

# ----------------------------- 데이터 로드 -----------------------------
try:
    df = db.get_data_from_db()  # 전체 데이터 가져오기

    if df.empty:
        st.warning("아직 등록된 지출 내역이 없습니다!")
        # 데이터가 없어도 메뉴는 나와야 하므로 st.stop()은 보류하거나 메뉴 아래로 이동

    # ----------------------------- 사이드바 설정 -----------------------------
    st.sidebar.title("🔧 설정")

    # 데이터가 있을 때만 필터링 로직 수행
    if not df.empty:
        # 카드 선택 멀티셀렉트
        card_list = sorted(df["CardName"].unique())
        selected_cards = st.sidebar.multiselect(
            "확인하고 싶은 카드를 선택하세요", card_list, default=card_list
        )
        # 데이터 필터링
        filtered_df = df[df["CardName"].isin(selected_cards)][["CardName", "Amount"]]
    else:
        filtered_df = pd.DataFrame()
        selected_cards = []

    # ----------------------------- 엑셀 + 차트 생성 함수 -----------------------------
    def to_excel_with_chart(data_df: pd.DataFrame) -> bytes:
        if data_df.empty:
            return None
        wb = Workbook()
        ws = wb.active
        ws.title = "카드별 지출"
        for row in dataframe_to_rows(data_df, index=False, header=True):
            ws.append(row)
        chart = BarChart()
        chart.title = "카드별 지출 금액"
        chart.style = 10
        chart.type = "col"
        chart.y_axis.title = "금액 (원)"
        chart.x_axis.title = "카드 이름"
        data_range = Reference(
            ws, min_col=2, min_row=1, max_col=2, max_row=len(data_df) + 1
        )
        categories = Reference(ws, min_col=1, min_row=2, max_row=len(data_df) + 1)
        chart.add_data(data_range, titles_from_data=True)
        chart.set_categories(categories)
        ws.add_chart(chart, "E2")
        output = BytesIO()
        wb.save(output)
        output.seek(0)
        return output.getvalue()

    # ----------------------------- 메인 화면 -----------------------------
    col1, col2 = st.columns([1, 2])

    with col1:
        st.write("### 📊 지출 요약")
        if not filtered_df.empty:
            total_amount = filtered_df["Amount"].sum()
            income_total = db.get_total_income()
            st.metric("총 수입", f"{income_total:,} 원")
            rest_amount = income_total - total_amount
            st.metric("남은 금액", f"{rest_amount:,} 원")
            st.metric("선택된 카드 총 지출", f"{total_amount:,} 원")
        else:
            st.info("데이터가 없습니다.")

    with col2:
        st.write("### 💳 카드별 지출 그래프")
        if not filtered_df.empty:
            st.bar_chart(filtered_df, x="CardName", y="Amount")

    st.divider()

    # ----------------------------- 상세 내역 및 수정/삭제 -----------------------------
    # 변수 초기화 (에러 방지용)
    selected_seq = None

    if st.sidebar.checkbox("상세 내역 표 보기", value=True):
        st.write("### 📋 상세 내역")
        st.dataframe(filtered_df, use_container_width=True)

        st.write("### 🛠️ 내역 수정 / 삭제")

        if not filtered_df.empty:
            display_options = (
                df[df["CardName"].isin(selected_cards)]["ID"].astype(str)
                + ". "
                + df["Item"]
                + " ("
                + df["Amount"].astype(str)
                + "원)"
            )

            option = st.selectbox("수정/삭제할 내역 선택", display_options)
            if option:
                selected_seq = int(option.split(".")[0])

            col_btn1, col_btn2 = st.columns(2)

            # [수정 포인트 1] switch_page 경로 단순화
            with col_btn1:
                if st.button("✏️ 수정하기"):
                    st.session_state["edit_seq"] = selected_seq
                    st.switch_page("pages/03_✏️_수정하기.py")

            with col_btn2:
                if st.button("🗑️ 삭제하기"):
                    st.session_state["delete_seq"] = selected_seq
                    st.switch_page("pages/04_🗑️_삭제하기.py")

    # ----------------------------- 엑셀 다운로드 (사이드바) -----------------------------
    st.sidebar.divider()
    st.sidebar.write("💾 **보고서 다운로드**")
    if not filtered_df.empty:
        excel_data = to_excel_with_chart(filtered_df)
        if excel_data:
            st.sidebar.download_button(
                label="📊 엑셀 다운로드 (차트 포함)",
                data=excel_data,
                file_name="우리집가계부_보고서.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            )

    # ----------------------------- 네비게이션 링크 (사이드바) -----------------------------
    st.sidebar.divider()

    # [수정 포인트 2] page_link 경로 단순화 (pages/파일명.py)
    # 주의: app.py가 pages 폴더 안에 있다면 "pages/app.py"라고 적어야 합니다.
    # if st.session_state["logged_in"] is not True:
    #     st.error("로그인이 필요합니다. 로그인 페이지로 이동합니다.")
    #     st.switch_page("login.py")
    # [1] 로그인 상태 확인 및 강제 이동 (보안)
    # 로그인이 안 되어 있는데 이 페이지에 들어왔다면? -> 내쫓기
    if "logged_in" not in st.session_state or not st.session_state["logged_in"]:
        st.warning("로그인이 필요합니다. 로그인 페이지로 이동합니다...")
        time.sleep(1)
        st.switch_page("login.py")  # login.py가 메인 루트에 있다면
        st.stop()  # 아래 코드 실행 중지

    st.write(st.session_state)
    # [3] 로그인 상태에 따라 다르게 보여주기
    if st.session_state.get("logged_in"):
        # 로그인 상태라면 -> '로그아웃 버튼' 보여주기
        # 버튼을 누르면 세션을 지우고 로그인 화면으로 보냄
        if st.sidebar.button("🚪 로그아웃"):
            st.session_state["logged_in"] = False
            st.session_state["username"] = None
            st.rerun()  # 화면을 새로고침하면 위의 [1]번 보안 코드에 걸려서 자동으로 login.py로 튕겨 나감
    else:
        # 로그인 안 된 상태라면 -> '로그인 링크' 보여주기
        st.sidebar.page_link("login.py", label="🔐 로그인", icon="🔐")

    st.sidebar.page_link("pages/app.py", label="🏠 홈", icon="🏠")

    st.sidebar.page_link("pages/02_📝_지출_입력.py", label="➕ 지출입력", icon="📝")

    # 선택된 값이 있을 때만 세션에 저장 (에러 방지)
    if selected_seq is not None:
        st.session_state["edit_seq"] = selected_seq
        st.session_state["delete_seq"] = selected_seq

    st.sidebar.page_link("pages/03_✏️_수정하기.py", label="✏️ 지출 수정", icon="✏️")
    st.sidebar.page_link("pages/04_🗑️_삭제하기.py", label="🗑️ 지출 삭제", icon="🗑️")
    st.sidebar.page_link("pages/board.py", label="📢 미니 게시판", icon="📢")
    st.sidebar.page_link("pages/05_🎁_수입입력.py", label="🎁 수입 입력", icon="🎁")
    st.sidebar.page_link("pages/readexcel.py", label="📈 Excel 입력", icon="📈")

    # 로그인 페이지는 메인 폴더(상위)에 있다면 경로가 다를 수 있습니다.
    # 만약 login.py가 메인 폴더에 있다면 "../login.py"는 안됩니다.
    # login.py가 메인 실행 파일이라면 switch_page로 돌아가기 까다롭습니다.
    # 보통 pages 안에 login.py도 같이 넣거나, 로그아웃 시 메인으로 튕기게 합니다.

    if st.sidebar.button("🔐 로그아웃"):
        st.session_state["logged_in"] = False
        st.switch_page(
            "login.py"
        )  # login.py가 메인 루트에 있다면 이렇게, 안되면 pages/login.py

except Exception as e:
    st.error(f"앗! 오류가 발생했어요: {e}")
    st.info("DB 연결이나 데이터 로드에 문제가 있을 수 있어요.")
    st.stop()
