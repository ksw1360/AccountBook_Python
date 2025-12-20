import streamlit as st
import pandas as pd  # turtle이 아니라 pandas입니다!
import os
from db_connect import insert_data
from datetime import datetime

st.set_page_config(page_title="Excel 입력", page_icon="📗")

st.title("📗 Excel 파일 읽기 및 DB 저장")

# 1. 파일 경로 설정
file_name = "excel/우리집가계부_보고서.xlsx"

# 2. 파일 존재 여부 확인
if os.path.exists(file_name):
    st.success(f"📂 파일을 찾았습니다: {file_name}")
else:
    st.error(f"❌ 파일을 찾을 수 없습니다: {file_name}")
    st.info("먼저 '지출 입력' 페이지에서 엑셀 파일을 생성해주세요.")
    st.stop()

# 3. 엑셀 파일 읽기
try:
    df = pd.read_excel(file_name, sheet_name="카드별 지출")
    st.subheader("📋 엑셀 데이터 미리보기")
    st.dataframe(df)
except Exception as e:
    st.error(f"엑셀 파일을 읽는 중 오류가 발생했습니다: {e}")
    st.stop()

# 4. 데이터 저장 로직
if not df.empty:
    # 로그인 사용자 확인 (안전하게 가져오기)
    current_username = st.session_state.get("username", "unknown_user")

    st.write(f"현재 사용자: **{current_username}**")

    now_dt = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    if st.button("💾 DB에 저장하기"):
        success_count = 0
        error_count = 0

        # 진행률 표시바
        progress_bar = st.progress(0)
        total_rows = len(df)

        for index, row in df.iterrows():
            try:
                # 엑셀에 없는 컬럼은 기본값 처리 (KeyError 방지)
                card_name = row.get("CardName", "알수없음")
                amount = row.get("Amount", 0)
                item = row.get("Item", "엑셀불러오기")  # 컬럼 없으면 기본값 사용
                pay_date = row.get("PayDate", "2024-01")  # 날짜 없으면 임시 날짜
                # insert_data 함수 호출 (순서 주의: db_connect.py의 정의 순서와 맞춰야 함)
                # 예시: username, date, category, item, amount, card_name, memo
                insert_data(
                    card_name,
                    amount,  # current_username,  # username
                    item,
                    pay_date,  # pay_date,  # date
                    current_username,  # "기타",  # category (엑셀에 없으므로 고정)
                    # now_dt,  # item,  # item
                    # now_dt,  # amount,  # amount
                )
                success_count += 1
                st.write(
                    f"✅ {index + 1}/{total_rows} 행 저장 성공: {card_name}, {amount}원"
                )
            except Exception as e:
                st.write(f"에러 발생: {e}")  # 디버깅용
                error_count += 1

            # 진행률 업데이트
            progress_bar.progress((index + 1) / total_rows)

        # 결과 출력 (루프 밖에서 한 번만)
        if error_count == 0:
            st.success(f"✅ 총 {success_count}건의 데이터가 성공적으로 저장되었습니다!")
        else:
            st.warning(f"⚠️ {success_count}건 저장 성공, {error_count}건 실패.")

        # 페이지 새로고침 (데이터 반영 확인용)
        # st.rerun()
