"""Advertiser Dashboard."""
import streamlit as st
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))
from frontend.utils.api_client import require_login, current_user, get

require_login()
user = current_user()

st.title(f"📊 廣告主儀表板")
st.markdown(f"歡迎, **{user['display_name']}**")

col1, col2, col3 = st.columns(3)
with col1:
    st.metric("方案", user.get("plan", "free").upper())
with col2:
    st.metric("本月匹配次數", f"{user.get('matches_used_this_month', 0)} / 3")
with col3:
    try:
        matches = get("/matching/results")
        st.metric("匹配結果", len(matches))
    except Exception:
        st.metric("匹配結果", 0)

st.divider()

col1, col2 = st.columns(2)
with col1:
    if st.button("📝 編輯品牌資料", type="primary", use_container_width=True):
        st.switch_page("pages/11_advertiser_profile.py")
with col2:
    if st.button("🔍 開始匹配", use_container_width=True):
        st.switch_page("pages/30_matches.py")

st.divider()
st.markdown("### 最近的匹配")
try:
    matches = get("/matching/results", {"limit": 5})
    if matches:
        for m in matches:
            with st.container(border=True):
                c1, c2, c3 = st.columns([3, 2, 1])
                with c1:
                    st.markdown(f"**{m.get('partner_name', 'Creator')}**")
                with c2:
                    st.progress(m.get("weighted_score", 0), text=f"匹配度 {m.get('weighted_score', 0):.1%}")
                with c3:
                    st.caption(m.get("status", "pending"))
    else:
        st.info("尚無匹配結果。請先完成品牌資料，再進行匹配。")
except Exception:
    st.info("尚無匹配結果。請先完成品牌資料，再進行匹配。")
