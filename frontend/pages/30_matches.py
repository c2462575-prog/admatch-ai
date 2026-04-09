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

# Filters and sorting
with st.expander("🔧 篩選與排序", expanded=False):
    fc1, fc2, fc3 = st.columns(3)
    with fc1:
        sort_by = st.selectbox("排序依據", ["weighted_score", "embedding_score", "audience_score", "budget_score", "values_score"],
                                format_func=lambda x: {"weighted_score": "總匹配度", "embedding_score": "內容相關性",
                                                        "audience_score": "受眾契合", "budget_score": "預算吻合",
                                                        "values_score": "價值觀一致"}.get(x, x))
    with fc2:
        min_score = st.slider("最低匹配度", 0.0, 1.0, 0.0, 0.05)
    with fc3:
        status_filter = st.selectbox("狀態", ["all", "pending", "negotiation_started"],
                                      format_func=lambda x: {"all": "全部", "pending": "待處理", "negotiation_started": "談判中"}.get(x, x))

# Apply filters
filtered = matches
if min_score > 0:
    filtered = [m for m in filtered if m.get("weighted_score", 0) >= min_score]
if status_filter != "all":
    filtered = [m for m in filtered if m.get("status") == status_filter]
filtered.sort(key=lambda x: x.get(sort_by, 0), reverse=True)

st.caption(f"顯示 {len(filtered)} / {len(matches)} 個匹配")

# Supply-side growth prompt
if len(matches) <= 3:
    partner_type = "創作者" if user.get("role") == "advertiser" else "廣告主"
    with st.container(border=True):
        st.markdown(f"💡 **想看到更多{partner_type}？** 邀請更多{partner_type}加入平台，匹配池越大，找到理想夥伴的機會越高！")
        try:
            ref = get("/referrals/my-code")
            st.markdown(f"你的邀請碼：`{ref['code']}` — 每邀請 1 人可獲得 2 次額外匹配")
        except Exception:
            pass

# Bar chart overview
if filtered:
    st.plotly_chart(score_bar_chart(filtered), use_container_width=True)

st.divider()

# Detailed cards — mobile-friendly stacked layout
for i, m in enumerate(filtered):
    with st.container(border=True):
        emoji, verdict = get_match_verdict(m.get("weighted_score", 0))
        # Header row: name + score
        hc1, hc2 = st.columns([3, 2])
        with hc1:
            st.markdown(f"### {emoji} {m.get('partner_name', 'Partner')}")
        with hc2:
            st.metric("匹配度", f"{m.get('weighted_score', 0):.1%}", delta=verdict)

        # Insight text
        st.caption(generate_match_insight(m))

        # Score bars (compact, mobile-friendly)
        scores = {"內容": m.get("embedding_score", 0), "受眾": m.get("audience_score", 0),
                  "預算": m.get("budget_score", 0), "價值觀": m.get("values_score", 0)}
        for label, val in scores.items():
            st.progress(min(val, 1.0), text=f"{label} {val:.0%}")

        # Action button
        match_id = m.get("id", "")
        if st.button("💬 開始談判", key=f"neg_{i}", use_container_width=True):
            st.session_state["negotiate_match_id"] = match_id
            st.switch_page("pages/31_negotiation.py")
