"""Advertiser Profile Setup page."""
import streamlit as st
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))
from frontend.utils.api_client import require_login, current_user, get, put

require_login()
user = current_user()

st.title("🏢 品牌資料設定")

# Load existing profile
existing = {}
try:
    existing = get("/advertisers/profile")
except Exception:
    pass

INDUSTRIES = ["food_beverage", "technology", "beauty", "fashion", "health", "education", "finance", "travel", "entertainment", "other"]
BUDGET_RANGES = ["low", "medium", "medium_high", "high"]
AUDIENCES = ["urban_professionals", "tech_professionals", "eco_conscious_women", "young_adults", "parents", "students", "general"]
GOALS = ["brand_awareness", "user_acquisition", "brand_loyalty", "product_launch", "sales_conversion"]
VALUES_OPTIONS = ["craftsmanship", "sustainability", "community", "innovation", "efficiency", "collaboration", "authenticity", "quality", "natural", "cruelty_free"]

with st.form("advertiser_profile"):
    industry = st.selectbox("行業", INDUSTRIES, index=INDUSTRIES.index(existing.get("industry", "other")) if existing.get("industry") in INDUSTRIES else 0)

    description = st.text_area("品牌描述（詳細說明品牌定位、目標客群、本次推廣目標）",
                               value=existing.get("description", ""), height=200)

    col1, col2 = st.columns(2)
    with col1:
        budget_range = st.selectbox("預算範圍", BUDGET_RANGES,
                                     index=BUDGET_RANGES.index(existing.get("budget_range", "medium")) if existing.get("budget_range") in BUDGET_RANGES else 1)
    with col2:
        budget_value = st.number_input("具體預算 (元)", value=existing.get("budget_value", 50000), step=10000, min_value=0)

    target_audience = st.selectbox("目標受眾", AUDIENCES,
                                    index=AUDIENCES.index(existing.get("target_audience", "general")) if existing.get("target_audience") in AUDIENCES else 0)

    values = st.multiselect("品牌價值觀", VALUES_OPTIONS, default=existing.get("values", []))

    campaign_goal = st.selectbox("推廣目標", GOALS,
                                  index=GOALS.index(existing.get("campaign_goal", "brand_awareness")) if existing.get("campaign_goal") in GOALS else 0)

    submitted = st.form_submit_button("儲存品牌資料", type="primary", use_container_width=True)

if submitted:
    try:
        result = put("/advertisers/profile", {
            "industry": industry,
            "description": description,
            "budget_range": budget_range,
            "budget_value": budget_value,
            "target_audience": target_audience,
            "values": values,
            "campaign_goal": campaign_goal,
        })
        st.success("品牌資料已儲存！")
        st.balloons()
    except Exception as e:
        st.error(f"儲存失敗：{e}")
