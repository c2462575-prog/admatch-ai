"""Creator Profile Setup page."""
import streamlit as st
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))
from frontend.utils.api_client import require_login, current_user, get, put
from frontend.utils.profile_completeness import creator_completeness, show_completeness_bar

require_login()
user = current_user()

st.title("👤 頻道資料設定")

existing = {}
try:
    existing = get("/creators/profile")
except Exception:
    pass

if existing:
    score, missing = creator_completeness(existing)
    show_completeness_bar(score, missing, "creator")

NICHES = ["lifestyle", "technology", "beauty", "sustainability", "food", "travel", "fitness", "education", "gaming", "finance", "entertainment"]
CONTENT_STYLES = ["lifestyle", "coffee", "urban_exploration", "sustainability", "organic", "zero_waste",
                  "tech_review", "tutorials", "developer_tools", "beauty_tips", "travel_vlog", "fitness_tips"]
VALUES_OPTIONS = ["authenticity", "quality", "aesthetics", "sustainability", "environmental_action",
                  "technical_accuracy", "hands_on_experience", "value_driven", "creativity", "community"]
SENSITIVITY = ["authenticity", "content_fit", "subtlety", "environmental_authenticity", "brand_ethics",
               "greenwashing_detection", "product_quality", "technical_accuracy", "professional_presentation"]
REJECTION_TRIGGERS = ["obvious_ads", "mismatched_products", "excessive_promotion", "greenwashing",
                      "unethical_brands", "fake_sustainability_claims", "low_quality_products",
                      "exaggerated_claims", "unprofessional_content"]

with st.form("creator_profile"):
    niche = st.selectbox("內容領域", NICHES,
                          index=NICHES.index(existing.get("niche", "lifestyle")) if existing.get("niche") in NICHES else 0)

    description = st.text_area("頻道描述（詳細說明內容方向、粉絲畫像、合作偏好）",
                               value=existing.get("description", ""), height=200)

    col1, col2 = st.columns(2)
    with col1:
        follower_count = st.number_input("粉絲數量", value=existing.get("follower_count", 10000), step=1000, min_value=0)
        engagement_rate = st.slider("互動率", 0.0, 0.20, existing.get("engagement_rate", 0.05), 0.005, format="%.3f")
    with col2:
        min_fee = st.number_input("最低報價 (元)", value=existing.get("min_fee", 10000), step=5000, min_value=0)
        max_fee = st.number_input("最高報價 (元)", value=existing.get("max_fee", 50000), step=5000, min_value=0)

    content_style = st.multiselect("內容風格標籤", CONTENT_STYLES, default=existing.get("content_style", []))
    values = st.multiselect("核心價值觀", VALUES_OPTIONS, default=existing.get("values", []))

    st.divider()
    st.markdown("### 🎯 粉絲受眾設定")
    audience_description = st.text_area("粉絲群體描述", value=existing.get("audience_description", ""), height=100)
    audience_threshold = st.slider("受眾接受度門檻", 0.0, 1.0, existing.get("audience_acceptance_threshold", 0.35), 0.05)
    sensitivity = st.multiselect("敏感因素", SENSITIVITY, default=existing.get("audience_sensitivity_factors", []))
    triggers = st.multiselect("拒絕觸發條件", REJECTION_TRIGGERS, default=existing.get("audience_rejection_triggers", []))

    submitted = st.form_submit_button("儲存頻道資料", type="primary", use_container_width=True)

if submitted:
    try:
        result = put("/creators/profile", {
            "niche": niche,
            "description": description,
            "follower_count": follower_count,
            "engagement_rate": engagement_rate,
            "content_style": content_style,
            "min_fee": min_fee,
            "max_fee": max_fee,
            "values": values,
            "audience_description": audience_description,
            "audience_acceptance_threshold": audience_threshold,
            "audience_sensitivity_factors": sensitivity,
            "audience_rejection_triggers": triggers,
        })
        st.success("頻道資料已儲存！")
        st.balloons()
    except Exception as e:
        st.error(f"儲存失敗：{e}")
