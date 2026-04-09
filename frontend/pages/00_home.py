"""Home / Landing page."""
import streamlit as st
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))
from frontend.utils.api_client import is_logged_in, current_user, logout
from frontend.utils.navigation import switch

st.title("🎯 AdMatch AI")
st.subheader("AI 驅動的網紅行銷媒合平台")

st.markdown("用 AI 自動完成：**匹配推薦** → **價值評估** → **談判模擬** → **合約建議**")

# Platform stats - 2x2 grid (better for mobile)
try:
    from frontend.utils.api_client import get
    stats = get("/stats/platform")
    r1c1, r1c2 = st.columns(2)
    with r1c1:
        st.metric("🏢 廣告主", stats.get("total_advertisers", 0))
    with r1c2:
        st.metric("🎬 創作者", stats.get("total_creators", 0))
    r2c1, r2c2 = st.columns(2)
    with r2c1:
        st.metric("🤝 匹配次數", stats.get("total_matches", 0))
    with r2c2:
        st.metric("✅ 成功合作", stats.get("successful_negotiations", 0))
except Exception:
    pass

st.divider()

# Features - stacked cards (mobile-friendly)
with st.container(border=True):
    st.markdown("**🔍 智能匹配** — 多維度 AI 分析，找到最合適的合作夥伴")
with st.container(border=True):
    st.markdown("**💬 談判模擬** — AI 輔助 3 輪談判，包含觀眾反饋評分")
with st.container(border=True):
    st.markdown("**📊 數據驅動** — Embedding + 預算 + 價值觀 + 受眾 四維評分")

st.divider()

if is_logged_in():
    user = current_user()
    st.success(f"已登入：{user['display_name']} ({user['role']})")
    if user["role"] == "advertiser":
        st.button("前往儀表板", type="primary", use_container_width=True, on_click=lambda: switch("10_advertiser_dashboard.py"))
    else:
        st.button("前往儀表板", type="primary", use_container_width=True, on_click=lambda: switch("20_creator_dashboard.py"))
    if st.button("登出", use_container_width=True):
        logout()
        st.rerun()
else:
    st.info("立即註冊，開始 AI 媒合之旅")
    if st.button("🏢 我是廣告主", type="primary", use_container_width=True):
        switch("02_register.py")
    if st.button("🎬 我是創作者", use_container_width=True):
        switch("02_register.py")

st.divider()
with st.expander("💡 運作流程", expanded=False):
    st.markdown("""
1. **註冊帳號** — 選擇廣告主或創作者身份
2. **填寫資料** — 品牌/頻道資料、預算/報價、合作偏好
3. **AI 分析** — 系統自動生成 profile 並計算 embedding
4. **智能匹配** — 四維度加權評分，找到最佳配對
5. **談判模擬** — 3 輪 AI 談判 + 觀眾反饋評分
6. **達成合作** — 雙方同意後生成合約建議
    """)
