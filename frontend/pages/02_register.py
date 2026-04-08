"""Register page."""
import streamlit as st
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))
from frontend.utils.api_client import register, is_logged_in
from frontend.utils.navigation import redirect_to_dashboard

st.title("📝 註冊新帳號")

if is_logged_in():
    redirect_to_dashboard()

with st.form("register_form"):
    display_name = st.text_input("顯示名稱")
    email = st.text_input("Email")
    password = st.text_input("密碼（至少 6 字元）", type="password")
    role = st.selectbox("身份", ["advertiser", "creator"], format_func=lambda x: "🏢 廣告主" if x == "advertiser" else "🎬 創作者")
    referral_code = st.text_input("邀請碼（選填）", placeholder="朋友給你的邀請碼")
    submitted = st.form_submit_button("註冊", type="primary", use_container_width=True)

if submitted:
    if not all([display_name, email, password]):
        st.error("請填寫所有欄位")
    elif len(password) < 6:
        st.error("密碼至少 6 字元")
    else:
        try:
            from frontend.utils.api_client import post
            result = post("/auth/register", {
                "email": email, "password": password, "role": role,
                "display_name": display_name, "referral_code": referral_code or None,
            })
            st.session_state["token"] = result["access_token"]
            st.session_state["user"] = result["user"]
            redirect_to_dashboard()
        except Exception as e:
            st.error(f"註冊失敗：{e}")

st.markdown("---")
st.markdown("已有帳號？")
if st.button("前往登入"):
    st.switch_page("pages/01_login.py")
