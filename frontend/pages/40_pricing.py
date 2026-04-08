"""Pricing Calculator page (public)."""
import streamlit as st
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))

st.title("💰 報價計算器")
st.markdown("根據創作者數據，AI 估算合理的合作報價。")

col1, col2 = st.columns(2)

with col1:
    st.markdown("### 創作者報價估算")
    followers = st.number_input("粉絲數量", value=50000, step=5000, min_value=100)
    engagement_rate = st.slider("互動率", 0.001, 0.200, 0.050, 0.005, format="%.3f")
    category = st.selectbox("內容類別", ["lifestyle", "tech", "beauty", "food", "travel", "finance"])

    if st.button("計算報價", type="primary"):
        try:
            from frontend.utils.api_client import get
            result = get("/pricing/estimate", {
                "followers": followers,
                "engagement_rate": engagement_rate,
                "category": category,
            })
            st.success(f"建議基礎報價：**¥{result['base_price']:,.0f}**")
            low, high = result["suggested_range"]
            st.info(f"建議報價範圍：¥{low:,.0f} — ¥{high:,.0f}")
        except Exception as e:
            # Fallback: compute locally
            from utils.price_calculator import calculate_creator_price
            result = calculate_creator_price(followers, engagement_rate, category)
            st.success(f"建議基礎報價：**¥{result['base_price']:,.0f}**")
            low, high = result["suggested_range"]
            st.info(f"建議報價範圍：¥{low:,.0f} — ¥{high:,.0f}")

with col2:
    st.markdown("### ROI 估算")
    price = st.number_input("投放費用 (元)", value=30000, step=5000, min_value=1)
    expected_reach = st.number_input("預期觸及人數", value=100000, step=10000, min_value=100)
    conversion_rate = st.slider("預期轉化率", 0.001, 0.100, 0.020, 0.005, format="%.3f")

    if st.button("計算 ROI"):
        try:
            from frontend.utils.api_client import get
            result = get("/pricing/roi", {
                "price": price,
                "expected_reach": expected_reach,
                "conversion_rate": conversion_rate,
            })
            st.metric("預估轉化次數", f"{result['estimated_conversions']:,.0f}")
            st.metric("每次轉化成本", f"¥{result['cost_per_conversion']:,.2f}")
            st.metric("ROI 指數", f"{result['roi_score']:.4f}")
        except Exception as e:
            from utils.price_calculator import estimate_roi
            result = estimate_roi(price, expected_reach, conversion_rate)
            st.metric("預估轉化次數", f"{result['estimated_conversions']:,.0f}")
            st.metric("每次轉化成本", f"¥{result['cost_per_conversion']:,.2f}")
            st.metric("ROI 指數", f"{result['roi_score']:.4f}")
