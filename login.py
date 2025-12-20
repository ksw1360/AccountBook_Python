import streamlit as st
import sqlite3
import os
import time

# ---------------------------------------------------------
# 1. 초기 설정 및 DB 연결 함수
# ---------------------------------------------------------
st.set_page_config(page_title="로그인 시스템", page_icon="🔐")


def init_db():
    conn = sqlite3.connect("users.db", check_same_thread=False)
    c = conn.cursor()
    c.execute(
        """CREATE TABLE IF NOT EXISTS users
           (id INTEGER PRIMARY KEY AUTOINCREMENT, 
            username TEXT UNIQUE, password TEXT)"""
    )
    conn.commit()
    return conn, c


conn, c = init_db()

# ---------------------------------------------------------
# 2. 세션 상태(Session State) 초기화
# ---------------------------------------------------------
# 로그인 상태 확인
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False
if "username" not in st.session_state:
    st.session_state["username"] = None
# 현재 보고 있는 화면 (login 또는 signup)
if "page_mode" not in st.session_state:
    st.session_state["page_mode"] = "login"

# ---------------------------------------------------------
# 3. 화면 UI 구성
# ---------------------------------------------------------

st.title("🔐 사용자 인증 시스템")

# [A] 로그인이 된 상태라면? -> 환영 메시지와 기능 버튼 표시
if st.session_state["logged_in"]:
    st.success(f"👋 {st.session_state['username']}님, 환영합니다!")

    st.write(f"현재 사용자 ID (Sequence): {st.session_state.get('user_id')}")

    col1, col2 = st.columns(2)

    with col1:
        # 수정하기 버튼
        if st.button("✏️ 수정하기 (메인 앱으로 이동)"):
            # 이동할 파일명 (같은 폴더에 app.py가 있어야 함, 혹은 pages/ 폴더 내부 파일)
            target_page = "app.py"
            script_dir = os.path.dirname(os.path.abspath(target_page))

            st.write(f"이동할 파일 경로: {script_dir+'/pages/'+target_page}")
            # 파일 존재 여부 확인 (에러 방지용)
            if os.path.exists(script_dir + "/pages/" + target_page):
                st.write("파일이 존재합니다. 페이지를 이동합니다...")

                st.switch_page(script_dir + "/pages/" + target_page)
                # st.switch_page("pages/app.py")
            else:
                st.error(
                    f"❌ 이동하려는 '{script_dir+'/pages/'+target_page}' 파일을 찾을 수 없습니다.",
                    st.write("script_dir:", script_dir),
                )

    with col2:
        # 로그아웃 버튼
        if st.button("🚪 로그아웃"):
            st.session_state["logged_in"] = False
            st.session_state["username"] = None
            st.rerun()  # 화면 즉시 새로고침

# [B] 로그인이 안 된 상태라면? -> 로그인 또는 회원가입 폼 표시
else:
    # 탭이나 버튼으로 모드 전환이 가능하지만, 요청하신 대로 버튼으로 모드 전환 구현
    if st.session_state["page_mode"] == "login":
        st.subheader("로그인")

        with st.form("login_form"):
            username = st.text_input("사용자 이름")
            password = st.text_input("비밀번호", type="password")
            submit = st.form_submit_button("로그인")

            if submit:
                c.execute(
                    "SELECT * FROM users WHERE username = ? AND password = ?",
                    (username, password),
                )
                user = c.fetchone()

                if user:
                    # 로그인 성공 시 세션에 정보 저장
                    st.session_state["logged_in"] = True
                    st.session_state["username"] = username
                    st.session_state["user_id"] = user[0]  # DB의 ID값
                    st.session_state["selected_login_seq"] = user[0]
                    st.success("로그인 성공! 잠시만 기다려주세요...")
                    time.sleep(1)
                    st.rerun()  # 중요: 화면을 다시 그려서 '로그인 된 화면'인 [A]로 이동
                    # 로그인 성공시 메인화면으로 이동
                    st.switch_page("pages/app.py")  # app.py로 이동
                else:
                    st.error("사용자 이름 또는 비밀번호가 올바르지 않습니다.")

        st.markdown("---")
        st.info("계정이 없으신가요?")
        if st.button("📝 회원가입 하러 가기"):
            st.session_state["page_mode"] = "signup"
            st.rerun()

    elif st.session_state["page_mode"] == "signup":
        st.subheader("회원가입")

        with st.form("signup_form"):
            new_username = st.text_input("새 사용자 이름")
            new_password = st.text_input("새 비밀번호", type="password")
            new_password_confirm = st.text_input("비밀번호 확인", type="password")
            signup_submit = st.form_submit_button("회원가입 완료")

            if signup_submit:
                if new_username and new_password:
                    if new_password != new_password_confirm:
                        st.error("비밀번호가 일치하지 않습니다.")
                    else:
                        try:
                            c.execute(
                                "INSERT INTO users (username, password) VALUES (?, ?)",
                                (new_username, new_password),
                            )
                            conn.commit()
                            st.success("가입 완료! 이제 로그인해주세요.")
                            time.sleep(1.5)
                            st.session_state["page_mode"] = (
                                "login"  # 로그인 화면으로 전환
                            )
                            st.rerun()
                        except sqlite3.IntegrityError:
                            st.error("이미 존재하는 사용자 이름입니다.")
                else:
                    st.warning("모든 필드를 입력해주세요.")

        st.markdown("---")
        if st.button("🔙 로그인 화면으로 돌아가기"):
            st.session_state["page_mode"] = "login"
            st.rerun()
