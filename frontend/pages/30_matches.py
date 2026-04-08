"""Match Results page."""
import streamlit as st
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))
from frontend.utils.api_client import require_login, current_user, get, post
from frontend.utils.charts import match_radar_chart, score_bar_chart
from frontend.utils.match_insights import generate_match_insight, get_match_verdict

require_login()
user = current_user()

st.title("🤝 匹配結果")

col1, col2 = st.columns([3, 1])
with col2:
    if st.button("🔄 重新匹配", type="primary"):
        with st.spinner("AI 匹配計算中..."):
            try:
                results = post("/matching/run")
                st.success(f"找到 {len(results)} 個匹配！")
                st.rerun()
            except Exception as e:
                st.error(f"匹配失敗：{e}")

# Load existing results
try:
    matches = get("/matching/results")
except Exception:
    matches = []

if not matches:
    st.info("尚無匹配結果。點擊「重新匹配」開始 AI 媒合。")
    st.stop()

# Bar chart overview
st.plotly_chart(score_bar_chart(matches), use_container_width=True)

st.divider()

# Detailed cards
for i, m in enumerate(matches):
    with st.container(border=True):
        col1, col2, col3 = st.columns([2, 3, 1])
        with col1:
            emoji, verdict = get_match_verdict(m.get("weighted_score", 0))
            st.markdown(f"### {emoji} {m.get('partner_name', 'Partner')}")
            st.metric("總匹配度", f"{m.get('weighted_score', 0):.1%}", delta=verdict)
            st.caption(generate_match_insight(m))
        with col2:
            fig = match_radar_chart({
                "embedding_score": m.get("embedding_score", 0),
                "audience_score": m.get("audience_score", 0),
                "budget_score": m.get("budget_score", 0),
                "values_score": m.get("values_score", 0),
            }, title=f"Score Breakdown")
            st.plotly_chart(fig, use_container_width=True, key=f"radar_{i}")
        with col3:
            st.caption(f"狀態: {m.get('status', 'pending')}")
            match_id = m.get("id", "")
            if st.button("💬 開始談判", key=f"neg_{i}"):
                st.session_state["negotiate_match_id"] = match_id
                st.switch_page("pages/31_negotiation.py")
