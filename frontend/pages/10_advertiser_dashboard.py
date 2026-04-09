"""Advertiser Dashboard."""
import streamlit as st
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))
from frontend.utils.api_client import require_login, current_user, get
from frontend.utils.navigation import switch
from frontend.utils.onboarding import show_advertiser_onboarding

require_login()
user = current_user()

st.title(f"📊 廣告主儀表板")
st.markdown(f"歡迎, **{user['display_name']}**")

# Onboarding checklist for new users
show_advertiser_onboarding()
st.divider()

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
        switch("11_advertiser_profile.py")
with col2:
    if st.button("🔍 開始匹配", use_container_width=True):
        switch("30_matches.py")

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

# Activity feed
st.divider()
st.markdown("### 📰 最近動態")
try:
    events = get("/activity/feed", {"limit": 5})
    if events:
        for ev in events:
            st.markdown(f"{ev['icon']} **{ev['text']}**")
    else:
        st.caption("尚無動態")
except Exception:
    st.caption("尚無動態")

# Referral section
st.divider()
st.markdown("### 🎁 邀請好友，獲得額外匹配次數")
try:
    ref = get("/referrals/my-code")
    st.code(ref["code"], language=None)
    st.caption(f"分享這個邀請碼給朋友，對方註冊時填入即可。每成功邀請 1 人，你獲得 **2 次額外匹配**。已邀請：{ref.get('total_referrals', 0)} 人")
except Exception:
    pass
