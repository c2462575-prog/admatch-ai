"""Login page."""
import streamlit as st
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))
from frontend.utils.api_client import login, is_logged_in
from frontend.utils.navigation import redirect_to_dashboard

st.title("🔑 登入")

if is_logged_in():
    redirect_to_dashboard()

with st.form("login_form"):
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")
    submitted = st.form_submit_button("登入", type="primary", use_container_width=True)

if submitted:
    if not email or not password:
        st.error("請填寫所有欄位")
    else:
        try:
            login(email, password)
            redirect_to_dashboard()
        except Exception as e:
            st.error(f"登入失敗：{e}")

st.markdown("---")
st.markdown("還沒有帳號？")
if st.button("前往註冊"):
    switch("02_register.py")
