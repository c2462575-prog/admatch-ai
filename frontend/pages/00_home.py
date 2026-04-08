"""Home / Landing page."""
import streamlit as st
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))
from frontend.utils.api_client import is_logged_in, current_user, logout

st.title("🎯 AdMatch AI")
st.subheader("AI 驅動的網紅行銷媒合平台")

st.markdown("""
用 AI 自動完成：**匹配推薦** → **價值評估** → **談判模擬** → **合約建議**
""")

# Platform stats - social proof
try:
    from frontend.utils.api_client import get
    stats = get("/stats/platform")
    s1, s2, s3, s4 = st.columns(4)
    with s1:
        st.metric("廣告主", stats.get("total_advertisers", 0))
    with s2:
        st.metric("創作者", stats.get("total_creators", 0))
    with s3:
        st.metric("匹配次數", stats.get("total_matches", 0))
    with s4:
        st.metric("成功合作", stats.get("successful_negotiations", 0))
except Exception:
    pass

st.divider()

col1, col2, col3 = st.columns(3)
with col1:
    st.markdown("### 🔍 智能匹配")
    st.markdown("多維度 AI 分析，找到最合適的合作夥伴")
with col2:
    st.markdown("### 💬 談判模擬")
    st.markdown("AI 輔助 3 輪談判，包含觀眾反饋評分")
with col3:
    st.markdown("### 📊 數據驅動")
    st.markdown("Embedding + 預算 + 價值觀 + 受眾 四維評分")

st.divider()

if is_logged_in():
    user = current_user()
    st.success(f"已登入：{user['display_name']} ({user['role']})")
    col1, col2 = st.columns(2)
    with col1:
        if user["role"] == "advertiser":
            if st.button("前往儀表板", type="primary", use_container_width=True):
                st.switch_page("pages/10_advertiser_dashboard.py")
        else:
            if st.button("前往儀表板", type="primary", use_container_width=True):
                st.switch_page("pages/20_creator_dashboard.py")
    with col2:
        if st.button("登出", use_container_width=True):
            logout()
            st.rerun()
else:
    st.info("立即註冊，開始 AI 媒合之旅")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🏢 我是廣告主", type="primary", use_container_width=True):
            st.switch_page("pages/02_register.py")
    with col2:
        if st.button("🎬 我是創作者", type="primary", use_container_width=True):
            st.switch_page("pages/02_register.py")

st.divider()
st.markdown("### 💡 運作流程")
st.markdown("""
1. **註冊帳號** — 選擇廣告主或創作者身份
2. **填寫資料** — 品牌/頻道資料、預算/報價、合作偏好
3. **AI 分析** — 系統自動生成 profile 並計算 embedding
4. **智能匹配** — 四維度加權評分，找到最佳配對
5. **談判模擬** — 3 輪 AI 談判 + 觀眾反饋評分
6. **達成合作** — 雙方同意後生成合約建議
""")
