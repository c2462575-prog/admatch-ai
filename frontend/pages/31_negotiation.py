"""Negotiation Simulation page."""
import streamlit as st
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))
from frontend.utils.api_client import require_login, current_user, get, post
from frontend.utils.navigation import switch
from frontend.utils.charts import audience_gauge

require_login()
user = current_user()

st.title("💬 AI 談判模擬")

# Check if we have an active negotiation or need to start one
match_id = st.session_state.get("negotiate_match_id")
neg_id = st.session_state.get("active_negotiation_id")

# Start new negotiation from match
if match_id and not neg_id:
    try:
        with st.spinner("初始化談判..."):
            neg = post("/negotiations/start", {"match_id": match_id})
            neg_id = neg["id"]
            st.session_state["active_negotiation_id"] = neg_id
            st.session_state.pop("negotiate_match_id", None)
    except Exception as e:
        st.error(f"無法啟動談判：{e}")
        st.stop()

if not neg_id:
    # Show list of existing negotiations to pick from
    try:
        negotiations = get("/negotiations/")
        if negotiations:
            st.markdown("### 選擇一個談判繼續")
            for neg_item in negotiations:
                status_map = {"in_progress": "🔄", "success": "✅", "failed": "❌", "audience_rejected": "🚫"}
                label = f"{status_map.get(neg_item['status'], '?')} {neg_item.get('advertiser_name', 'Advertiser')} ↔ {neg_item.get('creator_name', 'Creator')} ({neg_item['status']})"
                if st.button(label, key=f"pick_{neg_item['id']}", use_container_width=True):
                    st.session_state["active_negotiation_id"] = neg_item["id"]
                    st.rerun()
            st.divider()
    except Exception:
        pass
    st.info("或從匹配結果頁面選擇一個配對來開始新談判。")
    if st.button("前往匹配結果"):
        switch("30_matches.py")
    st.stop()

# Load negotiation data
try:
    neg = get(f"/negotiations/{neg_id}")
except Exception as e:
    st.error(f"載入談判失敗：{e}")
    st.stop()

# Status header
status_map = {"in_progress": "🔄 進行中", "success": "✅ 合作成功", "failed": "❌ 談判失敗", "audience_rejected": "🚫 觀眾否決"}
st.markdown(f"**狀態：{status_map.get(neg['status'], neg['status'])}** | 當前回合：{neg['current_round']}/3")

if neg.get("final_price"):
    st.success(f"最終合作價格：¥{neg['final_price']:,}")

st.divider()

# Display rounds
rounds = neg.get("rounds", [])
for r in rounds:
    st.markdown(f"### 第 {r['round_num']} 輪")

    col1, col2 = st.columns(2)
    with col1:
        with st.chat_message("user", avatar="🏢"):
            st.markdown("**廣告主：**")
            st.markdown(r.get("advertiser_message", "")[:1000])
    with col2:
        with st.chat_message("assistant", avatar="🎬"):
            st.markdown("**創作者：**")
            st.markdown(r.get("creator_message", "")[:1000])

    # Audience feedback
    if r.get("audience_score") is not None:
        col1, col2 = st.columns([1, 2])
        with col1:
            st.plotly_chart(audience_gauge(r["audience_score"]), use_container_width=True, key=f"gauge_{r['round_num']}")
        with col2:
            if r.get("audience_feedback"):
                st.info(f"🎯 觀眾反饋：{r['audience_feedback'][:500]}")
            if r.get("intervention_warning"):
                st.warning(f"⚠️ 觀眾警告：{r['intervention_warning'][:500]}")

    st.divider()

# Action button
if neg["status"] == "in_progress" and neg["current_round"] < 3:
    if st.button(f"▶️ 進行第 {neg['current_round'] + 1} 輪談判", type="primary", use_container_width=True):
        with st.spinner("AI 談判中...（可能需要 30-60 秒）"):
            try:
                result = post(f"/negotiations/{neg_id}/next-round")
                st.rerun()
            except Exception as e:
                st.error(f"談判失敗：{e}")

if neg["status"] != "in_progress":
    if neg.get("summary"):
        st.markdown(f"**結論：** {neg['summary']}")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("返回匹配結果"):
            st.session_state.pop("active_negotiation_id", None)
            switch("30_matches.py")
    with col2:
        if st.button("查看歷史記錄"):
            st.session_state.pop("active_negotiation_id", None)
            switch("32_history.py")
