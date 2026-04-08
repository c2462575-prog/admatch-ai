"""Pricing Plans page."""
import streamlit as st
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))
from frontend.utils.api_client import is_logged_in, current_user

st.title("💎 方案與定價")
st.markdown("選擇最適合你的方案，開始高效媒合之旅")

current_plan = "free"
if is_logged_in():
    user = current_user()
    current_plan = user.get("plan", "free") if user else "free"

col1, col2, col3 = st.columns(3)

with col1:
    with st.container(border=True):
        st.markdown("### Free")
        st.markdown("**免費**")
        st.divider()
        st.markdown("- 每月 **3 次** AI 匹配")
        st.markdown("- 基礎匹配分數")
        st.markdown("- 報價計算器")
        st.markdown("- ~~AI 談判模擬~~")
        st.markdown("- ~~優先客服~~")
        if current_plan == "free":
            st.button("目前方案", disabled=True, use_container_width=True, key="free_btn")
        else:
            st.caption("基礎方案")

with col2:
    with st.container(border=True):
        st.markdown("### Basic")
        st.markdown("**¥299 / 月**")
        st.divider()
        st.markdown("- 每月 **30 次** AI 匹配")
        st.markdown("- 完整四維匹配分數")
        st.markdown("- 報價計算器")
        st.markdown("- **3 次** AI 談判模擬 / 月")
        st.markdown("- Email 客服")
        if current_plan == "basic":
            st.button("目前方案", disabled=True, use_container_width=True, key="basic_btn")
        else:
            if st.button("升級到 Basic", type="primary", use_container_width=True, key="basic_upgrade"):
                st.info("即將推出線上付款。請聯繫 admatch@example.com 手動升級。")

with col3:
    with st.container(border=True):
        st.markdown("### Pro")
        st.markdown("**¥999 / 月**")
        st.divider()
        st.markdown("- **無限次** AI 匹配")
        st.markdown("- 完整四維匹配 + AI 深度分析")
        st.markdown("- 報價計算器 + ROI 預測")
        st.markdown("- **無限次** AI 談判模擬")
        st.markdown("- 優先客服 + 專屬顧問")
        if current_plan == "pro":
            st.button("目前方案", disabled=True, use_container_width=True, key="pro_btn")
        else:
            if st.button("升級到 Pro", type="primary", use_container_width=True, key="pro_upgrade"):
                st.info("即將推出線上付款。請聯繫 admatch@example.com 手動升級。")

st.divider()
st.markdown("### 常見問題")
with st.expander("免費方案可以做什麼？"):
    st.markdown("免費方案讓你體驗核心匹配功能，每月可進行 3 次 AI 智能匹配，並使用報價計算器評估合作價值。")
with st.expander("升級後可以降級嗎？"):
    st.markdown("可以。你的方案在當月結算週期結束後會降級為免費方案，已產生的匹配和談判記錄不受影響。")
with st.expander("AI 談判模擬是什麼？"):
    st.markdown("系統會模擬廣告主、創作者和觀眾三方的 3 輪談判過程，幫你預先了解合作的可能走向和最佳策略。")
