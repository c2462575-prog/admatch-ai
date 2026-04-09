"""Negotiation History page."""
import streamlit as st
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))
from frontend.utils.api_client import require_login, current_user, get
from frontend.utils.navigation import switch

require_login()
user = current_user()

st.title("📋 談判歷史")

try:
    negotiations = get("/negotiations/")
except Exception:
    negotiations = []

if not negotiations:
    st.info("尚無談判記錄。")
    st.stop()

status_map = {"in_progress": "🔄 進行中", "success": "✅ 成功", "failed": "❌ 失敗", "audience_rejected": "🚫 觀眾否決"}

for neg in negotiations:
    with st.container(border=True):
        col1, col2, col3, col4 = st.columns([3, 2, 2, 1])
        with col1:
            adv_name = neg.get("advertiser_name", "Advertiser")
            creator_name = neg.get("creator_name", "Creator")
            st.markdown(f"**{adv_name}** ↔ **{creator_name}**")
        with col2:
            st.markdown(status_map.get(neg["status"], neg["status"]))
        with col3:
            if neg.get("final_price"):
                st.markdown(f"¥{neg['final_price']:,}")
            else:
                st.markdown("—")
        with col4:
            if st.button("查看", key=f"view_{neg['id']}"):
                st.session_state["active_negotiation_id"] = neg["id"]
                switch("31_negotiation.py")
