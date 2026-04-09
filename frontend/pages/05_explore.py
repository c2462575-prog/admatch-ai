"""Public Creator Explore page — no login required."""
import streamlit as st
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))
from frontend.utils.api_client import get, is_logged_in
from frontend.utils.navigation import switch

st.title("🔍 探索創作者")
st.markdown("瀏覽平台上的創作者，找到你的理想合作夥伴。")

# Niche filter
try:
    niches = get("/explore/niches")
    niche_options = ["all"] + [n["niche"] for n in niches]
    niche_labels = {"all": "全部"}
    niche_labels.update({n["niche"]: f"{n['niche']} ({n['count']})" for n in niches})
    selected_niche = st.selectbox("按領域篩選", niche_options, format_func=lambda x: niche_labels.get(x, x))
except Exception:
    selected_niche = "all"

# Load creators
try:
    params = {"limit": 50}
    if selected_niche != "all":
        params["niche"] = selected_niche
    data = get("/explore/creators", params)
    creators = data.get("creators", [])
except Exception:
    creators = []

if not creators:
    st.info("目前沒有符合條件的創作者。")
    st.stop()

st.caption(f"共 {len(creators)} 位創作者")

for i, c in enumerate(creators):
    with st.container(border=True):
        # Header: name + stats
        hc1, hc2 = st.columns([3, 2])
        with hc1:
            st.markdown(f"**{c['display_name']}** · 📌 {c['niche']}")
        with hc2:
            fc = c.get("follower_count", 0)
            fc_str = f"{fc/10000:.1f}萬" if fc >= 10000 else f"{fc:,}"
            st.markdown(f"👥 {fc_str} · 💬 {c.get('engagement_rate', 0):.1%}")
        # Description
        st.caption(c.get("description", ""))
        # Tags
        tags = c.get("content_style", []) + c.get("values", [])
        if tags:
            st.markdown(" ".join(f"`{t}`" for t in tags[:6]))

if not is_logged_in():
    st.divider()
    st.markdown("### 想要聯繫這些創作者？")
    st.info("註冊成為廣告主，即可使用 AI 匹配找到最適合你的創作者。")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🏢 註冊為廣告主", type="primary", use_container_width=True):
            switch("02_register.py")
    with col2:
        if st.button("🔑 登入", use_container_width=True):
            switch("01_login.py")
