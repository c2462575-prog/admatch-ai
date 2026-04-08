"""Admin Analytics Dashboard — for founders/operators."""
import streamlit as st
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))
from frontend.utils.api_client import get

st.title("📈 Admin Analytics")

# Simple admin gate — check for admin query param or logged-in user
# For MVP, this dashboard is accessible but not in main navigation

try:
    data = get("/stats/admin/analytics")
except Exception as e:
    st.error(f"Cannot load analytics: {e}")
    st.stop()

# User metrics
st.markdown("### 👥 Users")
u = data["users"]
c1, c2, c3, c4 = st.columns(4)
with c1:
    st.metric("Total Users", u["total"])
with c2:
    st.metric("Advertisers", u["advertisers"])
with c3:
    st.metric("Creators", u["creators"])
with c4:
    st.metric("Paid Conversion", f"{u['conversion_rate']}%")

# Profile completion
st.markdown("### 📝 Profile Completion")
p = data["profiles"]
c1, c2 = st.columns(2)
with c1:
    rate = p["advertiser_completion_rate"] / 100
    st.progress(min(rate, 1.0), text=f"Advertiser: {p['advertiser_completed']}/{u['advertisers']} ({p['advertiser_completion_rate']}%)")
with c2:
    rate = p["creator_completion_rate"] / 100
    st.progress(min(rate, 1.0), text=f"Creator: {p['creator_completed']}/{u['creators']} ({p['creator_completion_rate']}%)")

# Matching
st.markdown("### 🤝 Matching")
m = data["matching"]
c1, c2, c3 = st.columns(3)
with c1:
    st.metric("Total Matches", m["total_matches"])
with c2:
    st.metric("Avg Score", f"{m['avg_score']:.1%}")
with c3:
    st.metric("High Quality (>60%)", m["high_quality_matches"])

# Negotiations
st.markdown("### 💬 Negotiations")
n = data["negotiations"]
c1, c2, c3, c4, c5 = st.columns(5)
with c1:
    st.metric("Total", n["total"])
with c2:
    st.metric("✅ Success", n["success"])
with c3:
    st.metric("❌ Failed", n["failed"])
with c4:
    st.metric("🚫 Rejected", n["audience_rejected"])
with c5:
    st.metric("Success Rate", f"{n['success_rate']}%")

# Growth
st.markdown("### 🚀 Growth")
g = data["growth"]
st.metric("Referrals Completed", g["referrals_completed"])

# Errors
st.markdown("### 🐛 Error Tracking")
try:
    summary = get("/stats/admin/error-summary")
    st.metric("Total Errors", summary.get("total_errors", 0))
    if summary.get("by_source"):
        st.json(summary["by_source"])
    if summary.get("total_errors", 0) > 0:
        with st.expander("Recent Errors"):
            errors = get("/stats/admin/errors", {"limit": 10})
            for err in errors:
                st.markdown(f"**{err['time']}** `{err['source']}` — {err['error_type']}: {err['message']}")
except Exception:
    st.caption("No error data available")
